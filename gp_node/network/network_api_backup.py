"""
Implements the primary interface to interact with Node
"""
import gp_node
import sys
import serial
import time
import inspect
import datetime
import dateutil.parser
import pprint
import os
import json
import getpass
import os.path
import gp_node.utils.serialize as serialize
import struct
import matplotlib.pyplot as plt

from gp_node._1p_fw_upgrade.soft_crc import SoftCRC

from functools import wraps
from gp_node.utils import Address, TamperFlag
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError

from gp_node.network.protocols._1p.syncstream import SyncstreamMaster, SyncstreamError
from gp_node.network.protocols._1p.simpleterm import SimpletermMaster, SimpletermError


from gp_node.network.protocols._1pn.syncstream import SyncstreamNMaster, SyncstreamNError  # 1p nd
from gp_node.network.protocols._1pn.simpleterm import SimpletermNMaster, SimpletermNError  # 1p nd
from gp_node.network.protocols._1pn.simpletime import SimpletimeNMaster

from gp_node.network.protocols._1pn.recharge import RechargeMasterN, RechargeErrorN
from gp_node.network.protocols._1pn.flash_io import FlashIOMasterN, FlashIOErrorN


from .protocols.packets._1pn.daily_deduction_params import DailyDeductionParamsN
from .protocols.packets._1pn.load_survey_params import LoadSurveyParamsN


from .protocols.packets._1pn.slab_packet import SlabConfigurationPacketN
from .protocols.packets._1pn.fixed_deduction_packet import FixedDeductionPacketN
from gp_node.network.circular_log._1p.log_reader1 import LogReaderN
from gp_node.network.circular_log._1p.load_survey import LoadSurveyReaderN

from gp_node.network.protocols._3p.simpleterm import SimpletermMaster_3P, SimpletermError_3P
from gp_node.network.protocols.common.data_type_container import INT8, UINT8, UINT32, UINT16, INT32, UINT64,\
    BYTE_ARRAY, ECOP_PACKET,TAMPER_RECORD_PACKET, DAILY_DEDUCTION_PARAMS,DATA_ARRAY, RESPONSE_PACKET,\
    BUNDLE, LOG_PACKET, LOAD_SURVEY_PARAMS, MAXIMUM_DEMAND_PACKET,EVENT_RECORD_TOTAL_PACKET,\
    PREPAID_ACCOUNT_PACKET, TARIFF_PACKET, SLAB_CONFIGURATION_PACKET, ACCOUNTING_STATE_PACKET, FIXED_DEDUCTION_PACKET,\
    ENERGY_HISTORY_PACKET, EVENT_RECORD_PACKET, DAILY_LOAD_PROFILE_PACKET,METERING_DATA_PACKET,\
    SYNCSTREAM_BUNDLE, GET_TIME_LEFT, PREPAID_ACCOUNT_PACKET_3P, SLAB_CONFIGURATION_PACKET_3P,ACCOUNTING_STATE_PACKET_3P,\
    FIXED_DEDUCTION_PACKET_3P, SURVEY_PACKET_3P, EVENT_RECORD_PACKET_3P,LOAD_SURVEY_PARAMS_3P,\
    METERING_DATA_PARAMS_3P, DAILY_PROFILE_3P, BILLING_PARAMS_3P, BILLING_LOG_PACKET_3P,\
    BILLING_HISTORY_PACKET_3P, SYS_PARAMS_1_PACKET_3P, BUNDLE_1P, DLMS_DBG_PACKET_3P, BUNDLE_3P, CRC_BUNDLE_3P, SYS_PARAMS_3P,\
    UINT32_BE,  UINT32N, INT32N, TAMPER_RECORD_PACKETN, DAILY_DEDUCTION_PARAMSN, BUNDLEN, LOG_PACKETN,\
    LOAD_SURVEY_PARAMSN, PREPAID_ACCOUNT_PACKETN, SLAB_CONFIGURATION_PACKETN, ACCOUNTING_STATE_PACKETN,\
    FIXED_DEDUCTION_PACKETN, MAXIMUM_DEMAND_PACKETN, INT8N, ECOP_PACKETN , TOD_CONFIGURATION_PACKET ,\
	GET_TOD_POWER_LIMIT,BILLING_MD_PACKET,BYTE_ARRAY_IPV6,GET_PARAMS_POWER_LIMIT,POWER_EVENT_RECORD,RELAY_STATUS_1P,\
    BUNDLE_PREPAID_OK, TAMPERS_THRESHOLD_PACKET, EVENTS_PTIME, INSTANT_PROFILE

SET_PARAM_HEADER_SIZEN = 2

from .protocols._1p.simpletime import SimpletimeMaster
from .protocols.common.packet_mode_commands import rfPacketModeCommandMaster


from .protocols._1p.recharge import RechargeMaster, RechargeError

from .protocols._1p.flash_io     import FlashIOMaster, FlashIOError
from .protocols._1p.flash_io_new import FlashIOMasterNew, FlashIOErrorNew

from .protocols._3p.flash_io import FlashIOMaster_3P, FlashIOError_3P
from .protocols.common.maxwell_bridge import MaxwellBridgeMaster
from .protocols.energy_cop.ecop_data_streamer import EcopDataStreamerMaster, EcopDataStreamerError
from .protocols.common.protocol import ProtocolError


from gp_node.network.protocols._1p.command_mapping_container import commandMappingContainer

from gp_node.network.protocols._1pn.command_mapping_container import commandMappingContainerN

from .protocols._3p.command_mapping_container import commandMappingContainer_3P
from gp_node.maxwell.calibrator.calibration_commands import get_command_string, TIME_DATE_CODE, MTRNO_CODE, CLEAR_1_CODE, CLEAR_2_CODE, ENERGY_CAL_CODE, VICAL_CODE


from .protocols.packets._1p.daily_deduction_params import DailyDeductionParams
from .protocols.packets._1p.load_survey_params import LoadSurveyParams


from gp_node.network.protocols.packets._3p.load_survey_params_3p import LoadSurveyParams3P
from gp_node.network.protocols.packets._3p.metering_data_params_3p import MeteringDataParams3P
from gp_node.network.protocols.packets._3p.crc_bundle_3p import CrcDataPacket3P
from gp_node.network.protocols.packets._3p.sys_params_3p import SystemsCommands3P


from .protocols.packets._1p.slab_packet import SlabConfigurationPacket
from .protocols.packets._1p.tariff_packet import TariffPacket
from .protocols.packets._1p.fixed_deduction_packet import FixedDeductionPacket
from .protocols.packets._1p.bundle_1p import DCUBundlePacket
from gp_node.network.protocols.packets._3p.bundle_3p import MeteringDataParamsBundle3P
import crc16
from gp_node.network.protocols.common.rc_commands import rcCommandPacket
#from protocols.packets.slab_packet import SlabConfigurationPacket3P
#from protocols.packets.fixed_deduction_packet import FixedDeductionPacket3P
from gp_node.network.protocols.packets._1p.tod_packet import TodConfigurationPacket
from gp_node.network.protocols.packets._1p.power_limit_tod_packet import PowerLimitTodPacket
from gp_node.network.protocols.packets._1p.power_limit_tod_packet import PowerLimitParamsPacket
from gp_node.network.protocols.packets._3p.tampers_threshold_params_3p import TampersThresholdPacket
from gp_node._3p_fw_upgrade.event_config_ptime import event_ptime_configuration_list


def _get_crc(block):
    """
    This function is similar to crc16.crc16xmodem() except that it uses
    0xFFFF as the initial value (crc16.crc16xmodem() uses 0x0000 as the initial value).
    The C++ implementation of CRC in node_bsl should be changed to use 0x0000
    as the initial value; once that is done, simply replace _get_crc with crc16.crc16xmodem

    :param bytearray block: The bytearray whose CRC is to be calculated

    :returns: CRC16-CCITT of the input block
    """
    def _bit_reverse(x):
        first_half = x % 16
        second_half = x / 16
        table = {
            0: 0,
            1: 8,
            2: 4,
            3: 12,
            4: 2,
            5: 10,
            6: 6,
            7: 14,
            8: 1,
            9: 9,
            10: 5,
            11: 13,
            12: 3,
            13: 11,
            14: 7,
            15: 15}
        return_value = 16 * table[first_half] + table[second_half]
        return return_value

    formatted_block = bytearray([])
    for byte in block:
        formatted_block.append(_bit_reverse(byte))
        formatted_block.append(0)

    crc = crc16.crc16xmodem(str(formatted_block), 0)
    # print "In CRC Length of block:",len(block), hex(crc)
    return crc


class NetworkAPIError(Exception):

    """
    PROTOCOL_ERROR: Thrown when command execution fails because of an underlying protocol error
    NO_FUNCTION_FOUND: Thrown by the handle_function method when no function by the given name is found
    """

    PROTOCOL_ERROR = 1
    NO_FUNCTION_FOUND = 2

    def __init__(self, error_code, protocol_error=None, msg=""):
        """
        :param protocol_error: valid only when an underlying protocol (ex: Simpleterm) fails.
        :type protocol_error: ProtocolError (or its subclass)
        """
        self.error_code = error_code
        self.msg = msg
        self.protocol_error = protocol_error

    def __str__(self):
        if self.error_code == self.PROTOCOL_ERROR:
            return str(self.protocol_error)
        else:
            return self.msg


def check_errors(func):
    """
    Used as a decorator to wrap around ProtocolError handling around commands of NetworkAPI

    :param func: A member function of NetworkAPI which is to be executed as a command
    :type func: method
    """
    @wraps(func)
    def wrapped_func(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)

        except ProtocolError as e:
            raise NetworkAPIError(
                NetworkAPIError.PROTOCOL_ERROR,
                protocol_error=e)
    return wrapped_func


class NetworkAPI:

    """
    NetworkAPI forms a thin layer on top of all Application Protocols. The only reason for
    the existence of this class to provide a consistent API to communicate with the Node.
    Any external python programs (such as the concentrator software) willing to communicate
    with the Node should use the NetworkAPI class. The external programs should NOT
    use SimpletermMaster, SyncstreamMaster (etc) classes directly.

    NetworkAPI has instances of each of the application protocol masters, namely:
    - SyncstreamMaster
    - SimpletermMaster
    - SimpletimeMaster
    - RechargeMaster
    - FlashIOMaster
    - MaxwellBridgeMaster

    Most member functions of NodeAPI are simply thin wrappers around one of the above
    protocols. As an example, the get_power_factor method of NetworkAPI simply calls
    the get_param method of SimpletermMaster.

        @check_errors
        def get_power_factor(self, addr):
            return self.my_simpleterm_master.get_param(addr, "power_factor", INT32)/1000.0

    There are two ways two use NetworkAPI
    1. Directly call member functions (such as get_power_factor). This is the normal way
    of using NetworkAPI. node-shell and most other utilities using NetworkAPI use this
    methodology
    2. Using handle_function_request method. The handle_function_request is present purely
    for the conc-engine. The handle_function_request takes in a string and makes a call to the
    method with the same name as given in the string. This is used in Transaction execution
    in conc-engine. (Eventually, the handle_function_request method should be removed
    entirely and its functionality should be shifted into the conc-engine implementation)
    """

    def __init__(
            self,
            ser,
            portID,
            mode="rc_packet",
            log_path="~/.grampower/gp_node/network_log"):
        """
        Does the following:
        * Creates a tap_handler to interact with the gateway.
        * Creates 'masters' for all protocols. All the masters share the same tap_handler
        * Hardcodes address of this API as 0.0.1.2; hence, all queries made from NetworkAPI would\
                have the source address as 0.0.1.2.
        * Inspects decorated member functions and stores them in a list for latter usage

        :param ser: serial object which is used to connect to the gateway
        :type ser: serial.Serial
        """
        self.my_address = Address("1.78.71.201")
        # current_path=gp_node.__file__
        # current_path=current_path.split('gp_node')[0]
        # command_map_json="C:/Python27/Lib/site-packages/gp_node-41-py2.7.egg/gp_node/network/meter_command.json"
        # fx=open(command_map_json,'r')
        # data=json.loads(fx.read())
        try:
            os.makedirs(os.path.expanduser("~/.grampower/gp_node/network_log"))
        except BaseException:
            pass
        self.log_path = os.path.expanduser(log_path)
        self.my_tap_handler = TAPHandler(ser, ser.timeout, mode, self.log_path)
        self.my_syncstream_master = SyncstreamMaster(
            self.my_address, self.my_tap_handler)
        self.my_syncstream_masterN = SyncstreamNMaster(
            self.my_address, self.my_tap_handler)

        self.my_simpleterm_master = SimpletermMaster(
            portID, self.my_address, self.my_tap_handler)
        self.my_simpleterm_masterN = SimpletermNMaster(
            self.my_address, self.my_tap_handler)
        self.my_recharge_masterN = RechargeMasterN(
            self.my_address, self.my_tap_handler)

        self.my_simpleterm_master_3p = SimpletermMaster_3P(
            self.my_address, self.my_tap_handler)
        self.my_recharge_master = RechargeMaster(
            self.my_address, self.my_tap_handler)
        self.my_flash_io_master = FlashIOMaster(
            self.my_address, self.my_tap_handler)
        self.my_flash_io_master_new = FlashIOMasterNew(
            portID, self.my_address, self.my_tap_handler)    
        self.my_flash_io_masterN = FlashIOMasterN(
            self.my_address, self.my_tap_handler)

        self.my_flash_io_master_3p = FlashIOMaster_3P(
            self.my_address, self.my_tap_handler)
        self.my_maxwell_bridge_master = MaxwellBridgeMaster(
            self.my_address, self.my_tap_handler)
        self.my_ecop_data_streamer = EcopDataStreamerMaster(
            self.my_address, self.my_tap_handler)
        self.rf_command_handler = rfPacketModeCommandMaster(
            self.my_address, self.my_tap_handler)
        command_functions = inspect.getmembers(self)
        self.function_list = []

        self.loggern = LogReaderN(self, 4, 42)
        self.load_surveyn = LoadSurveyReaderN(self, 232, 32)

        for entry in command_functions:
            if inspect.ismethod(entry[1]) and entry[0][0] != "_":
                if entry[0] != 'handle_function_request':
                    self.function_list.append(entry)

        self.pp = pprint.PrettyPrinter(indent=4)
        self.obj_rcCommandPacket = rcCommandPacket()
	# self.command_meter_dict=data

    def handle_function_request(self, addr, request):
        """
        Parses the request and calls a member function corresponding to the request.

        Two possible formats for request are allowed:
            - 'a sample function': \
                    In this case, the method a_sample_function(addr) is called
            - 'a sample function: argument': \
                    In this case, the method a_sample_function(addr, argument) is called.
                    The argument is passed in as a string

        :param addr: address of node to whom a request/command is to be sent
        :type addr: Address

        :param request:
        :type request: str

        :raises: NetworkAPIError
        """
        function_found = False
        if ":" not in request:
            for f in self.function_list:
                if f[0] == request.replace(" ", "_"):
                    function_found = True
                    # Pretty format result
                    #result = self.pp.pformat(f[1](addr))
                    result = str(f[1](addr))

                    try:
                        return result + " " + f[1].units
                    except AttributeError:
                        return result
            if function_found is False:
                raise NetworkAPIError(
                    error_code=NetworkAPIError.NO_FUNCTION_FOUND,
                    msg="no such function")
        else:
            f_str = request.split(":")[0]
            argument = ':'.join(request.split(":")[1:])
            function_found = False
            for f in self.function_list:
                if f[0] == f_str.replace(" ", "_"):
                    function_found = True
                    return str(f[1](addr, argument))
            if function_found is False:
                raise NetworkAPIError(
                    error_code=NetworkAPIError.NO_FUNCTION_FOUND,
                    msg="no such function")
 #    def handle_function_request_merged(self, addr, request):
 #        """
 #        Parses the request and calls a member function corresponding to the request.

 #        Two possible formats for request are allowed:
 #            - 'a sample function': \
 #                    In this case, the method a_sample_function(addr) is called
 #            - 'a sample function: argument': \
 #                    In this case, the method a_sample_function(addr, argument) is called.
 #                    The argument is passed in as a string

 #        :param addr: address of node to whom a request/command is to be sent
 #        :type addr: Address

 #        :param request:
 #        :type request: str

 #        :raises: NetworkAPIError
 #        """
 #        function_found = False
	# splitted_status = False
 #        if ":" not in request:
 #            for f in self.function_list:
	# 	if splitted_status is not True:
	# 		splitted_request=request.split('_')
	# 		m_version=splitted_request[0]
	# 		new_request=splitted_request[1]
	# 		for i in range(2,len(splitted_request)):
	# 			new_request+="_"+splitted_request[i]
	# 		print m_version,"<-------version    new_request-->",new_request
	# 		request=new_request 

	# 		if new_request in self.command_meter_dict.keys():
	# 			if str(m_version) in self.command_meter_dict[new_request].keys():
	# 				update_request=self.command_meter_dict[new_request][str(m_version)]
	# 				print "updated_request",update_request
	# 			else:
	# 				return False
	# 		splitted_status=True
	# 		request=update_request 

 #                if f[0] == request.replace(" ", "_"):
 #                    function_found = True
 #                    # Pretty format result
 #                    #result = self.pp.pformat(f[1](addr))
 #                    result = str(f[1](Address(addr)))
 #                    try:
 #                        return result + " " + f[1].units
 #                    except AttributeError:
 #                        return result
 #            if function_found is False:
 #                raise NetworkAPIError(
 #                    error_code=NetworkAPIError.NO_FUNCTION_FOUND,
 #                    msg="no such function")
 #        else:
 #            f_str = request.split(":")[0]
 #            argument = ':'.join(request.split(":")[1:])
 #            function_found = False
	#     if splitted_status is not True:
	# 	splitted_request=f_str.split('_')
	# 	m_version=splitted_request[0]
	# 	new_request=splitted_request[1]
	# 	for i in range(2,len(splitted_request)):
	# 		new_request+="_"+splitted_request[i]
	# 	print m_version,"<-------version    set_request-->",new_request
	# 	request=new_request 
	# 	if new_request in self.command_meter_dict.keys():
	# 		if str(m_version) in self.command_meter_dict[new_request].keys():
	# 			update_request=self.command_meter_dict[new_request][str(m_version)]
	# 			print "updated_set request",update_request
	# 		else:
	# 			return False
	# 	splitted_status=True
	# 	f_str=update_request 
 #            for f in self.function_list:
 #                if f[0] == f_str.replace(" ", "_"):
 #                    function_found = True
	# 	    print "function found-->",f[0]
 #                    return str(f[1](addr, argument))
 #            if function_found is False:
 #                raise NetworkAPIError(
 #                    error_code=NetworkAPIError.NO_FUNCTION_FOUND,
 #                    msg="no such function")


# Simpleterm Get Param Functions

    @check_errors
    def meter_tap_to_dlms(self, addr):
        try:
            self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.TAP_TO_DLMS, INT32)
        except Exception as e:
            pass
        return "Command sent to meter"

    @check_errors
    def dongle_dlms_to_tap(self, addr):
        bytes = bytearray(
            [0xAA, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3])
        self.my_tap_handler.send_raw_bytes(bytes)
        return "Command sent to dongle!"

    @check_errors
    def meter_dlms_to_tap(self, addr):
        bytes = bytearray(
            [0x7E, 0xA0, 0x07, 0xBB, 0x41, 0x93, 0xDA, 0x28, 0x7E])
        self.my_tap_handler.send_raw_bytes(bytes)
        return "Command sent to meter"

    @check_errors
    def get_credit_limit(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CREDIT_LIMIT, INT32)
    get_credit_limit.units = 'credits'

    @check_errors
    def get_master_credits(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_MASTER_CREDITS, UINT32)

    @check_errors
    def get_network(self, addr):        
        buf = self.obj_rcCommandPacket.frame_get_rc_cmd(self.obj_rcCommandPacket.RC_GET_NETWORK)
        val = serialize.deserialize_uint32(buf)
        return self.my_simpleterm_master.set_and_get_rc_param(addr, commandMappingContainer_3P.GET_RC_CONFIG_3P, val, UINT32, UINT32_BE)

    @check_errors
    def get_channel(self, addr):
        buf = self.obj_rcCommandPacket.frame_get_rc_cmd(self.obj_rcCommandPacket.RC_GET_CHANNEL)
        val = serialize.deserialize_uint32(buf)
        return self.my_simpleterm_master.set_and_get_rc_param(addr, commandMappingContainer_3P.GET_RC_CONFIG_3P, val, UINT32, UINT32_BE)
    
    @check_errors
    def rf_mem_read(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        length = int(args[1])
        payload = bytearray()
        payload.extend(serialize.serialize_uint8(start_address))
        payload.extend(serialize.serialize_uint8(length))
        payload = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer_3P.GET_RC_CONFIG_3P,
                                                            payload, BYTE_ARRAY,BYTE_ARRAY)
        print ([hex(f) for f in payload])
        return None

    @check_errors
    def get_rf_version(self, addr):
        start_address = 60
        length = 9
        payload = bytearray()
        payload.extend(serialize.serialize_uint8(start_address))
        payload.extend(serialize.serialize_uint8(length))
        payload = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer_3P.GET_RC_CONFIG_3P,
                                                            payload, BYTE_ARRAY,BYTE_ARRAY)
        print ([chr(f) for f in payload])
        return None

    @check_errors
    def get_rf_power(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_RF_POWER, INT8)


    # @check_errors
    # def get_voltage(self, addr):
    #     return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_VOLTAGE, INT32)/1000.0
    # get_voltage.units = 'volts'

    # @check_errors
    # def get_current(self, addr):
    #     return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_CURRENT, INT32)/1000.0
    # get_current.units = 'amps'

    @check_errors
    def get_live_tampers(self, addr):
        liveTamper = ['OVERVOLTAGE','LOWVOLTAGE','R_PHASE_MISSING','Y_PHASE_MISSING',
                      'B_PHASE_MISSING','VOLTAGE_UNBALANCE','PHASE_REVERSE','R_CUR_REVERSE',
                      'Y_CUR_REVERSE','B_CUR_REVERSE','CURRENT_UNBALANCE','CT_BYPASS',
                      'R_CTOPEN','Y_CTOPEN','B_CTOPEN','OVERCURRENT','HIGH_N_CURRENT','MAGNET',
                      'NDIST','LOWPF','COPEN','OVERLOAD','LOW_BALANCE','PLUG_OUT_COMM_MODULE',
                      'FREQ_MALF']
        reply = []
        flag_byte = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_LIVE_TAMPERS, UINT32)

        for i in range(len(liveTamper)):
            if(flag_byte & (1<<i)):
                reply.append(liveTamper[i])
        return reply

    @check_errors
    def get_int_version(self, addr):
        version = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_INT_VERSION, UINT32)
        return version

    @check_errors
    def get_cumulative_tamper_count(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CUMULATIVE_TAMPER_COUNT, UINT32)

    # Gurux related Commands
    @check_errors
    def get_extended_registers(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_EXTENDED_REGISTERS, INSTANT_PROFILE)
        
    @check_errors
    def md_reset(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.MD_RESET)
        
    # Command related to Activity Calender    
    @check_errors
    def set_tod_day_profile(self, addr, args):
        tod = TodConfigurationPacket()
        i = 0 
        #1,8,200,360,540,720,900,1080,1260,1380,1,2,3,4,5,6,7,8
        
        var = args.split(",")
        tod.day_profile.dayId     = int(var[0])    
        tod.day_profile.numberOfTOD = int(var[1])
        
        for j in range(tod.day_profile.numberOfTOD):
            tod.day_profile.timeStamp[j] = int(var[i + 2])
            tod.day_profile.tarrif[j] = int(var[i + 2 + (tod.day_profile.numberOfTOD)])
            print(tod.day_profile.timeStamp[j])
            if (tod.day_profile.tarrif[j] > 8):
                tod.day_profile.tarrif[j] = 8
                print("Tariff Value Should between 1 to 8")
            i+=1
            
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer_3P.SET_TOD_DAY_PROFILE, tod.day_profile, TOD_CONFIGURATION_PACKET)
    
    @check_errors
    def set_tod_week_profile(self, addr, args):
        tod = TodConfigurationPacket()
        i = 0 
        # Extract values
        var = args.split(",")
        tod.week_profile.weekNum = int(var[0]) 
        tod.week_profile.weekLen = int(var[1])
        tod.week_profile.weekName = var[2]
        print (tod.week_profile.weekName)
        
        for i in range(7):
            tod.week_profile.weekDaysId[i] = int(var[3+i])
        
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer_3P.SET_TOD_WEEK_PROFILE, tod.week_profile, TOD_CONFIGURATION_PACKET)
  
    @check_errors
    def set_tod_season_profile(self, addr, args):
        tod = TodConfigurationPacket()
        i = 0 
        # Extract values
        var = args.split(",")
        tod.season_profile.seasonNum = int(var[0])
        tod.season_profile.seasonLen = int(var[1])
        tod.season_profile.seasonName = var[2]
        tod.season_profile.seasonStartTS = int(var[3])
        tod.season_profile.weekLen = int(var[4])
        tod.season_profile.weekName = var[5]
        
        print (tod.season_profile.seasonStartTS)
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer_3P.SET_TOD_SEASON_PROFILE, tod.season_profile, TOD_CONFIGURATION_PACKET)
  
    @check_errors
    def get_passive_calender(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_PASSIVE_CALENDER, TOD_CONFIGURATION_PACKET)
        
    @check_errors
    def get_active_calender(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_ACTIVE_CALENDER, TOD_CONFIGURATION_PACKET)
    
    # TAMPER Related Configuration by Rahul
   
    @check_errors
    def get_event_ptime(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer.GET_EVENT_PTIME, EVENTS_PTIME)
    @check_errors
    def set_event_ptime(self, addr, args):
        byte_array = bytearray()
        for i in range(0,24):
            byte_array.extend(serialize.serialize_uint16((int(args.split(',')[i])),"reverse"))

        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_EVENT_PTIME, byte_array, BYTE_ARRAY)
    
    @check_errors
    def get_tampers_threshold(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_TAMPERS_THRESHOLD, TAMPERS_THRESHOLD_PACKET)
        
    @check_errors
    def set_tampers_threshold(self, addr, args):
        byte_array = bytearray()
    
        # Split arguments and determine length
        arg_values = args.split(',')
        arg_length = len(arg_values)

        print (arg_length)
        
        # Validate acceptable lengths
        if arg_length not in [25, 30]:
            raise ValueError("Unexpected number of arguments")

        # Loop over available values and serialize accordingly
        for i in range(arg_length):
            byte_array.extend(serialize.serialize_uint8(int(arg_values[i])))

        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer_3P.SET_TAMPERS_THRESHOLD, byte_array, BYTE_ARRAY)

    # @check_errors
    # def set_tampers_threshold(self, addr, args):
    #     byte_array = bytearray()
    #     for i in range(0,24):
    #         byte_array.extend(serialize.serialize_uint8(int(args.split(',')[i])))

    #     return self.my_simpleterm_master.set_param(addr, commandMappingContainer_3P.SET_TAMPERS_THRESHOLD, byte_array, BYTE_ARRAY)
        
    @check_errors
    def get_credits(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CREDITS, INT32)
    get_credits.units = 'credits'

    #=================================================================================
    @check_errors
    def get_net_account(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NET_ACCOUNT, INT32)
    #=================================================================================
    @check_errors
    def get_net_recharge(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NET_RECHARGE, INT32)
    get_credits.units = 'credits'

    @check_errors
    def get_pos_recharge(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_POS_RECHARGE, UINT32)
    get_credits.units = 'credits'

    @check_errors
    def get_neg_recharge(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NEG_RECHARGE, UINT32)
    get_credits.units = 'credits'

    @check_errors
    def get_power_limit(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_POWER_LIMIT, UINT32)
    get_power_limit.units = 'watts'

    @check_errors
    def get_Dgpower_limit(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_DG_POWER_LIMIT, UINT32)
    get_Dgpower_limit.units = 'watts'
    
    @check_errors
    def get_time_left(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_TIME_LEFT, INT32)  
    get_time_left.units = 'hours'

    @check_errors
    def get_energy_limit(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_ENERGY_LIMIT, INT32)
    get_energy_limit.units = 'watt-hour'

    @check_errors
    def get_energy_consumed_today(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_ENERGY_CONSUMED_TODAY, INT32)
    get_energy_consumed_today.units = 'watt-hour'

    @check_errors
    def get_price(self, addr):
        e_per_credit = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_ENERGY_PER_CREDIT, UINT32)
        credit_per_kwh = round(float(3600.00 * 1000.00 / e_per_credit), 2)
        return credit_per_kwh
    get_price.units = 'credits/kwh'

    @check_errors
    def get_address(self, addr):
        addr_int = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_ADDRESS, UINT32)
        # addr1 = addr_int / (2**24)
        # addr_int = addr_int - addr1 * (2**24)
        # addr2 = addr_int / 2**16
        # addr_int = addr_int - addr2 * (2**16)
        # addr3 = addr_int / 2**8
        # addr_int = addr_int - addr3 * (2**8)
        # addr4 = addr_int
        addr1 = (addr_int >> 24) & 0xFF
        addr2 = (addr_int >> 16) & 0xFF
        addr3 = (addr_int >> 8) & 0xFF
        addr4 = addr_int & 0xFF
        addr_str = str(addr1) + "." + str(addr2) + "." + \
            str(addr3) + "." + str(addr4)
        address = Address(addr_str)
        return address

    @check_errors
    def get_tamper_record(self, addr, tamper_type):
        tamper_type = tamper_type.strip(' ')
        if tamper_type == "all":
            earth_record = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_EARTH_TAMPER_RECORD, TAMPER_RECORD_PACKET)
            rev_record = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_REV_TAMPER_RECORD, TAMPER_RECORD_PACKET)
            nm_record = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_NM_TAMPER_RECORD, TAMPER_RECORD_PACKET)
            nd_record = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ND_TAMPER_RECORD, TAMPER_RECORD_PACKET)
            cover_record = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_COVER_TAMPER_RECORD, TAMPER_RECORD_PACKET)
            mag_record = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_MAG_TAMPER_RECORD, TAMPER_RECORD_PACKET)
            report = "{}\n{}\n{}\n{}\n{}\n{}\n".format(earth_record,
                                                       rev_record,
                                                       nm_record,
                                                       nd_record,
                                                       cover_record,
                                                       mag_record)
            return report
        elif tamper_type == "earth":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_EARTH_TAMPER_RECORD, TAMPER_RECORD_PACKET)
        elif tamper_type == "rev":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_REV_TAMPER_RECORD, TAMPER_RECORD_PACKET)
        elif tamper_type == "nm":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_NM_TAMPER_RECORD, TAMPER_RECORD_PACKET)
        elif tamper_type == "nd":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ND_TAMPER_RECORD, TAMPER_RECORD_PACKET)
        elif tamper_type == "cover":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_COVER_TAMPER_RECORD, TAMPER_RECORD_PACKET)
        elif tamper_type == "mag":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_MAG_TAMPER_RECORD, TAMPER_RECORD_PACKET)

    @check_errors
    def get_dd_params(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_DD_PARAMS, DAILY_DEDUCTION_PARAMS)

    @check_errors
    def get_block_load_profile_params(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_BLOCK_LOAD_PROFILE_PARAMS, LOAD_SURVEY_PARAMS)

    @check_errors
    def get_time(self, addr):
        time = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_TIME, UINT32)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def get_factory_time(self, addr):
        time = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer_3P.GET_LAST_FACTORY_TIME, UINT32)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def get_timeformat(self, addr, cal_time):
        time = int(cal_time)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def get_ref_time(self, addr):
        time = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_REF_TIME, UINT32)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def get_last_poweroff_time(self, addr):
        time = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_POWERDOWN_TIME, UINT32)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def set_ref_time(self, addr, cal_time):
        if cal_time == "":
            cal_time = 0
        elif cal_time == "now":
            cal_time = datetime.datetime.now()
        else:
            try:
                time_str = cal_time.split(' ')[1]
                if len(time_str) == 6:
                    time_str = time_str[0] + time_str[1] + ":" + time_str[2] + time_str[3] + ":" +time_str[4] + time_str[5]
                    cal_time = cal_time.split(' ')[0] + " " + time_str
                cal_time = datetime.datetime.strptime(cal_time, "%Y-%m-%d %H:%M:%S")
            except:
                return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = int((cal_time - unix_time_zero).total_seconds())
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_REF_TIME,
                                                   seconds_since_epoch, UINT32)

    @check_errors
    def set_last_poweroff_time(self, addr, cal_time):
        if cal_time == "":
            cal_time = 0
        elif cal_time == "now":
            cal_time = datetime.datetime.now()
        else:
            try:
                time_str = cal_time.split(' ')[1]
                if len(time_str) == 6:
                    time_str = time_str[0] + time_str[1] + ":" + time_str[2] + time_str[3] + ":" +time_str[4] + time_str[5]
                    cal_time = cal_time.split(' ')[0] + " " + time_str
                cal_time = datetime.datetime.strptime(cal_time, "%Y-%m-%d %H:%M:%S")
            except:
                return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = int((cal_time - unix_time_zero).total_seconds())
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_POWERDOWN_TIME,
                                                   seconds_since_epoch, UINT32)

    @check_errors
    def get_hw_version(self, addr):
        version = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_HW_VERSION, INT8)
        if(version == 0):
            return "3PH-V-T1.0 PCB"
        elif (version == 1):
            return "3PH-V-T1.1 PCB"
        elif (version == 2):
            return "3PH-V-P1.0 PCB"
        elif (version == 3):
            return "3PH-I-P2.0 PCB"
        elif (version == 4):
            return "3PH-CAPITAL_POWER"
        else:
            return "unknown"

    @check_errors
    def get_health_status(self, addr):
        version = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_HEALTH_STATUS, UINT32)
        health_mask=[]
        error_mask=[
        "BILL PARAMS NVM ERROR" ,
        "BILL HISTORY NVM ERROR" ,
        "DLMS IMG NVM ERROR"  ,
        "DLMS MISC NVM ERROR" ,
        "BLP NVM ERROR" ,
        "DLP NVM ERROR" ,
        "PWRLIM NVM ERROR" ,
        "RLY GP PARAMS NVM ERROR" ,
        "EVENT CURRENT NVM ERROR" ,
        "EVENT VOLTAGE NVM ERROR" ,
        "EVENT POWER NVM ERROR" ,
        "EVENT TRANS. NVM ERROR" ,
        "EVENT NON ROLLOVER NVM ERROR" ,
        "EVENT CONTROL NVM ERROR" ,
        "EVENT OTHER NVM ERROR" ,
        "EVENT MISC NVM ERROR" ,
        "TARIFF NVM ERROR" ,
        "PREPAID NVM ERROR" ,
        "RECHARGE TOKEN NVM ERROR" ,
        "RLY DLMS NVM ERROR" ,
        "RTC DATETIME ERROR" ,
        "TOD PARAMS NVM ERROR",
        "EVENT PTIME NVM ERROR",
        "GP RF LOG NVM ERROR",
        "ASSIGN-DEASSIGN LOG NVM ERROR",
        "PREPAID ENERGY LOG ERROR",
        "TOD_EXP_LOG_ERR_MASK",
        "BILL_HIST_TOD_PARAMS_ERR_MASK" ,
        "BILL_HIST_TOD_EXP_LOG_ERR_MASK",
		"GSM_PROFILE_ERR_MASK",
        ]

        if(version == 0):
            return "OK"
        else:
            for i in range(len(error_mask)):
                if (0 != version&(1<<i)):
                    health_mask.append(error_mask[i])
            return health_mask        
        
    @check_errors
    def get_self_diagnostic(self, addr):
        diagnostic = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_SELF_DIAGNOSTIC, UINT8)

        health_mask = []
        MEMORY_OK_MASK   = 0x04
        BATTERY_OK_MASK  = 0x02
        RTC_OK_MASK      = 0x01

        if (diagnostic & RTC_OK_MASK):
            health_mask.append("RTC_PASS")
        else:
            health_mask.append("RTC_FAIL")

        if (diagnostic & BATTERY_OK_MASK):
            health_mask.append("BATTERY_PASS")
        else:
            health_mask.append("BATTERY_FAIL")

        if (diagnostic & MEMORY_OK_MASK):
            health_mask.append("MEMORY_PASS")
        else:
            health_mask.append("MEMORY_FAIL")

        return health_mask

    @check_errors
    def get_live_version(self, addr):
        version = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_LIVE_VERSION, UINT32)
        return version
    

    @check_errors
    def get_ext_version(self, addr):
        version = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_EXT_VERSION, UINT32)
        return version

    @check_errors
    def get_newest_block_load_profile(self, addr):
        if self.get_num_block_load_profile(addr) == 0:
            return "No block load profiles have been stored!"
        else:
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_NEWEST_BLOCK_LOAD_PROFILE, BUNDLE)

    @check_errors
    def get_newest_daily_load_profile(self, addr):
        if self.get_num_daily_load_profile(addr) == 0:
            return "No daily load profiles have been stored!"
        else:
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_NEWEST_DAILY_LOAD_PROFILE,
                DAILY_LOAD_PROFILE_PACKET)

    @check_errors
    def get_oldest_block_load_profile(self, addr):
        if self.get_num_block_load_profile(addr) == 0:
            return "No block load profiles have been stored!"
        else:
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_OLDEST_BLOCK_LOAD_PROFILE, BUNDLE)

    @check_errors
    def get_oldest_daily_load_profile(self, addr):
        if self.get_num_daily_load_profile(addr) == 0:
            return "No daily load profiles have been stored!"
        else:
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_OLDEST_DAILY_LOAD_PROFILE,
                DAILY_LOAD_PROFILE_PACKET)

    @check_errors
    def get_block_load_profile_by_index(self, addr, index):
        index = int(index)
        if index < 0 or index > 21845:
            return "Invalid index! Index should be in the range of 0 to 21845!"
        else:
            return self.my_simpleterm_master.set_and_get_param(
                addr,
                commandMappingContainer.GET_BLOCK_LOAD_PROFILE_BY_INDEX,
                index,
                UINT32,
                BUNDLE,
                8640)

    @check_errors
    def get_block_load_profile_by_index1(self, addr, index):
        index = int(index)
        if index < 0 or index > 21845:
            return "Invalid index! Index should be in the range of 0 to 21845!"
        else:
            return self.my_simpleterm_master.set_and_get_param(
                addr,
                commandMappingContainer_3P.GET_BLOCK_LOAD_ENE_PROFILE_BY_INDEX,
                index,
                UINT32,
                BUNDLE,
                8640)

    @check_errors
    def get_daily_load_profile_by_index(self, addr, index):
        index = int(index)
        if index < 0 or index > 20480:
            return "Invalid index! Index should be in the range of 0 to 20480!"
        else:
            return self.my_simpleterm_master.set_and_get_param(
                addr,
                commandMappingContainer.GET_DAILY_LOAD_PROFILE_BY_INDEX,
                index,
                UINT32,
                DAILY_LOAD_PROFILE_PACKET,
                180)
        
    # Rahul Block and Daily Load
    @check_errors
    def get_block_load_profile_by_datetime(self, addr, line):
        cal_time = 0
        index = 0
        time_str = 0
        date_str = 0
        if line == "":
            return "get_block_load_profile_by_datetime : Enter datetime, no_of_entry"
        else:
            try:
                cal_time = line.split(',')[0]
                index = int(line.split(',')[1])
                time_str = cal_time.split(' ')[1]
                date_str = cal_time.split(' ')[0]
            except:
                try:
                    time_str = line.split(' ')[1]
                    date_str = line.split(' ')[0]
                except:
                    return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        if len(time_str) != 6 or len(date_str) != 10:
            return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        time_str = time_str[0] + time_str[1] + ":" + time_str[2] + time_str[3] + ":" +time_str[4] + time_str[5]
        cal_time = date_str + " " + time_str
        cal_time = datetime.datetime.strptime(cal_time, "%Y-%m-%d %H:%M:%S")
        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = int((cal_time - unix_time_zero).total_seconds())
        byte_array = bytearray()
        byte_array.extend(serialize.serialize_uint32(index))
        byte_array.extend(serialize.serialize_uint32(seconds_since_epoch))
        if index < 0 or index > 21845:
            return "Invalid index! Index should be in the range of 0 to 21845!"
        else:
            return self.my_simpleterm_master.set_and_get_param(
                addr,
                commandMappingContainer_3P.GET_BLOCK_LOAD_ENE_PROFILE_BY_INDEX,
                byte_array,
                BYTE_ARRAY,
                BUNDLE)
                # self.get_num_block_load_profile(addr))

    @check_errors
    def get_daily_load_profile_by_index(self, addr, index):
        index = int(index)
        if index < 0 or index > 20480:
            return "Invalid index! Index should be in the range of 0 to 20480!"
        else:
            return self.my_simpleterm_master.set_and_get_param(
                addr,
                commandMappingContainer.GET_DAILY_LOAD_PROFILE_BY_INDEX,
                index,
                UINT32,
                DAILY_LOAD_PROFILE_PACKET,
                self.get_num_daily_load_profile(addr))

    @check_errors
    def get_daily_load_profile_by_datetime(self, addr, line):
        cal_time = 0
        index = 0
        time_str = 0
        date_str = 0

        if line == "":
            return "get_daily_load_profile_by_datetime : Enter datetime, no_of_entry"
        else:
            try:
                cal_time = line.split(',')[0]
                index = int(line.split(',')[1])
                time_str = cal_time.split(' ')[1]
                date_str = cal_time.split(' ')[0]
            except:
                try:
                    time_str = line.split(' ')[1]
                    date_str = line.split(' ')[0]
                except:
                    return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        if len(time_str) != 6 or len(date_str) != 10:
            return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        time_str = time_str[0] + time_str[1] + ":" + time_str[2] + time_str[3] + ":" +time_str[4] + time_str[5]
        cal_time = date_str + " " + time_str
        cal_time = datetime.datetime.strptime(cal_time, "%Y-%m-%d %H:%M:%S")
        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = int((cal_time - unix_time_zero).total_seconds())
        byte_array = bytearray()
        byte_array.extend(serialize.serialize_uint32(index))
        byte_array.extend(serialize.serialize_uint32(seconds_since_epoch))
        if index < 0 or index > 21845:
            return "Invalid index! Index should be in the range of 0 to 21845!"
        else:
            return self.my_simpleterm_master.set_and_get_param(
                addr,
                commandMappingContainer.GET_DAILY_LOAD_PROFILE_BY_INDEX,
                byte_array,
                BYTE_ARRAY,
                DAILY_LOAD_PROFILE_PACKET,
                self.get_num_daily_load_profile(addr))
    @check_errors
    def get_num_block_load_profile(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_BLOCK_LOAD_PROFILE, UINT32)
    @check_errors
    def get_num_instant_data_profile(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_INSTANT_PROFILE, UINT32)

    @check_errors
    def get_num_block_load_profile_datetime(self, addr, line):
        if line == "":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_NUM_BLOCK_LOAD_PROFILE, UINT32)
        cal_time1 = 0
        time_str1 = 0
        date_str1 = 0
        cal_time2 = 0
        time_str2 = 0
        date_str2 = 0
        try:
            cal_time1 = line.split(',')[0]
            cal_time2 = line.split(',')[1]
        except:
            return "Enter datetime1, datetime2 in YYYY-MM-DD HH:MM:SS format"
        else:
            try:
                time_str1 = cal_time1.split(' ')[1]
                date_str1 = cal_time1.split(' ')[0]
                time_str2 = cal_time2.split(' ')[1]
                date_str2 = cal_time2.split(' ')[0]
            except:
                return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        if (len(time_str1) != 6 or len(date_str1) != 10) or (len(time_str2) != 6 or len(date_str2) != 10):
            return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        year  = (int(date_str1[0])*1000)+(int(date_str1[1])*100)+(int(date_str1[2])*10)+int(date_str1[3])
        year1 = year/256
        year2 = year%256
        month = (int(date_str1[5])*10)+int(date_str1[6])
        day   = (int(date_str1[8])*10)+int(date_str1[9])
        hour  = (int(time_str1[0])*10)+int(time_str1[1])
        minute= (int(time_str1[2])*10)+int(time_str1[3])
        second= (int(time_str1[4])*10)+int(time_str1[5])

        byte_array = bytearray()
        byte_array.extend(serialize.serialize_uint8(year1))
        byte_array.extend(serialize.serialize_uint8(year2))
        byte_array.extend(serialize.serialize_uint8(month))
        byte_array.extend(serialize.serialize_uint8(day))
        byte_array.extend(serialize.serialize_uint8(0x00))
        byte_array.extend(serialize.serialize_uint8(hour))
        byte_array.extend(serialize.serialize_uint8(minute))
        byte_array.extend(serialize.serialize_uint8(second))

        year  = (int(date_str2[0])*1000)+(int(date_str2[1])*100)+(int(date_str2[2])*10)+int(date_str2[3])
        year1 = year/256
        year2 = year%256
        month = (int(date_str2[5])*10)+int(date_str2[6])
        day   = (int(date_str2[8])*10)+int(date_str2[9])
        hour  = (int(time_str2[0])*10)+int(time_str2[1])
        minute= (int(time_str2[2])*10)+int(time_str2[3])
        second= (int(time_str2[4])*10)+int(time_str2[5])

        byte_array.extend(serialize.serialize_uint8(year1))
        byte_array.extend(serialize.serialize_uint8(year2))
        byte_array.extend(serialize.serialize_uint8(month))
        byte_array.extend(serialize.serialize_uint8(day))
        byte_array.extend(serialize.serialize_uint8(0x00))
        byte_array.extend(serialize.serialize_uint8(hour))
        byte_array.extend(serialize.serialize_uint8(minute))
        byte_array.extend(serialize.serialize_uint8(second))
        return self.my_simpleterm_master.set_and_get_param(
            addr, commandMappingContainer.GET_NUM_BLOCK_LOAD_BY_DATETIME, byte_array, BYTE_ARRAY, UINT32)

    @check_errors
    def get_num_daily_load_profile(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_DAILY_LOAD_PROFILE, UINT32)

    @check_errors
    def get_newest_log(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NEWEST_LOG, LOG_PACKET)

    @check_errors
    def get_oldest_log(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_OLDEST_LOG, LOG_PACKET)

    @check_errors
    def get_num_logs(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_LOGS, UINT32)

    @check_errors
    def get_block_load_profile_interval(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_BLOCK_LOAD_PROFILE_INTERVAL, INT8)
    get_block_load_profile_interval.units = "minutes"

    @check_errors
    def get_accurate_credits(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_ACCURATE_CREDITS, PREPAID_ACCOUNT_PACKET)

    @check_errors
    def get_accounting_state(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_ACTIVE_SLAB_INFO, ACCOUNTING_STATE_PACKET)

    @check_errors
    def get_slab_update_ts(self, addr):
        update_ts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_SLAB_UPDATE_TS, UINT32)
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=update_ts)

    @check_errors
    def get_fd_update_ts(self, addr):
        update_ts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_FD_UPDATE_TS, UINT32)
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=update_ts)

    @check_errors
    def get_active_fd_params(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_ACTIVE_FD_PARAMS, FIXED_DEDUCTION_PACKET)

    @check_errors
    def get_unlock_validity(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_UNLOCK_VALIDITY, UINT32) / (3600 * 24)
    get_unlock_validity.units = "days"

    @check_errors
    def get_time_since_unlock(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_TIME_SINCE_UNLOCK, UINT32) / (3600 * 24)
    get_time_since_unlock.units = "days"

    @check_errors
    def get_last_unlock_timestamp(self, addr):
        time = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_UNLOCK_TIMESTAMP, UINT32)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def get_active_energy_offset(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_ACTIVE_ENERGY_OFFSET, INT32)
    get_active_energy_offset.units = "watt-hour"

    @check_errors
    def get_reactive_energy_offset(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_REACTIVE_ENERGY_OFFSET, INT32)
    get_reactive_energy_offset.units = "volt-ampere-reactive-hour"

    @check_errors
    def get_apparent_energy_offset(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_APPARENT_ENERGY_OFFSET, INT32)
    get_apparent_energy_offset.units = "volt-ampere-hour"

    @check_errors
    def get_digital_input_status(self, addr):
        distatus = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_DI_STATUS, UINT8)
        binary_num = bin(distatus)[2:]
        return binary_num


