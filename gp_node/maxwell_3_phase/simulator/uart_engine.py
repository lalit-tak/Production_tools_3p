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
from maxwell_packet import MaxwellPacket
from status_flag import StatusFlag
#from gp_node.maxwell.packet import MaxwellPacket
from tamper_flag import TamperFlag


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
        flag = False
        while True:
            self.update_values()
            stream = bytearray()
            stream.append(MAXWELL_START_BYTE)
            if (flag == False):
                stream.append(0x02)
                stream.extend(self.packet.serialize_packet_one())
                flag = True
            else: 
                stream.append(0x01)
                stream.extend(self.packet.serialize_packet_two())
                flag = False

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
            temp = values["real_time"] + (datetime.datetime.now() - values["true_time"])
            self.packet.time = temp
            self.packet.total_real_energy = values["total_real_energy"]  
            self.packet.total_apparent_energy = values["total_apparent_energy"]
            self.packet.total_reactive_energy = values["total_reactive_energy"]
            self.packet.lag_only_reactive_energy = values["lag_only_reactive_energy"]
            self.packet.lag_only_apparent_energy = values["lag_only_apparent_energy"]
            self.packet.lead_only_reactive_energy = values["lead_only_reactive_energy"]
            self.packet.lead_only_apparent_energy = values["lead_only_apparent_energy"]

            self.packet.tampers = 0x0000
            self.packet.status = 0x00

            self.packet.r_voltage = values["r_voltage"]
            self.packet.y_voltage = values["y_voltage"]
            self.packet.b_voltage = values["b_voltage"]
            self.packet.r_current = values["r_current"]
            self.packet.y_current = values["y_current"]
            self.packet.b_current = values["b_current"]
            self.packet.neutral_current = values["neutral_current"]
            self.packet.r_active_power = values["r_active_power"]
            self.packet.y_active_power = values["y_active_power"]
            self.packet.b_active_power = values["b_active_power"]
            self.packet.r_apparent_power = values["r_apparent_power"]
            self.packet.y_apparent_power = values["y_apparent_power"]
            self.packet.b_apparent_power = values["b_apparent_power"]
            self.packet.r_reactive_power = values["r_reactive_power"]
            self.packet.y_reactive_power = values["y_reactive_power"]
            self.packet.b_reactive_power = values["b_reactive_power"]

            self.packet.frequency = values["frequency"]
            self.packet.total_active_power = values["total_active_power"]
            self.packet.total_apparent_power = values["total_apparent_power"]
            self.packet.total_reactive_power = values["total_reactive_power"]
            self.packet.total_harmonic_power = values["total_harmonic_power"]

            self.packet.r_pf = values["r_pf"]
            self.packet.y_pf = values["y_pf"] 
            self.packet.b_pf = values["b_pf"]
            self.packet.total_pf = values["total_pf"]

            self.packet.tampers = []
            if values["r_phase_missing_tamper"]:
                self.packet.tampers.append(TamperFlag("R_PHASE_MISSING"))
            if values["y_phase_missing_tamper"]:
                self.packet.tampers.append(TamperFlag("Y_PHASE_MISSING"))
            if values["b_phase_missing_tamper"]:
                self.packet.tampers.append(TamperFlag("B_PHASE_MISSING"))
            if values["current_bypass_tamper"]:
                self.packet.tampers.append(TamperFlag("CURRENT_BYPASS"))
            if values["r_phase_reverse_current_tamper"]:
                self.packet.tampers.append(TamperFlag("R_PHASE_REVERSE_CURRENT"))
            if values["y_phase_reverse_current_tamper"]:
                self.packet.tampers.append(TamperFlag("Y_PHASE_REVERSE_CURRENT"))
            if values["b_phase_reverse_current_tamper"]:
                self.packet.tampers.append(TamperFlag("B_PHASE_REVERSE_CURRENT"))
            if values["magnetic_tamper"]:
                self.packet.tampers.append(TamperFlag("MAGNETIC"))
            if values["r_phase_ct_open"]:
                self.packet.tampers.append(TamperFlag("R_PHASE_CT_OPEN"))
            if values["y_phase_ct_open"]:
                self.packet.tampers.append(TamperFlag("Y_PHASE_CT_OPEN"))
            if values["b_phase_ct_open"]:
                self.packet.tampers.append(TamperFlag("B_PHASE_CT_OPEN"))
            if values["current_unbalance"]:
                self.packet.tampers.append(TamperFlag("CURRENT_UNBALANCE"))
            if values["voltage_unbalance"]:
                self.packet.tampers.append(TamperFlag("VOLTAGE_UNBALANCE"))
            if values["r_phase_nd"]:
                self.packet.tampers.append(TamperFlag("R_PHASE_ND"))
            if values["y_phase_nd"]:
                self.packet.tampers.append(TamperFlag("Y_PHASE_ND"))
            if values["b_phase_nd"]:
                self.packet.tampers.append(TamperFlag("B_PHASE_ND"))

            self.packet.status = []
            if values["rtc_battery_status"]:
                self.packet.status.append(StatusFlag("RTC_BATTERY_FAULTY"))
            if values["uc_battery_status"]:
                self.packet.status.append(StatusFlag("UC_BATTERY_FAULTY"))
            if values["relay_status"]:
                self.packet.status.append(StatusFlag("RELAY_OFF"))
            if values["relay_driver_charge_pump_status"]:
                self.packet.status.append(StatusFlag("RELAY_PUMP_OFF"))
