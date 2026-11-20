# Copyright 2025 Wirepas Ltd licensed under Apache License, Version 2.0
#
# See file LICENSE for full license details.
#

import queue
import logging
import serial
import sys
import threading
import time

from colorama import Fore
from enum import Enum
from struct import pack, unpack
from threading import Thread, Event
from time import sleep

from yahdlc import (
    FRAME_ACK,
    FRAME_DATA,
    FRAME_NACK,
    FCSError,
    MessageError,
    frame_data,
    get_data,
    get_data_reset,
)


class ExitCodes(Enum):
    SUCCESS = 0
    SENDING_FAILED = 1
    RECEPTION_TIMEOUT = 2
    INVALID_PARAMETERS = 3
    MISSING_PARAMETERS = 4
    HDLC_PACKET_TOO_LARGE = 5
    CALL_TO_MAIN = 6
    SERIAL_ERROR = 7


class MessageType(Enum):
    PROVISIONING_WRITE_REQUEST = 0
    PROVISIONING_WRITE_RESPONSE = 1
    PROVISIONING_READ_REQUEST = 2
    PROVISIONING_READ_RESPONSE = 3
    PROVISIONING_REBOOT_REQUEST = 4
    STOP_FACTORY_MODE_AND_RESET = 5
    STOP_FACTORY_MODE_AND_RESET_RESPONSE = 6
    PROVISIONING_APPLY_REQUEST = 7
    PROVISIONING_APPLY_RESPONSE = 8
    PROVISIONING_CLEAR_REQUEST = 9
    TESTING_CELLULAR_REQUEST = 64
    TESTING_CELLULAR_RESPONSE = 65
    TESTING_GPIO_REQUEST = 66
    TESTING_GPIO_RESPONSE = 67
    TESTING_EXT_FLASH_REQUEST = 68
    TESTING_EXT_FLASH_RESPONSE = 69
    TESTING_RF_REQUEST = 70
    TESTING_RF_RESPONSE = 71
    MTCTE_REQUEST = 72
    MTCTE_RESPONSE = 73

class TapMessageType(Enum):
    RESET_REQUEST = 0x16
    RESET_RESPONSE = 0x17

PROVISIONING_CHALLENGE = b"WPP\n"
PROVISIONING_CHALLENGE_RESP = b"OK\n"
# Send challenge every 60 ms, to fit in 100ms window, with 32ms delay (send reset + challenge)
PROVISIONING_CHALLENGE_PERIOD_S = 0.090
PROVISIONING_RESET_INTERVAL_S = 0.6  # 500ms
PROVISIONING_STOP_RX_WAIT_S = 1.0  # 1s


class FactoryMode:
    MAX_TX_ATTEMPT = 8
    ACK_NACK_TIMEOUT_S = 2.000
    TAP_RESET_RESPONSE_RECEIVE_TIMEOUT_S = 4.000
    EMBEDDED_HDLC_BUFFER_MAX_SIZE = 2048

    ser = serial.Serial()
    serial_baudrate = 9600

    parse_message_callback = None

    hdlc_decode = Event()
    tx_seq = 0

    # Add a stop event for the rx thread
    rx_thread_stop = threading.Event()
    rx_thread = None

    tx_queue = queue.Queue(MAX_TX_ATTEMPT)
    rx_challenge_queue = queue.Queue()
    rx_ftype_queue = queue.Queue()
    tap_reset_response_queue = queue.Queue()

    serial_lock = threading.Lock()  # Add lock for thread-safe serial access

# Filter tap messages to not interfere with the other types of messages
tap_filter = False

def error_print_and_exit(fm: FactoryMode, message: str, error_code: ExitCodes):
    serial_cleanup(fm)
    logging.error(Fore.RED + message + Fore.RESET)
    print(error_code.value)


def error_print(message):
    logging.error(Fore.RED + message + Fore.RESET)


def success_print(message):
    logging.info(Fore.GREEN + message + Fore.RESET)


