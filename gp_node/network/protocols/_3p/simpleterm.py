import time

"""
Implements master side of Simpleterm protocol
"""
import binascii
from gp_node.network.protocols.common.tap import TAPError, TAPHandler, TAPError
from gp_node.network.protocols.common.protocol import ProtocolMaster, ProtocolError
#from packets.daily_deduction_params import DailyDeductionParams
from gp_node.network.protocols.packets._3p.load_survey_params_3p import LoadSurveyParams3P
from gp_node.network.protocols.packets._3p.load_survey_packet_3p import LoadSurveyPacket3P
from gp_node.network.protocols.packets._3p.event_record_3p import EventRecordPacket3P,EventRecordNumber3P
from gp_node.network.protocols.packets._3p.metering_data_params_3p import MeteringDataParams3P
from gp_node.network.protocols.packets._3p.billing_params_3p import BillingParams3P
from gp_node.network.protocols.packets._3p.prepaid_account_packet_3p import PrepaidAccountPacket3P
from gp_node.network.protocols.packets._3p.slab_packet_3p import SlabConfigurationPacket3P
from gp_node.network.protocols.packets._3p.accounting_state_packet_3p import AccountingStatePacket3P
from gp_node.network.protocols.packets._3p.fixed_deduction_packet_3p import FixedDeductionPacket3P
from gp_node.network.protocols.packets._1p.tod_packet import TodConfigurationPacket
from gp_node.network.protocols._3p.command_mapping_container import commandMappingContainer_3P
from gp_node.network.protocols.packets._3p.tampers_threshold_params_3p import TampersThresholdPacket
from gp_node._3p_fw_upgrade.event_config_ptime import EventsPtimePacket
import gp_node.utils.serialize as serialize
from gp_node.network.protocols.packets._3p.crc_bundle_3p import CrcDataPacket3P
from gp_node.network.protocols.common.data_type_container import INT8, UINT32 ,INT32, UINT64,\
    BYTE_ARRAY, ECOP_PACKET,TAMPER_RECORD_PACKET, DAILY_DEDUCTION_PARAMS,\
    BUNDLE, LOG_PACKET, LOAD_SURVEY_PARAMS, MAXIMUM_DEMAND_PACKET,EVENT_RECORD_TOTAL_PACKET,\
    PREPAID_ACCOUNT_PACKET, SLAB_CONFIGURATION_PACKET, ACCOUNTING_STATE_PACKET, FIXED_DEDUCTION_PACKET,\
    ENERGY_HISTORY_PACKET, EVENT_RECORD_PACKET, DAILY_LOAD_PROFILE_PACKET,METERING_DATA_PACKET,\
    SYNCSTREAM_BUNDLE, PREPAID_ACCOUNT_PACKET_3P, SLAB_CONFIGURATION_PACKET_3P,ACCOUNTING_STATE_PACKET_3P,\
    FIXED_DEDUCTION_PACKET_3P, SURVEY_PACKET_3P, EVENT_RECORD_PACKET_3P,LOAD_SURVEY_PARAMS_3P,\
    METERING_DATA_PARAMS_3P, DAILY_PROFILE_3P, BILLING_PARAMS_3P, BILLING_LOG_PACKET_3P,\
    BILLING_HISTORY_PACKET_3P, SYS_PARAMS_1_PACKET_3P, DLMS_DBG_PACKET_3P,BUNDLE_3P,CRC_BUNDLE_3P,SYS_PARAMS_3P,\
    UINT32_BE, TAMPERS_THRESHOLD_PACKET, EVENTS_PTIME, INSTANT_PROFILE, TOD_CONFIGURATION_PACKET

#from gp_node.network.protocols._3p.string_mapping_container import stringMappingContainer_3P
from gp_node.network.protocols._3p.string_mapping_container import stringMappingContainer_3P
from gp_node.network.protocols.packets._3p.bundle_3p import MeteringDataParamsBundle3P
from gp_node.network.protocols.packets._3p.sys_params_3p import SystemsCommands3P

SET_PARAM_HEADER_SIZE = 2

class SimpletermError_3P(ProtocolError):
    """
    error codes:
    
    GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH: raised when number of bytes in reply to a get_param query\
            does not contain expected number of bytes
    """
    GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH = 1



