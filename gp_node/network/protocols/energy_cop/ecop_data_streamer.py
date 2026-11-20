"""
Implements master side of EcopDataStreamer Protocol
"""

from gp_node.utils import Address
import time
import datetime
from gp_node.network.protocols.common.protocol import ProtocolMaster, ProtocolError
from gp_node.network.protocols.common.tap import TAPError
from gp_node.network.protocols.packets.energy_cop.ecop_data_stream_packet import EcopDataStreamPacket


class EcopDataStreamerError(ProtocolError):
    """
    Raised when there is any problem in MaxwellDataStream replies.
    DATA_NOT_READY: The energy cop currently does not have any valid data
            as it has not received any from the maxwell meter.
    REPLY_UNEXPECTED_PAYLOAD_LENGTH: The reply length should be off 35 bytes
            for error free data replies but this error is raised if the case
            is other wise.
    SENSOR_UNPLUGGED: Raised if the meter replies saying that the sensor is 
            unplugged.
    """
    DATA_NOT_READY = 1
    SENSOR_UNPLUGGED = 2
    REPLY_UNEXPECTED_PAYLOAD_LENGTH = 3
    pass


class EcopDataStreamerMaster(ProtocolMaster):

    """
    EcopDataStreamerMaster implements a method to retrieve data from energy_cop
    It internally uses EcopDataStreamPacket() to seserialize and temporarly
    store the restored information
    """

    SLAVE_PORT = 9
    MASTER_PORT = 9
    ECOP_DATA_STREAM_SIZE = 37
    GET_DATA_COMMAND = 0x01
    CAL_TIME = 0x02


    def send(self, slave_address):
        """
        This function passes the command argument in the TAP payload except that
        the first byte of the TAP payload is the length of the command.

        :param bytearray command: This is the command which is to be sent to the\
            maxwell board.

        :returns: The payload of the TAP reply
        """
        command = bytearray([self.GET_DATA_COMMAND]) 
        assert(isinstance(command, bytearray))
        #command.insert(0, length)
        self.my_tap_handler.send_packet(self.my_address, slave_address,
                                    self.SLAVE_PORT, self.MASTER_PORT, command)
        try:
            packet = self.my_tap_handler.get_packet_from\
                                (slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise EcopDataStreamerError\
                                (EcopDataStreamerError.TAP_ERROR, tap_error=e)

        bytes = packet.data
        if bytes[36] != 0:
             raise EcopDataStreamerError(bytes[36], tap_packet=packet)
        if len(bytes) == self.ECOP_DATA_STREAM_SIZE:
            packet = EcopDataStreamPacket()
            packet.deserialize(bytes)
            return packet
        else:
            raise EcopDataStreamerError(EcopDataStreamerError.\
                        REPLY_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=packet)

    def ecop_cal_time(self, slave_address, cal_time):
        """
        This function passes the command argument in the TAP payload except that
        the first byte of the TAP payload is the length of the command.

        :param bytearray command: This is the command which is to be sent to the\
            maxwell board.

        :returns: The payload of the TAP reply
        """
        def convert(num):
            if (num >= 10):
                return (num/10)*16 + (num%10)
            else:
                return num

        command = bytearray([self.CAL_TIME])

        if cal_time == "now": 
            cal_time = datetime.datetime.now()
 

        #serializing the time information
        command.append(((cal_time.hour)))
        command.append(chr((cal_time.minute)))
        command.append(chr((cal_time.second)))
        command.append(chr((cal_time.day)))
        command.append(chr((cal_time.month)))
        command.append(chr((cal_time.year%100)))


        assert(isinstance(command, bytearray))
        #command.insert(0, length)
        self.my_tap_handler.send_packet(self.my_address, slave_address,
                                    self.SLAVE_PORT, self.MASTER_PORT, command)
        try:
            packet = self.my_tap_handler.get_packet_from\
                                (slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise EcopDataStreamerError\
                                (EcopDataStreamerError.TAP_ERROR, tap_error=e)

        bytes = packet.data
        return bytes