# Simpleterm Set Param Functions

    @check_errors
    def set_credit_limit(self, addr, credit_limit):
        credit_limit = int(credit_limit)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_CREDIT_LIMIT, credit_limit, INT32)

    @check_errors
    def set_master_credits(self, addr, amount):
        amount = int(amount)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_MASTER_CREDITS, amount, UINT32)

    # @check_errors
    # def set_address(self, addr, address):
    #     address = Address(str(address))
    #     addr_str_list = str(address).split('.')
    #     addr_int = int(addr_str_list[3])
    #     addr_int += int(addr_str_list[2])*(2**8)
    #     addr_int += int(addr_str_list[1])*(2**16)
    #     addr_int += int(addr_str_list[0])*(2**24)
    #     return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_ADDRESS, addr_int, UINT32)
# to do: need to have different command nuber for 1p_3p_meter
# 3p is being used as chaning the command nuber will require the firmware change.
    @check_errors
    def set_address(self, addr, address):
        address = Address(str(address))
        addr_str_list = str(address).split('.')
        addr_int = int(addr_str_list[3])
        addr_int += int(addr_str_list[2])*(2**8)
        addr_int += int(addr_str_list[1])*(2**16)
        addr_int += int(addr_str_list[0])*(2**24)
        byte_array = bytearray()
        byte_array = serialize.serialize_uint32(addr_int,order="reverse")
        buf = self.obj_rcCommandPacket.frame_set_rc_mem_read_cmd(self.obj_rcCommandPacket.RC_SET_ADDRESS,byte_array)
        return self.my_simpleterm_master.set_rc_param(addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)



    @check_errors
    def set_channel(self, addr, channel):
        channel = int(channel)
        if channel > 16 or channel < 0:
            return "Invalid channel! Channel must be in the range of 0-16."
        else:
            channel_byte_array = bytearray()
            channel_byte_array = serialize.serialize_uint32(channel,order="reverse")
            buf = self.obj_rcCommandPacket.frame_set_rc_mem_read_cmd(self.obj_rcCommandPacket.RC_SET_CHANNEL,channel_byte_array)
            return self.my_simpleterm_master.set_rc_param(addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)



    @check_errors
    def set_rf_power(self, addr, rf_power):
        rf_power = int(rf_power)
        if rf_power > 5 or rf_power < 1:
            return "Invalid value! RF Power must be in the range of 1-5."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_RF_POWER, rf_power, INT8)

    @check_errors
    def set_network(self, addr, network):
        network = int(network)
        if network <= 0:
            print ("Invalid Network ID")
        network_byte_array = bytearray()
        network_byte_array = serialize.serialize_uint32(network,order="reverse")
        buf = self.obj_rcCommandPacket.frame_set_rc_mem_read_cmd(self.obj_rcCommandPacket.RC_SET_NETWORK,network_byte_array)
        return self.my_simpleterm_master.set_rc_param(addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)

    

    @check_errors
    def set_rc_buffer_margin(self, addr, rc_buffer_margin):
        rc_buffer_margin = int(rc_buffer_margin)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_RC_BUFFER_MARGIN, rc_buffer_margin, UINT32)

    @check_errors
    def set_rc_timeout(self, addr, rc_timeout):
        rc_timeout = int(rc_timeout)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_RC_TIMEOUT, rc_timeout, UINT32)

    @check_errors
    def set_power_limit(self, addr, power_limit):
        power_limit = int(power_limit)
        if power_limit < 1 or power_limit > 4294967:
            return "Invalid value! Power limit should be in the range of 1 to 4294967."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_POWER_LIMIT, power_limit, UINT32)

    @check_errors
    def set_Dgpower_limit(self, addr, power_limit):
        power_limit = int(power_limit)
        if power_limit < 1 or power_limit > 4294967:
            return "Invalid value! Power limit should be in the range of 1 to 4294967."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_DG_POWER_LIMIT, power_limit, UINT32)

    @check_errors
    def set_lockdown_period(self, addr, period):
        period = int(period)
        if period < 1 or period > 4294967:
            return "Invalid value! lock down period should be in the range of 1 to 4294967."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_LOCK_DOWN_PERIOD, period, UINT16)

    @check_errors
    def reset_lockdown_period(self, addr):
        return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_DEFAULT_LOCK_DOWN_PERIOD, 1800, UINT16)

    @check_errors
    def get_lockdown_period(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_LOCK_DOWN_PERIOD, UINT16)
    get_lockdown_period.units = 'seconds'

    @check_errors
    def enable_power_limiter(self, addr):
        return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_POWER_LIMITER_STATUS, 0x55, INT8)   

    @check_errors
    def disable_power_limiter(self, addr):
        return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_POWER_LIMITER_STATUS, 0, INT8)

    @check_errors
    def set_power_limit_on_time(self, addr, period):
        period = int(period)
        if period < 360:
            return "Invalid value! On time should be greater than 360."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_POWER_LIMITER_ON_TIME, period, UINT16) 

    @check_errors
    def set_power_limit_off_time(self, addr, period):
        period = int(period)
        if period < 30:
            return "Invalid value! off time should be greater than 360."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_POWER_LIMITER_OFF_TIME, period, UINT16) 

    @check_errors
    def get_power_limit_on_time(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_POWER_LIMITER_ON_TIME, UINT16)
    get_power_limit_on_time.units = 'seconds' 

    @check_errors
    def get_power_limit_off_time(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_POWER_LIMITER_OFF_TIME, UINT16)
    get_power_limit_off_time.units = 'seconds'

    @check_errors
    def set_manufaturing_year(self, addr, year):
        year = int(year)
        if year > 2000 and year < 2100:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_MANUFACTURING_YEAR, year, UINT16)
        else:
            return "Invalid value! On Year should be in the range of 2000 to 2100." 

    @check_errors
    def get_manufaturing_year(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_MANUFACTURING_YEAR, UINT16)

    @check_errors
    def power_limit_status(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_POWER_LIMITER_STATUS, INT8)
        if(sts):
            return "Enable"
        else:
            return "Disable"    

    @check_errors
    def set_nm_control_status(self, addr, period):
        if period == "":
            period = 1
        period = int(period)
        if period != 0:
            period = 0x77
        return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_NM_CONTROL, period, INT8) 

    @check_errors
    def get_nm_control_status(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NM_CONTROL, INT8)
        if(sts == 0x77):
            return "Enable"
        else:
            return "Disable" 

    @check_errors
    def set_metering_mode(self, addr, mode):
        mode = int(mode)
        if mode < 0 or mode > 1:
            print ("Warning : Enter 1 for net metering or 0 for forward only !!!")
        else:   
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_METERING_MODE, mode, INT8) 
    @check_errors
    def set_meter_type(self, addr, mode):
        mode = int(mode)
        if mode < 0 or mode > 2:
            print ("Warning : Eneter 2 for Current Rating (10-100)A or Enter 1 for current rating (10-60)A or 0 for current rating (20-100)A !!!")
        else:   
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_METER_TYPE, mode, INT8) 

    @check_errors
    def set_ct_ratio(self, addr, mode):
        mode = int(mode)
        if mode < 1 or mode > 120:
            print ("Warning : Enter ct ratio between 1 to 120!!!")
        else:   
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.set_ct_ratio, mode, UINT8) 
        
    @check_errors
    def set_apprent_led(self, addr, data):
        print (data)
        if data == "":
            return "0xBB:  Swap apprent LED."
        elif data == "0xBB":
            data = 0xBB
        elif data == "0xAA":
            data = 0xAA
        else:
            data = int(data)    
        return self.my_simpleterm_master.set_param(
                    addr, commandMappingContainer.SWAP_APPRENT_LED, data,UINT8)     

    @check_errors
    def set_metering_load(self, addr, mode):
        mode = int(mode)
        if mode < 0 or mode > 1:
            print ("Warning : Enter 1 for lag-lead mode or 0 for lag only mode !!!")
        else:   
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_METERING_LOAD, mode, INT8) 

    @check_errors
    def get_rtc_ppm(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_TEMPERATURE_PPM, BYTE_ARRAY)

    @check_errors
    def set_ppm_rtc(self, addr,line):
        arg = line.split(",")
        ppm = int(arg[0])
        temperature = int(arg[1])
        bytearray_array = bytearray()
        bytearray_array.extend(serialize.serialize_uint32(ppm))
        bytearray_array.extend(serialize.serialize_int32(temperature))
        return  self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_TEMPERATURE_PPM,bytearray_array,BYTE_ARRAY)

    @check_errors
    def calib_3p_phase_start(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.PH_CALIB_INIT_CALIB_RESET)

    @check_errors
    def calib_3p_phase_fu_start(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.PH_CALIB_FU_INIT)

    @check_errors
    def calib_3p_phase_fl_start(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.PH_CALIB_FL_INIT)

    @check_errors
    def calib_3p_neu_start(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.NE_CALIB_INIT)

    @check_errors
    def set_debug_print(self, addr, period):
        print (period)
        if period == "":
            return "0xAB: for Enable Debug Print.\n0xBA: for Enable GPRS Debug"
        elif period == "0xAB":
            period = 0xAB
        elif period == "0xBB":
            period = 0xBB
        elif period == "0xBA":
            period = 0xBA
        else:
            period = int(period)
        return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_DEBUG_PRINT, period, UINT8) 

    @check_errors
    def get_debug_print(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_DEBUG_PRINT, UINT8)
        if(sts==0xAB):
            return "Enable Debug Print"
        elif(sts==0xBA):
            return "Enable GPRS Debug"
        else:
            return "Disable"

    @check_errors
    def get_gprs_health_status(self, addr):
        status = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GPRS_HEALTH_STATUS, BYTE_ARRAY)

        # simSlotNum = status[0]
        if   status[0] == 0xFF:
            return "NO comm with module"
        elif status[0] == 0x0F:
            print ("-- Gprs module detected")
        if   status[0] == 0:
            return "-- NO Serial number assigned to meter"
        elif status[0] == 3:
            return "-- Single SIM module"
        else:
            print ("-- SIM Detect ",status[0])

        # signalStrength = status[1]
        if   status[1] == 0xFF:
            return "-- No SIM Card"
        elif status[1] == 99:
            return "-- No Signal Network Available"
        elif status[1] < 2:
            print ("-- Signal Strength is Poor : ", status[1])
        elif status[1] < 10:
            print ("-- Signal Strength is Marginal : ", status[1])
        elif status[1] < 15:
            print ("-- Signal Strength is OK : ", status[1])
        elif status[1] < 20:
            print ("-- Signal Strength is Good : ", status[1])
        else:
            print ("-- Signal Strength is Excellent : ", status[1])

        # networkConn = status[2]
        if   status[2] == 0:
            return "-- No Network Registered, No searching for operator"
        elif status[2] == 1:
            print ("-- Network Registerd to home network")
        elif status[2] == 2:
            return "-- No Network Registered, Searching for operator .."
        elif status[2] == 3:
            return "-- Network Registration Denied"
        elif status[2] == 4:
            return "-- No Signal Network Available"
        elif status[2] == 5:
            print ("-- Registerd, roaming")
        else:
            return "-- Network Registration: Unknown"

        # gprsAttach = status[3]
        if   status[3] == 0:
            print ("-- No Internet")
        elif status[3] == 1:
            print ("-- Internet Available")
        else:
            return "-- Internet Availability: Unknown"

        # pppStatus = status[4]
        if   status[4] == 0:
            print ("-- Not Connected with Internet")
        elif status[4] == 1:
            print ("-- Connected with Internet")
        else:
            return "-- Internet Connectivity: Unknown"

        # serverConn = status[5]
        if   status[5] == 0:
            print ("-- Disconnected with MQTT Server")
        elif status[5] == 1:
            print ("-- Connected with MQTT Server")
        elif status[5] == 2:
            print ("-- Trying to open TCP Socket @ 9999")
        elif status[5] == 3:
            print ("-- TCP Socket Open @ 9999")
        else:
            print ("-- Server Connectivity: Unknown")
            return "Note: --Get_GPRS_PROTOCOL-- or --Check Mqtt/Tcp params--"

        # simSlotRetryCnt = status[6]
        if len(status) > 6:
            if  status[6] > 9:
                print ("-- GPRS in LOCKDOWN State")
        if len(status) > 7:
            count = (status[10]<<24)+(status[9]<<16)+(status[8]<<8)+status[7]
            print ("-- Gprs reset retry count is", count)

    @check_errors
    def set_gprs_reset_retry_count(self, addr, count):
        try:
            count = int(count)
        except:
            print ("Enter value between 3 to 86400")
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_GPRS_RESET_CNT, count, UINT32)

    @check_errors
    def get_gprs_reset_retry_count(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_GPRS_RESET_CNT, UINT32)

    @check_errors
    def set_gprs_credentials(self, addr, line):
        try:
            args = line.split(',')
            username = bytearray()
            password = bytearray()

            line1 = args[0]
            line2 = args[1]

            for x in range(0,len(line1)):
                if line1[x] != '"':
                    username.append(line1[x])

            for x in range(0,len(line2)):
                if line2[x] != '"':
                    password.append(line2[x])

            index = len(username)
            if index > 32:
                return "Len of username is not more than 32 character"
            elif index < 32:
                for x in range(index,32):
                    username.append(0)

            index = len(password)
            if index > 32:
                return "Len of Password is not more than 32 character"
            elif index < 32:
                for x in range(index,32):
                    password.append(0)

            username.extend(password)
        except:
            return "Enter : \"username\", \"password\"\n<Note: not more than 32 character each>"

        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_GPRS_CREDENTIAL, username, BYTE_ARRAY)

    @check_errors
    # def get_gprs_credentials(self, addr):
    #     status = self.my_simpleterm_master.get_param(
    #         addr, commandMappingContainer.GET_GPRS_CREDENTIAL, BYTE_ARRAY)

    #     try:
    #         username = bytearray()
    #         password = bytearray()
    #         for x in range(0,32):
    #             username.append(status[x])
    #             password.append(status[x+32])
    #         print ("Username : ",username)
    #         print ("Password : ",password)
    #         return ''
    #     except:
    #         print ([b for b in status])
    #         return "Incorrect data len found"
    def get_gprs_credentials(self, addr):
        status = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_GPRS_CREDENTIAL, BYTE_ARRAY)

        try:
            # Extract raw 32 byte fields
            username_raw = status[0:32]
            password_raw = status[32:64]

            # Remove padding (\x00 and \xff)
            username = username_raw.rstrip(b'\x00').rstrip(b'\xff').decode('utf-8')
            password = password_raw.rstrip(b'\x00').rstrip(b'\xff').decode('utf-8')

            print("Username :", username)
            print("Password :", password)

            return username, password

        except Exception as e:
            print("Error:", e)
            print([b for b in status])
            return "Incorrect data len found"


    @check_errors
    def set_gprs_broker(self, addr, line):
        try:
            args = line.split(',')
            url  = bytearray()
            port = bytearray()

            line1 = args[0]
            line2 = args[1]

            # Check the url is ipv6 or ipv4
            count = 0
            alpha = 0
            for letter in line1:
                if letter not in['.','0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']:
                    alpha = alpha + 1
                if letter in ['.']:
                    count = count+1

            # Ensure correct url is entered
            if (count != 3) and (count != 7) and (alpha == 0):
                return "Please Enter correct Url"

            check_url = 0

            for x in range(0,len(line1)):
                if (line1[x] == '.') and (count == 7) and (alpha == 0):
                    url.append(58)
                    if check_url > 4:
                        return "Please Enter correct IPv6 Url \n<Note: use of ':'' in set url is not allowed>"
                    check_url = 0
                elif (line1[x] == '.') and (count == 3) and (alpha == 0):
                    if check_url > 3:
                        return "Please Enter correct IPv4 Url"
                    check_url = 0
                elif line1[x] != '"':
                    url.append(line1[x])
                    check_url = check_url+1

            for x in range(0,len(line2)):
                if line2[x] not in ['1','2','3','4','5','6','7','8','9','0',' ','"']:
                    return "Please Enter correct Port \n <Note: Port is interger value>"
                elif line2[x] != '"':
                    port.append(line2[x])

            # Append 0 to fill the full buffer 
            index = len(url)
            if index > 40:
                return "Len of url is greater than 40 character"
            elif index < 40:
                for x in range(index,40):
                    url.append(0)

            index = len(port)
            if index > 6:
                return "Len of port is not more than 6 character"
            elif index < 6:
                for x in range(index,6):
                    port.append(0)

            url.extend(port)
         except Exception as e:
            print(e)
            return "Enter : \"url\", \"port\"\n<Note: url(ipv4,ipv6) not more than 40 bytes and port 6 bytes>"

        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_GPRS_BROKER, url, BYTE_ARRAY)

    @check_errors
    def reset_rtc_calib(self, addr, line):
        line = int(line)
        if line > 255:
            line = 255
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.RESET_RTC_CALIB, int(line), UINT8)

    def get_gprs_broker(self, addr):
        status = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_GPRS_BROKER, BYTE_ARRAY)

        try:
            url  = bytearray()
            port = bytearray()
            for x in range(0,40):
                url.append(status[x])
            for x in range(40,44):
                port.append(status[x])

            print ("Url  : ",url)
            print ("Port : ",port)
            return ''
        except:
            print ([b for b in status])
            return "Incorrect data len found"

    @check_errors
    def set_gprs_protocol(self, addr, line):
        if line == "":
            return "Usage : Enter 1 for MQTT or 2 for TCP !!!"
        elif line == "MQTT":
            line = 0xAC41
        elif line == "TCP":
            line = 0xAC14

        try:
            mode = int(line)
            if mode > 2:
                return "Usage : Enter 1 for MQTT or 2 for TCP !!!"
            elif mode == 1:
                mode = 0xAC41
            elif mode == 2:
                mode = 0xAC14
        except:
            return "Usage : Enter 1 for MQTT or 2 for TCP !!!"

        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_GPRS_ACT_PROTOCOL, mode, UINT16) 

    @check_errors
    def get_gprs_protocol(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_GPRS_ACT_PROTOCOL, UINT16)
        if(sts == 0xAC14):
            print("TCP Protocol is active")
        else:
            print("MQTT Protocol is active")
        return sts
    @check_errors
    def get_gprs_ip(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_GPRS_IP, BYTE_ARRAY)

    @check_errors
    def set_gprs_topic(self, addr, line, index):
        try:
            tmp = bytearray(line)
            topic = bytearray()
            for b in range(0,len(tmp)):
                if tmp[b] != 0x22:
                    topic.append(tmp[b])
            if len(topic) > 30:
                return "Max Len of topic cab be 30 characters"
            if len(topic) < 30:
                for b in range(len(topic),30):
                    topic.append(0x00)
            sumx = 0
            for x in range(0,len(topic)):
                sumx = sumx+topic[x]
            val = sumx/256
            topic.append(val)
            val = sumx%256
            topic.append(val)
            index = int(index)
        except:
            return "Enter : \"Topic\" \n<Note: not more than 30 character allowed>"

        paramNumber = 0
        if index == 1:
            paramNumber = commandMappingContainer.SET_TAP_CMDEXE_TOPIC
        elif index == 2:
            paramNumber = commandMappingContainer.SET_TAP_COLLECTION_TOPIC
        elif index == 3:
            paramNumber = commandMappingContainer.SET_TAP_PUSH_TOPIC
        elif index == 4:
            paramNumber = commandMappingContainer.SET_DLMS_PULL_TOPIC
        elif index == 5:
            paramNumber = commandMappingContainer.SET_DLMS_PUSH_TOPIC
        else:
            return "false"

        return self.my_simpleterm_master.set_param(addr, paramNumber, topic, BYTE_ARRAY)

    @check_errors
    def get_gprs_topic(self, addr, index):
        index = int(index)
        paramNumber = 0
        if index == 1:
            paramNumber = commandMappingContainer.GET_TAP_TOPICS
        elif index == 2:
            paramNumber = commandMappingContainer.GET_DLMS_TOPICS
        else:
            return "false"

        return self.my_simpleterm_master.get_param(addr, paramNumber, BYTE_ARRAY)

    @check_errors
    def set_pcb_serial_no(self, addr, line, start_address=3049):
        try:
            # Encode string → bytes → bytearray
            tmp = bytearray(line.encode("ascii"))

            payload = bytearray()
            length = 30

            payload.extend(serialize.serialize_uint32(start_address))
            payload.extend(serialize.serialize_uint16(length))

            topic = bytearray()
            for b in tmp:
                if b != 0x22:   # remove double quotes (")
                    topic.append(b)

            if len(topic) > 30:
                return "Max 30 characters allowed"

            while len(topic) < 30:
                topic.append(0x00)

            payload.extend(topic)

        except Exception as e:
            # OPTIONAL: print real error for debugging
            print("set_pcb_serial_no error:", e)
            return 'Enter : "Topic"\n<Note: Max 30 characters allowed>'

        return self.my_simpleterm_master.set_param(
            addr,
            commandMappingContainer.MEM_EEPROM_WRITE,
            payload,
            BYTE_ARRAY
        )


    @check_errors
    def get_pcb_serial_no(self, addr, start_address = 3049):
        # start_address = 3049
        length  = 30
        payload = bytearray()

        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(serialize.serialize_uint16(length))
        data = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.MEM_EEPROM_READ,
                                                            payload, BYTE_ARRAY, BYTE_ARRAY)
        if not data:
            return ""

        pcb_serial = (
            data
            .rstrip(b'\x00')                 # remove null padding
            .decode("ascii", errors="ignore")  # decode safely
        )

        return pcb_serial

    @check_errors
    def set_auto_reg_push(self, addr, line):
        mode= int(line)
        if mode < 0 or mode > 1:
            print ("Warning : Enter 1 for Enable or 0 for Disable !!!")
        else:   
            if(mode == 1):
                period = 0x55
                return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_AUTO_REG_PUSH, period, INT8)
            else:
                period = 0x11
                return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_AUTO_REG_PUSH, period, INT8)

    @check_errors
    def get_auto_reg_push(self, addr):
        val = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_AUTO_REG_PUSH, INT8)
        if val == 0x11:
            return "Disable"
        else:
            return "Enable"

    @check_errors
    def set_pulse_count_flag(self, addr, line):
        mode= int(line)
        if mode < 0 or mode > 1:
            print ("Warning : Enter 1 for Enable or 0 for Disable !!!")
        else:   
            if(mode == 1):
                period = 0x55
                return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_PULSE_COUNT_FLAG, period, INT8)
            else:
                period = 0x11
                return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_PULSE_COUNT_FLAG, period, INT8)

    @check_errors
    def get_pulse_count_flag(self, addr):
        val = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PULSE_COUNT_FLAG, INT8)
        if val == 0x11:
            return "Disable"
        else:
            return "Enable"

    @check_errors
    def get_kwh_pulse_counter(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_KWH_PULSE_COUNTS, UINT16)

    @check_errors
    def get_kvah_pulse_counter(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_KVAH_PULSE_COUNTS, UINT16)

    @check_errors
    def set_nic_pcb_serial_no(self, addr, line, start_address = 3081):
        try:
            tmp = bytearray(line.encode("ascii"))
            payload = bytearray()
            # start_address = 3081
            length = 30
            payload.extend(serialize.serialize_uint32(start_address))
            payload.extend(serialize.serialize_uint16(length))

            topic = bytearray()
            for b in range(0,len(tmp)):
                if tmp[b] != 0x22:
                    topic.append(tmp[b])
            if len(topic) > 30:
                return "Max 30 characters allowed"
            if len(topic) <= 30:
                for b in range(len(topic),30):
                    topic.append(0x00)
            payload.extend(topic)
        except:
            return "Enter : \"Topic\" \n<Note: Max 30 characters allowed>"

        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.MEM_EEPROM_WRITE,
                                                   payload, BYTE_ARRAY)

    @check_errors
    def get_nic_pcb_serial_no(self, addr, start_address = 3081):
        # start_address = 3081
        length  = 30
        payload = bytearray()
        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(serialize.serialize_uint16(length))
        data =  self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.MEM_EEPROM_READ,
                                                            payload, BYTE_ARRAY, BYTE_ARRAY)
        if not data:
            return ""

        nic_pcb_serial = (
            data
            .rstrip(b'\x00')                 # remove null padding
            .decode("ascii", errors="ignore")  # decode safely
        )

        return nic_pcb_serial

    @check_errors
    def get_num_gprs_profile(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_GSM_LOGS, UINT32)

    @check_errors
    def get_gprs_profile_by_index(self, addr, index, isReturn=False):
        index = int(index)
        data = self.my_simpleterm_master.set_and_get_param(
            addr,
            commandMappingContainer.GET_GSM_LOGS_BY_INDEX,
            index,
            UINT32,
            BYTE_ARRAY
        )

        if not data or len(data) < 9:
            return "No entry found !!!"

        # ---------------- parsing ----------------
        unix_str_time = serialize.deserialize_uint32(data[0:4], "reverse")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(unix_str_time))

        status      = data[4]
        reasonOflog = data[5]
        act_slot    = data[6]
        s_strength  = data[7]
        net_reg     = data[8]

        # -------- helper to decode ascii fields --------
        def decode_field(b):
            return b.rstrip(b'\x00').decode("ascii", errors="ignore")

        imei        = decode_field(data[9:24])
        sim1_iccid  = decode_field(data[24:44])
        sim1_apn    = decode_field(data[44:60])
        sim2_iccid  = decode_field(data[60:80])
        sim2_apn    = decode_field(data[80:96])

        # ---------------- status / reason masks ----------------
        bStatus = {
            0: 'MQTT_CONNECTED', 1: 'MQTT_DISCONNECTED', 2: 'MQTT_CONNECTION_ERR',
            3: 'MQTT_SUBSCRIBE_ERR', 4: 'TCP_PORT_OPEN', 5: 'TCP_PORT_OPEN_ERR',
            6: 'GSM_LOCKDOWN', 7: 'GSM_PLUGOUT'
        }

        bReason = {
            0: 'GSM_POWERON', 1: 'GSM_POWEROFF', 2: 'GSM_SW_NO_SIM',
            3: 'GSM_SW_NO_CSQ', 4: 'GSM_SW_NO_REG', 5: 'GSM_SW_NO_PPP',
            6: 'GSM_SW_MANUAL', 7: 'GSM_SW_RETRY_EXHAUST'
        }

        statusMask = [bStatus[i] for i in bStatus if status & (1 << i)]
        reasonMask = [bReason[i] for i in bReason if reasonOflog & (1 << i)]

        # ---------------- active SIM slot ----------------
        if act_slot not in (1, 2):
            act_slot_mask = f"{act_slot} [NONE]"
            s_strength = 0xFF
            net_reg = 0xFF
        else:
            # act_slot_mask = f"SIM{act_slot}"
            act_slot_mask = act_slot

        # ---------------- return as dict (API mode) ----------------
        if isReturn:
            return {
                "TimeStamp": timestamp,
                "Status": statusMask,
                "Reason": reasonMask,
                "Active_Sim": act_slot_mask,
                "Signal_Strength": s_strength,
                "Network_Registered": net_reg,
                "IMEI": imei,
                "SIM1_ICCID": sim1_iccid,
                "SIM1_APN": sim1_apn,
                "SIM2_ICCID": sim2_iccid,
                "SIM2_APN": sim2_apn
            }

        # ---------------- signal strength ----------------
        if s_strength == 99:
            strengthMask = "99 [NO_SIGNAL]"
        elif s_strength < 2:
            strengthMask = f"{s_strength} [POOR]"
        elif s_strength < 10:
            strengthMask = f"{s_strength} [MARGINAL]"
        elif s_strength < 15:
            strengthMask = f"{s_strength} [OK]"
        elif s_strength < 20:
            strengthMask = f"{s_strength} [GOOD]"
        elif s_strength < 32:
            strengthMask = f"{s_strength} [EXCELLENT]"
        elif s_strength == 255:
            strengthMask = "-"
        else:
            strengthMask = str(s_strength)

        # ---------------- network registration ----------------
        if net_reg == 255:
            netRegMask = "-"
        else:
            netRegMap = {
                0: "No_Registered,No_searching for_operator",
                1: "Home_Network",
                2: "No_Registered,Searching for_operator",
                3: "Network_Registration_Denied",
                4: "No_Network_Available",
                5: "Registered,roaming"
            }
            netRegMask = f"{net_reg} [{netRegMap.get(net_reg, 'Unknown_Network_Registration')}]"


        # ---------------- formatted output ----------------
        return (
            "TimeStamp                  : {}\n"
            "Status                     : {}\n"
            "Reason of Log              : {}\n"
            "Active Sim Slot            : {}\n"
            "Signal Strength            : {}\n"
            "Network Registered         : {}\n"
            "GSM Module IMEI No         : {}\n"
            "SIM1 ICCID No              : {}\n"
            "SIM1 APN No                : {}\n"
            "SIM2 ICCID No              : {}\n"
            "SIM2 APN No                : {}\n"
        ).format(
            timestamp, statusMask, reasonMask,
            act_slot_mask, strengthMask, netRegMask,
            imei, sim1_iccid, sim1_apn, sim2_iccid, sim2_apn
        )

    @check_errors
    def gprs_profile_print_direct(self, addr):   
        no_of_survey = self.get_num_gprs_profile(addr)
        values = int(no_of_survey)
        if values == 0:
            return "No Entries Found !!!"
        values = values - 1
        flag = True
        while(flag):
            reply=None
            while reply is None:
                try:
                    reply= self.get_gprs_profile_by_index(addr,values)
                    print ("Index: ", values)
                    print (reply)
                    print (" ")
                except Exception as e:
                    print ("Retrying for Index: ",str(values))
                    pass
            values = values -1
            if (values == -1):
                flag = False
        return "No of GPRS profiles:"+str(no_of_survey)+"\n"

    @check_errors
    def set_gprs_sim_toggle(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.SET_GSM_SIM_TOGGLE, UINT8)

    @check_errors
    def set_gprs_apn(self, addr, line):
        try:
            args = line.split(',')
            apn = bytearray()

            ipVal = int(args[0])
            apn.extend(serialize.serialize_uint8(ipVal))
            line2 = args[1]

            for x in range(0,len(line2)):
                if line2[x] != '"':
                    apn.extend(line2[x])

            if len(apn) > 16:
                return "Len of username is not more than 15 character"
            print ("append remaining 0")
            for b in range(len(apn),17):
                apn.append(0x00)
        except:
            return "Enter : ip, apn \n'ip' : 1 for 'IPV6' and 2 for 'IPV4V6' \napn : 'not more than 15 character'"

        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_GSM_APN, apn, BYTE_ARRAY)

    @check_errors
    def get_metering_mode(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_METERING_MODE, INT8)
        if(sts == 1):
            return "Import-Export Mode is active"
        elif(sts == 0):
            return "Forward mode is active"
        else:
            return "Unknown mode"

    @check_errors
    def get_meter_type(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_METER_TYPE, INT8)
        if(sts == 1):
            return "Meter Current Rating : (10-60)A"
        elif(sts == 0):
            return "Meter Current Rating : (20-100)A"
        elif(sts == 2):
            return "Meter Current Rating : (10-100)A"
        else:
            return "Unknown current rating"

    @check_errors
    def get_ct_ratio(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.get_ct_ratio, UINT8)
        return sts
    
    @check_errors
    def get_apprent_led(self,addr):
        data = self.my_simpleterm_master.get_param(
                    addr, commandMappingContainer.GET_APPRENT_LED,UINT8)
        return "0x%02X" % data

    @check_errors
    def get_instant_config_time(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CONFIG_TIME, INT32)
        return sts
        # if(sts == 1):
        #     return "Import-Export Mode is active"
        # elif(sts == 0):
        #     return "Forward mode is active"
        # else:
        #     return "Unknown mode"

    @check_errors
    def get_metering_load(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_METERING_LOAD, INT8)
        if(sts == 0):
            return "Lag-Lead Mode is active"
        elif(sts ==1):
            return "Lag only mode is active"
        else:
            return "Unknown mode"

    @check_errors
    def set_calib_led2(self, addr, period):
        if period == "":
            period = 1
        period = int(period)
        if period < 0 or period > 1:
            print ("value should be 1 or 0")
        else :
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_CALIB_LED2, period, INT8) 

    @check_errors
    def get_calib_led2(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CALIB_LED2, INT8)
        if(sts == 0x01):
            return "kVAh Led"
        else:
            return "kVArh Led" 

    @check_errors
    def set_freq_ph_err(self, addr, line):
        try:
            args = line.split(',')
            payload = bytearray()

            RphErr = int(args[0])
            YphErr = int(args[1])
            BphErr = int(args[2])
            payload.extend(serialize.serialize_uint32(RphErr))
            payload.extend(serialize.serialize_uint32(YphErr))
            payload.extend(serialize.serialize_uint32(BphErr))
        except:
            return "Usage: RphErr, YphErr, BphErr"

        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_FREQ_DEPENDENT_PH_ERR, payload, BYTE_ARRAY)

    @check_errors
    def set_prepaid_billing_type(self, addr, line):
        if line == "":
            return "Usage : Enter 1 for KWH or 0 for KVAH only !!!"
        elif line == "kwh":
            line = 1
        elif line == "kvah":
            line = 0

        try:
            mode = int(line)
            if mode < 0 or mode > 1:
                return "Usage : Enter 1 for KWH or 0 for KVAH only !!!"
        except:
            return "Usage : Enter 1/'kwh' for KWH or 0/'kvah' for KVAH only !!!"

        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_PREPAID_BILLTYPE, mode, INT8) 

    @check_errors
    def get_prepaid_billing_type(self, addr):
        sts = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_PREPAID_BILLTYPE, INT8)
        if(sts == 1):
            return "KWH is active"
        elif(sts == 0):
            return "KVAH is active"
        else:
            return "Unknown mode"

    @check_errors
    def set_dg_phase_type(self, addr, line):
        if line == "":
            return " 0. All Phases OFF \n 1. R-Phase ON \n 2. Y-Phase ON \n 3. RY-Phase ON \n 4. B-Phase ON \n 5. RB Phase ON \n 6. YB Phase ON \n 7. All Phases ON"

        try:
            mode = int(line)
            if mode > 7:
                return " 0. All Phases OFF \n 1. R-Phase ON \n 2. Y-Phase ON \n 3. RY-Phase ON \n 4. B-Phase ON \n 5. RB Phase ON \n 6. YB Phase ON \n 7. All Phases ON"
        except:
                return " 0. All Phases OFF \n 1. R-Phase ON \n 2. Y-Phase ON \n 3. RY-Phase ON \n 4. B-Phase ON \n 5. RB Phase ON \n 6. YB Phase ON \n 7. All Phases ON"

        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_DG_PH_TYPE, mode, INT8) 

    @check_errors
    def get_dg_phase_type(self, addr):
        sts = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_DG_PH_TYPE, INT8)
        if sts == 0:
            return "All Phases OFF"
        flag = 0
        while flag < 3:
            temp = sts & (1 << flag)
            if(temp):
                if(flag == 0):
                    print ("R-Phase ON")
                elif(flag == 1):
                    print ("Y-Phase ON")
                else:
                    print ("B-Phase ON")
            flag = flag + 1

        return " "

    @check_errors
    def set_prepaid_auto_switch(self, addr, line):
        try:
            mode = int(line)
            if mode == 0:
                mode = 0x11
            elif mode == 1:
                mode = 0x55
            else:
                return " 0. Disable  1. Enable"

        except:
                return " 0. Disable  1. Enable"

        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_AUTO_PREPAID_MODE, mode, UINT8)

    @check_errors
    def get_prepaid_auto_switch(self, addr):
        sts = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_AUTO_PREPAID_MODE, UINT8)
        if sts == 0x11:
            return "Disable"
        elif sts == 0x55:
            return "Enable"
        else:
            return "Disable"

    @check_errors
    def set_friendly_holidays(self, addr, cal_time):
        if cal_time == "":
            return "Mention date YYYY-MM-DD i.e 2021-01-26 (26th January)"
        else:
            buf = bytearray()
            try:
                date_str = cal_time.split(',')
                index = 0
                len_str = len(date_str)
                if len_str > 24:
                    print ("Warning: Maximum 24 holidays allowed")
                    print ("Ignoring more than 24 days")
                    len_str = 24
                while index < len_str:
                    time_str = "00:00:00"
                    value = date_str[index]+ " " + time_str
                    cal_time = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    unix_time_zero = datetime.datetime(1970, 1, 1)
                    seconds_since_epoch = int((cal_time - unix_time_zero).total_seconds())
                    # print ("datetime",seconds_since_epoch)
                    buf.extend(serialize.serialize_uint32(seconds_since_epoch))
                    index = index + 1
                while index < 24:
                    buf.extend(serialize.serialize_uint32(0xFFFFFFFF))
                    index = index + 1
            except:
                return "Incorrect data and/or data format, should be YYYY-MM-DD"
        soft_crc = SoftCRC()
        crc = soft_crc.crc16ccitt(str(buf[0:96]))
        buf.extend(serialize.serialize_uint16(crc))
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_PREPAID_HOLIDAYS,
                                                   buf, BYTE_ARRAY)

    @check_errors
    def get_friendly_holidays(self, addr):
        time = bytearray()
        time = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_PREPAID_HOLIDAYS, BYTE_ARRAY)
        try:
            index = 0
            while(index < 96):
                dateTS = (time[index]<<24)+(time[index+1]<<16)+(time[index+2]<<8)+(time[index+3])
                if dateTS == 0xFFFFFFFF:
                    break
                print (str(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=dateTS)))
                index = index + 4
        except:
            return "len of byte is",len(time), "It should be 96"

        return "Total holidays found : " + str(index/4)

    @check_errors
    def set_friendly_weekday(self, addr, line):
        if line == "":
            return " 0. NONE \n 1. SUNDAY \n 2. MONDAY \n 3. TUESDAY \n 4. WEDNESDAY \n 5. THURSDAY \n 6. FRIDAY \n 7. SATURDAY"

        try:
            mode = int(line)
            if mode > 7:
                return " 0. NONE \n 1. SUNDAY \n 2. MONDAY \n 3. TUESDAY \n 4. WEDNESDAY \n 5. THURSDAY \n 6. FRIDAY \n 7. SATURDAY"
        except:
                return " 0. NONE \n 1. SUNDAY \n 2. MONDAY \n 3. TUESDAY \n 4. WEDNESDAY \n 5. THURSDAY \n 6. FRIDAY \n 7. SATURDAY"

        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_PREPAID_WEEKDAY, mode, INT8) 

    @check_errors
    def get_friendly_weekday(self, addr):
        sts = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_PREPAID_WEEKDAY, INT8)
        if sts == 1:
            return "SUNDAY"
        elif sts == 2:
            return "MONDAY"
        elif sts == 3:
            return "TUESDAY"
        elif sts == 4:
            return "WEDNESDAY"
        elif sts == 5:
            return "THURSDAY"
        elif sts == 6:
            return "FRIDAY"
        elif sts == 7:
            return "SATURDAY"
        else:
            return "NONE"

    @check_errors
    def get_solarRiseTime(self, addr, cal_time):
        if cal_time == "":
            cal_time = 0
        elif cal_time == "now":
            cal_time = datetime.datetime.now()
        else:
            try:
                time_str = cal_time.split(' ')[1]
                if len(time_str) == 6:
                    time_str = time_str[0] + time_str[1] + ":" + time_str[2] + time_str[3] + ":" +time_str[4] + time_str[5]
                    cal_time = cal_time.split(' ')[0] + " " + time_str
                cal_time = datetime.datetime.strptime(cal_time, "%Y-%m-%d %H:%M:%S")
            except:
                return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = 0
        if cal_time != 0:
            seconds_since_epoch = int((cal_time - unix_time_zero).total_seconds())
        #print seconds_since_epoch
        time = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_SUN_RISE_TIME,
                                                   seconds_since_epoch, UINT32, UINT32)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def get_solarSetTime(self, addr, cal_time):
        if cal_time == "":
            cal_time = 0
        elif cal_time == "now":
            cal_time = datetime.datetime.now()
        else:
            try:
                time_str = cal_time.split(' ')[1]
                if len(time_str) == 6:
                    time_str = time_str[0] + time_str[1] + ":" + time_str[2] + time_str[3] + ":" +time_str[4] + time_str[5]
                    cal_time = cal_time.split(' ')[0] + " " + time_str
                cal_time = datetime.datetime.strptime(cal_time, "%Y-%m-%d %H:%M:%S")
            except:
                return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = 0
        if cal_time != 0:
            seconds_since_epoch = int((cal_time - unix_time_zero).total_seconds())
        #print seconds_since_epoch
        time = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_SUN_SET_TIME,
                                                   seconds_since_epoch, UINT32, UINT32)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def set_solarPosition(self, addr, latitude, longitude):
        latitude = float(latitude)
        longitude= float(longitude)
        if(latitude > 90.0 and latitude < -90.0):
            print ("Warning: Wrong latitude Entry")
        elif(longitude > 180.0 and longitude < -180.0):
            print ("Warning: Wrong longitude Entry")
        else:
            lat = bytearray(struct.pack("f",latitude))
            lon = bytearray(struct.pack("f",longitude))
            buff = bytearray()
            buff.extend(serialize.serialize_uint8(int(lat[0])))
            buff.extend(serialize.serialize_uint8(int(lat[1])))
            buff.extend(serialize.serialize_uint8(int(lat[2]))) 
            buff.extend(serialize.serialize_uint8(int(lat[3])))
            buff.extend(serialize.serialize_uint8(int(lon[0])))
            buff.extend(serialize.serialize_uint8(int(lon[1])))
            buff.extend(serialize.serialize_uint8(int(lon[2])))
            buff.extend(serialize.serialize_uint8(int(lon[3])))
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_SUN_LOCATION, buff, BYTE_ARRAY)            

    @check_errors
    def get_solarPosition(self, addr):
        buf = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_SUN_LOCATION, BYTE_ARRAY)
        [lat,lon] = struct.unpack("ff", buf)
        print ("Latitude  : " +str(lat))
        print ("Longitude : " +str(lon))

    @check_errors
    def set_solarOffset(self, addr, sunrise, sunset):
        rise = int(sunrise)
        sset = int(sunset)
        if(rise > 180 and rise < -180):
            print ("Warning: not more than 180 minute")
        elif(sset > 180 and sset < -180):
            print ("Warning: not more than 180 minute")
        else:    
            buff = bytearray()
            buff.extend(serialize.serialize_int32(rise))
            buff.extend(serialize.serialize_int32(sset))
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_SUN_OFFSET, buff, BYTE_ARRAY) 

    @check_errors
    def get_solarOffset(self, addr):
        buf = bytearray()
        buf = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_SUN_OFFSET, BYTE_ARRAY)
        [lat,lon] = struct.unpack("!ii", buf)
        print ("SunRise time offset : " +str(lat))
        print ("SunSet time offsest : " +str(lon))

    @check_errors
    def get_num_fw_packets(self, addr):
        obj_id = 0x06
        payload = bytearray()
        payload.extend(serialize.serialize_uint8(obj_id))
        return self.my_simpleterm_master.set_and_get_param(
            addr, commandMappingContainer.IMAGE_TRANSFER_TAP, payload, BYTE_ARRAY, UINT32)

    @check_errors
    def get_fw_packet_status(self, addr,index):
        if index <= 5:
            obj_id = 0x07
            payload = bytearray()
            payload.extend(serialize.serialize_uint8(obj_id))
            payload.extend(serialize.serialize_uint8(index))
            data = self.my_simpleterm_master.set_and_get_param(addr,
                commandMappingContainer.IMAGE_TRANSFER_TAP, payload, BYTE_ARRAY,BYTE_ARRAY)
            print ([hex(b) for b in data])
        else:
            return "Invalid value! Index should be in the range of 0 to 5"

    @check_errors
    def get_flash_read(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        length = int(args[1])
        obj_id = 0x01
        payload = bytearray()
        payload.extend(serialize.serialize_uint8(obj_id))
        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(serialize.serialize_uint8(length))
        return self.my_simpleterm_master.set_and_get_param(addr,
                commandMappingContainer.IMAGE_TRANSFER_TAP, payload, BYTE_ARRAY,BYTE_ARRAY)

    @check_errors
    def get_live_display_version(self, addr):
        start_address = 0x43000
        length = 24
        obj_id = 0x01
        payload = bytearray()
        payload.extend(serialize.serialize_uint8(obj_id))
        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(serialize.serialize_uint8(length))
        data = self.my_simpleterm_master.set_and_get_param(addr,
                commandMappingContainer.IMAGE_TRANSFER_TAP, payload, BYTE_ARRAY,BYTE_ARRAY)
        soft_crc = SoftCRC()
        crc_image = soft_crc.crc16ccitt(str(data[0:22]))
        cal_crc = (data[23]<<8) + data[22]
        if crc_image == cal_crc:
            protocol_version = (data[1]<<8)+data[0]
            property_name = bytearray()
            for b in range(16):
                property_name.append(data[2+b])
            print ("UI Protocol Version : " + str(protocol_version))
            print ("UI Property Name : " + property_name)
        else:
            print ("Default: GPM-STANDARD-V_01") 
        return ""       

    @check_errors
    def get_ext_display_version(self, addr):
        start_address = 0x44000
        length = 24
        obj_id = 0x01
        payload = bytearray()
        payload.extend(serialize.serialize_uint8(obj_id))
        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(serialize.serialize_uint8(length))
        data = self.my_simpleterm_master.set_and_get_param(addr,
                commandMappingContainer.IMAGE_TRANSFER_TAP, payload, BYTE_ARRAY,BYTE_ARRAY)
        soft_crc = SoftCRC()
        crc_image = soft_crc.crc16ccitt(str(data[0:22]))
        cal_crc = (data[23]<<8) + data[22]
        if crc_image == cal_crc:
            protocol_version = (data[1]<<8)+data[0]
            property_name = bytearray()
            for b in range(16):
                property_name.append(data[2+b])
            print ("UI Protocol Version : " + str(protocol_version))
            print ("UI Property Name : " + property_name)
        else:
            print ("None")
        return ""      

    @check_errors
    def set_energy_limit(self, addr, energy_limit):
        energy_limit = int(energy_limit)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_ENERGY_LIMIT, energy_limit, INT32)

    @check_errors
    def dc_cal_v1(self, addr, voltage):
        voltage = int(voltage)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_DC_CAL_V1, voltage, UINT32)

    @check_errors
    def dc_cal_v2(self, addr, voltage):
        voltage = int(voltage)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_DC_CAL_V2, voltage, UINT32)

    @check_errors
    def dc_cal_i(self, addr, current):
        current = int(current)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_DC_CAL_I, current, UINT32)

    @check_errors
    def get_flash_erase_sector(self, addr, line):
        sector = int(line)
        obj_id = 0x04
        payload = bytearray()
        payload.extend(serialize.serialize_uint8(obj_id))
        payload.extend(serialize.serialize_uint32(sector))
        return self.my_simpleterm_master.set_and_get_param(addr,
                commandMappingContainer.IMAGE_TRANSFER_TAP, payload, BYTE_ARRAY,RESPONSE_PACKET)

    @check_errors
    def set_active_energy_offset(self, addr, active_offset):
        active_offset = int(active_offset)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_ACTIVE_ENERGY_OFFSET, active_offset, INT32)

    @check_errors
    def set_reactive_energy_offset(self, addr, reactive_offset):
        reactive_offset = int(reactive_offset)
        return self.my_simpleterm_master.set_param(
            addr,
            commandMappingContainer.SET_REACTIVE_ENERGY_OFFSET,
            reactive_offset,
            INT32)

    @check_errors
    def set_apparent_energy_offset(self, addr, apparent_offset):
        apparent_offset = int(apparent_offset)
        return self.my_simpleterm_master.set_param(
            addr,
            commandMappingContainer.SET_APPARENT_ENERGY_OFFSET,
            apparent_offset,
            INT32)

    @check_errors
    def set_price(self, addr, price):
        price = float(price)
        if float(price) <= 0.00 or float(price) >= 100.00:
            return "Invalid price input! Price must be higher than 0.00, and lower than 100.00."
        if float(price) != 0.0:
            e_per_credit = int(round(3600 * 1000 / float(price), 0))
        else:
            e_per_credit = 1.0
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_ENERGY_PER_CREDIT, e_per_credit, UINT32)

    @check_errors
    def set_dd_params(self, addr, ddp):
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_DD_PARAMS, ddp, DAILY_DEDUCTION_PARAMS)

    @check_errors
    def set_block_load_profile_params(self, addr, lsp):
        if not isinstance(lsp, LoadSurveyParams):
            args = lsp.split(",")
            if "now" in args[0]:
                delta = int(args[0].split("+")[1])
                start_time = datetime.datetime.now() + datetime.timedelta(seconds=delta)
            else:
                start_time = dateutil.parser.parse(args[0].strip(' '))
            interval = int(args[1])
            status = int(args[2])
            lsp = LoadSurveyParams()
            lsp.start_time = start_time
            lsp.interval = interval
            lsp.status = status

        if lsp.interval > 0 and lsp.interval < 60 and (60 % lsp.interval) == 0:
            return self.my_simpleterm_master.set_param(
                addr,
                commandMappingContainer.SET_BLOCK_LOAD_PROFILE_PARAMS,
                lsp,
                LOAD_SURVEY_PARAMS)
        else:
            return "Block load profile integration period must be in the range of 0-59 minutes, and it must be a factor of 60!"

    @check_errors
    def set_slab_params(self, addr, args):
        scp = SlabConfigurationPacket()
        scp.no_of_slabs = int(args.split(",")[0])
        scp.slab_price = map(
            int, (args.split("[")[1]).split("]")[0].split(","))
        scp.slab_limits = map(
            int, (args.split("[")[2]).split("]")[0].split(","))
        scp.mmc = int(args.split("],")[2])

        if (scp.no_of_slabs < 1 or scp.no_of_slabs > 6):
            return "Error! Number of slabs should be in the range of 1 to 6!"
        elif len(scp.slab_price) != 6:
            return "Error! 6 parameters need to be entered for slab_price!"
        elif len(scp.slab_limits) != 5:
            return "Error! 6 parameters need to be entered for slab_limits!"

        for index in range(len(scp.slab_price)):
            if index < scp.no_of_slabs:
                if scp.slab_price[index] < 1 or scp.slab_price[index] > 65000:
                    return "Error! Slab prices should be in the range of 1 to 65000!"
            else:
                if scp.slab_price[index] != 0:
                    return "Error! Number of slab prices entered is more than number of slabs!"

        for index in range(len(scp.slab_limits)):
            if index < (scp.no_of_slabs - 1):
                if scp.slab_limits[index] < 1 or scp.slab_limits[index] > 65000:
                    return "Error! Slab limits should be in the range of 1 to 65000!"
            else:
                if scp.slab_limits[index] != 0:
                    return "Error! Number of slab limits entered is more than number of slabs!"

            if index > 0 and index < (scp.no_of_slabs - 1):
                if scp.slab_limits[index] <= scp.slab_limits[index - 1]:
                    return "Error! Slab limits should be in increasing order!"

        if scp.mmc < 0 or scp.mmc > 65000:
            return "Error! MMC should be in the range of 0 to 65000!"

        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_SL_PARAMS, scp, SLAB_CONFIGURATION_PACKET)
    
    # @check_errors
    # def set_tod_params(self, addr, args):
    #     tcp = TodConfigurationPacket()
    #     var = args.split(",")
    #     updateTime = dateutil.parser.parse(var[0])
    #     seconds_since_epoch = int((updateTime - datetime.datetime(1970,1,1)).total_seconds())
        
    #     tcp.start_time_1 = ((seconds_since_epoch)%(86400))
    #     tcp.duration_1 = int(var[1])
    #     tcp.price_1 = int(var[2])

    #     updateTime = dateutil.parser.parse(var[3])
    #     seconds_since_epoch = int((updateTime - datetime.datetime(1970,1,1)).total_seconds())
        
    #     tcp.start_time_2 = ((seconds_since_epoch)%(86400))        
    #     tcp.duration_2 = int(var[4])
    #     tcp.price_2 = int(var[5])


        
        # return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_TOD_PARAMS, tcp, TOD_CONFIGURATION_PACKET)
    
    @check_errors
    def set_tod_params(self, addr, args):
        tcp = TodConfigurationPacket()
        var = args.split(",")
        updateTime = dateutil.parser.parse(var[0])
        seconds_since_epoch = int((updateTime - datetime.datetime(1970,1,1)).total_seconds())
        
        tcp.start_time_1 = ((seconds_since_epoch)%(86400))
        tcp.duration_1 = int(var[1])
        tcp.price_1 = int(var[2])

        updateTime = dateutil.parser.parse(var[3])
        seconds_since_epoch = int((updateTime - datetime.datetime(1970,1,1)).total_seconds())
        
        tcp.start_time_2 = ((seconds_since_epoch)%(86400))        
        tcp.duration_2 = int(var[4])
        tcp.price_2 = int(var[5])
        
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_TOD_PARAMS, tcp, TOD_CONFIGURATION_PACKET)

    @check_errors
    def get_tod_params(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_TOD_PARAMS, TOD_CONFIGURATION_PACKET)

    @check_errors
    def set_tod_power_limit(self, addr, args):
        tcp = PowerLimitTodPacket()
        var = args.split(",")
        tcp.highPowerLimit      = int(var[0])    
        tcp.overPowerLimit      = int(var[1])
        tcp.retryDelay5Sec      = int(var[2])
        tcp.maxRetryCount       = int(var[3])
        tcp.hiOrOvrpwrOccPtime  = int(var[4])
        tcp.overVoltLimit       = int(var[5])
        tcp.overVoltOccPtime    = int(var[6])
        tcp.overVoltResPtime    = int(var[7])
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_TOD_POWER_LIMIT, tcp, GET_TOD_POWER_LIMIT)

    @check_errors
    def get_tod_power_limit(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_TOD_POWER_LIMIT, GET_TOD_POWER_LIMIT)
    
    @check_errors
    def set_power_limit_params(self, addr, args):
        tcp = PowerLimitParamsPacket()
        var = args.split(",")
        tcp.EgPower      = int(var[0])    
        tcp.DgPower      = int(var[1])
        tcp.Lockperiod   = int(var[2])
        tcp.OccPtime     = int(var[3])
        tcp.ResPtime     = int(var[4])
        tcp.RetryCount   = int(var[5])
        tcp.StatusF      = int(var[6])
        #if tcp.OccPtime > 14 and tcp.ResPtime > 14:
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_POWER_LIMIT_PARAMS, tcp, GET_TOD_POWER_LIMIT)
        #print "On Time and Off time should be greater than or equal to 15"    

    @check_errors
    def get_power_limit_params(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_POWER_LIMIT_PARAMS, GET_PARAMS_POWER_LIMIT)

    @check_errors
    def get_power_event_logs(self, addr, index):
        try:
            index = int(index)
            if index > 1:
                index = 1
        except:
            index = 0
        return self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_POWER_EVENT_LOGS, 
                                         index, INT8, POWER_EVENT_RECORD)
        
    @check_errors
    def get_battery_logs(self, addr):
        buf = bytearray()
        buf = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_BATT_LOG, BYTE_ARRAY)
        wakeup = {
                    0 : 'None', 1 : 'Push Button', 2 : 'C-Open',
                    3 : 'NM', 4 : 'WDog reset', 5 : 'Unwanted wakeup'
                 }

        wakeupReason = {
                        0 : 'LLWU_0'  , 1  : 'LLWU_1' , 2  : 'LLWU_2',
                        3 : 'LLWU_3'  , 4  : 'LLWU_4' , 5  : 'LLWU_5',
                        6 : 'LLWU_6'  , 7  : 'LLWU_7' , 8  : 'LLWU_8',
                        9 : 'LLWU_9'  , 10 : 'LLWU_10', 11 : 'LLWU_11',
                        12: 'LLWU_12' , 13 : 'LLWU_13', 14 : 'LLWU_14',
                        15: 'LLWU_15' , 16 : 'LLWU_16', 17 : 'LLWU_17',
                        18: 'LLWU_18' , 19 : 'LLWU_19', 20 : 'LLWU_20',
                        21: 'LLWU_21' , 22 : 'LLWU_22', 23 : 'LLWU_23',
                        24: 'LPTMR_NM', 25 : 'RTC-ALM', 26 : 'CMP0'   ,
                        27: 'IRQ_COPN', 28 : 'CMP1'   , 29 : 'MAINS'  ,
                        30: 'PUSH-BTN', 31 : 'LLWU_31'
                      }

        resetReason = {
                        0 : 'LLWU_WAKEUP'  , 1 : 'LOW_VOLT_DETECT' ,
                        2 : 'LOSS_OF_CLOCK', 3 : 'LOSS OF PLL'     ,
                        5 : 'WATCH_DOG'    , 6 : 'RESET EXT PIN'   ,
                        7 : 'POWER_DETECT' , 9 : 'LOCKUP'          ,
                        10: 'SYSTEM_RESET' , 11: 'HOST_DEBUGGER'   ,
                        13: 'FAILURE_OF_PERIPHERAL(s)'             ,
                        4 : 'RESERVED', 8 : 'RESERVED', 12 : 'RESERVED',
                        14: 'RESERVED', 15: 'RESERVED'
                      }

        if len(buf) > 13:
            mtrSr = (buf[16]<<24)+(buf[15]<<16)+(buf[14]<<8)+buf[13]
            print ("Meter Serial Number    : " + str(mtrSr))
            
        if buf[12]==0x55:
            print ("type                   : valid data")
        else:
            print ("type                   : invalid data")

        print ("latest wakeup          : " + wakeup[buf[0]])
        print ("valid wakeup counts    : " + str(buf[1]))
        print ("wdog reset counts      : " + str(buf[2]))
        print ("unwanted wakeup counts : " + str(buf[3]))

        resetR  = (buf[5]<<8) + buf[4]
        wakeupR = (buf[9]<<24)+(buf[8]<<16)+(buf[7]<<8)+buf[6]

        RMSG = []
        for i in range(16):
            if resetR & 1<<i:
                RMSG.append(resetReason[i])

        WMSG = []
        for i in range(32):
            if wakeupR & 1<<i:
                WMSG.append(wakeupReason[i])      

        print ("total reset reasons    : " + str(hex(resetR))  + " " +  str(RMSG))

        print ("total wakeup reasons   : " + str(hex(wakeupR)) + " " +  str(WMSG))
        
    @check_errors
    def clear_battery_logs(self,addr):
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.CLEAR_BATT_LOG)

    @check_errors
    def get_bootloader_logs(self, addr):
        buf = bytearray()
        buf = self.my_simpleterm_master.get_param(addr, commandMappingContainer.BOOT_LOGS, BYTE_ARRAY)
        bErrorT = {
                    0 : 'Error: Firmware Magic Number',
                    1 : 'Error: Firmware Protocol Version',
                    2 : 'Error: CRC of header file',
                    3 : 'Error: Sectional CRCs',
                    4 : 'Error: Same External Image'
                 }
        bSign     =  (buf[4]<<24)+(buf[5]<<16)+(buf[6]<<8)+buf[7]
        bVersion  =  (buf[8]) 
        bFwStatus =  (buf[0]<<24)+(buf[1]<<16)+(buf[2]<<8)+buf[3]
        bError    =  (buf[9])
        bTable    =  (buf[10])
        if(len(buf) > 11):
            bProtocol =  (buf[11])
            print ("Bootloader Protocol    : " + str(bProtocol))

        if bSign == 0xBDDBACCA:
            print ("Bootloader Sign        : 1phase Present")
        elif bSign == 0xCEECFBBF: 
            print ("Bootloader Sign        : 3phase Present")   
        else:
            print ("Bootloader Sign        : Absent")

        if bVersion < 10:
            bVersion = bVersion*10
        bVersion = bVersion/10.0
        print ("Bootloader Version     : Ver-" + str(bVersion))

        if bFwStatus == 0xDEADBEEF:
            print ("Firmware Upgrade       : REJECTED")
        elif bFwStatus == 0xFFFFFFFF or bFwStatus == 0:
            print ("Boot Status            : BOOT Successfull")    
        else:
            print ("FUP Magic Number       : " + str(hex(bFwStatus)))
        EMSG = []
        for i in range(6):
            if bError & 1<<i:
                EMSG.append(bErrorT[i])

        if bError == 0x00:
            print ("Boot Error Status      : None")
        else:
            print ("Boot Status            : " +  str(EMSG))

        if bError & 0x08:
            print ("Allocation Table No.   : " + str(bTable))
        return str(bVersion)


    @check_errors
    def get_battery_volt_params(self, addr):
        buf = bytearray()
        buf = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_BATTERY_VOLT_PARAMS, BYTE_ARRAY)
      
        calib_volt          =  (buf[3]<<24)+(buf[2]<<16)+(buf[1]<<8)+buf[0]
        calib_batt_volt     =  (buf[7]<<24)+(buf[6]<<16)+(buf[5]<<8)+buf[4]
        actual_battery_count  =  (buf[11]<<24)+(buf[10]<<16)+(buf[9]<<8)+buf[8]
        actual_battery_volt   =  (buf[15]<<24)+(buf[14]<<16)+(buf[13]<<8)+buf[12]

        print ("Battery_calib_Volt         :"+str(calib_volt))
        print ("Battery_Calib_voltage      :"+str(calib_batt_volt/1000.0)+"v")
        print ("Battery_Actual_Count       :"+str(actual_battery_count))
        print ("Battry_actual_voltage      :"+str(actual_battery_volt/1000.0)+"v")
        # if(len(buf) > 11):
        #     bProtocol =  (buf[11])
        #     print "Bootloader Protocol    : " + str(bProtocol)

        # if bSign == 0xBDDBACCA:
        #     print "Bootloader Sign        : 1phase Present"
        # elif bSign == 0xCEECFBBF: 
        #     print "Bootloader Sign        : 3phase Present"   
        # else:
        #     print "Bootloader Sign        : Absent"

        # if bVersion < 10:
        #     bVersion = bVersion*10
        # bVersion = bVersion/10.0
        # print "Bootloader Version     : Ver-" + str(bVersion)

        # if bFwStatus == 0xDEADBEEF:
        #     print "Firmware Upgrade       : REJECTED"
        # elif bFwStatus == 0xFFFFFFFF or bFwStatus == 0:
        #     print "Boot Status            : BOOT Successfull"    
        # else:
        #     print "FUP Magic Number       : " + str(hex(bFwStatus))

        # EMSG = []
        # for i in range(6):
        #     if bError & 1<<i:
        #         EMSG.append(bErrorT[i])

        # if bError == 0x00:
        #     print "Boot Error Status      : None"
        # else:
        #     print "Boot Status            : " +  str(EMSG)

        # if bError & 0x08:
        #     print "Allocation Table No.   : " + str(bTable)
        # return buf


    @check_errors
    def get_nameplate(self, addr):
        buf = bytearray()
        buf = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_NAMEPLATE, BYTE_ARRAY)

        meterSr   =  (buf[0]<<24)+(buf[1]<<16)+(buf[2]<<8)+buf[3]
        fwVer     =  (buf[4]<<8)+buf[5]
        bVersion  =  buf[6]
        hwVersion =  buf[7]
        proVer    =  buf[8]
        mtrType   =  buf[9]
        curRating =  buf[10]
        manufYr   =  buf[11]+2000 
        toolVer   =  (buf[12] << 8) + buf[13]  

        print ("Meter Serial No               : " + str(meterSr))
        print ("Firmware External Version     : " + str(fwVer))
        print ("Firmware Internal Version     : " + str(toolVer))

        if bVersion < 10:
            bVersion = bVersion*10
        bVersion = bVersion/10.0
        print ("Bootloader Version            : Ver-" + str(bVersion))

        if mtrType == 3:
            if hwVersion == 0:
                print ("Hardware Version      : 3PH-V-T1.0 PCB")
            elif hwVersion == 1: 
                print ("Hardware Version      : 3PH-V-T1.1 PCB") 
            elif hwVersion == 2: 
                print ("Hardware Version      : 3PH-V-P1.0 PCB") 
            elif hwVersion == 3: 
                print ("Hardware Version      : 3PH-V-P1.1 PCB") 
            else:
                print ("Hardware Version      : UNKNOWN")
        elif mtrType == 1:
            if hwVersion == 0:
                print ("Hardware Version      : 3.3I PCB")
            elif hwVersion == 1: 
                print ("Hardware Version      : 3.3 PCB") 
            elif hwVersion == 2: 
                print ("Hardware Version      : WIFI_ISM PCB") 
            elif hwVersion == 3: 
                print ("Hardware Version      : 4.0 PCB") 
            else:
                print ("Hardware Version      : UNKNOWN")
        else:
            print ("Hardware Version          : UNKNOWN")

        print ("Protocol Version              : " + str(proVer))
        print ("Meter Type                    : " + str(mtrType) + "P")
        if curRating == 1:
            print ("Current Rating            : (5-30) A")
        elif curRating == 2:
            print ("Current Rating            : (10-60) A")
        elif curRating == 3:
            print ("Current Rating            : (5-60) A")
        elif curRating == 4:
            print ("Current Rating            : (5-10) A")
        elif curRating == 5:
            print ("Current Rating            : (20-100) A")
        elif curRating == 6:
            print ("Current Rating            : (10-60) A")
        elif curRating == 7:
            print ("Current Rating            : (10-100) A")
        else:
            print ("Current Rating            : UNKNOWN")
        print ("Manufacturing Year            : " + str(manufYr))

    @check_errors
    def tod_enable(self,addr):
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.TOD_ENABLE)
        
    @check_errors
    def tod_disable(self,addr):
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.TOD_DISABLE)

    @check_errors
    def enable_fixed_billing(self,addr):
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.ENABLE_FIXED_BILLING)
        
    @check_errors
    def disable_fixed_billing(self,addr):
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.DISABLE_FIXED_BILLING)

    @check_errors
    def get_disable_fixed_billing_status(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.DISABLE_FIXED_BILLING_STATUS, UINT32)



    @check_errors
    def set_slab_update_ts(self, addr, args):
        dt_string = args.split(",")
        if "now" in dt_string[0]:
            delta = int(dt_string[0].split("+")[1])
            updateTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            updateTime = dateutil.parser.parse(dt_string[0].strip(' '))
        if not isinstance(updateTime, datetime.datetime):
            updateTime = dateutil.parser.parse(updateTime)
        seconds_since_epoch = (
            updateTime -
            datetime.datetime(
                1970,
                1,
                1)).total_seconds()

        meterTime = self.get_time(addr)
        meter_seconds_since_epoch = (
            meterTime -
            datetime.datetime(
                1970,
                1,
                1)).total_seconds()
        if (meter_seconds_since_epoch >= seconds_since_epoch):
            return "Error! Entered update TS cannot be behind the current meter time!"

        return self.my_simpleterm_master.set_param(
            addr,
            commandMappingContainer.SET_SLAB_UPDATE_TS,
            int(seconds_since_epoch),
            UINT32)

    @check_errors
    def set_fd_params(self, addr, args):
        fdp = FixedDeductionPacket()
        fdp.amount = int(args.split(",")[0])
        fdp.type_of_deduction = str(args.split(",")[1])
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_FD_PARAMS, fdp, FIXED_DEDUCTION_PACKET)

    @check_errors
    def unlock(self, addr, unlock_validity):
        unlock_validity = (int(unlock_validity) * 3600 * 24)
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_UNLOCK, unlock_validity, UINT32)

    @check_errors
    def set_fd_update_ts(self, addr, args):
        args = args.split(",")
        if "now" in args[0]:
            delta = int(args[0].split("+")[1])
            updateTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            updateTime = dateutil.parser.parse(args[0].strip(' '))
        if not isinstance(updateTime, datetime.datetime):
            updateTime = dateutil.parser.parse(updateTime)
        seconds_since_epoch = int(
            (updateTime - datetime.datetime(1970, 1, 1)).total_seconds())

        meterTime = self.get_time(addr)
        meter_seconds_since_epoch = (
            meterTime -
            datetime.datetime(
                1970,
                1,
                1)).total_seconds()
        if (meter_seconds_since_epoch > seconds_since_epoch):
            return "Error! Entered update TS cannot be behind the current meter time!"

        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_FD_UPDATE_TS, seconds_since_epoch, UINT32)


