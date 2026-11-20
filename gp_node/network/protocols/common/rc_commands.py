"""
This module deals with the following:
1. Framing packets for packet mode
2. Retrieving relevant information from ACK packets

Please look into the following sections in the tiny mesh data sheet
to have a better understanding:
1. Page 17 to page 22
"""
import gp_node.utils.serialize as serialize
import time


class rcCommandPacket(object):
	RC_SET_ADDRESS = 45
	RC_SET_NETWORK = 49
	RC_SET_CHANNEL = 0
	RC_SET_RF_POWER = 1
	RC_SET_SERIAL_BUFF_MARGIN = 59
	LEN = {}

	RC_GET_ADDRESS = RC_SET_ADDRESS
	RC_GET_NETWORK = RC_SET_NETWORK
	RC_GET_CHANNEL = RC_SET_CHANNEL
	RC_GET_RF_POWER = RC_SET_RF_POWER

	def __init__(self):
		

		self.LEN[self.RC_SET_ADDRESS] = 4
		self.LEN[self.RC_SET_NETWORK] = 4
		self.LEN[self.RC_SET_CHANNEL] = 1
		self.LEN[self.RC_SET_RF_POWER] = 1
		self.LEN[self.RC_SET_SERIAL_BUFF_MARGIN] = 1

		self.CMD_MEM_READ = 1
		self.CMD_READ = 0



	def frame_rc_cmd_packet(self,data,type_cmd,cmd):
		temp_data = bytearray()
		temp_data = data
		buf = bytearray()
		buf.extend(chr(type_cmd))
		length = 0
		if (type_cmd == self.CMD_MEM_READ):
			buf.extend(chr(self.LEN[cmd]))
			buf.extend(chr(cmd))
			length = self.LEN[cmd]
		else:
			length = len(data)
			buf.extend(chr(length))

		for i in range(0,length):
			buf.extend(chr(temp_data[i]))

		while len(buf) < 8:
			buf.append(0)       
		return buf


	def frame_set_rc_mem_read_cmd(self,cmd,data):
		return self.frame_rc_cmd_packet( data,self.CMD_MEM_READ,cmd)

	def frame_set_rc_read_cmd(self,data):
		return self.frame_rc_cmd_packet( data,self.CMD_READ,0)

	def frame_get_rc_cmd(self,cmd):
		buf = bytearray()
		buf.extend(chr(cmd))
		buf.extend(chr(self.LEN[cmd]))
		while len(buf) < 4:
			buf.append(0)       
		return buf



		



