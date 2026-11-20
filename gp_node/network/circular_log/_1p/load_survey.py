import os
import argparse
import csv
import datetime
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1pn.flash_io import FlashIOMasterN, FlashIOErrorN
#from gp_node.network.protocols.common.flash_io import FlashIOMasterN, FlashIOErrorN
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
from gp_node.network.protocols.packets._1pn.bundle import Bundle
#import gp_concentrator.core.store as store
import json
from gp_node.network.circular_log.common.circular_log import CircularLog

#from gp_node.network.network_api import NetworkAPI


class LoadSurveyReaderN(CircularLog):

    """
    :param int START_ADDRESS: Indicates the start address of the load survey data in external flash memory
    """

    START_ADDRESS = 0x16000

    def get_survey_from_node(self, index):
        """
        Gets data from external flash chip using FlashIO protocol and deserializes
        it to get the Bundle packet.

        :param int index: The index of the entry which is being queried
        :returns: Bundle corresponding to the index^th entry
        :rtype: int
        """
        data = self.get_data_from_node(index)
        entry = Bundle()
        try:
            entry.deserialize(data)
        except BaseException:
            pass
        return entry

    def get_survey_from_bin(self, index, filepath, interval):
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
        entry = Bundle()
        try:
            entry.deserialize(data)
        except BaseException:
            pass
        return entry

    def print_survey_from_bin(self, filepath):
        """
        Reads the binary dumped image of the external flash chip
        and prints all log entries from the file

        :param str filepath: The file path of the binary dump of external flash
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_survey_from_bin(i, filepath)
            print (entry)

    def print_survey_from_node(self):
        """
        Keeps using flash io protocol to query all bundle entries from node,
        and prints them out on screen
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        for i in range(total_entries):
            entry = self.get_survey_from_node(i)
            print (entry)

    def store_survey_in_file(self, interval):
        """
        Keeps using flash io protocol to query all bundle entries from node,
        and stores them in a CSV file
        """
        total_entries = 0
        total_entries = self.get_total_entries()
        writer = csv.writer(
            open(
                "load_survey.csv",
                "ab"),
            delimiter=' ',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        title = [
            "start",
            "time",
            "end",
            "time",
            "voltage",
            "current",
            "active_power",
            "power_factor",
            "frequency",
            "active_energy",
            "apparent_energy",
            "credits",
            "energy_per_credit",
            "tamper_flags"]
        writer.writerow(title)
        for i in range(total_entries):
            entry = self.get_survey_from_node(i)
            data = [
                entry.end_time -
                datetime.timedelta(
                    minutes=interval),
                entry.end_time,
                entry.voltage,
                entry.current,
                entry.active_power,
                entry.power_factor,
                entry.frequency,
                entry.active_energy,
                entry.apparent_energy,
                entry.credits,
                entry.energy_per_credit,
                entry.tamper_flags]
            writer.writerow(data)

    def survey_to_store(self, filepath):
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
            sn.end_time = entry.end_time
            nd = store.Node()
            nd.voltage = entry.voltage
            nd.current = entry.current
            nd.active_power = entry.active_power
            nd.power_factor = entry.power_factor
            nd.frequency = entry.frequency
            nd.active_energy = entry.active_energy
            nd.reactive_energy = entry.reactive_energy
            nd.credits = entry.credits
            nd.price = entry.energy_per_credit
            nd.tamper_flag_list = entry.tamper_flags
            nd.survey_interval = entry.survey_interval
            sn.add_node(nd)
            sf.add_snapshot(sn)
            sk.save_sfile(sf, sn.end_time)