# Simpleterm Command Functions
    # push based protocol commands *******************
    @check_errors
    def push_disable(self,addr):
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.DCU_PUSH_DISABLE)
    @check_errors
    def set_push_interval(self, addr, push_interval):
        if int(push_interval) < 30 or int(push_interval) > 3600:
            return "Invalid interval ! \n interval should be between 30 to 3600."
        else:
            push_interval = int(push_interval)/10
            return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_DCU_PUSH_INTERVAL, push_interval, UINT32)
###******************************************************

    @check_errors
    def reset(self, addr, interval):
        interval = int(interval)
        if interval > 255:
            interval = 255
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.BOARD_RESET, interval, UINT8)


    @check_errors
    def gateway(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.GATEWAY)
    
    @check_errors
    def router(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.ROUTER)


    @check_errors
    def assert_false(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.ASSERT_FALSE)


    @check_errors
    def clear_nvm(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_NVM)

    @check_errors
    def clear_account(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_ACCOUNT)



    @check_errors
    def clear_recharges(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_RECHARGES)


    @check_errors
    def deassert(self, addr):
        return self.my_simpleterm_master.execute_command(addr, "x%?")

#    @check_errors
#    def turn_ui_on(self, addr):
#        reply = self.my_simpleterm_master.execute_command(addr, "turn ui on")
#        return reply
#
#    @check_errors
#    def turn_ui_off(self, addr):
#        reply = self.my_simpleterm_master.execute_command(addr, "turn ui off")
#        return reply

    @check_errors
    def dc_cal_i_ofs(self, addr):
        reply = self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.DC_CAL_I_OFS)
        return reply

    @check_errors
    def reset_tamper_latch(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.RESET_TAMPER_LATCH)

    @check_errors
    def turn_relay_on(self, addr):
        reply = self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.TURN_RELAY_ON)
        return reply

    @check_errors
    def turn_relay_off(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.TURN_RELAY_OFF)

    @check_errors
    def relay_manual_control(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.RELAY_MANUAL_CONTROL)

    @check_errors
    def relay_auto_control(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.RELAY_AUTO_CONTROL)

    @check_errors
    def relay_state(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.RELAY_STATE)

    @check_errors
    def syncstream_reset(self, addr):
        return self.my_syncstream_master.reset(addr)

    @check_errors
    def clear_log(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_LOG)

    @check_errors
    def clear_block_load_profile(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_BLOCK_LOAD_PROFILE)

    @check_errors
    def clear_daily_load_profile(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_DAILY_LOAD_PROFILE)

    @check_errors
    def allow_negative_credits(self, addr):
        reply = self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.ALLOW_NEGATIVE_CREDITS)
        return reply


    @check_errors
    def forbid_negative_credits(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.FORBID_NEGATIVE_CREDITS)


    @check_errors
    def reset_tamper_record(self, addr, tamper_type):
        if tamper_type == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.RESET_ALL_TAMPER_RECORD)
        elif tamper_type == "earth":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.RESET_EARTH_TAMPER_RECORD)
        elif tamper_type == "rev":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.RESET_REV_TAMPER_RECORD)
        elif tamper_type == "nm":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.RESET_NM_TAMPER_RECORD)
        elif tamper_type == "nd":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.RESET_ND_TAMPER_RECORD)
        elif tamper_type == "cover":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.RESET_COVER_TAMPER_RECORD)
        elif tamper_type == "mag":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.RESET_MAG_TAMPER_RECORD)

    @check_errors
    def request_recharge(self, addr):
        amount = int(amount)
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.REQUEST_RECHARGE)


    @check_errors
    def enable_elimiter(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.ENABLE_ELIMITER)


    @check_errors
    def disable_elimiter(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.DISABLE_ELIMITER)



    @check_errors
    def enable_lock(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.ENABLE_LOCK)


    @check_errors
    def disable_lock(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.DISABLE_LOCK)


    @check_errors
    def reset_lock(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.RESET_LOCK)


    @check_errors
    def lock_state(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.LOCK_STATE)

    @check_errors
    def check_dlms_activation(self, addr):
        try:
            dlms_flag = True
            dlms_act_check_list = []
            # payload = bytearray([0x00,0x01,0x00,0x10,0x00,0x01,0x00,0x1F,0x60,0x1D,0xA1,0x09,0x06,0x07,0x60,0x85,0x74,0x05,0x08,0x01,0x01,0xBE,0x10,0x04,0x0E,0x01,0x00,0x00,0x00,0x06,0x5F,0x1F,0x04,0x00,0x00,0x18,0x1D,0xFF,0xFF])
            payload1 = bytearray([0x7E,0xA0,0x07,0x03,0x21,0x93,0x0F,0x01,0x7E])
            payload2 = bytearray([0x7E,0xA0,0x2B,0x03,0x21,0x10,0xFB,0xAF,0xE6,0xE6,0x00,0x60,0x1D,0xA1,0x09,0x06,0x07,0x60,0x85,0x74,0x05,0x08,0x01,0x01,0xBE,0x10,0x04,0x0E,0x01,0x00,0x00,0x00,0x06,0x5F,0x1F,0x04,0x00,0x00,0x18,0x1D,0xFF,0xFF,0x5F,0xAF,0x7E])
            payload3 = bytearray([0x7E,0xA0,0x07,0x03,0x21,0x53,0x03,0xC7,0x7E])
            expected_response1 = '7ea01e210373c37a818012050180060180070400000001080400000001533b7e'
            expected_response2 = '7ea0372103306c7ce6e7006129a109060760857405080101a203020100a305a103020100be10040e0800065f1f0400000010020000071cea7e'
            expected_response3 = '7ea01e210373c37a818012050180060180070400000001080400000001533b7e'
            # print len(payload1)
            data_received1 = self.my_tap_handler.send_raw_bytes(payload1,32)
            if isinstance(data_received1, bytes):
                data_received1 = data_received1.decode('ascii').lower()

            if(data_received1 == expected_response1):
                dlms_act_check_list.append(0)
            else:
                dlms_act_check_list.append(1)
            if data_received1:
                print("Data 1")
            else:
                print("No Data 1")

            time.sleep(1)

            data_received2 = self.my_tap_handler.send_raw_bytes(payload2,57)
            if isinstance(data_received2, bytes):
                data_received2 = data_received2.decode('ascii').lower()
            if(data_received2 == expected_response2):
                dlms_act_check_list.append(0)
            else:
                dlms_act_check_list.append(1)

            if data_received2:
                print("Data 2")
            else:
                print("No Data 2")

            time.sleep(1)

            data_received3 = self.my_tap_handler.send_raw_bytes(payload3,32)
            if isinstance(data_received3, bytes):
                data_received3 = data_received3.decode('ascii').lower()
            if(data_received3 == expected_response3):
                dlms_act_check_list.append(0)
            else:
                dlms_act_check_list.append(1)

            if data_received3:
                print("Data 3")
            else:
                print("No Data 3")

            if 1 in dlms_act_check_list:
                dlms_flag = False

            if dlms_flag == False:
                print("DLMS NOT ACTIVATED IN THE METER")
                return 1
            else:
                print("DLMS SUCCESFULLY ACTIVATED IN THE METER")
                return 0
        except:
            print("Not received response of DLMS")
            return 1

    @check_errors
    def broadcast_time(self, addr):
        return self.my_simpletime_master.broadcast_time()


    @check_errors
    def syncstream_bundle(self, addr):
        return self.my_syncstream_master.get_bundle(addr)

    @check_errors
    def syncstream_setup(self, addr, interval):
        return self.my_syncstream_master.setup(addr, interval)

    @check_errors
    def syncstream_params(self, addr):
        return self.my_syncstream_master.get_params(addr)

    @check_errors
    def enable_load_profile(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.ENABLE_LOAD_PROFILE)

    @check_errors
    def disable_load_profile(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.DISABLE_LOAD_PROFILE)

    @check_errors
    def slab_reset(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.SLAB_RESET)

    @check_errors
    def slab_enable_on_update(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.SLAB_ENABLE_ON_UPDATE)

    @check_errors
    def slab_enable(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.SLAB_ENABLE)

    @check_errors
    def slab_disable(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.SLAB_DISABLE)

    @check_errors
    def fd_enable(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.FD_ENABLE)

    @check_errors
    def fd_disable(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.FD_DISABLE)



    @check_errors
    def fd_reset(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.FD_RESET)


    @check_errors
    def factory_init_1(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.FACTORY_INIT_1)

    @check_errors
    def factory_init_2(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.FACTORY_INIT_2)

    @check_errors
    def factory_init_app(self, addr, number):
        payload = int(number)
        if 1 == payload:
            print ("Billing Record Clear")
        if 2 == payload:
            print ("DLMS Log Clear")  
        if 3 == payload:
            print ("Event Records Clear")
        if 4 == payload:
            print ("Load Survey Logs Clear")
        if 5 == payload:
            print ("Power Limit Params Reset")
        if 6 == payload:
            print ("Relay Controller Reset")
        if 7 == payload:
            print ("Recharge Token Clear")
        if 8 == payload:
            print ("Prepaid Logs Clear")
        return self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.FACTORY_INIT_3,
                                                            payload, INT8,RESPONSE_PACKET)

    @check_errors
    def clear_event_by_category(self, addr, number):
        payload = int(number)
        if 1 == payload:
            print ("Current related Record Clear")
        elif 2 == payload:
            print ("Voltage related Record Clear")  
        elif 3 == payload:
            print ("Power related Record Clear")
        elif 4 == payload:
            print ("Transation related Record Clear")
        elif 5 == payload:
            print ("C-open Record Clear")
        elif 6 == payload:
            print ("Control related Record Clear")
        elif 7 == payload:
            print ("Other related Record Clear")
        else:
            print ("Enter b/w 1 to 7")
        return self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.CLEAR_EVENT_BY_RECORD,
                                                            payload, INT8,RESPONSE_PACKET)

