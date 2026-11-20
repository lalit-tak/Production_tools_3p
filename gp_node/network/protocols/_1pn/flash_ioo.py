"""
Implements master side of FlashIO protocol
"""

from gp_node.utils import Address
import time
from gp_node.network.protocols.common.protocol import ProtocolMaster, ProtocolError
from gp_node.network.protocols.common.tap import TAPError
import gp_node.utils.serialize as serialize
import crc16
import os

FLASH_IO_MAX_PAYLOAD_SIZE = 42


class FlashIOErrorNO(ProtocolError):
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
        payload.extend(serialize.serialize_uint32(self.start_address))
        payload.append(self.length)
        # Meta data in the payload is address (4 bytes), length (1 byte),
        # CRC (2 bytes) which is a total of 7 bytes.
        # Hence, the total size of the actual data (which is to be written in the external flash)
        # cannot exceed FLASH_IO_MAX_PAYLOAD_SIZE-7
        if len(self.data) > FLASH_IO_MAX_PAYLOAD_SIZE - 7:
            raise ValueError(
                "length of data cannot exceed {}".format(
                    FLASH_IO_MAX_PAYLOAD_SIZE - 7))
        payload.extend(self.data)

        # The size of a data chunk packet is necessarily FLASH_IO_MAX_PAYLOAD_SIZE.
        # Hence, if the actual data to be written is less than FLASH_IO_MAX_PAYLOAD_SIZE-7,
        # then the remaining bytes in the actual data are populated with 0x00.
        # The '-2' in the statement below indicates that don't fill the last two bytes
        # the last 2 bytes contains CRC
        while len(payload) < FLASH_IO_MAX_PAYLOAD_SIZE - 2:
            payload.append(0)
        self.crc = crc16.crc16xmodem(str(payload))
        payload.extend(serialize.serialize_uint16(self.crc))
        return payload

    def deserialize(self, payload):
        if len(payload) != FLASH_IO_MAX_PAYLOAD_SIZE:
            raise ValueError(
                "length of payload is not {}".format(FLASH_IO_MAX_PAYLOAD_SIZE))
        self.start_address = serialize.deserialize_uint32(payload[0:4])
        self.length = payload[4]
        if self.length <= FLASH_IO_MAX_PAYLOAD_SIZE - 7:
            self.data = payload[5:5 + self.length]
        self.crc = serialize.deserialize_uint16(
            payload[FLASH_IO_MAX_PAYLOAD_SIZE - 2:FLASH_IO_MAX_PAYLOAD_SIZE])


