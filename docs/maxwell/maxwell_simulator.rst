Maxwell Simulator
=================

The Maxwell Simulator is used to mimick the behavior of the Maxwell board's UART interface. The simulator is used to send periodic packets to the Node board over the UART line of the 12 pin connector. 

.. code-block:: console

	usage: maxwell-simulator [-h] [-d DEVICE] [-b BAUD]

	Simulates the Maxwell board. Sends packets on the FTDI cable as if the Maxwell
	board were sending it

	optional arguments:
	  -h, --help            show this help message and exit
	  -d DEVICE, --device DEVICE
	                        Device filename of the FTDI cable. Default is /dev/gp-
	                        gateway
	  -b BAUD, --baud BAUD  Baud rate to communicate with the Node board. Default
	                        is 2400


The following commands are implemented in the shell

.. code-block:: console
	
	clear_earth_tamper  clear_rev_tamper  phase_load        set_nd_tamper   voltage
	clear_mag_tamper    exit              power_factor      set_nm_tamper 
	clear_nd_tamper     frequency         set_earth_tamper  set_rev_tamper
	clear_nm_tamper     neutral_load      set_mag_tamper    time          

To know more about these commands, type in `help {command_name}` in the shell. For example, 

.. code-block:: console

	maxwell-simulator $ help voltage

	        Sets the voltage (in volts)
	        Example Usage: voltage 240.4


Implementation Details
----------------------

The maxwell-simulator is implemented using 3 threads. 

1. **Main Thread or Shell Thread**: The main thread runs the shell. This shell is responsible for getting inputs from the user. The user only feeds in "independent" variables; for example, the user only inputs *voltage*, *frequency*, *power_factor* etc. The dependent variables in the environment (such as *active_energy*) are calculated from the input variables. Once the input variables of the system are modified, an entry is passed in the *live_inputs_queue*. ie, everytime the user modifies any variables on the shell, an entry (a dictionary) is sent on the *live_inputs_queue*
2. **Meter Engine Thread**: This thread keeps listening for entries on the live_input_queue and keeps calculating all the dependent variables. For example, this thread is responsible for updating the value of *active_energy* consumed by the load so far. This thread keeps dumping the state of the environment (ie, all variables which define the environment) on the *live_env_queue* at a 1 Hz frequency. Note that the environment includes independent AND the dependent variables.
3. **UART Engine**: This thread keeps reading the *live_env_queue*, and sends Maxwell Packets at a 1 Hz frequency


.. graphviz::

	digraph
	{

		node[shape="oval"] shell_thread[label="Shell Thread"];
		node[shape="oval"] metering_thread[label="Metering Thread"];
		node[shape="oval"] uart_thread[label="UART Thread"];
		node[shape="box"] user[label="User"];
		node[shape="box"] serial_port[label="Serial Port"];
		
		user -> shell_thread;
		shell_thread -> metering_thread[label="*Inputs\n(live_inputs_queue)"];
		metering_thread -> uart_thread[label="*Environment\n(live_env_queue)"];
		uart_thread -> serial_port
	}

Refering to the above diagram, the communication between the User and the Shell Thread occurs whenever the user executes any command on the shell (say something like: `voltage 234.8`). For every command that the User executes on the shell, the Shell Thread also sends the updated state of Inputs on the `live_inputs_queue`. The inputs effectively contain the following information:

1. Time
2. Phase load (in ohms)
3. Neutral load (in ohms)
4. Voltage
5. Frequency
6. Power Factor
7. State of Earth Tamper
8. State of Neutral Missing Tamper
9. State of Neutral Disturbance Tamper
10. State of Line Load Reversal Tamper
11. State of Magnetic Tamper

Note that all the above mentioned variables are **independent variables**. ie, it is similar to the external variables which the Maxwell Board actually experiences. All other variables are then calculated by the Metering Thread.

The Metering Thread computes the state of the environment and sends the values to the UART Thread. The variables sent by the Metering Thread to the UART Thread over the `live_env_queue` are:


1. Time
2. Phase load (in ohms)
3. Neutral load (in ohms)
4. Voltage
5. Frequency
6. Power Factor
7. State of Earth Tamper
8. State of Neutral Missing Tamper
9. State of Neutral Disturbance Tamper
10. State of Line Load Reversal Tamper
11. State of Magnetic Tamper
12. Phase Current
13. Neutral Current
14. Active Power
15. Active Energy

The UART thread then serializes these values and sends them on the serial port of the computer at a 1 Hz frequency. For more details on the implementation of these three threads, refer the following links:

.. toctree::
   
   shell_thread
   metering_thread
   uart_thread