# Recharge

    @check_errors
    def recharge(self, addr, arg):

        arg_split = str(arg).split(',')
        amount = round(float(arg_split[0]),2)
        amount = int(amount)
        rupees = float(amount)
        rupees = rupees/100       
        transection_id = int(arg_split[1]) 
        print ("Amount in Rupees - ", rupees)
        return self.my_recharge_master.recharge(addr, amount, transection_id)
        # amount = int(amount)
        # return self.my_recharge_master.recharge(addr, amount)

    @check_errors
    def get_num_recharge_token(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_RECHARGE_LOGS, UINT32)

    @check_errors
    def get_recharge_token_by_index(self, addr,index):
        index = int(index)
        data = self.my_simpleterm_master.set_and_get_param(addr,
            commandMappingContainer.GET_RECHARGE_LOG_BY_INDEX, index, UINT32,BYTE_ARRAY)
        dataLen = len(data)
        if(dataLen == 0):
            return "No Entries Found"

        start_index = index*25
        run_index = 0
        index = 0
        print ("{:<10}{}".format("Index" , "Token"))
        while(dataLen > 3):
            token = serialize.deserialize_uint32(data[index:index+4],"reverse")
            run_index = (index/4)+start_index
            print ("{:<10}{}".format(run_index, token))
            dataLen = dataLen-4
            index = index+4
        return "Done"

    @check_errors
    def get_num_recharge_entries(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_RECHARGE_ENTRIES, UINT32)

    @check_errors
    def get_recharge_entries_by_index(self, addr,index):
        index = int(index)
        data = self.my_simpleterm_master.set_and_get_param(addr,
            commandMappingContainer.GET_RECHARGE_ENTRIES_LOG_BY_INDEX, index, UINT32,BYTE_ARRAY)
        dataLen = len(data)
        if(dataLen == 0):
            return "No Entries Found"
        start_index = index*8
        run_index = 0
        index = 0
        print ("{:<10}{:<15}{:<15}{}")\
                .format("Index" , "Amount", "Token", "Timestamp")
        while(dataLen > 11):
            amount    = serialize.deserialize_int32(data[index:index+4],"reverse")
            token     = serialize.deserialize_uint32(data[index+4:index+8],"reverse")
            timestamp = serialize.deserialize_uint32(data[index+8:index+12],"reverse")
            timestamp = str(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp))
            run_index = (index/12)+start_index

            print ("{:<10}{:<15}{:<15}{}")\
                    .format(run_index, amount, token, timestamp)
            dataLen = dataLen-12
            index = index+12
        return "Done"

    @check_errors
    def recharge_fract(self, addr, amount):
        amount = round(float(amount), 2)
        amount = int(100 * amount)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_RECHARGE_FRACT, amount, INT32N)

    @check_errors
    def beat_time(self, addr):
        unix_time = self.my_syncstream_master.get_current_beat_time()
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=unix_time)



    @check_errors
    def eeprom_write(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        length = int(args[1])
        payload = bytearray()
        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(serialize.serialize_uint16(length))
        data = args[2].split(' ')
        while ' ' in data:
            data.remove(' ')
        for entry in data:
            entry = int(entry, 16)
            payload.append(entry)
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.MEM_EEPROM_WRITE,
                                                   payload, BYTE_ARRAY)
    @check_errors
    def eeprom_read(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        length = int(args[1])
        payload = bytearray()
        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(serialize.serialize_uint16(length))
        return self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.MEM_EEPROM_READ,
                                                            payload, BYTE_ARRAY,BILLING_MD_PACKET)

    @check_errors
    def set_alarm_events(self, addr, line):
        try:
            arg = line.split(",")
            a = int(arg[0])         #just to ensure the at least single entry found
            statusF = 0xFFFFFFFF
            if a != 0:
                for b in range(len(arg)):
                    data = int(arg[b])
                    if data > 0 and data < 24:
                        data = data - 1
                        data = (1 << data)
                        statusF = statusF&(~data)
                    else:
                        print( str(data) + " is out of range : ignoring"  ) 
            payload = bytearray()
            payload.extend(serialize.serialize_uint32(statusF))
        except Exception as e:
            print("Event category should be in the range of 1 to 22 and 0 to reset")
            print("0. RESET (Note: using of 0 with other events will be ignored)")
            print("1. OverVoltage \n2. Undervoltage \n3. R-Ph Missing \n4. Y-Ph Missing \n5. B-Ph Missing \n6. Voltage Unbal \n7. Phase Sequence")
            print("8. R-Ph Reverse \n9. Y-Ph Reverse \n10. B-Ph Reverse \n11. Current Unbal \n12. CT Bypass \n13. R-Ph CT Open \n14. Y-Ph CT Open \n15. B-Ph CT Open \n16. Overcurrent")
            print("17. Magnet \n18. ND \n19. Low PF \n20. Overload \n21. C-Open \n22. Account Empty \n23. PF Malfunction")
        else:
            return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_ALARM_STATUS,payload, BYTE_ARRAY)
            
    @check_errors
    def get_alarm_events(self, addr):
        buf = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_ALARM_STATUS, UINT32)
        bErrorT = {
                    0 : 'OverVoltage',  1 : 'Undervoltage',  2 : 'R-Ph Missing',  3 : 'Y-Ph Missing',
                    4 : 'B-Ph Missing', 5 : 'Voltage Unbal', 6 : 'Phase Sequence',7 : 'R-Ph Reverse',
                    8 : 'Y-Ph Reverse', 9 : 'B-Ph Reverse', 10 : 'Current Unbal',11 : 'CT Bypass',
                    12: 'R-Ph CT Open', 13: 'Y-Ph CT Open', 14 : 'B-Ph CT Open', 15 : 'Overcurrent',
                    16: 'Magnet',       17: 'ND',           18 : 'Low PF',       19 : 'Overload',
                    20 : 'C-Open',      21: 'Account Empty',22 : 'Freq Malfunction'
                 }
        health_mask = []         
        for i in range(len(bErrorT)):
            if (0 == buf&(1<<i)):
                health_mask.append(bErrorT[i])
        return health_mask
    
    @check_errors
    def set_event_ptime2(self, addr):
        try:
            length = len(event_ptime_configuration_list)
            payload = bytearray()
            if length == 21:
                for b in range(21):
                    data1 = event_ptime_configuration_list[b][1]
                    if data1 > 0:
                        payload.extend(serialize.serialize_uint16(data1,"reverse"))
                    else:
                        print("ptime should not be negative or zero")
                        data1 = event_ptime_configuration_list[b][5] #used to raise an error
                for b in range(21):
                    data2 = event_ptime_configuration_list[b][2]
                    if data2 > 0:
                        payload.extend(serialize.serialize_uint16(data2,"reverse"))
                    else:
                        print("ptime should not be negative or zero")
                        data1 = event_ptime_configuration_list[b][5] #used to raise an error
            else:
                print("length is not matching in event_congig_ptime file")            
        except Exception as e:
            print("file has been corrupt")
        else:
            return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_EVENT_PTIME,payload, BYTE_ARRAY)
            
    @check_errors
    def get_event_ptime2(self, addr):
        buf = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_EVENT_PTIME, BYTE_ARRAY)        
        print ("\n{:<25}{:<15}{}".format("EVENT ID","OCCUR PTIME", "RESTORE PTIME"))
        print ("{:<25}{:<15}{}".format("---------------","-----------", "-------------"))
        for i in range(len(event_ptime_configuration_list)):
            idx = i*2
            idm = event_ptime_configuration_list[i][0]
            data1 = (buf[idx+1]<<8)+buf[idx]
            data2 = (buf[idx+39]<<8)+buf[idx+38]
            print ("{:<30}{:<15}{}".format(idm,data1,data2))
        return '!!!'

# Flash IO commands

    @check_errors
    def mem_write(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        data = args[1].split(' ')
        while '' in data:
            data.remove('')
        data_bytearray = bytearray()
        for entry in data:
            entry = int(entry, 16)
            data_bytearray.append(entry)

        return self.my_flash_io_master.write(
            addr, start_address, data_bytearray)

    @check_errors
    def mem_read(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        length = int(args[1])
        return self.my_flash_io_master.read(addr, start_address, length)

    @check_errors
    def mem_erase_block(self, addr, line):
        block_no  = int(line)
        if((block_no > 31) or (block_no <0 )):
            return "No of 64KB available block : 32, Command execution failed"
        return self.my_flash_io_master.erase(addr, int(line))


    @check_errors
    def mem_erase_sector(self, addr, line):
        sector_no  = int(line)
        if(sector_no > 511) or (sector_no <0 ):
            return "No of available sector : 512,  Command execution failed"
        return self.my_flash_io_master.erase(addr, int(line),sector_erase = True)

    @check_errors
    def one_ph_ui_config(self,addr,main_txt_file_path):
        print("I am here ")
        desktop =  os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        path = os.path.join(os.path.join(desktop), main_txt_file_path)
        ui_config_file = open(path, "rb")
        block = ui_config_file.read() 
        hexfile_payload = bytearray() 
        for ch in block:
            hexfile_payload.append(ch)
        length = len(block)   
        if length > 3000: 
          return "invalid binary file" 

        SECTOR_ADDRESS = 0x12B000
        sector_no = SECTOR_ADDRESS/4096
        self.my_flash_io_master.erase(addr, int(sector_no),sector_erase = True)
        new_hex_payload = hexfile_payload
        while len(new_hex_payload) < 4094:
            new_hex_payload.append(0xff)
        crc_calc = _get_crc(new_hex_payload)
        crc_buf = serialize.serialize_uint16(crc_calc,order="reverse")
        for byte in crc_buf:
            new_hex_payload.append(byte)
        self.my_flash_io_master.burn(Address("0.0.0.255"), SECTOR_ADDRESS, new_hex_payload, to_print=True)
        return "1PUI_Okay"


# Maxwell calibration commands

    @check_errors
    def maxwell_cal_time(self, addr, cal_time):
        if cal_time == 0:
            return "Error! This command needs an argument!"
        if cal_time == "now":
            cal_time = datetime.datetime.now()
        if not isinstance(cal_time, datetime.datetime):
            cal_time = dateutil.parser.parse(cal_time)
        payload = get_command_string(TIME_DATE_CODE, cal_time)
        return self.my_maxwell_bridge_master.send(addr, payload)

    @check_errors
    def set_pulse(self, addr, cal_time):
        buff = bytearray()
        var = cal_time.split(",")
        pulse = int(var[0])
        duration = int(var[1])
        buff.extend(serialize.serialize_uint16(pulse))
        buff.extend(serialize.serialize_uint16(duration))
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_PULSE,
                                                   buff, BYTE_ARRAY)

    @check_errors
    def maxwell_cal_mtrno(self, addr, serial_num):
        payload = get_command_string(MTRNO_CODE, serial_num)
        if int(serial_num) < 100000 or int(serial_num) > 999999:
            return "Error! Meter serial number should be in the range of 100000 to 999999!"
        else:
            return self.my_maxwell_bridge_master.send(addr, payload)

    def maxwell_cal_energy(self, addr, error_percent):
        if not isinstance(error_percent, float):
            error_percent = float(error_percent)
        payload = get_command_string(ENERGY_CAL_CODE, float(error_percent))
        return self.my_maxwell_bridge_master.send(addr, payload)

    @check_errors
    def maxwell_clear_1(self, addr):
        payload = get_command_string(CLEAR_1_CODE)
        return self.my_maxwell_bridge_master.send(addr, payload)

    @check_errors
    def maxwell_clear_2(self, addr):
        payload = get_command_string(CLEAR_2_CODE)
        return self.my_maxwell_bridge_master.send(addr, payload)

    def maxwell_cal_v(self, addr):
        payload = get_command_string(VICAL_CODE, 'v')
        return self.my_maxwell_bridge_master.send(addr, payload)

    def maxwell_cal_ip(self, addr):
        payload = get_command_string(VICAL_CODE, 'ip')
        return self.my_maxwell_bridge_master.send(addr, payload)

    def maxwell_cal_in(self, addr):
        payload = get_command_string(VICAL_CODE, 'in')
        return self.my_maxwell_bridge_master.send(addr, payload)

    def maxwell_meter_lock(self, addr):
        return self.my_maxwell_bridge_master.lock(addr)




    @check_errors
    def get_meter_serial_no(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_METER_SERIAL_NO, DATA_ARRAY)

    @check_errors
    def get_relay_status(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.RELAY_STATUS, RELAY_STATUS_1P)

    @check_errors
    def get_3p_relay_status(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_PH_WISE_RELAY_STATUS, RELAY_STATUS_1P)
# RF packet mode commands
    @check_errors
    def trace_path(self, addr):
        return self.rf_command_handler.trace_path(addr)



# E-cop commands

    @check_errors
    def get_metering_data(self, addr):
        return self.my_ecop_data_streamer.send(addr)

    @check_errors
    def get_calib_status(self, addr):
        buf = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_CALIB_STATUS, BYTE_ARRAY)

        sw_calib = (buf[0]<<8)+buf[1]
        hw_calib = buf[2]

        if hw_calib == 0:
            print("HW Locked")
        else:
            print("HW Unlocked")

        if sw_calib == 0xDEAD:
            return "SW Calib Locked !!!"
        elif sw_calib == 0x5AB0 or sw_calib == 0x5ABC:
            return "SW Calib Unlocked !!!"
        elif hw_calib == 1:
            if sw_calib == 0x5AB1 or sw_calib == 0x5AB2 or sw_calib == 0x5AB3:
                return "Under Calibration (SW Calib Unlocked)!!!"
        else:
            return "Un-Calibrated (SW Calib Locked)!!!"

    @check_errors
    def ecop_cal_time(self, addr, date_time):
        return self.my_ecop_data_streamer.ecop_cal_time(addr, date_time)

    @check_errors
    def set_dlog_params(self, addr, lsp):
        return self.my_simpleterm_master.set_param(
            addr, commandMappingContainer.SET_SURVEY_PARAMS, lsp, LOAD_SURVEY_PARAMS)

    @check_errors
    def get_dlog_params(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_SURVEY_PARAMS, LOAD_SURVEY_PARAMS)

    @check_errors
    def get_newest_dlog(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NEWEST_SURVEY, ECOP_PACKET)

    @check_errors
    def get_oldest_dlog(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_OLDEST_SURVEY, ECOP_PACKET)

    @check_errors
    def get_num_dlog(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_SURVEYS, UINT32)

    @check_errors
    def get_dlog_interval(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_SURVEY_PARAMS, UINT32)
    get_dlog_interval.units = "seconds"

    @check_errors
    def clear_dlog(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_BLOCK_LOAD_SURVEY)

    @check_errors
    def enable_dlog(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.ENABLE_SURVEY)

    @check_errors
    def disable_dlog(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.DISABLE_SURVEY)



