"""
Implements master side of SimpletermN protocol
"""

from gp_node.network.protocols.common.tap import TAPError, TAPHandler, TAPError
from gp_node.network.protocols.common.protocol import ProtocolMaster, ProtocolError
from gp_node.network.protocols.packets._1pn.daily_deduction_params import DailyDeductionParamsN
from gp_node.network.protocols.packets._1pn.load_survey_params import LoadSurveyParamsN
from gp_node.network.protocols.packets._1pn.tamper_record_packet import TamperRecordPacket
from gp_node.network.protocols.packets._1pn.bundle import Bundle
from gp_node.network.protocols.packets._1pn.log_packet import LogPacketN
from gp_node.network.protocols.packets._1pn.prepaid_account_packet import PrepaidAccountPacket
from gp_node.network.protocols.packets._1pn.slab_packet import SlabConfigurationPacketN
from gp_node.network.protocols.packets._1pn.accounting_state_packet import AccountingStatePacket
from gp_node.network.protocols.packets._1pn.fixed_deduction_packet import FixedDeductionPacketN
from gp_node.network.protocols.packets._1pn.maximum_demand_packet import MaximumDemandPacket
from gp_node.network.protocols._1pn.command_mapping_container import commandMappingContainerN
import gp_node.utils.serialize as serialize
from gp_node.network.protocols.packets.energy_cop.ecop_data_stream_packet import EcopDataStreamPacket
from gp_node.network.protocols.common.string_mapping_container import stringMappingContainer


UINT32 = 1
INT32 = 2
TAMPER_RECORD_PACKET = 3
DAILY_DEDUCTION_PARAMS = 4
BUNDLE = 5
LOG_PACKET = 6
LOAD_SURVEY_PARAMS = 7
PREPAID_ACCOUNT_PACKET = 8
SLAB_CONFIGURATION_PACKET = 9
ACCOUNTING_STATE_PACKET = 10
FIXED_DEDUCTION_PACKET = 11
MAXIMUM_DEMAND_PACKET = 12
INT8 = 13
ECOP_PACKET = 14
SET_PARAM_HEADER_SIZE = 2


class SimpletermNError(ProtocolError):
    """
    error codes:

    GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH: raised when number of bytes in reply to a get_param query\
            does not contain expected number of bytes
    """
    GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH = 1


