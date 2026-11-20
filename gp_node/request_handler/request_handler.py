from gp_node.network.network_api import NetworkAPI, NetworkAPIError
from gp_node.utils import Address
from gp_node.maxwell.simulator.maxwell_sim_api import MaxwellSimulatorAPI
from gp_node.network.circular_log.log_reader import LogReader
from gp_node.network.circular_log.load_survey import LoadSurveyReader
from gp_node.network.protocols.packets.load_survey_params import LoadSurveyParams
from gp_node.network.protocols.flash_io import FlashIOMaster, FlashIOError
from gp_node.network.protocols.packets.bundle import Bundle
import time
import serial
import os
import os.path
import sys
import time
import contextlib
import cStringIO

class RequestHandler(object):
    """
    RequestHandler a very thin layer over available interfaces to the node
    board.The handler is designed for automatic regression tests where it is
    necessary to interact with node board using all the available interfaces
    simultaneously.

    It contains handles for :
    1.NetworkAPI
    2.MaxwellSimulator
    3.Logger(kind of circular log)
    4.LoadSurvey(kind of circular log)
    The handles take care of exceptions and also provide some options to
    overcome communication errors(timeouts,bit corruptons etc)	
    
    Usage:
    Simpleterm commands can be called using "handle_network_request"
        ex:handle_network_request("get_voltage")
    MaxwellSimulator parameters can be configured using "handle_maxwell_request"
        ex:handle_maxwell_request("voltage:240")
    Logger provides API only to retrieve index^th log
        ex:handle_logger_retrieve(1)
    LoadSurvey provides API only to retrieve index^th survey
        ex:handle_survey_retrieve(1)
    """

    def __init__(self):
        """
        Does the following:
        * Reads port and baud rate for my_network_port and my_maxwell_port
        from options.txt
        * Initializes network_api, my_maxwell_api, logger & load_survey by
           acquiring the required parameters from "get_options()"
        """
        self.get_options()
        self.my_network_api = NetworkAPI(self.my_network_port,"irda")
        self.handle_network_request("reset", print_on_stdout=False, no_of_tries=2)
        self.my_maxwell_api = MaxwellSimulatorAPI(self.my_maxwell_port.port, 
            self.my_maxwell_port.baudrate)
        self.logger = LogReader(self.my_network_api, 4, 42)
        self.load_survey = LoadSurveyReader(self.my_network_api, 4, 42)
        return


    def handle_network_request(self, request, no_of_tries=1,
            print_on_stdout=True,  force_valid=False, validity_level="low", meter_type="1p"): 
        """
        Handler for simpleterm commands
        
        :param request: simpleterm command
        :type request: String
        
        :param no_of_tries: The no of tries to be made for the request
        :type no_of_tries: int
        
        :param print_on_stdout: True prints the exception on stdout
        :type print_on_stdout: bool

        :param force_valid: Takes the majority reply after getting three
                three reply's
        :type force_valid: bool

        :param validity_level: The no of tries to be made for the request
        :type validity_level:  "low" "medium" "high" "extreme"
        
        :param meter_type: Type of meter (single phase or three phase)
        :type string:  "1p" "3p"
        
        Use case for "get" commands:
            ex: handle_network_request("get_voltage", validity_level="high")
        Use case for "set" commands:
            ex: handle_network_request("set_power_limit:300", validity_level="medium")
        Use case for commands "recharge"
            ex: handle_network_request("recharge:50", validity_level="low")
        
        """

        self.no_of_tries = no_of_tries
        self.no_of_samples = 1
        
        responses = []
        
        if force_valid:
            self.no_of_samples = 3
            
        #sets no_of_samples & no_of_tries according to the validity level
        def low(self):
            self.no_of_samples = 1
            self.no_of_tries = 1
         
            
        def medium(self):
            self.no_of_samples = 1
            self.no_of_tries = 5
   
               
        def high(self):
            self.no_of_samples = 3
            self.no_of_tries = 5
      
            
        def extreme(self):
            self.no_of_samples = 5 
            self.no_of_tries = 5
    
        
        validity_levels = {"low":low, "medium":medium, "high":high, "extreme":extreme}
        try:
            validity_levels[validity_level](self)
        except KeyError as e:
            print "validity level should be low,medium,high or extreme"
            pass

        sample = ''  
        
        # print self.no_of_samples, "samples"
        # print self.no_of_tries, "tries"
        if(meter_type == "3p"):
            request.replace("3p","three_ph")

        for sample_no in range(self.no_of_samples):
            for try_no in range(self.no_of_tries):
                try:
                    responses.append(self.my_network_api.handle_function_request(
                        self.my_address, request))

                except NetworkAPIError as err:
                    if(print_on_stdout):
                        print request
                        print err
                        print try_no, 'try'
                        time.sleep(2)
                else:
                    break
                
            for sample in responses:
                if responses.count(sample) > 1:
                    return sample
                    
            time.sleep(2)
        
        return sample
  

    def handle_maxwell_request(self, request):
        """
	        Handler for maxwell simulator requests
        """
        try:
	        self.my_maxwell_api.handle_function(request)
	
        except Exception as err:
	        print err
    	        return
        
        time.sleep(1.5)
        return
        
    def handle_logger_retrieve(self, index, no_of_tries=1, force_valid=False):
        """
            Retrives the index^th log from the logs
        """
        no_of_samples = 1
        responses = []
        if force_valid:
            no_of_samples = 3
            
        for j in range(no_of_samples):
            for i in range(no_of_tries):
                try:
                    self.logger.update_header()
                    responses.append(self.logger.get_log_from_node(index))
                except FlashIOError as err:
                    print err
                    return
                else:
                    time.sleep(0.3)
                    break
                time.sleep(0.3)
                
        sample = ''        
        for sample in responses:
            if responses.count(sample) > 1:
                return sample
        
        return sample
            
    def handle_survey_retrieve(self, index, no_of_tries=1, force_valid=False):
        """
            Retrieves the index^th survey from the surveys
        """
        no_of_samples = 1
        responses = []
        if force_valid:
            no_of_samples = 3
            
        for j in range(no_of_samples):
            for i in range(no_of_tries):
                try:
                    self.load_survey.update_header()
                    responses.append(self.load_survey.get_survey_from_node(index))
                except FlashIOError as err:
                    print err
                    return
                else:
                    time.sleep(0.3)
                    break
                time.sleep(0.3)
                
        sample = ''        
        for sample in responses:
            if responses.count(sample) > 1:
                return sample
        
        return sample

    def set_address(self, addr):
        """
            Overrides the address obtained from options file
            
        :param addr: set address for network API 
        :type request: int
        """
        self.my_network_api.set_address(self.my_address, addr)
        self.my_address = addr
        return

    def kill(self):
        """
            Kills all the threads in maxwell simulator
            if this is not called the control wouldn't come
            out of the function
        """
        self.my_maxwell_api.handle_function("stop")

    def get_options(self):
        """
            Reads options from options.txt and sets variables accordingly
            Options must be written in options.txt in the following format:
                option_name option_val_1 option_vak_2 ...

            Each option must be written in seperate line
            One option must be written in one line only

            e.g.
                maxwell_port /dev/ttyUSB0 2400
                network_port /dev/ttyUSB0 38400
                address 0.0.0.255

        """
        try:
            command_file = open(os.path.expanduser
                ("~/.grampower/gp_node/request_handler_options.txt"), "r")
        except Exception as e:
            self.error_message = """No options file found\n 
                    create options file as ~/.grampower/gp_node/request_handler_options.txt\n
                    The example content will be:\n  
                    maxwell_port /dev/ttyUSB0 2400\n
                                	network_port /dev/ttyUSB0 38400\n
                                	address 0.0.0.255"""
            sys.exit(self.error_message)		

        for line in command_file:
            prop = line.split(' ')
            if prop[0] == 'maxwell_port':
                self.my_maxwell_port =serial.Serial(prop[1],int(prop[2]), timeout=4)
            elif prop[0] == 'network_port':
                self.my_network_port =serial.Serial(prop[1],int(prop[2]), timeout=4)
                
            elif prop[0] == 'address':
                self.my_address = Address(prop[1])
                print prop[1]

        command_file.close()
        return



"""
Below are few tools which come handy in tests
Eventually all the tools should be a part of the request handler class
"""
class Timer:    
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start
        print self.interval


@contextlib.contextmanager
def no_stdout():

    """
    Prevent print to stdout, but if there was an error then catch it and
    print the output before raising the error.
    """
    saved_stdout = sys.stdout
    sys.stdout = cStringIO.StringIO()
    try:
        yield
    except Exception as err:
        saved_output = sys.stdout
        sys.stdout = saved_stdout
        print err
    sys.stdout = saved_stdout
    
def timer(timed):
    """
    Used to execute a command recursively for some time
    
    :param timed: the time till which generator should generate
    :type request: int
    
    ex usage:(will print "hello world" for 10 seconds)
        for i in timer(10):
            print "hello world"
    """
    initial_time = time.time()
    while True:
        yield (time.time() - initial_time) > timed
        if (time.time() - initial_time) > timed:
            return