# Maximum Demand Commands

    @check_errors
    def clear_active_MD_month(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_MD_MONTH_ALL)
        elif MD_month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_MD_MONTH_1)
        elif MD_month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_MD_MONTH_2)
        elif MD_month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_MD_MONTH_3)
        elif MD_month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_MD_MONTH_4)
        elif MD_month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_MD_MONTH_5)
        elif MD_month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_MD_MONTH_6)
        elif MD_month == "0":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_MD_MONTH_7)

    @check_errors
    def clear_reactive_MD_month(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_MD_MONTH_ALL)
        elif MD_month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_MD_MONTH_1)
        elif MD_month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_MD_MONTH_2)
        elif MD_month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_MD_MONTH_3)
        elif MD_month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_MD_MONTH_4)
        elif MD_month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_MD_MONTH_5)
        elif MD_month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_MD_MONTH_6)
        elif MD_month == "0":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_MD_MONTH_7)

    @check_errors
    def clear_apparent_MD_month(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_MD_MONTH_ALL)
        elif MD_month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_MD_MONTH_1)
        elif MD_month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_MD_MONTH_2)
        elif MD_month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_MD_MONTH_3)
        elif MD_month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_MD_MONTH_4)
        elif MD_month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_MD_MONTH_5)
        elif MD_month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_MD_MONTH_6)
        elif MD_month == "0":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_MD_MONTH_7)

    @check_errors
    def clear_active_energy_history(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_ENERGY_HISTORY_ALL)
        elif month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_ENERGY_HISTORY_1)
        elif month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_ENERGY_HISTORY_2)
        elif month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_ENERGY_HISTORY_3)
        elif month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_ENERGY_HISTORY_4)
        elif month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_ENERGY_HISTORY_5)
        elif month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_ACTIVE_ENERGY_HISTORY_6)

    @check_errors
    def clear_reactive_lead_energy_history(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LEAD_ENERGY_HISTORY_ALL)
        elif month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LEAD_ENERGY_HISTORY_1)
        elif month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LEAD_ENERGY_HISTORY_2)
        elif month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LEAD_ENERGY_HISTORY_3)
        elif month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LEAD_ENERGY_HISTORY_4)
        elif month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LEAD_ENERGY_HISTORY_5)
        elif month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LEAD_ENERGY_HISTORY_6)

    @check_errors
    def clear_reactive_lag_energy_history(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LAG_ENERGY_HISTORY_ALL)
        elif month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LAG_ENERGY_HISTORY_1)
        elif month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LAG_ENERGY_HISTORY_2)
        elif month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LAG_ENERGY_HISTORY_3)
        elif month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LAG_ENERGY_HISTORY_4)
        elif month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LAG_ENERGY_HISTORY_5)
        elif month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_REACTIVE_LAG_ENERGY_HISTORY_6)

    @check_errors
    def clear_apparent_energy_history(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_ENERGY_HISTORY_ALL)
        elif month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_ENERGY_HISTORY_1)
        elif month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_ENERGY_HISTORY_2)
        elif month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_ENERGY_HISTORY_3)
        elif month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_ENERGY_HISTORY_4)
        elif month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_ENERGY_HISTORY_5)
        elif month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_APPARENT_ENERGY_HISTORY_6)

    @check_errors
    def clear_billing_date(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_DATE_ALL)
        elif month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_DATE_1)
        elif month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_DATE_2)
        elif month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_DATE_3)
        elif month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_DATE_4)
        elif month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_DATE_5)
        elif month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_DATE_6)
        elif month == "0":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_DATE_7)

    @check_errors
    def clear_system_power_factor(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_SYSTEM_POWER_FACTOR_ALL)
        elif month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_SYSTEM_POWER_FACTOR_1)
        elif month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_SYSTEM_POWER_FACTOR_2)
        elif month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_SYSTEM_POWER_FACTOR_3)
        elif month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_SYSTEM_POWER_FACTOR_4)
        elif month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_SYSTEM_POWER_FACTOR_5)
        elif month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_SYSTEM_POWER_FACTOR_6)
        elif month == "0":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_SYSTEM_POWER_FACTOR_7)

    @check_errors
    def clear_cumulative_billing_count(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_CUMULATIVE_BILLING_COUNT)

    @check_errors
    def clear_billing_power_on_time(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_POWER_ON_TIME_ALL)
        elif month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_POWER_ON_TIME_1)
        elif month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_POWER_ON_TIME_2)
        elif month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_POWER_ON_TIME_3)
        elif month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_POWER_ON_TIME_4)
        elif month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_POWER_ON_TIME_5)
        elif month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_POWER_ON_TIME_6)
        elif month == "0":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_BILLING_POWER_ON_TIME_7)

    @check_errors
    def clear_cumulative_power_on_time(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_CUMULATIVE_POWER_ON_TIME)

    @check_errors
    def clear_cumulative_programming_count(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_CUMULATIVE_PROGRAMMING_COUNT)

    @check_errors
    def get_instantaneous_active_MD(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_INSTANTANEOUS_ACTIVE_MD, UINT32)
    get_instantaneous_active_MD.units = 'watts'

    @check_errors
    def get_current_active_MD(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CURRENT_ACTIVE_MD, MAXIMUM_DEMAND_PACKET)

    @check_errors
    def get_past_active_MD(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_1, MAXIMUM_DEMAND_PACKET)
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_2, MAXIMUM_DEMAND_PACKET)
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_3, MAXIMUM_DEMAND_PACKET)
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_4, MAXIMUM_DEMAND_PACKET)
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_5, MAXIMUM_DEMAND_PACKET)
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_6, MAXIMUM_DEMAND_PACKET)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n".format(month_6,
                                                          month_5,
                                                          month_4,
                                                          month_3,
                                                          month_2,
                                                          month_1)
            return month_all
        elif MD_month == "-6":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_1, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-5":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_2, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-4":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_3, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-3":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_4, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-2":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_5, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-1":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_ACTIVE_MD_6, MAXIMUM_DEMAND_PACKET)

    @check_errors
    def get_instantaneous_reactive_MD(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_INSTANTANEOUS_REACTIVE_MD, UINT32)
    get_instantaneous_reactive_MD.units = 'watts'

    @check_errors
    def get_current_reactive_MD(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CURRENT_REACTIVE_MD, MAXIMUM_DEMAND_PACKET)

    @check_errors
    def get_past_reactive_MD(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_1, MAXIMUM_DEMAND_PACKET)
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_2, MAXIMUM_DEMAND_PACKET)
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_3, MAXIMUM_DEMAND_PACKET)
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_4, MAXIMUM_DEMAND_PACKET)
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_5, MAXIMUM_DEMAND_PACKET)
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_6, MAXIMUM_DEMAND_PACKET)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n".format(month_6,
                                                          month_5,
                                                          month_4,
                                                          month_3,
                                                          month_2,
                                                          month_1)
            return month_all
        elif MD_month == "-6":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_1, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-5":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_2, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-4":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_3, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-3":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_4, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-2":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_5, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-1":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_REACTIVE_MD_6, MAXIMUM_DEMAND_PACKET)

    @check_errors
    def get_instantaneous_apparent_MD(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_INSTANTANEOUS_APPARENT_MD, UINT32)
    get_instantaneous_apparent_MD.units = 'watts'

    @check_errors
    def get_current_apparent_MD(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CURRENT_APPARENT_MD, MAXIMUM_DEMAND_PACKET)
    @check_errors
    def get_billing_info(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_BILLING_INFO,BILLING_MD_PACKET)

    @check_errors
    def get_billing_by_index(self, addr,index):
        if index <= 12:
            return self.my_simpleterm_master.set_and_get_param(addr,commandMappingContainer.GET_BILLING_BY_INDEX, index, UINT32,BILLING_MD_PACKET)
        else:
            return "Invalid value! Event category should be in the range of 0 to 12."

    @check_errors
    def get_billing_tod_by_index(self, addr,index, flag):
        if index <= 12:
            payload = bytearray()
            payload.extend(serialize.serialize_uint32(index))
            payload.extend(serialize.serialize_uint8(flag))
            return self.my_simpleterm_master.set_and_get_param(addr,commandMappingContainer.GET_TOD_BILLING_BY_INDEX, payload, BYTE_ARRAY,BILLING_MD_PACKET)
        else:
            return "Invalid value! Event category should be in the range of 0 to 12."

    @check_errors
    def get_billing_data_by_index(self, addr,index):
        if index <= 12:
            return self.my_simpleterm_master.set_and_get_param(addr,commandMappingContainer.GET_BILLING_DATA_BY_INDEX, index, UINT32,BILLING_MD_PACKET)
        else:
            return "Invalid value! Event category should be in the range of 0 to 12."

    @check_errors
    def get_past_apparent_MD(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_1, MAXIMUM_DEMAND_PACKET)
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_2, MAXIMUM_DEMAND_PACKET)
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_3, MAXIMUM_DEMAND_PACKET)
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_4, MAXIMUM_DEMAND_PACKET)
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_5, MAXIMUM_DEMAND_PACKET)
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_6, MAXIMUM_DEMAND_PACKET)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n".format(month_6,
                                                          month_5,
                                                          month_4,
                                                          month_3,
                                                          month_2,
                                                          month_1)
            return month_all
        elif MD_month == "-6":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_1, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-5":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_2, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-4":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_3, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-3":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_4, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-2":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_5, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-1":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_APPARENT_MD_6, MAXIMUM_DEMAND_PACKET)

    @check_errors
    def get_active_energy_history(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_1, ENERGY_HISTORY_PACKET)
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_2, ENERGY_HISTORY_PACKET)
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_3, ENERGY_HISTORY_PACKET)
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_4, ENERGY_HISTORY_PACKET)
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_5, ENERGY_HISTORY_PACKET)
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_6, ENERGY_HISTORY_PACKET)
            month_7 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_7, ENERGY_HISTORY_PACKET)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(month_7,
                                                              month_6,
                                                              month_5,
                                                              month_4,
                                                              month_3,
                                                              month_2,
                                                              month_1)
            return month_all
        elif month == "-6":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_1, ENERGY_HISTORY_PACKET)
        elif month == "-5":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_2, ENERGY_HISTORY_PACKET)
        elif month == "-4":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_3, ENERGY_HISTORY_PACKET)
        elif month == "-3":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_4, ENERGY_HISTORY_PACKET)
        elif month == "-2":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_5, ENERGY_HISTORY_PACKET)
        elif month == "-1":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_6, ENERGY_HISTORY_PACKET)
        elif month == "0":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_ACTIVE_ENERGY_HISTORY_7, ENERGY_HISTORY_PACKET)

    @check_errors
    def get_reactive_lead_energy_history(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_1,
                ENERGY_HISTORY_PACKET)
            month_2 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_2,
                ENERGY_HISTORY_PACKET)
            month_3 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_3,
                ENERGY_HISTORY_PACKET)
            month_4 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_4,
                ENERGY_HISTORY_PACKET)
            month_5 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_5,
                ENERGY_HISTORY_PACKET)
            month_6 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_6,
                ENERGY_HISTORY_PACKET)
            month_7 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_7,
                ENERGY_HISTORY_PACKET)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(month_7,
                                                              month_6,
                                                              month_5,
                                                              month_4,
                                                              month_3,
                                                              month_2,
                                                              month_1)
            return month_all
        elif month == "-6":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_1,
                ENERGY_HISTORY_PACKET)
        elif month == "-5":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_2,
                ENERGY_HISTORY_PACKET)
        elif month == "-4":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_3,
                ENERGY_HISTORY_PACKET)
        elif month == "-3":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_4,
                ENERGY_HISTORY_PACKET)
        elif month == "-2":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_5,
                ENERGY_HISTORY_PACKET)
        elif month == "-1":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_6,
                ENERGY_HISTORY_PACKET)
        elif month == "0":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LEAD_ENERGY_HISTORY_7,
                ENERGY_HISTORY_PACKET)

    @check_errors
    def get_reactive_lag_energy_history(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_1,
                ENERGY_HISTORY_PACKET)
            month_2 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_2,
                ENERGY_HISTORY_PACKET)
            month_3 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_3,
                ENERGY_HISTORY_PACKET)
            month_4 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_4,
                ENERGY_HISTORY_PACKET)
            month_5 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_5,
                ENERGY_HISTORY_PACKET)
            month_6 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_6,
                ENERGY_HISTORY_PACKET)
            month_7 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_7,
                ENERGY_HISTORY_PACKET)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(month_7,
                                                              month_6,
                                                              month_5,
                                                              month_4,
                                                              month_3,
                                                              month_2,
                                                              month_1)
            return month_all
        elif month == "-6":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_1,
                ENERGY_HISTORY_PACKET)
        elif month == "-5":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_2,
                ENERGY_HISTORY_PACKET)
        elif month == "-4":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_3,
                ENERGY_HISTORY_PACKET)
        elif month == "-3":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_4,
                ENERGY_HISTORY_PACKET)
        elif month == "-2":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_5,
                ENERGY_HISTORY_PACKET)
        elif month == "-1":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_6,
                ENERGY_HISTORY_PACKET)
        elif month == "0":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_REACTIVE_LAG_ENERGY_HISTORY_7,
                ENERGY_HISTORY_PACKET)

    @check_errors
    def get_apparent_energy_history(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_1,
                ENERGY_HISTORY_PACKET)
            month_2 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_2,
                ENERGY_HISTORY_PACKET)
            month_3 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_3,
                ENERGY_HISTORY_PACKET)
            month_4 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_4,
                ENERGY_HISTORY_PACKET)
            month_5 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_5,
                ENERGY_HISTORY_PACKET)
            month_6 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_6,
                ENERGY_HISTORY_PACKET)
            month_7 = self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_7,
                ENERGY_HISTORY_PACKET)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(month_7,
                                                              month_6,
                                                              month_5,
                                                              month_4,
                                                              month_3,
                                                              month_2,
                                                              month_1)
            return month_all
        elif month == "-6":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_1,
                ENERGY_HISTORY_PACKET)
        elif month == "-5":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_2,
                ENERGY_HISTORY_PACKET)
        elif month == "-4":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_3,
                ENERGY_HISTORY_PACKET)
        elif month == "-3":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_4,
                ENERGY_HISTORY_PACKET)
        elif month == "-2":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_5,
                ENERGY_HISTORY_PACKET)
        elif month == "-1":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_6,
                ENERGY_HISTORY_PACKET)
        elif month == "0":
            return self.my_simpleterm_master.get_param(
                addr,
                commandMappingContainer.GET_APPARENT_ENERGY_HISTORY_7,
                ENERGY_HISTORY_PACKET)

    @check_errors
    def get_billing_date(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_1, UINT32)
            time_1 = datetime.datetime(
                1970, 1, 1) + datetime.timedelta(seconds=month_1)
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_2, UINT32)
            time_2 = datetime.datetime(
                1970, 1, 1) + datetime.timedelta(seconds=month_2)
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_3, UINT32)
            time_3 = datetime.datetime(
                1970, 1, 1) + datetime.timedelta(seconds=month_3)
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_4, UINT32)
            time_4 = datetime.datetime(
                1970, 1, 1) + datetime.timedelta(seconds=month_4)
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_5, UINT32)
            time_5 = datetime.datetime(
                1970, 1, 1) + datetime.timedelta(seconds=month_5)
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_6, UINT32)
            time_6 = datetime.datetime(
                1970, 1, 1) + datetime.timedelta(seconds=month_6)
            month_7 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_7, UINT32)
            time_7 = datetime.datetime(
                1970, 1, 1) + datetime.timedelta(seconds=month_7)
            time_all = "Month 0: {}\nMonth -1: {}\nMonth -2: {}\nMonth -3: {}\nMonth -4: {}\nMonth -5: {}\nMonth -6: {}\n".format(
                time_7, time_6, time_5, time_4, time_3, time_2, time_1)
            return time_all
        elif month == "-6":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_1, UINT32)
            return datetime.datetime(1970, 1, 1) + \
                datetime.timedelta(seconds=month_1)
        elif month == "-5":
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_2, UINT32)
            return datetime.datetime(1970, 1, 1) + \
                datetime.timedelta(seconds=month_2)
        elif month == "-4":
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_3, UINT32)
            return datetime.datetime(1970, 1, 1) + \
                datetime.timedelta(seconds=month_3)
        elif month == "-3":
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_4, UINT32)
            return datetime.datetime(1970, 1, 1) + \
                datetime.timedelta(seconds=month_4)
        elif month == "-2":
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_5, UINT32)
            return datetime.datetime(1970, 1, 1) + \
                datetime.timedelta(seconds=month_5)
        elif month == "-1":
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_6, UINT32)
            return datetime.datetime(1970, 1, 1) + \
                datetime.timedelta(seconds=month_6)
        elif month == "0":
            month_7 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_DATE_7, UINT32)
            return datetime.datetime(1970, 1, 1) + \
                datetime.timedelta(seconds=month_7)

    @check_errors
    def get_system_power_factor(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_1, INT32) / 1000.0
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_2, INT32) / 1000.0
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_3, INT32) / 1000.0
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_4, INT32) / 1000.0
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_5, INT32) / 1000.0
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_6, INT32) / 1000.0
            month_7 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_7, INT32) / 1000.0
            month_all = "Month 0: {}\nMonth -1: {}\nMonth -2: {}\nMonth -3: {}\nMonth -4: {}\nMonth -5: {}\nMonth -6: {}\n".format(
                month_7, month_6, month_5, month_4, month_3, month_2, month_1)
            return month_all
        elif month == "-6":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_1, INT32) / 1000.0
        elif month == "-5":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_2, INT32) / 1000.0
        elif month == "-4":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_3, INT32) / 1000.0
        elif month == "-3":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_4, INT32) / 1000.0
        elif month == "-2":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_5, INT32) / 1000.0
        elif month == "-1":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_6, INT32) / 1000.0
        elif month == "0":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_SYSTEM_POWER_FACTOR_7, INT32) / 1000.0

    @check_errors
    def get_cumulative_billing_count(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CUMULATIVE_BILLING_COUNT, UINT32)

    @check_errors
    def get_billing_power_on_time(self, addr, month):
        month = month.strip(' ')
        if month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_1, UINT32)
            month_1_day = month_1 / 86400
            month_1 -= month_1_day * 86400
            month_1_hour = month_1 / 3600
            month_1 -= month_1_hour * 3600
            month_1_min = month_1 / 60
            month_1 -= month_1_min * 60
            month_1_sec = month_1

            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_2, UINT32)
            month_2_day = month_2 / 86400
            month_2 -= month_2_day * 86400
            month_2_hour = month_2 / 3600
            month_2 -= month_2_hour * 3600
            month_2_min = month_2 / 60
            month_2 -= month_2_min * 60
            month_2_sec = month_2

            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_3, UINT32)
            month_3_day = month_3 / 86400
            month_3 -= month_3_day * 86400
            month_3_hour = month_3 / 3600
            month_3 -= month_3_hour * 3600
            month_3_min = month_3 / 60
            month_3 -= month_3_min * 60
            month_3_sec = month_3

            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_4, UINT32)
            month_4_day = month_4 / 86400
            month_4 -= month_4_day * 86400
            month_4_hour = month_4 / 3600
            month_4 -= month_4_hour * 3600
            month_4_min = month_4 / 60
            month_4 -= month_4_min * 60
            month_4_sec = month_4

            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_5, UINT32)
            month_5_day = month_5 / 86400
            month_5 -= month_5_day * 86400
            month_5_hour = month_5 / 3600
            month_5 -= month_5_hour * 3600
            month_5_min = month_5 / 60
            month_5 -= month_5_min * 60
            month_5_sec = month_5

            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_6, UINT32)
            month_6_day = month_6 / 86400
            month_6 -= month_6_day * 86400
            month_6_hour = month_6 / 3600
            month_6 -= month_6_hour * 3600
            month_6_min = month_6 / 60
            month_6 -= month_6_min * 60
            month_6_sec = month_6

            month_7 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_7, UINT32)
            month_7_day = month_7 / 86400
            month_7 -= month_7_day * 86400
            month_7_hour = month_7 / 3600
            month_7 -= month_7_hour * 3600
            month_7_min = month_7 / 60
            month_7 -= month_7_min * 60
            month_7_sec = month_7

            month_all = "Month 0: {} d {} h {} m {} s\nMonth -1: {} d {} h {} m {} s\nMonth -2: {} d {} h {} m {} s\nMonth -3: {} d {} h {} m {} s\nMonth -4: {} d {} h {} m {} s\nMonth -5: {} d {} h {} m {} s\nMonth -6: {} d {} h {} m {} s\n".format(
                month_7_day,
                month_7_hour,
                month_7_min,
                month_7_sec,
                month_6_day,
                month_6_hour,
                month_6_min,
                month_6_sec,
                month_5_day,
                month_5_hour,
                month_5_min,
                month_5_sec,
                month_4_day,
                month_4_hour,
                month_4_min,
                month_4_sec,
                month_3_day,
                month_3_hour,
                month_3_min,
                month_3_sec,
                month_2_day,
                month_2_hour,
                month_2_min,
                month_2_sec,
                month_1_day,
                month_1_hour,
                month_1_min,
                month_1_sec)
            return month_all

        elif month == "-6":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_1, UINT32)
            month_1_day = month_1 / 86400
            month_1 -= month_1_day * 86400
            month_1_hour = month_1 / 3600
            month_1 -= month_1_hour * 3600
            month_1_min = month_1 / 60
            month_1 -= month_1_min * 60
            month_1_sec = month_1
            return "{} d {} h {} m {} s".format(
                month_1_day, month_1_hour, month_1_min, month_1_sec)

        elif month == "-5":
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_2, UINT32)
            month_2_day = month_2 / 86400
            month_2 -= month_2_day * 86400
            month_2_hour = month_2 / 3600
            month_2 -= month_2_hour * 3600
            month_2_min = month_2 / 60
            month_2 -= month_2_min * 60
            month_2_sec = month_1
            return "{} d {} h {} m {} s".format(
                month_2_day, month_2_hour, month_2_min, month_2_sec)

        elif month == "-4":
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_3, UINT32)
            month_3_day = month_3 / 86400
            month_3 -= month_3_day * 86400
            month_3_hour = month_3 / 3600
            month_3 -= month_3_hour * 3600
            month_3_min = month_3 / 60
            month_3 -= month_3_min * 60
            month_3_sec = month_3
            return "{} d {} h {} m {} s".format(
                month_3_day, month_3_hour, month_3_min, month_3_sec)

        elif month == "-3":
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_4, UINT32)
            month_4_day = month_4 / 86400
            month_4 -= month_4_day * 86400
            month_4_hour = month_4 / 3600
            month_4 -= month_4_hour * 3600
            month_4_min = month_4 / 60
            month_4 -= month_4_min * 60
            month_4_sec = month_4
            return "{} d {} h {} m {} s".format(
                month_4_day, month_4_hour, month_4_min, month_4_sec)

        elif month == "-2":
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_5, UINT32)
            month_5_day = month_5 / 86400
            month_5 -= month_5_day * 86400
            month_5_hour = month_5 / 3600
            month_5 -= month_5_hour * 3600
            month_5_min = month_5 / 60
            month_5 -= month_5_min * 60
            month_5_sec = month_5
            return "{} d {} h {} m {} s".format(
                month_5_day, month_5_hour, month_5_min, month_5_sec)

        elif month == "-1":
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_6, UINT32)
            month_6_day = month_6 / 86400
            month_6 -= month_6_day * 86400
            month_6_hour = month_6 / 3600
            month_6 -= month_6_hour * 3600
            month_6_min = month_6 / 60
            month_6 -= month_6_min * 60
            month_6_sec = month_6
            return "{} d {} h {} m {} s".format(
                month_6_day, month_6_hour, month_6_min, month_6_sec)

        elif month == "0":
            month_7 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_BILLING_POWER_ON_TIME_7, UINT32)
            month_7_day = month_7 / 86400
            month_7 -= month_7_day * 86400
            month_7_hour = month_7 / 3600
            month_7 -= month_7_hour * 3600
            month_7_min = month_7 / 60
            month_7 -= month_7_min * 60
            month_7_sec = month_7
            return "{} d {} h {} m {} s".format(
                month_7_day, month_7_hour, month_7_min, month_7_sec)

    @check_errors
    def get_cumulative_power_on_time(self, addr):
        pod = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CUMULATIVE_POWER_ON_TIME, UINT32)
        pod_day = pod / 86400
        pod -= pod_day * 86400
        pod_hour = pod / 3600
        pod -= pod_hour * 3600
        pod_min = pod / 60
        pod -= pod_min * 60
        pod_sec = pod
        return "{} d {} h {} m {} s".format(
            pod_day, pod_hour, pod_min, pod_sec)

    @check_errors
    def get_cumulative_programming_count(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CUMULATIVE_PROGRAMMING_COUNT, UINT32)

    @check_errors
    def get_billing_timestamp(self, addr):
        billing_timestamp = self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_BILLING_TIMESTAMP, UINT32)
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=billing_timestamp)

    @check_errors
    def get_MD_avg_period(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_MD_AVG_PERIOD, UINT32)
    get_MD_avg_period.units = 'minutes'

    @check_errors
    def set_billing_timestamp(self, addr, billing_timestamp):
        if billing_timestamp == 0:
            return "Error! This command needs an argument!"
        if billing_timestamp == "now":
            billing_timestamp = datetime.datetime.now()
        if not isinstance(billing_timestamp, datetime.datetime):
            billing_timestamp = dateutil.parser.parse(billing_timestamp)

        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = int(
            (billing_timestamp - unix_time_zero).total_seconds())
        return self.my_simpleterm_master.set_param(
            addr,
            commandMappingContainer.SET_BILLING_TIMESTAMP,
            seconds_since_epoch,
            UINT32)

    @check_errors
    def set_MD_avg_period(self, addr, avg_period):
        avg_period = int(avg_period)
        if avg_period == 0:
            avg_period = 30

        if avg_period == 15 or avg_period == 30 or avg_period == 60:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_MD_AVG_PERIOD, avg_period, UINT32)
        else:
            return "MD averaging period must be 15/30/60 minutes"

    @check_errors
    def get_MD_LCD_display(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_MD_PAST_LCD_DISPLAY, UINT32)

    @check_errors
    def set_MD_LCD_display(self, addr, past_display):
        past_display = int(past_display)
        if past_display < 0 or past_display > 6:
            return "Invalid value! Value must be in the range of 0-6."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_MD_PAST_LCD_DISPLAY, past_display, UINT32)


# Tamper Logger Commands

    @check_errors
    def clear_tamper_log(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_TAMPER_LOG)

    @check_errors
    def get_tamper_logger_period(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_TAMPER_LOGGER_PERIOD, UINT32)
    get_tamper_logger_period.units = 'seconds'

    @check_errors
    def get_num_tamper_logs(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_TAMPER_LOGS, UINT32)

    @check_errors
    def set_tamper_logger_period(self, addr, persistence_period):
        persistence_period = int(persistence_period)
        # if persistence_period < 1 or persistence_period > 1000:
            # return "Invalid value! Value must be in the range of 1-1000 seconds."
        # elif (persistence_period % 4) != 0:
            # return "Invalid value! Value must be a multiple of 4."
        # else:
        return self.my_simpleterm_master.set_param(
            addr,
            commandMappingContainer.SET_TAMPER_LOGGER_PERIOD,
            persistence_period,
            UINT32)

# Undervoltage Threshold Commands

    @check_errors
    def get_undervoltage_threshold(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_UNDERVOLTAGE_THRESHOLD, UINT32)
    get_undervoltage_threshold.units = 'volts'

    @check_errors
    def set_undervoltage_threshold(self, addr, threshold):
        threshold = int(threshold)
        if threshold < 0 or threshold > 65535:
            return "Invalid value! Value must be in the range of 0-65535."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_UNDERVOLTAGE_THRESHOLD, threshold, UINT32)

# Power Failure Commands

    @check_errors
    def clear_power_failure_duration(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_POWER_FAILURE_DURATION)

    @check_errors
    def clear_power_failure_count(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_POWER_FAILURE_COUNT)

    @check_errors
    def get_power_failure_duration(self, addr):
        pfd = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_POWER_FAILURE_DURATION, UINT32)
        pfd_day = pfd/86400
        pfd -= pfd_day*86400
        pfd_hour = pfd/3600
        pfd -= pfd_hour*3600
        pfd_min = pfd/60
        pfd -= pfd_min*60
        pfd_sec = pfd
        return "{} d {} h {} m {} s".format(pfd_day, pfd_hour, pfd_min, pfd_sec)

    @check_errors
    def get_power_failure_count(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_POWER_FAILURE_COUNT, UINT32)

# Event Record Commands

    @check_errors
    def clear_event_record(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.CLEAR_EVENT_RECORD)

    def enable_event_record(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.ENABLE_EVENT_RECORD)

    def disable_event_record(self, addr):
        return self.my_simpleterm_master.execute_command(
            addr, commandMappingContainer.DISABLE_EVENT_RECORD)

    @check_errors
    def get_newest_event_record(self, addr, index):
        index = int(index)
        if index < 1 or index > 8:
            return "Invalid value! Event category should be in the range of 1 to 5.\n 1. Current Related Events \n 2. Power Related Events \n 3. Transaction Related Events \n 4. Other Events \n 5. Non Rollover Events"
        else:
            number_of_records = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_NUM_EVENT_RECORD, EVENT_RECORD_TOTAL_PACKET)
            number_of_records = str(number_of_records)
            arg = number_of_records.split("\n")
            event = ['0']
            try:
                for line_number in range(1, 8):
                    event.append(int(arg[line_number].split(": ")[1]))
            except Exception as e:
                print (e)

            values = int(event[index])
            values = values - 1
            if (values == -1):
                return "No records found!"
            else:
                return self.my_simpleterm_master.set_and_get_param(
                    addr,
                    commandMappingContainer.GET_NEWEST_EVENT_RECORD,
                    index,
                    UINT32,
                    EVENT_RECORD_PACKET)

    @check_errors
    def get_oldest_event_record(self, addr, index):
        index = int(index)
        if index < 1 or index > 5:
            return "Invalid value! Event category should be in the range of 1 to 5.\n 1. Current Related Events \n 2. Power Related Events \n 3. Transaction Related Events \n 4. Other Events \n 5. Non Rollover Events"
        else:
            number_of_records = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_NUM_EVENT_RECORD, EVENT_RECORD_TOTAL_PACKET)
            number_of_records = str(number_of_records)
            arg = number_of_records.split("\n")
            event = ['0']
            try:
                for line_number in range(1, 6):
                    event.append(int(arg[line_number].split(": ")[1]))
            except Exception as e:
                print (e)

            values = int(event[index])
            values = values - 1
            if (values == -1):
                return "No records found!"
            else:
                return self.my_simpleterm_master.set_and_get_param(
                    addr,
                    commandMappingContainer.GET_OLDEST_EVENT_RECORD,
                    index,
                    UINT32,
                    EVENT_RECORD_PACKET)

    @check_errors
    def get_num_event_record(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_EVENT_RECORD, EVENT_RECORD_TOTAL_PACKET)

    @check_errors
    def get_event_record_by_index(self, addr, event_category, index):
        if event_category < 1 or event_category > 8:
            return "Event category should be in the range of 1 to 8.\n 1. Current Related Events \n 2. Voltage Related Events \n 3. Power Related Events \n 4. Transaction Related Events \n 5. Non-roll over Related Events \n 6. Control Related Events \n 7. Other Related Events\n 8. RF Related Events"
        if index < 0 or index > 340:
            return "Invalid value! Index should be in the range of 0 to 340."
        else:
            number_of_records = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_NUM_EVENT_RECORD, EVENT_RECORD_TOTAL_PACKET)
            number_of_records = str(number_of_records)
            arg = number_of_records.split("\n")
            event = ['0']
            try:
                for line_number in range(1, 9):
                    event.append(int(arg[line_number].split(": ")[1]))
            except Exception as e:
                print (e)

            values = int(event[event_category])
            values = values - 1
            if (values == -1):
                return "No records found!"
            elif (index > values):
                return "Error! Index cannot be higher than number of record entries."
            else:
                buf = bytearray()
                if event_category >=8:
                    event_category = event_category+1
                buf.extend(serialize.serialize_uint32(event_category))
                buf.extend(serialize.serialize_uint32(index))
                return self.my_simpleterm_master.set_and_get_param(
                    addr,
                    commandMappingContainer.GET_EVENT_RECORD_BY_INDEX,
                    buf,
                    BYTE_ARRAY,
                    EVENT_RECORD_PACKET)

    @check_errors
    def get_metering_record_by_index(self, addr,index):
        if index <= 720:
            return self.my_simpleterm_master.set_and_get_param(addr,commandMappingContainer.GET_NXP_PARAMS_BY_INDEX, index, UINT32,METERING_DATA_PACKET)
        else:
            return "Index is out of range (max. upto 720)"

    @check_errors
    def get_num_metering_record(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_NUM_NXP_PARAMS, UINT32)

    @check_errors
    def clear_metering_record(self, addr):
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.CLEAR_NXP_PARAMS)

    @check_errors
    def set_metering_record_interval(self, addr, line):
        try:
            seconds = int(line)
            payload = bytearray()
            payload.extend(serialize.serialize_uint16(seconds))
            payload.extend(serialize.serialize_uint8(0x55))
            return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_GET_NXP_PARAMS_INTERVAL,
                                                       payload, BYTE_ARRAY)
        except:
            print("Usage: set_metering_record_interval : seconds")

    @check_errors
    def get_metering_record_interval(self, addr):
            payload = bytearray()
            seconds = 30;
            payload.extend(serialize.serialize_uint16(seconds))
            payload.extend(serialize.serialize_uint8(0x11))
            sts = self.my_simpleterm_master.set_and_get_param(addr,
                        commandMappingContainer.SET_GET_NXP_PARAMS_INTERVAL, payload, BYTE_ARRAY, UINT16)
            seconds = sts%256
            sts = sts/256
            seconds = (seconds*256) + sts
            return seconds

    @check_errors
    def get_metering_samples_by_index(self, addr,index):
        if index <= 720:
            buf = bytearray()
            buf =  self.my_simpleterm_master.set_and_get_param(addr,commandMappingContainer.GET_NXP_SAMPLES_BY_INDEX, index, UINT32,BYTE_ARRAY)
            
            try:
                index = 0
                sampleType = serialize.deserialize_uint16(buf[index:index+2], "reverse")
                index = index+2

                currentSmpl = []
                voltageSmpl = []

                numSmpl = 32
                while(numSmpl):
                    voltageSmpl.append(serialize.deserialize_int16(buf[index:index+2], "reverse"))
                    index   += 2
                    numSmpl -= 1

                numSmpl = 32
                while(numSmpl):
                    #value = serialize.deserialize_int32(buf[index:index+4])
                    value = (buf[index+1]<<24)+(buf[index]<<16)+(buf[index+3]<<8)+(buf[index+2])
                    if(value & 0x80000000):
                        value = ((value - 0xFFFFFFFF) - 0x00000001)
                    currentSmpl.append(value)
                    index   += 4
                    numSmpl -= 1

                if 0 == sampleType:
                    sampleType = "R_Phase"
                elif 1 == sampleType:
                    sampleType = "Y-Phase"
                elif 2 == sampleType:
                    sampleType = "B-Phase"

                print("Type of Sample : ",sampleType)
                print("Voltage Sample : ",voltageSmpl)
                print("Current Sample : ",currentSmpl)

                #plt.plot(voltageSmpl, label="Voltage")
                plt.plot(currentSmpl, label="Current")
                plt.legend()
                plt.show()
                return ""
            except:
                print ("length : ",len(buf))
        else:
            return "Index is out of range (max. upto 720)"

    @check_errors
    def get_num_metering_samples_record(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_NUM_NXP_SAMPLES, UINT32)

    @check_errors
    def clear_metering_samples_record(self, addr):
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.CLEAR_NXP_SAMPLES)


    @check_errors
    def metering_record_print_direct(self, addr):
        values = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_NUM_NXP_PARAMS, UINT32)
        records = values
        print("Total Records Founds : "+ str(records))
        #print number_or_records
        if values == 0:
            return "No Records found !!!"

        values = values-1
        flag = True
        print ("{:<8}{:<21}{:<8}{:<8}{:<36}{:<36}{} \n"
               "{:<8}{:<21}{:<8}{:<8}{:<36}{:<36}{}".format(
                "Index", "DateTime", "Freq","N-Cur","V1     , A1    , PF1  , kW1      ",
                "V2     , A2    , PF2  , kW2      ","V3     , A3    , PF3  , kW3      ",
                "------","-------------------","------","------","---------------------------------",
                "---------------------------------","---------------------------------"))
        while(flag):
            reply = None
            while reply is None:
                try:
                    reply = self.my_simpleterm_master.set_and_get_param(addr,
                        commandMappingContainer.GET_NXP_PARAMS_BY_INDEX, values, UINT32,
                        METERING_DATA_PACKET,commandMappingContainer.PRINT_DIRECT)
                    print (reply)
                except Exception as e:
                    print ("retrying for Index: ", str(values))
                    pass
            values = values -1
            if (values == -1):
                flag = False
        print ("Total Records : "+ str(records))
        return " "
