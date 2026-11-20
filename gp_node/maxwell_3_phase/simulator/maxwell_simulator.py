"""
Implements the Maxwell Simulator Shell, which simulates packets on
the UART port of the 12 pin connector. To use this script, attach
the FTDI cable to the simulation board and place the Node board
on top of the simulation board.

The shell allows the user to set certain parameters of the inputs.
These parameters are then used by the simulator to calculate all the
fields of the packet. For example, the shell allows the user to set voltage,
power factor, and the phase_load and neutral_load (in ohm) being 
used in phase and neutral current circuitry. This is then used by the 
simulator to calculate the active power, active energy etc. The simulator
then keeps sending these packets on the FTDI cable at a 1Hz frequency
"""
import cmd
import argparse
import atexit
import json
import sys
import threading
import datetime
import dateutil.parser

from colorama import Fore
from uart_engine import UARTEngine
from meter_engine import MeterEngine
from Queue import Queue

INITIAL_INPUTS = {
    #------------------packet 1------------------------------
    "true_time": datetime.datetime(2000, 1, 1, 0, 0, 0),
    "real_time": datetime.datetime(2000, 1, 1, 0, 0, 0),
    "total_real_energy": 1.0,
    "total_apparent_energy": 1.0,
    "total_reactive_energy": 1.0,
    "lag_only_reactive_energy": 1.0,
    "lag_only_apparent_energy": 1.0,
    "lead_only_reactive_energy": 1.0,
    "lead_only_apparent_energy": 1.0,
    #--TAMPERS-------------------------
    "r_phase_missing_tamper": 0,
    "y_phase_missing_tamper": 0,
    "b_phase_missing_tamper": 0,
    "current_bypass_tamper": 0,
    "r_phase_reverse_current_tamper": 0,
    "y_phase_reverse_current_tamper": 0,
    "b_phase_reverse_current_tamper": 0,
    "magnetic_tamper": 0,
    "r_phase_ct_open":0,
    "y_phase_ct_open":0,
    "b_phase_ct_open":0,
    "current_unbalance":0,
    "voltage_unbalance":0,
    "r_phase_nd":0,
    "y_phase_nd":0,
    "b_phase_nd":0,
    #--STATUS BYTE---------------------
    "rtc_battery_status": 0,
    "uc_battery_status": 0,
    "relay_status": 0,
    "relay_driver_charge_pump_status": 0,
    #-------------------packet 2-----------------------------
    "r_voltage": 220.0,
    "y_voltage": 220.0,
    "b_voltage": 220.0,
    "r_current": 1.0,
    "y_current": 1.0,
    "b_current": 1.0,
    "neutral_current": 1.0,
    "r_active_power": 0.0,
    "y_active_power": 0.0,
    "b_active_power": 0.0,
    "r_apparent_power": 0.0,
    "y_apparent_power": 0.0,
    "b_apparent_power": 0.0,
    "r_reactive_power": 0.0,
    "y_reactive_power": 0.0,
    "b_reactive_power": 0.0,
    "frequency": 50.49,
    "total_active_power": 0.0,
    "total_apparent_power": 0.0,
    "total_reactive_power": 0.0,
    "total_harmonic_power": 0.0,
    "r_pf": 1.0,
    "y_pf": 1.0,
    "b_pf": 1.0,
    "total_pf": 1.0
}

class MaxwellSimulator(cmd.Cmd, object):

    prompt = "{yellow}max-3-phase-sim{blue} ${white} ".\
                format(yellow=Fore.YELLOW,
                       blue=Fore.BLUE,
                       white=Fore.WHITE)

    def __init__(self, device, baud):
        super(MaxwellSimulator, self).__init__()
        self.live_inputs_queue = Queue(maxsize=0)
        self.live_env_queue = Queue(maxsize=0)
        self.inputs = INITIAL_INPUTS
        self.dump_inputs()
        self.board = UARTEngine(self.live_env_queue, device, baud_rate=baud)
        self.board.start()
        self.engine = MeterEngine(self.live_inputs_queue, self.live_env_queue)
        self.engine.start()
