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

class TestRCCommands(object):
	"""
	TEST-SUIT : RC COMMANDS

	This test suit tests the RC Commands that can be queried via network API.
	"""

	@classmethod
	def setup_class(self):
		print "################################################################"
		print "RC Commands Tests \n"
		self.test_handler = RequestHandler()
		return

	@classmethod
	def teardown_class(self):
		self.test_handler.kill()
		return

	def setup(self):
		return

	def teardown(self):
		return

	def test_01_set_network(self):
		"""
		TEST1 : To test the network setting

		The test sets the network as 9 and reads it back. If the response is
		equal to 9 then test PASSES
		"""
		self.test_handler.handle_network_request("set_network:9",3)
		response = self.test_handler.handle_network_request("get_network",3)
		assert_equal(response,9)

	def test_02_set_channel(self):
		"""
		TEST2 : To test channel setting

		The test channel as 4 and reads it back. If the response is equal to 4 
		then test PASSES.
		
		"""
		self.test_handler.handle_network_request("set_channel:4",3)
		response = self.test_handler.handle_network_request("get_channel",3)
		assert_equal(response,4)


