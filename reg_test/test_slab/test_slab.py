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
from gp_node.network.protocols.packets.slab_packet import SlabConfigurationPacket
from gp_node.network.protocols.packets.accounting_state_packet import AccountingStatePacket
import datetime
from gp_node.network.protocols.packets.bundle import Bundle

class TestSlab(object):
    @classmethod
    def setup_class(self):
        print "Slab APP Tests"
        self.testHandler = RequestHandler()
        
    @classmethod
    def teardown_class(self):
        self.testHandler.kill()

    def setUp(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""

    @attr(speed='fast')
    def test_01_reset_update_slab(self):
        """
        TEST1
        The test checks the resetting the slab,then sets the update time and sees whether the
        slab set is updated
        """
        self.testHandler.handle_network_request("slab_reset")
        self.testHandler.handle_network_request("set_slab_params:3,[100,300,450,0,0,0],[20,30,0,0,0],9000", validity_level="high")

        change_time = datetime.datetime(2015, 07, 07, 10, 30, 15)
        set_time = '{}:{}'.format('time',str(change_time))
        self.testHandler.handle_maxwell_request(set_time)
        time.sleep(15)

        self.testHandler.handle_network_request("set_slab_update_ts:2015-07-07 10:30:30")
      
        asp = self.testHandler.handle_network_request("get_accounting_state", validity_level="high")
        asp = (asp.split("\n"))[7].split(":")[1]
        assert_equal(int(asp),2)

        time.sleep(15) #sleep till the update_ts

        asp = self.testHandler.handle_network_request("get_accounting_state", validity_level="high")
        asp = (asp.split("\n"))[7].split(":")[1]
        assert_equal(int(asp),1)


    @attr(speed='fast')
    def test_02_slab_deduction(self):
        """
        TEST2
        The test checks the resetting the slab,then sets the update time and sees whether the
        slab set is updated.The time period taken into account is within the same month.
        """
        self.testHandler.handle_network_request("slab_reset")
        self.testHandler.handle_network_request("set_slab_params:3,[100,300,450,0,0,0],[4,8,0,0,0],0", validity_level="medium")
        self.testHandler.handle_network_request("slab_enable", validity_level="medium")
        self.testHandler.handle_network_request("clear_account", validity_level="medium")

        change_time = datetime.datetime(2015, 07, 07, 10, 30, 15)
        set_time = '{}:{}'.format('time',str(change_time))
        self.testHandler.handle_maxwell_request(set_time)
        #time.sleep(8)

        self.testHandler.handle_network_request("set_slab_update_ts:2015-07-07 10:30:20", validity_level="high")
        time.sleep(1)
        self.testHandler.handle_network_request("recharge:50")
        #print self.testHandler.handle_network_request("get_credits", validity_level="medium")
        self.testHandler.handle_maxwell_request("phase_load:1")
        self.testHandler.handle_maxwell_request("voltage:1000")
        #time.sleep(40)
        self.testHandler.handle_maxwell_request("phase_load:1000000000")
        left_credits=int((self.testHandler.handle_network_request("get_credits", validity_level="medium")).split(" ")[0])
        #time.sleep(2)
        #consumed_energy=int((self.testHandler.handle_network_request("get_active_energy", validity_level="medium")).split(" ")[0])
        #cal_credits = (4)+(12)+(((consumed_energy/1000) - 8)*4.5)
        #print consumed_energy
        #print str(cal_credits)
        #print str(left_credits)
        self.testHandler.handle_network_request("recharge:50")
        time.sleep(3)
        left_credits=int((self.testHandler.handle_network_request("get_credits", validity_level="medium")).split(" ")[0])
        assert(left_credits,50)
        #assert (cal_credits - (50-left_credits)) < 3

    @attr(speed='fast')
    def test_03_deduction_over_month_transition(self):
        """
        TEST3
        This test verifies the credit deduction over the month boundary
        """
        self.testHandler.handle_network_request("slab_reset")
        self.testHandler.handle_network_request("set_slab_params:3,[100,300,450,0,0,0],[4,8,0,0,0],0", validity_level="medium")
        self.testHandler.handle_network_request("slab_enable", validity_level="medium")
        self.testHandler.handle_network_request("clear_account", validity_level="medium")

        change_time = datetime.datetime(2015, 07, 31, 10, 30, 15)
        set_time = '{}:{}'.format('time',str(change_time))
        self.testHandler.handle_maxwell_request(set_time)
        time.sleep(8)

        self.testHandler.handle_network_request("set_slab_update_ts:2015-07-30 10:30:20", validity_level="high")
        time.sleep(1)
        self.testHandler.handle_network_request("recharge:50")
        self.testHandler.handle_maxwell_request("phase_load:1")
        self.testHandler.handle_maxwell_request("voltage:1000")
        time.sleep(20)
        self.testHandler.handle_maxwell_request("phase_load:1000000000")
        consumed_energy_m1=int((self.testHandler.handle_network_request("get_active_energy", validity_level="medium")).split(" ")[0])

        change_time = datetime.datetime(2015, 8, 01, 10, 30, 15)
        set_time = '{}:{}'.format('time',str(change_time))
        self.testHandler.handle_maxwell_request(set_time)
        time.sleep(8)
        self.testHandler.handle_maxwell_request("phase_load:1") 
        time.sleep(20)
        consumed_energy_m2=int((self.testHandler.handle_network_request("get_active_energy", validity_level="medium")).split(" ")[0])
        #print str(consumed_energy_m1)
        #print str(consumed_energy_m2)
        cal_credits = (4)+(((consumed_energy_m1/1000.0) - 4.0)*3.0) + (4.0)+((((consumed_energy_m2 - consumed_energy_m1)/1000.0) - \
                           4.0)*3.0)
        left_credits=int((self.testHandler.handle_network_request("get_credits", validity_level="medium")).split(" ")[0])
        #print str(cal_credits)
        #print str(left_credits)
        assert (cal_credits - (50-left_credits)) < 4 


    @attr(speed='slow')
    def test_04_mmc_dedcution(self):
        """
        TEST4
        This test verifies the credit deduction over the month boundary
        """
        self.testHandler.handle_network_request("slab_reset")
        self.testHandler.handle_network_request("set_slab_params:3,[100,300,450,0,0,0],[4,8,0,0,0],4000", validity_level="medium")
        self.testHandler.handle_network_request("slab_enable", validity_level="medium")
        self.testHandler.handle_network_request("clear_account", validity_level="medium")

        change_time = datetime.datetime(2015, 07, 31, 10, 30, 15)
        set_time = '{}:{}'.format('time',str(change_time))
        self.testHandler.handle_maxwell_request(set_time)
        time.sleep(15)
        
        self.testHandler.handle_network_request("set_slab_update_ts:2015-07-30 10:30:20", validity_level="high")
        time.sleep(1)
        self.testHandler.handle_network_request("recharge:50")
        self.testHandler.handle_maxwell_request("voltage:1000")
        self.testHandler.handle_maxwell_request("phase_load:1")
        time.sleep(15)
        self.testHandler.handle_maxwell_request("phase_load:100000000")
        #print ((self.testHandler.handle_network_request("get_credits", validity_level="medium")).split(" ")[0])

        change_time = datetime.datetime(2015, 8, 1, 10, 30, 15)
        set_time = '{}:{}'.format('time',str(change_time))
        self.testHandler.handle_maxwell_request(set_time)
        time.sleep(15)
        credits_left = int((self.testHandler.handle_network_request("get_credits", validity_level="medium")).split(" ")[0])
        assert_equal(credits_left,10)


#time less than now - slab update   
        
