from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import timed
from nose.plugins.skip import Skip, SkipTest
from nose.plugins.attrib import attr

from gp_node.request_handler.request_handler import RequestHandler
from gp_node.request_handler.request_handler import Timer
from gp_node.request_handler.request_handler import no_stdout
from gp_node.utils import Address

import time
import datetime


#########################################################################################################

def no_invalid_data(func,*args):
	"""
	To retry the network request if ? received as response
	"""
	while(True):
		x = func(*args)
		if x != '?' :
			return x

class SODTestManager():
	"""
	Context manager to setup initial conditions and complete testing when exit for tests 6 to 8.
	"""
	test_num = 0
	def __init__(self,test_handler):
		self.test_handler = test_handler


	def __enter__(self):
		"""
		Resets the energy_limiter and ensures relay in auto mode
		"""
		SODTestManager.test_num = SODTestManager.test_num + 1
		self.test_handler.handle_network_request("disable_elimiter",3)
		self.test_handler.handle_network_request("enable_elimiter",3)
		self.test_handler.handle_network_request("relay_auto_control",3)
		time.sleep(1)	
	

	def __exit__(self, *args):
		"""
		Carries out the test. If relay is off initially then test is skipped. The test 
		needs three conditions to be true in order to pass:
		
		1) initial energy_consumed_today must be close to 0
		2) for each query successive energy_consumed_today must be non-decreasing
		3) relay turns off finally when energy limit is exceeded.

		"""

		self.PASS_TEST = True
		self.CONDITION1 = False   #energy consumed today must start form 0 as SOD is set
		self.CONDITION2 = True    #energy consumed today must be strictly non-decrementing function
		self.CONDITION3 = False   #Relay must turn off once limit is reached 

		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			raise SkipTest		
		

		last_energy = self.test_handler.handle_network_request("get_energy_consumed_today",3)
		print last_energy
		last_energy = int(last_energy.split(' ')[0])
		if 0<=last_energy<=5:
			self.CONDITION1 = True
		

	
		while last_energy<=10:

			now_energy = self.test_handler.handle_network_request("get_energy_consumed_today",3)
			print now_energy
			now_energy = int(now_energy.split(' ')[0])

			try:
				assert(last_energy<=now_energy)
			except:
				self.CONDITION2 = False

			last_energy = now_energy

		
		time.sleep(0.5)

		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		
		if (relay_state=='off'):
			self.CONDITION3 = True

		self.PASS_TEST = self.CONDITION1 & self.CONDITION2 & self.CONDITION3
		assert_equal(self.PASS_TEST,True)




#########################################################################################################

