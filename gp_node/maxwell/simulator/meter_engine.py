"""
Implements the Metering thread. This thread is responsible
for calculating all the dependent variables from the independent variables.
This thread reads inputs from the live_input_queues, and dumps the environment
state in the live_env_queue.
"""
import argparse
import math
import json
import time
import threading
import Queue

class MeterEngine(threading.Thread):

    def __init__(self, live_inputs_queue, live_env_queue):
        threading.Thread.__init__(self)
        self.live_inputs_queue = live_inputs_queue
        self.live_env_queue = live_env_queue
        self.sampling_period = 0.1  # Seconds
        # Calculated paramters
        self.results = {
                "phase_current": 0,
                "neutral_current": 0,
                "current": 0,
                "active_power": 0,
                "active_energy": 0
                }
        self.request_shutdown = False

    def run(self):
        self.start_time = time.time()
        self.last_tick = 0
        while True:
            self.update()
            time.sleep(0.1)
            if self.request_shutdown is True:
                return

    def update(self):
        """
        Keeps reading independent variables (inputs) from the live_inputs_queue
        and keeps dumping the independent + dependent variables (environment)
        into the live_env_queue.

        The indepdendent variables which are used in this function are:

        1. voltage
        2. phase_load
        3. neutral_load
        4. power_factor

        The dependent variables which are computed using the independen
        variables are:
        
        1. phase_current    = voltage/phase_load
        2. neutral_current  = voltage/neutral_current
        3. current          = greater of phase_current and neutral_current
        4. active_power     = total_power*power_factor
        5. total_power      = voltage*current
        6. reactive_power   = sqrt(total_power^2 - active_power^2)
        7. active_energy    = integral of active_power

        """
        this_tick = int((time.time() - self.start_time) / self.sampling_period)
        if this_tick > self.last_tick:
            self.last_tick = this_tick
            self.load_latest_inputs()
            try:
                self.results["phase_current"] = float(self.inputs["voltage"])/\
                        float(self.inputs["phase_load"])
            except ZeroDivisionError:
                self.results["phase_current"] = 0
            try:
                self.results["neutral_current"] = float(self.inputs["voltage"])/\
                        float(self.inputs["neutral_load"])
            except ZeroDivisionError:
                self.results["neutral_current"] = 0
            if self.results["phase_current"] > self.results["neutral_current"]:
                self.results["current"] = self.results["phase_current"]
            else:
                self.results["current"] = self.results["neutral_current"]
            self.results["total_power"] = self.inputs["voltage"] *\
                    self.results["current"]
            self.results["active_power"] = self.inputs["power_factor"] *\
                    self.results["total_power"]
            self.results["reactive_power"] = self.results["total_power"] *\
                    (1 - (math.sqrt(1 - self.inputs["power_factor"])**2))
            self.results["active_energy"] += (self.results["active_power"] *\
                    self.sampling_period) / 3600
            self.dump_latest_results()

    def load_latest_inputs(self):
        """
        Updates self.inputs with the latest values coming in from the live_inputs_queue
        The main shell thread (implemented in maxwell_simulator.py) dumps values in
        the live_inputs_queue. The values in this queue contain mainly independent
        variables such as voltage, phase_load etc.
        """
        try:
            self.inputs = self.live_inputs_queue.get(False)
            self.live_inputs_queue.task_done()
        except Queue.Empty:
            pass

    def dump_latest_results(self):
        """
        New entries are dumped into the live_env_queue. This queue is then
        read by the thread implemented in uart_engine.py.
        The values dumped in this thread contains the entire state of the
        environment. The queue contains dependent as well as independent variables
        """
        if self.live_env_queue.empty():
            to_dump = dict(self.inputs.items() + self.results.items())
            self.live_env_queue.put(to_dump)
