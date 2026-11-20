import os
import argparse
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io import FlashIOMaster, FlashIOError
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
from gp_node.network.protocols.packets._1p.tamper_log_packet import TamperLog
import json
from gp_node.network.circular_log.common.circular_log import CircularLog
from gp_node.network.network_api import NetworkAPI


class TamperLogReader(CircularLog):

    """
    :param int START_ADDRESS: Indicates the start address of the tamper log data in external flash memory
    """

    START_ADDRESS = 0x104000

    def get_tamper_log_from_node(self, index):
        """
        Gets data from external flash chip using FlashIO protocol and deserializes
        it to get the Bundle packet.

        :param int index: The index of the entry which is being queried
        :returns: Bundle corresponding to the index^th entry
        :rtype: int
        """
        data = self.get_data_from_node(index)
        entry = TamperLog()
        try:
            entry.deserialize(data)
        except BaseException:
            pass
        return entry

    def print_tamper_log_from_node(self):
        """
        Keeps using flash io protocol to query all tamper log entries from node,
        and prints them out on screen
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_tamper_log_from_node(i)
            print (entry)
