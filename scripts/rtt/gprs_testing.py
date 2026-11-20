import argparse
from colorama import Fore, Style
import queue
import logging
import json
from scripts.rtt import factory_mode as factory_mode
from scripts.rtt import wirepas_provisioning
from struct import pack, unpack
import sys
import cbor2
from scripts.rtt.wirepas_provisioning import WirepasProvisioning
from threading import Thread, Event
import threading
from struct import pack, unpack
from enum import Enum, IntEnum
from time import sleep
import time
import serial
from threading import Timer
import os
import re
import datetime
from utility.communication import Communication as Commun
import openpyxl
from openpyxl.utils import get_column_letter
import threading
import tkinter as tk
from tkinter import scrolledtext
from scripts.rtt import db_connect
from colorama import Fore, Style, init

init(autoreset=True)

# ---------- EXCEL LOGGING ----------
def write_to_excel(pcb_serial, pcb_serial_no_test_status, nic_pcb_Serial_no, nic_pcb_serial_no_test_status, debug_status, rf_test_status,GPRS_SIM1_TEST_STATUS,GPRS_SIM2_TEST_STATUS, overall_result):
    """
    Writes the test results to an Excel file.
    If the file doesn't exist, it creates it and adds headers.
    Serial numbers are auto-incremented.
    """
    # Check if the Excel file exists
    starttime = datetime.datetime.now()
    if os.path.exists(EXCEL_FILE):
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        # Create headers
        headers = ["Serial No", "Date_Time","PCB Serial No", "NIC PCB Serial No","PCB Serial No Test Status", "NIC PCB Serial No Test Status","Transparent Mode status", "RF Test Status","GPRS SIM1 TEST STATUS","GPRS SIM2 TEST STATUS", "Overall Result"]
        for col, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=header)

    # Calculate next serial number based on existing rows
    next_row = ws.max_row + 1
    serial_no = next_row - 1  # subtract 1 for header row

    def sanitize_excel_string(s):
        # Remove illegal characters (ASCII control characters 0x00-0x1F except tab/newline/carriage return)
        s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", s)
        # Optionally, trim if too long
        if len(s) > 100:  # choose max length suitable for your case
            s = s[:100]
        return s

    # Fill the data
    ws.cell(row=next_row, column=1, value=serial_no)
    ws.cell(row=next_row, column=2, value=sanitize_excel_string(str(starttime)))
    ws.cell(row=next_row, column=3, value=sanitize_excel_string(str(pcb_serial)))
    ws.cell(row=next_row, column=4, value=sanitize_excel_string(str(nic_pcb_Serial_no)))
    ws.cell(row=next_row, column=5, value=sanitize_excel_string(str(pcb_serial_no_test_status)))
    ws.cell(row=next_row, column=6, value=sanitize_excel_string(str(nic_pcb_serial_no_test_status)))
    ws.cell(row=next_row, column=7, value=sanitize_excel_string(str(debug_status)))
    ws.cell(row=next_row, column=8, value=sanitize_excel_string(str(rf_test_status)))
    ws.cell(row=next_row, column=9, value=sanitize_excel_string(str(GPRS_SIM1_TEST_STATUS)))
    ws.cell(row=next_row, column=10,value=sanitize_excel_string(str(GPRS_SIM2_TEST_STATUS)))
    ws.cell(row=next_row, column=11,value=sanitize_excel_string(str(overall_result)))

    # Save the workbook
    wb.save(EXCEL_FILE)
    wb.close()



class SignalAcceptanceCriteria:
    RSRP_MIN_DBM = -95
    RSRQ_MIN_DB = -20


class WirepasParams:
    KEY_SIZE = 16
    MINIMUM_NETWORK_ADDRESS = 1
    MAXIMUM_NETWORK_ADDRESS = 0xFFFFFF
    MINIMUM_NETWORK_CHANNEL = 1
    MAXIMUM_NETWORK_CHANNEL = 12
    MINIMUM_NODE_ADDRESS = 1
    MAXIMUM_NODE_ADDRESS = 0xFFFFFFFB

    def validate_key(key: str) -> bytes:
        byte_data = bytes.fromhex(key)
        if len(byte_data) != WirepasParams.KEY_SIZE:
            raise argparse.ArgumentTypeError(
                "Given key must be " + str(WirepasParams.KEY_SIZE) + " bytes long"
            )
        return byte_data

    def validate_network_address(network_address: str) -> int:
        network_address = int(network_address, 0)
        if network_address not in range(
            WirepasParams.MINIMUM_NETWORK_ADDRESS,
            WirepasParams.MAXIMUM_NETWORK_ADDRESS + 1,
        ):
            raise argparse.ArgumentTypeError("Given Network Address is out of range")
        return network_address

    def validate_network_channel(network_channel: str) -> int:
        network_channel = int(network_channel, 0)
        if network_channel not in range(
            WirepasParams.MINIMUM_NETWORK_CHANNEL,
            WirepasParams.MAXIMUM_NETWORK_CHANNEL + 1,
        ):
            raise argparse.ArgumentTypeError("Given Network Channel is out of range")
        return network_channel

    def validate_node_address(node_address: str) -> int:
        node_address = int(node_address, 0)
        if (
            node_address < WirepasParams.MINIMUM_NODE_ADDRESS
            or node_address > WirepasParams.MAXIMUM_NODE_ADDRESS
        ):
            raise argparse.ArgumentTypeError("Given Node Address is out of range")

        if (node_address & 0xFF000000) == 0x80000000:
            raise argparse.ArgumentTypeError(
                "Given Node Address is in the multicast address range"
            )

        return node_address


class SimParams:
    SIM_USER_MAX_LEN = 22
    SIM_PWD_MAX_LEN = 21
    SIM_APN_MAX_LEN = 51
    SIM_PIN_LENGTH = 10
    SIM_PUK_LENGTH = 10

    IMEI_LENGTH = 16
    IMSI_LENGTH = 16


class SimId(Enum):
    SIM1 = 0
    SIM2 = 1


class TestStatus(IntEnum):
    SUCCESS = 0
    UNTESTED = 1
    FAILED = 2


# RX_RSSI_THRESHOLD_DBM = config["rf_rx_rssi_dbm"]
# TX_RSSI_THRESHOLD_DBM = config["rf_tx_rssi_dbm"]

# # Constants for cellular test retry logic
# CELLULAR_TEST_MAX_RETRIES = config["gprs_test_retry"]
RESET_WAIT_TIME_S = 0.5


