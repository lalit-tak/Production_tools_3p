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

class TestTamperRecord(object):
    @classmethod
    def setup_class(self):
        print "Tamper Record APP tests"
        self.testHandler = RequestHandler()
        self.testHandler.handle_network_request("reset_tamper_record:all")
        self.testHandler.handle_network_request("clear_account")
        
    @classmethod
    def teardown_class(self):
        self.testHandler.handle_network_request("reset_tamper_record:all")
        self.testHandler.kill()

    def setUp(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
    
    
    def tamper_record_2_dict(str,rslt_str):
        rslt_dict = {}
        rslt_str =  rslt_str.strip('\n')
        for every in rslt_str.split('\n'):
            z=every.split(': ')
            rslt_dict[z[0]]=z[1]
        return rslt_dict
        
    @attr(speed='fast')
    def test_01_earth_tamper(self):
        """
        TEST1
        This tests earth tamper storage
        """
        self.testHandler.handle_network_request("reset_tamper_record:earth")
        start_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time"), '%Y-%m-%d %H:%M:%S')
        self.testHandler.handle_maxwell_request("set_earth_tamper")
        time.sleep(5)
        self.testHandler.handle_maxwell_request("clear_earth_tamper")
        time.sleep(1)
        stop_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time"), '%Y-%m-%d %H:%M:%S')
        rslt_dict = self.tamper_record_2_dict(self.testHandler.handle_network_request
        ("get_tamper_record:earth", no_of_tries=3, print_on_stdout=False))
        rslt_start_ts = datetime.datetime.strptime(rslt_dict['start_time'], '%Y-%m-%d %H:%M:%S')
        rslt_stop_ts = datetime.datetime.strptime(rslt_dict['end_time'], '%Y-%m-%d %H:%M:%S')
        #checks wether the tamper registration happens within 4 seconds
        assert_equal(abs((start_ts - rslt_start_ts).total_seconds()) <= 4, True)
        #checks wether the time diff b/w start and stop of tamper is acceptable
        assert_equal(abs((stop_ts - rslt_stop_ts).total_seconds()) <= 4, True)
        #checks wether the retrivedd tamper type is same as requested tamper type
        assert_equal(rslt_dict['tamper_type'], 'earth_tamper_record')
        #checka the tamper count
        assert_equal(int(rslt_dict['tamper_count']), 1)
    
    @attr(speed='fast')
    def test_02_reverse_tamper(self):
        """
        TEST2
        This tests reverse tamper storage
        """
        self.testHandler.handle_network_request("reset_tamper_record:rev")
        start_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        self.testHandler.handle_maxwell_request("set_rev_tamper")
        time.sleep(5)
        self.testHandler.handle_maxwell_request("clear_rev_tamper")
        time.sleep(1)
        stop_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        rslt_dict = self.tamper_record_2_dict(self.testHandler.handle_network_request
            ("get_tamper_record:rev", no_of_tries=3, print_on_stdout=False))
        rslt_start_ts = datetime.datetime.strptime(rslt_dict['start_time'], '%Y-%m-%d %H:%M:%S')
        rslt_stop_ts = datetime.datetime.strptime(rslt_dict['end_time'], '%Y-%m-%d %H:%M:%S')
        #checks wether the tamper registration happens within 4 seconds
        assert_equal(abs((start_ts - rslt_start_ts).total_seconds()) <= 4, True)
        #checks wether the time diff b/w start and stop of tamper is acceptable
        assert_equal(abs((stop_ts - rslt_stop_ts).total_seconds()) <= 4, True)
        assert_equal(rslt_dict['tamper_type'], 'rev_tamper_record')
        assert_equal(int(rslt_dict['tamper_count']), 1)
   
    @attr(speed='fast')
    def test_03_nm_tamper(self):
        """
        TEST3
        This tests nm tamper storage
        """
        self.testHandler.handle_network_request("reset_tamper_record:nm")
        start_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3),'%Y-%m-%d %H:%M:%S')
        self.testHandler.handle_maxwell_request("set_nm_tamper")
        time.sleep(5)
        self.testHandler.handle_maxwell_request("clear_nm_tamper")
        time.sleep(1)
        stop_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        rslt_dict = self.tamper_record_2_dict(self.testHandler.handle_network_request
            ("get_tamper_record:nm", no_of_tries=3, print_on_stdout=False))
        rslt_start_ts = datetime.datetime.strptime(rslt_dict['start_time'],'%Y-%m-%d %H:%M:%S')
        rslt_stop_ts = datetime.datetime.strptime(rslt_dict['end_time'],'%Y-%m-%d %H:%M:%S')
        #checks wether the tamper registration happens within 4 seconds
        assert_equal(abs((start_ts - rslt_start_ts).total_seconds()) <= 4, True)
        #checks wether the time diff b/w start and stop of tamper is acceptable
        assert_equal(abs((stop_ts - rslt_stop_ts).total_seconds()) <= 4, True)
        assert_equal(rslt_dict['tamper_type'], 'nm_tamper_record')
        assert_equal(int(rslt_dict['tamper_count']), 1)
        
    @attr(speed='fast')
    def test_04_nd_tamper(self):
        """
        TEST4
        This tests nd tamper storage
        """
        self.testHandler.handle_network_request("reset_tamper_record:nd")
        start_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        self.testHandler.handle_maxwell_request("set_nd_tamper")
        time.sleep(5)
        self.testHandler.handle_maxwell_request("clear_nd_tamper")
        time.sleep(1)
        stop_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        rslt_dict = self.tamper_record_2_dict(self.testHandler.handle_network_request
            ("get_tamper_record:nd", no_of_tries=3, print_on_stdout=False))
        rslt_start_ts = datetime.datetime.strptime(rslt_dict['start_time'], '%Y-%m-%d %H:%M:%S')
        rslt_stop_ts = datetime.datetime.strptime(rslt_dict['end_time'], '%Y-%m-%d %H:%M:%S')
        #checks wether the tamper registration happens within 4 seconds
        assert_equal(abs((start_ts - rslt_start_ts).total_seconds()) <= 4, True)
        #checks wether the time diff b/w start and stop of tamper is acceptable
        assert_equal(abs((stop_ts - rslt_stop_ts).total_seconds()) <= 4, True)
        assert_equal(rslt_dict['tamper_type'], 'nd_tamper_record')
        assert_equal(int(rslt_dict['tamper_count']), 1)
        
    @attr(speed='fast')
    def test_05_mag_tamper(self):
        """
        TEST5
        This tests mag tamper storage
        """
        self.testHandler.handle_network_request("reset_tamper_record:mag")
        start_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        self.testHandler.handle_maxwell_request("set_mag_tamper")
        time.sleep(5)
        self.testHandler.handle_maxwell_request("clear_mag_tamper")
        time.sleep(1)
        stop_ts = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        rslt_dict = self.tamper_record_2_dict(self.testHandler.handle_network_request
            ("get_tamper_record:mag", no_of_tries=3, print_on_stdout=False))
        rslt_start_ts = datetime.datetime.strptime(rslt_dict['start_time'], '%Y-%m-%d %H:%M:%S')
        rslt_stop_ts = datetime.datetime.strptime(rslt_dict['end_time'], '%Y-%m-%d %H:%M:%S')
        #checks wether the tamper registration happens within 4 seconds
        assert_equal(abs((start_ts - rslt_start_ts).total_seconds()) <= 4 ,True)
        #checks wether the time diff b/w start and stop of tamper is acceptable
        assert_equal(abs((stop_ts - rslt_stop_ts).total_seconds()) <= 4, True)
        assert_equal(rslt_dict['tamper_type'], 'mag_tamper_record')
        assert_equal(int(rslt_dict['tamper_count']), 1)
        
    @attr(speed='slow')
    def test_06_tamper_comb(self):
        """
        TEST6
        This tests cominations of tamper storage
        The occurences of tamper is in the following order
        1.earth
        2.rev
        3.nm + nd
        4.mag
        """
        tamper_name_list = ["earth", "rev", "nm", "nd", "mag"]
        start_ts_dict = {}
        stop_ts_dict = {}
        self.testHandler.handle_network_request("reset_tamper_record:all")
        #For earth tamper
        start_ts_dict["earth"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        self.testHandler.handle_maxwell_request("set_earth_tamper")
        time.sleep(5)
        self.testHandler.handle_maxwell_request("clear_earth_tamper")
        time.sleep(1)
        stop_ts_dict["earth"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        
        #for rev tamper
        start_ts_dict["rev"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        self.testHandler.handle_maxwell_request("set_rev_tamper")
        time.sleep(5)
        self.testHandler.handle_maxwell_request("clear_rev_tamper")
        time.sleep(1)
        stop_ts_dict["rev"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        
        #for nm + nd tamper
        start_ts_dict["nm"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        start_ts_dict["nd"] = start_ts_dict["nm"]
        self.testHandler.handle_maxwell_request("set_nm_tamper")
        self.testHandler.handle_maxwell_request("set_nd_tamper")
        time.sleep(3)
        self.testHandler.handle_maxwell_request("clear_nm_tamper")
        time.sleep(1)
        stop_ts_dict["nm"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')
        time.sleep(2)
        self.testHandler.handle_maxwell_request("clear_nd_tamper")
        time.sleep(1)
        stop_ts_dict["nd"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')

        #for mag tamper
        start_ts_dict["mag"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3),'%Y-%m-%d %H:%M:%S')
        self.testHandler.handle_maxwell_request("set_mag_tamper")
        time.sleep(5)
        self.testHandler.handle_maxwell_request("clear_mag_tamper")
        time.sleep(1)
        stop_ts_dict["mag"] = datetime.datetime.strptime(
            self.testHandler.handle_network_request("get_time", no_of_tries=3), '%Y-%m-%d %H:%M:%S')

        
        rslt = {}
        for tamper in tamper_name_list:
            rslt_dict = self.tamper_record_2_dict(self.testHandler.handle_network_request
                ("get_tamper_record:" + tamper, no_of_tries=3, print_on_stdout=False))
            #checks wether the tamper start registration happens within 4 seconds
            rslt_start_ts = datetime.datetime.strptime(rslt_dict['start_time'], '%Y-%m-%d %H:%M:%S')
            assert_equal(abs((start_ts_dict[tamper] - rslt_start_ts).total_seconds()) <= 4,True)
            #checks wether the tamper stop registration happens within 4 seconds
            rslt_stop_ts = datetime.datetime.strptime(rslt_dict['end_time'], '%Y-%m-%d %H:%M:%S')
            assert_equal(abs((rslt_stop_ts - stop_ts_dict[tamper]).total_seconds()) <= 4, True)
            #checks if the retrieved tamper type is same as requested
            assert_equal(rslt_dict['tamper_type'], tamper + '_tamper_record')
            #check for tamper count
            assert_equal(int(rslt_dict['tamper_count']), 1)
                      

