from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import nottest
from nose.plugins.attrib import attr
import time
import datetime
import dateutil.parser
from gp_node.request_handler.request_handler import RequestHandler,timer
from gp_node.network.protocols.packets.load_survey_params import LoadSurveyParams
import datetime
from gp_node.network.protocols.packets.bundle import Bundle

class TestLoadSurvey(object):
    @classmethod
    def setup_class(cls):
        print "Load Survey APP Tests"
        cls.testHandler = RequestHandler()
        cls.testHandler.handle_network_request("clear_load_survey",\
            validity_level="medium")
        cls.testHandler.handle_network_request("clear_account", \
            validity_level="medium")
        cls.set_survey_params("now+1",1)
        
    @classmethod
    def teardown_class(cls):
        cls.testHandler.handle_network_request("clear_account", \
            validity_level="medium")
        cls.testHandler.kill()

    def setUp(cls):
        """This method is run once before _each_ test method is executed"""

    def teardown(cls):
        """This method is run once after _each_ test method is executed"""


    @classmethod
    def set_survey_params(cls, start_time, interval):
        """
            The following lines for "set_survey_params" are jugad because 
            the network_api doesn't have a clean way of handling set_survey_params
            we should improve this eventually
        """
        cls.start_time = start_time
        cls.interval = interval
        if "now" in start_time:
            delta = int(cls.start_time.split("+")[1])
            cls.start_time = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            cls.start_time = dateutil.parser.parse(cls.start_time.strip(' '))
        cls.lsp = LoadSurveyParams()
        cls.lsp.start_time = cls.start_time
        cls.lsp.interval = int(cls.interval)
        cls.testHandler.my_network_api.set_survey_params(\
            addr=cls.testHandler.my_address, lsp=cls.lsp) 
        
    @attr(speed='fast')
    def test_01_clear_survey(self):
        """
        TEST1
        The test checks the clear_load_survey functionality
        """
        self.testHandler.handle_network_request("clear_load_survey", \
            validity_level="medium")
        time.sleep(1)
        result = self.testHandler.handle_network_request("get_num_surveys", \
            validity_level="high")
        assert_equal(int(result), 0)

    @attr(speed='fast')
    def test_02_set_get_params(self):
        """
        TEST2
        The test checks whether the set_survey_params & get_survey_params
        works fine.
        """
        input_date_time = "2014-10-10 10:10:10"
        input_interval = 1
        self.set_survey_params(input_date_time,input_interval)
        self.reply = str(self.testHandler.handle_network_request(\
            "get_survey_params", validity_level="high"))
        reply_date_time = self.reply.split(' ')[1] + ' ' + self.reply.split(' ')[2][0:8]
        reply_interval =  self.reply.split(' ')[3]
        assert_equal(reply_date_time, input_date_time)
        assert_equal(int(reply_interval), input_interval)
    
    @attr(speed='fast')    
    def test_03_clear_get_survey(self):
        """
        TEST3
        The test checks how the reply is when the load survey is cleared
        and a get_newest_survey is executed(ideally the reply should be blank)
        """
        self.testHandler.handle_network_request("clear_load_survey")
        assert_equal(self.testHandler.handle_network_request(\
            "get_newest_survey", validity_level="high"), ' ')
     
    @attr(speed='fast')    
    def test_04_clear_get_survey(self):
        """
        TEST4
        The test checks how the reply is when the load survey is cleared
        and a get_newest_survey is executed(ideally the reply should be blank)
        """
        self.testHandler.handle_network_request("clear_load_survey")
        assert_equal(int(self.testHandler.handle_network_request(\
            "get_num_surveys", validity_level="high")),0)
        assert_raises(Exception, self.testHandler.handle_survey_retrieve,1)
    
    @attr(speed='slow')    
    def test_05_check_load_surveying(self):
        """
        TEST5
        The test keeps the meter on for some time and checks if the 
        retrieved data matches the data set on simulator
        """
        #set the time duration for which the test needs to be done
        self.no_of_minutes = 3
        #Set parameters in simulator to validate against the survey data
        self.testHandler.handle_maxwell_request("time:now+1")
        self.testHandler.handle_maxwell_request("voltage:230")
        self.testHandler.handle_network_request("clear_load_survey")
        self.testHandler.handle_network_request("clear_account")
        self.testHandler.handle_network_request("recharge:50")
        time.sleep(5)
        self.response = Bundle()
        #will collect data bundles(load survey) for 2 or 3 seconds
        time.sleep(60*self.no_of_minutes + 10)
        
        self.no_of_surveys = int(self.testHandler.handle_network_request(
            "get_num_surveys", validity_level="high"))
        if isinstance(self.no_of_surveys, int):
            for i in range(self.no_of_surveys):
                self.reply_bundle_list = []
                self.temp_bundle = self.testHandler.handle_survey_retrieve(i)
                if isinstance(self.temp_bundle, Bundle):
                    #Check for beat time within the limit of the current time
                    self.reply_bundle_list.append(self.temp_bundle)
                    assert_equal((datetime.datetime.now() - \
                        self.temp_bundle.beat_time).total_seconds() < 190, True)
                    #Check for credits
                    assert_equal(int(self.temp_bundle.credits), 50)
                    #Check for voltage
                    assert_equal(self.temp_bundle.voltage, 230)
                else:
                    assert_raises(TypeError)
            """
            This validates the time stamp by checking difference beetween consecutive
            timestamps
            """
            for bundle in range(len(self.reply_bundle_list) - 1):
                assert_equal((self.reply_bundle_list[i+1].beat_time - \
                    self.reply_bundle_list[i].beat_time).total_seconds() \
                        < 70, True)
     
    @attr(speed='slow')  
    def test_06_survey_over_reset_cycles(self):
        """
        TEST6
        The test keeps the meter on reset cycles for some time and checks if the 
        retrieved data matches the data set on simulator
        """
        #set the time duration for which the test needs to be done
        self.no_of_minutes = 2
        #Set parameters in simulator to validate against the survey data
        self.testHandler.handle_maxwell_request("time:now+1")
        self.testHandler.handle_maxwell_request("voltage:230")
        self.testHandler.handle_network_request("clear_load_survey", 
            validity_level="medium")
        self.testHandler.handle_network_request("clear_account", 
            validity_level="medium")
        self.testHandler.handle_network_request("recharge:50")
        time.sleep(5)
        self.response = Bundle()
        #will collect data bundles(load survey) for 2 or 3 seconds
        for i in timer(60*self.no_of_minutes + 10):
            time.sleep(5)
            self.testHandler.handle_network_request("reset", print_on_stdout=False)
        
        self.no_of_surveys = int(self.testHandler.handle_network_request(\
            "get_num_surveys", validity_level="medium"))
        if isinstance(self.no_of_surveys,int):
            for i in range(self.no_of_surveys):
                self.reply_bundle_list = []
                self.temp_bundle = self.testHandler.handle_survey_retrieve(i)
                if isinstance(self.temp_bundle,Bundle):
                    #Check for beat time within the limit of the current time
                    self.reply_bundle_list.append(self.temp_bundle)
                    assert_equal((datetime.datetime.now() - \
                        self.temp_bundle.beat_time).total_seconds() < \
                            60*self.no_of_minutes + 10,True)
                    #Check for credits
                    assert_equal(int(self.temp_bundle.credits),50)
                    #Check for voltage
                    assert_equal(self.temp_bundle.voltage,230)
                else:
                    assert_raises(TypeError)
            """
            This validates the time stamp by checking difference beetween consecutive
            timestamps
            """
            for bundle in range(len(self.reply_bundle_list) - 1):
                print (self.reply_bundle_list[i+1].beat_time - \
                    self.reply_bundle_list[i].beat_time).total_seconds()