class FlashIOMasterNO(ProtocolMaster):

    """
    """

    SLAVE_PORT = 6
    MASTER_PORT = 6

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
        payload = bytearray("read ")
        payload.extend(serialize.serialize_uint32(start_address))
        payload.append(length)
        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.SLAVE_PORT,
            self.MASTER_PORT,
            payload)
        try:
            packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise FlashIOErrorNO(FlashIOErrorNO.TAP_ERROR, e)

        if packet.data == "invalid start address":
            raise FlashIOErrorNO(
                FlashIOErrorNO.READ_INVALID_START_ADDRESS,
                tap_packet=packet)
        elif packet.data == "invalid length":
            raise FlashIOErrorNO(
                FlashIOErrorNO.READ_INVALID_LENGTH,
                tap_packet=packet)
        elif packet.data_len != FLASH_IO_MAX_PAYLOAD_SIZE:
            raise FlashIOErrorNO(
                FlashIOErrorNO.READ_INVALID_PACKET_SIZE,
                tap_packet=packet)

        if len(packet.data) != FLASH_IO_MAX_PAYLOAD_SIZE:
            raise FlashIOErrorNO(
                FlashIOErrorNO.READ_INVALID_PACKET_SIZE,
                tap_packet=packet)

        data_chunk_packet = DataChunkPacket()
        data_chunk_packet.deserialize(packet.data)
        if data_chunk_packet.length != length:
            raise FlashIOErrorNO(
                FlashIOErrorNO.READ_LENGTH_MISMATCH,
                tap_packet=packet)
        if data_chunk_packet.crc != crc16.crc16xmodem(
                str(packet.data[0:FLASH_IO_MAX_PAYLOAD_SIZE - 2])):
            raise FlashIOErrorNO(
                FlashIOErrorNO.READ_CRC_MISMATCH,
                tap_packet=packet)
        if data_chunk_packet.start_address != start_address:
            raise FlashIOErrorNO(
                FlashIOErrorNO.READ_START_ADDRESS_MISMATCH,
                tap_packet=packet)
        return data_chunk_packet.data

    def write(self, slave_address, start_address, data):
        """
        Sends data to be written in the flash memory of the Node.
        This method sends just one FlashIO packet. If data argument is large,
        then use burn() method instead

        :param int start_address: The starting address in flash where data is to be written

        :param bytearray data: The data to be written in flash

        :returns: "ok" if data was successfully written

        :raises: FlashIOError with appropriate error codes
        """
        payload = DataChunkPacket(start_address, data).serialize()
        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.SLAVE_PORT,
            self.MASTER_PORT,
            payload)
        try:
            packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise FlashIOError(FlashIOError.TAP_ERROR, e)
        if str(packet.data) == "invalid packet size":
            raise FlashIOError(
                FlashIOError.WRITE_INVALID_PACKET_SIZE,
                tap_packet=packet)
        elif str(packet.data) == "invalid start address":
            raise FlashIOError(
                FlashIOError.WRITE_INVALID_START_ADDRESS,
                tap_packet=packet)
        elif str(packet.data) == "invalid length":
            raise FlashIOError(
                FlashIOError.WRITE_INVALID_LENGTH,
                tap_packet=packet)
        elif str(packet.data) == "crc mismatch":
            raise FlashIOError(
                FlashIOError.WRITE_CRC_MISMATCH,
                tap_packet=packet)
        elif str(packet.data) == "ok":
            return "ok"
        else:
            raise FlashIOErrorNO(
                FlashIOErrorNO.WRITE_UNKNOWN_ERROR,
                tap_packet=packet)

    def erase(self, slave_address, block_id):
        """
        Sends command to erase a block of flash memory on the Node board

        :param int block_id: The id of the block which needs to b erased.

        :returns: "ok" if data was successfully erased

        :raises: FlashIOError with appropriate error codes
        """
        payload = bytearray("erase ")
        payload.extend(serialize.serialize_uint32(block_id))
        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.SLAVE_PORT,
            self.MASTER_PORT,
            payload)
        try:
            packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise FlashIOErrorNO(FlashIOErrorNO.TAP_ERROR, e)
        if str(packet.data) == "invalid block id":
            raise FlashIOErrorNO(
                FlashIOErrorNO.ERASE_INVALID_BLOCK_ID,
                tap_packet=packet)
        elif str(packet.data) == "ok":
            return "ok"
        else:
            raise FlashIOErrorNO(
                FlashIOErrorNO.ERASE_UNKNOWN_ERROR,
                tap_packet=packet)

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
        while length - len(hexfile_payload) >= FLASH_IO_MAX_PAYLOAD_SIZE - 7:
            retry = True
            while retry:
                if to_print:
                    print (str(len(hexfile_payload * 100) / length) + " %")
                try:
                    data = self.read(
                        slave_address,
                        start_address=start_address +
                        len(hexfile_payload),
                        length=FLASH_IO_MAX_PAYLOAD_SIZE -
                        7)
                    hexfile_payload.extend(data)
                except FlashIOErrorNO as err:
                    # print err
                    retry = True
                else:
                    retry = False
        retry = True
        while retry:
            if to_print:
                print (str(len(hexfile_payload * 100) / length) + " %")
            try:
                data = self.read(
                    slave_address,
                    start_address=start_address +
                    len(hexfile_payload),
                    length=length -
                    len(hexfile_payload))
                hexfile_payload.extend(data)
            except FlashIOErrorNO as err:
                # print err
                retry = True
            else:
                retry = False
        return hexfile_payload

    def fetch_ls(
            self,
            slave_address,
            start_address,
            length,
            to_print=False,
            l_s=False):
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
        count = 0
        hexfile_payload = bytearray()
        num_bytes_recv = 0
        while length - len(hexfile_payload) >= FLASH_IO_MAX_PAYLOAD_SIZE - 7:
            retry = True
            print ("count", count)
            if count > 5:
                break
            while retry:
                if to_print:
                    print (str(len(hexfile_payload * 100) / length) + " %")
                try:
                    count += 1
                    data = self.read(
                        slave_address,
                        start_address=start_address +
                        len(hexfile_payload),
                        length=FLASH_IO_MAX_PAYLOAD_SIZE -
                        7)
                    hexfile_payload.extend(data)
                    count = 0
                except FlashIOErrorNO as err:
                    # print err
                    retry = True
                    if (l_s is True) and count > 5:
                        break
                else:
                    retry = False
        retry = True
        while retry:
            if to_print:
                print (str(len(hexfile_payload * 100) / length) + " %")
            try:
                count += 1
                data = self.read(
                    slave_address,
                    start_address=start_address +
                    len(hexfile_payload),
                    length=length -
                    len(hexfile_payload))
                hexfile_payload.extend(data)
                count = 0
            except FlashIOErrorNO as err:
                # print err
                retry = True
                if (l_s is True) and count > 5:
                    break
            else:
                retry = False
        return hexfile_payload

    def burn(
            self,
            slave_address,
            start_address,
            hexfile_payload,
            to_print=False):
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
        num_bytes_sent = 0
        while len(hexfile_payload) - \
                num_bytes_sent >= FLASH_IO_MAX_PAYLOAD_SIZE - 7:
            data = hexfile_payload[num_bytes_sent:num_bytes_sent +
                                   FLASH_IO_MAX_PAYLOAD_SIZE - 7]
            retry = True
            while retry:
                if to_print:
                    os.system("clear")
                    print ("Loading" + str((100 * num_bytes_sent) / len(hexfile_payload)) + " %")
                try:
                    self.write(
                        slave_address,
                        start_address=start_address +
                        num_bytes_sent,
                        data=data)
                except FlashIOErrorNO as err:
                    # print err
                    retry = True
                else:
                    retry = False
            num_bytes_sent += FLASH_IO_MAX_PAYLOAD_SIZE - 7
        data = hexfile_payload[num_bytes_sent:]
        while len(data) != FLASH_IO_MAX_PAYLOAD_SIZE - 7:
            data.append(0)
        retry = True
        while retry:
            if to_print:
                os.system("clear")
                print ("Loading" + str((100 * num_bytes_sent) / len(hexfile_payload)) + " %")
            try:
                self.write(
                    slave_address,
                    start_address=start_address +
                    num_bytes_sent,
                    data=data)
            except FlashIOErrorNO as err:
                # print err
                retry = True
            else:
                retry = False