class TestSummary:
    def __init__(self, test_name, status, duration, rx_rssi=None, tx_rssi=None):
        self.test_name = test_name
        self.status = status
        self.duration = duration
        self.rx_rssi = rx_rssi
        self.tx_rssi = tx_rssi
        self.retry_count = 0  # Track number of retries

    def set_status(self, status: TestStatus):
        self.status = status

    def print_summary(self):
        retry_info = f" (after {self.retry_count} retries)" if self.retry_count > 0 else ""
        result_str = f"{'✅ Success ✅' if self.status == TestStatus.SUCCESS else '❌ Failed ❌'}{retry_info} (took {self.duration:.2f}s)"
        # Calculate the padding needed to right-justify at 80 characters
        justified_result = result_str.rjust(
            80 - len(self.test_name) - 7
        )  # 7 accounts for " Test: "
        print(f"{self.test_name} Test: {justified_result}")
        logging.info(f"{self.test_name} Test: {justified_result}")

        # Print RSSI values if available
        # if self.rx_rssi is not None and self.tx_rssi is not None:
        #     print(f"\t├ RX RSSI: {self.rx_rssi} dBm")
        #     print(f"\t└ TX RSSI: {self.tx_rssi} dBm")


class CellularTestSelection(IntEnum):
    SKIP = 0
    SIM = 1
    DATA_CONNECTION = 2


class RfSummaryTestingResult(TestSummary):
    rx_rssi = None
    tx_rssi = None
    
    def __init__(self, test_name: str, status: TestStatus, duration: float):
        super().__init__(test_name, status, duration)
    
    def print_rf_summary(self):
        if self.rx_rssi is None or self.tx_rssi is None:
            return

        print(f"\t├ RX RSSI: {self.rx_rssi} dBm")
        print(f"\t└ TX RSSI: {self.tx_rssi} dBm")
        logging.info(f"\t├ RX RSSI: {self.rx_rssi} dBm")
        logging.info(f"\t└ TX RSSI: {self.tx_rssi} dBm")


class CellularTestingResult(TestSummary):
    test_type = None
    imei = ""
    imsi = ""
    rsrp = 0
    rsrq = 0
    valid_measurements = False

    def __init__(self, test_name: str, status: TestStatus, duration: float):
        super().__init__(test_name, status, duration)
        
    
    def set_test_type(self, test_type: CellularTestSelection):
        self.test_type = test_type

    @classmethod
    def from_bytes(cls, data, name="Cellular"):
    # def from_bytes(cls, data):
        instance = cls(name, TestStatus.UNTESTED, 0)
        format_str = f"<B{SimParams.IMEI_LENGTH}s{SimParams.IMSI_LENGTH}shh?"
        unpacked_data = unpack(format_str, data)
        instance.test_type = CellularTestSelection(unpacked_data[0])
        instance.imei = unpacked_data[1].decode("utf-8").rstrip("\x00")
        instance.imsi = unpacked_data[2].decode("utf-8").rstrip("\x00")
        instance.rsrp = unpacked_data[3]
        instance.rsrq = unpacked_data[4]
        instance.valid_measurements = unpacked_data[5]

        if instance.test_type == CellularTestSelection.SKIP:
            instance.status = TestStatus.SUCCESS
        return instance

    def print_cellular_details(self):
        test_type_info = ""
        if self.test_type is not None:
            if self.test_type == CellularTestSelection.SKIP:
                test_type_info = " [SKIPPED]"
            elif self.test_type == CellularTestSelection.SIM:
                test_type_info = " [SIM]"
            elif self.test_type == CellularTestSelection.DATA_CONNECTION:
                test_type_info = " [DATA CONNECTION]"
        
        print(f"\t├ {test_type_info}")

        if self.test_type == CellularTestSelection.SKIP:
            return
        
        print(f"\t├ IMEI: {self.imei}")
        print(f"\t├ IMSI: {self.imsi}")
        if self.test_type == CellularTestSelection.DATA_CONNECTION:
            print(f"\t├ RSRP: {self.rsrp} dBm")
            print(f"\t├ RSRQ: {self.rsrq} dB")
            print(
                f"\t└ Valid Signal Measurements: {'Yes' if self.valid_measurements else 'No'}"
            )



class TestResults:
    def __init__(self):
        self.cellular_results_sim1 = None
        self.cellular_results_sim2 = None
        self.gpio_result = None
        self.ext_flash_result = None
        self.rf_result = None

        self.cellular_sim_1_success = False
        self.cellular_sim_2_success = False
        self.gpio_success = False
        self.ext_flash_success = False
        self.rf_success = False
        self.rx_rssi = 0
        self.tx_rssi = 0

        self.cellular_summary_sim_1 = CellularTestingResult("Cellular SIM1", TestStatus.UNTESTED, 0)
        self.cellular_summary_sim_2 = CellularTestingResult("Cellular SIM2", TestStatus.UNTESTED, 0)
        self.ext_flash_summary = TestSummary("External Flash", TestStatus.UNTESTED, 0)
        self.rf_summary = RfSummaryTestingResult("RF", TestStatus.UNTESTED, 0)

    def print_results(self):
        print("_" * 80)
        print("Test Results Summary".center(80))
        logging.info("Test Results Summary")
        print()

        # Cellular SIM 1 Test Results
        self.cellular_summary_sim_1.print_summary()
        # if self.cellular_summary_sim_1.status == TestStatus.SUCCESS:
        self.cellular_summary_sim_1.print_cellular_details()

        # Cellular SIM 2 Test Results
        self.cellular_summary_sim_2.print_summary()
        # if self.cellular_summary_sim_2.status == TestStatus.SUCCESS:
        self.cellular_summary_sim_2.print_cellular_details()

        # External Flash Test Results
        self.ext_flash_summary.print_summary()

        # # RF Test Results
        self.rf_summary.print_summary()
        # # if self.rf_summary.status == TestStatus.SUCCESS:
        self.rf_summary.print_rf_summary()


