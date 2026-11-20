"""
Implements the master side of Recharge protocol
"""

from gp_node.network.protocols.common.protocol import ProtocolMaster, ProtocolError
from gp_node.network.protocols.common.tap import TAPPacket, TAPHandler, TAPError

class RechargeError(ProtocolError):
    """
    error codes:

    HELLO_REPLY_INCORRECT: when the reply to HELLO_CLIENT is not HELLO_MASTER

    TRANSFER_CREDIT_REPLY_INCORRECT: when the reply to AMOUNT is not one among\
            ACCEPT, REJECT_AMT_TOO_LARGE, REJECT_NEGATIVE_VALUE, REJECT_RECHARGE_LIMIT

    PAYLOAD_FORMAT_ERROR: when the paylod of reply is incorrectly formatted
    """

    HELLO_REPLY_INCORRECT = 1
    TRANSFER_CREDIT_REPLY_INCORRECT = 2
    PAYLOAD_FORMAT_ERROR = 3

    

class RechargePacket:

    HELLO_CLIENT = 0
    HELLO_MASTER = 1
    AMOUNT = 2
    ACCEPT = 3
    REJECT_AMT_TOO_LARGE = 4
    RECHARGE_CMD_REJECT_REPEATED_RECHARGE = 5
    REJECT_AS_PREPAID_DISABLE = 6
    def __init__(self):
        """
        :param uid: unique transaction ID associcated with each recharge. NOT USED IN CURRENT VERSION
        :type uid: int

        :param command: represents one of the 5 possible commands in the recharge transaction
        :type command: int

        :param data: stores information of the amount that is to be recharged
        :type data: bytearray
        """
        self.uid = 0
        self.command = self.HELLO_CLIENT
        self.data = bytearray()

    def __eq__(self, other):
        output = True
        output = output and (self.uid == other.uid)
        output = output and (self.command == other.command)
        output = output and (self.data == other.data)
        return output

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        output = "uid: " + str(self.uid) + "\n"
        output += "command: " + str(self.command) + "\n"
        output += "data: " + str(self.data) + "\n"
        return output

    def fill(self, uid, command, data):
        """
        populates uid, command and data
        """
        self.uid = uid
        self.command = command
        self.data = data

    def deserialize(self, tap_packet):
        """
        Converts the packet into the payload of the underlying TAP packet
        """
        buf = tap_packet.data
        if len(buf) < 5:
            raise RechargeError(RechargeError.PAYLOAD_FORMAT_ERROR, tap_packet=tap_packet)
        self.uid = (buf[0] << 24) + (buf[1] << 16) + (buf[2] << 8) + buf[3]
        self.command = buf[4]
        if len(buf) > 5:
            self.data = buf[5:]
        else:
            self.data = bytearray()

    def serialize(self):
        """
        Populates uid, command & data, from the payload of the underlying
        TAP packet

        :returns: recharge protocol's payload for TAP packet
        :rtype: bytearray
        """
        payload = bytearray()
        payload.extend(chr((self.uid & 0xFF000000) >> 24))
        payload.extend(chr((self.uid & 0x00FF0000) >> 16))
        payload.extend(chr((self.uid & 0x0000FF00) >> 8))
        payload.extend(chr((self.uid & 0x000000FF) >> 0))
        payload.extend(chr(self.command))
        payload.extend(self.data)
        return payload


class RechargeMaster(ProtocolMaster, object):

    """
    """

    MASTER_PORT = 103
    SLAVE_PORT = 3
    dummy_uid = 0

    def _exchange_hello(self, slave_address):
        """
        This forms the first stage of a recharge transaction.
        Sends HELLO packet to the slave, and verifies that the slave correctly replies to the HELLO packet
        """
        my_recharge_packet = RechargePacket()
        my_recharge_packet.fill(self.dummy_uid, RechargePacket.HELLO_CLIENT, bytearray())
        self.my_tap_handler.send_packet(self.my_address, slave_address, self.MASTER_PORT,
                                        self.SLAVE_PORT, my_recharge_packet.serialize())
        try:
            packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise RechargeError(RechargeError.TAP_ERROR, tap_error=e)
        my_recharge_packet.deserialize(packet)
        if my_recharge_packet.command != RechargePacket.HELLO_MASTER:
            raise RechargeError(RechargeError.HELLO_REPLY_INCORRECT, tap_packet=packet)

    #TODO: maybe raise exception when recharge is rejected ?
    def _transfer_credit(self, slave_address, amount, uid):
        """
        This is the second stage of a recharge transaction
        Sends the amount by which the slave is to be recharged.

        :param amount: amount by which the slave is to be recharged
        :type amount: int

        :returns: reply from the slave. This can either be 'accepted' or 'rejected'
        :rtype: str
        """

        # Send amount
        my_recharge_packet = RechargePacket()

        # The first 8 bytes of the payload are ignored. The last 4 bytes of the payload is the amount.
        transfer_credit_packet_data = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + \
                chr((amount >> 24) & 0xFF) + chr((amount >> 16) & 0xFF) + chr((amount >> 8) & 0xFF) + chr(amount & 0xFF)
        my_recharge_packet.fill(uid, RechargePacket.AMOUNT, transfer_credit_packet_data)
        self.my_tap_handler.send_packet(self.my_address, slave_address, self.MASTER_PORT, self.SLAVE_PORT, my_recharge_packet.serialize())
        # Receive accept or reject
        recharge_status = ''
        try:
            packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise RechargeError(RechargeError.TAP_ERROR, tap_error=e)
        my_recharge_packet.deserialize(packet)
        if my_recharge_packet.command == RechargePacket.ACCEPT:
            recharge_status = 'Accepted'
        elif my_recharge_packet.command == RechargePacket.REJECT_AMT_TOO_LARGE:
            recharge_status = 'Rejected: Amount too large.'
        elif my_recharge_packet.command == RechargePacket.RECHARGE_CMD_REJECT_REPEATED_RECHARGE:
            recharge_status = 'rejected: Repeated Recharge'
        elif my_recharge_packet.command == RechargePacket.REJECT_AS_PREPAID_DISABLE:
            recharge_status = 'rejected: Prepaid is disable'
        else:
            raise RechargeError(RechargeError.TRANSFER_CREDIT_REPLY_INCORRECT)
        return recharge_status    

    def recharge(self, slave_address, amount, uid):
        """
        Recharges a node with the amount mentioned.

        Step 1. Exchange Hello

        Step 2. Transfer Credits

        :returns: A string which can either be "accepted" or "rejected: amount too large".

        :raises: RechargeError with appropriate error codes
        """
        # self._exchange_hello(slave_address)
        return self._transfer_credit(slave_address, amount, uid)