def send_raw_hdlc_data(fm: FactoryMode, data: bytes):
    hdlc_frame = frame_data(data, FRAME_DATA, fm.tx_seq)

    if len(hdlc_frame) > fm.EMBEDDED_HDLC_BUFFER_MAX_SIZE:
        error_print_and_exit(
            fm,
            "Length of the HDLC packet cannot be processed by the embedded application!",
            ExitCodes.HDLC_PACKET_TOO_LARGE,
        )

    for _ in range(fm.MAX_TX_ATTEMPT):
        fm.tx_queue.put_nowait(hdlc_frame)

    # Cleaning any remaining items stored in the rx_ftype queue
    with fm.rx_ftype_queue.mutex:
        fm.rx_ftype_queue.queue.clear()

    ret = False
    try:
        while fm.tx_queue.empty() is False:
            packet = fm.tx_queue.get()
            logging.debug(
                "Sending %d bytes long data frame: %s with seq: %d",
                len(packet),
                packet.hex(),
                fm.tx_seq,
            )
            fm.ser.write(packet)
            try:
                ftype = fm.rx_ftype_queue.get(timeout=fm.ACK_NACK_TIMEOUT_S)
            except queue.Empty:
                logging.warning("Timeout detected!")
                continue

            if ftype != FRAME_ACK:
                ret = False
                continue
            else:
                with fm.tx_queue.mutex:
                    fm.tx_queue.queue.clear()
                ret = True

        fm.tx_seq += 1
        fm.tx_seq %= 7

        return ret

    except serial.SerialException as e:
        error_print_and_exit(
            fm,
            f"Serial connection problem: {str(e)}", ExitCodes.SERIAL_ERROR
        )


def send_factory_mode_message(fm: FactoryMode, data: bytes, type: MessageType) -> bool:
    # Generating header
    header = pack("<BB", 0, type.value)
    message = header + data

    return send_raw_hdlc_data(fm, message)


def parse_message_received(fm: FactoryMode, data: bytes):
    global tap_filter

    if tap_filter:
        if data.startswith(bytes([0, TapMessageType.RESET_RESPONSE.value])):
            logging.debug("Received tap reset response: Status = %d", data[2])
            fm.tap_reset_response_queue.put(True)
        return

    # parse header
    version, type = unpack("<BB", data[0:2])
    if version != 0:
        logging.warning("Not a valid protocol version")
        return

    # Convert to enum
    type = MessageType(type)

    # Remove header from received data
    data = data[2:]

    # Call the callback function with the parsed data
    fm.parse_message_callback(type, data)


def rx_callback(fm: FactoryMode):
    buffer = bytes()
    MAX_BUFFER_SIZE = fm.EMBEDDED_HDLC_BUFFER_MAX_SIZE
    
    while not fm.rx_thread_stop.is_set():
        try:
            # Thread-safe serial access with timeout
            with fm.serial_lock:
                if not hasattr(fm.ser, "is_open") or not fm.ser.is_open:
                    logging.debug("Serial port closed, exiting rx_callback")
                    break
                
                in_waiting = fm.ser.in_waiting
                if in_waiting == 0:
                    pass
                else:
                    # Limit read size to prevent buffer overflow
                    read_size = min(in_waiting, MAX_BUFFER_SIZE)
                    new_data = fm.ser.read(read_size)
            
            # Sleep outside the lock
            if in_waiting == 0:
                sleep(0.01)
                continue
            
            # Check buffer size BEFORE adding new data
            if len(buffer) + len(new_data) > MAX_BUFFER_SIZE * 2:
                logging.warning("Buffer approaching overflow, clearing old data")
                last_flag = buffer.rfind(b"\x7e")
                if last_flag >= 0:
                    buffer = buffer[last_flag:]
                else:
                    buffer = bytes()
            
            # Process data (existing code)
            if fm.hdlc_decode.is_set():
                buffer += new_data
                logging.debug(f"HDLC buffer size: {len(buffer)} bytes")

                # Process buffer until no more complete frames
                while True:
                    try:
                        # Reset decoder state before attempting to decode
                        get_data_reset()

                        # Try to extract a frame
                        logging.debug(f"Attempting to decode HDLC frame from buffer: {buffer.hex()}")
                        data, ftype, seq_no = get_data(buffer)

                        # Log successful frame reception
                        logging.debug(
                            f"HDLC frame received - Type: {ftype}, Seq: {seq_no}, Data length: {len(data)}, Data: {data.hex()}"
                        )

                        # Handle the frame based on its type
                        fm.rx_ftype_queue.put(ftype)
                        if ftype == FRAME_DATA:
                            # Send ACK for data frames
                            ack_frame = frame_data("", FRAME_ACK, seq_no)
                            logging.debug(f"Sending ACK for seq {seq_no}: {ack_frame.hex()}")
                            fm.ser.write(ack_frame)
                            parse_message_received(fm, data)
                        elif ftype == FRAME_ACK:
                            logging.debug(f"Received ACK frame with seq {seq_no}")
                        elif ftype == FRAME_NACK:
                            logging.debug(f"Received NACK frame with seq {seq_no}")

                        # Find the end flag position to remove processed data
                        # The +1 is to include the end flag itself
                        end_pos = buffer.find(b"\x7e", 1) + 1
                        if end_pos > 0:
                            logging.debug(f"Removing {end_pos} bytes from buffer (processed frame)")
                            buffer = buffer[end_pos:]
                        else:
                            buffer = bytes()

                    except MessageError:
                        # No complete frame in buffer yet
                        logging.debug("No complete HDLC frame in buffer yet")
                        break

                    except FCSError:
                        logging.warning(f"Bad FCS in frame: {buffer.hex()}")
                        # Find next flag and continue from there
                        next_flag = buffer.find(b"\x7e", 1)
                        if next_flag > 0:
                            logging.debug(f"Skipping {next_flag} bytes to next flag after FCS error")
                            buffer = buffer[next_flag:]
                        else:
                            buffer = bytes()

                # Prevent buffer from growing too large
                if len(buffer) > fm.EMBEDDED_HDLC_BUFFER_MAX_SIZE * 2:
                    # Keep only data after the last flag
                    last_flag = buffer.rfind(b"\x7e")
                    if last_flag >= 0:
                        buffer = buffer[last_flag:]
                    else:
                        buffer = bytes()
                    logging.warning(f"Buffer overflow detected, truncated to last flag. New buffer size: {len(buffer)}")

            else:
                # Serial Reading (No protocol) - Challenge response mode
                buffer += new_data
                logging.debug(f"Challenge mode - buffer size: {len(buffer)} bytes")
                if PROVISIONING_CHALLENGE_RESP in buffer:
                    logging.debug("Provisioning challenge response detected!")
                    fm.rx_challenge_queue.put(True)
                    buffer = bytes()

        except (serial.SerialException, OSError) as e:
            # Handle serial port errors (including closed port)
            if not fm.rx_thread_stop.is_set():
                logging.warning(f"Serial error in rx_callback: {e}")
            break
        except Exception as e:
            logging.error(f"Unexpected error in rx_callback: {e}")
            break

    logging.debug("rx_callback thread stopped")


