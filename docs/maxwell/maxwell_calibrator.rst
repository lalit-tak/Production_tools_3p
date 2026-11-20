Maxwell Calibrator
==================


.. code-block:: console

	usage: maxwell-calibrator [-h] [-d DEVICE] [-b BAUD]

	A shell to calibrate Maxwell board directly using a FTDI cable

	optional arguments:
	  -h, --help            show this help message and exit
	  -d DEVICE, --device DEVICE
	                        Device filename of the FTDI cable. Default is /dev/gp-
	                        gateway
	  -b BAUD, --baud BAUD  Baud rate to communicate with Maxwell board. Default
	                        is 2400

Implements the following commands:

.. code-block:: console

	cal_energy  cal_mtrno  cal_time  clear1  clear2

Refer to the Maxwell Calibrator Shell section below to understand the usage of these commands

Calibration Commands
--------------------

.. automodule:: gp_node.maxwell.calibrator.calibration_commands
   :members: get_command_string


Maxwell Calibrator Shell
------------------------

.. autoclass:: gp_node.maxwell.calibrator.maxwell_calibrator.MaxwellCalibrator
   :members:
