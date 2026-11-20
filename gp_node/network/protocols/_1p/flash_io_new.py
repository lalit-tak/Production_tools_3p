"""
Implements master side of FlashIO protocol
"""

from gp_node.utils import Address
import time
from gp_node.network.protocols.common.protocol import ProtocolMaster, ProtocolError
from gp_node.network.protocols.common.tap import TAPPacket, TAPHandler, TAPError
import gp_node.utils.serialize as serialize
import crc16
import os

FLASH_IO_MAX_PAYLOAD_SIZE = 64

class FlashIOErrorNew(ProtocolError):
    """
    READ_CRC_MISMATCH: raised when the computed CRC returned in the data chunk packet\
            does not match the crc field in the data chunk packet
   
    READ_INVALID_LENGTH: raised when the length field in the read request\
            exceeds the limit
    
    READ_INVALID_START_ADDRESS: raised when the start_address in the read request\
            exceeds the limit
    
    READ_INVALID_PACKET_SIZE: raised when the size of the returned data chunk packet\
            is not MAX_PAYLOAD_SIZE nor is the data 'invalid length' or 'invalid start address'
    
    READ_START_ADDRESS_MISMATCH: raised when the start_address in the returned packet\
            does not match the start_address in the read request
    
    WRITE_INVALID_PACKET_SIZE: raised when the packet which was sent to Node was not\
            MAX_PAYLOAD_SIZE bytes long
    
    WRITE_INVALID_START_ADDRESS: raised when the start address in the write request\
            exceeds limit
    
    WRITE_INVALID_LENGTH: raised when the length in the write request exceeds limit
    
    WRITE_INVALID_START_ADDRESS: raised when the start_address in the write request\
            exceeds limit
    
    WRITE_CRC_MISMATCH: raised when the computed crc in the write request does not match\
            the crc field in the write request
    
    WRITE_UNKNOWN_ERROR: raised in case of unknown error
    
    ERASE_INVALID_BLOCK_ID: raised when the block id of the erase request is out of range
    
    ERASE_UNKNOWN_ERROR: raised when the response from the node is neither "ok" nor any known\
            errors
    """
    READ_INVALID_LENGTH = 1
    READ_INVALID_START_ADDRESS = 2
    READ_INVALID_PACKET_SIZE = 3
    READ_START_ADDRESS_MISMATCH = 4
    READ_LENGTH_MISMATCH = 5
    READ_CRC_MISMATCH = 6
    WRITE_INVALID_PACKET_SIZE = 7
    WRITE_CRC_MISMATCH = 8
    WRITE_INVALID_LENGTH = 9
    WRITE_INVALID_START_ADDRESS = 10
    WRITE_UNKNOWN_ERROR = 11
    ERASE_INVALID_BLOCK_ID = 12
    ERASE_UNKNOWN_ERROR = 13




class DataChunkPacket:

    def __init__(self, start_address=0, data=None):
        self.start_address = start_address
        if data is None:
            self.data = bytearray()
            self.length = 0
        else:
            self.data = data
            self.length = len(data)
        # self.serialize comutes crc and stores it in self.crc
        self.crc = 0

    def serialize(self):
        payload = bytearray()
        payload.extend(FLASH_IO_WRITE)
        payload.extend(serialize.serialize_uint32(self.start_address))
        payload.append(self.length)
        # Meta data in the payload is address (4 bytes), length (1 byte),
        # CRC (2 bytes) which is a total of 7 bytes.
        # Hence, the total size of the actual data (which is to be written in the external flash)
        # cannot exceed FLASH_IO_MAX_PAYLOAD_SIZE-7
        if len(self.data) > FLASH_IO_MAX_PAYLOAD_SIZE:
            raise ValueError("length of data cannot exceed {}".format(FLASH_IO_MAX_PAYLOAD_SIZE))
        payload.extend(self.data)

        # The size of a data chunk packet is necessarily FLASH_IO_MAX_PAYLOAD_SIZE.
        # Hence, if the actual data to be written is less than FLASH_IO_MAX_PAYLOAD_SIZE-7,
        # then the remaining bytes in the actual data are populated with 0x00.
        # The '-2' in the statement below indicates that don't fill the last two bytes
        # the last 2 bytes contains CRC
        while len(payload) < FLASH_IO_MAX_PAYLOAD_SIZE:
            payload.append(0)

        crc = crc16.crc16xmodem(str(payload[0:]))     
        payload.extend(serialize.serialize_uint16(crc))
        return payload

    def deserialize(self, payload):
        if len(payload) > FLASH_IO_MAX_PAYLOAD_SIZE:
            raise ValueError("length of payload is greater than  {}".format(FLASH_IO_MAX_PAYLOAD_SIZE))

        self.start_address = serialize.deserialize_uint32(payload[0:4])
        self.length = len(payload)
        if self.length <= FLASH_IO_MAX_PAYLOAD_SIZE:
            self.data = payload[4:4+self.length]

