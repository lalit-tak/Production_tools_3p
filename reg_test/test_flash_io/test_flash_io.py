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



class TestFlashIO(object):
	"""
	TEST-SUIT : FLASH IO
	
	FlashIO handles reading and writing data to external flash using flash drivers.
	This test suit tests the maximum length of data to be written in one command, read and write
	at invalid address (0x2000 to 0x00fffff are valid addresses), and read-write with reset cycles. 
	"""

	@classmethod
	def setup_class(self):
		print "################################################################"
		print "Flash IO APP Tests \n"
		self.MESSAGE = '0x00 '*20

		self.test_handler = RequestHandler()
		self.test_handler.handle_network_request("set_power_limit:3000",3)
		self.test_handler.handle_network_request("clear_account",3)	
		self.test_handler.handle_network_request("recharge:1000",3)
		self.test_handler.handle_network_request("relay_auto_control",3)
		self.test_handler.handle_network_request("reset_tamper_latch",3)
		self.test_handler.handle_maxwell_request("phase_load:20")
		self.test_handler.handle_maxwell_request("time:now")
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

	def test_01_invalid_length(self):
		"""
		TEST1 : To test the data with invalid length

		40 bytes each of 0x00 are given to mem_write. Currently it gives a python error.
		"""
		invalid_data = '0x00 '*40
		write = "{}:{},{}".format("mem_write",'2000',invalid_data)
		response = self.test_handler.handle_network_request(write,3)
		print response
		


	def test_02_invalid_start_address_write(self):
		"""
		TEST2 : To test writing at invalid address of flash.

		20 bytes of data is given as argument to be written to address ffff0000.
		Currently it raises a FlashIO exception
		"""
		write = "{}:{},{}".format("mem_write",'ffff0000',self.MESSAGE)
		response = self.test_handler.
		(write,3)
		print response
	

	def test_03_invalid_start_address_read(self):
		"""
		TEST3 :To test writing at invalid address of flash.

		Test tries to read 20 bytes of data from ffff0000.
		Currently it gives FlashIO exception
		"""
		write = "{}:{},{}".format("mem_read",'ffff0000',20)
		response = self.test_handler.handle_network_request(write,3)
		print response

	def test_04_invalid_block_id(self):
		"""
		TEST4 : To test block erase at invalid block invalid_data

		Test tries to erase data from block id 16 (valid ids are from 0 to 15)
		It raises a FlashIO exception
		"""
		response = self.test_handler.handle_network_request("mem_erase_block:16",3)
		print response


	def test_05_read_write(self):
		"""
		TEST5 : To test reading and writing from external flash at valid address

		20 bytes of data is written at address 2000 and read back. If response equals 
		to the written bytes, the test PASSES
		"""
		self.test_handler.handle_network_request("mem_erase_block:1",3)
		write = "{}:{},{}".format("mem_write",2000,self.MESSAGE)
		response = self.test_handler.handle_network_request(write,3)
		write = "{}:{},{}".format("mem_read",2000,20)
		response = self.test_handler.handle_network_request(write,3)
		print self.MESSAGE
		print response
		assert_equal(response,str(bytearray(20)))


	def test_06_power_cycle(self):
		"""
		TEST06 : To test reading and writing to external flash with reset cycles

		20 bytes of data is written at address 2000 and read back. 3 reset cycles are done after each
		read/write/erase command
		"""
		self.test_handler.handle_network_request("mem_erase_block:1",3)
		for i in range(3):
			with no_stdout():
				self.test_handler.handle_network_request("reset",3)
			print 'reset ',i	

		write = "{}:{},{}".format("mem_write",2000,self.MESSAGE)
		response = self.test_handler.handle_network_request(write,3)

		for i in range(3):
			with no_stdout():
				self.test_handler.handle_network_request("reset",3)
			print 'reset ',i
		
		write = "{}:{},{}".format("mem_read",2000,20)
		response = self.test_handler.handle_network_request(write,3)
		
		for i in range(3):
			with no_stdout():
				self.test_handler.handle_network_request("reset",3)
			print 'reset ',i

		print self.MESSAGE
		print response
		assert_equal(response,str(bytearray(20)))




