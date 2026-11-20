"""
Implements the packet reader of Maxwell board. This utility
should be used when an FTDI cable is attached to the Rx/Tx
lines of the Maxwell board, and a laptop is being used
to read the packets sent by the Maxwell board.

The run() method is the entry point of the maxwell-packet-monitor

The parser is implemented as a state machine; the parser can
be in three possible state:
    1. STATE_IDLE: when the parser is waiting to receive a start byte (0xAA)
    2. STATE_IN_PROGRESS: when the parser has received 0xAA and is waiting to\
            receive a total of 58 bytes (including the start byte)
    3. STATE_RECEIVED: when the parser has received 58 bytes (including start byte)\
            and when it has been verified that the CRC of the incoming \
            packet is consistent
"""
import crc16
import argparse
import serial
from maxwell_packet import MaxwellPacket
from colorama import Fore

STATE_IDLE = 0
STATE_IN_PROGRESS = 1
STATE_RECEIVED = 2

START_BYTE = 0xAA
NUM_BYTES_IN_PACKET = 58


def run():
    parser = argparse.ArgumentParser( \
        description=("Allows to monitor the packets coming from maxwell board."
                     "Attach the FTDI cable to the Maxwell board and use "
                     "this utility to monitor the packets sent by the Maxwell board.")
    );
    parser.add_argument('-d', '--device', default='/dev/gp-gateway', \
            help='Device filename of the FTDI cable. Default is /dev/gp-gateway');
    parser.add_argument('-b', '--baud', default=2400, \
            help='Baud rate to use to communicate with Maxwell board. Default is 2400');
    args = parser.parse_args()
    ser = serial.Serial(args.device, args.baud, timeout=3)

    num_bytes_received = 0
    state = STATE_IDLE
    # stream is a container for all incoming bytes. Whenever 58 bytes
    # are received in stream, it is again initialized to an empty
    # bytearray()
    stream = bytearray()

    while True:
        if state == STATE_IDLE:
            x = ser.read()
            if x == '':
                # when ser.read() time outs, it returns ''. Ignore this case
                # This would happen when the Maxwell board is not sending
                # any data on the serial port
                continue
            if ord(x) == START_BYTE:
                state = STATE_IN_PROGRESS
                stream.extend(x)
        elif state == STATE_IN_PROGRESS:
            x = ser.read()
            stream.extend(x)
            if len(stream) == NUM_BYTES_IN_PACKET:
                crc_in_packet = 256*stream[NUM_BYTES_IN_PACKET-2] + \
                        stream[NUM_BYTES_IN_PACKET-1]
                crc_computed = crc16.crc16xmodem(str(stream[0:NUM_BYTES_IN_PACKET-2]))
                if crc_in_packet != crc_computed:
                    print("{red}CRC Mismatch{white}".format(red=Fore.RED,
                                                            white=Fore.WHITE))
                    stream = bytearray()
                    state = STATE_IDLE
                else:
                    state = STATE_RECEIVED
        elif state == STATE_RECEIVED:
            packet = MaxwellPacket()
            packet.deserialize(stream[1:])
            print("{}\n".format(packet))
            stream = bytearray()
            state = STATE_IDLE

if __name__ == "__main__":
    run()
