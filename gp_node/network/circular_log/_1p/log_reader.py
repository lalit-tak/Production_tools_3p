import gp_node.utils.serialize as serialize
from gp_node.network.protocols.packets._1p.log_packet import LogPacket
from gp_node.network.circular_log.common.circular_log import CircularLog


class LogReader(CircularLog):

    """
    :param int START_ADDRESS: Indicates the start address of the load survey data in external flash memory
    """

    START_ADDRESS = 0x21000

    def get_log_from_node(self, index):
        """
        Gets data from external flash chip using FlashIO protocol and deserializes
        it to get the LogPacket.

        :param int index: The index of the entry which is being queried
        :returns: LogPacket corresponding to the index^th entry
        :rtype: int
        """
        data = self.get_data_from_node(index)
        entry = LogPacket()
        try:
            entry.deserialize(data)
        except BaseException:
            pass
        return entry

    def get_log_from_bin(self, index, filepath):
        """
        Reads the binary dumped file and returns the LogPacket entry corresponding
        to the index^th entry

        :param int index: the index of the entry which is being queried
        :param str filepath: the index of the binary dumped file
        """
        bin_file = open(filepath, "rb")
        file_address = self.get_start_address(
            index) - self.header["data_block_addr"]
        bin_file.seek(file_address)
        data = bytearray(bin_file.read(self.ENTRY_SIZE))
        entry = LogPacket()
        try:
            entry.deserialize(data)
        except BaseException:
            pass
        return entry

    def print_log_from_bin(self, filepath):
        """
        Reads the binary dumped image of the external flash chip
        and prints all log entries from the file

        :param str filepath: The file path of the binary dump of external flash
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_log_from_bin(i, filepath)
            print (entry)

    def print_log_from_node(self):
        """
        Keeps using flash io protocol to query all log entries from node,
        and prints them out on screen
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_log_from_node(i)
            print (entry)
