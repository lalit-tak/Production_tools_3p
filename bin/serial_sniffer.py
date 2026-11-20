#!/usr/bin/python
# serial_sniffer.py
# Sniffs the traffic on a serial port by redirecting it through a virtual port.
# Creates two new serial ports, one of which outputs the RX traffic and the
# other which outputs TX traffic.
#
# Copyright 2014 Gram Power, Inc.

import argparse
import atexit
import serial
import subprocess
import sys
import time

baud_rate = 19200;
source = '';
dest = '';
rxdump = '';
txdump = '';


class SerialBridge:
    def __init__(self, source_path, dest_path):
        self.source_path = source_path;
        self.dest_path = dest_path;
        # First, start the subprocess which creates the serial ports
        socat_command = "socat PTY,link=" + source_path + ",raw,echo=0,b" + str(baud_rate) + " " + \
                "PTY,link=" + dest_path + ",raw,echo=0,b" + str(baud_rate);
        self.socat_process = subprocess.Popen(socat_command, shell=True);
        # Wait for the subprocess to start the bridge
        time.sleep(0.2);

        # Next, open the source side
        self.serial_port = serial.Serial(source_path, timeout=0);


    def write(self, string):
        return self.serial_port.write(string);


    def read(self):
        return self.serial_port.read();


    def close(self):
        self.socat_process.terminate();
        self.serial_port.close();


# Parse command-line arguments
parser = argparse.ArgumentParser( \
        description="Monitors bi-directional serial communication on the \"source\" port. \
        Creates three additional serial ports: \"dest\", which user now uses instead of \
        the \"source\" port; \"rxdump\", where all received bytes are dumped; and \
        \"txdump\", where all transmitted bytes are dumped.");
parser.add_argument('source', help='The serial port to sniff');
parser.add_argument('-b', '--baud', default=19200, type=int, \
        help="Baud rate for all serial ports");

args = parser.parse_args();


# Clean-up commands which terminate socat processes and close serial ports on exit
def exit_gracefully():
    source.close();
    dest.close();
    rxdump.close();
    txdump.close();
    print("Stopped.");

# executed when ctrl-C is pressed.
@atexit.register
def at_exit():
    exit_gracefully();

# Main function
if __name__ == '__main__':
    baud_rate = args.baud;
    
    # First, open source serial port, the only real one
    try:
        source = serial.Serial(args.source, baud_rate, timeout=0);
    except:
        sys.exit("Couldn't open source serial port.");

    # Next, open the virtual serial ports
    dest = SerialBridge("/tmp/.dest", "/tmp/dest");
    rxdump = SerialBridge("/tmp/.rxdump", "/tmp/rxdump");
    txdump = SerialBridge("/tmp/.txdump", "/tmp/txdump");

    # Output success message
    print("Using baud rate " + str(baud_rate));
    print("destination port at " + dest.dest_path);
    print("rxdump port at " + rxdump.dest_path);
    print("txdump port at " + txdump.dest_path);
    print("");

    while 1:
        # Read and distribute bytes sent by source
        incoming_bytes = source.read();
        if incoming_bytes != '':
            #print "<",;
            dest.write(incoming_bytes);
            rxdump.write(incoming_bytes);

        # Read and distribute bytes sent by dest
        outgoing_bytes = dest.read();

        if outgoing_bytes != '':
            #print ">",;
            source.write(outgoing_bytes);
            txdump.write(outgoing_bytes);

