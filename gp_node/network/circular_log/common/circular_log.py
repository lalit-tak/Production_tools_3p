import copy
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io import FlashIOMaster, FlashIOError
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json
import crc16


class CircularLog:

    """
    :param int SECTOR_SIZE: The size of one sector in the external flash memory (4kB)
    :param int HEADER_SIZE: Size of the header meta data
    :param dict header: The header contains the following keys:

    - *magic_number (int)*: Ideally, if the header has been read from a node, then its value shoule be 0xBAE1DEED
    - *protocol_version (int)*: Ideally, this should be 1
    - *data_block_addr (int)*: Ideally, this should be address from where the Entries of the circular log are saved
    - *sector_entry_count (list(int))*: Indicates the number of entries in each sector occupied by circular log data structure
    - *read_sector (int)*: The sector number indicating the tail of the circular log 
    - *write_sector (int)*: The sector number indicating the head of the circular log
    """
    EXPECTED_MAGIC_NUMBER = 0xBAE1DEED
    EXPECTED_PROTOCOL_VERSION = 1
    SECTOR_SIZE = 0x1000
    HEADER_SIZE = 18

    def __init__(self, network_api, NUMBER_OF_SECTORS, ENTRY_SIZE):
        """
        :param NetworkAPI network_api: Used to execute flash io commands on the node
        :param int NUMBER_OF_SECTORS: Number of sectors of external flash occupied by\
             this circular log data structure 
        :param int ENTRY_SIZE: the size in bytes of the each entry of the circular log
        """
        self.ENTRY_SIZE = ENTRY_SIZE
        self.NUMBER_OF_SECTORS = NUMBER_OF_SECTORS
        self.NUMBER_OF_ENTRIES_PER_SECTOR = int(self.SECTOR_SIZE / self.ENTRY_SIZE)
        self.flash_io = network_api.my_flash_io_master_3p
        self.network_api = network_api
        self.header = {}

    def update_header(self):
        """
        Uses FlashIO to get the bytes corresponding to the header of the circular log
        and deserializes the bytestream to populate self.header dictionary after verifying
        the CRC data integrity of the header bytestream
        """
        header = {}
        header_byte_stream = self.flash_io.fetch(Address("255.255.255.255"), self.START_ADDRESS, self.HEADER_SIZE)
        header["magic_number"] = serialize.deserialize_uint32(header_byte_stream[0:4], "reverse")
        header["protocol_version"] = serialize.deserialize_uint16(header_byte_stream[4:6], "reverse")
        header["data_block_addr"] = serialize.deserialize_uint32(header_byte_stream[6:10], "reverse")
        header["tail_sector_entry_count"] = serialize.deserialize_uint16(header_byte_stream[10:12], "reverse")
        header["read_sector"] = serialize.deserialize_uint16(header_byte_stream[12:14], "reverse")
        header["write_sector"] = serialize.deserialize_uint16(header_byte_stream[14:16], "reverse")
        header["crc"] = serialize.deserialize_uint16(header_byte_stream[16:18], "reverse")
        computed_crc = crc16.crc16xmodem(str(header_byte_stream[0:self.HEADER_SIZE-2]))
        if computed_crc != header["crc"]:
            print ("CRC mismatch in header. computed: {}, actual: {}".format(computed_crc, header["crc"]))
            exit()
        
        #Debugg
        # print "magic number " + str(header["magic_number"])
        # print "computed_crc" + str(computed_crc)
        # print "header_crc" + str(header["crc"]) 
        # print "data block address: " + str(header["data_block_addr"])
        # print "tail sector entry count: " + str(header["tail_sector_entry_count"])
        # print "read sector: " + str(header["read_sector"])
        # print "write sector: " + str(header["write_sector"])
        self.header = header

    def get_start_address(self, index):
        """
        :param int index: The index of the entry whose external_flash_address is being queried
        :returns: The start address in external flash memory, of the queried index, None otherwise
        :rtype: int
        """
        sector_number = 0
        temp_sum = 0
        entry_available = False
        read_sector = self.header["read_sector"]
        write_sector = self.header["write_sector"]

        if self.header["read_sector"] > self.header["write_sector"]:
            limit = read_sector + self.NUMBER_OF_SECTORS
        else:
            limit = write_sector + 1

        for i in range(read_sector, limit):
            prev_sum = temp_sum
            if (i % self.NUMBER_OF_SECTORS) == self.header["write_sector"]:          
                temp_sum += self.header["tail_sector_entry_count"]            
            else:
                temp_sum += self.NUMBER_OF_ENTRIES_PER_SECTOR
            
            
            if index < temp_sum:
                entry_available = True
                sector_number = i % self.NUMBER_OF_SECTORS
                index_within_sector = index - prev_sum
                break

        if entry_available:
            start_location = sector_number*self.SECTOR_SIZE + index_within_sector*self.ENTRY_SIZE
            print (sector_number, index_within_sector)
            return start_location + self.header["data_block_addr"]
        else:
            return None

    def get_total_entries(self):
        """
        returns:Returns the total number of entries in the circular log.
        It caluclates this by using the data from the header.
        """
        if(self.header["read_sector"] > self.header["write_sector"]):
            return ((self.NUMBER_OF_SECTORS - 1) * self.NUMBER_OF_ENTRIES_PER_SECTOR) + self.header["tail_sector_entry_count"]
        elif self.header["read_sector"] <= self.header["write_sector"]:
            return (self.header["write_sector"] * self.NUMBER_OF_ENTRIES_PER_SECTOR) + self.header["tail_sector_entry_count"]

    def get_data_from_node(self, index):
        """
        :param int index: The index of the entry whose bytestream is being queried
        :returns: The bytearray corresponding to the entry indexed by the index argument
        :rtype: bytearray
        """
        start_address = self.get_start_address(index)
        if start_address is None:
            return None
        data = self.flash_io.fetch(Address("0.0.0.255"), start_address, self.ENTRY_SIZE)
        return data

    def dump(self, filepath):
        """
        Queries the entire circular log data structure and writes it to a binary file.
        This essentially creates a binary dump image of a certain address range of the external flash chip

        :param str filepath: The path of the file where the binary data from external flash chip is to be dump_header_to_file
        """
        start_address = self.header["data_block_addr"]
        length = self.NUMBER_OF_SECTORS*self.SECTOR_SIZE
        hexfile_payload = self.flash_io.fetch(Address("0.0.0.255"), start_address, length, to_print=True)
        binary_file = open(filepath, "wb")
        binary_file.write(hexfile_payload)
        binary_file.close()

    def dump_header_to_file(self, filepath):
        """
        Dumps the self.header dictionary into the file given by filepath in JSON format

        :param str filepath: path of file where self.header is to be dumped
        """
        f = open(filepath, "w")
        f.write(json.dumps(self.header, indent=2))
        f.close()

    def load_header_from_file(self, filepath):
        """
        Reads a JSON file representing the header, and populates self.header with it
        
        :param str filepath: The file path of the JSON file representing the header of the\
            circular log data structure
        """
        f = open(filepath, "r")
        self.header = json.loads(f.read())
        f.close()


