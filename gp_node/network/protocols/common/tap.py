"""
Definition of the TAP, used as the basis 
for Gram Power network communication.
"""

import time
import sys
from gp_node.utils import Address
import crcmod

crc16 = crcmod.predefined.mkPredefinedCrcFun('xmodem')
import gp_node.utils.serialize as serialize
from gp_node.network.protocols.common.rc_packet_mode import rfPacket
from gp_node.network.network_log.network_log import networkDataLogger
from copy import deepcopy
import os
import os.path
import binascii


class TAPError(Exception):
    """
    The values of error code can be:

    TAPError.TIMEOUT_START_BYTE: used when start byte is not found withing a threshold duration

    TAPError.TIMEOUT_LENGTH: used when sufficient bytes are not received on the serial port \
            within a threshold duration

    TAPError.STOP_BYTE_MISMATCH: used when stop byte in incoming stream is not 0x55

    TAPError.TIMEOUT_PACKET_MODE: used to raise exception if there is any issue in incomming 
    packet parsing in packet mode.

    """

    TIMEOUT_START_BYTE = 1
    TIMEOUT_LENGTH = 2
    STOP_BYTE_MISMATCH = 3
    TIMEOUT_PACKET_MODE = 4
    PACKET_MODE_DATA_CORRUPT = 5
    PORT_ID_MISMATCH = 10

    def __init__(self, error_code):
        self.error_code = error_code

    def __str__(self):
        if self.error_code == self.TIMEOUT_START_BYTE:
            output = "TIMEOUT_START_BYTE"
        elif self.error_code == self.TIMEOUT_LENGTH:
            output = "TIMEOUT_LENGTH"
        elif self.error_code == self.STOP_BYTE_MISMATCH:
            output = "STOP_BYTE_MISMATCH"
        elif self.error_code == self.TIMEOUT_PACKET_MODE:
            output = "TIMEOUT_PACKET_MODE"
        elif self.error_code == self.PACKET_MODE_DATA_CORRUPT:
            output = "PACKET_MODE_DATA_CORRUPT"
        elif self.error_code == self.PORT_ID_MISMATCH:
            output = "PORT_ID_MISMATCH ( use: node-shell -id device Port Id )"
        
        return output


