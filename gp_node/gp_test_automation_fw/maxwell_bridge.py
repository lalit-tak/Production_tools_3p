"""
Implements master side of MaxwellBridge Protocol
"""
from address import Address
import time
from protocol import ProtocolMaster, ProtocolError
from tap import TAPError


class MaxwellBridgeError(ProtocolError):
    """
    """
    pass


class MaxwellBridgeMaster(ProtocolMaster):

    """
    """

    SLAVE_PORT = 7
    MASTER_PORT = 7

    def send(self, command):
        """
        This function passes the command argument in the TAP payload except that
        the first byte of the TAP payload is the length of the command.

        :param bytearray command: This is the command which is to be sent to the\
            maxwell board.

        :returns: The payload of the TAP reply
        """
        assert(isinstance(command, bytearray))
        length = len(command)
        command.insert(0, length)
        
        return command

    def lock(self, slave_address):
        command = bytearray()
        command.insert(0, 200)
        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.SLAVE_PORT,
            self.MASTER_PORT,
            command)
        try:
            packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise MaxwellBridgeError(MaxwellBridgeError.TAP_ERROR, e)
        return packet.data