class TestEnergyLimiterAPP(object):
	"""
	TEST-SUIT : ENERGY LIMITER APP

	The test suit tests the behaviour of energy limiter app normally, in disable and with reset cycles.
	The tests also test the setting of SOD after power cuts.
	"""

	@classmethod
	def setup_class(self):
		"""
		TEST SUIT SETUP:

		sets power limit to 3000
		disables lock
		sets credits to 1000
		ensures relay in auto mode
		resets tamper reset_tamper_latch
		and sets load to 20 ohms in maxwell simulator
		"""
		print "################################################################"
		print "Energy Meter APP Tests \n"
		self.test_handler = RequestHandler()
		self.test_handler.handle_network_request("set_power_limit:3000",3)
		self.test_handler.handle_network_request("disable_lock",3)
		self.test_handler.handle_network_request("clear_account",3)	
		self.test_handler.handle_network_request("recharge:1000",3)
		self.test_handler.handle_network_request("relay_auto_control",3)
		self.test_handler.handle_network_request("reset_tamper_latch",3)
		self.test_handler.handle_maxwell_request("phase_load:20")
		return

	@classmethod
	def teardown_class(self):
		self.test_handler.kill()
		return

	def setup(self):
		self.test_handler.handle_network_request("disable_elimiter",3)
		self.test_handler.handle_network_request("enable_elimiter",3)
		self.test_handler.handle_network_request("set_energy_limit:10",3)
		time.sleep(1)
		return

	def teardown(self):
		return

	

	def test_01_energy_limit(self):
		"""
		TEST1 : To test the setting of energy limit 
		The checks if the energy limit set in setup is 10 Watt-hour
		"""

		response = self.test_handler.handle_network_request(
						"get_energy_limit",3)
		response = int(response.split(' ')[0])
		assert_equal(response,10)


	
	def	test_02_exceed_energy_limit(self):
		"""
			TEST2 : To test energy consumption at regular intervals and setting 
			of energyLimiteExceeded flag

			Initially if relay is off then test is skipped.
			energy_consumed_today is checked continuously and checked to be non-decreasing
			finally relay must turn off when energy limit is exceeded.

		"""
		PASS = True

		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			raise SkipTest		
		

		last_energy = self.test_handler.handle_network_request("get_energy_consumed_today",3)
		print last_energy
		last_energy = int(last_energy.split(' ')[0])
		

	
		while last_energy<=10:

			now_energy = self.test_handler.handle_network_request("get_energy_consumed_today",3)
			print now_energy
			now_energy = int(now_energy.split(' ')[0])

			try:
				assert(last_energy<=now_energy)
			except:
				PASS = False

			last_energy = now_energy

		


		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		
		

		assert_equal(((relay_state=='off') & PASS),True)





	@timed(65)
	def test_03_energy_limit_power_cycle(self):
		"""
		TEST3 : To test sanity of energy limit stored across power cycles

		Energy limit is set to 50 watt-hour
		Relay is tested to be in on state initally, otherwise the test is skipped.
		8 reset cycles are performed at a gap of 1 sec each
		finally relay is checked to be off when energy limit is exceeded.

		The test is restricted to pass in 65 sec as expected time for a 20 ohm load to reach 50 watt-hour is 62.5 sec. 
		Time taken by the test is also printed at the end (taken care of by Timer() context manager). 
		"""
		with Timer():
			self.test_handler.handle_network_request("set_energy_limit:50",3)
			relay_state = self.test_handler.handle_network_request("relay_state",3)
			relay_state = relay_state.split(',')[0]
			print '{} {}'.format('relay is',relay_state)		

			
			if relay_state == 'off':
				raise SkipTest		
			
			
			print self.test_handler.handle_network_request("get_energy_limit",3)



			for i in range(8):	
				with no_stdout():
					self.test_handler.handle_network_request("reset")
				print "reset"
				time.sleep(1)


			count = 0
			while(1):
				count = count+1
				relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
				print self.test_handler.handle_network_request("get_energy_consumed_today",3)	
				relay_state = relay_state.split(',')[0]
				if (relay_state == 'off') | (count > 10):
					break

		assert_equal(relay_state,'off')


	def test_04_disable_flag_set(self):
		"""
		TEST4 : To test energyLimitExceeded flag in disable

		if relay is off test is skipped.
		then sleeps for 15 seconds
		if relay turns off when limit exceeds, test fails 


		"""
		self.test_handler.handle_network_request("disable_elimiter",3)
		relay_state = self.test_handler.handle_network_request("relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)

		if relay_state == 'off':
			raise SkipTest		
		

		time.sleep(15)
		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		print relay_state
		assert_equal(relay_state == 'off',False)
		
	
	def test_05_nvm(self):
		"""
		TEST5 : To test registration of Energy Limiter APP with NVM Controller APP

		The test resets the node 10 times and checks if the energy limiter app is enabled. If the app is registered
		with nvm control then it enabled otherwise disables. If out of 10 times it registers for 9 times, Test PASSES
		"""
		count = 0
		for i in range(10):
			with no_stdout():
				self.test_handler.handle_network_request("reset")
			print 'reset', count

			self.test_handler.handle_network_request("set_energy_limit:10",3)
			limit = self.test_handler.handle_network_request("get_energy_consumed_today",3)
			limit = int(limit.split(' ')[0])

			if limit != -1:
				count = count+1
			if (i-count)>4 : 
				assert_equal(False,True)

		assert_equal(count>=9,True)



	def test_06_SOD_day(self):		
		"""
		TEST6 : Tests the setting of SOD when a power cut is for 1 day
		"""
		with SODTestManager(self.test_handler):
			print 'day changed'
			now= datetime.datetime.now()
			change_time = datetime.datetime(now.year, now.month, now.day+1, now.hour, now.minute, now.second)
			set_time = '{}:{}'.format('time',str(change_time))
			self.test_handler.handle_maxwell_request(set_time)
			time.sleep(10)


	def test_07_SOD_month(self):
		"""
		TEST7 : Tests the setting of SOD when a power cut is for 1 month
		"""	
		
		with SODTestManager(self.test_handler):
			print 'month changed'
			now= datetime.datetime.now()
			change_time = datetime.datetime(now.year, now.month+1, now.day, now.hour, now.minute, now.second)
			set_time = '{}:{}'.format('time',str(change_time))
			self.test_handler.handle_maxwell_request(set_time)
			time.sleep(10)


	def test_08_SOD_year(self):	
		"""
		TEST8 : Tests the setting of SOD when a power cut is for 1 year
		"""
		
		with SODTestManager(self.test_handler):
			print 'year changed'
			now= datetime.datetime.now()
			change_time = datetime.datetime(now.year+1, now.month, now.day, now.hour, now.minute, now.second)
			set_time = '{}:{}'.format('time',str(change_time))
			self.test_handler.handle_maxwell_request(set_time)
			time.sleep(10)



	def test_09_no_data_form_maxwell(self):
		"""
		TEST9 : To test the response of node if no data is received form maxwell board

		Maxwell simulator is killed and then get_active energy is queried
		"""

		energy = self.test_handler.handle_network_request("get_active_energy",3)
		energy = int(energy.split(' ')[0])
		self.test_handler.kill()
		time.sleep(2)

		energy_no_data = self.test_handler.handle_network_request("get_active_energy",3)
		energy_no_data = int(energy_no_data.split(' ')[0])

		if 0<=(energy_no_data - energy)<=1 :
			assert_equal(True,True)
		else:
			assert_equal(True,False)



		




