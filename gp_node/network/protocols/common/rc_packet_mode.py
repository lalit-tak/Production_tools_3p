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