class SimpletermNMaster(ProtocolMaster):

    """
    """

    SLAVE_PORT = 4
    MASTER_PORT = 4

    def execute_command(self, slave_address, command_number):
        """
        Sends the command_string argument as it is
        to the underlying TAP layer & returns the reply from the TAP layer
        as it is. This function is a very thin layer on top of TAP.

        :param str command_number: The mapped command number of the parameter which is being asked for.\
            Such as 10025 for "lock_state", 10031 for "fd_reset" etc.
        :returns: The bytearray as returned by the underlying TAP layer
        """

        command = bytearray()
        command.extend(serialize.serialize_uint16(command_number))
        command.append('\0')
        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.SLAVE_PORT,
            self.MASTER_PORT,
            command.strip())

        try:
            packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)

        except TAPError as e:
            raise SimpletermNError(SimpletermNError.TAP_ERROR, e)
        else:
            for key, val in stringMappingContainer.items():
                if key == serialize.deserialize_uint16(packet.data, "reverse"):
                    return val

    def get_param(self, slave_address, param_number, param_type, interval=0):
        """
        This function is used to execute commands such as "get_voltage".

        :param str param_number: The mapped command number of the parameter which is being asked for.\
            Such as 20000 for "network", 20036 for "oldest_survey" etc.
        :param int param_type: Indicates the type of the expected value to be retuned by\
            the client. For example, if param_type is UINT32, then the reply\
            should contain 4 bytes, and the reply would then be deserialized as a UINT32\

        :returns: The deserialized value of the returned type.
        :rtype: depends on param_type.
        :raises: SimpletermNError with error code GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH\
            if the length of the reply is not the consistent with the param_type argument
        """

        cmd = bytearray()
        cmd.extend(serialize.serialize_uint16(param_number))

        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.MASTER_PORT,
            self.SLAVE_PORT,
            cmd)
        try:
            tap_packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SimpletermNError(SimpletermNError.TAP_ERROR, tap_error=e)
        if param_type == UINT32:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_uint32(tap_packet.data)
            else:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
        if param_type == INT32:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_int32(tap_packet.data)
            else:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
        if param_type == INT8:
            if len(tap_packet.data) == 1:
                return serialize.deserialize_int8(tap_packet.data)
            else:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
        if param_type == TAMPER_RECORD_PACKET:
            if param_number == commandMappingContainerN.GET_EARTH_TAMPER_RECORD:
                tamper_type = "earth"
            elif param_number == commandMappingContainerN.GET_REV_TAMPER_RECORD:
                tamper_type = "rev"
            elif param_number == commandMappingContainerN.GET_NM_TAMPER_RECORD:
                tamper_type = "nm"
            elif param_number == commandMappingContainerN.GET_ND_TAMPER_RECORD:
                tamper_type = "nd"
            elif param_number == commandMappingContainerN.GET_COVER_TAMPER_RECORD:
                tamper_type = "cover"
            elif param_number == commandMappingContainerN.GET_MAG_TAMPER_RECORD:
                tamper_type = "mag"
            trp = TamperRecordPacket(tamper_type)
            try:
                trp.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return trp
        if param_type == DAILY_DEDUCTION_PARAMS:
            ddp = DailyDeductionParams()
            try:
                ddp.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return ddp
        if param_type == LOAD_SURVEY_PARAMS:
            lsp = LoadSurveyParamsN()
            try:
                lsp.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return lsp
        if param_type == BUNDLE:
            entry = Bundle()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return entry
        if param_type == LOG_PACKET:
            entry = LogPacketN()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return entry
        if param_type == PREPAID_ACCOUNT_PACKET:
            entry = PrepaidAccountPacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return entry

        if param_type == SLAB_CONFIGURATION_PACKET:
            entry = SlabConfigurationPacketN()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return entry

        if param_type == ACCOUNTING_STATE_PACKET:
            entry = AccountingStatePacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return entry

        if param_type == FIXED_DEDUCTION_PACKET:
            entry = FixedDeductionPacketN()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return entry

        if param_type == MAXIMUM_DEMAND_PACKET:
            if param_number == commandMappingContainerN.GET_PAST_MD_1:
                MD_month = 1
            elif param_number == commandMappingContainerN.GET_PAST_MD_2:
                MD_month = 2
            elif param_number == commandMappingContainerN.GET_PAST_MD_3:
                MD_month = 3
            elif param_number == commandMappingContainerN.GET_PAST_MD_4:
                MD_month = 4
            elif param_number == commandMappingContainerN.GET_PAST_MD_5:
                MD_month = 5
            elif param_number == commandMappingContainerN.GET_PAST_MD_6:
                MD_month = 6
            elif param_number == commandMappingContainerN.GET_CURRENT_MD:
                MD_month = 7
            entry = MaximumDemandPacket(MD_month)
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return entry

        if param_type == ECOP_PACKET:
            entry = EcopDataStreamPacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermNError(
                    SimpletermNError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                    tap_packet=tap_packet)
            return entry

    def set_param(self, slave_address, param_number, value, param_type):
        """
        This function is used execute commands like "set_power_limit".
        To create the correct payload for TAP layer, this function appends the param_number
        (which is the mapped command number for a command such as "set power_limit").
        It then also appends the serialized bytearray of the "value" argument
        Thus, the payload looks like "30008 {serialized_value}"

        :param str param_number: The mapped command number of the parameter which is being asked for.\
            Such as 30000 for "address", 30010 for "unlock" etc.
        :param int param_type: Tells how the "value" argument should be serialized\
            to create the TAP payload
        :param value: type of "value" can be variable. It can be an int or DailyDeductionParams etc.\
            This value is serialized and appended to the TAP payload
        """

        cmd = bytearray()
        cmd.extend(serialize.serialize_uint16(param_number))
        while len(cmd) < SET_PARAM_HEADER_SIZE:
            cmd.append('\x00')

        if param_type == UINT32:
            cmd.extend(serialize.serialize_uint32(value))
        if param_type == INT32:
            cmd.extend(serialize.serialize_int32(value))
        if param_type == INT8:
            cmd.extend(serialize.serialize_int8(value))
        if param_type == DAILY_DEDUCTION_PARAMS:
            cmd.extend(value.serialize())
        if param_type == LOAD_SURVEY_PARAMS:
            cmd.extend(value.serialize())
        if param_type == SLAB_CONFIGURATION_PACKET:
            cmd.extend(value.serialize())
        if param_type == FIXED_DEDUCTION_PACKET:
            cmd.extend(value.serialize())
        if param_type == MAXIMUM_DEMAND_PACKET:
            cmd.extend(value.serialize())

        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.MASTER_PORT,
            self.SLAVE_PORT,
            cmd)
        try:
            tap_packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SimpletermNError(SimpletermNError.TAP_ERROR, tap_error=e)
        else:
            for key, val in stringMappingContainer.items():
                if key == serialize.deserialize_uint16(
                        tap_packet.data, "reverse"):
                    return val
