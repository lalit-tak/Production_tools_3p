Application Protocols
=====================

This page talks about the public API provided by the application level protocol's implementation. It is advised to first go through the PDF documents explaining the internals of these protocols before going through this page.

Simpleterm
----------

.. code-block:: python

	import serial
	from gp_node.network.protocols.tap import TAPHandler
	from gp_node.network.protocols.simpleterm import SimpletermMaster, PREPAID_ACCOUNT_PACKET, UINT32
	from gp_node.utils import Address

	if __name__ == "__main__":

		ser = serial.Serial("/dev/gp-gateway", 38400, timeout=3)
		my_tap_handler = TAPHandler(ser, 3)
		my_address = Address("0.0.1.2")
		my_simpleterm_master = SimpletermMaster(my_address, my_tap_handler)

		print my_simpleterm_master.execute_command(Address("0.0.0.255"), "turn relay on")

		# print my_simpleterm_master.get_param(Address("0.0.0.255"),"accurate_credits", PREPAID_ACCOUNT_PACKET)

		# print my_simpleterm_master.set_param(Address("0.0.0.255"), "network", 7, UINT32)


.. automodule:: gp_node.network.protocols.simpleterm
   :members:

+----------------------------+------------------------------------------------+
|         param_type         |                  Description                   |
+============================+================================================+
| UINT32 = 1                 | serializes/deserializes value as a 4 byte      |
|                            | unsigned integer                               |
+----------------------------+------------------------------------------------+
| INT32 = 2                  | serializes/deserializes value as a 4 byte      |
|                            | signed integer                                 |
+----------------------------+------------------------------------------------+
| TAMPER_RECORD_PACKET = 3   | deserializes value as a                        |
|                            | TamperRecordPacket() whose size is 18 bytes    |
+----------------------------+------------------------------------------------+
| DAILY_DEDUCTION_PARAMS = 4 | serializes/deserializes value as a             |
|                            | DailyDeductionParams() object whose size       |
|                            | is 12 bytes                                    |
+----------------------------+------------------------------------------------+
| BUNDLE = 5                 | deserializes value as a Bundle() whose size is |
|                            | 38 bytes                                       |
+----------------------------+------------------------------------------------+
| LOG_PACKET = 6             | deserializes value as a LogPacket() whose      |
|                            | size is 42 bytes                               |
+----------------------------+------------------------------------------------+
| LOAD_SURVEY_PARAMS = 7     | serializes/deserializes value as a             |
|                            | LoadSurveyParams() whose size is               |
|                            | 12 bytes                                       |
+----------------------------+------------------------------------------------+
| PREPAID_ACCOUNT_PACKET = 8 | deserializes value as a PrepaidAccountPacket() |
|                            | whose size is expected to be 14 bytes          |
+----------------------------+------------------------------------------------+


Recharge
--------

.. code-block:: python

	import serial
	from gp_node.network.protocols.tap import TAPHandler
	from gp_node.network.protocols.recharge import RechargeMaster
	from gp_node.utils import Address

	if __name__ == "__main__":

		ser = serial.Serial("/dev/gp-gateway", 38400, timeout=3)
		my_tap_handler = TAPHandler(ser, 3)
		my_address = Address("0.0.1.2")
		my_recharge_master = RechargeMaster(my_address, my_tap_handler)

		print my_recharge_master.recharge(Address("0.0.0.255"), 50)

.. automodule:: gp_node.network.protocols.recharge
   :members:


Syncstream
++++++++++

.. code-block:: python

	import serial
	import time
	import datetime
	from gp_node.network.protocols.tap import TAPHandler
	from gp_node.network.protocols.syncstream import SyncstreamMaster
	from gp_node.utils import Address

	if __name__ == "__main__":

		ser = serial.Serial("/dev/gp-gateway", 38400, timeout=3)
		my_tap_handler = TAPHandler(ser, 3)
		my_address = Address("0.0.1.2")
		my_syncstream_master = SyncstreamMaster(my_address, my_tap_handler)

		my_syncstream_master.setup(Address("0.0.0.255"), 
			start_time=datetime.datetime.now() + datetime.timedelta(seconds=5),
			interval=10)

		while True:
			time.sleep(10)
			print my_syncstream_master.get_bundle(Address("0.0.0.255"))


.. automodule:: gp_node.network.protocols.syncstream
   :members:

FlashIO
-------

.. code-block:: python

	import serial
	import time
	from gp_node.network.protocols.tap import TAPHandler
	from gp_node.network.protocols.flash_io import FlashIOMaster
	from gp_node.utils import Address

	if __name__ == "__main__":

		ser = serial.Serial("/dev/gp-gateway", 38400, timeout=3)
		my_tap_handler = TAPHandler(ser, 3)
		my_address = Address("0.0.1.2")
		my_flash_io_master = FlashIOMaster(my_address, my_tap_handler)

		my_flash_io_master.fetch(Address("0.0.0.255"), start_address=0x100,
		 	length=300, to_print=True)

.. automodule:: gp_node.network.protocols.flash_io
   :members:

MaxwellBridge
-------------

.. code-block:: python

	import serial
	import time
	from gp_node.network.protocols.tap import TAPHandler
	from gp_node.network.protocols.maxwell_bridge import MaxwellBridgeMaster
	from gp_node.utils import Address

	from gp_node.maxwell.calibrator.calibration_commands import (get_command_string,
		TIME_DATE_CODE)

	if __name__ == "__main__":

		ser = serial.Serial("/dev/gp-gateway", 38400, timeout=3)
		my_tap_handler = TAPHandler(ser, 3)
		my_address = Address("0.0.1.2")
		my_maxwell_bridge_master = MaxwellBridgeMaster(my_address, my_tap_handler)

		command = get_command_string(TIME_DATE_CODE)
		my_maxwell_bridge_master.send(Address("0.0.0.255"), command)

.. automodule:: gp_node.network.protocols.maxwell_bridge
   :members:


Simpletime
----------

This is a legacy protocol used only with DC meters now (ie, meters which don't have RTC in them)

.. code-block:: python

	import serial
	import time
	from gp_node.network.protocols.tap import TAPHandler
	from gp_node.network.protocols.simpletime import SimpletimeMaster
	from gp_node.utils import Address

	if __name__ == "__main__":

		ser = serial.Serial("/dev/gp-gateway", 38400, timeout=3)
		my_tap_handler = TAPHandler(ser, 3)
		my_address = Address("0.0.1.2")
		my_simpletime_master = SimpletimeMaster(my_address, my_tap_handler)

		my_simpletime_master.broadcast_time()


.. automodule:: gp_node.network.protocols.simpletime
   :members:
