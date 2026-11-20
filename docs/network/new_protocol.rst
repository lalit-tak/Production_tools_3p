Creating a new Protocol
=======================

The base classes implemented ``protocol.py`` are used to implement all application level protocols. All application protocols such as ``Syncstream``, ``Simpleterm`` subclass from ``Protocol``. Also, ``SimpletermError``, ``SyncstreamError`` also subclass from ``ProtocolError``. These base classes provide the boilerplate code which is common to all applications.

.. autoclass:: gp_node.network.protocols.protocol.ProtocolMaster
   :members: __init__

.. autoclass:: gp_node.network.protocols.protocol.ProtocolError
   :members: __init__, __str__


Let us create a new protocol which simply sends the bytestream "AAA" to the client on port 10. Let us call this protocol ``DummyProtocol``. Create a new file ``gp_node/network/protocols/dummy_protocol.py`` and populate it with the following contents:

.. code-block:: python

	from gp_node.utils import Address
	from protocol import ProtocolMaster, ProtocolError
	from tap import TAPError

	class DummyProtocolError(ProtocolError):
	    pass


	class DummyProtocolMaster(ProtocolMaster):

	    SLAVE_PORT = 10
	    MASTER_PORT = 10

	    def send(self, slave_address):
	        self.my_tap_handler.send_packet(self.my_address, slave_address,
	                                        self.SLAVE_PORT, self.MASTER_PORT, bytearray("AAA"))
	        try:
	            packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
	        except TAPError as e:
	            raise DummyProtocolError(DummyProtocolError.TAP_ERROR, e)
	        return packet.data

You can use this protocol by running the following code snippet:

.. code-block:: python

	import serial
	from gp_node.network.protocols.tap import TAPHandler
	from gp_node.network.protocols.dummy_protocol import DummyProtocolMaster
	from gp_node.utils import Address


	if __name__ == "__main__":

		ser = serial.Serial("/dev/gp-gateway", 38400, timeout=3)
		my_tap_handler = TAPHandler(ser, 3)
		my_address = Address("0.0.1.2")
		my_dummy_protocol_master = DummyProtocolMaster(my_address, my_tap_handler)

		my_dummy_protocol_master.send()

Now, you can also add a ``network_api`` layer on top of this dummy protocol. Open ``network_api.py`` and create a new dummy protocol master in the ``__init__`` function of ``NetworkAPI``.

.. code-block:: python

	from protocols.dummy_protocol import DummyProtocolError, DummyProtocolMaster


	.
	.
	self.my_flash_io_master = FlashIOMaster(self.my_address, self.my_tap_handler)
	self.my_maxwell_bridge_master = MaxwellBridgeMaster(self.my_address, self.my_tap_handler)
	self.my_dummy_protocol_master = DummyProtocolMaster(self.my_address, self.my_tap_handler)

Now, add a network_api wrapper on top of dummy protocol's send() function

.. code-block:: python

	@check_errors
	def dummy_send(self, addr):
		return self.my_dummy_protocol_master.send(addr)

Now, we can directly access ``NetworkAPI`` to run this command

.. code-block:: python

	import serial
	from gp_node.utils import Address
	from gp_node.network.network_api import NetworkAPI, NetworkAPIError


	ser = serial.Serial("/dev/ttyUSB0", 38400, timeout=3)
	n_api = NetworkAPI(ser) 

	while True:
		try:
			reply = n_api.dummy_send(Address("0.0.0.255"))
		except NetworkAPIError as err:
			print(err)
		else:
			print reply


As a final step, this command can be added in ``node-shell``. Open ``node_shell.py`` and add the following function

.. code-block:: python

	def do_dummy_send(self, line):
		self.print_command(self.network_api.dummy_send, kwargs={})


To test the protocol, you can either actually implement the C++ Dummy protocol and have the C++ code respond back with some data, or you can just verify using ``serial_sniffer.py``, that the bytes AAA are actually being sent on ``/tmp/txdump``. To monitor the packets using ``tap_monitor.py``, you would need edit ``tap_monitor.py`` and update the dicionary in it as follows:

.. code-block:: python

	KNOWN_PORTS = {
	    0: "echo",
	    1: "time",
	    2: "SRP",
	    3: "recharge",
	    4: "simpleterm",
	    5: "syncstream",
	    6: "flash_io",
	    7: "maxwell_calibrate",
	    8: "tamper_record"
	    10: "dummy_protocol"
	};

Refer to the :doc:`/bin/index` tutorial on details.