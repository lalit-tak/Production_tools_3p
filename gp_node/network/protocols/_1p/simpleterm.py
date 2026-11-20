import time
import datetime
"""
Implements master side of Simpleterm protocol
"""
import binascii
from gp_node.network.protocols.common.tap import TAPError, TAPHandler, TAPError
from gp_node.network.protocols.common.protocol import ProtocolMaster, ProtocolError
from gp_node.network.protocols.packets._1p.daily_deduction_params import DailyDeductionParams
from gp_node.network.protocols.packets._1p.load_survey_params import LoadSurveyParams
from gp_node.network.protocols.packets._1p.tamper_record_packet import TamperRecordPacket
from gp_node.network.protocols.packets._1p.bundle import Bundle
from gp_node.network.protocols.packets._1p.daily_load_profile_packet import DailyLoadProfilePacket
from gp_node.network.protocols.packets._1p.log_packet import LogPacket
from gp_node.network.protocols.packets._1p.prepaid_account_packet import PrepaidAccountPacket
from gp_node.network.protocols.packets._1p.slab_packet import SlabConfigurationPacket
from gp_node.network.protocols.packets._1p.accounting_state_packet import AccountingStatePacket
from gp_node.network.protocols.packets._1p.fixed_deduction_packet import FixedDeductionPacket
from gp_node.network.protocols.packets._1p.maximum_demand_packet import MaximumDemandPacket
from gp_node.network.protocols.packets._1p.energy_history_packet import EnergyHistoryPacket
from gp_node.network.protocols.packets._1p.event_record_packet import EventRecordPacket, EventRecordNumber
from gp_node.network.protocols.packets._1p.metering_data_packet import MeteringDataPacket
from gp_node.network.protocols.packets._1p.syncstream_bundle import SyncstreamBundle
from gp_node.network.protocols.packets._1p.bundle_1p import DCUBundlePacket
from gp_node.network.protocols.packets._1p.meter_para_1p import IP_MeterPara
from gp_node.network.protocols.packets._1p.relay_para_1p import IP_RelayPara
from gp_node.network.protocols.packets._1p.tariff_packet import TariffPacket
from gp_node.network.protocols._1p.command_mapping_container import commandMappingContainer
import gp_node.utils.serialize as serialize
from gp_node.network.protocols.packets._1p.billing_md_packet import BillingMdPacket
from gp_node.network.protocols.packets.energy_cop.ecop_data_stream_packet import EcopDataStreamPacket
from gp_node.network.protocols.common.string_mapping_container import stringMappingContainer
from gp_node.network.protocols.packets._1p.tod_packet import TodConfigurationPacket
from gp_node.network.protocols.packets._1p.power_limit_tod_packet import PowerLimitTodPacket
from gp_node.network.protocols.packets._1p.power_limit_tod_packet import PowerLimitParamsPacket
from gp_node.network.protocols._3p.string_mapping_container import stringMappingContainer_3P # patch
from gp_node.network.protocols.common.data_type_container import INT8, UINT8, UINT32 ,UINT16,INT32, UINT64,\
    BYTE_ARRAY, ECOP_PACKET,TAMPER_RECORD_PACKET, DAILY_DEDUCTION_PARAMS,DATA_ARRAY, RESPONSE_PACKET,\
    BUNDLE, LOG_PACKET, TARIFF_PACKET,LOAD_SURVEY_PARAMS, MAXIMUM_DEMAND_PACKET,EVENT_RECORD_TOTAL_PACKET,\
    PREPAID_ACCOUNT_PACKET, SLAB_CONFIGURATION_PACKET, ACCOUNTING_STATE_PACKET, FIXED_DEDUCTION_PACKET,\
    ENERGY_HISTORY_PACKET, EVENT_RECORD_PACKET, DAILY_LOAD_PROFILE_PACKET,METERING_DATA_PACKET,\
    SYNCSTREAM_BUNDLE, GET_TIME_LEFT, PREPAID_ACCOUNT_PACKET_3P, SLAB_CONFIGURATION_PACKET_3P,ACCOUNTING_STATE_PACKET_3P,\
    FIXED_DEDUCTION_PACKET_3P, SURVEY_PACKET_3P, EVENT_RECORD_PACKET_3P,LOAD_SURVEY_PARAMS_3P,\
    METERING_DATA_PARAMS_3P, DAILY_PROFILE_3P, BILLING_PARAMS_3P, BILLING_LOG_PACKET_3P,\
    BILLING_HISTORY_PACKET_3P, SYS_PARAMS_1_PACKET_3P, BUNDLE_1P, DLMS_DBG_PACKET_3P,UINT32_BE,TOD_CONFIGURATION_PACKET,\
    GET_TOD_POWER_LIMIT,BILLING_MD_PACKET,RELAY_STATUS_1P, GET_PARAMS_POWER_LIMIT,POWER_EVENT_RECORD,BYTE_ARRAY_IPV6,\
    BUNDLE_PREPAID_OK, EVENTS_PTIME, INSTANT_PROFILE