class Communication:
    TIMEOUT_RSP_TESTING_CELLULAR_S = 120
    TIMEOUT_RSP_TESTING_EXT_FLASH_S = 10
    TIMEOUT_RSP_TESTING_GPIO_S = 6
    TIMEOUT_RSP_TESTING_RF_S = 55
    READ_PARAMETERS_TIMEOUT_S = 2
    STOP_FACTORY_MODE_TIMEOUT_S = 2

    fm = factory_mode.FactoryMode()

    cellular_testing_queue = queue.Queue()
    sim_testing_queue = queue.Queue()
    gpio_testing_queue = queue.Queue()
    ext_flash_testing_queue = queue.Queue()
    rf_testing_queue = queue.Queue()
    read_parameters_queue = queue.Queue()
    stop_factory_mode_queue = queue.Queue()


nic_com = Communication()


def parse_message_received(type: factory_mode.MessageType, data: bytes):
    if type == factory_mode.MessageType.TESTING_CELLULAR_RESPONSE:
        logging.debug("Cellular testing received!")
        nic_com.cellular_testing_queue.put_nowait(data)
    elif type == factory_mode.MessageType.TESTING_GPIO_RESPONSE:
        logging.debug("GPIO testing received!")
        nic_com.gpio_testing_queue.put_nowait(data)
    elif type == factory_mode.MessageType.TESTING_EXT_FLASH_RESPONSE:
        logging.debug("External flash testing received!")
        nic_com.ext_flash_testing_queue.put_nowait(data)
    elif type == factory_mode.MessageType.TESTING_RF_RESPONSE:
        logging.debug("RF testing received!")
        nic_com.rf_testing_queue.put_nowait(data)
    elif type == factory_mode.MessageType.PROVISIONING_READ_RESPONSE:
        logging.debug("Read Request Response Received")
        nic_com.read_parameters_queue.put_nowait(data)
    elif type == factory_mode.MessageType.STOP_FACTORY_MODE_AND_RESET_RESPONSE:
        logging.debug("Stop Factory Mode and Reset Response Received")
        nic_com.stop_factory_mode_queue.put_nowait(True)
    else:
        logging.warning("Unknown type received: %s", type)


def filter_version_info(nic_params: dict) -> dict:
    """Filter parameters to only include version information (NicInfoDataIds)"""
    version_keys = [
        "DEV_EUI64",
        "APP_VER",
        "STACK_VER",
        "GW_IMEI",
        "GW_SIM1_IMSI",
        "GW_SIM1_ICCID",
        "GW_SIM2_IMSI",
        "GW_SIM2_ICCID",
        "GW_CORE_VER",
        "GW_MAIN_VER",
        "GW_SINK_APP_VER",
        "GW_MODEM_FIRMWARE_VER",
        "GW_METER_LIB_VER"
    ]

    version_info = {}
    for key, value in nic_params.items():
        if key in version_keys:
            version_info[key] = value

    return version_info


def print_version_summary(version_info: dict):
    """Print version summary using the same format as read_parameters"""
    summary = "\n\n\tNIC Version Information Summary:\n"
    summary += "_" * 80 + "\n"
    summary += "\n".join("{!r}: {!r}".format(k, v) for k, v in version_info.items())
    summary += "\n" + "_" * 80 + "\n"
    logging.info(summary)


def read_nic_version_info_for_testing(com: Communication):
    """Read only NIC version information using the existing factory mode connection"""
    try:
        nic_parameters_data = {}
        logging.info("Sending request to read NIC Parameters")
        if (
            factory_mode.send_factory_mode_message(
                com.fm, bytes(), factory_mode.MessageType.PROVISIONING_READ_REQUEST
            )
            is False
        ):
            if (
                factory_mode.send_factory_mode_message(
                com.fm, bytes(), factory_mode.MessageType.PROVISIONING_READ_REQUEST
                )
                is False
            ):
                logging.error("Sending Read Parameters Request not successful!")
                return

        try:
            nic_parameters_data = com.read_parameters_queue.get(
                timeout=com.READ_PARAMETERS_TIMEOUT_S
            )
        except queue.Empty:
            logging.error("Read Parameters response was not received in the given timeout!")
            return

        # Decode the full parameter data
        nic_parameters_data = wirepas_provisioning.decode_prov_dict(nic_parameters_data)
        print(nic_parameters_data)
        # Filter to show only version information
        version_info = filter_version_info(nic_parameters_data)
        print(version_info)
        if version_info:
            print_version_summary(version_info)
        else:
            logging.warning("No version information found in device response!")
        return nic_parameters_data

    except Exception as e:
        logging.error(f"Failed to read NIC version information: {e}")
        return None

def reset_device_and_reenter_factory_mode(com: Communication, serial_port: str, baudrate: int):
    """Reset the device and re-enter factory mode"""
    logging.info("🔄 Resetting device and re-entering factory mode...")

    try:
        # Send stop factory mode and reset command with 0 second delay (immediate reset)
        if hasattr(com.fm.ser, 'is_open') and com.fm.ser.is_open:
            # Clear the queue before sending command
            with com.stop_factory_mode_queue.mutex:
                com.stop_factory_mode_queue.queue.clear()
            
            # Reuse stop_factory_mode_and_reset with 0 delay
            if not stop_factory_mode_and_reset(com):
                logging.debug("Could not send STOP_FACTORY_MODE_AND_RESET command, will try serial reinitialization")
            else:
                sleep(1.0)  # Give time for the device to reset

        # Reinitialize the serial connection (this handles stopping threads and closing ports)
        factory_mode.serial_initialization(serial_port, com.fm, baudrate)

        # Wait for the device to fully reset and boot up
        sleep(RESET_WAIT_TIME_S)

        # Re-enter factory mode with the challenge/response loop
        factory_mode.wait_for_challenge_response_with_reset_loop(com.fm)

        logging.info("✅ Successfully re-entered factory mode")
        return True

    except Exception as e:
        logging.error(f"❌ Failed to reset device and re-enter factory mode: {e}")
        return False

def stop_factory_mode_and_reset(com: Communication, delay_s: int = 0):
    """
    Send command to stop factory mode and reset after specified delay
    
    Args:
        com: Communication object
        delay_s: Delay in seconds before reset
    """
    logging.info(f"Sending request to stop factory mode and reset in {delay_s} seconds")
    
    # Encode delay as CBOR
    delay_data = cbor2.dumps(delay_s)
    stop_success = False
    
    if (
        factory_mode.send_factory_mode_message(
            com.fm, delay_data, factory_mode.MessageType.STOP_FACTORY_MODE_AND_RESET
        )
        is False
    ):
        factory_mode.error_print_and_exit(
            com.fm,
            "Sending Stop Factory Mode and Reset request not successful!",
            factory_mode.ExitCodes.SENDING_FAILED,
        )
        factory_mode.serial_cleanup(com.fm)
        return False
    
    # Wait for acknowledgment
    try:
        stop_success = com.stop_factory_mode_queue.get(
            timeout=com.STOP_FACTORY_MODE_TIMEOUT_S
        )
    except queue.Empty:
        factory_mode.error_print_and_exit(
            com.fm,
            "Stop Factory Mode and Reset response not received in the given timeout!",
            factory_mode.ExitCodes.RECEPTION_TIMEOUT,
        )
        factory_mode.serial_cleanup(com.fm)
        return False
    
    if stop_success:
        logging.info(f"Device will reset in {delay_s} seconds")
    
    
    factory_mode.serial_cleanup(com.fm)
    return True

