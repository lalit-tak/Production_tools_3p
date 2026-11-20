"""
This provides API's to use the maxwell simulator
There are API's to set each parameter(voltage,tampers etc).
Also a generic API handle_request() can be used to set any
parameter
"""
import cmd
import argparse
import atexit
import json
import sys
import threading
import datetime
import dateutil.parser
import inspect

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

class MaxwellSimulatorAPI(object):

    def __init__(self, device, baud):
        super(MaxwellSimulatorAPI, self).__init__()
        self.live_inputs_queue = Queue(maxsize=0)
        self.live_env_queue = Queue(maxsize=0)
        self.inputs = INITIAL_INPUTS
        self.dump_inputs()
        self.board = UARTEngine(self.live_env_queue, device, baud_rate=baud)
        self.board.start()
        self.engine = MeterEngine(self.live_inputs_queue, self.live_env_queue)
        self.engine.start()
        command_functions = inspect.getmembers(self)
        self.function_list = []
        for entry in command_functions:
            if inspect.ismethod(entry[1]) and entry[0][0] != "_":
                if entry[0] != 'handle_function':
                    self.function_list.append(entry)

    def handle_function(self, request):
        if ":" not in request:
            for f in self.function_list:
                if f[0] == request:
                    return str(f[1]())

        else:                    
            f_str = request.split(":")[0]
            argument = ':'.join(request.split(":")[1:])
            for f in self.function_list:
                if f[0] == f_str.replace(" ", "_"):
                    return str(f[1](argument))

        
    def voltage(self, volt):
        """
        Sets the voltage (in volts)
        Example Usage: voltage 240.4
        """
        try:
            self.inputs["voltage"] = float(volt)
        except:
            print("Usage: voltage {float}")
        self.dump_inputs()

    def power_factor(self, power_factor):
        """
        Sets the power factor in range 0.0 to 1.0
        Example Usage: power_factor 0.97
        """
        try:
            self.inputs["power_factor"] = float(power_factor)
        except:
            print("Usage: power_factor {float}")
        self.dump_inputs()

    def frequency(self, line):
        """
        Sets the frequency in Hertz
        Example Usage: frequency 49.7
        """
        try:
            self.inputs["frequency"] = float(line)
        except:
            print("Usage: frequency {float}")
        self.dump_inputs()

    def phase_load(self, line):
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

    def neutral_load(self, line):
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

    def time(self, line):
        """
        Sets the time field.
        Example usage: time 2014-11-10 23:10:33
        Example usage: time now
        """
        self.line =line
        try:
            
            if line == "now":
                self.inputs["time"] = datetime.datetime.now()
            elif "now" in line:
                delta = int(self.line.split("+")[1])
                self.inputs["time"] = datetime.datetime.now() + datetime.timedelta(seconds=delta)
            else:
                self.inputs["time"] = dateutil.parser.parse(line)
        except:
            print("Usage: time now OR time YYYY-MM-DD DD-MM-SS")
        self.inputs["start_true_time"] = datetime.datetime.now()
        self.dump_inputs()

    def set_earth_tamper(self):
        """
        Sets the earth tamper flag
        """
        self.inputs["earth_tamper"] = True
        self.dump_inputs()

    def clear_earth_tamper(self):
        """
        Clears the earth tamper flag
        """
        self.inputs["earth_tamper"] = False
        self.dump_inputs()

    def set_rev_tamper(self):
        """
        Sets the line load reversal tamper flag
        """
        self.inputs["rev_tamper"] = True
        self.dump_inputs()

    def clear_rev_tamper(self):
        """
        Clears the line load reversal tamper flag
        """
        self.inputs["rev_tamper"] = False
        self.dump_inputs()

    def set_nm_tamper(self):
        """
        Sets the neutral missing tamper flag
        """
        self.inputs["nm_tamper"] = True
        self.dump_inputs()

    def clear_nm_tamper(self):
        """
        Clears the neutral missing tamper flag
        """
        self.inputs["nm_tamper"] = False
        self.dump_inputs()

    def set_nd_tamper(self):
        """
        Sets the neutral disturbance tamper flag
        """
        self.inputs["nd_tamper"] = True
        self.dump_inputs()

    def clear_nd_tamper(self):
        """
        Clears the neutral disturbance tamper flag
        """
        self.inputs["nd_tamper"] = False
        self.dump_inputs()

    def set_mag_tamper(self):
        """
        Sets the magnetic tamper flag
        """
        self.inputs["mag_tamper"] = True
        self.dump_inputs()

    def clear_mag_tamper(self):
        """
        Clears the magnetic tamper flag
        """
        self.inputs["mag_tamper"] = False
        self.dump_inputs()

    def dump_inputs(self):
        if self.live_inputs_queue.empty():
            self.live_inputs_queue.put(self.inputs)


    def stop(self):
        """
        Exits the simulator
	    kills the simulator threads
        """
        self.board.request_shutdown = True
        self.engine.request_shutdown = True
        self.board.join()
        self.engine.join()
        return True
    

