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

class TestMaxwellMeterAPP(object):
	"""
	TEST-SUIT : MAXWELL METER APP

	The test suit tests the behaviour of Maxwell Meter App. Most of the tests include setting a parameter 
	in maxwell simulator and reading it them through Network API.
	"""

	@classmethod
	def setup_class(self):
		print "################################################################"
		print "Maxwell Meter APP Tests \n"
		self.test_handler = RequestHandler()
		self.test_handler.handle_network_request("set_power_limit:3000",3)
		self.test_handler.handle_network_request("disable_lock",3)
		self.test_handler.handle_network_request("clear_account",3)	
		self.test_handler.handle_network_request("recharge:1000",3)
		self.test_handler.handle_network_request("relay_auto_control",3)
		self.test_handler.handle_network_request("reset_tamper_latch",3)
		self.test_handler.handle_maxwell_request("phase_load:20")
		self.test_handler.handle_network_request("disable_elimiter",3)
		return

	@classmethod
	def teardown_class(self):
		self.test_handler.kill()
		return

	def setup(self):
		return

	def teardown(self):
		return

	def test_01_get_time(self):
		"""
		TEST1 : Compares the time from node board to system time
		"""
		meter_time = self.test_handler.handle_network_request("get_time",3)
		now = datetime.datetime.now()
		meter_time = meter_time.split(' ')
		meter_time = datetime.datetime(*(int(x) for x in (meter_time[0].split('-') + meter_time[1].split(':'))))
		sec = now-meter_time
		print sec.seconds
		assert_equal(0<=sec.seconds<=59,True)

	def test_02_get_voltage(self):
		"""
		TEST2 : Validates the voltage reading read by maxwell meter from simulator
		"""
		voltage = self.test_handler.handle_network_request("get_voltage",3)
		print voltage
		voltage = float(voltage.split(' ')[0])
		assert_equal(235.0<=voltage<=245.0,True)

	def test_03_get_phase_current(self):
		"""
		TEST3 : Validates the phase current reading read by maxwell meter from simulator
		"""
		phase_current = self.test_handler.handle_network_request("get_phase_current",3)
		print phase_current
		phase_current = float(phase_current.split(' ')[0])
		assert_equal(11.5<=phase_current<=12.5,True)

	def test_04_get_neutral_current(self):
		"""
		TEST4 : Validates the neutral current reading read by maxwell meter from simulator
		"""
		neutral_current = self.test_handler.handle_network_request("get_neutral_current",3)
		print neutral_current
		neutral_current = float(neutral_current.split(' ')[0])
		assert_equal(0<=neutral_current<=0.5,True)

	def test_05_get_current(self):
		"""
		TEST5 : Validates the current reading read by maxwell meter from simulator
		"""
		current = self.test_handler.handle_network_request("get_current",3)
		print current
		current = float(current.split(' ')[0])    	
		assert_equal(11.5<=current<=12.5,True)

	def test_06_get_active_power(self):
		"""
		TEST6 : Validates the active power reading read by maxwell meter from simulator
		"""
		active_power= self.test_handler.handle_network_request("get_active_power",3)
		print active_power 
		active_power= float(active_power.split(' ')[0])   	   	
		assert_equal(2850.0<=active_power<=2950.0, True)


	def test_07_get_power_factor(self):
		"""
		TEST7 : Validates the power factor reading read by maxwell meter from simulator
		"""
		power_factor= self.test_handler.handle_network_request("get_power_factor",3)
		print power_factor 
		power_factor= float(power_factor.split(' ')[0])    	   	
		assert_equal(0.9<=power_factor<=1.0, True)


	def test_08_get_frequency(self):
		"""
		TEST8 : Validates the frequency reading read by maxwell meter from simulator
		"""
		frequency= self.test_handler.handle_network_request("get_frequency",3)
		print frequency 
		frequency= float(frequency.split(' ')[0])    	   	
		assert_equal(49.8<=frequency<=50.2, True)

	def test_09_get_active_energy(self):
		"""
		TEST9 : Validates the active energy reading read by maxwell meter from simulator
		"""
		active_energy= self.test_handler.handle_network_request("get_active_energy",3)
		print active_energy 
		active_energy= float(active_energy.split(' ')[0])    	   	
		assert_equal(0.0<=active_energy<=100.0, True)


	def test_10_earth_tamper(self):
		"""
		TEST10 : Test the detection of earth tamper

		The tamper is first set in maxwell simulator and records are read through network API
		"""

		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			raise SkipTest	


		record = self.test_handler.handle_network_request("get_tamper_record:earth",3)
		no_of_tampers_prev =int(record.split('\n')[1].split(' ')[1])
		self.test_handler.handle_maxwell_request("set_earth_tamper")
		self.test_handler.handle_maxwell_request("clear_earth_tamper")
		record = self.test_handler.handle_network_request("get_tamper_record:earth",3)
		no_of_tampers_now =int(record.split('\n')[1].split(' ')[1])


		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)

		self.test_handler.handle_network_request("reset_tamper_latch",3)

		#assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1) & (relay_state == 'off'), True)

		assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1), True)
		

	def test_11_mag_tamper(self):
		"""
		TEST11 : Test the detection of magnetic tamper

		The tamper is first set in maxwell simulator and records are read through network API
		"""

		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			raise SkipTest	


		record = self.test_handler.handle_network_request("get_tamper_record:mag",3)
		no_of_tampers_prev =int(record.split('\n')[1].split(' ')[1])
		self.test_handler.handle_maxwell_request("set_mag_tamper")
		self.test_handler.handle_maxwell_request("clear_mag_tamper")
		record = self.test_handler.handle_network_request("get_tamper_record:mag",3)
		no_of_tampers_now =int(record.split('\n')[1].split(' ')[1])

		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)

		self.test_handler.handle_network_request("reset_tamper_latch",3)
		#assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1) & (relay_state == 'off'),True)

		assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1), True)


	def test_12_nd_tamper(self):
		"""
		TEST12 : Test the detection of nd tamper

		The tamper is first set in maxwell simulator and records are read through network API
		"""
		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			raise SkipTest	


		record = self.test_handler.handle_network_request("get_tamper_record:nd",3)
		no_of_tampers_prev =int(record.split('\n')[1].split(' ')[1])
		self.test_handler.handle_maxwell_request("set_nd_tamper")
		self.test_handler.handle_maxwell_request("clear_nd_tamper")
		record = self.test_handler.handle_network_request("get_tamper_record:nd",3)
		no_of_tampers_now =int(record.split('\n')[1].split(' ')[1])

		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)


		self.test_handler.handle_network_request("reset_tamper_latch",3)
		#assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1) & (relay_state == 'off'), True)
		assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1), True)


	def test_13_nm_tamper(self):
		"""
		TEST13 : Test the detection of nm tamper

		The tamper is first set in maxwell simulator and records are read through network API
		"""
		
		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			raise SkipTest	

		
		record = self.test_handler.handle_network_request("get_tamper_record:nm",3)
		no_of_tampers_prev =int(record.split('\n')[1].split(' ')[1])
		self.test_handler.handle_maxwell_request("set_nm_tamper")
		self.test_handler.handle_maxwell_request("clear_nm_tamper")
		record = self.test_handler.handle_network_request("get_tamper_record:nm",3)
		no_of_tampers_now =int(record.split('\n')[1].split(' ')[1])

		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)

		self.test_handler.handle_network_request("reset_tamper_latch",3)
		#assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1) & (relay_state == 'off'), True)
		assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1), True)

	@nottest
	def test_14_rev_tamper(self):
		"""
		TEST14 : Test the detection of rev tamper

		The tamper is first set in maxwell simulator and records are read through network API
		"""
		
		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			raise SkipTest	


		record = self.test_handler.handle_network_request("get_tamper_record:rev",3)
		no_of_tampers_prev =int(record.split('\n')[1].split(' ')[1])
		self.test_handler.handle_maxwell_request("set_rev_tamper")
		self.test_handler.handle_maxwell_request("clear_rev_tamper")
		record = self.test_handler.handle_network_request("get_tamper_record:rev",3)
		no_of_tampers_now =int(record.split('\n')[1].split(' ')[1])

		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)

		self.test_handler.handle_network_request("reset_tamper_latch",3)
		#assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1) & (relay_state == 'off'), True)
		assert_equal(((no_of_tampers_now-no_of_tampers_prev)==1), True)
	
	def test_15_all_tampers(self):
		"""
		TEST15 : Test the detection of all tampers simultaneously.

		The tamper is first set in maxwell simulator and records are read through network API
		"""
		
		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)
		if relay_state == 'off':
			raise SkipTest	


		record_earth = self.test_handler.handle_network_request("get_tamper_record:earth",3)
		record_mag = self.test_handler.handle_network_request("get_tamper_record:mag",3)
		record_nm = self.test_handler.handle_network_request("get_tamper_record:nm",3)
		record_nd = self.test_handler.handle_network_request("get_tamper_record:nd",3)
		record_rev = self.test_handler.handle_network_request("get_tamper_record:rev",3)

		record_earth_prev =int(record_earth.split('\n')[1].split(' ')[1])
		record_mag_prev =int(record_mag.split('\n')[1].split(' ')[1])
		record_nm_prev =int(record_nm.split('\n')[1].split(' ')[1])
		record_nd_prev =int(record_nd.split('\n')[1].split(' ')[1])
		record_rev_prev =int(record_rev.split('\n')[1].split(' ')[1])

		self.test_handler.handle_maxwell_request("set_earth_tamper")
		self.test_handler.handle_maxwell_request("set_mag_tamper")
		self.test_handler.handle_maxwell_request("set_nm_tamper")
		self.test_handler.handle_maxwell_request("set_nd_tamper")
		self.test_handler.handle_maxwell_request("set_rev_tamper")

		time.sleep(1)

		self.test_handler.handle_maxwell_request("clear_earth_tamper")
		self.test_handler.handle_maxwell_request("clear_mag_tamper")
		self.test_handler.handle_maxwell_request("clear_nm_tamper")
		self.test_handler.handle_maxwell_request("clear_nd_tamper")
		self.test_handler.handle_maxwell_request("clear_rev_tamper")

		record_earth = self.test_handler.handle_network_request("get_tamper_record:earth",3)
		record_mag = self.test_handler.handle_network_request("get_tamper_record:mag",3)
		record_nm = self.test_handler.handle_network_request("get_tamper_record:nm",3)
		record_nd = self.test_handler.handle_network_request("get_tamper_record:nd",3)
		record_rev = self.test_handler.handle_network_request("get_tamper_record:rev",3)

		record_earth_now =int(record_earth.split('\n')[1].split(' ')[1])
		record_mag_now =int(record_mag.split('\n')[1].split(' ')[1])
		record_nm_now =int(record_nm.split('\n')[1].split(' ')[1])
		record_nd_now =int(record_nd.split('\n')[1].split(' ')[1])
		record_rev_now =int(record_rev.split('\n')[1].split(' ')[1])

		relay_state = no_invalid_data(self.test_handler.handle_network_request,"relay_state",3)
		relay_state = relay_state.split(',')[0]
		print '{} {}'.format('relay is',relay_state)

		self.test_handler.handle_network_request("reset_tamper_latch",3)

		record = (record_earth_now + record_mag_now + record_nm_now + record_nd_now + record_rev_now) \
				 -(record_earth_prev + record_mag_prev + record_nm_prev + record_nd_prev + record_rev_prev)

		#assert_equal((record == 5) & (relay_state == 'off'), True)
		assert_equal((record == 5), True)

	
	def test_16_continuous_query(self):
		"""
		TEST16 : Tests the response if a query is made multiple times

		get_voltage is queried for 50 times.
		"""
		PASS = True
		for i in range(50):
			print i
			voltage = self.test_handler.handle_network_request("get_voltage",3)
			voltage = float(voltage.split(' ')[0])
			if voltage != 240.0 :
				PASS = False

		assert_equal(PASS,True)


	
	def test_17_first_query_after_reset(self):
		"""
		TEST17 : To find the time taken by first query after reset
		"""
		with no_stdout():
			self.test_handler.handle_network_request("reset",3)
		
		with Timer():
			voltage = self.test_handler.handle_network_request("get_voltage",3)
		
		voltage = float(voltage.split(' ')[0])
		assert_equal(voltage,240.0)




	def test_18_no_data_form_maxwell(self):
		"""
		TEST18 : To test the response of node if no data is received form maxwell board
		"""

		self.test_handler.kill()
		time.sleep(20)

		voltage_no_data = self.test_handler.handle_network_request("get_voltage",3)
		voltage_no_data = float(voltage_no_data.split(' ')[0])

		assert_equal(voltage_no_data,0.0)

		