class FlashIOMasterNew:

    def __init__(self, PortId, my_address, my_tap_handler):

        self.SLAVE_PORT =  int(PortId)
        self.MASTER_PORT = int(PortId)
        self.my_address = my_address
        self.my_tap_handler = my_tap_handler

    FLASH_IO_READ                = 0x01
    FLASH_IO_WRITE               = 0x02
    FLASH_IO_WRITE_NACK          = 0x03
    FLASH_IO_ERASE_SECTOR        = 0x04
    FLASH_IO_ERASE_BLOCK         = 0x05

    IMAGE_TRANSFER_TAP           = 0XCF08     # 53000 Command Id
    


    def read(self, slave_address, start_address, length):
        """
        Reads the contents of the external flash memory of the node board.
        This method reads just one FlashIO packet. If the length of data to be
        read is large, use fetch() method instead.

        :param int start_addrss: the address of the flash location from where\
            data is to be read

        :param int length: The number of bytes of data to be read

        :returns: The contents of the internal info flash bank
        :rtype: bytearray
        """
        payload = bytearray()
        payload.extend(serialize.serialize_uint16(self.IMAGE_TRANSFER_TAP))
        payload.extend(chr(self.FLASH_IO_READ))
        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(chr(length))
        self.my_tap_handler.send_packet(self.my_address, slave_address,
                                        self.SLAVE_PORT, self.MASTER_PORT, payload)

        try:
            packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise FlashIOErrorNew(FlashIOErrorNew.TAP_ERROR, e)

        #print "recieve packet"
        #print [hex(b) for b in packet.data]    


        # data_chunk_packet = DataChunkPacket()
        # data_chunk_packet.deserialize(packet.data)
        # if data_chunk_packet.length != (length+4):
        #     raise FlashIOErrorNew(FlashIOErrorNew.READ_LENGTH_MISMATCH, tap_packet=packet)
        # if data_chunk_packet.start_address != start_address:
        #     raise FlashIOErrorNew(FlashIOErrorNew.READ_START_ADDRESS_MISMATCH, tap_packet=packet)
        # return data_chunk_packet.data


    def write(self, slave_address, start_address, data):
        """
        Sends data to be written in the flash memory of the Node.
        This method sends just one FlashIO packet. If data argument is large,
        then use burn() method instead

        :param int start_address: The starting address in flash where data is to be written

        :param bytearray data: The data to be written in flash

        :returns: "ok" if data was successfully written

        :raises: FlashIOErrorNew with appropriate error codes
        """
        #payload = DataChunkPacket(start_address, data).serialize()
        payload = bytearray()
        payload.extend(serialize.serialize_uint16(self.IMAGE_TRANSFER_TAP))
        payload.extend(chr(self.FLASH_IO_WRITE))
        payload.extend(serialize.serialize_uint32(start_address))
        length =  len(data)
        payload.extend(chr(length))

        if len(data) > FLASH_IO_MAX_PAYLOAD_SIZE:
            raise ValueError("length of data cannot exceed {}".format(FLASH_IO_MAX_PAYLOAD_SIZE))
        payload.extend(data)

        # The size of a data chunk packet is necessarily FLASH_IO_MAX_PAYLOAD_SIZE.
        # Hence, if the actual data to be written is less than FLASH_IO_MAX_PAYLOAD_SIZE-6,
        # then the remaining bytes in the actual data are populated with 0x00.
        # The '-2' in the statement below indicates that don't fill the last two bytes
        # the last 2 bytes contains CRC
        while len(payload) < FLASH_IO_MAX_PAYLOAD_SIZE:
            payload.append(0)

        crc = crc16.crc16xmodem(str(payload[0:]))     
        payload.extend(serialize.serialize_uint16(crc))

        self.my_tap_handler.send_packet(self.my_address, slave_address,
                                        self.SLAVE_PORT, self.MASTER_PORT, payload)
        try:
            packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise FlashIOErrorNew(FlashIOErrorNew.TAP_ERROR, e)
        if str(packet.data) != "ok":
            raise FlashIOErrorNew(FlashIOErrorNew.WRITE_INVALID_PACKET_SIZE, tap_packet=packet)
        elif str(packet.data) == "ok":
            return "ok"
        else:
           raise FlashIOErrorNew(FlashIOErrorNew.WRITE_UNKNOWN_ERROR, tap_packet=packet)

    def erase(self, slave_address, block_id, sector_erase = False):
        """
        Sends command to erase a block of flash memory on the Node board

        :param int block_id: The id of the block which needs to b erased.

        :param sector_erase: True for Sector wise erasing\
                             False for block wise erase (64Kb)

        :returns: "ok" if data was successfully erased

        :raises: FlashIOErrorNew with appropriate error codes
        """
        payload = bytearray()
        payload.extend(serialize.serialize_uint16(self.IMAGE_TRANSFER_TAP))
        if(sector_erase == True):
            payload.extend(chr(self.FLASH_IO_ERASE_SECTOR))
        else:
            payload.extend(chr(self.FLASH_IO_ERASE_BLOCK))
        payload.extend(serialize.serialize_uint32(block_id))

        self.my_tap_handler.send_packet(self.my_address, slave_address,
                                        self.SLAVE_PORT, self.MASTER_PORT, payload)
        try:
            packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise FlashIOErrorNew(FlashIOErrorNew.TAP_ERROR, e)
        if str(packet.data) != "ok":
            raise FlashIOErrorNew(FlashIOErrorNew.ERASE_INVALID_BLOCK_ID, tap_packet=packet)
        elif str(packet.data) == "ok":
            print ("NVM erased !!!")
            return "ok"
        else:
            raise FlashIOErrorNew(FlashIOErrorNew.ERASE_UNKNOWN_ERROR, tap_packet=packet)


    def fetch(self, slave_address, start_address, length, to_print=False):
        """
        A wrapper around read() command. The fetch() command executes several
        read() commands and appends the replies of all the read() commands
        to return a large chunk of data as asked by the length argument

        :param int start_address: The address in external flash memory from where\
            data is to be read

        :param int length: The number of bytes of data to be read

        :param bool to_print: If to_print is True, then the percentage completion\
            is printed on the screen. Default is False

        :returns: The bytearray representing the fetched data
        """
        hexfile_payload = bytearray()
        num_bytes_recv = 0
        retry_cnt = 0
        while length - len(hexfile_payload) >= FLASH_IO_MAX_PAYLOAD_SIZE-4:
            retry = True
            while retry:
                if to_print:
                    print (str(len(hexfile_payload*100)/length) + " %")
                try:
                    print ("start addr", start_address+len(hexfile_payload))
                    data = self.read(slave_address, start_address=start_address+len(hexfile_payload), length=FLASH_IO_MAX_PAYLOAD_SIZE-4)
                    hexfile_payload.extend(data)
                except FlashIOErrorNew as err:
                    retry_cnt = retry_cnt + 1
                    #print err
                    retry = True
                else:
                    retry = False
        retry = True
        while retry:
            if to_print:
                print (str(len(hexfile_payload*100)/length) + " %")
            try:
                print ("start addr", start_address+len(hexfile_payload))
                data = self.read(slave_address, start_address=start_address+len(hexfile_payload), length=length-len(hexfile_payload))
                hexfile_payload.extend(data)
            except FlashIOErrorNew as err:
                retry_cnt = retry_cnt+1
                #print err
                retry = True
            else:
                retry = False
        print ("Retry Count:", retry_cnt)
        return hexfile_payload

    def burn(self, slave_address, start_address, hexfile_payload, to_print=False):
        """
        A wrapper around the write() method. The burn() method splits the hexfile_payload
        and calls write() method for each of the smaller chunks.

        :param int start_address: The address in external flash memory where the\
            data is to be written

        :param bytearray hexfile_payload: The data which is to be written in external\
            flash memory

        :param bool to_print: If to_print is True, then the percentage completion is\
            printed on the screen. Default is False
        """
        packet_retry_cnt = 0
        num_bytes_sent = 0
        payload_len = len(hexfile_payload)
        remaining_len = 0
        retry_counter = 0
        # no_of_pkt = 0
        print ("Len of file : " + str(payload_len) + " bytes")
        print ("Number of packets to be sent : " + str(1 + (payload_len-1)/FLASH_IO_MAX_PAYLOAD_SIZE))
        print ("Loading Image .....")
        while (payload_len - num_bytes_sent) > 0:
            if( (payload_len - num_bytes_sent) >= FLASH_IO_MAX_PAYLOAD_SIZE ):
                data = hexfile_payload[num_bytes_sent:num_bytes_sent+FLASH_IO_MAX_PAYLOAD_SIZE]
                remaining_len = FLASH_IO_MAX_PAYLOAD_SIZE
            else:
                data = hexfile_payload[num_bytes_sent:]
                remaining_len = len(data)
                while len(data)!=FLASH_IO_MAX_PAYLOAD_SIZE:
                    data.append(0)    
            # no_of_pkt = no_of_pkt + 1
            retry = True
            while retry:
                if to_print:
                    if (os.name == 'nt'):
                        #os.system('cls')
                        pass
                    else:
                        #os.system('clear')
                        pass
                try:

                    # print no_of_pkt
                    # print [hex(b) for b in data]
                    self.write(slave_address, start_address=start_address+num_bytes_sent, data=data)
                    # self.read(slave_address, start_address=start_address+num_bytes_sent, length=len(data))
                    # print "@0x44000"
                    # self.read(slave_address, 0x44000, 96)
                    per = ((num_bytes_sent+remaining_len)*100.0)/payload_len
                    print ('\rLoading [%.2f%%]'%per),
                except FlashIOErrorNew as err:
                    #print err
                    packet_retry_cnt = packet_retry_cnt+1
                    retry = True
                    retry_counter = retry_counter + 1
                    if(retry_counter > 200):
                        retry_counter = 0
                        retry = False
                        print ("\nNumber of packet transfered : " + str(1 + (num_bytes_sent-1)/FLASH_IO_MAX_PAYLOAD_SIZE))
                        num_bytes_sent = payload_len - remaining_len
                        time.sleep(0.2)

                else:
                    retry = False
                    retry_counter = 0 
            num_bytes_sent += remaining_len


    def write_without_ack(self, slave_address, start_address, data):
        """
        Sends data to be written in the flash memory of the Node.
        This method sends just one FlashIO packet and does not wait for 
        acknowledement. If data argument is large, then use burn() method instead

        :param int start_address: The starting address in flash where data is to be written

        :param bytearray data: The data to be written in flash

        :returns: "ok" if data was successfully written

        :raises: FlashIOErrorNew with appropriate error codes
        """
        #payload = DataChunkPacket(start_address, data).serialize()
        payload = bytearray()
        payload.extend(serialize.serialize_uint16(IMAGE_TRANFER_TAP))
        payload.extend(chr(self.FLASH_IO_WRITE_NACK))
        payload.extend(serialize.serialize_uint32(start_address))
        length =  len(data)
        payload.extend(chr(length))

        if len(data) > FLASH_IO_MAX_PAYLOAD_SIZE:
            raise ValueError("length of data cannot exceed {}".format(FLASH_IO_MAX_PAYLOAD_SIZE))
        payload.extend(data)

        # The size of a data chunk packet is necessarily FLASH_IO_MAX_PAYLOAD_SIZE.
        # Hence, if the actual data to be written is less than FLASH_IO_MAX_PAYLOAD_SIZE-7,
        # then the remaining bytes in the actual data are populated with 0x00.
        # The '-2' in the statement below indicates that don't fill the last two bytes
        # the last 2 bytes contains CRC
        while len(payload) < FLASH_IO_MAX_PAYLOAD_SIZE:
            payload.append(0)

        crc = crc16.crc16xmodem(str(payload[0:]))     
        payload.extend(serialize.serialize_uint16(crc))

        print ("start_address",start_address)

        print ("Length of TAP Packet", len(payload))

        self.my_tap_handler.send_packet(self.my_address, slave_address,
                                        self.SLAVE_PORT, self.MASTER_PORT, payload)


    def burn_nack(self,\
                    slave_address,\
                    start_address,\
                    hexfile_payload,\
                    db,\
                    broadcast_address,\
                    LOG_DEFAULT_METER_ADDRESS,\
                    BROADCAST_STEP_NO,\
                    SCRIPT_LOG_BROADCAST_ADDRESS,\
                    BROADCAST_DELAY_BETWEEN_PACKETS,\
                    to_print = False):
        """
        A wrapper around the write_without_ack() method. The burn_nack() method splits 
        the hexfile_payload  and calls write_without_ack() method for each of the smaller chunks.

        :param int start_address: The address in external flash memory where the\
            data is to be written

        :param bytearray hexfile_payload: The data which is to be written in external\
            flash memory

        :param bool to_print: If to_print is True, then the percentage completion is\
            printed on the screen. Default is False
        """
        num_bytes_sent = 0
        temp_address = start_address
        while len(hexfile_payload) - num_bytes_sent >= FLASH_IO_MAX_PAYLOAD_SIZE:
            data = hexfile_payload[num_bytes_sent:num_bytes_sent+FLASH_IO_MAX_PAYLOAD_SIZE]
            retry = True
           
            if to_print:
                if (os.name == 'nt'):
                    #os.system('cls')
                    pass
                else:
                    #os.system('clear')
                    print ("Loading " + str((100*num_bytes_sent)/len(hexfile_payload)) + " %")
            
            temp_address = start_address+num_bytes_sent
            if temp_address >= broadcast_address:
                
                self.write_without_ack(slave_address,temp_address , data=data) 
                db.delete_script_brodcast_entry()

                db.display(BROADCAST_STEP_NO, str(temp_address) ,status=SCRIPT_LOG_BROADCAST_ADDRESS, script_logging = True, printing = False)
                                
                time.sleep(BROADCAST_DELAY_BETWEEN_PACKETS) 
            
            num_bytes_sent += FLASH_IO_MAX_PAYLOAD_SIZE

        data = hexfile_payload[num_bytes_sent:]
        while len(data)!=FLASH_IO_MAX_PAYLOAD_SIZE:
            data.append(0)
        retry = True

        while retry:
            if to_print:
                if (os.name == 'nt'):
                    pass
                    #os.system('cls')
                else:
                    #os.system('clear')
                    print ("Loading" + str((100*num_bytes_sent)/len(hexfile_payload)) + " %")
            self.write_without_ack(slave_address, start_address=start_address+num_bytes_sent, data=data)
            retry = False
