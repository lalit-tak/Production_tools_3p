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

class TestPrepidAccount(object):
    @classmethod
    def setup_class(self):
        print "Prepaid Account APP Tests"
        self.testHandler = RequestHandler()
        self.testHandler.handle_network_request("deassert", validity_level="low")
        self.testHandler.handle_network_request("clear_account", validity_level="medium")
        
    @classmethod
    def teardown_class(self):
        self.testHandler.handle_network_request("clear_account", validity_level="medium")
        self.testHandler.kill()

    def setUp(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""

    @attr(speed='fast')
    # def test_01_clear_account(self):
    #     """
    #     TEST1
    #     The test checks the clear_load_survey functionality
    #     """
    #     self.testHandler.handle_network_request("recharge:50")
    #     self.testHandler.handle_network_request("clear_account", validity_level="medium")
    #     time.sleep(1)
    #     result = self.testHandler.handle_network_request("get_credits", validity_level="high")
    #     assert_equal(int(result.split(' ')[0]),0)
        
    # @attr(speed='fast')
    # def test_02_do_recharge(self):
    #     """
    #     TEST2
    #     The test for recharge happening properly
    #     """
    #     self.testHandler.handle_network_request("clear_account", \
    #         validity_level="medium")
    #     self.testHandler.handle_network_request("recharge:50")
    #     time.sleep(1)
    #     result = self.testHandler.handle_network_request("get_credits", \
    #         validity_level="high")
    #     assert_equal(int(result.split(' ')[0]),50)  
        
    # @attr(speed='fast')
    # def test_03_negative_recharges(self):
    #     """
    #     TEST3
    #     The test checks for negative recharges
    #     """
    #     self.testHandler.handle_network_request("clear_account", \
    #         validity_level="medium")
    #     self.testHandler.handle_network_request("recharge:50")
    #     self.testHandler.handle_network_request("recharge:-10")
    #     time.sleep(1)
    #     result = self.testHandler.handle_network_request("get_credits", \
    #         validity_level="medium")
    #     assert_equal(int(result.split(' ')[0]),40) 
        
    # @attr(speed='fast')
    # def test_04_negative_recharges(self):
    #     """
    #     TEST4
    #     The test checks for whether negative recharges takes credits below zero
    #     with "forbid_negative_credits"  
    #     """
    #     self.testHandler.handle_network_request("clear_account", \
    #         validity_level="medium")
    #     self.testHandler.handle_network_request("forbid_negative_credits", \
    #         validity_level="medium")
    #     self.testHandler.handle_network_request("recharge:50")
    #     time.sleep(0.5)
    #     self.testHandler.handle_network_request("recharge:-70")
    #     time.sleep(0.5)
    #     result = self.testHandler.handle_network_request("get_credits", \
    #         validity_level="high")
    #     assert_equal(int(result.split(' ')[0]),50)
        
    # @attr(speed='fast')
    # def test_05_negative_recharges(self):
    #     """
    #     TEST5
    #     The test checks for consecutive recharges
    #     """
    #     self.testHandler.handle_network_request("clear_account", \
    #         validity_level="medium")
    #     self.testHandler.handle_network_request("forbid_negative_credits", \
    #         validity_level="medium")
    #     for i in range(5):
    #         self.testHandler.handle_network_request("recharge:50")
    #         time.sleep(1)
    #     self.testHandler.handle_network_request("reset", print_on_stdout=False)
    #     result = self.testHandler.handle_network_request("get_credits", \
    #         validity_level="high")
    #     assert_equal(int(result.split(' ')[0]),250)
        
    # @attr(speed='fast')
    # def test_06_clear_recharges(self):
    #     """
    #     TEST6
    #     The test 'clear_recharges' work
    #     """
    #     self.testHandler.handle_network_request("recharge:70", validity_level="medium")
    #     self.testHandler.handle_network_request("recharge:-20")
    #     self.testHandler.handle_network_request("clear_recharges", validity_level="medium")
    #     assert_equal(int(self.testHandler.handle_network_request("get_pos_recharge", validity_level="high")),0)
    #     assert_equal(int(self.testHandler.handle_network_request("get_neg_recharge", validity_level="high")),0)
        
    # @attr(speed='fast')
    # def test_07_forbid_neg_recharges(self):
    #     """
    #     TEST7
    #     The test 'get_pos_recharge' & 'get_neg_recharge'
    #     """
    #     self.testHandler.handle_network_request("clear_account", validity_level="medium")
    #     self.testHandler.handle_network_request("forbid_negative_credits", validity_level="medium")
    #     self.testHandler.handle_network_request("recharge:70")
    #     self.testHandler.handle_network_request("recharge:-20")
    #     assert_equal(int(self.testHandler.handle_network_request("get_pos_recharge", validity_level="high")),70)
    #     time.sleep(0.5)
    #     assert_equal(int(self.testHandler.handle_network_request("get_neg_recharge", validity_level="high")),20)
    #     time.sleep(0.5)
    #     assert_equal(int(self.testHandler.handle_network_request("get_net_recharge", validity_level="high")),50)

    # @attr(speed='fast')
    # def test_08_set_price(self):
    #     """
    #     TEST8
    #     The test 'get_price' & 'set_price'
    #     """
    #     self.testHandler.handle_network_request("set_price:30", validity_level="medium")
    #     time.sleep(0.5)
    #     assert_equal(int(self.testHandler.handle_network_request("get_price", validity_level="high").split(' ')[0]),30)
                      
    # @attr(speed='fast')
    # def test_09_allow_neg_recharges(self):
    #     """
    #     TEST9
    #     The test 'get_pos_recharge' & 'get_neg_recharge'
    #     """
    #     self.testHandler.handle_network_request("clear_account", validity_level="medium")
    #     self.testHandler.handle_network_request("clear_recharges", validity_level="medium")
    #     self.testHandler.handle_network_request("allow_negative_credits", validity_level="medium")
    #     self.testHandler.handle_network_request("recharge:50")
    #     time.sleep(0.5)
    #     self.testHandler.handle_network_request("recharge:-60")
    #     result = self.testHandler.handle_network_request("get_credits", validity_level="high")
    #     assert_equal(int(self.testHandler.handle_network_request("get_credits", validity_level="high").split(' ')[0]),-10)
    #     assert_equal(int(self.testHandler.handle_network_request("get_pos_recharge", validity_level="high")),50)
    #     assert_equal(int(self.testHandler.handle_network_request("get_neg_recharge", validity_level="high")),60)
    #     assert_equal(int(self.testHandler.handle_network_request("get_net_recharge", validity_level="high")),-10)        
     
    # @attr(speed='fast')
    # def test_10_whole_credits(self):
    #     """
    #     TEST10
    #     The test whether changing price affects the credits 
    #     """
    #     self.testHandler.handle_network_request("set_price:30", validity_level="medium")
    #     initial_credits = int(self.testHandler.handle_network_request("get_credits", validity_level="high").split(' ')[0])
    #     time.sleep(0.5)
    #     self.testHandler.handle_network_request("set_price:100", validity_level="high")
    #     assert_equal(int(self.testHandler.handle_network_request("get_credits", validity_level="high").split(' ')[0]), initial_credits)

    
    # def test_11_fast_recharge(self):
    #     """
    #     TEST11 
    #     100 recharges continuously
    #     """
    #     count=0
    #     for i in range(100):
    #         if self.recharge_50():
    #             print i, count
    #             if count != i:
    #                 break
    #             else:
    #                 count = count+1

    #     assert_equal(count,i+1) 

    def test_12_credit_limit_set(self):
        """
        TEST12
        Testing credit limit
        """
        self.testHandler.handle_network_request("set_credit_limit:-10", validity_level="medium")
        response =  self.testHandler.handle_network_request("get_credit_limit", validity_level="medium")
        assert_equal(int(response), -10)

    def test_13_credit_limit_recharge_1(self):
        """
        TEST13
        To test the credit depreciation to credit limit
        """
        self.testHandler.handle_maxwell_request("phase_load 1")
        self.testHandler.handle_network_request("clear_account", validity_level="medium")
        self.testHandler.handle_network_request("set_price:100", validity_level="medium")
        self.testHandler.handle_network_request("set_credit_limit:-20", validity_level="medium")
        self.testHandler.handle_network_request("recharge:10", validity_level="medium")
        """
        set load to 1 ohm == 57600 watts
        -> 16 watt-hour in 1 sec
        ->  price set to 100 credits per kW-h
        ->  62.5 secs to consume 1 unit -> 100 credits
        """
        time.sleep(30)
        response = self.testHandler.handle_network_request("get_credits", validity_level="medium")
        response = int(response[0:-8])
        assert_equal(response, -20)

    def test_14_credit_limit_recharge_2(self):
        """
        TEST14
        To test recharge while credits are negattive
        """
        self.testHandler.handle_maxwell_request("phase_load 1000")
        self.testHandler.handle_network_request("clear_account", validity_level="medium")
        self.testHandler.handle_network_request("set_credit_limit:-20", validity_level="medium")
        self.testHandler.handle_network_request("recharge:-10", validity_level="medium")
        response = self.testHandler.handle_network_request("get_credits", validity_level="medium")
        response = int(response[0:-8])
        assert_equal(response, -10)

    def test_15_credits_limit_recharge_3(self):
        """
        TEST15
        To test recharge while credits are negattive and become positive after recharge
        """

        self.testHandler.handle_network_request("clear_account", validity_level="medium")
        self.testHandler.handle_network_request("set_credit_limit:-20", validity_level="medium")
        self.testHandler.handle_network_request("recharge:-10", validity_level="medium")
        self.testHandler.handle_network_request("recharge:20", validity_level="medium")
        response = self.testHandler.handle_network_request("get_credits", validity_level="medium")
        response = int(response[0:-8])
        assert_equal(response, 10)
    
    @nottest
    def recharge_50(self):
        
        while(1):
            response = self.testHandler.handle_network_request("get_credits")
            try:
                response = int(response)
            except:
                continue
            else: 
                if response==0:
                    break
                else:    
                    neg_credits = str(-response)
                    self.testHandler.handle_network_request("recharge:"+neg_credits)

       
        self.testHandler.handle_network_request("clear_account",validity_level="medium")
        time.sleep(0.1) 
        
        self.testHandler.handle_network_request("recharge:50",validity_level = "medium")
        time.sleep(0.1)
        
        response = self.testHandler.handle_network_request("get_credits",validity_level="medium")
        time.sleep(0.1)

        print response
        response = int(response[0:-8])
        if response%50 == 0 and response!=0:
            return True
        else:
            return False