def create_cellular_testing_payload(test_type, sim_id, user, pwd, apn, pin, puk):
    user = user.encode("utf-8").ljust(SimParams.SIM_USER_MAX_LEN, b"\0")
    pwd = pwd.encode("utf-8").ljust(SimParams.SIM_PWD_MAX_LEN, b"\0")
    apn = apn.encode("utf-8").ljust(SimParams.SIM_APN_MAX_LEN, b"\0")
    pin = pin.encode("utf-8").ljust(SimParams.SIM_PIN_LENGTH, b"\0")
    puk = puk.encode("utf-8").ljust(SimParams.SIM_PUK_LENGTH, b"\0")

    payload = pack(
        f"<BB{SimParams.SIM_USER_MAX_LEN}s{SimParams.SIM_PWD_MAX_LEN}s{SimParams.SIM_APN_MAX_LEN}s{SimParams.SIM_PIN_LENGTH}s{SimParams.SIM_PUK_LENGTH}s",
        test_type,
        sim_id,
        user,
        pwd,
        apn,
        pin,
        puk,
    )
    return payload


def perform_single_cellular_test(
    com: Communication,
    test_type: CellularTestSelection,
    sim_id: SimId,
    user: str,
    pwd: str,
    apn: str,
    pin: str,
    puk: str,
) -> tuple[bool, CellularTestingResult]:
    try:
        """Perform a single cellular test attempt"""
        test_type_str = "SKIP" if test_type == CellularTestSelection.SKIP else \
                        "SIM" if test_type == CellularTestSelection.SIM else "DATA CONNECTION"
        logging.info(f"📶 Starting Cellular Testing ({test_type_str}) on {sim_id.name} 📶")
        payload = create_cellular_testing_payload(test_type, sim_id.value, user, pwd, apn, pin, puk)
        logging.debug(payload)

        if not factory_mode.send_factory_mode_message(
            com.fm, payload, factory_mode.MessageType.TESTING_CELLULAR_REQUEST
        ):
            logging.error("Failed to send cellular testing message")
            return False, None

        try:
            cellular_test_data = com.cellular_testing_queue.get(
                timeout=com.TIMEOUT_RSP_TESTING_CELLULAR_S
            )
        except queue.Empty:
            # cellular_test_result = CellularTestingResult.from_bytes(cellular_test_data, f"Cellular {sim_id.name}")
            # print(f"Received cellular test result this for deactivated sim: {cellular_test_result.__dict__}, {cellular_test_result}, ----------------------")
            logging.error("RSP_TEST_CELLULAR was not received in the given timeout!")
            return False, None
        cellular_test_result = CellularTestingResult.from_bytes(cellular_test_data, f"Cellular {sim_id.name}")
        # cellular_test_result = CellularTestingResult.from_bytes(cellular_test_data)
        
        # Determine success based on test type
        if test_type == CellularTestSelection.SKIP:
            success = True
        elif test_type == CellularTestSelection.SIM:
            # SIM test succeeds if we got IMEI and IMSI
            success = bool(cellular_test_result.imei and cellular_test_result.imsi)
        else:  # CellularTestSelection.DATA_CONNECTION
            success = cellular_test_result.valid_measurements
        return success, cellular_test_result
    except Exception as e:
        logging.error(f"Error in perform singular cellular test: {str(e)}, for com: {com}")
        return "False", {}