#-------here we go -----------------------
    def do_set_total_real_energy(self, line):
        """
        Sets the total_real_energy (in wh)
        Example Usage: total_real_energy 240.4
        """
        try:
            self.inputs["total_real_energy"] = float(line)
        except:
            print("Usage: total_real_energy {float}")
        self.dump_inputs()
    def do_set_total_apparent_energy(self, line):
        """
        Sets the total_apparent_energy (in va)
        Example Usage: total_apparent_energy 240.4
        """
        try:
            self.inputs["total_apparent_energy"] = float(line)
        except:
            print("Usage: total_apparent_energy {float}")
        self.dump_inputs()
    def do_set_total_reactive_energy(self, line):
        """
        Sets the total_reactive_energy (in var)
        Example Usage: total_reactive_energy 240.4
        """
        try:
            self.inputs["total_reactive_energy"] = float(line)
        except:
            print("Usage: total_reactive_energy {float}")
        self.dump_inputs()
    def do_set_lag_only_reactive_energy(self, line):
        """
        Sets the lag_only_reactive_energy (in var)
        Example Usage: lag_only_reactive_energy 240.4
        """
        try:
            self.inputs["lag_only_reactive_energy"] = float(line)
        except:
            print("Usage: lag_only_reactive_energy {float}")
        self.dump_inputs()
    def do_set_lag_only_apparent_energy(self, line):
        """
        Sets the lag_only_apparent_energy (in va)
        Example Usage: lag_only_apparent_energy 240.4
        """
        try:
            self.inputs["lag_only_apparent_energy"] = float(line)
        except:
            print("Usage: lag_only_apparent_energy {float}")
        self.dump_inputs()
    def do_set_lead_only_reactive_energy(self, line):
        """
        Sets the lead_only_reactive_energy (in var)
        Example Usage: lead_only_reactive_energy 240.4
        """
        try:
            self.inputs["lead_only_reactive_energy"] = float(line)
        except:
            print("Usage: lead_only_reactive_energy {float}")
        self.dump_inputs()
    def do_set_lead_only_apparent_energy(self, line):
        """
        Sets the lead_only_apparent_energy (in va)
        Example Usage: lead_only_apparent_energy 240.4
        """
        try:
            self.inputs["lead_only_apparent_energy"] = float(line)
        except:
            print("Usage: lead_only_apparent_energy {float}")
        self.dump_inputs()
    def do_set_r_phase_missing_tamper(self, line):
        """
        Sets the r phase missing tamper flag
        """
        self.inputs["r_phase_missing_tamper"] = True
        self.dump_inputs()

    def do_clear_r_phase_missing_tamper(self, line):
        """
        Clears the r phase missing tamper flag
        """
        self.inputs["r_phase_missing_tamper"] = False
        self.dump_inputs()
    def do_set_y_phase_missing_tamper(self, line):
        """
        Sets the y phase missing tamper flag
        """
        self.inputs["y_phase_missing_tamper"] = True
        self.dump_inputs()

    def do_clear_y_phase_missing_tamper(self, line):
        """
        Clears the y phase missing tamper flag
        """
        self.inputs["y_phase_missing_tamper"] = False
        self.dump_inputs()
    def do_set_b_phase_missing_tamper(self, line):
        """
        Sets the b phase missing tamper flag
        """
        self.inputs["b_phase_missing_tamper"] = True
        self.dump_inputs()

    def do_clear_b_phase_missing_tamper(self, line):
        """
        Clears the b phase missing tamper flag
        """
        self.inputs["b_phase_missing_tamper"] = False
        self.dump_inputs()
    def do_set_current_bypass_tamper(self, line):
        """
        Sets the current bypass tamper flag
        """
        self.inputs["current_bypass_tamper"] = True
        self.dump_inputs()

    def do_clear_current_bypass_tamper(self, line):
        """
        Clears the current bypass tamper flag
        """
        self.inputs["current_bypass_tamper"] = False
        self.dump_inputs()
    def do_set_r_phase_reverse_current_tamper(self, line):
        """
        Sets the r phase reverse current tamper flag
        """
        self.inputs["r_phase_reverse_current_tamper"] = True
        self.dump_inputs()

    def do_clear_r_phase_reverse_current_tamper(self, line):
        """
        Clears the r phase reverse current tamper flag
        """
        self.inputs["r_phase_reverse_current_tamper"] = False
        self.dump_inputs()
    def do_set_y_phase_reverse_current_tamper(self, line):
        """
        Sets the y phase reverse current tamper flag
        """
        self.inputs["y_phase_reverse_current_tamper"] = True
        self.dump_inputs()

    def do_clear_y_phase_reverse_current_tamper(self, line):
        """
        Clears the y phase reverse current tamper flag
        """
        self.inputs["y_phase_reverse_current_tamper"] = False
        self.dump_inputs()
    def do_set_b_phase_reverse_current_tamper(self, line):
        """
        Sets the b phase reverse current tamper flag
        """
        self.inputs["b_phase_reverse_current_tamper"] = True
        self.dump_inputs()

    def do_clear_b_phase_reverse_current_tamper(self, line):
        """
        Clears the b phase reverse current tamper flag
        """
        self.inputs["b_phase_reverse_current_tamper"] = False
        self.dump_inputs()
    def do_set_magnetic_tamper(self, line):
        """
        Sets the magnetic tamper flag
        """
        self.inputs["magnetic_tamper"] = True
        self.dump_inputs()

    def do_clear_magnetic_tamper(self, line):
        """
        Clears the magnetic tamper flag
        """
        self.inputs["magnetic_tamper"] = False
        self.dump_inputs()
    def do_set_r_phase_ct_open(self, line):
        """
        Sets the R phase CT open tamper flag
        """
        self.inputs["r_phase_ct_open"] = True
        self.dump_inputs()

    def do_clear_r_phase_ct_open(self, line):
        """
        Clears the R phase CT open tamper flag
        """
        self.inputs["r_phase_ct_open"] = False
        self.dump_inputs()
    def do_set_y_phase_ct_open(self, line):
        """
        Sets the Y phase CT open tamper flag
        """
        self.inputs["y_phase_ct_open"] = True
        self.dump_inputs()

    def do_clear_y_phase_ct_open(self, line):
        """
        Clears the Y phase CT open tamper flag
        """
        self.inputs["y_phase_ct_open"] = False
        self.dump_inputs()

    def do_set_b_phase_ct_open(self, line):
        """
        Sets the B phase CT open tamper flag
        """
        self.inputs["b_phase_ct_open"] = True
        self.dump_inputs()

    def do_clear_b_phase_ct_open(self, line):
        """
        Clears the B phase CT open tamper flag
        """
        self.inputs["b_phase_ct_open"] = False
        self.dump_inputs()
    #----------------------------------------
    def do_set_r_phase_nd(self, line):
        """
        Sets the R phase CT open tamper flag
        """
        self.inputs["r_phase_nd"] = True
        self.dump_inputs()

    def do_clear_r_phase_nd(self, line):
        """
        Clears the R phase CT open tamper flag
        """
        self.inputs["r_phase_nd"] = False
        self.dump_inputs()
    def do_set_y_phase_nd(self, line):
        """
        Sets the Y phase CT open tamper flag
        """
        self.inputs["y_phase_nd"] = True
        self.dump_inputs()

    def do_clear_y_phase_nd(self, line):
        """
        Clears the Y phase CT open tamper flag
        """
        self.inputs["y_phase_nd"] = False
        self.dump_inputs()

    def do_set_b_phase_nd(self, line):
        """
        Sets the B phase CT open tamper flag
        """
        self.inputs["b_phase_nd"] = True
        self.dump_inputs()

    def do_clear_b_phase_nd(self, line):
        """
        Clears the B phase CT open tamper flag
        """
        self.inputs["b_phase_nd"] = False
        self.dump_inputs()
    #----------------------------------------
    def do_set_current_unbalance(self, line):
        """
        Sets the current unbalance tamper flag
        """
        self.inputs["current_unbalance"] = True
        self.dump_inputs()

    def do_clear_current_unbalance(self, line):
        """
        Clears the current unbalance tamper flag
        """
        self.inputs["current_unbalance"] = False
        self.dump_inputs()
    def do_set_voltage_unbalance(self, line):
        """
        Sets the voltage unbalance tamper flag
        """
        self.inputs["voltage_unbalance"] = True
        self.dump_inputs()

    def do_clear_voltage_unbalance(self, line):
        """
        Clears the voltage unbalance tamper flag
        """
        self.inputs["voltage_unbalance"] = False
        self.dump_inputs()
    def do_set_rtc_battery_status(self, line):
        """
        Sets the rtc battery status flag
        """
        self.inputs["rtc_battery_status"] = True
        self.dump_inputs()

    def do_clear_rtc_battery_status(self, line):
        """
        Clears the rtc battery status flag
        """
        self.inputs["rtc_battery_status"] = False
        self.dump_inputs()
    def do_set_uc_battery_status(self, line):
        """
        Sets the uc battery status flag
        """
        self.inputs["uc_battery_status"] = True
        self.dump_inputs()

    def do_clear_uc_battery_status(self, line):
        """
        Clears the uc battery status flag
        """
        self.inputs["uc_battery_status"] = False
        self.dump_inputs()
    def do_set_relay_status(self, line):
        """
        Sets the relay status flag
        """
        self.inputs["relay_status"] = True
        self.dump_inputs()

    def do_clear_relay_status(self, line):
        """
        Clears the relay status flag
        """
        self.inputs["relay_status"] = False
        self.dump_inputs()
    def do_set_relay_driver_charge_pump_status(self, line):
        """
        Sets the relay driver charge pump status flag
        """
        self.inputs["relay_driver_charge_pump_status"] = True
        self.dump_inputs()

    def do_clear_relay_driver_charge_pump_status(self, line):
        """
        Clears the relay driver charge pump status flag
        """
        self.inputs["relay_driver_charge_pump_status"] = False
        self.dump_inputs()
    def do_set_r_voltage(self, line):
        """
        Sets the set_r_voltage (in volts)
        Example Usage: r_voltage 240.4
        """
        try:
            self.inputs["r_voltage"] = float(line)
        except:
            print("Usage: set_r_voltage {float}")
        self.dump_inputs()
    def do_set_y_voltage(self, line):
        """
        Sets the set_r_voltage (in volts)
        Example Usage: set_y_voltage 240.4
        """
        try:
            self.inputs["y_voltage"] = float(line)
        except:
            print("Usage: set_y_voltage {float}")
        self.dump_inputs()
    def do_set_b_voltage(self, line):
        """
        Sets the set_b_voltage (in volts)
        Example Usage: set_b_voltage 240.4
        """
        try:
            self.inputs["b_voltage"] = float(line)
        except:
            print("Usage: set_b_voltage {float}")
        self.dump_inputs()
    def do_set_r_current(self, line):
        """
        Sets the r current (in ampere)
        Example Usage: set_r_current 20.4
        """
        try:
            self.inputs["r_current"] = float(line)
        except:
            print("Usage: set_r_current {float}")
        self.dump_inputs()
    def do_set_y_current(self, line):
        """
        Sets the y_current (in ampere)
        Example Usage: set_y_current 0.4
        """
        try:
            self.inputs["y_current"] = float(line)
        except:
            print("Usage: set_y_current {float}")
        self.dump_inputs()
    def do_set_b_current(self, line):
        """
        Sets the b_current (in ampere)
        Example Usage: set_b_current 240.4
        """
        try:
            self.inputs["b_current"] = float(line)
        except:
            print("Usage: set_b_current {float}")
        self.dump_inputs()
    def do_set_neutral_current(self, line):
        """
        Sets the nutral current (in ampere)
        Example Usage: set_neutral_current 240.4
        """
        try:
            self.inputs["neutral_current"] = float(line)
        except:
            print("Usage: set_neutral_current {float}")
        self.dump_inputs()
    def do_set_r_active_power(self, line):
        """
        Sets the r active power (in wats)
        Example Usage: set_r_active_power 240.4
        """
        try:
            self.inputs["r_active_power"] = float(line)
        except:
            print("Usage: set_r_active_power{float}")
        self.dump_inputs()
    def do_set_y_active_power(self, line):
        """
        Sets the y active power (in wats)
        Example Usage: set_y_active_power 240.4
        """
        try:
            self.inputs["y_active_power"] = float(line)
        except:
            print("Usage: set_y_active_power{float}")
        self.dump_inputs()
    def do_set_b_active_power(self, line):
        """
        Sets the b active power (in wats)
        Example Usage: set_b_active_power 240.4
        """
        try:
            self.inputs["b_active_power"] = float(line)
        except:
            print("Usage: set_b_active_power{float}")
        self.dump_inputs()
    def do_set_r_apparent_power(self, line):
        """
        Sets the r apparent power (in wats)
        Example Usage: set_r_apparent_power 240.4
        """
        try:
            self.inputs["r_apparent_power"] = float(line)
        except:
            print("Usage: set_r_apparent_power{float}")
        self.dump_inputs()
    def do_set_y_apparent_power(self, line):
        """
        Sets the y apparent power (in wats)
        Example Usage: set_y_apparent_power 240.4
        """
        try:
            self.inputs["y_apparent_power"] = float(line)
        except:
            print("Usage: set_y_apparent_power{float}")
        self.dump_inputs()
    def do_set_b_apparent_power(self, line):
        """
        Sets the b apparent power (in wats)
        Example Usage: set_b_apparent_power 240.4
        """
        try:
            self.inputs["b_apparent_power"] = float(line)
        except:
            print("Usage: set_b_apparent_power{float}")
        self.dump_inputs()
    def do_set_r_reactive_power(self, line):
        """
        Sets the r reactive power (in wats)
        Example Usage: set_r_reactive_power 240.4
        """
        try:
            self.inputs["r_reactive_power"] = float(line)
        except:
            print("Usage: set_r_reactive_power{float}")
        self.dump_inputs()
    def do_set_y_reactive_power(self, line):
        """
        Sets the r reactive power (in wats)
        Example Usage: set_y_reactive_power 240.4
        """
        try:
            self.inputs["y_reactive_power"] = float(line)
        except:
            print("Usage: set_y_reactive_power{float}")
        self.dump_inputs()
    def do_set_b_reactive_power(self, line):
        """
        Sets the r reactive power (in wats)
        Example Usage: set_b_reactive_power 240.4
        """
        try:
            self.inputs["b_reactive_power"] = float(line)
        except:
            print("Usage: set_b_reactive_power{float}")
        self.dump_inputs()

    def do_set_frequency(self, line):
        """
        Sets the frequency in Hertz
        Example Usage: set_frequency 49.7
        """
        try:
            self.inputs["frequency"] = float(line)
        except:
            print("Usage: set_frequency {float}")
        self.dump_inputs()
    def do_set_total_active_power(self, line):
        """
        Sets the total active power in watts
        Example Usage: set_total_active_power 49.7
        """
        try:
            self.inputs["total_active_power"] = float(line)
        except:
            print("Usage: set_total_active_power {float}")
        self.dump_inputs()
    def do_set_total_apparent_power(self, line):
        """
        Sets the total_apparent_power in va
        Example Usage: set_frequency 49.7
        """
        try:
            self.inputs["total_apparent_power"] = float(line)
        except:
            print("Usage: set_total_apparent_power {float}")
        self.dump_inputs()

    def do_set_total_reactive_power(self, line):
        """
        Sets the total_reactive_power in var
        Example Usage: set_frequency 49.7
        """
        try:
            self.inputs["total_reactive_power"] = float(line)
        except:
            print("Usage: set_total_reactive_power {float}")
        self.dump_inputs()

    def do_set_total_harmonic_power(self, line):
        """
        Sets the total_reactive_power in wats
        Example Usage: set_total_harmonic_power 49.7
        """
        try:
            self.inputs["total_harmonic_power"] = float(line)
        except:
            print("Usage: set_total_harmonic_power {float}")
        self.dump_inputs()

    def do_set_r_pf(self, line):
        """
        Sets the power factor in range 0.0 to 1.0
        Example Usage: power_factor 0.97
        """
        try:
            self.inputs["r_pf"] = float(line)
        except:
            print("Usage: set_r_pf {float}")
        self.dump_inputs()
    def do_set_y_pf(self, line):
        """
        Sets the power factor in range 0.0 to 1.0
        Example Usage: power_factor 0.97
        """
        try:
            self.inputs["y_pf"] = float(line)
        except:
            print("Usage: set_y_pf {float}")
        self.dump_inputs()
    def do_set_b_pf(self, line):
        """
        Sets the power factor in range 0.0 to 1.0
        Example Usage: power_factor 0.97
        """
        try:
            self.inputs["b_pf"] = float(line)
        except:
            print("Usage: set_b_pf {float}")
        self.dump_inputs()
    def do_set_total_pf(self, line):
        """
        Sets the power factor in range 0.0 to 1.0
        Example Usage: power_factor 0.97
        """
        try:
            self.inputs["total_pf"] = float(line)
        except:
            print("Usage: total_pf {float}")
        self.dump_inputs()

    def do_set_date_time(self, line):
        """
        sets the date and real_time
        """
        #print line
        try:
            if line == "now":
                self.inputs["real_time"] = datetime.datetime.now()
            else:
                self.inputs["real_time"] = dateutil.parser.parse(line)
        except:
            print("Usage: time now OR time YYYY-MM-DD DD-MM-SS")
        print self.inputs["real_time"]
        self.inputs["true_time"] = datetime.datetime.now()
        print self.inputs["true_time"]
        self.dump_inputs()


    def do_exit(self, line):
        """
        Exits the simulator
        """
        self.board.request_shutdown = True
        self.engine.request_shutdown = True
        self.board.join()
        self.engine.join()
        return True


    def dump_inputs(self):
        if self.live_inputs_queue.empty():
            self.live_inputs_queue.put(self.inputs)

def run():
    parser = argparse.ArgumentParser( \
            description=("Simulates the Maxwell board. Sends packets on the FTDI cable "
                         "as if the Maxwell board were sending it")
            )
    parser.add_argument('-d', '--device', default='/dev/gp-gateway', \
            help='Device filename of the FTDI cable. Default is /dev/gp-gateway')
    parser.add_argument('-b', '--baud', default=2400, \
            help='Baud rate to communicate with the Node board. Default is 2400')
    args = parser.parse_args()
    maxwell_simulator = MaxwellSimulator(args.device, args.baud)
    maxwell_simulator.cmdloop()



if __name__ == "__main__":
    run()
