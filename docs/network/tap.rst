TAP
===

TAP stands for Tiny Address Protocol. All higher level protocols (such as Syncstream, Simpleterm etc) use TAP under the hood.


Tutorial
--------

Probably, it makes sense to directly dive in and get an hands on introduction to TAP.

The standard way of using TAP to send packets is shown below. Save the program as `send.py`

.. code-block:: python

  import serial
  from gp_node.network.protocols.tap import TAPHandler
  from gp_node.utils.address import Address

  ser = serial.Serial("/tmp/txport", 9600, timeout=0)
  my_tap_handler = TAPHandler(ser, timeout=3)

  my_address = Address("0.0.1.4")
  my_port = 80
  receiver_address = Address("0.0.2.56")
  receiver_port = 30
  my_tap_handler.send_packet(my_address, receiver_address,
                          my_port, receiver_port, bytearray("hello world"))

To receive packet from a serial port, save the program shown below as `recv.py`

.. code-block:: python

  import serial
  from gp_node.network.protocols.tap import TAPHandler, TAPPacket, TAPError

  ser = serial.Serial("/tmp/rxport", 9600, timeout=0)
  my_tap_handler = TAPHandler(ser, timeout=3)
  
  while True:
    try:
      received_packet = my_tap_handler.get_packet()
    except TAPError as e:
      print "Error while parsing for packet. Error code: ", e.error_code
    else:
      print received_packet


Now, fire up a terminal and lets emulate two serial ports, namely `/tmp/rxport` and `/tmp/txport`.

.. code-block:: console

  socat PTY,link=/tmp/txport,raw,echo=0,b9600 PTY,link=/tmp/rxport,raw,echo=0,b9600

In a second terminal, run the `recv.py` program

.. code-block:: console

  python recv.py

The program should keep dumping the string "Error while parsing for packet. Error code: 1". This is expected,
as their is no one sending any packets. Hence the receiver timeouts. (error_code = 1 indicates a timeout)

Now, fire up a third terminal and run `send.py`

.. code-block:: console

  python send.py

You should now be able to see the contents of the sent packet in the second terminal. Congratulation :)

TAP Packet
----------

Structure of a TAP packet is as follows:

1: start byte (0xAA)

2-5: source address

6-9: destination address

10: source port

11: dest port

12: data length

13-12+data_len: payload

13+data_len: stop byte (0x55)


.. autoclass:: gp_node.network.protocols.tap.TAPPacket
   :members: __init__, __str__, __eq__, fill, serialize, deserialize


TAP Handler
-----------

.. autoclass:: gp_node.network.protocols.tap.TAPHandler
   :members: __init__, get_packet, get_packet_from, send_packet


TAPError
--------

.. autoclass:: gp_node.network.protocols.tap.TAPError
   :members: __init__