# 1P Metering Data

    @check_errors
    def get_3p_metering_data(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_1P_METERING_DATA, METERING_DATA_PACKET)

    @check_errors
    def get_THD_data(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_THD, METERING_DATA_PACKET)
    @check_errors
    def get_3p_metering_data2(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_METERING_DATA_IM2, METERING_DATA_PACKET)
    @check_errors
    def get_3p_HR_energy_values(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_METERING_DATA_IM3, METERING_DATA_PACKET)

    @check_errors
    def dcu_data_bundle(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_SYNCSTREAM_BUNDLE, BUNDLE_1P)

    @check_errors
    def get_3p_calib_cofficient(self, addr,isReturn=0):

        line = "0x180,114"  #calibration cofficients address for 3p meter
        args = line.split(',')
        start_address = int(args[0], 16)
        length = int(args[1])
        payload = bytearray()
        payload.extend(serialize.serialize_uint32(start_address))
        payload.extend(serialize.serialize_uint16(length))
        payload1 = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.MEM_EEPROM_READ,
                                                            payload, BYTE_ARRAY,BYTE_ARRAY)
        data2 = [hex(b) for b in payload1]
        formatted_data2 =",".join(data2)

        def return_calib_cofficient(payload1):
            # payload = "0xad,0xde,0xef,0xbe,0xc8,0x0,0x80,0x3f,0x4d,0xcf,0x16,0x36,0x40,0xc5,0x78,0x36,0x5f,0x96,0xc2,0x34,0xc8,0x94,0x12,0x2d,0x42,0x1e,0xc2,0x2b,0x40,0x44,0xe5,0x3c,0x0,0x41,0x99,0x3b"
            payload = payload1
            # Convert the payload string back to a list of integers
            payload = [int(x, 16) for x in payload.split(',')]
            return_dict = {}

            parser  = [
                ['CalibStatus',4],
                ['FrequencyCoeff','float_val'],
                ['VCoeff[R]','float_val'],
                ['VCoeff[Y]','float_val'],
                ['VCoeff[B]','float_val'],
                ['ICoeff[R]','float_val'],
                ['ICoeff[Y]','float_val'],
                ['ICoeff[B]','float_val'],
                ['ICoeff[N]','float_val'],
                ['ActPowerCoeff[R]','float_val'],
                ['ActPowerCoeff[Y]','float_val'],
                ['ActPowerCoeff[B]','float_val'],
                ['PhAngle[R]','float_val'],
                ['PhAngle[Y]','float_val'],
                ['PhAngle[B]','float_val'],
                ['FinalPhAngle[R]','float_val'],
                ['FinalPhAngle[Y]','float_val'],
                ['FinalPhAngle[B]','float_val'],
                ['VFCoeff[R]','float_val'],
                ['VFCoeff[Y]','float_val'],
                ['VFCoeff[B]','float_val'],
                ['IFCoeff[R]','float_val'],
                ['IFCoeff[Y]','float_val'],
                ['IFCoeff[B]','float_val'],
                ['IFCoeff[N]','float_val'],
                ['PhAngleF[R]','float_val'],
                ['PhAngleF[Y]','float_val'],
                ['PhAngleF[B]','float_val'],
                ['RTCCompValue',1],
                ['RTCCompInterval',1],
                ['PhCalibDone',1],
                ['NuCalibDone',1],
                ['FreCalibDone',1],
                ['FreLowerCalibDone',1]
            ]

            if len(payload) == 0:
                print("no payload !!!")
            else:
                print("payload len -: " + str(len(payload)))
                if len(parser) == 0:
                    print("no parser !!!")
                else:
                    index_payload  = 0
                    length_payload = len(payload)

                    index_parser  = 0
                    length_parser = len(parser)

                    while length_payload > 0 and length_parser > 0:
                        msglen = parser[index_parser][1]

                        if msglen == 'date_time':
                            msglen = 4
                        elif msglen == 'time':
                            msglen = 2
                        elif msglen == 'float_val':
                            msglen = 4
                        if msglen > length_payload:
                            break

                        index = 1
                        value = 0
                        while index <= msglen:
                            value = (value << 8) + payload[index_payload + msglen - index]
                            index += 1

                        if parser[index_parser][1] == 'date_time':
                            print(parser[index_parser][0] + " : " + str(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=value)))
                            return_dict[parser[index_parser][0]] = str(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=value))
                        elif parser[index_parser][1] == 'time':
                            print(parser[index_parser][0] + " : " + str(datetime.timedelta(minutes=value)))
                            return_dict[parser[index_parser][0]] = str(datetime.timedelta(minutes=value))
                        elif parser[index_parser][1] == 'float_val':
                            index = 1
                            buf = [0, 0, 0, 0]
                            while index <= msglen:
                                buf[msglen - index] = payload[index_payload + msglen - index]
                                index += 1
                            ba = bytearray(buf)
                            [valuef] = struct.unpack("f", ba)
                            print(parser[index_parser][0] + " : " + str(valuef))
                            return_dict[parser[index_parser][0]] = str(valuef)
                        else:
                            print(parser[index_parser][0] + " : " + str(value))
                            return_dict[parser[index_parser][0]] = str(value)

                        index_payload  += msglen
                        length_payload -= msglen

                        if (length_parser == 1) and (length_payload >= msglen):
                            index_parser  = 0
                        else:
                            index_parser  += 1
                            length_parser -= 1
            return return_dict

        data = return_calib_cofficient(formatted_data2)
        return data
    


