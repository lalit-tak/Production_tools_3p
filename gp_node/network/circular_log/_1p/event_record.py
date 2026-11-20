import os
import argparse
import csv
import datetime
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io import FlashIOMaster, FlashIOError
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
from gp_node.network.protocols.packets._1p.event_record_packet import EventRecordPacket
#import gp_concentrator.core.store as store
import json
from gp_node.network.circular_log.common.circular_log import CircularLog
from gp_node.network.network_api import NetworkAPI


class EventRecordReader(CircularLog):

    """
    :param int START_ADDRESS: Indicates the start address of the event record data in external flash memory
     """
    START_ADDRESS = 0x00

    def set_start_address(self, event_category):
        """
        Sets the start address based on event category.

        :param int index: Event category (can be between 1 and 5)
        """
        if event_category == 1:
            self.START_ADDRESS = 0x26000
        elif event_category == 2:
            self.START_ADDRESS = 0x2A000 #0x29000
        elif event_category == 3:
            self.START_ADDRESS = 0x2E000 #0x2C000
        elif event_category == 4:
            self.START_ADDRESS = 0x32000 #0x2F000
        elif event_category == 5:
            self.START_ADDRESS = 0x36000 #0x32000


    def get_event_record_from_node(self, index):
        """
        Gets data from external flash chip using FlashIO protocol and deserializes
        it to get the event record packet.

        :param int index: The index of the entry which is being queried
        :returns: Event record corresponding to the index^th entry
        :rtype: int
        """
        data = self.get_data_from_node(index)
        entry = EventRecordPacket()
        try:
            entry.deserialize(data)
        except:
            pass
        return entry

    def print_event_record_from_node(self):
        """
        Keeps using flash io protocol to query all event record entries from node,
        and prints them out on screen
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_event_record_from_node(i)
            print (entry)
