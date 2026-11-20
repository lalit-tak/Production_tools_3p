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

def no_invalid_data(func,*args):
    while(True):
        x = func(*args)
        if x != '?' :
            return x


class TestLockAPP(object):
	"""
	TEST-SUIT : LOCK APP

	The test suit tests the locking and unlocking of LOCK and respective effect on relay

	"""

	@classmethod
	def setup_class(self):
		print "################################################################"
		print "Lock APP Tests \n"
		self.test_handler = RequestHandler()
		self.test_handler.handle_network_request("set_power_limit:3000",3)
		self.test_handler.handle_network_request("clear_account",3)	
		self.test_handler.handle_network_request("recharge:1000",3)
		self.test_handler.handle_network_request("relay_auto_control",3)
		self.test_handler.handle_network_request("reset_tamper_latch",3)
		self.test_handler.handle_maxwell_request("phase_load:20")
		self.test_handler.handle_maxwell_request("time:now")
		self.test_handler.handle_network_request("disable_elimiter",3)
		self.test_handler.handle_network_request("enable_lock",3)
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

	def test_01_unlock(self):
		"""
		TEST1 : To test the unlock period

		Initially if relay is on then test is skipped as initially the app is locked and relay 
		must be off

		The test unlocks the app for 1 day. Then time is changed on maxwell simulator
		with an increment of 1 day. If the lock resets and relay turns off, test PASSES

		"""
		self.CONDITION = True

		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'on':
			raise SkipTest	

		self.test_handler.handle_network_request("unlock:1",3)
		now = self.test_handler.handle_network_request("get_time",3)

		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			print 'Locked'
			self.CONDITION = False
			

		now = now.split(' ')
		now = datetime.datetime(*(int(x) for x in (now[0].split('-') + now[1].split(':'))))

		change_time = datetime.datetime(now.year, now.month, now.day+1, now.hour, now.minute, now.second)
		set_time = '{}:{}'.format('time',str(change_time))

		self.test_handler.handle_maxwell_request(set_time)


		time.sleep(10)

		state = self.test_handler.handle_network_request("lock_state",3)
		if state != 'locked':
			self.CONDITION = False
			print 'Unlocked'

		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'on':
			print 'Locked'
			self.CONDITION = False

		assert_equal(self.CONDITION, True)




	def test_02_disable_unlock(self):
		"""
		TEST2 : It tests the unlock period with disabling of app.

		The test unlocks the app for 1 day and then disables it.
		The date is then incremented by 1 day + 5 minutes in maxwell simulator.
		The app is then enabled, if it gets locked and relay turns off, it PASSES

		"""

		self.CONDITION = True


		self.test_handler.handle_network_request("unlock:1",3)
		now = self.test_handler.handle_network_request("get_time",3)

		state = self.test_handler.handle_network_request("lock_state",3)
		if state != 'unlocked':
			self.CONDITION = False
			print 'Locked'

		self.test_handler.handle_network_request("disable_lock",3)
		
		now = now.split(' ')
		now = datetime.datetime(*(int(x) for x in (now[0].split('-') + now[1].split(':'))))

		change_time = datetime.datetime(now.year, now.month, now.day+1, now.hour, now.minute+5, now.second)
		set_time = '{}:{}'.format('time',str(change_time))

		self.test_handler.handle_maxwell_request(set_time)


		time.sleep(10)
		self.test_handler.handle_network_request("enable_lock",3)
		
		state = self.test_handler.handle_network_request("lock_state",3)
		if state != 'locked':
			self.CONDITION = False
			print 'Unlocked'

		assert_equal(self.CONDITION, True)


	def test_03_unlock_validity(self):
		"""
		TEST3 : To test the unlock validity

		The test unlocks for 1 day and then checks for unlock validity. If validity is
		1 day, then it PASSES.
		"""
		self.test_handler.handle_network_request("unlock:1",3)
		
		valid = self.test_handler.handle_network_request("get_unlock_validity",3)
		valid = int(valid.split(' ')[0])

		assert_equal(valid,1)

	def test_04_last_unlock_time(self):
		"""
		TEST4 : To test last unlock time

		The test unlocks the app for 1 day and stores the time of node. If the last unlock time 
		does not differ form stored node time  by 30 seconds then, it PASSES
		"""
		self.test_handler.handle_network_request("unlock:1",3)

		now = self.test_handler.handle_network_request("get_time",3)
		now = now.split(' ')
		now = datetime.datetime(*(int(x) for x in (now[0].split('-') + now[1].split(':'))))

		stamp = self.test_handler.handle_network_request("get_last_unlock_timestamp",3)
		stamp = stamp.split(' ')
		stamp = datetime.datetime(*(int(x) for x in (stamp[0].split('-') + stamp[1].split(':'))))

		DIFF = now - stamp
		assert_equal(DIFF.seconds<=30,True)


	def test_05_time_since_unlock(self):
		"""
		TEST5 : To test time since unlock

		The test unlocks the app for 2 days. The date in maxwell simulator is incremented by 1 day.
		If time since unlock is 1 then it PASSES.
		"""

		self.test_handler.handle_network_request("unlock:2",3)
		now = self.test_handler.handle_network_request("get_time",3)
		now = now.split(' ')
		now = datetime.datetime(*(int(x) for x in (now[0].split('-') + now[1].split(':'))))

		change_time = datetime.datetime(now.year, now.month, now.day+1, now.hour, now.minute, now.second)
		set_time = '{}:{}'.format('time',str(change_time))

		self.test_handler.handle_maxwell_request(set_time)
		time.sleep(10)

		days = self.test_handler.handle_network_request("get_time_since_unlock",3)
		days = int(days.split(' ')[0])

		assert_equal(days,1)



	def test_06_unlock_reset_cycle(self):
		"""
		TEST6 : To test the behaviour of app with reset cycles at the time near unlock period expiry

		Relay is tested to be off, if its on the test is skipped.
		The app is unlocked for 1 day. Now the time in maxwell simulator is incremented by 1 day - 1 minute.

		After 10 reset cycles relay state is checked to be off. 
		"""
		self.CONDITION = True

		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'on':
			raise SkipTest	

		self.test_handler.handle_network_request("unlock:1",3)
		now = self.test_handler.handle_network_request("get_time",3)
		

		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			print 'Locked'
			self.CONDITION = False


		now = now.split(' ')
		now = datetime.datetime(*(int(x) for x in (now[0].split('-') + now[1].split(':'))))

		change_time = datetime.datetime(now.year, now.month, now.day+1, now.hour, now.minute-1, now.second)
		set_time = '{}:{}'.format('time',str(change_time))

		self.test_handler.handle_maxwell_request(set_time)
		time.sleep(30)

		for i in range(10):	
			with no_stdout():
				self.test_handler.handle_network_request("reset")
			print "reset"
			time.sleep(1)

		state = self.test_handler.handle_network_request("lock_state",3)
		if state != 'locked':
			self.CONDITION = False
			print 'Unlocked'

		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'on':
			print 'Locked'
			self.CONDITION = False

		assert_equal(self.CONDITION,True)