def wait_for_challenge_response_with_reset_loop(fm: FactoryMode, timeout_s: float = 45.0):
    """Wait for challenge response with timeout"""
    fm.hdlc_decode.clear()

    logging.info("Sending Soft Reset sequence and Provisioning Challenge in loop...")

    last_reset_time = 0
    last_challenge_time = 0

    with fm.rx_challenge_queue.mutex:
        fm.rx_challenge_queue.queue.clear()

    start_time = time.time()

    while fm.rx_challenge_queue.empty():
        current_time = time.time()
        
        # Check for timeout
        if current_time - start_time > timeout_s:
            error_print_and_exit(
                fm,
                f"Device did not respond to challenge within {timeout_s} seconds. "
                "Please check device connection and power.",
                ExitCodes.RECEPTION_TIMEOUT,
            )
            return False

        if current_time - start_time > timeout_s:
            error_print_and_exit("Timeout waiting for challenge response", ExitCodes.RECEPTION_TIMEOUT)
            return False

        # Send soft reset sequence periodically
        if current_time - last_reset_time >= PROVISIONING_RESET_INTERVAL_S:
            try:
                # Send reset without waiting for response
                with fm.serial_lock:
                    fm.hdlc_decode.set()  # Temporarily enable HDLC for reset
                    payload = bytes([0, TapMessageType.RESET_REQUEST.value])

                    # Clear queues before sending reset
                    with fm.rx_ftype_queue.mutex:
                        fm.rx_ftype_queue.queue.clear()

                    # Send reset command (don't wait for response)
                    hdlc_frame = frame_data(payload, FRAME_DATA, fm.tx_seq)
                    if len(hdlc_frame) <= fm.EMBEDDED_HDLC_BUFFER_MAX_SIZE:
                        fm.ser.write(hdlc_frame)
                        logging.debug("Reset command sent")
                        fm.tx_seq = (fm.tx_seq + 1) % 7

                    fm.hdlc_decode.clear()  # Disable HDLC for challenge mode
                logging.debug("Soft reset sequence query sent")
                last_reset_time = current_time
            except serial.SerialException as e:
                error_print_and_exit(
                    fm,
                    f"Serial connection problem during soft reset: {str(e)}",
                    ExitCodes.SERIAL_ERROR,
                )
                return False

        # Send challenge periodically
        if current_time - last_challenge_time >= PROVISIONING_CHALLENGE_PERIOD_S:
            try:
                with fm.serial_lock:
                    fm.ser.write(PROVISIONING_CHALLENGE)
                logging.debug("Challenge sent")
                last_challenge_time = current_time
            except serial.SerialException as e:
                error_print_and_exit(
                    fm,
                    f"Serial connection problem during challenge: {str(e)}",
                    ExitCodes.SERIAL_ERROR,
                )
                return False
        sleep(0.005)

    with fm.rx_challenge_queue.mutex:
        fm.rx_challenge_queue.queue.clear()

    fm.hdlc_decode.set()
    logging.info("Received Provisioning Challenge Response!")
    return True


