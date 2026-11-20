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
    "start_true_time": datetime.datetime(2000, 1, 1, 0, 0, 0),
    "time": datetime.datetime(2000, 1, 1, 0, 0, 0),
    "phase_load": 0,
    "neutral_load": 0,
    "voltage": 240.0,
    "frequency": 50.0,
    "power_factor": 1.0,
    "earth_tamper": 0,
    "rev_tamper": 0,
    "mag_tamper": 0,
    "nm_tamper": 0,
    "nd_tamper": 0
}

class MaxwellSimulator(cmd.Cmd, object):

    prompt = "{yellow}maxwell-simulator{blue} ${white} ".\
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

    def do_voltage(self, line):
        """
        Sets the voltage (in volts)
        Example Usage: voltage 240.4
        """
        try:
            self.inputs["voltage"] = float(line)
        except:
            print("Usage: voltage {float}")
        self.dump_inputs()

    def do_power_factor(self, line):
        """
        Sets the power factor in range 0.0 to 1.0
        Example Usage: power_factor 0.97
        """
        try:
            self.inputs["power_factor"] = float(line)
        except:
            print("Usage: power_factor {float}")
        self.dump_inputs()

    def do_frequency(self, line):
        """
        Sets the frequency in Hertz
        Example Usage: frequency 49.7
        """
        try:
            self.inputs["frequency"] = float(line)
        except:
            print("Usage: frequency {float}")
        self.dump_inputs()

    def do_phase_load(self, line):
        """
        Sets phase load (in ohms).
        This is used to calculate phase_current = voltage/phase_phase
        Example Usage: phase_load 100
        """
        try:
            self.inputs["phase_load"] = int(line)
        except:
            print("Usage: phase_load {int}")
        self.dump_inputs()

    def do_neutral_load(self, line):
        """
        Sets neutral load (in ohms).
        This is used to calculate neutral_current = voltage/neutral_phase
        Example Usage: neutral_load 100
        """
        try:
            self.inputs["neutral_load"] = int(line)
        except:
            print("Usage: neutral_load {int}")
        self.dump_inputs()

    def do_time(self, line):
        """
        Sets the time field.
        Example usage: time 2014-11-10 23:10:33
        Example usage: time now
        """
        try:
            if line == "now":
                self.inputs["time"] = datetime.datetime.now()
            else:
                self.inputs["time"] = dateutil.parser.parse(line)
        except:
            print("Usage: time now OR time YYYY-MM-DD DD-MM-SS")
        self.inputs["start_true_time"] = datetime.datetime.now()
        self.dump_inputs()

    def do_set_earth_tamper(self, line):
        """
        Sets the earth tamper flag
        """
        self.inputs["earth_tamper"] = True
        self.dump_inputs()

    def do_clear_earth_tamper(self, line):
        """
        Clears the earth tamper flag
        """
        self.inputs["earth_tamper"] = False
        self.dump_inputs()

    def do_set_rev_tamper(self, line):
        """
        Sets the line load reversal tamper flag
        """
        self.inputs["rev_tamper"] = True
        self.dump_inputs()

    def do_clear_rev_tamper(self, line):
        """
        Clears the line load reversal tamper flag
        """
        self.inputs["rev_tamper"] = False
        self.dump_inputs()

    def do_set_nm_tamper(self, line):
        """
        Sets the neutral missing tamper flag
        """
        self.inputs["nm_tamper"] = True
        self.dump_inputs()

    def do_clear_nm_tamper(self, line):
        """
        Clears the neutral missing tamper flag
        """
        self.inputs["nm_tamper"] = False
        self.dump_inputs()

    def do_set_nd_tamper(self, line):
        """
        Sets the neutral disturbance tamper flag
        """
        self.inputs["nd_tamper"] = True
        self.dump_inputs()

    def do_clear_nd_tamper(self, line):
        """
        Clears the neutral disturbance tamper flag
        """
        self.inputs["nd_tamper"] = False
        self.dump_inputs()

    def do_set_mag_tamper(self, line):
        """
        Sets the magnetic tamper flag
        """
        self.inputs["mag_tamper"] = True
        self.dump_inputs()

    def do_clear_mag_tamper(self, line):
        """
        Clears the magnetic tamper flag
        """
        self.inputs["mag_tamper"] = False
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
