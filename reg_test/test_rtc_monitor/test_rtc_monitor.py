from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import timed
from nose.plugins.skip import Skip, SkipTest
from gp_node.request_handler.request_handler import RequestHandler
from gp_node.request_handler.request_handler import Timer
from gp_node.request_handler.request_handler import no_stdout
from gp_node.utils import Address
import datetime
import time


class TestRTCMonitor(object):
	"""
	TEST-SUIT : RTC Monitor

	The test suit tests the timely syncronization of node time with meter time.

	"""

	@classmethod
	def setup_class(self):
		print "################################################################"
		print "RTC Monitor APP Tests \n"
		self.test_handler = RequestHandler()
		self.test_handler.handle_network_request("set_power_limit:3000",3)
		self.test_handler.handle_network_request("clear_account",3)	
		self.test_handler.handle_network_request("recharge:1000",3)
		return

	@classmethod
	def teardown_class(self):
		self.test_handler.kill()
		return

	def setup(self):
		self.test_handler.handle_network_request("reset_lock",3)
		return

	def teardown(self):
		return

	def test_01_sync(self):
		"""
		TEST1 : The Test sets the date to 2013-10-10 10:30:41 in maxwell simulator and checks if
		node syncronizes with the set-time.
		"""
		change_time = datetime.datetime(2013, 10, 10, 10, 30, 41)
		set_time = '{}:{}'.format('time',str(change_time))
		self.test_handler.handle_maxwell_request(set_time)
		time.sleep(10)
		get_time = self.test_handler.handle_network_request("get_time",3)
		get_time = get_time.split(' ')
		get_time = datetime.datetime(*(int(x) for x in (get_time[0].split('-') + get_time[1].split(':'))))

		del_time = get_time-change_time

		assert_equal(del_time.seconds < 15,True)

	def test_02_valid_date(self):
		"""
		TEST2 : The Test sets the date to 2013-10-10 10:30:41 in maxwell simulator and checks if node
		syncronizes with valid time
		"""
		change_time = datetime.datetime(2013, 10, 10, 10, 30, 41)
		set_time = '{}:{}'.format('time',str(change_time))
		self.test_handler.handle_maxwell_request(set_time)
		time.sleep(15)
		self.test_handler.kill()
		time.sleep(10)
		get_time = self.test_handler.handle_network_request("get_time",3)
		get_time = get_time.split(' ')
		get_time = datetime.datetime(*(int(x) for x in (get_time[0].split('-') + get_time[1].split(':'))))

		del_time = get_time-change_time
		assert_equal(del_time.seconds < 40,True)