# Syncstream Client

    @check_errors
    def get_syncstream_interval(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_SYNCSTREAM_INTERVAL, UINT32)
    get_syncstream_interval.units = 'minutes'

    @check_errors
    def set_syncstream_interval(self, addr, syncstream_interval):
        syncstream_interval = int(syncstream_interval)
        return self.my_simpleterm_master.set_param(
            addr,
            commandMappingContainer.SET_SYNCSTREAM_INTERVAL,
            syncstream_interval,
            UINT32)

    @check_errors
    def get_syncstream_bundle(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_SYNCSTREAM_BUNDLE, SYNCSTREAM_BUNDLE)

    #--------------------------------------------------------------------------------------------------#
    #--------------------------------------------------------------------------------------------------#
    #-------------------------------------3 Phase Commands Start Here----------------------------------#
    #--------------------------------------------------------------------------------------------------#
    #--------------------------------------------------------------------------------------------------#

        '''
    3 phase things start from here
    '''
    ''' TARIFF-RELEATED COMMANDS'''
    '''-------------------------'''
    @check_errors
    def three_ph_get_accounting_state(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr,
            commandMappingContainer_3P.GET_ACTIVE_SLAB_INFO_3P,
            ACCOUNTING_STATE_PACKET_3P)

    @check_errors
    def three_ph_get_slab_update_ts(self, addr):
        update_ts = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SLAB_UPDATE_TS_3P, UINT32)
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=update_ts)

    @check_errors
    def three_ph_set_slab_params(self, addr, args):
        scp = SlabConfigurationPacket3P()
        scp.no_of_slabs = int(args.split(",")[0])
        scp.slab_price = map(
            int, (args.split("[")[1]).split("]")[0].split(","))
        scp.slab_limits = map(
            int, (args.split("[")[2]).split("]")[0].split(","))
        scp.mmc = int(args.split("],")[2])

        if (scp.no_of_slabs < 1 or scp.no_of_slabs > 6):
            return "Error! Number of slabs should be in the range of 1 to 6!"
        elif len(scp.slab_price) != 6:
            return "Error! 6 parameters need to be entered for slab_price!"
        elif len(scp.slab_limits) != 5:
            return "Error! 5 parameters need to be entered for slab_limits!"

        for index in range(len(scp.slab_price)):
            if index < scp.no_of_slabs:
                if scp.slab_price[index] < 1 or scp.slab_price[index] > 65000:
                    return "Error! Slab prices should be in the range of 1 to 65000!"
            else:
                if scp.slab_price[index] != 0:
                    return "Error! Number of slab prices entered is more than number of slabs!"

        for index in range(len(scp.slab_limits)):
            if index < (scp.no_of_slabs - 1):
                if scp.slab_limits[index] < 1 or scp.slab_limits[index] > 65000:
                    return "Error! Slab limits should be in the range of 1 to 65000!"
            else:
                if scp.slab_limits[index] != 0:
                    return "Error! Number of slab limits entered is more than number of slabs!"

            if index > 0 and index < (scp.no_of_slabs - 1):
                if scp.slab_limits[index] <= scp.slab_limits[index - 1]:
                    return "Error! Slab limits should be in increasing order!"

        if scp.mmc < 0 or scp.mmc > 65000:
            return "Error! MMC should be in the range of 0 to 65000!"

        return self.my_simpleterm_master_3p.set_param(
            addr,
            commandMappingContainer_3P.SET_SLAB_PARAMS_3P,
            scp,
            SLAB_CONFIGURATION_PACKET_3P)

    @check_errors
    def three_ph_set_slab_update_ts(self, addr, args):
        dt_string = args.split(",")
        if "now" in dt_string[0]:
            delta = int(dt_string[0].split("+")[1])
            updateTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            updateTime = dateutil.parser.parse(dt_string[0].strip(' '))
        if not isinstance(updateTime, datetime.datetime):
            updateTime = dateutil.parser.parse(updateTime)
        seconds_since_epoch = (
            updateTime -
            datetime.datetime(
                1970,
                1,
                1)).total_seconds()

        meterTime = self.get_time(addr)
        meter_seconds_since_epoch = (
            meterTime -
            datetime.datetime(
                1970,
                1,
                1)).total_seconds()
        if (meter_seconds_since_epoch >= seconds_since_epoch):
            return "Error! Entered update TS should not be behind the current meter time!"

        return self.my_simpleterm_master_3p.set_param(
            addr,
            commandMappingContainer_3P.SET_SLAB_UPDATE_TS_3P,
            int(seconds_since_epoch),
            UINT32)

    @check_errors
    def three_ph_slab_reset(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.SLAB_RESET_3P)

    @check_errors
    def three_ph_slab_enable_on_update(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.SLAB_ENABLE_ON_UPDATE_3P)

    @check_errors
    def three_ph_slab_enable(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.SLAB_ENABLE_3P)

    @check_errors
    def three_ph_slab_disable(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.SLAB_DISABLE_3P)

    ''' FIXED-RELEATED-COMMANDS '''
    '''-------------------------'''

    @check_errors
    def three_ph_get_fd_update_ts(self, addr):
        update_ts = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_FD_UPDATE_TS_3P, UINT32)
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=update_ts)

    @check_errors
    def three_ph_get_active_fd_params(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr,
            commandMappingContainer_3P.GET_ACTIVE_FD_PARAMS_3P,
            FIXED_DEDUCTION_PACKET_3P)

    @check_errors
    def three_ph_set_fd_params(self, addr, args):
        fdp = FixedDeductionPacket3P()
        fdp.amount = int(args.split(",")[0])
        fdp.type_of_deduction = str(args.split(",")[1])
        return self.my_simpleterm_master_3p.set_param(
            addr,
            commandMappingContainer_3P.SET_FD_PARAMS_3P,
            fdp,
            FIXED_DEDUCTION_PACKET_3P)

    @check_errors
    def three_ph_set_fd_update_ts(self, addr, args):
        args = args.split(",")
        if "now" in args[0]:
            delta = int(args[0].split("+")[1])
            updateTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            updateTime = dateutil.parser.parse(args[0].strip(' '))
        if not isinstance(updateTime, datetime.datetime):
            updateTime = dateutil.parser.parse(updateTime)
        seconds_since_epoch = int(
            (updateTime - datetime.datetime(1970, 1, 1)).total_seconds())

        meterTime = self.get_time(addr)
        meter_seconds_since_epoch = (
            meterTime -
            datetime.datetime(
                1970,
                1,
                1)).total_seconds()
        if (meter_seconds_since_epoch >= seconds_since_epoch):
            return "Error! Entered update TS should not be behind the current meter time!"

        return self.my_simpleterm_master_3p.set_param(
            addr,
            commandMappingContainer_3P.SET_FD_UPDATE_TS_3P,
            seconds_since_epoch,
            UINT32)

    @check_errors
    def three_ph_fd_enable(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.FD_ENABLE_3P)

    @check_errors
    def three_ph_fd_disable(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.FD_DISABLE_3P)

    @check_errors
    def three_ph_fd_reset(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.FD_RESET_3P)

    '''------PREPAID-ACCOUNT-RELEATED-COMMANDS -----'''
    '''---------------------------------------------'''

    @check_errors
    def three_ph_clear_account(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.CLEAR_ACCOUNT_3P)

    @check_errors
    def three_ph_allow_negative_credits(self, addr):
        reply = self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.ALLOW_NEGATIVE_CREDITS_3P)
        return reply

    @check_errors
    def three_ph_forbid_negative_credits(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.FORBID_NEGATIVE_CREDITS_3P)

    @check_errors
    def three_ph_get_credit_limit(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_CREDIT_LIMIT_3P, INT32)
    get_credit_limit.units = 'credits'

    @check_errors
    def three_ph_get_accurate_credits(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr,
            commandMappingContainer_3P.GET_ACCURATE_CREDITS_3P,
            PREPAID_ACCOUNT_PACKET_3P)

    @check_errors
    def three_ph_get_credits(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_CREDITS_3P, INT32)
    get_credits.units = 'credits'

    @check_errors
    def three_ph_set_credit_limit(self, addr, credit_limit):
        credit_limit = int(credit_limit)
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_CREDIT_LIMIT_3P, credit_limit, INT32)

    @check_errors
    def three_ph_set_price(self, addr, price):
        price = float(price)
        if float(price) <= 0.00 or float(price) >= 100.00:
            return "Invalid price input! Price must be higher than 0.00, and lower than 100.00."
        if float(price) != 0.0:
            e_per_credit = int(round(3600 * 1000 / float(price), 0))
        else:
            e_per_credit = 1.0
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_ENERGY_PER_CREDIT_3P, e_per_credit, UINT32)

    @check_errors
    def three_ph_get_price(self, addr):
        e_per_credit = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_ENERGY_PER_CREDIT_3P, UINT32)
        credit_per_kwh = round(float(3600.00 * 1000.00 / e_per_credit), 2)
        return credit_per_kwh
    get_price.units = 'credits/kwh'

    ''''-----RECHARGE-CLIENT-RELEATED-COMMANDS----------------'''
    '''--------------------------------------------------------'''

    # ===============================================================================
    @check_errors
    def three_ph_get_net_account(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_NET_ACCOUNT_3P, INT32)
    get_credits.units = 'credits'
    #================================================================================
    @check_errors
    def three_ph_get_net_recharge(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_NET_RECHARGE_3P, INT32)
    get_credits.units = 'credits'

    @check_errors
    def three_ph_get_pos_recharge(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_POS_RECHARGE_3P, UINT32)
    get_credits.units = 'credits'

    @check_errors
    def three_ph_get_neg_recharge(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_NEG_RECHARGE_3P, UINT32)
    get_credits.units = 'credits'

    @check_errors
    def three_ph_clear_recharges(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.CLEAR_RECHARGES_3P)

    @check_errors
    def three_ph_request_recharge(self, addr):
        amount = int(amount)
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.REQUEST_RECHARGE_3P)

    @check_errors
    def three_ph_recharge_fract(self, addr, amount):
        amount = round(float(amount), 2)
        amount = int(100 * amount)
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_RECHARGE_FRACT_3P, amount, INT32)

    @check_errors
    def beat_time(self, addr):
        unix_time = self.my_syncstream_master.get_current_beat_time()
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=unix_time)

    ''''------LOAD-SURVEY-RELEATED-THREE-PHASE-COMMANDS--------'''
    '''--------------------------------------------------------'''

    @check_errors
    def three_ph_get_newest_survey(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_NEWEST_SURVEY_3P, SURVEY_PACKET_3P)

    @check_errors
    def three_ph_get_oldest_survey(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_OLDEST_SURVEY_3P, SURVEY_PACKET_3P)

    @check_errors
    def three_ph_get_survey_by_index(self, addr, index):
        #-----------------------------------------------
        values = self.three_ph_get_num_surveys(addr)
        print ("No of Suraveys :", values)
        values = values - 1
        if (values == -1):
            return "No records found!"
        elif (index > values):
            return "Error! Index cannot be higher than number of record entries."
        else:
            index = int(index)
            if index < 0 or index > values:
                print ("No of surveys generated is :", (values + 1))
                return "Invalid Index!!!."
            else:
                return self.my_simpleterm_master_3p.set_and_get_param(
                    addr,
                    commandMappingContainer_3P.GET_SURVEY_BY_INDEX_3P,
                    index,
                    UINT32,
                    SURVEY_PACKET_3P)

    @check_errors
    def three_ph_get_daily_profile_by_index(self, addr, index):
        no_of_survey = self.three_ph_get_num_daily_profile(addr)
        values = int(no_of_survey)
        print(values)
        index = int(index)
        values = values - 1
        if index < 0 or index > values:
            print("No of Daily Profile Log:", (values + 1))
            return "Invalid Index!!!"
        else:
            return self.my_simpleterm_master_3p.set_and_get_param(
                addr,
                commandMappingContainer_3P.GET_DAILY_PROFILE_BY_INDEX_3P,
                index,
                UINT32,
                DAILY_PROFILE_3P)

    @check_errors
    def three_ph_survey_print_direct(self, addr):
        no_of_survey = self.three_ph_get_num_surveys(addr)
        values = int(no_of_survey)
        values = values - 1
        if (values == -1):
            values = 15777
        if (values < 15776):
            flag = True
            while(flag):
                print("Index : " + str(values))
                print(self.my_simpleterm_master_3p.set_and_get_param(addr, commandMappingContainer_3P.GET_SURVEY_BY_INDEX_3P, values, UINT32, SURVEY_PACKET_3P))
                print("\n")
                values = values - 1
                if (values == -1):
                    flag = False
        return "No of Survey:" + str(no_of_survey)

    @check_errors
    def block_load_print_direct(self, addr, line):
        no_of_survey = self.get_num_block_load_profile(addr)
        values = int(no_of_survey)
        values = values -1 
        if (values == -1):
          #  " 136 entries per sector, 136 * 159  = 21624 entries."
            values = 21624 
        if (values < 21624):
            flag = True
            while(flag):
                print("Index : "+ str(values))
                reply=None
                while reply is None:
                    try:
                        if (line == "ene"):
                            reply= self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_BLOCK_LOAD_ENE_PRO_BY_INDEX, values, UINT32, BUNDLE, 8640)
                        else:
                            reply= self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_BLOCK_LOAD_PROFILE_BY_INDEX, values, UINT32, BUNDLE, 8640)
                        print(reply)
                    except Exception as e:
                        print("Retrying for Index: ",str(values))
                        pass
                print("\n")
                values = values -1
                if (values == -1):
                    flag = False
        return "No of Block load profiles:"+str(no_of_survey)

    @check_errors
    def instant_load_print_direct(self, addr, line):
        no_of_survey = self.get_num_instant_data_profile(addr)
        values = int(no_of_survey)
        print(values)
        values = values -1 
        if (values == -1):
          #  " 136 entries per sector, 136 * 159  = 21624 entries."
            values = 21624 
        if (values < 21624):
            flag = True
            while(flag):
                print("Index : "+ str(values))
                reply=None
                while reply is None:
                    try:
                        if (line == "ene"):
                            reply = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_INSTANT_PROFILE_BY_INDEX, values, UINT32, METERING_DATA_PACKET, 2000)
                        else:
                            reply = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_INSTANT_PROFILE_BY_INDEX, values, UINT32, METERING_DATA_PACKET, 2000)
                        print(reply)
                    except Exception as e:
                        print("Retrying for Index: ",str(values))
                        pass
                print("\n")
                values = values -1
                if (values == -1):
                    flag = False
        return "No of Block load profiles:"+str(no_of_survey)

    @check_errors
    def set_config_time(self,addr, num):
        value = num
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_CONFIG_TIME, int(value), UINT32)

    @check_errors
    def set_enable_write_data(self,addr, num):
        value = num
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.ENABLE_WRITE_DATA, int(value), UINT8)

    @check_errors
    def daily_load_profile_print_direct(self, addr):
        no_of_survey = self.get_num_daily_load_profile(addr)
        #print "No of surveys:", no_of_survey
        values = int(no_of_survey)
        values = values -1 
        flag = False
        if(values == -1):
            flag = False
        else:
            flag = True
        while(flag):
            print("Index : "+ str(values))
            reply = None
            while reply is None:
                try:
                    reply = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_DAILY_LOAD_PROFILE_BY_INDEX, values, UINT32, DAILY_LOAD_PROFILE_PACKET, 180) 
                    print(reply)
                except Exception as e:
                    print("Retrying for Index: ",str(values))
                    pass
            print("\n")
            values = values -1
            if (values == -1):
                flag = False
        return "No of Daily Profile:"+str(no_of_survey)





    @check_errors
    def three_ph_daily_profile_print_direct(self, addr):
        no_of_survey = self.three_ph_get_num_daily_profile(addr)
        #print "No of surveys:", no_of_survey
        values = int(no_of_survey)
        values = values -1 
        flag = False
        if(values == -1):
            flag = False
        else:
            flag = True
        while(flag):
            print("Index : "+ str(values))
            
            print(self.my_simpleterm_master_3p.set_and_get_param(addr, commandMappingContainer_3P.GET_DAILY_PROFILE_BY_INDEX_3P, values, UINT32,DAILY_PROFILE_3P))
            print("\n")
            values = values -1
            if (values == -1):
                flag = False
        return "No of Daily Profile:"+str(no_of_survey)
    #-------------------------------------------------------------------------
    #-------------------NEW ADDING--------------------------------------------
    #-------------------------------------------------------------------------

    @check_errors
    def three_ph_get_num_surveys(self, addr):
        #-----------------------------------------------
        profile_params_str = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_PROFILE_3P, SYS_PARAMS_3P)

        # print profile_params_str
        profile_params_str = str(profile_params_str)
        # print profile_params_str
        arg = profile_params_str.split("\n")
        # print arg
        profile_params = []
        try:
            for line_number in range(0, 23):
                profile_params.append(arg[line_number].split(": ")[1])
        except Exception as e:
            print(e)

        values = int(profile_params[1])
        return values

    @check_errors
    def three_ph_get_num_daily_profile(self, addr):
        #-----------------------------------------------
        profile_params_str = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_PROFILE_3P, SYS_PARAMS_3P)

        # print profile_params_str
        profile_params_str = str(profile_params_str)
        arg = profile_params_str.split("\n")
        profile_params = []
        try:
            for line_number in range(0, 23):
                profile_params.append(arg[line_number].split(": ")[1])
        except Exception as e:
            print (e)
        # for syrveys
        # print profile_params
        values = int(profile_params[2])
        # print "No of Suraveys :",values
        return values
        # return self.my_simpleterm_master_3p.get_param(addr,
        # commandMappingContainer_3P.GET_NUM_DAILY_PROFILE_3P, UINT32)

    @check_errors
    def three_ph_clear_load_survey(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.CLEAR_LOAD_SURVEY_3P)

    @check_errors
    def three_ph_clear_daily_profile(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.CLEAR_DAILY_PROFILE_3P)

    @check_errors
    def three_ph_get_survey_interval(self, addr):
        #-----------------------------------------------
        profile_params_str = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_PROFILE_3P, SYS_PARAMS_3P)

        # print profile_params_str
        profile_params_str = str(profile_params_str)
        arg = profile_params_str.split("\n")
        profile_params = []
        try:
            for line_number in range(0, 23):
                profile_params.append(arg[line_number].split(": ")[1])
        except Exception as e:
            print (e)
        # for syrveys
        values = int(profile_params[0])
        #values = profile_params
        return values
        # print "No of Suraveys :",values
        # return self.my_simpleterm_master_3p.get_param(addr,
        # commandMappingContainer_3P.GET_SURVEY_INTERVAL_3P, UINT32)
    three_ph_get_survey_interval.units = "minutes"

    @check_errors
    def three_ph_set_survey_interval(self, addr, survey_interval):
        if((60 % survey_interval) == 0):
            return self.my_simpleterm_master_3p.set_param(
                addr, commandMappingContainer_3P.SET_SURVEY_INTERVAL_3P, survey_interval, UINT32)
        else:
            return "survey interval should be diviser of 60"
    #-------------------------------------------------------------------------
    #-------------------END HERE----------------------------------------------
    #-------------------------------------------------------------------------

    @check_errors
    def three_ph_clear_event_record(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.CLEAR_EVENT_RECORD_3P)

    @check_errors
    def three_ph_get_newest_event_record(self, addr, index):
        index = int(index)
        if index < 1 or index > 7:
            return "Invalid value! Index should be in the range of 1 to 7.\n 1.Voltage Related Event\
            \n 2.Current Related Event \n 3.Power Related Event \n 4.Transaction Related Event \
            \n 5.CO Tamper Event \n 6.Control Related Event \n 7.Other Event"
        else:
            return self.my_simpleterm_master_3p.set_and_get_param(
                addr,
                commandMappingContainer_3P.GET_NEWEST_EVENT_RECORD_3P,
                index,
                UINT32,
                EVENT_RECORD_PACKET_3P)

    @check_errors
    def three_ph_get_oldest_event_record(self, addr, index):
        index = int(index)
        if index < 1 or index > 7:
            return "Invalid value! Index should be in the range of 1 to 7.\n 1.Voltage Related Event\
            \n 2.Current Related Event \n 3.Power Related Event \n 4.Transaction Related Event \
            \n 5.CO Tamper Event \n 6.Control Related Event \n 7.Other Event"
        else:
            return self.my_simpleterm_master_3p.set_and_get_param(
                addr,
                commandMappingContainer_3P.GET_OLDEST_EVENT_RECORD_3P,
                index,
                UINT32,
                EVENT_RECORD_PACKET_3P)

    @check_errors
    def three_ph_get_num_event_record(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr,
            commandMappingContainer_3P.GET_NUM_EVENT_RECORD_3P,
            EVENT_RECORD_TOTAL_PACKET)

    @check_errors
    def three_ph_get_event_record_by_index(self, addr, event_category, index):
        if event_category < 1 or event_category > 7:
            return "Invalid value! Index should be in the range of 1 to 7.\n 1.Voltage Related Event\
            \n 2.Current Related Event \n 3.Power Related Event \n 4.Transaction Related Event \
            \n 5.CO Tamper Event \n 6.Control Related Event \n 7.Other Event"
        if index < 0 or index > 15776:
            return "Invalid value! Index should be in the range of 0 to 15776."
        else:
            buf = bytearray()
            buf.extend(serialize.serialize_uint32(event_category))
            buf.extend(serialize.serialize_uint32(index))
            return self.my_simpleterm_master_3p.set_and_get_param(
                addr,
                commandMappingContainer_3P.GET_EVENT_RECORD_BY_INDEX_3P,
                buf,
                BYTE_ARRAY,
                EVENT_RECORD_PACKET_3P)

    @check_errors
    def three_ph_event_record_print_direct(self, addr, index):
        if index < 1 or index > 8:
            return "Invalid value! Index should be in the range of 1 to 7.\n 1.Voltage Related Event\
            \n 2.Current Related Event \n 3.Power Related Event \n 4.Transaction Related Event \
            \n 5.CO Tamper Event \n 6.Control Related Event \n 7.Other Event"

        number_or_records = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_NUM_EVENT_RECORD_3P, EVENT_RECORD_TOTAL_PACKET)
        # print number_or_records
        number_or_records = str(number_or_records)
        arg = number_or_records.split("\n")
        event = ['0']
        try:
            for line_number in range(8):
                event.append(int(arg[line_number].split(":")[1]))
        except Exception as e:
            print (e)

        values = int(event[index])
        print("No of Event Record in this catogery :" + str(values))
        values = values - 1
        flag = False
        if (values != -1):
            flag = True
        while(flag):
            buf = bytearray()
            print("Index : " + str(values))
            buf.extend(serialize.serialize_uint32(index))
            buf.extend(serialize.serialize_uint32(values))
            print(self.my_simpleterm_master_3p.set_and_get_param(addr, commandMappingContainer_3P.GET_EVENT_RECORD_BY_INDEX_3P, buf, BYTE_ARRAY, EVENT_RECORD_PACKET_3P))
            values = values - 1
            if (values == -1):
                flag = False
        return ' '

    @check_errors
    def event_record_print_direct(self, addr,index):
        if index < 1 or index > 8:
            return "Invalid value! Event category should be in the range of 1 to 7.\n 1.Voltage Related Event\
            \n 2.Current Related Event \n 3.Power Related Event \n 4.Transaction Related Event \
            \n 5.CO Tamper Event \n 6.Control Related Event \n 7.Other Event\n 8. RF Related Events"
        
        number_or_records = self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_NUM_EVENT_RECORD, EVENT_RECORD_TOTAL_PACKET)
        #print number_or_records
        number_or_records = str(number_or_records)
        arg = number_or_records.split("\n")
        event = ['0']
        try:
            for line_number in range(1,9):
                event.append(int(arg[line_number].split(": ")[1]))
        except Exception as e:
                print (e)

        values = int(event[index])
        print("No of Event Record in this catogery :"+ str(values))
        values = values -1 
        flag = False
        if (values != -1):
            flag = True
        if index >=8:
            index = index+1
        while(flag):   
            buf = bytearray();
            print("Index : "+ str(values))
            buf.extend(serialize.serialize_uint32(index))
            buf.extend(serialize.serialize_uint32(values))
            reply = None
            while reply is None:
                try:
                    reply = self.my_simpleterm_master.set_and_get_param(addr, commandMappingContainer.GET_EVENT_RECORD_BY_INDEX, buf, BYTE_ARRAY, EVENT_RECORD_PACKET)
                    print(reply)
                except Exception as e:
                    print("retrying for Index: ", str(values)) 
                    pass   
            values = values -1
            if (values == -1):
                flag = False
        return ' '

    @check_errors
    def three_ph_set_persistance_time(self, addr,occurence_time,restoration_time):
        buf = bytearray();
        if(occurence_time%3):
            occurence_time = occurence_time + 3

        if(restoration_time % 3):
            restoration_time = restoration_time + 3

        buf.extend(serialize.serialize_uint32(occurence_time))
        buf.extend(serialize.serialize_uint32(restoration_time))

        occurence_time = int(occurence_time / 3)
        restoration_time = int(restoration_time / 3)

        occurence_time = int(occurence_time * 3)
        restoration_time = int(restoration_time * 3)

        print("New Occurence time : " + str(occurence_time) + " Seconds")
        print("New Restoration time : " + str(restoration_time) + " Seconds")

        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_EVENT_PERSISTANT_TIME_3P, buf, BYTE_ARRAY)

    @check_errors
    def three_ph_get_cumulative_tamper_count(self, addr):
        #-----------------------------------------------
        profile_params_str = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_PROFILE_3P, SYS_PARAMS_3P)

        profile_params_str = str(profile_params_str)
        arg = profile_params_str.split("\n")
        profile_params = []
        try:
            for line_number in range(0, 23):
                profile_params.append(arg[line_number].split(": ")[1])
        except Exception as e:
            print(e)

        values = int(profile_params[21])
        return values
        # return self.my_simpleterm_master_3p.get_param(addr,
        # commandMappingContainer_3P.GET_CUMULATIVE_TAMPER_COUNT_3P, UINT32)

    @check_errors
    def three_ph_get_metering_data_ip(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr,
            commandMappingContainer_3P.GET_METERING_DATA_IP_3P,
            METERING_DATA_PARAMS_3P)

    @check_errors
    def three_ph_get_metering_data_energy(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr,
            commandMappingContainer_3P.GET_METERING_DATA_ENERGY_3P,
            METERING_DATA_PARAMS_3P)

    @check_errors
    def three_ph_get_metering_data_resoultion(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr,
            commandMappingContainer_3P.GET_METERING_DATA_RESOULTION_3P,
            METERING_DATA_PARAMS_3P)

    @check_errors
    def three_ph_get_metering_data_reserved(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr,
            commandMappingContainer_3P.GET_METERING_DATA_RESERVED_3P,
            METERING_DATA_PARAMS_3P)

    @check_errors
    def three_ph_turn_relay_on(self, addr):
        reply = self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.RELAY_ON_3P)
        return reply

    @check_errors
    def three_ph_turn_relay_off(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.RELAY_OFF_3P)

    @check_errors
    def three_ph_get_relay_status(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.GET_RELAY_STATUS_3P)

    "------------CHANGE METER PROTOCOL RELEATED COMMANDS-----------"
    "---------------------------------------------------------------"
    @check_errors
    def three_ph_meter_tap_to_dlms(self, addr):
        try:
            self.my_simpleterm_master_3p.get_param(
                addr, commandMappingContainer_3P.TAP_TO_DLMS_3P, INT32)
        except Exception as e:
            pass
        return "Command sent to meter"

    @check_errors
    def dongle_dlms_to_tap(self, addr):
        bytes = bytearray(
            [0xAA, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3])
        self.my_tap_handler.send_raw_bytes(bytes)
        return "Command sent to dongle!"

    @check_errors
    def three_ph_meter_dlms_to_tap(self, addr):
        bytes = bytearray(
            [0x7E, 0xA0, 0x07, 0xBB, 0x41, 0x93, 0xDA, 0x28, 0x7E])
        self.my_tap_handler.send_raw_bytes(bytes)
        return "Command sent to meter"
    ###############################

    @check_errors
    def three_ph_recharge(self, addr, amount):
        amount = int(amount)
        print(amount)
        return self.my_recharge_master.recharge(addr, amount)
    "------------BILLING PROFILE RELEATED COMMANDS------------------"
    "---------------------------------------------------------------"
    @check_errors
    def three_ph_clear_billing_log(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.CLEAR_BILLING_LOG_3P)

    @check_errors
    def three_ph_clear_billing_history(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.CLEAR_BILLING_HISTORY_3P)

    @check_errors
    def three_ph_set_MD_integration_period(self, addr, interval):
        if((interval == 15) or (interval == 30) or (interval == 60)):
            return self.my_simpleterm_master_3p.set_param(
                addr, commandMappingContainer_3P.SET_INTEGRATION_PERIOD_3P, interval, UINT32)
        else:
            return "MD integration period can be 15/30/60"

    @check_errors
    def three_ph_set_billing_date(self, addr, billing_timestamp):
        if billing_timestamp == 0:
            return "Error! This command needs an argument!"
        if billing_timestamp == "now":
            billing_timestamp = datetime.datetime.now()
        if not isinstance(billing_timestamp, datetime.datetime):
            billing_timestamp = dateutil.parser.parse(billing_timestamp)

        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = int(
            (billing_timestamp - unix_time_zero).total_seconds())
        return self.my_simpleterm_master_3p.set_param(
            addr,
            commandMappingContainer_3P.SET_BILLING_DATE_3P,
            seconds_since_epoch,
            UINT32)

    @check_errors
    def three_ph_get_billing_params(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_BILLING_PARAMS_3P, BILLING_PARAMS_3P)

    @check_errors
    def three_ph_get_billing_log_by_index(self, addr, index):
        return self.my_simpleterm_master_3p.set_and_get_param(
            addr,
            commandMappingContainer_3P.GET_NUM_BILLING_LOG_INDEX_3P,
            index,
            UINT32,
            BILLING_LOG_PACKET_3P)

    @check_errors
    def three_ph_get_billing_history_by_index(self, addr, index):
        return self.my_simpleterm_master_3p.set_and_get_param(
            addr,
            commandMappingContainer_3P.GET_NUM_BILLING_HISTORY_INDEX_3P,
            index,
            UINT32,
            BILLING_HISTORY_PACKET_3P)

    @check_errors
    def calib_unlock(self, addr, calib_number):
        if calib_number == "":
            return "Error! Password required."
        elif int(calib_number) == 1331:
            return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.CALIB_UNLOCK)
        else:
            return "Error! Password is incorrect, Access denied."
    
    @check_errors
    def set_ip_time(self, addr, cal_time):
        if cal_time == "":
            cal_time = 0
        elif cal_time == "now":
            cal_time = datetime.datetime.now()
        else:
            try:
                time_str = cal_time.split(' ')[1]
                if len(time_str) == 6:
                    time_str = time_str[0] + time_str[1] + ":" + time_str[2] + time_str[3] + ":" +time_str[4] + time_str[5]
                    cal_time = cal_time.split(' ')[0] + " " + time_str
                cal_time = datetime.datetime.strptime(cal_time, "%Y-%m-%d %H:%M:%S")
            except:
                return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = int((cal_time - unix_time_zero).total_seconds())
        # print "seconds : ", seconds_since_epoch
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.IP_SET_TIME,
                                                   seconds_since_epoch, UINT32)
    @check_errors
    def three_ph_print_billing_history(self, addr):

        #-----------------------------------------------
        profile_params_str = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_PROFILE_3P, SYS_PARAMS_3P)

        # print profile_params_str
        profile_params_str = str(profile_params_str)
        arg = profile_params_str.split("\n")
        profile_params = []
        try:
            for line_number in range(0, 23):
                profile_params.append(arg[line_number].split(": ")[1])
        except Exception as e:
            print(e)
        # for syrveys
        # print len(profile_params)
        # print profile_params
        values = int(profile_params[5])
        # return values
        print("No of Billing History:", values)
        no_of_history = values
        values = no_of_history - 1

        print("Current Billing Data")
        print(self.my_simpleterm_master_3p.set_and_get_param(addr, commandMappingContainer_3P.GET_NUM_BILLING_HISTORY_INDEX_3P,
                                                             0xffff, UINT32, BILLING_HISTORY_PACKET_3P))
        print("\n")
        if (values == -1):
            return "No Billing History Found"

        flag = True
        while(flag):
            print("Index : " + str(values))
            print(self.my_simpleterm_master_3p.set_and_get_param(addr, commandMappingContainer_3P.GET_NUM_BILLING_HISTORY_INDEX_3P,
                                                                 values, UINT32, BILLING_HISTORY_PACKET_3P))
            print("\n")
            values = values - 1
            if (values == -1):
                flag = False

        return "No of History:" + str(no_of_history)

    @check_errors
    def three_ph_get_num_billing_debug_logs(self, addr):
        #-----------------------------------------------
        profile_params_str = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_PROFILE_3P, SYS_PARAMS_3P)

        # print profile_params_str
        profile_params_str = str(profile_params_str)
        arg = profile_params_str.split("\n")
        profile_params = []
        try:
            for line_number in range(0, 23):
                profile_params.append(arg[line_number].split(": ")[1])
        except Exception as e:
            print(e)
        # for syrveys
        # print len(profile_params)
        # print profile_params
        values = int(profile_params[4])
        return values
        # return self.my_simpleterm_master_3p.get_param(addr,
        # commandMappingContainer_3P.GET_NUM_BILLING_LOG_3P, UINT32)

    @check_errors
    def initiate_fw_upgrade(self, addr):
        print("Firmware upgrade initiate")
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.INITIATE_FW_UPGRADE)

    @check_errors
    def initiate_ui_upgrade(self, addr):
        print("UI upgrade initiate...")
        return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.INITIATE_UI_UPGRADE)

    @check_errors
    def three_ph_factory_init(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.FACTORY_INIT_3P)


    @check_errors
    def three_ph_print_billing_log(self, addr):
        no_of_billing_log = self.three_ph_get_num_billing_debug_logs(addr)
        values = int(no_of_billing_log)
        values = values - 1
        if (values != -1):
            flag = True
            while(flag):
                print ("Index : " + str(values))
                print(self.my_simpleterm_master_3p.set_and_get_param(addr, commandMappingContainer_3P.GET_NUM_BILLING_LOG_INDEX_3P,
                                                                     values, UINT32, BILLING_LOG_PACKET_3P))
                print("\n")
                values = values - 1
                if (values == -1):
                    flag = False
        return "No of Billing Log:" + str(no_of_billing_log)

    @check_errors
    def three_ph_meter_dlms_to_tap(self, addr):
        bytes = bytearray(
            [0x7E, 0xA0, 0x07, 0xBB, 0x41, 0x93, 0xDA, 0x28, 0x7E])
        self.my_tap_handler.send_raw_bytes(bytes)
        return "Command sent to meter"

    @check_errors
    def three_ph_get_system_params(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_1, SYS_PARAMS_1_PACKET_3P)

    @check_errors
    def three_ph_system_params_data(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_DATA_3P, SYS_PARAMS_3P)

    @check_errors
    def three_ph_system_params_profile(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SYS_PARAMS_PROFILE_3P, SYS_PARAMS_3P)

    @check_errors
    def three_ph_get_dlms_dbg_info(self, addr):
        return self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_DLMS_DEBUG_INFO, DLMS_DBG_PACKET_3P)

    @check_errors
    def three_ph_set_power_limit(self, addr, power_limit):
        power_limit = int(power_limit)
        if power_limit < 1 or power_limit > 4294967:
            return "Invalid value! Power limit should be in the range of 1 to 4294967."
        else:
            power_limit = 1000 * power_limit
            return self.my_simpleterm_master_3p.set_param(
                addr, commandMappingContainer_3P.SET_POWER_LIMIT_3P, power_limit, UINT32)

    @check_errors
    def three_ph_relay_manual_control(self, addr):
        relay_control_mode = 1
        return self.my_simpleterm_master_3p.set_param(
            addr,
            commandMappingContainer_3P.SET_RELAY_CONTROL_MODE_3P,
            relay_control_mode,
            UINT32)

    @check_errors
    def three_ph_relay_auto_control(self, addr):
        relay_control_mode = 0
        return self.my_simpleterm_master_3p.set_param(
            addr,
            commandMappingContainer_3P.SET_RELAY_CONTROL_MODE_3P,
            relay_control_mode,
            UINT32)

    @check_errors
    def three_ph_erase_flash_sector(self, addr, flash_sector):
        flash_sector = int(flash_sector)
        if int(flash_sector) < 0 or int(flash_sector) >= 512:
            return "Invalid sector input! Sector must be higher than -1, and lower than 512"
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.ERASE_FLASH_SECTOR_3P, flash_sector, UINT32)

    @check_errors
    def three_ph_get_serial_no(self, addr):
        serial_no = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_SERIAL_NO_3P, UINT32)
        return serial_no

    @check_errors
    def rc_transmit_mode_on(self, addr):
        byte_array = bytearray()
        byte_array.append('1')
        buf = self.obj_rcCommandPacket.frame_set_rc_read_cmd(byte_array)
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)

        # return self.my_simpleterm_master_3p.execute_command(addr,
        # commandMappingContainer_3P.RC_TRANSMIT_MODE_ON_3P)
    @check_errors
    def rc_transmit_mode_off(self, addr):
        byte_array = bytearray()
        byte_array.append('3')
        buf = self.obj_rcCommandPacket.frame_set_rc_read_cmd(byte_array)
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)

    @check_errors
    def three_ph_get_ext_flash_crc(
            self,
            addr,
            ext_flash_address,
            length_of_payload):
        buf = bytearray()
        buf.extend(serialize.serialize_uint32(ext_flash_address))
        buf.extend(serialize.serialize_uint32(length_of_payload))
        EXT_FLASH_SIZE = (2 * 1024 * 1024)  # Bytes
        BYTES_PER_SECTOR = 4096
        MSP430_FLASH_SIZE = (128 * 1024)
        if(ext_flash_address > EXT_FLASH_SIZE):
            ext_flash_address = (EXT_FLASH_SIZE - BYTES_PER_SECTOR)
        if(length_of_payload > MSP430_FLASH_SIZE):
            length_of_payload = MSP430_FLASH_SIZE
        if((length_of_payload + ext_flash_address) > EXT_FLASH_SIZE):
            return "Invalid Lenth and Address"

        print("Ext Flash Start Address : " + str(ext_flash_address))
        print("Length  : " + str(length_of_payload) + " Bytes")
        buf = bytearray()
        buf.extend(serialize.serialize_uint32(ext_flash_address))
        buf.extend(serialize.serialize_uint32(length_of_payload))

        return self.my_simpleterm_master_3p.set_and_get_param(
            addr, commandMappingContainer_3P.GET_CRC_EXT_FLASH, buf, BYTE_ARRAY, UINT32)

    @check_errors
    def three_ph_get_crc_bundle(
            self,
            addr,
            ext_flash_start_address,
            length_of_payload):
        if ext_flash_start_address < 0 or length_of_payload <= 0:
            print("Invalid Flash Address or Invalid Length")
        else:
            print("External Flash Start Address : " + str(ext_flash_start_address))
            if(length_of_payload % 2):
                length_of_payload += 1
            print("Length Of Payload : " + str(length_of_payload) + " Bytes")
            buf = bytearray()
            buf.extend(serialize.serialize_uint32(ext_flash_start_address))
            buf.extend(serialize.serialize_uint32(length_of_payload))
            return self.my_simpleterm_master_3p.set_and_get_param(
                addr, commandMappingContainer_3P.GET_CRC_BUNDLE_3P, buf, BYTE_ARRAY, CRC_BUNDLE_3P)

    @check_errors
    def three_ph_ui_config(self, addr, main_txt_file_path):
        desktop = os.path.join(
            os.path.join(
                os.path.expanduser('~')),
            'Desktop')
        path = os.path.join(os.path.join(desktop), main_txt_file_path)
        ui_config_file = open(path, "rb")
        block = ui_config_file.read()
        hexfile_payload = bytearray()
        for ch in block:
            hexfile_payload.append(ch)
        length = len(block)
        if length > 3000:
            return "invalid binary file"

        SECTOR_ADDRESS = 0x12B000
        sector_no = SECTOR_ADDRESS/4096
        self.my_flash_io_master_3p.erase(addr, int(sector_no),sector_erase = True)
        new_hex_payload = hexfile_payload
        while len(new_hex_payload) < 4094:
            new_hex_payload.append(0xff)
        crc_calc = _get_crc(new_hex_payload)
        crc_buf = serialize.serialize_uint16(crc_calc,order="reverse")
        for byte in crc_buf:
            new_hex_payload.append(byte)
        self.my_flash_io_master_3p.burn(Address("0.0.0.255"), SECTOR_ADDRESS, new_hex_payload, to_print=True)
        return "3PUI_Okay"
    

    # 3 phase Flash IO commands

    @check_errors
    def three_ph_mem_write(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        data = args[1].split(' ')
        while '' in data:
            data.remove('')
        data_bytearray = bytearray()
        for entry in data:
            entry = int(entry, 16)
            data_bytearray.append(entry)

        return self.my_flash_io_master_3p.write(
            addr, start_address, data_bytearray)

    @check_errors
    def three_ph_mem_read(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        length = int(args[1])
        return self.my_flash_io_master_3p.read(addr, start_address, length)

    @check_errors
    def three_ph_mem_erase_block(self, addr, line):
        block_no = int(line)
        if((block_no > 31) or (block_no < 0)):
            return "No of 64KB available block : 32, Command execution failed"
        return self.my_flash_io_master_3p.erase(addr, int(line))

    @check_errors
    def three_ph_mem_erase_sector(self, addr, line):
        sector_no = int(line)
        if(sector_no > 511) or (sector_no < 0):
            return "No of available sector : 512,  Command execution failed"
        return self.my_flash_io_master_3p.erase(
            addr, int(line), sector_erase=True)

    @check_errors
    def three_ph_get_metering_data_bundle(self, addr):
        lastTamperIntiger = 0
        desktop = os.path.join(
            os.path.join(
                os.path.expanduser('~')),
            'Desktop')
        path = os.path.join(os.path.join(desktop), 'BundleTamperFlag.txt')
        with open(path, 'a+') as fp:
            lastTamperIntiger = fp.read()
            fp.close()
        if(len(lastTamperIntiger) == 0):
            lastTamperIntiger = 0

        # print " Last Tamper Intiger:",int(lastTamperIntiger)
        rcvdTamperFlag = int(lastTamperIntiger)
        bundle_packet_3p = self.my_simpleterm_master_3p.set_and_get_param(
            addr,
            commandMappingContainer_3P.GET_METERING_DATA_BUNDLE_3P,
            rcvdTamperFlag,
            UINT32,
            BUNDLE_3P)
        bundle_dict = bundle_packet_3p
        values = bundle_dict['tamper_int_d']
        with open(path, 'w+') as fp:
            fp.write(str(values))
            fp.close()
        return bundle_packet_3p

    @check_errors
    def three_ph_get_network(self, addr):
        buf = self.obj_rcCommandPacket.frame_get_rc_cmd(
            self.obj_rcCommandPacket.RC_GET_NETWORK)
        val = serialize.deserialize_uint32(buf)
        return self.my_simpleterm_master_3p.set_and_get_param(
            addr, commandMappingContainer_3P.GET_RC_CONFIG_3P, val, UINT32, UINT32_BE)

    @check_errors
    def three_ph_get_channel(self, addr):
        buf = self.obj_rcCommandPacket.frame_get_rc_cmd(
            self.obj_rcCommandPacket.RC_GET_CHANNEL)
        val = serialize.deserialize_uint32(buf)
        return self.my_simpleterm_master_3p.set_and_get_param(
            addr, commandMappingContainer_3P.GET_RC_CONFIG_3P, val, UINT32, UINT32_BE)

    @check_errors
    def three_ph_get_rf_power(self, addr):
        buf = self.obj_rcCommandPacket.frame_get_rc_cmd(
            self.obj_rcCommandPacket.RC_GET_RF_POWER)
        val = serialize.deserialize_uint32(buf)
        return self.my_simpleterm_master_3p.set_and_get_param(
            addr, commandMappingContainer_3P.GET_RC_CONFIG_3P, val, UINT32, UINT32_BE)

    @check_errors
    def three_ph_get_address(self, addr):
        # buf = self.obj_rcCommandPacket.frame_get_rc_cmd(self.obj_rcCommandPacket.RC_GET_ADDRESS)
        # val = serialize.deserialize_uint32(buf)
        # addr_int = self.my_simpleterm_master_3p.set_and_get_param(addr, commandMappingContainer_3P.GET_RC_CONFIG_3P, val, UINT32, UINT32_BE)
        # addr1 = addr_int/(2**24)
        # addr_int = addr_int - addr1*(2**24)
        # addr2 = addr_int/2**16
        # addr_int = addr_int - addr2*(2**16)
        # addr3 = addr_int/2**8
        # addr_int = addr_int - addr3*(2**8)
        # addr4 = addr_int
        # addr_str = str(addr1) + "." + str(addr2) + "." + str(addr3) + "." + str(addr4)
        # address = Address(addr_str)
        # print "by RC GET Methord:",address
        addr_int = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_ADDRESS_3P, UINT32)
        addr1 = addr_int / (2**24)
        addr_int = addr_int - addr1 * (2**24)
        addr2 = addr_int / 2**16
        addr_int = addr_int - addr2 * (2**16)
        addr3 = addr_int / 2**8
        addr_int = addr_int - addr3 * (2**8)
        addr4 = addr_int
        addr_str = str(addr1) + "." + str(addr2) + "." + \
            str(addr3) + "." + str(addr4)
        address = Address(addr_str)
        return address

    @check_errors
    def three_ph_get_time(self, addr):
        time = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_TIME_3P, UINT32)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def three_ph_get_live_version(self, addr):
        version = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_LIVE_VERSION_3P, UINT32)
        return version

    @check_errors
    def three_ph_get_ext_version(self, addr):
        version = self.my_simpleterm_master_3p.get_param(
            addr, commandMappingContainer_3P.GET_EXT_VERSION_3P, UINT32)
        return version

    @check_errors
    def three_ph_set_address(self, addr, address):
        address = Address(str(address))
        addr_str_list = str(address).split('.')
        addr_int = int(addr_str_list[3])
        addr_int += int(addr_str_list[2]) * (2**8)
        addr_int += int(addr_str_list[1]) * (2**16)
        addr_int += int(addr_str_list[0]) * (2**24)
        byte_array = bytearray()
        byte_array = serialize.serialize_uint32(addr_int, order="reverse")
        buf = self.obj_rcCommandPacket.frame_set_rc_mem_read_cmd(
            self.obj_rcCommandPacket.RC_SET_ADDRESS, byte_array)
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)

    @check_errors
    def three_ph_set_channel(self, addr, channel):
        channel = int(channel)
        if channel > 16 or channel < 0:
            return "Invalid channel! Channel must be in the range of 0-16."
        else:
            channel_byte_array = bytearray()
            channel_byte_array = serialize.serialize_uint32(
                channel, order="reverse")
            buf = self.obj_rcCommandPacket.frame_set_rc_mem_read_cmd(
                self.obj_rcCommandPacket.RC_SET_CHANNEL, channel_byte_array)
            return self.my_simpleterm_master_3p.set_param(
                addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)

    @check_errors
    def three_ph_set_rf_power(self, addr, rf_power):
        rf_power = int(rf_power)
        if rf_power > 5 or rf_power < 1:
            return "Invalid value! RF Power must be in the range of 1-5."
        else:
            byte_array = bytearray()
            byte_array = serialize.serialize_uint32(rf_power, order="reverse")
            buf = self.obj_rcCommandPacket.frame_set_rc_mem_read_cmd(
                self.obj_rcCommandPacket.RC_SET_RF_POWER, byte_array)
            return self.my_simpleterm_master_3p.set_param(
                addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)

    @check_errors
    def three_ph_set_network(self, addr, network):
        network = int(network)
        if network <= 0:
            print("Invalid Network ID")
        network_byte_array = bytearray()
        network_byte_array = serialize.serialize_uint32(
            network, order="reverse")
        buf = self.obj_rcCommandPacket.frame_set_rc_mem_read_cmd(
            self.obj_rcCommandPacket.RC_SET_NETWORK, network_byte_array)
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)

    @check_errors
    def three_ph_set_rc_buffer_margin(self, addr, rc_buffer_margin):
        rc_buffer_margin = int(rc_buffer_margin)
        return self.my_simpleterm_master_3p.set_param(
            addr,
            commandMappingContainer_3P.SET_RC_BUFFER_MARGIN_3P,
            rc_buffer_margin,
            UINT32)

    @check_errors
    def three_ph_set_rc_timeout(self, addr, rc_timeout):
        rc_timeout = int(rc_timeout)
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_RC_TIMEOUT_3P, rc_timeout, UINT32)

    @check_errors
    def rc_revert_to_factory(self, addr):
        byte_array = bytearray()
        byte_array.append('@')
        byte_array.append('T')
        byte_array.append('M')
        buf = self.obj_rcCommandPacket.frame_set_rc_read_cmd(byte_array)
        return self.my_simpleterm_master_3p.set_param(
            addr, commandMappingContainer_3P.SET_RC_CONFIG_3P, buf, BYTE_ARRAY)

    @check_errors
    def three_ph_reset(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.BOARD_RESET_3P)

    @check_errors
    def three_ph_gateway(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.GATEWAY_3P)

    @check_errors
    def three_ph_router(self, addr):
        return self.my_simpleterm_master_3p.execute_command(
            addr, commandMappingContainer_3P.ROUTER_3P)




    #--------------------------------------------------------------------------------------------------#
    #--------------------------------------------------------------------------------------------------#
    #------------------------------1 Phase Non-DLMS Commands Start Here--------------------------------#
    #--------------------------------------------------------------------------------------------------#
    #--------------------------------------------------------------------------------------------------#


    @check_errors
    def non_dlms_get_credit_limit(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_CREDIT_LIMIT, INT32N)
    non_dlms_get_credit_limit.units = 'credits'

    @check_errors
    def non_dlms_get_master_credits(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_MASTER_CREDITS, UINT32N)

    @check_errors
    def non_dlms_get_network(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_NETWORK, UINT32N)

    @check_errors
    def non_dlms_get_channel(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_CHANNEL, UINT32N)

    @check_errors
    def non_dlms_get_rf_power(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_RF_POWER, INT8N)

    @check_errors
    def non_dlms_get_voltage(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_VOLTAGE, INT32N) / 1000.0
    non_dlms_get_voltage.units = 'volts'

    @check_errors
    def non_dlms_get_current(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_CURRENT, INT32N) / 1000.0
    non_dlms_get_current.units = 'amps'

    @check_errors
    def non_dlms_get_phase_current(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_PHASE_CURRENT, INT32N) / 1000.0
    non_dlms_get_phase_current.units = 'amps'

    @check_errors
    def non_dlms_get_neutral_current(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_NEUTRAL_CURRENT, INT32N) / 1000.0
    non_dlms_get_neutral_current.units = 'amps'

    @check_errors
    def non_dlms_get_active_energy(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ACTIVE_ENERGY, INT32N)
    non_dlms_get_active_energy.units = 'watt-hour'

    @check_errors
    def non_dlms_get_reactive_energy(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_REACTIVE_ENERGY, INT32N)
    non_dlms_get_reactive_energy.units = 'volt-ampere-reactive-hour'

    @check_errors
    def non_dlms_get_apparent_energy(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_APPARENT_ENERGY, INT32N)
    non_dlms_get_apparent_energy.units = 'volt-ampere-hour'

    @check_errors
    def non_dlms_get_live_tampers(self, addr):
        reply = []
        flag_byte = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_LIVE_TAMPERS, UINT32N)
        flag_byte = flag_byte % 256
        if flag_byte >= 128:
            raise ValueError("Bit 7 of flag_list was unexpectedly set.")
            flag_byte = flag_byte - 128
        if flag_byte >= 64:
            raise ValueError("Bit 6 of flag_list was unexpectedly set.")
            flag_byte = flag_byte - 64
        if flag_byte >= 32:
            reply.append(TamperFlag("NEUTRAL_DISTURBANCE"))
            flag_byte = flag_byte - 32
        if flag_byte >= 16:
            reply.append(TamperFlag("NEUTRAL_MISSING"))
            flag_byte = flag_byte - 16
        if flag_byte >= 8:
            reply.append(TamperFlag("COVER_OPEN"))
            flag_byte = flag_byte - 8
        if flag_byte >= 4:
            reply.append(TamperFlag("MAGNETIC"))
            flag_byte = flag_byte - 4
        if flag_byte >= 2:
            reply.append(TamperFlag("LINE_LOAD_REVERSAL"))
            flag_byte = flag_byte - 2
        if flag_byte >= 1:
            reply.append(TamperFlag("EARTH"))
            flag_byte = flag_byte - 1
        return reply

    @check_errors
    def non_dlms_get_active_power(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ACTIVE_POWER, INT32N) / 1000.0
    non_dlms_get_active_power.units = 'watts'

    @check_errors
    def non_dlms_get_frequency(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_FREQUENCY, INT32N) / 10.0
    non_dlms_get_frequency.units = 'Hz'

    @check_errors
    def non_dlms_get_power_factor(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_POWER_FACTOR, INT32N) / 1000.0

    @check_errors
    def non_dlms_get_credits(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_CREDITS, INT32N)
    non_dlms_get_credits.units = 'credits'

    # newly added====================================================================
    @check_errors
    def non_dlms_get_net_account(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_NET_ACCOUNT, INT32N)
    non_dlms_get_credits.units = 'credits'
    #================================================================================

    @check_errors
    def non_dlms_get_net_recharge(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_NET_RECHARGE, INT32N)
    non_dlms_get_credits.units = 'credits'

    @check_errors
    def non_dlms_get_pos_recharge(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_POS_RECHARGE, UINT32N)
    non_dlms_get_credits.units = 'credits'

    @check_errors
    def non_dlms_get_neg_recharge(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_NEG_RECHARGE, UINT32N)
    non_dlms_get_credits.units = 'credits'

    @check_errors
    def non_dlms_get_power_limit(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_POWER_LIMIT, UINT32N)
    non_dlms_get_power_limit.units = 'watts'

    @check_errors
    def non_dlms_get_energy_limit(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ENERGY_LIMIT, INT32N)
    non_dlms_get_energy_limit.units = 'watt-hour'

    @check_errors
    def non_dlms_get_energy_consumed_today(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ENERGY_CONSUMED_TODAY, INT32N)
    non_dlms_get_energy_consumed_today.units = 'watt-hour'

    @check_errors
    def non_dlms_get_price(self, addr):
        e_per_credit = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ENERGY_PER_CREDIT, UINT32N)
        credit_per_kwh = round(float(3600.00 * 1000.00 / e_per_credit), 2)
        return credit_per_kwh
    non_dlms_get_price.units = 'credits/kwh'

    @check_errors
    def non_dlms_get_address(self, addr):
        addr_int = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ADDRESS, UINT32N)
        addr1 = addr_int / (2**24)
        addr_int = addr_int - addr1 * (2**24)
        addr2 = addr_int / 2**16
        addr_int = addr_int - addr2 * (2**16)
        addr3 = addr_int / 2**8
        addr_int = addr_int - addr3 * (2**8)
        addr4 = addr_int
        addr_str = str(addr1) + "." + str(addr2) + "." + \
            str(addr3) + "." + str(addr4)
        address = Address(addr_str)
        return address

    @check_errors
    def non_dlms_get_tamper_record(self, addr, tamper_type):
        tamper_type = tamper_type.strip(' ')
        if tamper_type == "all":
            earth_record = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_EARTH_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
            rev_record = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_REV_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
            nm_record = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_NM_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
            nd_record = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_ND_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
            cover_record = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_COVER_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
            mag_record = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_MAG_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
            report = "{}\n{}\n{}\n{}\n{}\n{}\n".format(earth_record,
                                                       rev_record,
                                                       nm_record,
                                                       nd_record,
                                                       cover_record,
                                                       mag_record)
            return report
        elif tamper_type == "earth":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_EARTH_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
        elif tamper_type == "rev":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_REV_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
        elif tamper_type == "nm":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_NM_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
        elif tamper_type == "nd":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_ND_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
        elif tamper_type == "cover":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_COVER_TAMPER_RECORD, TAMPER_RECORD_PACKETN)
        elif tamper_type == "mag":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_MAG_TAMPER_RECORD, TAMPER_RECORD_PACKETN)

    @check_errors
    def non_dlms_get_dd_params(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_DD_PARAMS, DAILY_DEDUCTION_PARAMSN)

    @check_errors
    def non_dlms_get_survey_params(self, addr):
        LOAD_SURVEY_PARAMSN = 7
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_SURVEY_PARAMS, LOAD_SURVEY_PARAMSN)

    @check_errors
    def non_dlms_get_time(self, addr):
        time = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_TIME, UINT32N)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def non_dlms_get_live_version(self, addr):
        version = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_LIVE_VERSION, UINT32N)
        return version

    @check_errors
    def non_dlms_get_ext_version(self, addr):
        version = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_EXT_VERSION, UINT32N)
        return version

    @check_errors
    def non_dlms_get_newest_survey(self, addr):
        if self.non_dlms_get_num_surveys(addr) == 0:
            return "No surveys stored!"
        else:
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_NEWEST_SURVEY, BUNDLEN)

    @check_errors
    def non_dlms_get_oldest_survey(self, addr):
        if self.non_dlms_get_num_surveys(addr) == 0:
            return "No surveys stored!"
        else:
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_OLDEST_SURVEY, BUNDLEN)

    @check_errors
    def non_dlms_get_num_surveys(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_NUM_SURVEYS, UINT32N)

    @check_errors
    def non_dlms_get_newest_log(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_NEWEST_LOG, LOG_PACKETN)

    @check_errors
    def non_dlms_get_oldest_log(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_OLDEST_LOG, LOG_PACKETN)

    @check_errors
    def non_dlms_get_num_logs(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_NUM_LOGS, UINT32N)

    @check_errors
    def non_dlms_get_survey_interval(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_SURVEY_INTERVAL, UINT32N)
    non_dlms_get_survey_interval.units = "minutes"

    @check_errors
    def non_dlms_get_accurate_credits(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ACCURATE_CREDITS, PREPAID_ACCOUNT_PACKETN)
        # return self.my_simpleterm_masterN.get_param(addr,
        # commandMappingContainerN.GET_ACCURATE_CREDITS,PREPAID_ACCOUNT_PACKET)

    @check_errors
    def non_dlms_get_accounting_state(self, addr):
        # ACCOUNTING_STATE_PACKETN=10
        # return self.my_simpleterm_masterN.get_param(addr,
        # commandMappingContainerN.GET_ACTIVE_SLAB_INFO,
        # ACCOUNTING_STATE_PACKET)
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ACTIVE_SLAB_INFO, ACCOUNTING_STATE_PACKETN)

    @check_errors
    def non_dlms_get_slab_update_ts(self, addr):
        update_ts = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_SLAB_UPDATE_TS, UINT32N)
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=update_ts)

    @check_errors
    def non_dlms_get_fd_update_ts(self, addr):
        update_ts = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_FD_UPDATE_TS, UINT32N)
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=update_ts)

    @check_errors
    def non_dlms_get_active_fd_params(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ACTIVE_FD_PARAMS, FIXED_DEDUCTION_PACKETN)

    @check_errors
    def non_dlms_get_unlock_validity(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_UNLOCK_VALIDITY, UINT32N) / (3600 * 24)
        non_dlms_get_unlock_validity.units = "days"

    @check_errors
    def non_dlms_get_time_since_unlock(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_TIME_SINCE_UNLOCK, UINT32N) / (3600 * 24)
        non_dlms_get_time_since_unlock.units = "days"

    @check_errors
    def non_dlms_get_last_unlock_timestamp(self, addr):
        time = self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_UNLOCK_TIMESTAMP, UINT32N)
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=time)

    @check_errors
    def non_dlms_get_active_energy_offset(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_ACTIVE_ENERGY_OFFSET, INT32N)
    non_dlms_get_active_energy_offset.units = "watt-hour"

    @check_errors
    def non_dlms_get_reactive_energy_offset(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_REACTIVE_ENERGY_OFFSET, INT32N)
    non_dlms_get_reactive_energy_offset.units = "volt-ampere-reactive-hour"

    @check_errors
    def non_dlms_get_apparent_energy_offset(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_APPARENT_ENERGY_OFFSET, INT32N)
    non_dlms_get_apparent_energy_offset.units = "volt-ampere-hour"

    @check_errors
    def non_dlms_set_credit_limit(self, addr, credit_limit):
        credit_limit = int(credit_limit)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_CREDIT_LIMIT, credit_limit, INT32N)

    @check_errors
    def non_dlms_set_master_credits(self, addr, amount):
        amount = int(amount)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_MASTER_CREDITS, amount, UINT32N)

    @check_errors
    def non_dlms_set_address(self, addr, address):
        address = Address(str(address))
        addr_str_list = str(address).split('.')
        addr_int = int(addr_str_list[3])
        addr_int += int(addr_str_list[2]) * (2**8)
        addr_int += int(addr_str_list[1]) * (2**16)
        addr_int += int(addr_str_list[0]) * (2**24)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_ADDRESS, addr_int, UINT32N)

    @check_errors
    def non_dlms_set_channel(self, addr, channel):
        channel = int(channel)
        if channel > 16 or channel < 0:
            return "Invalid channel! Channel must be in the range of 0-16."
        else:
            return self.my_simpleterm_masterN.set_param(
                addr, commandMappingContainerN.SET_CHANNEL, channel, UINT32N)

    @check_errors
    def non_dlms_set_rf_power(self, addr, rf_power):
        rf_power = int(rf_power)
        if rf_power > 5 or rf_power < 1:
            return "Invalid value! RF Power must be in the range of 1-5."
        else:
            return self.my_simpleterm_masterN.set_param(
                addr, commandMappingContainerN.SET_RF_POWER, rf_power, INT8N)

    @check_errors
    def non_dlms_set_network(self, addr, network):
        network = int(network)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_NETWORK, network, UINT32N)

    @check_errors
    def non_dlms_set_rc_buffer_margin(self, addr, rc_buffer_margin):
        rc_buffer_margin = int(rc_buffer_margin)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_RC_BUFFER_MARGIN, rc_buffer_margin, UINT32N)

    @check_errors
    def non_dlms_set_rc_timeout(self, addr, rc_timeout):
        rc_timeout = int(rc_timeout)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_RC_TIMEOUT, rc_timeout, UINT32N)

    @check_errors
    def non_dlms_set_power_limit(self, addr, power_limit):
        power_limit = int(power_limit)
        if power_limit < 1 or power_limit > 4294967:
            return "Invalid value! Power limit should be in the range of 1 to 4294967."
        else:
            return self.my_simpleterm_masterN.set_param(
                addr, commandMappingContainerN.SET_POWER_LIMIT, power_limit, UINT32N)

    @check_errors
    def non_dlms_set_energy_limit(self, addr, energy_limit):
        energy_limit = int(energy_limit)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_ENERGY_LIMIT, energy_limit, INT32N)

    @check_errors
    def non_dlms_set_active_energy_offset(self, addr, active_offset):
        active_offset = int(active_offset)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_ACTIVE_ENERGY_OFFSET, active_offset, INT32N)

    @check_errors
    def non_dlms_set_reactive_energy_offset(self, addr, reactive_offset):
        reactive_offset = int(reactive_offset)
        return self.my_simpleterm_masterN.set_param(
            addr,
            commandMappingContainerN.SET_REACTIVE_ENERGY_OFFSET,
            reactive_offset,
            INT32N)

    @check_errors
    def non_dlms_set_apparent_energy_offset(self, addr, apparent_offset):
        apparent_offset = int(apparent_offset)
        return self.my_simpleterm_masterN.set_param(
            addr,
            commandMappingContainerN.SET_APPARENT_ENERGY_OFFSET,
            apparent_offset,
            INT32N)

    @check_errors
    def non_dlms_set_price(self, addr, price):
        price = float(price)
        if float(price) <= 0.00 or float(price) >= 100.00:
            return "Invalid price input! Price must be higher than 0.00, and lower than 100.00."
        if float(price) != 0.0:
            e_per_credit = int(round(3600 * 1000 / float(price), 0))
        else:
            e_per_credit = 1.0
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_ENERGY_PER_CREDIT, e_per_credit, UINT32N)

    @check_errors
    def non_dlms_set_dd_params(self, addr, ddp):
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_DD_PARAMS, ddp, DAILY_DEDUCTION_PARAMSN)

    @check_errors
    def non_dlms_set_survey_params(self, addr, lsp):
        if not isinstance(lsp, LoadSurveyParams):
            args = lsp.split(",")
            if "now" in args[0]:
                delta = int(args[0].split("+")[1])
                start_time = datetime.datetime.now() + datetime.timedelta(seconds=delta)
            else:
                start_time = dateutil.parser.parse(args[0].strip(' '))
            interval = int(args[1])
            status = int(args[2])
            lsp = LoadSurveyParams()
            lsp.start_time = start_time
            lsp.interval = interval
            lsp.status = status

        seconds_since_epoch = int(
            (lsp.start_time -
             datetime.datetime(
                 1970,
                 1,
                 1)).total_seconds())
        meterTime = self.get_time(addr)
        meter_seconds_since_epoch = int(
            (meterTime - datetime.datetime(1970, 1, 1)).total_seconds())
        if (meter_seconds_since_epoch >= seconds_since_epoch):
            return "Error! Entered survey start time cannot be behind the current meter time!"

        interval = int(lsp.interval)
        if interval > 0 and interval <= 60 and (60 % interval) == 0:
            return self.my_simpleterm_masterN.set_param(
                addr, commandMappingContainerN.SET_SURVEY_PARAMS, lsp, LOAD_SURVEY_PARAMSN)
        else:
            return "Survey interval must be in the range of 0-60 minutes, and it must be a factor of 60!"

    @check_errors
    def non_dlms_set_slab_params(self, addr, args):
        scp = SlabConfigurationPacketN()
        scp.no_of_slabs = int(args.split(",")[0])
        scp.slab_price = map(
            int, (args.split("[")[1]).split("]")[0].split(","))
        scp.slab_limits = map(
            int, (args.split("[")[2]).split("]")[0].split(","))
        scp.mmc = int(args.split("],")[2])

        if (scp.no_of_slabs < 1 or scp.no_of_slabs > 6):
            return "Error! Number of slabs should be in the range of 1 to 6!"
        elif len(scp.slab_price) != 6:
            return "Error! 6 parameters need to be entered for slab_price!"
        elif len(scp.slab_limits) != 5:
            return "Error! 6 parameters need to be entered for slab_limits!"

        for index in range(len(scp.slab_price)):
            if index < scp.no_of_slabs:
                if scp.slab_price[index] < 1 or scp.slab_price[index] > 65000:
                    return "Error! Slab prices should be in the range of 1 to 65000!"
            else:
                if scp.slab_price[index] != 0:
                    return "Error! Number of slab prices entered is more than number of slabs!"

        for index in range(len(scp.slab_limits)):
            if index < (scp.no_of_slabs - 1):
                if scp.slab_limits[index] < 1 or scp.slab_limits[index] > 65000:
                    return "Error! Slab limits should be in the range of 1 to 65000!"
            else:
                if scp.slab_limits[index] != 0:
                    return "Error! Number of slab limits entered is more than number of slabs!"

            if index > 0 and index < (scp.no_of_slabs - 1):
                if scp.slab_limits[index] <= scp.slab_limits[index - 1]:
                    return "Error! Slab limits should be in increasing order!"

        if scp.mmc < 0 or scp.mmc > 65000:
            return "Error! MMC should be in the range of 0 to 65000!"

        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_SL_PARAMS, scp, SLAB_CONFIGURATION_PACKETN)

    @check_errors
    def non_dlms_set_slab_update_ts(self, addr, args):
        dt_string = args.split(",")
        if "now" in dt_string[0]:
            delta = int(dt_string[0].split("+")[1])
            updateTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            updateTime = dateutil.parser.parse(dt_string[0].strip(' '))
        if not isinstance(updateTime, datetime.datetime):
            updateTime = dateutil.parser.parse(updateTime)

        seconds_since_epoch = int(
            (updateTime - datetime.datetime(1970, 1, 1)).total_seconds())
        meterTime = self.get_time(addr)
        meter_seconds_since_epoch = int(
            (meterTime - datetime.datetime(1970, 1, 1)).total_seconds())
        if (meter_seconds_since_epoch >= seconds_since_epoch):
            return "Error! Entered update TS cannot be behind the current meter time!"

        return self.my_simpleterm_masterN.set_param(
            addr,
            commandMappingContainerN.SET_SLAB_UPDATE_TS,
            int(seconds_since_epoch),
            UINT32N)
			
    @check_errors
    def set_serial_number(self, addr, serial_number):
        if int(serial_number) < 00000000 or int(serial_number) > 99999999:
            return "Error! Meter serial number should be in the range of 00000000 to 99999999!"
        else:
            return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_METER_SERIAL_NO, serial_number, UINT32)

    @check_errors
    def set_relay_mode(self, addr, calib_number):
        if calib_number == "":
            calib_number = 0
        else:
            calib_number = int(calib_number)
            if calib_number > 6:
                calib_number = 6
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.RELAY_MODE, calib_number, INT8)
		
    @check_errors
    def non_dlms_set_fd_params(self, addr, args):
        fdp = FixedDeductionPacket()
        fdp.amount = int(args.split(",")[0])
        fdp.type_of_deduction = str(args.split(",")[1])
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_FD_PARAMS, fdp, FIXED_DEDUCTION_PACKETN)

    @check_errors
    def unlock(self, addr, unlock_validity):
        unlock_validity = (int(unlock_validity) * 3600 * 24)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_UNLOCK, unlock_validity, UINT32N)

    @check_errors
    def non_dlms_set_fd_update_ts(self, addr, args):
        args = args.split(",")
        if "now" in args[0]:
            delta = int(args[0].split("+")[1])
            updateTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            updateTime = dateutil.parser.parse(args[0].strip(' '))
        if not isinstance(updateTime, datetime.datetime):
            updateTime = dateutil.parser.parse(updateTime)

        seconds_since_epoch = int(
            (updateTime - datetime.datetime(1970, 1, 1)).total_seconds())
        meterTime = self.get_time(addr)
        meter_seconds_since_epoch = int(
            (meterTime - datetime.datetime(1970, 1, 1)).total_seconds())
        if (meter_seconds_since_epoch >= seconds_since_epoch):
            return "Error! Entered update TS cannot be behind the current meter time!"

        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_FD_UPDATE_TS, seconds_since_epoch, UINT32N)

    @check_errors
    def non_dlms_set_fd_params(self, addr, args):
        fdp = FixedDeductionPacket()
        fdp.amount = int(args.split(",")[0])
        fdp.type_of_deduction = str(args.split(",")[1])
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_FD_PARAMS, fdp, FIXED_DEDUCTION_PACKETN)

    @check_errors
    def non_dlms_unlock(self, addr, unlock_validity):
        unlock_validity = (int(unlock_validity) * 3600 * 24)
        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_UNLOCK, unlock_validity, UINT32N)

    @check_errors
    def non_dlms_set_fd_update_ts(self, addr, args):
        args = args.split(",")
        if "now" in args[0]:
            delta = int(args[0].split("+")[1])
            updateTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            updateTime = dateutil.parser.parse(args[0].strip(' '))
        if not isinstance(updateTime, datetime.datetime):
            updateTime = dateutil.parser.parse(updateTime)

        seconds_since_epoch = int(
            (updateTime - datetime.datetime(1970, 1, 1)).total_seconds())
        meterTime = self.get_time(addr)
        meter_seconds_since_epoch = int(
            (meterTime - datetime.datetime(1970, 1, 1)).total_seconds())
        if (meter_seconds_since_epoch >= seconds_since_epoch):
            return "Error! Entered update TS cannot be behind the current meter time!"

        return self.my_simpleterm_masterN.set_param(
            addr, commandMappingContainerN.SET_FD_UPDATE_TS, seconds_since_epoch, UINT32N)

    @check_errors
    def non_dlms_syncstream_bundle(self, addr):
        return self.my_syncstream_masterN.get_bundle(addr)

    @check_errors
    def non_dlms_syncstream_setup(self, addr, interval):
        return self.my_syncstream_masterN.setup(addr, interval)

    @check_errors
    def non_dlms_syncstream_params(self, addr):
        return self.my_syncstream_masterN.get_params(addr)

    @check_errors
    def non_dlms_syncstream_reset(self, addr):
        return self.my_syncstream_masterN.reset(addr)

    @check_errors
    def non_dlms_clear_load_survey(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.CLEAR_LOAD_SURVEY)

    @check_errors
    def non_dlms_enable_survey(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.ENABLE_SURVEY)


