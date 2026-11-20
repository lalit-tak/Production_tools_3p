import os
import argparse
import csv
import datetime
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io import FlashIOMaster, FlashIOError
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
from gp_node.network.protocols.packets._1p.daily_load_profile_packet import DailyLoadProfilePacket
#import gp_concentrator.core.store as store
import json
from gp_node.network.circular_log.common.circular_log import CircularLog
from gp_node.network.network_api import NetworkAPI

class DailyLoadProfileReader(CircularLog):

    """
    :param int START_ADDRESS: Indicates the start address of the daily load profile data in external flash memory
    """

    START_ADDRESS = 0x3F000 #0x3B000

    def get_daily_profile_from_node(self, index):
        """
        Gets data from external flash chip using FlashIO protocol and deserializes
        it to get the Bundle packet.

        :param int index: The index of the entry which is being queried
        :returns: Bundle corresponding to the index^th entry
        :rtype: int
        """
        data = self.get_data_from_node(index)
        entry = DailyLoadProfilePacket()
        try:
            entry.deserialize(data)
        except:
            pass
        return entry

    def get_daily_profile_from_bin(self, index, filepath):
        """
        Reads the binary dumped file and returns the Bundle entry corresponding
        to the index^th entry

        :param int index: the index of the entry which is being queried
        :param str filepath: the index of the binary dumped file
        """
        bin_file = open(filepath, "rb")
        file_address = self.get_start_address(
            index) - self.header["data_block_addr"]
        bin_file.seek(file_address)
        data = bytearray(bin_file.read(self.ENTRY_SIZE))
        entry = DailyLoadProfilePacket()
        try:
            entry.deserialize(data)
        except BaseException:
            pass
        return entry

    def print_daily_profile_from_bin(self, filepath):
        """
        Reads the binary dumped image of the external flash chip
        and prints all log entries from the file

        :param str filepath: The file path of the binary dump of external flash
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_daily_profile_from_bin(i, filepath)
            print (entry)

    def print_daily_profile_from_node(self):
        """
        Keeps using flash io protocol to query all bundle entries from node,
        and prints them out on screen
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_daily_profile_from_node(i)
            print (entry)

    def store_daily_profile_in_file(self):
        """
        Keeps using flash io protocol to query all bundle entries from node,
        and stores them in a CSV file
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        writer = csv.writer(
            open(
                "daily_load_profile.csv",
                "ab"),
            delimiter=' ',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        title = [
            "date",
            "time",
            "cumulative_real_energy",
            "cumulative_apparent_energy"]
        writer.writerow(title)
        for i in range(total_entries):
            entry = self.get_daily_profile_from_node(i)
            data = [
                entry.date_time,
                entry.cumulative_real_energy,
                entry.cumulative_apparent_energy]
            writer.writerow(data)

    def daily_profile_to_store(self, filepath):
        """
        Converts the binary dumped file into store (from gp_concentrator)

        :param str filepath: file path of the binary dumped image of the external flash
        """
        try:
            os.mkdir("store")
        except BaseException:
            pass
        sk = store.open("store")
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_survey_from_bin(i, filepath)
            sf = store.SFile()
            sn = store.Snapshot()
            sn.date_time = entry.date_time
            nd = store.Node()
            nd.cumulative_real_energy = entry.cumulative_real_energy
            nd.cumulative_apparent_energy = entry.cumulative_apparent_energy
            sn.add_node(nd)
            sf.add_snapshot(sn)
            sk.save_sfile(sf, sn.date_time)
