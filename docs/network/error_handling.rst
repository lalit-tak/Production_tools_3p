Error Handling
==============

The error handling in the ``gp_node.network`` is a combination of exceptions and error codes. For example, whenever an error takes place in the TAP method calls, a ``TAPError`` exception is raised. The exception contains certain error codes to infer the exact kind of error. Possible errors at TAP layer are:

1. TIMEOUT_START_BYTE
2. TIMEOUT_LENGTH
3. STOP_BYTE_MISMATCH

If it were not for the error code, we would have had to make separate exception classes for ``TimeoutStartByteTAPError``, ``TimeoutLengthTAPError``, ``StopByteMismatchTAPError`` .. which would have been a bit unclean.	

Essentially, there are three layers of error handling:

1. ``NetworkAPIError``
2. ``{Application}Error``, where ``Application`` is something like ``Simpleterm``
3. ``TAPError``


``NetworkAPIError`` is the only type of error that is raised while executing methods of ``NetworkAPI``. For example, ``network_api.get_voltage`` might fail for various reasons. Probably, the error could be because of a timeout at TAP layer, or it could be because of incorrectly formatted reply from client. In any case, the ``NetworkAPIError`` would be raised & the exact cause of error would be encapsulated within the raised error. The diagram shown below depicts the various levels of error handling. 

.. graphviz::
	
	digraph
	{
		node[shape="rectangle"] network_api_error[label="NetworkAPIError"]
								protocol_error[label="ProtocolError"]
								tap_error[label="TAPError"];

		node[shape="oval"] network_api_error_code[label="Error Code"]
						   network_api_msg[label="msg"]

						   protocol_error_code[label="Error Code"]
						   protocol_tap_packet[label="TAPPacket"]

						   tap_error_code[label="Error Code"]

		network_api_error -> protocol_error;
		network_api_error -> network_api_error_code;
		network_api_error -> network_api_msg;
		protocol_error -> protocol_error_code;
		protocol_error -> protocol_tap_packet
		protocol_error -> tap_error;
		tap_error -> tap_error_code;
	}

Say for example, the command ``get_voltage`` had a timeout at TAP layer, in such a case, no ``TAPPacket`` would have been received. The diagram below shows how ``NetworkAPIError`` would look like in such an error case.


.. graphviz::
	
	digraph
	{
		node[shape="rectangle"] network_api_error[label="NetworkAPIError"]
								protocol_error[label="SimpletermError"]
								tap_error[label="TAPError"];

		node[shape="oval"] network_api_error_code[label="Error Code\n=PROTOCOL_ERROR"]
						   network_api_msg[label="msg=''"]

						   protocol_error_code[label="Error Code\n=TAP_ERROR"]

						   tap_error_code[label="Error Code\n=TIMEOUT_START_BYTE"]

		network_api_error -> protocol_error;
		network_api_error -> network_api_error_code;
		network_api_error -> network_api_msg;
		protocol_error -> protocol_error_code;
		protocol_error -> tap_error;
		tap_error -> tap_error_code;
	}

Say an error took place while executing recharge command, where in, the reply from client was not consistent with the recharge protocol. ie, in this case, the error is not in TAP layer, but is in the application protocol layer. The diagram below shows how ``NetworkAPIError`` would look like in such a case.

.. graphviz::

	digraph
	{
		node[shape="rectangle"] network_api_error[label="NetworkAPIError"]
								protocol_error[label="RechargeError"]

		node[shape="oval"] network_api_error_code[label="Error Code\n=PROTOCOL_ERROR"]
						   network_api_msg[label="msg=''"]

						   protocol_error_code[label="Error Code\n=HELLO_REPLY_INCORRECT"]

						   tap_packet[label="TAPPacket"]

		network_api_error -> protocol_error;
		network_api_error -> network_api_error_code;
		network_api_error -> network_api_msg;
		protocol_error -> protocol_error_code;
		protocol_error -> tap_packet;
	}

Finally, if you are using the ``handle_function_request`` method of ``network_api`` (just as ``conc-engine`` does), and if you pass in a string whose namesake function does not exist, then the ``NetworkAPIError`` would look as follows:

.. graphviz::

	digraph
	{
		node[shape="rectangle"] network_api_error[label="NetworkAPIError"]

		node[shape="oval"] network_api_error_code[label="Error Code\n=NO_FUNCTION_FOUND"]
						   network_api_msg[label="msg=''"]

		network_api_error -> network_api_error_code;
		network_api_error -> network_api_msg;

	}

