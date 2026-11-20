"""
Sends packets on a serial port simulating the behavior of the Maxwell board.
"""

import argparse
import json
import serial
import sys
import time
import datetime
import threading
import crc16
import Queue
from gp_node.maxwell.packet import MaxwellPacket
from gp_node.utils import TamperFlag


DEFAULT_PACKET_PERIOD = 1.0
DEFAULT_BAUD_RATE = 2400
MAXWELL_START_BYTE = 0xAA
MAXWELL_STOP_BYTE = 0x55

class UARTEngine(threading.Thread):

    def __init__(self, live_env_queue, device, packet_period=DEFAULT_PACKET_PERIOD, 
                 baud_rate=DEFAULT_BAUD_RATE):
        threading.Thread.__init__(self)
        self.live_env_queue = live_env_queue
        self.packet_period = packet_period
        self.baud_rate = baud_rate
        self.packet = MaxwellPacket()
        try:
            self.ser = serial.Serial(device, baud_rate, timeout=0)
        except:
            sys.exit("Couldn't open source serial port: " + device)
        self.request_shutdown = False

    def run(self):
        """
        A continous while loop which keeps reading the latest environment state,
        and sending the corresponding MaxwellPacket over the serial port
        at a 1 Hz frequency
        """
        while True:
            self.update_values()
            stream = bytearray()
            stream.append(MAXWELL_START_BYTE)
            stream.extend(self.packet.serialize())
            crc = crc16.crc16xmodem(str(stream))
            stream.append(crc/256)
            stream.append(crc%256)
            self.ser.write(stream)
            time.sleep(self.packet_period)
            if self.request_shutdown is True:
                return

    def update_values(self):
        """
        Tries to read new entries (if available) from the live_env_queue.
        The live_env_queue is a queue of dictionaries which contains the
        state of the entire environment (including inputs and simulated outputs).
        The environment is then used to self.packet (which is a MaxwellPacket), 
        so that the self.packet can be sent off over the serial port in the run() method
        """
        try:
            values = self.live_env_queue.get(False)
            self.live_env_queue.task_done()
        except Queue.Empty:
            pass
        else: 
            self.packet.protocol_version = 2
            self.packet.time = values["time"] + \
                    (datetime.datetime.now() - values["start_true_time"])
            self.packet.voltage = values["voltage"]
            self.packet.phase_current = values["phase_current"]
            self.packet.neutral_current = values["neutral_current"]
            self.packet.power_factor = values["power_factor"]
            self.packet.active_power = values["active_power"]
            self.packet.total_power = values["total_power"] 
            self.packet.active_energy = values["active_energy"]
            self.packet.frequency = values["frequency"]
            self.packet.tamper_events = []
            if values["earth_tamper"]:
                self.packet.tamper_events.append(TamperFlag("EARTH"))
            if values["rev_tamper"]:
                self.packet.tamper_events.append(TamperFlag("LINE_LOAD_REVERSAL"))
            if values["mag_tamper"]:
                self.packet.tamper_events.append(TamperFlag("MAGNETIC"))
            if values["nm_tamper"]:
                self.packet.tamper_events.append(TamperFlag("NEUTRAL_MISSING"))
            if values["nd_tamper"]:
                self.packet.tamper_events.append(TamperFlag("NEUTRAL_DISTURBANCE"))
