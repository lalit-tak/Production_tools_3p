from gp_node.network.network_api import NetworkAPI, NetworkAPIError
from gp_node.utils import Address
import time
import serial
import os
import os.path
import sys
import time
import contextlib
import cStringIO
import logging

class RequestHandler_3P(object):
    """
    RequestHandler a very thin layer over available interfaces to the node
    board.The handler is designed for automatic regression tests where it is
    necessary to interact with node board using all the available interfaces
    simultaneously.

    It contains handles for :
    1.NetworkAPI
    The handles take care of exceptions and also provide some options to
    overcome communication errors(timeouts,bit corruptons etc)	
    
    Usage:
    Simpleterm commands can be called using "handle_network_request"
        ex:handle_network_request("get_voltage")

    """

    def __init__(self,network_api):
        """
        Does the following:
        * Reads port and baud rate for my_network_port and my_maxwell_port
        from options.txt
        * Initializes network_api, my_maxwell_api, logger & load_survey by
           acquiring the required parameters from "get_options()"
        """
        #self.get_options()
        self.my_network_api = network_api
        #self.my_network_api = NetworkAPI(self.my_network_port,"irda")
        #self.handle_network_request("reset", print_on_stdout=False, no_of_tries=2)
        #self.my_maxwell_api = MaxwellSimulatorAPI(self.my_maxwell_port.port, self.my_maxwell_port.baudrate)
        #self.logger = LogReader(self.my_network_api, 4, 42)
        #self.load_survey = LoadSurveyReader(self.my_network_api, 4, 42)
        #----------------------------------------------------------------
        self.file_logger = logging.getLogger(__name__)
        self.file_logger.setLevel(logging.INFO)
        # create a file handler
        self.handler = logging.FileHandler('tests.log')
        self.handler.setLevel(logging.INFO)

        # create a logging format
        self.formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        # add the handlers to the logger
        self.file_logger.addHandler(self.handler)
        return


    def handle_network_request(self, request, no_of_tries=4):         
        response = ""
        #self.file_logger.info(request)
        for try_no in range(no_of_tries):
            try:
                response=self.my_network_api.handle_function_request(Address("0.0.0.255"), request)
            except Exception as err:

                time.sleep(1)
            else:
                strt = '{} {}  {} {}  {} {}'.format('request',request,'response',response,'try_no:',try_no)
                self.file_logger.info(strt)
                return response
                break

        response = None
        strt = '{} {}  {} {}  {} {}'.format('request',request,'response',response,'try_no:',try_no)
        self.file_logger.info(strt)

        return None

        
  

    
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