class TAPPacket(object):
    """
    :param src_addr: address of source (sender)
    :type src_addr: Address

    :param dest_addr: address of destination (receiver)
    :type dest_addr: Address

    :param src_port: port number of sender
    :type src_port: int

    :param dest_port: port number of receiver
    :type dest_port: int

    :param data_len: length of self.data
    :type data_len: int

    :param data: content
    :type data_len: str
    """

    def __init__(self):
        """Initializes contents of the packet"""
        self.src_addr = Address("0.0.0.0")
        self.src_port = 0
        self.dest_addr = Address("0.0.0.0")
        self.dest_port = 0
        self.data_len = 0
        self.data = ''
        self.pStatus = False

    def __str__(self):
        """Prints out the contents of this packet"""
        assert(isinstance(self.src_addr, Address))
        assert(isinstance(self.dest_addr, Address))
        output = ""
        output += "Source address: " + str(self.src_addr) + "\n"
        output += "Dest address: " + str(self.dest_addr) + "\n"
        output += "Source port: " + str(self.src_port) + "\n"
        output += "Dest port: " + str(self.dest_port) + "\n"
        output += "Data Length: " + str(self.data_len) + "\n"
        output += "Data: " + str(self.data) + "\n"
        return output

    def __eq__(self, other):
        """Implements == for TAP packets"""
        assert isinstance(other, self.__class__)
        equals = True
        equals = equals and (self.src_addr == other.src_addr)
        equals = equals and (self.src_port == other.src_port)
        equals = equals and (self.dest_addr == other.dest_addr)
        equals = equals and (self.dest_port == other.dest_port)
        equals = equals and (self.data_len == other.data_len)
        equals = equals and (self.data == other.data)
        return equals

    def __ne__(self, other):
        """Implements != for TAP packets"""
        return not self.__eq__(other)

    def fill(self, src_addr, dest_addr, src_port, dest_port, data_len, data):
        """Fills the packet with argument values"""
        assert(isinstance(src_addr, Address))
        assert(isinstance(dest_addr, Address))
        assert(isinstance(data, bytearray))
        self.src_addr = src_addr
        self.dest_addr = dest_addr
        self.src_port = src_port
        self.dest_port = dest_port
        self.data_len = data_len
        self.data = data

    def serialize(self):
        """Converts the packet into a buf which can be sent over the serial port

        :returns: serialized buf
        :rtype: str
        """
        src_addr_num = self.src_addr.dump_to_integer()
        dest_addr_num = self.dest_addr.dump_to_integer()
        buf = bytearray()
        buf.append(0xAA)
        buf.append((src_addr_num & 0xFF000000) >> 24)
        buf.append((src_addr_num & 0x00FF0000) >> 16)
        buf.append((src_addr_num & 0x0000FF00) >> 8)
        buf.append((src_addr_num & 0x000000FF) >> 0)
        buf.append((dest_addr_num & 0xFF000000) >> 24)
        buf.append((dest_addr_num & 0x00FF0000) >> 16)
        buf.append((dest_addr_num & 0x0000FF00) >> 8)
        buf.append((dest_addr_num & 0x000000FF) >> 0)
        buf.append(self.src_port)
        buf.append(self.dest_port)
        buf.append(self.data_len)
        #The 2 byte CRC forms the stop byte
        for i in range(0, self.data_len):
            buf.append(self.data[i])
        
        #CRC is calculated for even bytes to be in sync with the embedded part
        #If data bytes is odd.'0' is appended and then CRC is calculated
        if (len(buf[1:]) % 2) != 0:
            temp_buf = deepcopy(buf)
            temp_buf.append(0)
            self.crc = crc16(bytes(temp_buf[1:]))
        else:
            self.crc = crc16(bytes(buf[1:]))

        buf.extend(serialize.serialize_uint16(self.crc))
        if self.pStatus == True:
            print ("Tx:[", end=" ")
            for i in range (0,len(buf)):
                print (hex(buf[i]), end=" "),
            print ("]")    
        return buf

    def deserialize(self, buf):
        """
        Populates the TAP packet from buf argument

        :param buf: The string which represents the TAP payload \
                (ie, start byte and stop byte are not included in buf)
        :type buf: bytearray
        """
        assert(isinstance(buf, bytearray))
        # Fill network packet object and return
        src_addr_num = (buf[0] << 24) + (buf[1] << 16) + (buf[2] << 8) + buf[3]
        dest_addr_num = (buf[4] << 24) + (buf[5] << 16) + \
            (buf[6] << 8) + buf[7]
        self.src_addr = Address(address_integer=src_addr_num)
        self.dest_addr = Address(address_integer=dest_addr_num)
        self.src_port = buf[8]
        self.dest_port = buf[9]
        self.data_len = buf[10]
        self.data = buf[11:]
        
    def print_state(self, data):
        self.pStatus = data;