# Maximum Demand Commands

    @check_errors
    def clear_MD_month(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_MD_MONTH_ALL)
        elif MD_month == "-6":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_MD_MONTH_1)
        elif MD_month == "-5":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_MD_MONTH_2)
        elif MD_month == "-4":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_MD_MONTH_3)
        elif MD_month == "-3":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_MD_MONTH_4)
        elif MD_month == "-2":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_MD_MONTH_5)
        elif MD_month == "-1":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_MD_MONTH_6)
        elif MD_month == "0":
            return self.my_simpleterm_master.execute_command(
                addr, commandMappingContainer.CLEAR_MD_MONTH_7)

    @check_errors
    def get_instantaneous_MD(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_INSTANTANEOUS_MD, UINT32)
    get_instantaneous_MD.units = 'watts'

    @check_errors
    def get_current_MD(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_CURRENT_MD, MAXIMUM_DEMAND_PACKET)

    @check_errors
    def get_past_MD(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            month_1 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_1, MAXIMUM_DEMAND_PACKET)
            month_2 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_2, MAXIMUM_DEMAND_PACKET)
            month_3 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_3, MAXIMUM_DEMAND_PACKET)
            month_4 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_4, MAXIMUM_DEMAND_PACKET)
            month_5 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_5, MAXIMUM_DEMAND_PACKET)
            month_6 = self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_6, MAXIMUM_DEMAND_PACKET)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n".format(month_6,
                                                          month_5,
                                                          month_4,
                                                          month_3,
                                                          month_2,
                                                          month_1)
            return month_all
        elif MD_month == "-6":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_1, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-5":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_2, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-4":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_3, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-3":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_4, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-2":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_5, MAXIMUM_DEMAND_PACKET)
        elif MD_month == "-1":
            return self.my_simpleterm_master.get_param(
                addr, commandMappingContainer.GET_PAST_MD_6, MAXIMUM_DEMAND_PACKET)

    @check_errors
    def get_MD_avg_period(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_MD_AVG_PERIOD, UINT32)
    get_MD_avg_period.units = 'minutes'

    # @check_errors
    # def get_MD_ignorance_period(self, addr):
    #     return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_MD_IGNORANCE_PERIOD, UINT32)
    # get_MD_ignorance_period.units = 'seconds'

    # @check_errors
    # def set_MD_ignorance_period(self, addr, ignorance_period):
    #     ignorance_period = int(ignorance_period)
    #     if ignorance_period >= int(self.get_MD_avg_period(addr)):
    #         return "Error! Ignorance period cannot be greater than the MD averaging period!"
    #     else:
    # return self.my_simpleterm_master.set_param(addr,
    # commandMappingContainer.SET_MD_IGNORANCE_PERIOD, ignorance_period,
    # UINT32)

    @check_errors
    def get_MD_LCD_display(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_MD_PAST_LCD_DISPLAY, UINT32)

    @check_errors
    def set_MD_LCD_display(self, addr, past_display):
        past_display = int(past_display)
        if past_display < 0 or past_display > 6:
            return "Invalid value! Value must be in the range of 0-6."
        else:
            return self.my_simpleterm_master.set_param(
                addr, commandMappingContainer.SET_MD_PAST_LCD_DISPLAY, past_display, UINT32)


# NON-DLMS Maximum Demand Commands

    @check_errors
    def non_dlms_clear_MD_month(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            return self.my_simpleterm_masterN.execute_command(
                addr, commandMappingContainerN.CLEAR_MD_MONTH_ALL)
        elif MD_month == "-6":
            return self.my_simpleterm_masterN.execute_command(
                addr, commandMappingContainerN.CLEAR_MD_MONTH_1)
        elif MD_month == "-5":
            return self.my_simpleterm_masterN.execute_command(
                addr, commandMappingContainerN.CLEAR_MD_MONTH_2)
        elif MD_month == "-4":
            return self.my_simpleterm_masterN.execute_command(
                addr, commandMappingContainerN.CLEAR_MD_MONTH_3)
        elif MD_month == "-3":
            return self.my_simpleterm_masterN.execute_command(
                addr, commandMappingContainerN.CLEAR_MD_MONTH_4)
        elif MD_month == "-2":
            return self.my_simpleterm_masterN.execute_command(
                addr, commandMappingContainerN.CLEAR_MD_MONTH_5)
        elif MD_month == "-1":
            return self.my_simpleterm_masterN.execute_command(
                addr, commandMappingContainerN.CLEAR_MD_MONTH_6)
        elif MD_month == "0":
            return self.my_simpleterm_masterN.execute_command(
                addr, commandMappingContainerN.CLEAR_MD_MONTH_7)

    @check_errors
    def non_dlms_get_instantaneous_MD(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_INSTANTANEOUS_MD, UINT32N)
    get_instantaneous_MD.units = 'watts'

    @check_errors
    def non_dlms_get_current_MD(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_CURRENT_MD, MAXIMUM_DEMAND_PACKETN)

    @check_errors
    def non_dlms_get_past_MD(self, addr, MD_month):
        MD_month = MD_month.strip(' ')
        if MD_month == "all":
            month_1 = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_1, MAXIMUM_DEMAND_PACKETN)
            month_2 = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_2, MAXIMUM_DEMAND_PACKETN)
            month_3 = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_3, MAXIMUM_DEMAND_PACKETN)
            month_4 = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_4, MAXIMUM_DEMAND_PACKETN)
            month_5 = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_5, MAXIMUM_DEMAND_PACKETN)
            month_6 = self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_6, MAXIMUM_DEMAND_PACKETN)
            month_all = "{}\n{}\n{}\n{}\n{}\n{}\n".format(month_6,
                                                          month_5,
                                                          month_4,
                                                          month_3,
                                                          month_2,
                                                          month_1)
            return month_all
        elif MD_month == "-6":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_1, MAXIMUM_DEMAND_PACKETN)
        elif MD_month == "-5":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_2, MAXIMUM_DEMAND_PACKETN)
        elif MD_month == "-4":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_3, MAXIMUM_DEMAND_PACKETN)
        elif MD_month == "-3":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_4, MAXIMUM_DEMAND_PACKETN)
        elif MD_month == "-2":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_5, MAXIMUM_DEMAND_PACKETN)
        elif MD_month == "-1":
            return self.my_simpleterm_masterN.get_param(
                addr, commandMappingContainerN.GET_PAST_MD_6, MAXIMUM_DEMAND_PACKETN)

    @check_errors
    def non_dlms_get_MD_avg_period(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_MD_AVG_PERIOD, UINT32N)
    get_MD_avg_period.units = 'minutes'

    # @check_errors
    # def get_MD_ignorance_period(self, addr):
    #     return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_MD_IGNORANCE_PERIOD, UINT32)
    # get_MD_ignorance_period.units = 'seconds'

    @check_errors
    def non_dlms_set_MD_avg_period(self, addr, avg_period):
        avg_period = int(avg_period)
        if avg_period == 0:
            avg_period = 1

        if avg_period > 0 and avg_period <= 60 and (60 % avg_period) == 0:
            return self.my_simpleterm_masterN.set_param(
                addr, commandMappingContainerN.SET_MD_AVG_PERIOD, avg_period, UINT32N)
        else:
            return "MD averaging period must be in the range of 0-60 minutes, and it must be a factor of 60!"

    # @check_errors
    # def set_MD_ignorance_period(self, addr, ignorance_period):
    #     ignorance_period = int(ignorance_period)
    #     if ignorance_period >= int(self.get_MD_avg_period(addr)):
    #         return "Error! Ignorance period cannot be greater than the MD averaging period!"
    #     else:
    # return self.my_simpleterm_master.set_param(addr,
    # commandMappingContainer.SET_MD_IGNORANCE_PERIOD, ignorance_period,
    # UINT32)

    @check_errors
    def non_dlms_get_MD_LCD_display(self, addr):
        return self.my_simpleterm_masterN.get_param(
            addr, commandMappingContainerN.GET_MD_PAST_LCD_DISPLAY, UINT32N)

    @check_errors
    def non_dlms_set_MD_LCD_display(self, addr, past_display):
        past_display = int(past_display)
        if past_display < 0 or past_display > 6:
            return "Invalid value! Value must be in the range of 0-6."
        else:
            return self.my_simpleterm_masterN.set_param(
                addr, commandMappingContainerN.SET_MD_PAST_LCD_DISPLAY, past_display, UINT32N)
########

    def non_dlms_log_print_direct(self, line):
        self.loggern.update_header()
        self.loggern.print_log_from_node()

    def non_dlms_log_dump_bin(self, line):
        self.loggern.update_header()
        self.loggern.dump("log.bin")
        self.loggern.dump_header_to_file("header.json")

    def non_dlms_log_print_bin(self, line):
        self.loggern.load_header_from_file("header.json")
        self.loggern.print_log_from_bin("log.bin")

    def non_dlms_log_header(self, line):
        self.loggern.update_header()
        self.loggern.dump_header_to_file("header.json")
        print (self.loggern.header)

    def non_dlms_survey_print_direct(self, line):
        self.load_surveyn.update_header()
        self.load_surveyn.print_survey_from_node()

    def non_dlms_survey_store_file(self, line):
        self.load_surveyn.update_header()
        self.load_surveyn.store_survey_in_file()

    def non_dlms_survey_dump_bin(self, line):
        self.load_surveyn.update_header()
        self.load_surveyn.dump("survey.bin")
        self.load_surveyn.dump_header_to_file("header.json")

    def non_dlms_survey_print_bin(self, line):
        self.load_surveyn.load_header_from_file("header.json")
        self.load_surveyn.print_survey_from_bin("survey.bin")

    def non_dlms_survey_header(self, line):
        self.load_surveyn.update_header()
        self.load_surveyn.dump_header_to_file("header.json")
        print(self.load_surveyn.header)

    def non_dlms_survey_to_store(self, line):
        self.load_surveyn.survey_to_store("survey.bin")

    @check_errors
    def non_dlms_factory_init(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.FACTORY_INIT)
    
    @check_errors
    def non_dlms_reset(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.BOARD_RESET)

    @check_errors
    def non_dlms_gateway(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.GATEWAY)

    @check_errors
    def non_dlms_router(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.ROUTER)

    @check_errors
    def non_dlms_assert_false(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.ASSERT_FALSE)


    @check_errors
    def non_dlms_clear_nvm(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.CLEAR_NVM)

    @check_errors
    def non_dlms_clear_recharges(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.CLEAR_RECHARGES)

    @check_errors
    def non_dlms_deassert(self, addr):
        return self.my_simpleterm_masterN.execute_command(addr, "x%?")

    @check_errors
    def non_dlms_clear_account(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.CLEAR_ACCOUNT)


    @check_errors
    def non_dlms_clear_log(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.CLEAR_LOG)

    @check_errors
    def non_dlms_allow_negative_credits(self, addr):
        reply = self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.ALLOW_NEGATIVE_CREDITS)
        return reply

    @check_errors
    def non_dlms_forbid_negative_credits(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.FORBID_NEGATIVE_CREDITS)


    @check_errors
    def non_dlms_request_recharge(self, addr):
        amount = int(amount)
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.REQUEST_RECHARGE)

    @check_errors
    def non_dlms_disable_elimiter(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.DISABLE_ELIMITER)

    @check_errors
    def non_dlms_enable_elimiter(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.ENABLE_ELIMITER)


    @check_errors
    def non_dlms_enable_lock(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.ENABLE_LOCK)

    @check_errors
    def non_dlms_disable_lock(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.DISABLE_LOCK)

    @check_errors
    def non_dlms_reset_lock(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.RESET_LOCK)

    @check_errors
    def non_dlms_lock_state(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.LOCK_STATE)

    @check_errors
    def non_dlms_broadcast_time(self, addr):
        return self.my_simpletime_masterN.broadcast_time()

    @check_errors
    def non_dlms_fd_enable(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.FD_ENABLE)

    @check_errors
    def non_dlms_fd_disable(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.FD_DISABLE)

    @check_errors
    def non_dlms_fd_reset(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.FD_RESET)

# Relay non dlms

    @check_errors
    def non_dlms_turn_relay_on(self, addr):
        reply = self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.TURN_RELAY_ON)
        return reply

    @check_errors
    def non_dlms_turn_relay_off(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.TURN_RELAY_OFF)

    @check_errors
    def non_dlms_relay_manual_control(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.RELAY_MANUAL_CONTROL)

    @check_errors
    def non_dlms_relay_auto_control(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.RELAY_AUTO_CONTROL)

    @check_errors
    def non_dlms_relay_state(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.RELAY_STATE)


# recharge 1p non-dlms

    @check_errors
    def non_dlms_recharge(self, addr, amount):
        amount = int(amount)
        return self.my_recharge_masterN.recharge(addr, amount)

    @check_errors
    def non_dlms_beat_time(self, addr):
        unix_time = self.my_syncstream_masterN.get_current_beat_time()
        return datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=unix_time)

# Flash IO commands

    @check_errors
    def non_dlms_mem_write(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        data = args[1].split(' ')
        while '' in data:
            data.remove('')
        data_bytearray = bytearray()
        for entry in data:
            entry = int(entry, 16)
            data_bytearray.append(entry)

        return self.my_flash_io_masterN.write(
            addr, start_address, data_bytearray)

    @check_errors
    def non_dlms_mem_read(self, addr, line):
        args = line.split(',')
        start_address = int(args[0], 16)
        length = int(args[1])
        return self.my_flash_io_masterN.read(addr, start_address, length)

    @check_errors
    def non_dlms_mem_erase_block(self, addr, line):
        return self.my_flash_io_masterN.erase(addr, int(line))


# Maxwell calibration commands

    @check_errors
    def non_dlms_maxwell_cal_time(self, addr, cal_time):
        if cal_time == 0:
            return "Error! This command needs an argument!"
        if cal_time == "now":
            cal_time = datetime.datetime.now()
        if not isinstance(cal_time, datetime.datetime):
            cal_time = dateutil.parser.parse(cal_time)
        payload = get_command_string(TIME_DATE_CODE, cal_time)
        return self.my_maxwell_bridge_master.send(addr, payload)

    @check_errors
    def non_dlms_maxwell_cal_mtrno(self, addr, serial_num):
        payload = get_command_string(MTRNO_CODE, serial_num)
        if int(serial_num) < 100000 or int(serial_num) > 999999:
            return "Error! Meter serial number should be in the range of 100000 to 999999!"
        else:
            return self.my_maxwell_bridge_master.send(addr, payload)

    def non_dlms_maxwell_cal_energy(self, addr, error_percent):
        if not isinstance(error_percent, float):
            error_percent = float(error_percent)
        payload = get_command_string(ENERGY_CAL_CODE, float(error_percent))
        return self.my_maxwell_bridge_master.send(addr, payload)

    @check_errors
    def non_dlms_maxwell_clear_1(self, addr):
        payload = get_command_string(CLEAR_1_CODE)
        return self.my_maxwell_bridge_master.send(addr, payload)

    @check_errors
    def non_dlms_maxwell_clear_2(self, addr):
        payload = get_command_string(CLEAR_2_CODE)
        return self.my_maxwell_bridge_master.send(addr, payload)

    def non_dlms_maxwell_cal_v(self, addr):
        payload = get_command_string(VICAL_CODE, 'v')
        return self.my_maxwell_bridge_master.send(addr, payload)

    def non_dlms_maxwell_cal_ip(self, addr):
        payload = get_command_string(VICAL_CODE, 'ip')
        return self.my_maxwell_bridge_master.send(addr, payload)

    def non_dlms_maxwell_cal_in(self, addr):
        payload = get_command_string(VICAL_CODE, 'in')
        return self.my_maxwell_bridge_master.send(addr, payload)

    def non_dlms_maxwell_meter_lock(self, addr):
        return self.my_maxwell_bridge_master.lock(addr)

    @check_errors
    def non_dlms_trace_path(self, addr):
        return self.rf_command_handler.trace_path(addr)

    @check_errors
    def non_dlms_disable_survey(self, addr):
        return self.my_simpleterm_masterN.execute_command(
            addr, commandMappingContainerN.DISABLE_SURVEY)
			
    # @check_errors
    # def do_clear_energy_registers(self, addr):
    #     return self.my_simpleterm_master.execute_command(addr, commandMappingContainer.CLEAR_ENERGY_REGISTERS)

    @check_errors
    def enable_print_rxtx(self, addr):
        return self.my_tap_handler.print_status(True)
		
    @check_errors
    def disable_print_rxtx(self, addr):
        return self.my_tap_handler.print_status(False)
		
    @check_errors
    def set_ipv6_address(self,addr,args):
        # print (I am here)
        final_str = ''
        buf = bytearray()

        ipv6_addr = args.split('.')
        if len(ipv6_addr) != 8:
            return "Incorrect IPV6 Address Format"    

        for i in range(0,8):
            if len(ipv6_addr[i]) > 4:
                print("Incorrect IPV6 Address Format")
                return "length should be less than or equal to 4"
            temp_str = ''
            for z in range(0,(4-len(ipv6_addr[i]))):
                temp_str += "0"
            temp_str += ipv6_addr[i]
            final_str += temp_str
            final_str +=":"

        # print (final_str)

        for i in range(0,len(final_str)-1):
            buf.extend(chr(ord(final_str[i])))

        # for j in range(0,len(buf)):
        #     print (hex(buf[j]))
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_IPV6_ADDRESS, buf, BYTE_ARRAY)

    @check_errors
    def get_ipv6_address(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_IPV6_ADDRESS, BYTE_ARRAY_IPV6)
		
    # OYO prepaid commands ================================================
    @check_errors
    def get_prepaid_info(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_PREPAID_INFO,TARIFF_PACKET)

    @check_errors
    def get_num_prepaid_logs(self, addr):
        return self.my_simpleterm_master.get_param(
            addr, commandMappingContainer.GET_NUM_ASSIGN_DEASSGN_LOG, UINT32)

    @check_errors
    def get_prepaid_logs_by_index(self, addr, index):
        return self.my_simpleterm_master.set_and_get_param(addr,commandMappingContainer.GET_ASSIGN_DEASSIGN_LOG_BY_INDEX, index, UINT32,TARIFF_PACKET)

    @check_errors
    def assign(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.ASSIGN,UINT32)/100.00
    @check_errors
    def deassign(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.DEASSIGN,UINT32)/100.00
    @check_errors
    def enable_dg_tariff(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.ENABLE_DG_TARIFF, BUNDLE_PREPAID_OK)
    @check_errors
    def enable_eg_tariff(self, addr):
        return self.my_simpleterm_master.get_param(addr, commandMappingContainer.ENABLE_EG_TARIFF, BUNDLE_PREPAID_OK)

    @check_errors
    def get_tariff_group_info(self, addr, groupNo):
        if groupNo > 2 or groupNo < 0:
            print("Only 2 groups are available")
            return
        elif groupNo == 1:        
            return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_GROUP1_INFO, TARIFF_PACKET)
        elif groupNo == 2:
            return self.my_simpleterm_master.get_param(addr, commandMappingContainer.GET_GROUP2_INFO, TARIFF_PACKET)

    @check_errors
    def three_ph_set_dg_tariff_params(self, addr, args):
        scp = TariffPacket3P()
        scp.tariffType      = int(0)   
        scp.fdType          = int(args.split(",")[0])
        scp.fdTelescopicF   = int(args.split(",")[1])
        scp.mmcApplication  = int(args.split(",")[2])
        
         
        friendlyHoursPM     = int(args.split(",")[3]) - 12
        if friendlyHoursPM == -12:
            friendlyHoursPM = 0
        friendlyHoursAM     = int(args.split(",")[4])

        
        if friendlyHoursPM < 0 or friendlyHoursPM > 13:
            print("Incorrect format of friendly hours PM")
        if friendlyHoursAM < 0 or friendlyHoursAM > 13:
            print("Incorrect format of friendly hours AM")

        scp.friendlyHours   = int(friendlyHoursAM + friendlyHoursPM*16)

        scp.alertLimit      = int(args.split(",")[5])
        scp.emergencyCredit = int(args.split(",")[6])
        scp.topUpLimit      = int(args.split(",")[7])
        scp.mmc             = int(args.split(",")[8])

        scp.fdPrice = map(int,(args.split("[")[1]).split("]")[0].split(","))
        scp.energyPrice = map(int,(args.split("[")[2]).split("]")[0].split(","))

        for x in xrange(0,len(scp.energyPrice)):
            scp.energyPrice[x] = scp.energyPrice[x]*10

        scp.energySlab = map(int,(args.split("[")[3]).split("]")[0].split(","))
        
        if len(scp.fdPrice) != 6:
            return "Error! 6 parameters need to be entered for fdPrice!"
        elif len(scp.energyPrice) != 6:
            return "Error! 6 parameters need to be entered for energyPrice!"
        elif len(scp.energySlab) != 5:
            return "Error! 5 parameters need to be entered for energySlab!"

        for index in range(len(scp.fdPrice)):
            if scp.fdPrice[index] < 0 or scp.fdPrice[index] > 10000000:
                return "Error! Slab prices should be in the range of 0 to 10000000 Paisa!"

        for index in range(len(scp.energyPrice)):
            if scp.energyPrice[index] < 0 or scp.energyPrice[index] > 60000:
                return "Error! Slab prices should be in the range of 0 to 60000!"
        if scp.mmc < 0 or scp.mmc > 600000:
            return "Error! MMC should be in the range of 0 to 600000!"


        for index in range(len(scp.energySlab)):
            if index > 0:
                if scp.energySlab[index] < 0 or scp.energySlab[index] > 60000:
                    return "Error! Slab limits should be in the range of 1 to 60000!"



        print("\n\n",scp,"\n\n")
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_TARIFF_PARAMS, scp, TARIFF_PACKET)
    @check_errors
    def three_ph_set_eg_tariff_params(self, addr, args):
        scp = TariffPacket3P()
        scp.tariffType      = int(1)   
        scp.fdType          = int(args.split(",")[0])
        scp.fdTelescopicF   = int(args.split(",")[1])
        scp.mmcApplication  = int(args.split(",")[2])
        
         
        friendlyHoursPM     = int(args.split(",")[3]) - 12
        if friendlyHoursPM == -12:
            friendlyHoursPM = 0
        friendlyHoursAM     = int(args.split(",")[4])

        
        if friendlyHoursPM < 0 or friendlyHoursPM > 13:
            print ("Incorrect format of friendly hours PM")
        if friendlyHoursAM < 0 or friendlyHoursAM > 13:
            print("Incorrect format of friendly hours AM")

        scp.friendlyHours   = int(friendlyHoursAM + friendlyHoursPM*16)

        scp.alertLimit      = int(args.split(",")[5])
        scp.emergencyCredit = int(args.split(",")[6])
        scp.topUpLimit      = int(args.split(",")[7])
        scp.mmc             = int(args.split(",")[8])

        scp.fdPrice = map(int,(args.split("[")[1]).split("]")[0].split(","))
        scp.energyPrice = map(int,(args.split("[")[2]).split("]")[0].split(","))
        scp.energySlab = map(int,(args.split("[")[3]).split("]")[0].split(","))
        
        if len(scp.fdPrice) != 6:
            return "Error! 6 parameters need to be entered for fdPrice!"
        elif len(scp.energyPrice) != 6:
            return "Error! 6 parameters need to be entered for energyPrice!"
        elif len(scp.energySlab) != 5:
            return "Error! 5 parameters need to be entered for energySlab!"

        for index in range(len(scp.fdPrice)):
            if scp.fdPrice[index] < 0 or scp.fdPrice[index] > 10000000:
                return "Error! Slab prices should be in the range of 0 to 10000000 Paisa!"

        for index in range(len(scp.energyPrice)):
            if scp.energyPrice[index] < 0 or scp.energyPrice[index] > 60000:
                return "Error! Slab prices should be in the range of 0 to 60000!"
        if scp.mmc < 0 or scp.mmc > 600000:
            return "Error! MMC should be in the range of 0 to 600000!"


        for index in range(len(scp.energySlab)):
            if index > 0:
                if scp.energySlab[index] < 0 or scp.energySlab[index] > 60000:
                    return "Error! Slab limits should be in the range of 1 to 60000!"



        print("\n\n",scp,"\n\n")
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_TARIFF_PARAMS, scp, TARIFF_PACKET)

    @check_errors
    def set_fd_tariff(self, addr, args):

        fdType          = int(args.split(",")[0])
        fdPrice         = int(args.split(",")[1])

        if fdPrice < 0 or fdPrice > 10000000:
            return "Error! FD prices should be in the range of 0 to 10000000 Paisa!"

        if fdType < 0 or fdType >1:
            return "Error! FD type should be Daily or Monthly"

        buf = bytearray()
        buf.extend(serialize.serialize_uint8(fdType))
        buf.extend(serialize.serialize_uint32(fdPrice))
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_FD_TARIFF, buf, BYTE_ARRAY)

    @check_errors
    def set_eg_tariff_params(self, addr, args):
        scp = TariffPacket()
        scp.tariffType      = int(1)   
        scp.fdType          = int(args.split(",")[0])
        scp.fdTelescopicF   = int(args.split(",")[1])
        scp.mmcApplication  = int(args.split(",")[2])
        
         
        friendlyHoursPM     = int(args.split(",")[3])
        if friendlyHoursPM > 0 and (friendlyHoursPM == 24 or friendlyHoursPM < 13):
            return "friendly Start hours should between from 13:00 to 23:00"

        if friendlyHoursPM > 0:    
            friendlyHoursPM     = friendlyHoursPM - 12

        friendlyHoursAM     = int(args.split(",")[4])
        if friendlyHoursAM != 0 and friendlyHoursAM > 12:
            return "friendly End hours should between from 1:00 to 12:00"

        scp.friendlyHours   = int(friendlyHoursAM + friendlyHoursPM*16)

        scp.alertLimit      = int(args.split(",")[5])
        scp.emergencyCredit = int(args.split(",")[6])
        scp.topUpLimit      = int(args.split(",")[7])
        scp.mmc             = int(args.split(",")[8])

        scp.fdPrice = map(int,(args.split("[")[1]).split("]")[0].split(","))
        scp.energyPrice = map(int,(args.split("[")[2]).split("]")[0].split(","))
        scp.energySlab = map(int,(args.split("[")[3]).split("]")[0].split(","))
        

        if len(scp.fdPrice) != 6:
            return "Error! 6 parameters need to be entered for fdPrice!"
        elif len(scp.energyPrice) != 6:
            return "Error! 6 parameters need to be entered for energyPrice!"
        elif len(scp.energySlab) != 5:
            return "Error! 5 parameters need to be entered for energySlab!"

        for index in range(len(scp.fdPrice)):
            if scp.fdPrice[index] < 0 or scp.fdPrice[index] > 10000000:
                return "Error! Slab prices should be in the range of 0 to 10000000 Paisa!"

        for index in range(len(scp.energyPrice)):
            if scp.energyPrice[index] < 0 or scp.energyPrice[index] > 60000:
                return "Error! Slab prices should be in the range of 0 to 60000!"
        if scp.mmc < 0 or scp.mmc > 600000:
            return "Error! MMC should be in the range of 0 to 600000!"


        for index in range(len(scp.energySlab)):
            if index > 0:
                if scp.energySlab[index] < 0 or scp.energySlab[index] > 60000:
                    return "Error! Slab limits should be in the range of 1 to 60000!"



        print("\n\n",scp,"\n\n")
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_TARIFF_PARAMS, scp, TARIFF_PACKET)
    @check_errors
    def set_dg_tariff_params(self, addr, args):
        scp = TariffPacket()
        scp.tariffType      = int(0)   
        scp.fdType          = int(args.split(",")[0])
        scp.fdTelescopicF   = int(args.split(",")[1])
        scp.mmcApplication  = int(args.split(",")[2])
         
        friendlyHoursPM     = int(args.split(",")[3])
        if friendlyHoursPM > 0 and (friendlyHoursPM == 24 or friendlyHoursPM < 13):
            return "friendly Start hours should between from 13:00 to 23:00"

        if friendlyHoursPM > 0:    
            friendlyHoursPM     = friendlyHoursPM - 12

        friendlyHoursAM     = int(args.split(",")[4])
        if friendlyHoursAM != 0 and friendlyHoursAM > 12:
            return "friendly End hours should between from 1:00 to 12:00"

        scp.friendlyHours   = int(friendlyHoursAM + friendlyHoursPM*16)

        scp.alertLimit      = int(args.split(",")[5])
        scp.emergencyCredit = int(args.split(",")[6])
        scp.topUpLimit      = int(args.split(",")[7])
        scp.mmc             = int(args.split(",")[8])

        scp.fdPrice = map(int,(args.split("[")[1]).split("]")[0].split(","))
        scp.energyPrice = map(int,(args.split("[")[2]).split("]")[0].split(","))
        scp.energySlab = map(int,(args.split("[")[3]).split("]")[0].split(","))
        
        if len(scp.fdPrice) != 6:
            return "Error! 6 parameters need to be entered for fdPrice!"
        elif len(scp.energyPrice) != 6:
            return "Error! 6 parameters need to be entered for energyPrice!"
        elif len(scp.energySlab) != 5:
            return "Error! 5 parameters need to be entered for energySlab!"

        for index in range(len(scp.fdPrice)):
            if scp.fdPrice[index] < 0 or scp.fdPrice[index] > 10000000:
                return "Error! Slab prices should be in the range of 0 to 10000000 Paisa!"

        for index in range(len(scp.energyPrice)):
            if scp.energyPrice[index] < 0 or scp.energyPrice[index] > 60000:
                return "Error! Slab prices should be in the range of 0 to 60000!"
        if scp.mmc < 0 or scp.mmc > 600000:
            return "Error! MMC should be in the range of 0 to 600000!"


        for index in range(len(scp.energySlab)):
            if index > 0:
                if scp.energySlab[index] < 0 or scp.energySlab[index] > 60000:
                    return "Error! Slab limits should be in the range of 1 to 60000!"



        print("\n\n",scp,"\n\n")
        return self.my_simpleterm_master.set_param(addr, commandMappingContainer.SET_TARIFF_PARAMS, scp, TARIFF_PACKET)


