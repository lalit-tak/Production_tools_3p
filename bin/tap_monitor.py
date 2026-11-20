#!/usr/bin/python
# tap_monitor.py
# Monitors a serial port and outputs all TAP packets recieved as pretty-formatted
# lines. Like a very simple tcpdump for TAP.
#
# Copyright 2014 Gram Power, Inc.

import colorama
from colorama import Fore
import datetime
import serial
import sys

from gp_node.network.protocols.tap import TAPHandler, TAPPacket, TAPError

colorama.init();

KNOWN_PORTS = {
    0: "echo",
    1: "time",
    2: "SRP",
    3: "recharge",
    4: "simpleterm",
    5: "syncstream",
    6: "flash_io",
    7: "maxwell_calibrate",
    8: "tamper_record"
};

BAUD_RATE = 38400;
TAP_TIMEOUT = 3.0;
DIGITS_PER_LINE = 8;
display_packet_id = True;
ser = '';
handler = '';

# Get serial port from command line
if (len(sys.argv) != 2):
    sys.exit("Incorrect command format\nFormat: tap_monitor [serial port]");

serial_port = sys.argv[1];
try:
    ser = serial.Serial(serial_port, BAUD_RATE, timeout=0);
except:
    sys.exit("Could not open serial port \"" + serial_port + "\".");

# Open TAP handler
handler = TAPHandler(ser, TAP_TIMEOUT);

def get_sanitized(my_string):
    toReturn = '';

    for i in range(0, len(my_string)):
        if ord(my_string[i]) < 32 or ord(my_string[i]) > 126:
            toReturn += '.';
        else:
            toReturn += my_string[i];

    return toReturn;


def display_data(data):
    print(len(data))
    remainder = data;

    while len(remainder) > 0:
        line = remainder[:DIGITS_PER_LINE];
        remainder = remainder[DIGITS_PER_LINE:];

        print('\t' + ' '.join(["%.2X" % digit for digit in line]), end=' ');

        if len(line) < DIGITS_PER_LINE:
            print(' '.join(["  " for i in range(0, DIGITS_PER_LINE - len(line))]), end=' ');

        print("|", end=' ');
        print(get_sanitized(str(line)));


    print("");


def display_packet(packet):

    print(Fore.WHITE + "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]\t" + \
    Fore.GREEN + str(packet.src_addr) + ":" + str(packet.src_port) + "\t" + \
            Fore.BLUE + str(packet.dest_addr) + ":" + str(packet.dest_port), end=' ');

    if display_packet_id:
        print(Fore.CYAN + "\t" + "Protocol:", end=' ');
        if packet.src_port in KNOWN_PORTS:
            print(KNOWN_PORTS[packet.src_port], end=' ');
        else:
            print("unknown", end=' ');

        if packet.dest_port != packet.src_port:
            print("/", end=' ');
            if packet.dest_port in KNOWN_PORTS:
                print(KNOWN_PORTS[packet.dest_port], end=' ');
            else:
                print("unknown", end=' ');

        print("");

    # Data
    print(Fore.RED);
    display_data(packet.data);

    print("");


while 1:
    # Try to receive a tap packet
    try:
        packet = handler.get_packet()
        display_packet(packet)
    except TAPError:
        pass