SET_PARAM_HEADER_SIZE = 2

class SimpletermError(ProtocolError):
    """
    error codes:

    GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH: raised when number of bytes in reply to a get_param query\
            does not contain expected number of bytes
    """
    GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH = 1



class SimpletermMaster:


    """
    """

    def __init__(self, PortId, my_address, my_tap_handler):

        self.SLAVE_PORT = 4
        self.REC_SLAVE_ID = int(PortId)
        self.MASTER_PORT = 4
        self.my_address = my_address
        self.my_tap_handler = my_tap_handler

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
        command.append(0)
        self.my_tap_handler.send_packet(self.my_address, slave_address, 
                                        self.SLAVE_PORT, self.MASTER_PORT, command.strip())

        try:
            packet = self.my_tap_handler.get_packet_from(slave_address, self.REC_SLAVE_ID)
        except TAPError as e:
            raise SimpletermError(SimpletermError.TAP_ERROR, e)
        for key,val in stringMappingContainer.items():
            if key == serialize.deserialize_uint16(packet.data,"reverse"):
                return val
            elif key == serialize.deserialize_uint16(packet.data):
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
            tap_packet = self.my_tap_handler.get_packet_from(slave_address, self.REC_SLAVE_ID)
        except TAPError as e:
            raise SimpletermError(SimpletermError.TAP_ERROR, tap_error=e)
        
        if param_type == BYTE_ARRAY and param_number != commandMappingContainer.GET_TEMPERATURE_PPM:
            return tap_packet.data
        if param_type == BYTE_ARRAY and param_number == commandMappingContainer.GET_TEMPERATURE_PPM:
            offset = 0
            offsetTemperature = offset+4
            offsetppm = offsetTemperature+4
            offsetTicks = offsetppm+1
            offsetInterval = offsetTicks+1
            reply_dict={}
            reply_dict['TEMPERATURE(C)']=serialize.deserialize_int32(tap_packet.data[offset:offsetTemperature])
            reply_dict['COMPENSATED PPM(DIVED BY 100)']=serialize.deserialize_int32(tap_packet.data[offsetTemperature:offsetppm])
            reply_dict['TICKS']=serialize.deserialize_int8(tap_packet.data[offsetppm:offsetTicks])
            reply_dict['INTERVAL']=serialize.deserialize_uint8(tap_packet.data[offsetTicks:offsetInterval])
            #return reply_dict
            return ("TEMPERATURE(C) : {}\n"
                    "COMPENSATED PPM(DIVED BY 100) : {}\n"
                    "TICKS : {}\n"
                    "INTERVAL : {}\n"
                    ).format(reply_dict['TEMPERATURE(C)'],
                             reply_dict['COMPENSATED PPM(DIVED BY 100)'],
                             reply_dict['TICKS'],
                             reply_dict['INTERVAL'])

        if param_type == UINT32:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_uint32(tap_packet.data[:4])
            else:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if param_type == UINT16:
            if len(tap_packet.data) == 2:
                return serialize.deserialize_uint16(tap_packet.data)
            else:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if param_type == INT32:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_int32(tap_packet.data)
            else:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
        
        if param_type == BILLING_MD_PACKET:
            entry = BillingMdPacket() 
            if param_number == commandMappingContainer.GET_BILLING_INFO:
                try:
                    entry.deserialize_billing_info(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                                          tap_packet=tap_packet)
                return entry.get_billing_info_packet()
            elif param_number == commandMappingContainer.GET_INSTANTANEOUS_DEMAND:
                try:
                    entry.deserialize_get_instantaneous_demand(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                                          tap_packet=tap_packet)
                return entry.get_instantaneous_demand_packet()

        if param_type == INT8:
            if len(tap_packet.data) == 1:
                return serialize.deserialize_int8(tap_packet.data)
            else:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
        
        if param_type == UINT8:
            if len(tap_packet.data) == 1:
                return serialize.deserialize_uint8(tap_packet.data)
            else:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if param_type == BYTE_ARRAY_IPV6:
            temp_str = ''
            if len(tap_packet.data) >38:
                for x in xrange(0,len(tap_packet.data)):
                    temp_str += chr(tap_packet.data[x])
                return temp_str
            else:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)     

        if param_type == TAMPER_RECORD_PACKET:
            if param_number == commandMappingContainer.GET_EARTH_TAMPER_RECORD:
                tamper_type = "earth"
            elif param_number == commandMappingContainer.GET_REV_TAMPER_RECORD:
                tamper_type = "rev"
            elif param_number == commandMappingContainer.GET_NM_TAMPER_RECORD:
                tamper_type = "nm"
            elif param_number == commandMappingContainer.GET_ND_TAMPER_RECORD:
                tamper_type = "nd"
            elif param_number == commandMappingContainer.GET_COVER_TAMPER_RECORD:
                tamper_type = "cover"
            elif param_number == commandMappingContainer.GET_MAG_TAMPER_RECORD:
                tamper_type = "mag"
            trp = TamperRecordPacket(tamper_type)
            try:
                trp.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return trp

        if param_type == DAILY_DEDUCTION_PARAMS:
            ddp = DailyDeductionParams()
            try:
                ddp.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return ddp

        if param_type == LOAD_SURVEY_PARAMS:
            lsp = LoadSurveyParams()
            try:
                lsp.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return lsp

        if param_type == BUNDLE:
            entry = Bundle()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == DAILY_LOAD_PROFILE_PACKET:
            entry = DailyLoadProfilePacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == LOG_PACKET:
            entry = LogPacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == PREPAID_ACCOUNT_PACKET:
            entry = PrepaidAccountPacket() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == SLAB_CONFIGURATION_PACKET:
            entry = SlabConfigurationPacket() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == ACCOUNTING_STATE_PACKET:
            entry = AccountingStatePacket() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == GET_TOD_POWER_LIMIT:
            entry = PowerLimitTodPacket() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == GET_PARAMS_POWER_LIMIT:
            entry = PowerLimitParamsPacket() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == TOD_CONFIGURATION_PACKET:
            entry = TodConfigurationPacket() 
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == FIXED_DEDUCTION_PACKET:
            entry = FixedDeductionPacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == MAXIMUM_DEMAND_PACKET:
            if param_number == commandMappingContainer.GET_PAST_ACTIVE_MD_1 or param_number == commandMappingContainer.GET_PAST_REACTIVE_MD_1 or param_number == commandMappingContainer.GET_PAST_APPARENT_MD_1:
                MD_month = 1
            elif param_number == commandMappingContainer.GET_PAST_ACTIVE_MD_2 or param_number == commandMappingContainer.GET_PAST_REACTIVE_MD_2 or param_number == commandMappingContainer.GET_PAST_APPARENT_MD_2:
                MD_month = 2
            elif param_number == commandMappingContainer.GET_PAST_ACTIVE_MD_3 or param_number == commandMappingContainer.GET_PAST_REACTIVE_MD_3 or param_number == commandMappingContainer.GET_PAST_APPARENT_MD_3:
                MD_month = 3
            elif param_number == commandMappingContainer.GET_PAST_ACTIVE_MD_4 or param_number == commandMappingContainer.GET_PAST_REACTIVE_MD_4 or param_number == commandMappingContainer.GET_PAST_APPARENT_MD_4:
                MD_month = 4
            elif param_number == commandMappingContainer.GET_PAST_ACTIVE_MD_5 or param_number == commandMappingContainer.GET_PAST_REACTIVE_MD_5 or param_number == commandMappingContainer.GET_PAST_APPARENT_MD_5:
                MD_month = 5
            elif param_number == commandMappingContainer.GET_PAST_ACTIVE_MD_6 or param_number == commandMappingContainer.GET_PAST_REACTIVE_MD_6 or param_number == commandMappingContainer.GET_PAST_APPARENT_MD_6:
                MD_month = 6
            elif param_number == commandMappingContainer.GET_CURRENT_ACTIVE_MD or param_number == commandMappingContainer.GET_CURRENT_REACTIVE_MD or param_number == commandMappingContainer.GET_CURRENT_APPARENT_MD:
                MD_month = 7
            entry = MaximumDemandPacket(MD_month)
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry


        if param_type == ECOP_PACKET:
            entry = EcopDataStreamPacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == ENERGY_HISTORY_PACKET:
            if param_number == commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_1 or param_number == commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_1 or param_number == commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_1 or param_number == commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_1:
                month = 1
            elif param_number == commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_2 or param_number == commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_2 or param_number == commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_2 or param_number == commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_2:
                month = 2
            elif param_number == commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_3 or param_number == commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_3 or param_number == commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_3 or param_number == commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_3:
                month = 3
            elif param_number == commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_4 or param_number == commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_4 or param_number == commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_4 or param_number == commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_4:
                month = 4
            elif param_number == commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_5 or param_number == commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_5 or param_number == commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_5 or param_number == commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_5:
                month = 5
            elif param_number == commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_6 or param_number == commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_6 or param_number == commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_6 or param_number == commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_6:
                month = 6
            elif param_number == commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_7 or param_number == commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_7 or param_number == commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_7 or param_number == commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_7:
                month = 7
            entry = EnergyHistoryPacket(month)
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == EVENT_RECORD_PACKET:
            entry = EventRecordPacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == POWER_EVENT_RECORD:
            # entry = EventRecordPacket()
            # try:
            #     entry.deserializex(tap_packet.data)
            # except IndexError:
            #     raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            # return entry
            try:

                VALID_EVENT_NAMES = {   0 :'EVT_NONE',
                                        # Current Related
                                        69  : 'EVT_EARTH_LOADING_OCCURRENCE',
                                        70  : 'EVT_EARTH_LOADING_RESTORATION',
                                        67  : 'EVT_OVER_CURRENT_OCCURRENCE',
                                        68  : 'EVT_OVER_CURRENT_RESTORATION',
                                        51  : 'EVT_REVERSE_OCCURRENCE',
                                        52  : 'EVT_REVERSE_RESTORATION',
                                        71  : 'EVT_HIGH_NEUTRAL_OCCURRENCE',
                                        72  : 'EVT_HIGH_NEUTRAL_RESTORATION',
                                        # Voltage Related
                                         7  : 'EVT_OVER_VOLTAGE_OCCURRENCE',
                                         8  : 'EVT_OVER_VOLTAGE_RESTORATION',
                                         9  : 'EVT_LOW_VOLTAGE_OCCURRENCE',
                                        10  : 'EVT_LOW_VOLTAGE_RESTORATION',
                                        13  : 'EVT_PHASE_SEQUENCE_OCCURRENCE',
                                        14  : 'EVT_PHASE_SEQUENCE_RESTORATION',
                                        # Power Related
                                        101 :'EVT_POWER_FAILURE_OCCURRENCE',
                                        102 :'EVT_POWER_FAILURE_RESTORATION',
                                        # Transactions Related
                                        151 :'EVT_RTC_DATETIME_SET',
                                        152 :'EVT_DEMAND_PERIOD_SET',
                                        153 :'EVT_PROFILE_PERIOD_SET',
                                        154 :'EVT_BILLING_SCHEDULE_SET',
                                        155 :'EVT_ACTIVITY_CALANDER_SET',
                                        157 :'EVT_FIRMWARE_UPGRADE_OCCURENCE',
                                        158 :'EVT_LOAD_LIMIT_SET',
                                        159 :'EVT_LOAD_LIMIT_ENABLE',
                                        160 :'EVT_LOAD_LIMIT_DISABLE',
                                        166 :'EVT_MD_RESET_OCCURENCE',
                                        # Other Related
                                        201 :'EVT_MAGNETIC_TAMPER_OCCURENCE',
                                        202 :'EVT_MAGNETIC_TAMPER_RESTORATION',
                                        203 :'EVT_ND_TAMPER_OCCURENCE',
                                        204 :'EVT_ND_TAMPER_RESTORATION',
                                        207 :'EVT_NM_TAMPER_OCCURENCE',
                                        208 :'EVT_NM_TAMPER_RESTORATION',
                                        209:'EVT_PLUG_OUT_MODULE',
                                        210:'EVT_PLUG_IN_MODULE',
                                        213 :'EVT_CHANGE_TO_FORWARD_MODE',
                                        214 :'EVT_CHANGE_TO_IMP_EXP_MODE',
                                        215 :'EVT_OVERLOAD_OCCURENCE',
                                        216 :'EVT_OVERLOAD_RESTORATION',
                                        # Non-Rollover Related
                                        251:'EVT_COVER_OPEN_OCCURENCE',
                                        # Control Related
                                        301 :'EVT_LOAD_SWITCH_DISCONNECTED',
                                        302 :'EVT_LOAD_SWITCH_CONNECTED',
                                        #Grampower Custom Related Events
                                        10008:'EVT_OVER_POWER_OCCURENCE',
                                        10009:'EVT_OVER_POWER_RESTORATION',
                                        # Invalid Event for errors
                                        512:'INVALID_EVT'}

                buf = bytearray()
                buf = tap_packet.data
                dt = datetime.datetime(1970, 1, 1, 0, 0, 0)

                index=0
                length = len(buf)

                if(length ==0):
                    return "No entry found !!!"
                
                print ("{:<10}{:25}{}".format("Index" , "TimeStamp", "Event"))
                while length > 0:
                    evtId = buf[index]

                    unix_time = ((buf[index+4]<<24)+(buf[index+3]<<16)+(buf[index+2]<<8) +buf[index+1])
                    dt = str(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_time))

                    print ("{:<10}{:25}{}".format((index/5), dt, VALID_EVENT_NAMES[evtId]))
                    index+=5
                    length-=5
                return "Log fetch done !!!"
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return tap_packet   

        if param_type == EVENT_RECORD_TOTAL_PACKET:
            entry = EventRecordNumber()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry    

        if param_type == METERING_DATA_PACKET:
            entry = MeteringDataPacket()
            if param_number == commandMappingContainer.GET_1P_METERING_DATA:
                try:
                    entry.deserialize(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry
            elif param_number == commandMappingContainer.GET_METERING_DATA_IM2:    
                try:
                    entry.deserializePacket2(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.getMeterpacket2()
            elif param_number == commandMappingContainer.GET_THD:    
                try:
                    entry.deserializeTHD(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.getMeterpacketTHD()
            else:    
                try:
                    entry.deserializePacket3(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.getMeterpacket3()

        if param_type == SYNCSTREAM_BUNDLE:
            entry = SyncstreamBundle()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if param_type == BUNDLE_1P:
            bdl = DCUBundlePacket()
            try:
                bdl.deserialize_packet_bundle(tap_packet.data)                    
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            # return bdl.get_packet_dictionary_bundle()  
            return bdl.get_packet_bundle()

        if param_type == BUNDLE_PREPAID_OK:
            try:
                payLen = len(tap_packet.data)
                if payLen == 2:
                    for key,val in stringMappingContainer.items():
                        if key == serialize.deserialize_uint16(packet.data,"reverse"):
                            return val
                        elif key == serialize.deserialize_uint16(packet.data):
                            return val
                else:
                    bdl = DCUBundlePacket()
                    bdl.deserialize_packet_bundle(tap_packet.data)
                    return bdl.get_packet_bundle()
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if param_type == DATA_ARRAY:
            bdl = IP_MeterPara()
            try:
                bdl.deserialize_packet_bundle(tap_packet.data)                    
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return bdl.get_packet_bundle() 
        if param_type == RELAY_STATUS_1P:
            bdl = IP_RelayPara()
            if param_number == commandMappingContainer.GET_PH_WISE_RELAY_STATUS:
                try:
                    bdl.deserialize_ph_packet_bundle(tap_packet.data)                    
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return bdl.get_ph_packet_bundle()
            else:
                try:
                    bdl.deserialize_packet_bundle(tap_packet.data)                    
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return bdl.get_packet_bundle() 
            
        if param_type == TARIFF_PACKET:
            
            entry = TariffPacket() 
            if param_number == commandMappingContainer.GET_PREPAID_INFO:
                
                try:
                    entry.deserializePrepaidInfo(tap_packet.data)
                    # print ">>>>>>>>>>>>>>>>>>>>>>>."
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.getPacketPrepaidInfo()
            else:                
                entry = TariffPacket() 
                try:
                    entry.deserializeTariffGroupInfo(tap_packet.data)                    
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.getTariffGroupInfo()

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
            #print "value being serialized :",value
            cmd.extend(serialize.serialize_uint32(value))
        if param_type == UINT16:
            cmd.extend(serialize.serialize_uint16(value))
        if param_type == INT32:
            cmd.extend(serialize.serialize_int32(value))
        if param_type == INT8:
            cmd.extend(serialize.serialize_int8(value))
        if param_type == UINT8:
            cmd.extend(serialize.serialize_uint8(value))  
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
        if param_type == TOD_CONFIGURATION_PACKET:
            cmd.extend(value.serialize())
        if param_type == TARIFF_PACKET:
            cmd.extend(value.serialize())
        if param_type == GET_TOD_POWER_LIMIT:
            cmd.extend(value.serialize())
        if param_type == EVENTS_PTIME:
            cmd.extend(value.serialize())
        if param_type == BYTE_ARRAY:
            length_ = len(value)
            cmd.extend(value[0:length_])
            
        self.my_tap_handler.send_packet(self.my_address, slave_address, self.MASTER_PORT, self.SLAVE_PORT, cmd)
        try:
            tap_packet = self.my_tap_handler.get_packet_from(slave_address, self.REC_SLAVE_ID)
        except TAPError as e:
            raise SimpletermError(SimpletermError.TAP_ERROR, tap_error=e)
        for key,val in stringMappingContainer.items():
            if key == serialize.deserialize_uint16(tap_packet.data,"reverse"):
                return val
            elif key == serialize.deserialize_uint16(tap_packet.data):
                return val

    #######################################
    def set_rc_param(self, slave_address, param_number, value, param_type):
        """
        this is a temporary block to handle radiocraft set function
        this needs to be integrated in set paramsss function
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
        if param_type == BYTE_ARRAY:
            cmd.extend(value[0:8])

        self.my_tap_handler.send_packet(self.my_address, slave_address, self.MASTER_PORT, self.SLAVE_PORT, cmd)
        try:
            tap_packet = self.my_tap_handler.get_packet_from(slave_address, self.REC_SLAVE_ID)
        except TAPError as e:
            raise SimpletermError(SimpletermError.TAP_ERROR, tap_error=e)
        else:
            #print "i M in KEy , Value"
            for key,val in stringMappingContainer_3P.items():
                if key == serialize.deserialize_uint16(tap_packet.data, "reverse"):
                    return val


    ##########################################
    def set_and_get_param(self, slave_address, param_number, set_param, set_param_type, get_param_type, additional_param = 0):
        """
        This is a temporary block to handle radiocraft get and set function
        this needs to be integrated in set and get params function
        """
    
        cmd = bytearray()
        cmd.extend(serialize.serialize_uint16(param_number))
        while len(cmd) < SET_PARAM_HEADER_SIZE:
            cmd.append(0)

        if set_param_type == UINT32:
            cmd.extend(serialize.serialize_uint32(set_param))
        if set_param_type == INT8:
            cmd.extend(serialize.serialize_uint8(set_param))
        if set_param_type == BYTE_ARRAY:
            cmd.extend(set_param)

        if param_number == commandMappingContainer.IMAGE_TRANSFER_TAP:
            self.my_tap_handler.send_packet(self.my_address, slave_address, self.REC_SLAVE_ID, self.REC_SLAVE_ID, cmd)
        else :
            self.my_tap_handler.send_packet(self.my_address, slave_address, self.MASTER_PORT, self.SLAVE_PORT, cmd)
        #time.sleep(2)
        try:
            tap_packet = self.my_tap_handler.get_packet_from(slave_address, self.REC_SLAVE_ID)
        except TAPError as e:
            raise SimpletermError(SimpletermError.TAP_ERROR, tap_error=e)

        if get_param_type == UINT32:
            if len(tap_packet.data) == 4:
                return serialize.deserialize_uint32(tap_packet.data)
            else:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if get_param_type == UINT16:
            if len(tap_packet.data) == 2:
                return serialize.deserialize_uint16(tap_packet.data,"reverse")
            else:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)

        if (get_param_type == BUNDLE):
            #if (set_param < additional_param):
            entry = Bundle()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry
            #else:
            #    return "Invalid index! Index cannot be greater than the number of block load profiles stored!"
        if (get_param_type == DAILY_LOAD_PROFILE_PACKET):
            #if (set_param < additional_param):
            entry = DailyLoadProfilePacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry
            #else:
            #    return "Invalid index! Index cannot be greater than the number of daily load profiles stored!"
        if (get_param_type == EVENT_RECORD_PACKET):
            entry = EventRecordPacket()
            try:
                entry.deserialize(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry

        if get_param_type == POWER_EVENT_RECORD:
            # entry = EventRecordPacket()
            # try:
            #     entry.deserializex(tap_packet.data)
            # except IndexError:
            #     raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            # return entry
            try:

                VALID_EVENT_NAMES = {   0 :'EVT_NONE',
                                        # Current Related
                                        69  : 'EVT_EARTH_LOADING_OCCURRENCE',
                                        70  : 'EVT_EARTH_LOADING_RESTORATION',
                                        67  : 'EVT_OVER_CURRENT_OCCURRENCE',
                                        68  : 'EVT_OVER_CURRENT_RESTORATION',
                                        51  : 'EVT_REVERSE_OCCURRENCE',
                                        52  : 'EVT_REVERSE_RESTORATION',
                                        71  : 'EVT_HIGH_NEUTRAL_OCCURRENCE',
                                        72  : 'EVT_HIGH_NEUTRAL_RESTORATION',
                                        
                                        # Voltage Related
                                         7  : 'EVT_OVER_VOLTAGE_OCCURRENCE',
                                         8  : 'EVT_OVER_VOLTAGE_RESTORATION',
                                         9  : 'EVT_LOW_VOLTAGE_OCCURRENCE',
                                        10  : 'EVT_LOW_VOLTAGE_RESTORATION',
                                        13  : 'EVT_PHASE_SEQUENCE_OCCURRENCE',
                                        14  : 'EVT_PHASE_SEQUENCE_RESTORATION',
                                        # Power Related
                                        101 :'EVT_POWER_FAILURE_OCCURRENCE',
                                        102 :'EVT_POWER_FAILURE_RESTORATION',
                                        # Transactions Related
                                        151 :'EVT_RTC_DATETIME_SET',
                                        152 :'EVT_DEMAND_PERIOD_SET',
                                        153 :'EVT_PROFILE_PERIOD_SET',
                                        154 :'EVT_BILLING_SCHEDULE_SET',
                                        155 :'EVT_ACTIVITY_CALANDER_SET',
                                        157 :'EVT_FIRMWARE_UPGRADE_OCCURENCE',
                                        158 :'EVT_LOAD_LIMIT_SET',
                                        159 :'EVT_LOAD_LIMIT_ENABLE',
                                        160 :'EVT_LOAD_LIMIT_DISABLE',
                                        166 :'EVT_MD_RESET_OCCURENCE',
                                        # Other Related
                                        201 :'EVT_MAGNETIC_TAMPER_OCCURENCE',
                                        202 :'EVT_MAGNETIC_TAMPER_RESTORATION',
                                        203 :'EVT_ND_TAMPER_OCCURENCE',
                                        204 :'EVT_ND_TAMPER_RESTORATION',
                                        207 :'EVT_NM_TAMPER_OCCURENCE',
                                        208 :'EVT_NM_TAMPER_RESTORATION',
                                        209:'EVT_PLUG_OUT_MODULE',
                                        210:'EVT_PLUG_IN_MODULE',
                                        213 :'EVT_CHANGE_TO_FORWARD_MODE',
                                        214 :'EVT_CHANGE_TO_IMP_EXP_MODE',
                                        215 :'EVT_OVERLOAD_OCCURENCE',
                                        216 :'EVT_OVERLOAD_RESTORATION',
                                        # Non-Rollover Related
                                        251:'EVT_COVER_OPEN_OCCURENCE',
                                        # Control Related
                                        301 :'EVT_LOAD_SWITCH_DISCONNECTED',
                                        302 :'EVT_LOAD_SWITCH_CONNECTED',
                                        #Grampower Custom Related Events
                                        10008:'EVT_OVER_POWER_OCCURENCE',
                                        10009:'EVT_OVER_POWER_RESTORATION',
                                        # Invalid Event for errors
                                        512:'INVALID_EVT'}

                buf = bytearray()
                buf = tap_packet.data
                dt = datetime.datetime(1970, 1, 1, 0, 0, 0)

                index=0
                length = len(buf)

                if(length ==0):
                    return "No entry found !!!"

                print ("{:<10}{:25}{}".format("Index" , "TimeStamp", "Event"))
                while length > 0:
                    evtId = buf[index]

                    unix_time = ((buf[index+4]<<24)+(buf[index+3]<<16)+(buf[index+2]<<8) +buf[index+1])
                    dt = str(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_time))

                    print ("{:<10}{:25}{}".format((index/5), dt, VALID_EVENT_NAMES[evtId]))
                    index+=5
                    length-=5
                return "Log fetch done !!!"
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return tap_packet

        if (get_param_type == METERING_DATA_PACKET):
            entry = MeteringDataPacket()
            if param_number == commandMappingContainer.GET_1P_METERING_DATA:
                try:
                    entry.deserializeRecord(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                if (additional_param == commandMappingContainer.PRINT_DIRECT):
                    return entry.printMeterRecord(set_param)
                else:
                    return entry.getMeterRecord()
            elif(param_number == commandMappingContainer.GET_INSTANT_PROFILE_BY_INDEX):    
                try:
                    entry.deserializePacket4(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.getMeterpacket4()
            else:    
                try:
                    entry.deserializePacket2(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
                return entry.getMeterpacket2()

        if get_param_type == TARIFF_PACKET:
            entry = TariffPacket()
            try:
                entry.deserializePrepaidLogs(tap_packet.data)
            except IndexError:
                raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
            return entry.getPacketPrepaidLogs()

        if get_param_type == BILLING_MD_PACKET:
            entry = BillingMdPacket()
            if param_number == commandMappingContainer.GET_BILLING_BY_INDEX:
                try:
                    entry.deserialize_billing_by_index(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                                          tap_packet=tap_packet)
                return entry.get_billing_by_index_packet()
            elif param_number == commandMappingContainer.GET_FETCH_BILLING_BY_INDEX:
                try:
                    entry.deserialize_billing_by_index(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                                          tap_packet=tap_packet)
                return entry.get_billing_by_index_packet()
            elif param_number == commandMappingContainer.GET_TOD_BILLING_BY_INDEX:
                try:
                    entry.deserialize_tod_params(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                                          tap_packet=tap_packet)
                if set_param[4] == 1:
                    return entry.get_tod_exp_params()
                return entry.get_tod_params()
            elif param_number == commandMappingContainer.GET_BILLING_DATA_BY_INDEX:
                try:
                    entry.deserialize_billing_data_params(tap_packet.data)
                except IndexError:
                    raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH,
                                          tap_packet=tap_packet)
                return entry.get_billdata_params()
                
        if get_param_type == RESPONSE_PACKET:
            for key,val in stringMappingContainer.items():
                if key == serialize.deserialize_uint16(tap_packet.data,"reverse"):
                    return val

        if get_param_type == BYTE_ARRAY:
            return  tap_packet.data;               

    def set_and_get_rc_param(self, slave_address, command, set_param, set_param_type, get_param_type):    
        cmd = bytearray()
        cmd.extend(serialize.serialize_uint16(command))
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
            tap_packet = self.my_tap_handler.get_packet_from(slave_address, self.REC_SLAVE_ID)
        except TAPError as e:
            raise SimpletermError_3P(SimpletermError_3P.TAP_ERROR, tap_error=e)
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
        
