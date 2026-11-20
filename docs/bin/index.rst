Network Helper Binaries
=======================

The ``gp_node/bin`` folder contains some helper scripts which help in communicating (and more importantly, debugging) the network layer. We would be discussing these binaries in the following binaries in this document:

1. ``serial_sniffer.py``
2. ``tap_monitor.py``
3. ``tapcat.py``

Apart from the above mentioned scripts, the binary ``rc_shell.py`` is present in ``gp_node/bin``. This script helps in configuring a RC module with appropriate parameters.

tapcat
------

The ``tapcat.py`` binary is used to send arbitrary TAP packets to the node. This utility can be considered as a simpler version of ``node-shell``. Here is an example use case:

::
	
	tapcat.py --srcaddr 0.0.1.2 --destaddr 0.0.0.255 --srcport 4 --destport 4 -d /dev/gp-gateway "turn relay on"

This command would send the command ``turn relay on`` to ``0.0.0.255`` on port 4 (which is the port number of Simpleterm protocol). You can also send raw hex data using ``tapcat.py``

::

	tapcat.py --srcaddr 0.0.1.2 --destaddr 0.0.0.255 --srcport 4 --destport 4 -d /dev/gp-gateway "\x12\x87\xAB"

This command would send the bytes ``0x1287AB`` in the simpleterm payload (of course, this command does not make sense, but you now know how to send raw hex payload!). Using ``node-shell``, you can only send a select few TAP payloads; but ``tapcat.py`` allows you to send arbitrary TAP payloads.

sniffer & tap_monitor with node-shell
-------------------------------------

``serial_sniffer`` simply relays bytes between three types of files. For example:

.. graphviz::

	digraph
	{
		serial_sniffer[shape="rectangle"];
		tmp_dest[label="/tmp/dest"];
		dev_gateway[label="/dev/gp-gateway"];
		tmp_txdump[label="/tmp/txdump"];
		tmp_rxdump[label="/tmp/rxdump"];

		tmp_dest-> serial_sniffer[color="blue"];
		serial_sniffer -> tmp_dest[color="violet"];
		dev_gateway -> serial_sniffer[color="violet"];
		serial_sniffer -> dev_gateway[color="blue"];
		serial_sniffer -> tmp_rxdump[color="violet"];
		serial_sniffer -> tmp_txdump[color="blue"];
	}

Whatever data is received on ``/tmp/dest`` is transmitted on ``/dev/gp-gateway`` & also on ``/tmp/txdump``. Similarly, whatever data is received on ``/dev/gp-gateway`` is transmitted on ``/tmp/dest`` & also on ``/tmp/rxdump``.


The ``serial_sniffer`` and ``tap_monitor`` tools were written to allow us to read the packets being exchanged between the Python code and the Node board. ie, ``serial_sniffer`` eavesdrops over the data being exchanged between the computer and the node board.


Here is an example usage.

::

	bash$ serial_sniffer.py /dev/ttyUSB0 -b 38400

Running ``serial_sniffer.py`` opens three virtual ports, by the name ``/tmp/rxdump``, ``/tmp/txdump`` & ``/tmp/dest`` using the `socat <http://freecode.com/projects/socat>`_ program. Now, programs such as ``node-shell`` should use ``/tmp/dest`` instead of ``/dev/ttyUSB0`` for communicating with the node. The behavior from ``node-shell``'s perspective would be exactly as if it were using ``/dev/ttyUSB0``. ``serial_sniffer.py`` simply relays the bytes coming in from ``/dev/ttyUSB0`` into the ``/tmp/dest`` virtual device (& vice versa). 
::

	bash$ node-shell -d /tmp/dest -b 38400

At the same time, ``serial_sniffer.py`` sends all bytes sent on ``/tmp/dest`` on the ``/tmp/txdump`` virtual device. ie, you can open ``/tmp/txdump`` on cutecom and actually see the bytes which are being sent by ``node-shell``. But just looking at the bytes in the raw form is not very useful; hence, the tool ``tap_monitor.py`` should be used as it partially parses the outgoing bytes and displays the packet in a nicely formatted way. Similarly, all incoming bytes are read by ``serial_sniffer.py`` and relayed to the ``/tmp/rxdump`` virtual device.


::
	
	bash$ tap_monitor /tmp/rxdump

::
	
	bash$ tap_monitor /tmp/txdump

Here is a snapshot of 4 terminals using the ``serial_sniffer``, ``tap_monitor`` and ``node-shell`` to monitor the exact TAP packets sent/received while executing the simpleterm command ``relay state`` (which is supposed to return whether the relay is in auto/manual mode, and whether the relay is turned on or off)

.. image:: /_static/serial_sniffer_demo.png


Using sniffer with tapcat
-------------------------

Here is yet another small tutorial. Fire up a terminal and type in the following:


::

	bash$ serial_sniffer.py /dev/ttyUSB0 -b 38400

In a separate terminal, type in the following

::

	bash$ tap_monitor /tmp/txdump

In yet another terminal, type in the following

::

	tapcat.py --srcaddr 0.0.1.2 --destaddr 0.0.0.255 --srcport 4 --destport 4 -d /dev/gp-gateway "\x12\x87\xAB"

The byte being sent would be visible in the terminal where ``tap_monitor.py`` is running.


rc_shell
--------

``rc_shell`` is used to configure a raw radiocraft module. It is typically used to configure the gateway with appropriate network id, channel id etc. The gateway C++ code is rather simple, it simply acts as a bridge; ie, redirects all the imcoming bytes from FTDI cable to the TX line of the RC module; and similarly, redirects all the bytes from RX line of the RC module back to the FTDI cable. Hence, the ``rc_shell.py`` is actually responsible for properly formatting the commands to configure the RC module. Here is a typical usage of ``rc_shell.py``.


**Step 1**: start ``rc_shell.py`` after attaching the FTDI cable to the computer

::
	
	rc_shell.py -d /dev/gp-gateway

**Step 2**: Put the gateway in config mode by pressing the push button (pressing this push button will send a signal to the microcontroller to make the rc module enter configuration state)

.. image:: /_static/pmu_gateway_config_button.png

**Step 3**: Execute commands on ``rc_shell.py``. Here is an example:

::

	rc-shell $ network?

This will send raw hex commands as specified by the RC11XX datasheet. The RC module would reply back with the raw hex commands and this reply is then parsed by ``rc_shell.py`` to infer the network number of the RC module.

Here are some commonly used commands:

::

	rc-shell $ gateway
	rc-shell $ network=8
	rc-shell $ channel=7

The first command configures the RC module as a gateway (remember that the default state of the RC module is as a router). The next two commands set the appropriate network and channel id of the module.