class SimpletermMaster_3P(ProtocolMaster):

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
        self.my_tap_handler.send_packet(self.my_address, slave_address, 
                                        self.SLAVE_PORT, self.MASTER_PORT, command.strip());

        try:
            packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SimpletermError_3P(SimpletermError_3P.TAP_ERROR, e)
        else:
            for key,val in stringMappingContainer_3P.items():
                if key == serialize.deserialize_uint16(packet.data):
                    #print "val", val
                    #print "key", key
                    return val



    def get_param(self, slave_address, param_number, param_type, interval = 0):
        """
        This function is used to execute commands such as "get_voltage".
        :param str param_number: The mapped command number of the parameter which is being asked for.\
            Such as 20000 for "network", 20036 for "oldest_survey" etc.
        :param int param_type: Indicates the type of the expected value to be retuned by\
            the client. For example, if param_type is UINT32, then the reply\
            should contain 4 bytes, and the reply would then be deserialized as a UINT32\
        :returns: The deserialized value of the returned type.
        :rtype: depends on param_type.
        :raises: SimpletermError with error code GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH\
            if the length of the reply is not the consistent with the param_type argument
        """

        cmd = bytearray()
        cmd.extend(serialize.serialize_uint16(param_number))

        self.my_tap_handler.send_packet(self.my_address, slave_address, self.MASTER_PORT, self.SLAVE_PORT, cmd)

        try:
            tap_packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SimpletermError_3P(SimpletermError_3P.TAP_ERROR, tap_error=e)
            
        # Here 3 phase things begin
        '''
        print "Sending Recived Things"
        temp_buf =  bytearray()
        temp_buf =  tap_packet.data
        for byte in temp_buf:
            print hex(byte)
        '''
        # Debugging End here
        if param_type == UINT64:
            if len(tap_packet.data) == 8:
                print (' '.join(format(n,'02X') for n in tap_packet.data ))
                return serialize.deserialize_uint64(tap_packet.data)
            else:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if param_type == UINT32:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_uint32(tap_packet.data)
            else:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
        if param_type == INT32:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_int32(tap_packet.data)
            else:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
        if param_type == INT8:
            if len(tap_packet.data) == 1:
                return serialize.deserialize_int8(tap_packet.data)
            else:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
        #if param_type == UINT8:
        #    if len(tap_packet.data) == 1:
        #        return serialize.deserialize_int8(tap_packet.data)
        #    else:
        #        raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
        if param_type == DAILY_DEDUCTION_PARAMS:
            ddp = DailyDeductionParams()
            try:
                ddp.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return ddp
        if param_type == LOAD_SURVEY_PARAMS_3P:
            #print ' '.join(format(n,'02X') for n in tap_packet.data )
            lsp = LoadSurveyParams3P()
            try:
                lsp.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return lsp
        
        if param_type == METERING_DATA_PARAMS_3P:
            mdp = MeteringDataParams3P()
            if param_number == commandMappingContainer_3P.GET_METERING_DATA_ENERGY_3P:
                try:
                    mdp.deserialize_p2(tap_packet.data)
                except IndexError:
                    raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return mdp.get_packet_p2()
            elif param_number == commandMappingContainer_3P.GET_METERING_DATA_IP_3P:
                try:
                    mdp.deserialize_p1(tap_packet.data)
                except IndexError:
                    raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return mdp.get_packet_p1()

            elif param_number == commandMappingContainer_3P.GET_METERING_DATA_RESOULTION_3P:
                try:                  
                    mdp.deserialize_p3(tap_packet.data)
                except IndexError:
                    raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return mdp.get_packet_p3()

            elif param_number == commandMappingContainer_3P.GET_METERING_DATA_RESERVED_3P:
                try:                  
                    mdp.deserialize_p4(tap_packet.data)
                except IndexError:
                    raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return mdp.get_packet_p4()
        
        if param_type == PREPAID_ACCOUNT_PACKET_3P:
            entry = PrepaidAccountPacket3P() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == SLAB_CONFIGURATION_PACKET_3P:
            entry = SlabConfigurationPacket3P() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == ACCOUNTING_STATE_PACKET_3P:
            entry = AccountingStatePacket3P() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == FIXED_DEDUCTION_PACKET_3P:
            entry = FixedDeductionPacket3P()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

       
        
        if param_type == SURVEY_PACKET_3P:
            #print  " Reached Found"
            entry = LoadSurveyPacket3P()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry
            
        if param_type == EVENT_RECORD_PACKET_3P:
            #print  " Event Record Packet"
            entry = EventRecordPacket3P()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry   
        if param_type == EVENT_RECORD_TOTAL_PACKET:
            entry = EventRecordNumber3P()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry   

        if param_type == BILLING_PARAMS_3P:
            entry = BillingParams3P()
            try:
                entry.deserialize_billing_params(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.get_billing_params_packet()

        if param_type == SYS_PARAMS_1_PACKET_3P:
            entry = BillingParams3P()
            try:
                entry.deserialize_sys_params(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.get_sys_packet()
        
        if param_type == SYS_PARAMS_3P:
            entry = SystemsCommands3P()
            if param_number == commandMappingContainer_3P.GET_SYS_PARAMS_DATA_3P:
                try:
                    entry.deserialize_sys_params_data(tap_packet.data)
                except IndexError:
                    raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.get_sys_params_data()
            elif param_number == commandMappingContainer_3P.GET_SYS_PARAMS_PROFILE_3P:
                try:
                    entry.deserialize_sys_params_profile(tap_packet.data)
                except IndexError:
                    raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.get_sys_params_profile()         

        if param_type == DLMS_DBG_PACKET_3P:
            entry = BillingParams3P()
            try:
                entry.deserialize_dlms_params(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.get_dlms_debug_packet()
        
        if param_type == TAMPERS_THRESHOLD_PACKET:
            entry = TampersThresholdPacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry
        
        if param_type == EVENTS_PTIME:
            entry = EventsPtimePacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.getEventsPtime()
        
        if param_type == INSTANT_PROFILE:
            entry = MeteringDataParams3P()
            try:
                entry.deserialize_instant_profile_packet(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.get_instant_profile_packet()
        
        if param_type == TOD_CONFIGURATION_PACKET:
            entry = TodConfigurationPacket()
            try:
                print(tap_packet.data)
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
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
        if param_type == LOAD_SURVEY_PARAMS_3P:
            cmd.extend(value.serialize())
        if param_type == SLAB_CONFIGURATION_PACKET_3P:
            cmd.extend(value.serialize())
        if param_type == FIXED_DEDUCTION_PACKET_3P:
            cmd.extend(value.serialize())
        if param_type == MAXIMUM_DEMAND_PACKET:
            cmd.extend(value.serialize())
        if param_type == BYTE_ARRAY:
            length_ = len(value)
            cmd.extend(value[0:length_])
        #if param_type == BYTE_ARRAY:
        #    cmd.extend(value[0:8])

        self.my_tap_handler.send_packet(self.my_address, slave_address, self.MASTER_PORT, self.SLAVE_PORT, cmd)
        try:
            tap_packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SimpletermError_3P(SimpletermError_3P.TAP_ERROR, tap_error=e)
        else:
            #print "i M in KEy , Value"
            for key,val in stringMappingContainer_3P.items():
                if key == serialize.deserialize_uint16(tap_packet.data, "reverse"):
                    return val



    def set_and_get_param(self, slave_address, command, set_param, set_param_type, get_param_type):
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
        cmd.extend(serialize.serialize_uint16(command))
        #print "Command :" + str(command)
        while len(cmd) < SET_PARAM_HEADER_SIZE:
            cmd.append('\x00')
        if set_param_type == UINT32:
            cmd.extend(serialize.serialize_uint32(set_param))
        if set_param_type == BYTE_ARRAY:
            cmd.extend(set_param[0:8])
            for byte in cmd:
                hex(byte)

        self.my_tap_handler.send_packet(self.my_address, slave_address, self.MASTER_PORT, self.SLAVE_PORT, cmd)
        try:
            tap_packet = self.my_tap_handler.get_packet_from(slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SimpletermError_3P(SimpletermError_3P.TAP_ERROR, tap_error=e)
            
        if (get_param_type == SURVEY_PACKET_3P):
            entry = LoadSurveyPacket3P()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry
        if (get_param_type == EVENT_RECORD_PACKET_3P):
            entry = EventRecordPacket3P()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry
        
        if get_param_type == CRC_BUNDLE_3P:
            crc = CrcDataPacket3P()
            try:
                crc.deserialize_crc_packet1(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return crc.get_crc_packet1()

        if get_param_type == DAILY_PROFILE_3P:
            #print  " Reached Found"
            entry = LoadSurveyPacket3P()
            try:
                entry.deserialize_daily_profile(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.get_daily_profile_packet()
            
        if get_param_type == BILLING_LOG_PACKET_3P:
            entry = BillingParams3P()
            try:
                entry.deserialize_billing_log_packet(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.get_billing_log_packet()

        if get_param_type == BILLING_HISTORY_PACKET_3P:
            entry = BillingParams3P()
            try:
                entry.deserialize_billing_history_packet(tap_packet.data)
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.get_billing_history_packet()

        if get_param_type == UINT32:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_uint32(tap_packet.data)
            else:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if get_param_type == UINT32_BE:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_uint32(tap_packet.data, order = "reverse")
            else:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if get_param_type == BUNDLE_3P:
            bdl = MeteringDataParamsBundle3P()
            try:
                bdl.deserialize_packet_bundle(tap_packet.data)                    
            except IndexError:
                raise SimpletermError_3P(SimpletermError_3P.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return bdl.get_packet_bundle()