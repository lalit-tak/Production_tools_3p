"""
This module deals with the following:
1. Framing packets for packet mode
2. Retrieving relevant information from ACK packets

Please look into the following sections in the tiny mesh data sheet
to have a better understanding:
1. Page 17 to page 22
"""
from gp_node.utils import Address
import time


class rfPacket(object):

	def __init__(self):
		self.start_byte = 7
		self.node_address = Address("0.0.0.0")
		self.command_num = 0
		self.fcstab = [
		0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
		0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
		0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
		0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
		0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
		0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
		0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
		0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
		0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
		0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
		0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
		0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
		0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
		0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
		0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
		0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
		0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
		0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
		0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
		0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
		0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
		0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
		0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
		0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
		0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
		0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
		0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
		0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
		0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
		0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
		0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
		0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78]
		

		

	def frame_rf_data_packet(self,dest_addr,TAP_packet_bytestream):
		"""
		Frames RF packet by adding the header information needed to
		transmit data in packet mode.
		:param dest_addr: Address of the node that we are sending the data to
		:type dest_addr: Address

		:param TAP_packet_bytestream: The data that needs to be populated in the
		 payload field of the RC serial packet
		:type TAP_packet_bytestream: bytearray

		:return :The RC packet mode packet
		:return type:bytearray
		"""
		#frames the RF packet by adding the header
		self.packet_type = 17
		tap_packet_length = len(TAP_packet_bytestream)
		print(tap_packet_length)
		dest_addr_num = dest_addr.dump_to_integer()
		buf = bytearray()
		self.start_byte = 7 + tap_packet_length
		buf.extend(chr(self.start_byte))     #start byte
		buf.extend(chr((dest_addr_num & 0x000000FF) >> 0))#address byte 1
		buf.extend(chr((dest_addr_num & 0x0000FF00) >> 8))#address byte 2
		buf.extend(chr((dest_addr_num & 0x00FF0000) >> 16))#address byte 3
		buf.extend(chr((dest_addr_num & 0xFF000000) >> 24))#address byte 4
		buf.extend(chr(1))                                #packet number
		buf.extend(chr(self.packet_type))
		for j in range(0, tap_packet_length):             #populate the payload
			buf.extend(chr(TAP_packet_bytestream[j]))
		temp = bytearray()
		temp.extend(buf)
		for byte in temp:
			print(hex(byte))
		return buf

	def parse_event_packet(self,data):
		"""
		Parses the ACK packet from the node and strips out useful network related
		information.
		:param data:The ACK data packet from the node.
		:type data: bytearray

		:return :Dictionary containing the header information
		:return type:type reply_dict (see implementation)
		"""
		START_CHARACTER_POS = 0
		SYSTEM_ID_POS = 1
		ORIGIN_ID_POS = 5
		ORIGIN_RSSI_POS = 9
		ORIGIN_NETWORK_LVL_POS = 10
		HOP_COUNTER_POS = 11
		MESSAGE_CNT_POS = 12
		LATENCY_CNT_POS = 14
		PKT_TYPE_POS = 16
		MSG_DETAIL_POS = 17
		MSG_DATA_MSB_POS = 18
		MSG_DATA_LSB_POS = 19
		ADDR_DATA_POS = 21
		TEMPERATURE_POS = 24
		VOLTAGE_POS = 25
		DIGITAL_IP_POS = 26
		ANG0_POS = 27
		ANG1_POS = 29
		HW_VER_POS = 31
		FW_VER_POS = 33
		reply_dict = {"start-character":0,"system-id":0,
		              "origin-id":Address("255.255.255.255"),"origin-rssi":0,
		              "origin-network-level":0,"hop-counter":0,"message-counter":0,
		              "latency-counter":0,"packet-type":0,"message-detail":0,
		              "message-data-msb":0,"message-data-lsb":0,"address-data":0,
		              "module-temprature":0,"module-voltage":0,"digital-inputs":0,
		              "analogue-0":0,"analogue-1":0,"hw-version":0,"fw-version":0}

		reply_dict["start-character"] = data[START_CHARACTER_POS]
		reply_dict["system-id"] = data[SYSTEM_ID_POS]
		
		addr = Address()
		addr.load_from_integer((data[ORIGIN_ID_POS]<<0) + (data[ORIGIN_ID_POS+1]<<8)
								+ (data[ORIGIN_ID_POS+2]<<16) + (data[ORIGIN_ID_POS+3]<<24))
		reply_dict["origin-id"] = str(addr)

		reply_dict["origin-rssi"] = data[ORIGIN_RSSI_POS]
		reply_dict["origin-network-level"] = data[ORIGIN_NETWORK_LVL_POS]
		reply_dict["hop-counter"] = data[HOP_COUNTER_POS]
		reply_dict["message-counter"] = (data[MESSAGE_CNT_POS]<<8) + (data[MESSAGE_CNT_POS+1])
		reply_dict["latency-counter"] = (data[LATENCY_CNT_POS]<<8) + data[LATENCY_CNT_POS+1]
		reply_dict["packet-type"] = data[PKT_TYPE_POS]
		reply_dict["message-detail"] = data[MSG_DETAIL_POS]
		reply_dict["message-data-msb"] = data[MSG_DATA_MSB_POS]
		reply_dict["message-data-lsb"] = data[MSG_DATA_LSB_POS]
		reply_dict["address-data"] = (data[ADDR_DATA_POS]<<0) + (data[ADDR_DATA_POS+1]<<8) \
		                             + (data[ADDR_DATA_POS+2]<<16) + (data[ADDR_DATA_POS+3] << 24)
		reply_dict["module-temprature"] = data[TEMPERATURE_POS] - 128 #refer tiny mesh data sheet page 35
		reply_dict["module-voltage"] = data[VOLTAGE_POS] *0.030       #refer tiny mesh datasheet page 35
		reply_dict["digital-inputs"] = data[DIGITAL_IP_POS]
		reply_dict["analogue-0"] = (data[ANG0_POS] << 8) + data[ANG0_POS+1]
		reply_dict["analogue-1"] = (data[ANG1_POS] << 8) + data[ANG1_POS+1]
		reply_dict["hw-version"] = (data[HW_VER_POS]<<8) + data[HW_VER_POS+1]
		reply_dict["fw-version"] = (data[FW_VER_POS]<<8) + data[FW_VER_POS+1]
		return reply_dict

	def crc16ccitt(self, data):
		buf = bytearray(data)
		crc = 0xFFFF
		i=0
		while(i<len(buf)):
			data_byte = buf[i]
			crc = (crc >> 8) ^ self.fcstab[(crc ^ data_byte) & 0xFF]
			i = i+1
		crc = crc ^ 0xFFFF
		return crc
