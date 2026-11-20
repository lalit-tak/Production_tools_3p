"""
Utility to construct and send arbitrary TAP packets over a given interface.

Note that this is not designed for production - it's mainly for designing and
debugging TAP-based protocols on the command line. If the intent is to integrate
this into a live data handling system, it would need to be cleaned up and made
more robust.
"""

import argparse
import serial
import sys

from gp_node.network.protocols import tap
from gp_node.utils import Address

DEFAULT_TIMEOUT_SEC = 3.0
DEFAULT_BAUD_RATE = 38400

# Parse command-line arguments
parser = argparse.ArgumentParser( \
        description="Sends a single TAP packet on the given interface with the"
                    "given address and port, and waits for a response for the"
                    "given amount of time. Packet payload may be entered directly"
                    "through stdin or as a string.")
parser.add_argument('payload', help='The packet payload')
parser.add_argument('--device', '-d', help='Serial device on which to send the'
                                           'packet.')
parser.add_argument('--baud', '-b', default=DEFAULT_BAUD_RATE, type=int, help='Baud rate of the serial'
                                                   'device.')
parser.add_argument('--srcaddr', help="Source address to use in the packet.")
parser.add_argument('--srcport', help="Source port to use in the packet.")
parser.add_argument('--destaddr', help="Destination address to use in the packet.")
parser.add_argument('--destport', help="Destionation port to use in the packet.")
parser.add_argument('--timeout', '-t', type=float, default=DEFAULT_TIMEOUT_SEC,
                    help="Time to wait for a response before giving up.")

args = parser.parse_args()

# Check address handling
try:
    src_addr = Address(args.srcaddr)
except ValueError:
    sys.exit("Incorrectly formatted source address. Address must be in the format x.x.x.x")

try:
    dest_addr = Address(args.destaddr)
except ValueError:
    sys.exit("Incorrectly formatted destination address. Address must be in the format x.x.x.x")

# Open the serial port
try:
    ser = serial.Serial(args.device, args.baud, timeout=0)
except Exception as err:
    print(err)
    sys.exit("Couldn't open serial port.")

# Open TAP handler
handler = tap.TAPHandler(ser, args.timeout)

handler.send_packet(src_addr, dest_addr, int(args.srcport), int(args.destport), bytearray(args.payload.decode('string_escape')))

# Wait for response. If there is a response, print it; else exit silently
try:
    packet = handler.get_packet()
    sys.stdout.write(packet.data)
except tap.TAPError:
    pass