def perform_cellular_testing(
    com: Communication,
    test_type: CellularTestSelection,
    sim_id: SimId,
    user: str,
    pwd: str,
    apn: str,
    pin: str,
    puk: str,
    results: TestResults,
    serial_port: str,
    CELLULAR_TEST_MAX_RETRIES: int) -> bool:

    """Perform cellular testing with retry logic"""
    start_time = time.time()
    print(f"in sim {sim_id} test start")
    success = False
    cellular_test_result = None
    retry_count = 0
    max_retries = 1
	# Skip test doesn't need retries
    if str(sim_id.name) == "SIM1":
        max_retries = 1 if test_type == CellularTestSelection.SKIP else CELLULAR_TEST_MAX_RETRIES
    else:
        max_retries = 1
    for attempt in range(max_retries):
        logging.info(f"🔄 Cellular test attempt {attempt + 1}/{max_retries}")
        if attempt > 0:
            logging.info(f"🔄 Cellular test attempt {attempt + 1}/{max_retries}")

            retry_count = attempt

            # Reset device and re-enter factory mode for retry attempts
            if not reset_device_and_reenter_factory_mode(com, serial_port, 9600):
                if not reset_device_and_reenter_factory_mode(com, serial_port, 9600):
                    logging.error(f"Failed to reset device for retry attempt {attempt + 1}")
                    print(f"Failed to reset device for retry attempt {attempt + 1}")
                continue

        # sleep(20.0)
        # Clear any existing messages in the queue before the test
        with com.cellular_testing_queue.mutex:
            com.cellular_testing_queue.queue.clear()

        # Perform the cellular test
        success, cellular_test_result = perform_single_cellular_test(
            com, test_type, sim_id, user, pwd, apn, pin, puk
        )

        if success:
            logging.info(f"✅ Cellular test succeeded on {sim_id.name} (attempt {attempt + 1})")
            print(f"✅ Cellular test succeeded on {sim_id.name} (attempt {attempt + 1})")
            break
        else:
            logging.warning(f"❌ Cellular test failed on {sim_id.name} (attempt {attempt + 1})")
            print(f"❌ Cellular test failed on {sim_id.name} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                logging.info("Will retry after device reset...")

	# Store results
    if cellular_test_result is None:
            cellular_test_result = CellularTestingResult(f"Cellular {sim_id.name}", TestStatus.FAILED, 0)


    if sim_id == SimId.SIM1:
        results.cellular_summary_sim_1 = cellular_test_result
        results.cellular_summary_sim_1.duration = time.time() - start_time
        results.cellular_summary_sim_1.retry_count = retry_count
        results.cellular_summary_sim_1.set_test_type(test_type)
        results.cellular_summary_sim_1.status = (
            TestStatus.SUCCESS if success else TestStatus.FAILED
        )
    else:
        results.cellular_summary_sim_2 = cellular_test_result
        results.cellular_summary_sim_2.duration = time.time() - start_time
        results.cellular_summary_sim_2.retry_count = retry_count
        results.cellular_summary_sim_2.set_test_type(test_type)
        results.cellular_summary_sim_2.status = (
            TestStatus.SUCCESS if success else TestStatus.FAILED
        )

    if not success and test_type != CellularTestSelection.SKIP:
        logging.error(f"❌ Cellular test failed after {max_retries} attempts")

    return success

def perform_ext_flash_testing(com: Communication, results: TestResults) -> bool:
    start_time = time.time()
    logging.info("💾 Starting External Flash Testing 💾")

    if not factory_mode.send_factory_mode_message(
        com.fm, bytes(), factory_mode.MessageType.TESTING_EXT_FLASH_REQUEST
    ):
        factory_mode.error_print_and_exit(
            com.fm,
            "Failed to send external flash testing message",
            factory_mode.ExitCodes.SENDING_FAILED,
        )

    try:
        ext_flash_data = com.ext_flash_testing_queue.get(
            timeout=com.TIMEOUT_RSP_TESTING_EXT_FLASH_S
        )
    except queue.Empty:
        results.ext_flash_summary.duration = time.time() - start_time
        factory_mode.error_print_and_exit(
            com.fm,
            "RSP_TEST_EXT_FLASH was not received in the given timeout!",
            factory_mode.ExitCodes.RECEPTION_TIMEOUT,
        )

    (ext_flash_res,) = unpack(">B", ext_flash_data)
    results.ext_flash_result = ext_flash_res
    results.ext_flash_summary.duration = time.time() - start_time
    results.ext_flash_summary.status = (
        TestStatus.SUCCESS if ext_flash_res else TestStatus.FAILED
    )
    return ext_flash_res

def perform_gpio_testing(com: Communication, results: TestResults) -> bool:
    start_time = time.time()
    logging.info("📍 Starting GPIO Testing 📍")

    if not factory_mode.send_factory_mode_message(
        com.fm, bytes(), factory_mode.MessageType.TESTING_GPIO_REQUEST
    ):
        factory_mode.error_print_and_exit(
            com.fm,
            "Failed to send GPIO testing message",
            factory_mode.ExitCodes.SENDING_FAILED,
        )

    try:
        gpio_test_data = com.gpio_testing_queue.get(
            timeout=com.TIMEOUT_RSP_TESTING_GPIO_S
        )
    except queue.Empty:
        results.gpio_summary.duration = time.time() - start_time
        factory_mode.error_print_and_exit(
            com.fm,
            "RSP_TEST_GPIO was not received in the given timeout!",
            factory_mode.ExitCodes.RECEPTION_TIMEOUT,
        )

    (gpio_res,) = unpack(">B", gpio_test_data)
    results.gpio_result = gpio_res
    results.gpio_summary.duration = time.time() - start_time
    results.gpio_summary.status = TestStatus.SUCCESS if gpio_res else TestStatus.FAILED
    return gpio_res

def create_rf_testing_payload(
    factory_mode_companion_app_addr: int,
    net_addr: int,
    net_chan: int,
    enc_key: bytes,
    auth_key: bytes,
    TX_RSSI_THRESHOLD_DBM: int,
    RX_RSSI_THRESHOLD_DBM: int
):
    return pack(
        "<LLB16s16sbb",
        factory_mode_companion_app_addr,
        net_addr,
        net_chan,
        enc_key,
        auth_key,
        TX_RSSI_THRESHOLD_DBM,
        RX_RSSI_THRESHOLD_DBM,
    )

def perform_rf_testing(
    com: Communication,
    factory_mode_companion_app_addr: int,
    net_addr: int,
    net_chan: int,
    enc_key: bytes,
    auth_key: bytes,
    TX_RSSI_THRESHOLD_DBM: int,
    RX_RSSI_THRESHOLD_DBM: int,
    results: TestResults,
) -> bool:
    start_time = time.time()
    logging.info("📶 Starting RF Testing 📶")
    payload = create_rf_testing_payload(
        factory_mode_companion_app_addr, net_addr, net_chan, enc_key, auth_key, TX_RSSI_THRESHOLD_DBM, RX_RSSI_THRESHOLD_DBM
    )
    logging.debug(payload)

    print(payload)

    if not factory_mode.send_factory_mode_message(
        com.fm, payload, factory_mode.MessageType.TESTING_RF_REQUEST
    ):
        results.rf_summary.duration = time.time() - start_time
        factory_mode.error_print_and_exit(
            com.fm,
            "Failed to send RF testing message", factory_mode.ExitCodes.SENDING_FAILED
        )
        return "Port is Not Connected", 0, 0

    try:
        rf_test_data = com.rf_testing_queue.get(timeout=com.TIMEOUT_RSP_TESTING_RF_S)
    except queue.Empty:
        results.rf_summary.duration = time.time() - start_time
        factory_mode.error_print_and_exit(
            com.fm,
            "TESTING_RF_RESPONSE was not received in the given timeout!",
            factory_mode.ExitCodes.RECEPTION_TIMEOUT,
        )
        return "Port is Not Connected", 0, 0

    results.rf_summary.duration = time.time() - start_time

    (
        results.rf_summary.rx_rssi,
        results.rf_summary.tx_rssi,
        results.rf_summary.status,
    ) = unpack(">bbB", rf_test_data)
    return (results.rf_summary.status == TestStatus.SUCCESS, results.rf_summary.rx_rssi, results.rf_summary.tx_rssi)

def validate_length_and_alnum(value, max_length, name):
    if len(value) > max_length:
        raise argparse.ArgumentTypeError(
            f"{name} exceeds maximum length of {max_length}"
        )
    if len(value) and not value.isalnum():
        raise argparse.ArgumentTypeError(
            f"{name} must contain only alphanumeric characters"
        )
    return value

def print_overall_test_result(total_duration, overall_success):
    print("_" * 80)
    print(f"\nTotal Testing Time: {total_duration:.2f} seconds")

    result_color = Fore.GREEN if overall_success else Fore.RED
    result_emoji = "✅" if overall_success else "❌"

    print(
        f"\nOverall Test Result: {result_color}{result_emoji} "
        + ("SUCCESS" if overall_success else "FAIL")
        + f" {result_emoji}{Style.RESET_ALL}"
    )
    print("\n")

def test_gateway(com_port, config):
    test_results = TestResults()
    RF_Test_status = 'Fail'
    test_results.rx_rssi = 0
    test_results.tx_rssi = 0
    GPRS_SIM1_TEST_STATUS = 'Fail'
    GPRS_SIM2_TEST_STATUS = 'Fail'
    IMG_VER = ''
    param_data = {}
    try:
        global nic_com
        nic_com.fm.parse_message_callback = parse_message_received

        if not factory_mode.serial_initialization(str(com_port), nic_com.fm, 9600):
            return "Port is Not Connected", test_results.rx_rssi, test_results.tx_rssi, GPRS_SIM1_TEST_STATUS, GPRS_SIM2_TEST_STATUS, ''
        if not factory_mode.wait_for_challenge_response_with_reset_loop(nic_com.fm):
            return "Port is Not Connected", test_results.rx_rssi, test_results.tx_rssi, GPRS_SIM1_TEST_STATUS, GPRS_SIM2_TEST_STATUS, ''

        # Read NIC version information before testing
        logging.debug("Reading NIC version information before testing...")
        param_data = read_nic_version_info_for_testing(nic_com)

        if param_data is None:
            logging.debug("Failed to read NIC parameters, cannot proceed with testing.")
            return "Port is Not Connected", test_results.rx_rssi, test_results.tx_rssi, GPRS_SIM1_TEST_STATUS, GPRS_SIM2_TEST_STATUS, ''

        IMG_VER = param_data.get("GW_CORE_VER", "")
        
        # sleep(5.0)
        start_time = time.time()
        test_results.ext_flash_success = perform_ext_flash_testing(nic_com, test_results)
        
        test_results.rf_success, test_results.rx_rssi, test_results.tx_rssi = perform_rf_testing(
        nic_com,
        int(str(config["test_router_address"]), 0),     # convert from hex/decimal string → int
        int(str(config["network_address"]), 0),
        int(str(config["network_channel"]), 0),
        bytes.fromhex(str(config["encryption_key"])),    # convert from hex string → bytes
        bytes.fromhex(str(config["authentication_key"])),
        int(config["rf_tx_rssi_dbm"]),
        int(config["rf_rx_rssi_dbm"]),
        test_results,
        )
        
        logging.info(f"RF Test Success: {test_results.rf_success}, RX RSSI: {test_results.rx_rssi} dBm, TX RSSI: {test_results.tx_rssi} dBm for COM: {com_port}")
        test_results.cellular_sim_1_success = perform_cellular_testing(
            nic_com,
            CellularTestSelection.DATA_CONNECTION,
            SimId.SIM1,
            config["sim1_user"],
            config["sim1_pwd"],
            config["sim1_apn"],
            config["sim1_pin"],
            config["sim1_puk"],
            test_results,
            str(com_port),
            config["gprs_test_retry"],
            # args.baudrate,
        )


        test_results.cellular_sim_2_success = perform_cellular_testing(
            nic_com,
            CellularTestSelection.DATA_CONNECTION,
            SimId.SIM2,
            config["sim2_user"],
            config["sim2_pwd"],
            config["sim2_apn"],
            config["sim2_pin"],
            config["sim2_puk"],
            test_results,
            str(com_port),
            config["gprs_test_retry"],
            # args.baudrate,
        )
        
        if not test_results.cellular_sim_2_success:
            logging.error("Cellular SIM 2 test failed")
            test_results.cellular_summary_sim_2.imei = param_data.get("GW_IMEI", "")
            test_results.cellular_summary_sim_2.imsi = param_data.get("GW_SIM2_IMSI", "")
        elif not test_results.cellular_sim_1_success:
            logging.info("Cellular SIM 1 test succeeded")
            test_results.cellular_summary_sim_1.imei = param_data.get("GW_IMEI", "")
            test_results.cellular_summary_sim_1.imsi = param_data.get("GW_SIM1_IMSI", "")
        elif (not test_results.cellular_sim_1_success) and (not test_results.cellular_sim_2_success):
            logging.error("Both Cellular SIM tests failed")
            test_results.cellular_summary_sim_1.imei = param_data.get("GW_IMEI", "")
            test_results.cellular_summary_sim_1.imsi = param_data.get("GW_SIM1_IMSI", "")
            test_results.cellular_summary_sim_2.imei = param_data.get("GW_IMEI", "")
            test_results.cellular_summary_sim_2.imsi = param_data.get("GW_SIM2_IMSI", "")
        else:
            pass

        logging.info(f"Sim Resullt for COM: {com_port}, SIM1: {test_results.cellular_summary_sim_1}, SIM2: {test_results.cellular_summary_sim_2}")


        total_duration = time.time() - start_time

        test_results.print_results()

        overall_success = (
            test_results.cellular_sim_1_success
            and test_results.cellular_sim_2_success
            and test_results.rf_success
        )

        print_overall_test_result(total_duration, overall_success)
        
        if('True' == str(test_results.rf_success)):
            RF_Test_status = 'Pass'
        else:
            if 'False' == str(test_results.rf_success):
                RF_Test_status = 'Fail'
            else:
                RF_Test_status = str(test_results.rf_success)


        if('True' == str(test_results.cellular_sim_1_success)):
            GPRS_SIM1_TEST_STATUS = 'Pass'
        else:
            GPRS_SIM1_TEST_STATUS = 'Fail'

        if('True' == str(test_results.cellular_sim_2_success)):
            GPRS_SIM2_TEST_STATUS = 'Pass'
        else:
            GPRS_SIM2_TEST_STATUS = 'Fail'



        # stop_factory_mode_and_reset(nic_com)
        #exit_factory_mode(nic_com)
        time.sleep(0.5)
        factory_mode.serial_cleanup(nic_com.fm)

        return RF_Test_status, test_results.rx_rssi, test_results.tx_rssi, GPRS_SIM1_TEST_STATUS, GPRS_SIM2_TEST_STATUS, IMG_VER
    except Exception as e:
        logging.error(f"Error in test gateway to get result: {str(e)}")
        return RF_Test_status, test_results.rx_rssi, test_results.tx_rssi, GPRS_SIM1_TEST_STATUS, GPRS_SIM2_TEST_STATUS, IMG_VER

def get_pcb_serial(serial_port, com):
    logging.debug(f"PORT {serial_port}: Starting process for PCB Serial number fetch")
    retryCnt = 3
    while (retryCnt):
        try:
            if not com.open():
                return None

            # Frame to send the command to get nic pcb number
            # body = bytes([
            #         0xaa, 0x1, 0xc7, 0x52, 0xc9,
            #         0xff, 0xff, 0xff, 0xff,
            #         0x4, 0x4, 0x8, 0xc7, 0x52, 0x0,
            #         0x0, 0x5, 0x60, 0x0, 0x1e, 0x20, 0x8f
            # ])
            body = bytes([
                    0xaa, 0x1, 0x4e, 0x47, 0xc9,
                    0xff, 0xff, 0xff, 0xff,
                    0x4, 0x4, 0x8, 0xc7, 0x52, 0x0,
                    0x0, 0xc, 0x7, 0x0, 0x1e, 0xae, 0x8d
                ])

            # Send the data
            com.send_data(body, expected_payload_len=2)
            logging.debug(f"Send Command to get PCBA Serial Numebr, attempt: {4-retryCnt}, for com: {serial_port}")

            # Wait for response
            response = com.read_response(timeout=5)
            logging.debug(f"get pcba serial numebr response: {response}, for com: {serial_port}")
            start_index = 12
            end_index = 39  # exclusive

            # Extract serial bytes
            serial_bytes = response[start_index:end_index]
            logging.debug(f"Successfully fetched PCBA Serial number, for com: {serial_port}")
            serial_num = serial_bytes.replace(b'\x00', b'').decode('ascii')
            logging.debug(f"PCBA Serial Number: {serial_num}, for com: {serial_port}")
            return serial_num
        except Exception as e:
            retryCnt -= 1
            logging.error(f"PORT {serial_port}: Error during PCB Serial number fetch, {str(e)}")        
    return None

def nic_pcb_number(serial_port, com):
    logging.debug(f"\nPORT {serial_port}: Starting process for NIC PCB Serial number fetch")
    retryCnt = 3
    while (retryCnt):
        try:
            if not com.open():
                return None

            # Frame to send the command to get nic pcb number
            # body = bytes([
            #         0xaa, 0x1, 0xd2, 0xfa, 0xc9,
            #         0xff, 0xff, 0xff, 0xff,
            #         0x4, 0x4, 0x2, 0xd2, 0xfa, 0xc9, 0xbe
            # ])
            body = bytes([
                    0xaa, 0x1, 0x4e, 0x47, 0xc9,
                    0xff, 0xff, 0xff, 0xff,
                    0x4, 0x4, 0x8, 0xc7, 0x52, 0x0, 0x0,
                    0xc, 0x27, 0x0, 0x1e, 0x99, 0xc3
                ])

            # Send the data
            com.send_data(body, expected_payload_len=2)
            logging.debug(f"Send Command to get NIC PCB Number, attempt: {4-retryCnt}, for com: {serial_port}")

            # Wait for response
            response = com.read_response(timeout=5)
            start_index = 12
            end_index = 39  # exclusive

            # Extract serial bytes
            serial_bytes = response[start_index:end_index]
            logging.debug(f"Successfully fetched NIC PCB Serial Number, for com: {serial_port}")
            nic_pcb_number = serial_bytes.decode('ascii')
            logging.info(f"PORT {serial_port}, NIC PCB Serial Number: {nic_pcb_number}")
            return nic_pcb_number

        except Exception as e:
            retryCnt -= 1
            logging.error(f"PORT {serial_port}: Error during NIC PCB Serial number fetch, {str(e)}")

    return None

def set_debug_print(serial_port, com):
    logging.debug(f"Sending Command to Set tunnel mode On, for com: {serial_port}")
    try:
        if not com.open():
            return None

        # Frame to send the command to on set_debug_print
        # body = bytes([
        #     0xaa, 0x1, 0x82, 0x35, 0xc9,
        #     0xff, 0xff, 0xff, 0xff,
        #     0x4, 0x4, 0x3, 0x82, 0x35, 0xbb, 0xd9, 0x78 ])
        body = bytes([
                0xaa, 0x01, 0x4e, 0x47, 0xc9,
                0xff, 0xff, 0xff, 0xff,
                0x4, 0x4, 0x3, 0x82, 0x35, 0xbb, 0xba, 0xa5 ])

        # Send the data
        com.send_data(body, expected_payload_len=2)
        logging.debug(f"Command sent to enable tunnel mode, for com: {serial_port}")
        # Wait for response
        response = com.read_response(timeout=5)

        pattern = bytes.fromhex("e8 03")
        if pattern in response:
            logging.debug(f"tunnel mode is on, for com: {serial_port}")
            return True
        else:
            logging.debug(f"Error to Set Tunnel mode On response: {response}, for com: {serial_port}")
            return False
    except Exception as e:
        logging.error(f"Port {serial_port}, SET TUNNEL MODE ON Error: {str(e)}")
    return False

def tap_cmd_send(com_port):

    try:
        com = Commun(str(com_port))
    except serial.SerialException:
        logging.error(f"COM{com_port} not available or cannot be opened.")
        return 0
    
    pcb_Serial_no = None
    pcb_serial_test_status = 'Fail'
    nic_pcb_serial_no_test_status = "Fail"
    nic_pcb_Serial_no = None
    debug_status = 'Fail'
    debug_test = False

    pcb_Serial_no = get_pcb_serial(com_port, com)
    if pcb_Serial_no is None:
        pcb_serial_test_status = "Fail"
        pcb_Serial_no = 0
        com.close()
        return 0
    else:
        pcb_serial_test_status = "Pass"
        logging.debug(f"Meter PCB Serial No: {pcb_Serial_no}, for com: {com_port}")

    calibration_result = db_connect.fetch_by_pcb_serial(pcb_Serial_no)

    if not calibration_result:
        logging.info(
            f"Calibration failed for com: {com_port}, PCB: {pcb_Serial_no}, "
            f"Calibration overall_result: {calibration_result!r} -- skipping RTT test for this meter"
        )

    if calibration_result:
        
        nic_pcb_Serial_no = nic_pcb_number(com_port, com)
        if nic_pcb_Serial_no is None:
            nic_pcb_serial_no_test_status = "Fail"
            nic_pcb_Serial_no = 0
            com.close()
            return 0
        else:
            nic_pcb_serial_no_test_status = "Pass"
            logging.debug(f"Meter NIC PCB Serial No: {nic_pcb_Serial_no}, for com: {com_port}")
        
        debug_test = set_debug_print(com_port, com)
        if not debug_test:
            debug_status = "Fail"
            com.close()
            return 0
        else:
            debug_status = "Pass"
            logging.debug(f"Meter transparent mode enable: ok, for com: {com_port}")
        
    # ser.close()
    com.close()
    return pcb_Serial_no, pcb_serial_test_status, calibration_result, nic_pcb_Serial_no, nic_pcb_serial_no_test_status, debug_status

class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def run_test(port, config):
    """
    Run the complete RF + SIM + PCB test for the given port.
    Example: result = run_test("4") or result = run_test(4)
    Returns a dictionary with all results.
    """
    try:
        print(f"\n===== Starting Test for {port} =====")
        overall_result = main_function(port, config)
        logging.info(f"Overall Result of RTT:{overall_result}, for com: {port}")
        print(f"===== Test Completed for {port} =====\n")
        return overall_result
    except Exception as e:
        print(f"❌ Exception during test on {port}: {e}")
        return {
            "port": f"{port}",
            "overall_result": "Fail",
            "error": str(e)
        }

def disable_debug_mode(com_port):
    # try:
    # Try opening serial port
    ser = serial.Serial(str(com_port), 9600, timeout=10)
    # Data to send
    data_to_send1 = bytes.fromhex('AA BB CC DD')
    

    # expected_response1 = 'aaffffffff1c752c91341effffffffffffffffffffffffffffffffffffffffffffffffffffffffffff052'
    retry_count = 3
    while(retry_count):
        # Send data
        ser.reset_input_buffer()  
        ser.write(data_to_send1)
        logging.debug(f"Data sent on serial port: {data_to_send1}")
        time.sleep(0.5)
        retry_count = retry_count - 1
    # except serial.SerialException:
    #     print(f"Unknown Error occurred while disable the debug mode for COM{com_port} ")
          # return 0  # return early, no port

       

# Modify main_function to return structured result
def main_function(port, config):
    disable_debug_mode(port)
    logging.debug(f"debug mode is cosed, for com: {port}")
    result = tap_cmd_send(port)
    if result == 0:
        overall_result = "Fail"
        return {
            "port": f"{port}",
            "pcb_serial_no": f"{port}",
            'calib_status': False,
            "nic_serial_no": f"{port}",
            "pcb_serial_test_status": 'Fail',
            "nic_serial_test_status": 'Fail',
            "debug_status": 'Fail',
            "rssi-rx": 0,
            "rssi-tx": 0,
            "rf_test_status": 'Fail',
            "sim1_status": 'Fail',
            "sim2_status": 'Fail',
            "img_ver": '',
            "overall_result": overall_result
        }

    pcb_Serial_no, pcb_serial_test_status, calib_status, nic_pcb_Serial_no, nic_pcb_serial_no_test_status, debug_status = result

    if calib_status:
        RF_Test_status, rx_rssi, tx_rssi, GPRS_SIM1_TEST_STATUS, GPRS_SIM2_TEST_STATUS, IMG_VER = test_gateway(port, config)
        disable_debug_mode(port)
    else:
        RF_Test_status, rx_rssi, tx_rssi, GPRS_SIM1_TEST_STATUS, GPRS_SIM2_TEST_STATUS, IMG_VER = 'fail', 0, 0, 'fail', 'fail', 'fail'

    overall_result = "Pass" if (
        pcb_serial_test_status.lower() == "pass"
        and debug_status.lower() == "pass"
        and RF_Test_status.lower() == "pass"
        and GPRS_SIM1_TEST_STATUS.lower() == "pass"
        and GPRS_SIM2_TEST_STATUS.lower() == "fail"
        and nic_pcb_serial_no_test_status.lower() == "pass"
    ) else "Fail"

    return {
        "port": f"{port}",
        "pcb_serial_no": pcb_Serial_no,
        "nic_serial_no": nic_pcb_Serial_no,
        "pcb_serial_test_status": pcb_serial_test_status,
        'calib_status': calib_status,
        "nic_serial_test_status": nic_pcb_serial_no_test_status,
        "debug_status": debug_status,
        "rssi-rx": rx_rssi,
        "rssi-tx": tx_rssi,
        "rf_test_status": RF_Test_status,
        "sim1_status": GPRS_SIM1_TEST_STATUS,
        "sim2_status": GPRS_SIM2_TEST_STATUS,
        "img_ver": IMG_VER,
        "overall_result": overall_result
    }



def show_results_popup(results_list):
    root = tk.Tk()
    root.title("IMG Testing Failures")

    # --- Set window size and center it ---
    window_width = 700
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.resizable(False, False)

    # Title label
    tk.Label(root, text="IMG Testing Failures", font=("Arial", 20, "bold")).pack(pady=15)

    # Scrolled text for results
    # Use fill='both' and expand=True so it takes up the remaining vertical space
    # but still allows the button Frame to be packed at the bottom.
    text_area = scrolledtext.ScrolledText(root, width=80, height=1, font=("Arial", 14), wrap=tk.WORD)
    text_area.pack(side='top', fill='both', expand=True, padx=20, pady=(0, 10))

    # Insert results like COM4 = Pass
    for port, result in results_list:
        text_area.insert(tk.END, f"{port} = {result}\n")
    text_area.config(state='disabled')

    # ----------------------------------------------------
    # Frame for the OK button (to guarantee it's at the bottom)
    # ----------------------------------------------------
    button_frame = tk.Frame(root)
    button_frame.pack(side='bottom', fill='x', pady=(0, 20)) # Pack the frame at the bottom

    # OK button at the bottom center
    ok_button = tk.Button(
        button_frame, # Pack the button inside the new frame
        text="OK",
        font=("Arial", 16, "bold"),
        width=20,
        height=2,
        command=root.destroy
    )
    # Use .pack() without side='bottom' inside the frame to center it
    ok_button.pack(pady=0)

    root.mainloop()
# ---------------------



if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s", level=logging.DEBUG)
    logging.info("Starting testing...")
  



    