def serial_initialization(serial_port: str, fm: FactoryMode, baudrate: int):
    """Initialize serial connection with proper cleanup of existing connection"""
    # Stop existing rx thread if running
    if fm.rx_thread is not None and fm.rx_thread.is_alive():
        logging.debug("Stopping existing rx thread")
        fm.rx_thread_stop.set()
        fm.rx_thread.join(timeout=PROVISIONING_STOP_RX_WAIT_S)
        
        if fm.rx_thread.is_alive():
            error_print_and_exit(
                fm,
                "Failed to stop rx thread gracefully. Cannot safely reinitialize serial port.",
                ExitCodes.SERIAL_ERROR,
            )
            return False

    # Close existing serial connection if open
    with fm.serial_lock:
        if hasattr(fm.ser, "is_open") and fm.ser.is_open:
            fm.ser.close()

        fm.serial_baudrate = baudrate

        logging.info(
            "Connecting to " + serial_port + " at " + str(fm.serial_baudrate) + " bauds"
        )

        # Reset the stop event for the new thread
        fm.rx_thread_stop.clear()

        try:
            fm.ser = serial.Serial(serial_port, fm.serial_baudrate, timeout=1)
            
            # Wait for serial port to be ready
            sleep(0.1)
            
        except serial.SerialException as e:
            if (
                "could not open port" in str(e).lower()
                or "no such file or directory" in str(e).lower()
            ):
                logging.error(
                    Fore.RED + 
                    f"Serial port '{serial_port}' is not available or does not exist. "
                    f"Please check the port name and ensure the device is connected.\n"
                    f"Error details: {str(e)}" +
                    Fore.RESET
                )
                print(ExitCodes.SERIAL_ERROR.value)
                return False
            elif "permission denied" in str(e).lower():
                logging.error(
                    Fore.RED +
                    f"Permission denied accessing serial port '{serial_port}'. "
                    f"Please check user permissions or try running with sudo.\n"
                    f"Error details: {str(e)}" +
                    Fore.RESET
                )
                print(ExitCodes.SERIAL_ERROR.value)
                return False
            else:
                logging.error(
                    Fore.RED +
                    f"Failed to open serial port '{serial_port}': {str(e)}" +
                    Fore.RESET
                )
                print(ExitCodes.SERIAL_ERROR.value)
                return False
        except Exception as e:
            logging.error(
                Fore.RED +
                f"Unexpected error opening serial port '{serial_port}': {str(e)}" +
                Fore.RESET
            )
            print(ExitCodes.SERIAL_ERROR.value)
            return False

    # Start rx thread AFTER serial port is confirmed open and ready
    fm.rx_thread = Thread(
        target=rx_callback,
        daemon=True,
        args=(fm,),
    )
    fm.rx_thread.start()
    
    # Give thread time to start
    sleep(0.05)
    return True


def serial_cleanup(fm: FactoryMode):
    """Safely cleanup serial connection and rx thread"""
    # Stop rx thread first
    if fm.rx_thread and fm.rx_thread.is_alive():
        fm.rx_thread_stop.set()
        fm.rx_thread.join(timeout=PROVISIONING_STOP_RX_WAIT_S)
        
        # Verify thread stopped
        if fm.rx_thread.is_alive():
            logging.error("rx thread did not stop - forcing serial close anyway")
            # Thread is stuck, but we need to close the port
            # The thread will crash when it tries to access the closed port
    
    # Now safe to close serial port
    with fm.serial_lock:
        if hasattr(fm.ser, "is_open") and fm.ser.is_open:
            try:
                fm.ser.close()
                logging.debug("Serial port closed successfully")
            except Exception as e:
                logging.error(f"Error closing serial port: {e}")


def switch_baudrate_if_needed(fm: FactoryMode, serial_port: str, new_baudrate: int):
    """Switch serial baudrate if different from current"""
    if new_baudrate != fm.serial_baudrate:
        logging.info(f"Switching baudrate from {fm.serial_baudrate} to {new_baudrate}")

        # Reinitialize with new baudrate (this handles thread management)
        serial_initialization(serial_port, fm, new_baudrate)

        # Small delay to ensure clean initialization
        sleep(0.2)

        return True
    return False