class TAPHandler(object):
    """Implementation for sending and receving TAP packets over a serial port"""

    def __init__(self, ser, timeout, mode="rc_packet",
                 network_log_path=os.path.expanduser("~/")):
        """
        :param ser: serial port object pointing to gateway
        :type ser: serial.Serial

        :param timeout: the timeout duration for sending a packet
        :type timeout: int
        """
        self.ser = ser
        self.timeout = timeout
        self.mode = mode
        self.nLog = networkDataLogger(network_log_path)
        self.pStatus=False


    def get_packet(self):
        """
        Parses the incoming byte stream from the serial port and returns a TAP packet is parsing is succesful


        :raises: TAPError in case parsing of incoming bytes fails
        :returns: a parsed TAP packet
        :rtype: TAPPacket
        """

        buf = bytearray()
        self.ser.flushInput()
        valuea = False
        if self.mode == "rc_packet":
            rply = self.get_rc_packet()
            #check for data length
            if len(rply) < 17:
                raise TAPError.PACKET_MODE_DATA_CORRUPT

            if rply[16] == 0x02:  #if event packet
                ack_rply = rply
                rfp = rfPacket()
                self.nLog.put_network_log(rfp.parse_event_packet(ack_rply)) #print log
                ser_data_rply = self.get_rc_packet()
            else:
                ser_data_rply = rply

            buf = ser_data_rply[18:]

        else:
            start_byte_found = False

            while not start_byte_found:
                byte_read = self.ser.read()
                if len(byte_read) > 0:
                    if byte_read[0] == 0xAA:
                        start_byte_found = True
                    elif byte_read == b'\x7e':
                        next_byte = self.ser.read()
                        if next_byte == b'\xff':
                            start_byte_found = True
                            valuea = True
                    else:
                        print(binascii.hexlify(byte_read).decode('ascii'), end=' ')
                else:
                    raise TAPError(TAPError.TIMEOUT_START_BYTE)
        if(valuea == True):
            buf = bytearray([0xff,0xff,0xff,0xff,0x1,0x82,0x35,0xc9,0x13,0x4,0x2,0xfc,0x3,0x1b,0xd2])
        else:
            buf = buf[1:]
        parsing_complete = False
        crc_h=0
        crc_l=0
        while parsing_complete == False:
            
            # If we're at the data length field or beyond, start looking for the end
            if len(buf) >= 11:
                # Calculate where the stop byte should be based on data len
                stop_byte_pos = 11 + buf[10]
                # If this is where the stop byte should be, check it
                if len(buf) == (stop_byte_pos + 2):
                    crc_h=buf[stop_byte_pos]
                    crc_l=buf[stop_byte_pos+1]
                    crc_in_packet = serialize.deserialize_uint16(buf[stop_byte_pos:stop_byte_pos + 2])
                    
                    #Always calculate CRC for even data bytes,if not even append zero and calculate
                    if (len(buf[0:stop_byte_pos]) % 2) != 0:
                        buf[stop_byte_pos] = 0x00
                        #Calculate the CRC of data in packet
                        crc_computed = crc16(bytes(buf[0:stop_byte_pos+1]))
                    else:
                        #Calculate the CRC of data in packet
                        crc_computed = crc16(bytes(buf[0:stop_byte_pos]))
                    
                    #Accept if calculated CRC matches the received CRC                    
                    if (crc_in_packet == crc_computed):
                        parsing_complete = True
                    # If this was supposed to be the stop byte but wasn't, return an error
                    else:
                        print ("Rx:[0xaa", end=" ")
                        for i in range(0,len(buf)):
                            print (hex(buf[i]), end=" "),
                        print ("]")

                        print ("recieved_crc", hex(crc_in_packet), end=" ")
                        print ("calculated_crc", hex(crc_computed))
                        raise TAPError(TAPError.STOP_BYTE_MISMATCH)

            if parsing_complete == False:
                byte_read = self.ser.read()
                if len(byte_read) > 0:
                    buf.extend(byte_read)
                else:
                    raise TAPError(TAPError.TIMEOUT_LENGTH)
                
        if self.pStatus == True:
            print ("Rx:[ 0xaa", end=" "),
            for i in range(0,len(buf)):
                print (hex(buf[i]), end=" "),
            print ("]")
        my_tap_packet = TAPPacket()
        my_tap_packet.deserialize(buf[0:stop_byte_pos])  
        return my_tap_packet

    def get_rc_packet(self):
        """
        Waits and retrieves the radio craft packet from the node.
        This module is currently a helper function for "get_packet"

        :raises : TAP error in case parsing is failed
        :returns : Packet mode packet retrieved from the node
        :rtype : bytearray
        """
        start_time = time.time()
        rc_header_recieved = False
        packet_complete = False
        if(self.mode == "rc_packet"):
            rc_buf = bytearray()
            while not rc_header_recieved:
                if ((time.time() - start_time) > self.timeout):
                    raise TAPError(TAPError.TIMEOUT_PACKET_MODE)
                else:
                    rc_buf.extend(self.ser.read())
                    if len(rc_buf) > 1:
                        rc_header_recieved = True
                        #byte 0 gives the length of the packet(check tiny mesh data sheet)
                        rc_data_length = rc_buf[0]
                        while not packet_complete:
                            if ((time.time() - start_time) > self.timeout):
                                raise TAPError(TAPError.TIMEOUT_PACKET_MODE)
                            else:
                                rc_buf.extend(self.ser.read())
                                if len(rc_buf) == rc_data_length:
                                    packet_complete = True

        return rc_buf




    def get_packet_from(self, src_addr, src_port, dest_addr=Address("1.78.71.201")):
        """
        Drops all packets which are don't have the mentioned source address & source port

        :param src_addr: The expected source address in the incoming TAP packet
        :type src_addr: Address

        :param src_port: The expected source port in the incoming TAP packet
        :type src_port: int

        :returns: TAP packet which matches the address & port as mentioned
        :rtype: TAPPacket

        :raises TAPError:
        """
        src_port = int(src_port)
        while True:
            tap_packet = self.get_packet()

            if (tap_packet.src_addr == src_addr or src_addr.dump_to_integer()%256 == 255) and (tap_packet.src_port == src_port)\
                    and (tap_packet.dest_addr == dest_addr):
                return tap_packet
            elif (tap_packet.src_port != src_port):
                print ("RECIEVE PORT ID : ", tap_packet.src_port)
                return tap_packet
                # raise TAPError(TAPError.PORT_ID_MISMATCH)

    def send_packet(self, src_addr, dest_addr, src_port, dest_port, data):
        """
        Creates and sends a TAP packet over the serial port. The data_len field 
        is set as len(data).It adds the needed header and tailer if the module
        is operating in packet mode.

        :param src_addr: address of this machine
        :type src_addr: Address

        :param dest_addr: address of node to which the packet is being sent
        :type dest_addr: Address

        :param src_port: source port number
        :type src_port: int

        :param dest_port: destination port number
        :type dest_port: int

        :param data: The payload
        :type data: str
        """
        self.ser.flushOutput()
        assert(isinstance(data, bytearray))
        p = TAPPacket()
        p.print_state(self.pStatus)
        p.fill(src_addr, dest_addr, src_port, dest_port, len(data), data)
        #self.ser.write(p.serialize())
        if self.mode == "rc_packet":
            rfp = rfPacket()
            tap_bytes = p.serialize()
            rfp_bytes = rfp.frame_rf_data_packet(dest_addr, tap_bytes)
            self.ser.write(rfp_bytes)
        else:
            self.ser.write(p.serialize())

    def send_raw_bytes(self, data, receive_len):
        """
        This API allows to directly send bytes to the serial port.This is
        kind of bypass over TAP.For instance this API is used by the 
        packet_mode_commands module to send data as it does not depend on
        TAP packets for communication.
        :param data: The data that needds to transmitted over the UART channel
        :type data: bytearray

        :return :None
        """
        data_to_send = ''
        assert(isinstance(data, bytearray))
        self.ser.write(data)
        time.sleep(1)
        start_time = time.time()
        while (time.time() - start_time) < 5:
            if self.ser.inWaiting() >= receive_len:
                data_receive = self.ser.read(receive_len)
                data_to_send = binascii.hexlify(data_receive)
                break
        return data_to_send
        
    def print_status(self, data):
        self.pStatus = data;
        if data == True:
            return "Tx and Rx bytes are enable to print !!!"
        else:
            return "Tx and Rx bytes are disable to print !!!"

