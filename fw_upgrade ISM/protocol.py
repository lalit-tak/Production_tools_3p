"""
This module implements helpers in building and testing application level protocols.
Namely, Simpleterm, Syncstream, Simpletime, SRP & Recharge protocols use this module

All Application protocols must inherit from ProtocolMaster
"""

import inspect
import subprocess
import serial
import time
from tap import TAPHandler, TAPPacket
from gp_node.utils import Address
from nose.tools import assert_raises


class ProtocolMaster:
    """
    Superclass of all application level protocols
    """

    def __init__(self, my_address, my_tap_handler):
        """
        :param master_address: Source address (ie, Master's address) which is to be sent in the packet TAP packet
        :type master_address: Address

        :param my_tap_handler: the TAPHandler instance which is used to access the serial port
        :type my_tap_handler: TAPHandler
        """
        self.my_address = my_address
        self.my_tap_handler = my_tap_handler

class ProtocolError(Exception):
    """
    Parent class for other application protocol exceptions
    """

    TAP_ERROR = 0

    def __init__(self, error_code, tap_error=None, tap_packet=None):
        """
        :param error_code: one of the several possible error codes for \
                the application protocol concerned
        :type error_code: int

        :param tap_error: application level protocols fill this variable as the \
                exception that was thrown by the underlying TAP protocol. \
                Only valid when error_code is TAP_ERROR
        :type tap_error: TAPError

        :param tap_packet: The higher level protocol fills this field when it finds some\
                discrepency.
        :type tap_packet: TAPPacket
        """
        self.error_code = error_code
        self.tap_error = tap_error
        self.tap_packet = tap_packet

    def __str__(self):
        """
        error codes are of integer type, but while printing them out, we would like to see\
        them as strings. As an example, the value of TAP_ERROR is 0, but we would like to print\
        it out as 'TAP_ERROR'. To do this, __str__ traverses through all upper case variables\
        (assuming that error codes are only in upper case), and prints the error code also\
        as string
        """
        error_code_string = "not a valid error code!"
        member_list = inspect.getmembers(self)
        error_code_name_list = []
        for member in member_list:
            if member[0].isupper():
                error_code_name_list.append(member[0])
                if self.error_code == member[1]:
                    error_code_string = member[0]
        output = "\n" + self.__class__.__name__ + "\n"
        output += "error code: " + error_code_string + "\n"
        if self.error_code == self.TAP_ERROR:
            output += "tap error:" + str(self.tap_error) + "\n"
        else:
            output += "tap packet:\n" + str(self.tap_packet) + "\n"
        return output

