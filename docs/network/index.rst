Network
=======
  
The gp_node.network subpackage implements the entire networking stack of the Node. This package provides a clean API to communicate with a Node in the network. The following program would keep quering the meter with address ``0.0.0.255`` (which is the broadcast address) for the voltage being measured and would keep printing out the voltage. All errors thrown out by the ``NetworkAPI`` are encapsulated in the ``NetworkAPIError``; In case of any error (for example, a timeout error), the error would be printed out.

.. code-block:: python

	import serial
	from gp_node.utils import Address
	from gp_node.network.network_api import NetworkAPI, NetworkAPIError


	ser = serial.Serial("/dev/ttyUSB0", 38400, timeout=3)
	n_api = NetworkAPI(ser) 

	while True:
		try:
			voltage = n_api.get_voltage(Address("0.0.0.255"))
		except NetworkAPIError as err:
			print(err)
		else:
			print("Voltage: {}".format(voltage))

An alternative way of using ``network_api`` is by using the ``handle_function_request`` method. This method takes as input a string, and calls a method with the same name. This method is used by ``conc-engine`` to execute transactions, as the request sent by ``conc-shell`` is just a string.

.. code-block:: python

	import serial
	from gp_node.utils import Address
	from gp_node.network.network_api import NetworkAPI, NetworkAPIError


	ser = serial.Serial("/dev/ttyUSB0", 38400, timeout=3)
	n_api = NetworkAPI(ser) 

	while True:
		try:
			voltage = n_api.handle_function_request(Address("0.0.0.255"), "get_voltage")
		except NetworkAPIError as err:
			print(err)
		else:
			print("Voltage: {}".format(voltage))


Programs such as the concentrator, calibration scripts etc. all execute the commands using the public API of ``NetworkAPI``.

**WARNING:** As of present implementation, the source address in ``network_api`` is ``0.0.1.2``. This means that ``network_api`` cannot be used to communicate with a node whose address is ``0.0.1.2``. The source address of ``network_api`` should be changed to something like ``244.244.244.244`` or something similar.

.. code-block:: console

	Network API -> Application Protocol -> TAP

To give an example, when the command ``network_api.get_voltage(Address("0.0.0.255"))`` is executed, the sequence of command calls looks like:

.. code-block:: console

	NetworkAPI.get_voltage()
		-> Simpleterm.get_param("voltage", UINT32)
			-> TAP.send_packet()
			-> TAP.get_packet()

Here, the ``Address("0.0.0.255")`` is implicitly assumed for the sake of brevity.



.. toctree:: 
   :maxdepth: 1

   tap
   application_protocols
   new_protocol
   error_handling
   circular_log

Files in network subpackage
---------------------------

The folder structure of the ``gp_node/network`` is as follows:

::

	gp_node/network
		circular_log
			circular_log.py:
			load_survey.py:
			log_reader.py
		protocols
			packets/
				bundle.py
				daily_deduction_params.py
				load_survey_params.py
				log_packet.py
				prepaid_account_packet.py
				tamper_record_packet.py
			flash_io.py
			maxwell_bridge.py
			protocol.py
			recharge.py
			simpleterm.py
			simpletime.py
			syncstream.py
			tap.py
		network_api.py


Here is a description of all the files

+---------------------------+-------------------------------------------------------+
|         File name         |                      Description                      |
+===========================+=======================================================+
| circular_log.py           | Implements base class (CircularLog) for directly      |
|                           | reading circular log data structure from external     |
|                           | flash chip of the node board using flash io protocol  |
+---------------------------+-------------------------------------------------------+
| load_survey.py            | subclasses from CircularLog to directly read          |
|                           | load survey data using flash io                       |
+---------------------------+-------------------------------------------------------+
| log_reader.py             | subclasses from CircularLog to directly  read         |
|                           | log events data using flash io                        |
+---------------------------+-------------------------------------------------------+
| bundle.py                 | implements the deserialization of load survey data.   |
|                           | Used in load_survey.py to deserialize load survey     |
|                           | data directly read using flash io. Also used in       |
|                           | simpleterm.py and network_api.py to implement         |
|                           | commands such as "get_newest_survey"                  |
+---------------------------+-------------------------------------------------------+
| daily_deduction_params.py | implements serialization and deserialization of       |
|                           | the parameters for daily deduction app.               |
|                           | Used in simpleterm.py, network_api.py                 |
+---------------------------+-------------------------------------------------------+
| load_survey_params.py     | implements serialization and deserialization of       |
|                           | the parameters for load survey app.                   |
|                           | Used in simpleterm.py, network_api.py                 |
+---------------------------+-------------------------------------------------------+
| log_packet.py             | implements deserialzation of log packets.             |
|                           | Used in simpleterm.py, network_api.py for             |
|                           | implementing commands such as "get_newest_log".       |
|                           | Also used in log_reader.py to deserialize log packets |
|                           | directly read using flash io protocol                 |
+---------------------------+-------------------------------------------------------+
| prepaid_account_packet.py | Used to deserialize data received by executing        |
|                           | command "get_accurate_credits". Used in simpleterm.py |
|                           | and network_api.py                                    |
+---------------------------+-------------------------------------------------------+
| tamper_record_packet.py   | Used to deserialize data received by executing        |
|                           | commands such as "get_tamper_record". Used in         |
|                           | simpleterm.py and in network_api.py                   |
+---------------------------+-------------------------------------------------------+
| flash_io.py               | Implements the Master of the FlashIO protocol         |
+---------------------------+-------------------------------------------------------+
| maxwell_bridge.py         | Implements the Master of the MaxwellBridge protocol   |
+---------------------------+-------------------------------------------------------+
| protocol.py               | Implements the base class for all protocols           |
|                           | such as FlahsIO, MasterBridge etc.                    |
+---------------------------+-------------------------------------------------------+
| recharge.py               | Implements the Master of the Recharge protocol        |
+---------------------------+-------------------------------------------------------+
| simpleterm.py             | Implements the Master of the Simpleterm protocol      |
+---------------------------+-------------------------------------------------------+
| simpletime.py             | Implements the Master of the Simpletime protocol      |
+---------------------------+-------------------------------------------------------+
| syncstream.py             | Implements the Master of the Syncstream protocol      |
+---------------------------+-------------------------------------------------------+
| tap.py                    | Implements the TAP layer which is used in all         |
|                           | application level protocols such as Simpleterm        |
+---------------------------+-------------------------------------------------------+
