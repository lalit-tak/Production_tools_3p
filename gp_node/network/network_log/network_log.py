"""
The module poulates the log file with the network log retrieved from the header
of packet mode packet.The log is created in CSV format.
"""
from gp_node.utils import Address
import time
import csv
import os.path
import datetime


class networkDataLogger(object):

    def __init__(self, log_folder_path):
        """
        The constructor for log handler
        :param log_folder_path:Location where the log needs to be stored.
        :type log_folder_path: str
        """
        self.log_folder_path = log_folder_path
        pass

    def put_network_log(self, data_dict):
        """
        Puts a log into the log file.Creates a new file everyday.

        :param data_dict:Data that needs to be populated
        :type data_dict: data_dict (please look into the implementation)
        """
        header = (
            "time",
            "start character",
            "system ID",
            "origin-id",
            "origin rssi",
            "origin-network-level",
            "hop counter",
            "message counter",
            "latency counter",
            "message detail",
            "message data msb",
            "message data lsb",
            "address data",
            "module temperature",
            "module voltage",
            "digital inputs",
            "analogue 0",
            "analogue 1",
            "HW version",
            "FW version")
        write_header = False
        # form the file path
        file_path = self.log_folder_path + "/" + \
            str(datetime.datetime.now().date()) + ".txt"
        # check if file present
        if os.path.isfile(file_path) == False:
            write_header = True
        # open the file
        self.f = open(file_path, "a")

        self.csv_writer = csv.writer(self.f)
        # if new file created print a header
        if write_header:
            self.csv_writer.writerow(header)
        # for the row to be written
        row = (str(datetime.datetime.strftime(datetime.datetime.now(),
                                              "%H:%M:%S")),
               data_dict["start-character"],
               data_dict["system-id"],
               data_dict["origin-id"],
               data_dict["origin-rssi"],
               data_dict["origin-network-level"],
               data_dict["hop-counter"],
               data_dict["message-counter"],
               data_dict["latency-counter"],
               data_dict["message-detail"],
               data_dict["message-data-msb"],
               data_dict["message-data-lsb"],
               data_dict["address-data"],
               data_dict["module-temprature"],
               data_dict["module-voltage"],
               data_dict["digital-inputs"],
               data_dict["analogue-0"],
               data_dict["analogue-1"],
               data_dict["hw-version"],
               data_dict["fw-version"])
        self.csv_writer.writerow(row)
        self.f.close()
