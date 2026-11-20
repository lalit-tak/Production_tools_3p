from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.plugins.attrib import attr
import time
import datetime
from gp_node.request_handler.request_handler import RequestHandler,no_stdout

class TestLoggerApp(object):
    @classmethod
    def setup_class(self):
        print "Logger APP Tests"
        self.testHandler = RequestHandler()

    @classmethod
    def teardown_class(self):
        self.testHandler.handle_network_request("clear_account", \
            validity_level="medium")
        self.testHandler.kill()

    def setUp(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
    
    @attr(speed='fast')
    def test_01_clear_log(self):
        """
        TEST1
        The test checks the clear_log functionality
        """
        self.testHandler.handle_network_request("clear_log", \
            validity_level="low")
        time.sleep(1)
        result = self.testHandler.handle_network_request("get_num_logs", \
            validity_level="high")
        assert_equal(int(result), 0)
    
    @attr(speed='fast')   
    def test_02_log_order(self):
        """
        TEST2
        This tests if the logging is in chronological order 
        """
        self.testHandler.handle_network_request("clear_log", validity_level="low")

        self.testHandler.handle_network_request("reset", print_on_stdout=False)
        time.sleep(1)
        self.testHandler.handle_network_request("recharge:50")
        self.testHandler.handle_network_request("recharge:50")
        self.testHandler.handle_network_request("reset", print_on_stdout=False)
        time.sleep(1)
        
        retrieved_data = []
        no_of_logs = int(self.testHandler.handle_network_request(\
            "get_num_logs", validity_level="medium"))
        for i in range(no_of_logs):
            with no_stdout():
                retrieved_data.append(self.testHandler.handle_logger_retrieve(i))
        
        for i in range(no_of_logs - 1):
            dt1 = datetime.datetime.strptime(str(retrieved_data[i]).\
                split(": ")[0][0:19], '%Y-%m-%d %H:%M:%S')
            dt2 = datetime.datetime.strptime(str(retrieved_data[i + 1]).\
                split(": ")[0][0:19], '%Y-%m-%d %H:%M:%S')
            assert_equal(dt1 > dt2, False)
    
    @attr(speed='fast')  
    def test_03_log_number(self):
        """
        TEST3
        This is to check the 'get_num_logs' logic
        """
        self.testHandler.handle_network_request("clear_log")
        self.testHandler.handle_network_request("reset", print_on_stdout=False)
        self.testHandler.handle_network_request("recharge:50")
        time.sleep(1)       
        result = self.testHandler.handle_network_request("get_num_logs", \
            validity_level="high")
        assert_equal(int(result),2)
    
    @attr(speed='fast')    
    def test_04_first_last(self):
        """
        TEST4
        This test tests the get_newest_log & get_oldest_log
        """
        self.testHandler.handle_network_request("clear_log",no_of_tries=2)
        time.sleep(1)
        self.testHandler.handle_network_request("reset", print_on_stdout=False)
        self.testHandler.handle_network_request("recharge:50")
        self.testHandler.handle_network_request("reset", print_on_stdout=False)
        self.testHandler.handle_network_request("recharge:50")
        result1 = self.testHandler.handle_network_request("get_newest_log", \
            validity_level="high")
        result2 = self.testHandler.handle_network_request("get_oldest_log", \
            validity_level="high")
        assert_equal(result1.split(": ")[1][0:17], "Recharge success!")
        assert_equal(result2.split(": ")[1][0:17], "Version 5 started")
    
    @attr(speed='slow')       
    def test_05_stress_logger(self):
        """
        TEST5
        Stress tests the logger by doing 10 recharges
        """
        self.testHandler.handle_network_request("clear_log", no_of_tries=2)
        for i in range(10):
            self.testHandler.handle_network_request("recharge:50")
            
        retrieved_data=[]
        no_of_logs = int(self.testHandler.handle_network_request("get_num_logs", \
            no_of_tries=2, force_valid=True))
        for i in range(no_of_logs):
            with no_stdout():
                retrieved_data.append(self.testHandler.handle_logger_retrieve(i))
        for data in retrieved_data:
            assert_equal(str(data).split(": ")[1][0:17], "Recharge success!")

