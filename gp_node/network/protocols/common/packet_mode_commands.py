"""
This modules is used to send commands specific to RC configuration
and status.
"""
from gp_node.utils import Address
import time
from .protocol import ProtocolMaster, ProtocolError
from .tap import TAPError
import gp_node.utils.serialize as serialize
import crc16
import os


class rfPacketModeCommandMaster(ProtocolMaster):


	def trace_path(self,address):
		"""
		Retrieves the path from the node to gateway.
		:param address: address of the intended node
		:type address: Address
		"""
		address_int = address.dump_to_integer()
		bytes_to_be_sent = bytearray()
		bytes_to_be_sent.extend(chr(0x0A))#start character
		#bytes_to_be_sent.extend(chr((address_int & 0xFF000000) >> 24))#address byte 1
		#bytes_to_be_sent.extend(chr((address_int & 0x00FF0000) >> 16))#address byte 2
		#bytes_to_be_sent.extend(chr((address_int & 0x0000FF00) >> 8))#address byte 3
		#bytes_to_be_sent.extend(chr((address_int & 0x000000FF) >> 0))#address byte 4
		bytes_to_be_sent.extend(chr((address_int & 0x000000FF) >> 0))#address byte 4
		bytes_to_be_sent.extend(chr((address_int & 0x0000FF00) >> 8))#address byte 3
		bytes_to_be_sent.extend(chr((address_int & 0x00FF0000) >> 16))#address byte 2
		bytes_to_be_sent.extend(chr((address_int & 0xFF000000) >> 24))#address byte 1
		bytes_to_be_sent.extend(chr(1))#command number
		bytes_to_be_sent.extend(chr(0x03))#packet type
		bytes_to_be_sent.extend(chr(0x16))#command argument - get packet path
		bytes_to_be_sent.extend(chr(0x00))#Dont care
		bytes_to_be_sent.extend(chr(0x00))#Dont care
		self.my_tap_handler.send_raw_bytes(bytes_to_be_sent)
		bytes_received = self.my_tap_handler.get_rc_packet()
		#debugg
		#print "system id :"
		#print "origin id :"
		#print "origin RSSI :",str(bytes_received[9]/-2.0),"dBm"
		#print "origin network level :",str(bytes_received[10])
		#print "hop count :",str(bytes_received[11])
		#print "message counter :",str((bytes_received[12]<<8) + bytes_received[13])
		#print "latency counter :",str(((bytes_received[14]<<8) + bytes_received[15])*10)," ms"
		#print "packet type :",str(bytes_received[16])
		#print "message detail :",str(bytes_received[17])
		hop_list = []
		for i in range(bytes_received[11]):
			#header =  "********************"+ "hop " + str(i) + "**************************"
			#print header
			#print "hop ",str(i),"RSSI ",str(bytes_received[18 + (i*5)]/-2.0),"dBm"
			address = str(bytes_received[22 + (i*5)]) + "." + str(bytes_received[21 + (i*5)])\
				+ "." + str(bytes_received[20 + (i*5)]) + "." + str(bytes_received[19 + (i*5)])
			#print "hop ",str(i),"address ",address
			hop_entry = []
			hop_entry.append(i)#hop number
			hop_entry.append(address) #Address
			hop_entry.append(bytes_received[18 + (i*5)]/-2.0) #RSSI reading
			hop_list.append(hop_entry)
		#print bytes_received
		return hop_list