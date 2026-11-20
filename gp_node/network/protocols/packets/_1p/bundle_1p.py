import datetime
import gp_node.utils.serialize as serialize
import time
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils.serialize import deserialize_uint32
from gp_node.utils.serialize import deserialize_uint24
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils import TamperFlag

class  DCUBundlePacket(object):

    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        dt = datetime.datetime(1970, 1, 1)
        self.return_params = {
                "date_time":dt
                ,"meter_type ":0
                ,"R_voltage":0.00
                ,"Y_voltage":0.00
                ,"B_voltage":0.00
                ,"R_phase_current":0.000
                ,"Y_phase_current":0.000
                ,"B_phase_current":0.000
                ,"neutral_current":0.00
                ,"R_avg_pf":0.00
                ,"Y_avg_pf":0.00
                ,"B_avg_pf":0.00
                ,"T_avg_pf":0.00
                ,"cumm_total_real_energy":0.000
                ,"cumm_total_apparent_energy":0.000
                ,"cumm_total_real_energy_export":0.000
                ,"cumm_total_apparent_energy_export":0.000
                ,"cumm_total_reactive_energy":0.00
                ,"total_real_power":0.000
                ,"total_apparent_power": 0.000
                ,"total_reactive_power":0.00
                ,"avg_frequency":0
                ,"credits_left":0.00
                ,"tamper_count":0
                ,"live_tamper_flags":[]
                ,"current_events":0.00
                ,"power_events":0.00
                ,"others_events":0.00
                ,"voltage_events":0
                ,"data_valid":"VALID"
                ,"kw_md_flag":0
                ,"kva_md_flag":0
                ,"relay_state":0
                ,"sw_off":0
                ,"current_tariff_grp":"DATA_NOT_AVAILABLE"
                ,"prepaid_status":"DATA_NOT_AVAILABLE"
                ,"account_status":"DATA_NOT_AVAILABLE"
                ,"total_net_recharge":0.0
                ,"current_net_recharge":0.0
                ,"DG_energy_consumed":0.0
                ,"EG_energy_consumed":0.0
                ,"DG_energy_amount_deducted":0.0
                ,"EG_energy_amount_deducted":0.0
                ,"current_running_price":0.0
                ,"cummulative_FDCost":0.0
                ,"Meter_Serial_Number":0
                ,"live_version":0
                ,"hw_version":"unknown"
                ,"billType":"kWh"}

    def deserialize_packet_bundle(self,payload):
        """
        Deserializes the input payload and populates the data to the default
        dictionary.This API needs to be used to retrieve information from the 
        reply bytestream.
        :param payload:input bytestream
        :return :none
        """
        bytes = bytearray()
        bytes = payload
        if len(payload)==88:
            return self.deserialize_packet_bundle_WP(payload)

        if len(payload)==84:
            return self.deserialize_packet_bundle_netmetering(payload)

        #self.return_params["meter_type"] = bytes[0]
        dt = datetime.datetime(1970, 1, 1) +\
                datetime.timedelta(seconds=serialize.deserialize_uint32(bytes[0:4]))
        self.return_params["date_time"] = dt
        self.return_params["Meter_Serial_Number"] = serialize.deserialize_uint24(bytes[4:7])
        version = serialize.deserialize_uint16(bytes[7:9])
        self.return_params["live_version"] = version % 10000

        version = version/10000
        if(version == 0):
            self.return_params["hw_version"] = "3PH-V-T1.0 PCB"
        elif (version == 1):
            self.return_params["hw_version"] = "3PH-V-T1.1 PCB"
        elif (version == 2):
            self.return_params["hw_version"] = "3PH-V-P1.0 PCB"
        elif (version == 3):
            self.return_params["hw_version"] = "3PH-I-P2.0 PCB"
        elif (version == 4):
            self.return_params["hw_version"] = "3PH-CAPITAL_POWER"
        else:
            self.return_params["hw_version"] = "unknown"

        self.return_params["R_voltage"] =  (serialize.deserialize_uint16(bytes[9:11]))/100.0
        self.return_params["Y_voltage"] =  (serialize.deserialize_uint16(bytes[11:13]))/100.0
        self.return_params["B_voltage"] =  (serialize.deserialize_uint16(bytes[13:15]))/100.0
        self.return_params["R_phase_current"] =  (serialize.deserialize_uint16(bytes[15:17]))/100.0
        self.return_params["Y_phase_current"] =  (serialize.deserialize_uint16(bytes[17:19]))/100.0
        self.return_params["B_phase_current"] =  (serialize.deserialize_uint16(bytes[19:21]))/100.0
        self.return_params["neutral_current"] =  (serialize.deserialize_uint16(bytes[21:23]))/100.0
        self.return_params["R_avg_pf"] = (serialize.deserialize_int16(bytes[23:25]))/1000.0
        self.return_params["Y_avg_pf"] = (serialize.deserialize_int16(bytes[25:27]))/1000.0 
        self.return_params["B_avg_pf"] = (serialize.deserialize_int16(bytes[27:29]))/1000.0 
        self.return_params["T_avg_pf"] = (serialize.deserialize_int16(bytes[29:31]))/1000.0 
        self.return_params["avg_frequency"] = (serialize.deserialize_uint16(bytes[31:33]))/100.0
        self.return_params["total_real_power"] = (serialize.deserialize_int16(bytes[33:35]))/100.0
        self.return_params["total_apparent_power"] =  (serialize.deserialize_uint16(bytes[35:37]))/100.0
        self.return_params["total_reactive_power"] =  (serialize.deserialize_int16(bytes[37:39]))/100.0
        self.return_params["cumm_total_real_energy"] = (serialize.deserialize_uint32(bytes[39:43]))/100.0
        self.return_params["cumm_total_apparent_energy"] = (serialize.deserialize_uint32(bytes[43:47]))/100.0
        self.return_params["cumm_total_reactive_energy"] = (serialize.deserialize_uint32(bytes[47:51]))/100.0
        self.return_params["credits_left"] =  (serialize.deserialize_int32(bytes[51:55]))/100.0
        self.return_params["tamper_count"] =  (serialize.deserialize_uint32(bytes[55:59]))

        bErrorT = {
                    0 : 'OverVoltage',  1 : 'Undervoltage',  2 : 'R-Ph Missing',  3 : 'Y-Ph Missing',
                    4 : 'B-Ph Missing', 5 : 'Voltage Unbal', 6 : 'Phase Sequence',7 : 'R-Ph Reverse',
                    8 : 'Y-Ph Reverse', 9 : 'B-Ph Reverse', 10 : 'Current Unbal',11 : 'CT Bypass',
                    12: 'R-Ph CT Open', 13: 'Y-Ph CT Open', 14 : 'B-Ph CT Open', 15 : 'Overcurrent',
                    16: 'Magnet',       17: 'ND',           18 : 'Low PF',       19 : 'Overload',
                    20 : 'C-Open'
                 }
        tamper_events = (serialize.deserialize_uint24(bytes[59:62]))
        health_mask = []
        for i in range(len(bErrorT)):
            if (tamper_events&(1<<i)):
                health_mask.append(bErrorT[i])

        self.return_params["live_tamper_flags"] =  health_mask

        occured_tampered_tamp = (serialize.deserialize_uint16(bytes[62:64]))
        
        current_releated = occured_tampered_tamp & 0xF000
        current_releated = (current_releated >> 12) 

        power_releated = occured_tampered_tamp & 0x0F00
        power_releated = (power_releated >> 8)

        others_related = occured_tampered_tamp & 0x00F0
        others_related = (others_related >> 4)

        voltage_related = occured_tampered_tamp & 0x000F

        self.return_params["others_events"] = others_related
        self.return_params["power_events"] = power_releated
        self.return_params["current_events"] = current_releated
        self.return_params["voltage_events"] = voltage_related

        soff_status = ["SWOFF_OVER_CURRENT","SWOFF_BY_REMOTE","SWOFF_ACCNT_EMPTY",
                       "SWOFF_HIGH_LOAD","SWOFF_BY_MANUAL"]

        temp = bytes[64] & 0x07
        if temp == 1:
            self.return_params["relay_state"] = "AUTO_CONTROL_ON"
        elif temp == 2:
            self.return_params["relay_state"] = "AUTO_CONTROL_OFF"
        elif temp == 3:
            self.return_params["relay_state"] = "MANUAL_CONTROL_ON"
        elif temp == 4:     
            self.return_params["relay_state"] = "MANUAL_CONTROL_OFF"

        relay_sw_off_reasons = bytes[64] & 0xF8
        relay_sw_off_reasons = relay_sw_off_reasons >> 3
        if relay_sw_off_reasons == 0:
            self.return_params["sw_off"]  = "NULL"
        else:    
            for i in range(len(soff_status)):
                if (relay_sw_off_reasons&(1<<i)):
                    self.return_params["sw_off"]  = soff_status[i]
                    break

        prepaid_flag = bytes[65]

        if (prepaid_flag & 0x80):
            self.return_params["current_tariff_grp"]   =  "EG Tariff Activated"   
        else:
            self.return_params["current_tariff_grp"]   =  "DG Tariff Activated"

        if (prepaid_flag & 0x40):
            self.return_params["prepaid_status"]       =  "Prepaid Activated"
        else:
            self.return_params["prepaid_status"]       =  "Prepaid Deactivated"

        if (prepaid_flag & 0x20):
            print ("Test Msg: Pwr_Cycle_was_occured..")

        prepaid_flag = (prepaid_flag & 0x07)

        account_status = ["ACC_NO_BALANCE","ACC_NO_BALANCE_FRIENDLY_HOURS","ACC_EMERGENCY_CREDIT",
                          "ACC_LOW_BALANCE","ACC_ENOUGH_BALANCE","ACC_PREPAID_DISABLED",
                          "ACC_DATA_NOT_AVAILABLE","ACC_NO_BALANCE_FRIENDLY_DAYS"]

        self.return_params["account_status"]            = account_status[prepaid_flag]
        self.return_params["total_net_recharge"]        =   serialize.deserialize_int32(bytes[66:70])/100.00
        self.return_params["current_net_recharge"]      =   serialize.deserialize_int32(bytes[70:74])/100.00    
        self.return_params["DG_energy_consumed"]        =   serialize.deserialize_uint32(bytes[74:78])/100.00
        self.return_params["EG_energy_consumed"]        =   serialize.deserialize_uint32(bytes[78:82])/100.00
        self.return_params["DG_energy_amount_deducted"] =   serialize.deserialize_uint32(bytes[82:86])/100.00        
        self.return_params["EG_energy_amount_deducted"] =   serialize.deserialize_uint32(bytes[86:90])/100.00        
        self.return_params["current_running_price"]     =   serialize.deserialize_uint16(bytes[90:92])/100.00
        self.return_params["cummulative_FDCost"]        =   serialize.deserialize_uint32(bytes[92:96])/100.00
        if len(payload) > 96 and payload[96]==0:
            self.return_params["billType"] = "kVAh"

    def deserialize_packet_bundle_WP(self,payload):
        """
        Deserializes the input payload and populates the data to the default
        dictionary.This API needs to be used to retrieve information from the 
        reply bytestream.
        :param payload:input bytestream
        :return :none
        """
        bytes = bytearray()
        bytes = payload
        

        #self.return_params["meter_type"] = bytes[0]
        # print "In wp deserialize"
        dt = datetime.datetime(1970, 1, 1) +\
                datetime.timedelta(seconds=serialize.deserialize_uint32(bytes[0:4]))
        self.return_params["date_time"] = dt
        self.return_params["Meter_Serial_Number"] = serialize.deserialize_uint24(bytes[4:7])
        version = serialize.deserialize_uint16(bytes[7:9])
        self.return_params["live_version"] = version % 10000

        version = version/10000
        if(version == 0):
            self.return_params["hw_version"] = "3PH-V-T1.0 PCB"
        elif (version == 1):
            self.return_params["hw_version"] = "3PH-V-T1.1 PCB"
        elif (version == 2):
            self.return_params["hw_version"] = "3PH-V-P1.0 PCB"
        elif (version == 3):
            self.return_params["hw_version"] = "3PH-I-P2.0 PCB"
        elif (version == 4):
            self.return_params["hw_version"] = "3PH-CAPITAL_POWER"
        else:
            self.return_params["hw_version"] = "unknown"

        self.return_params["R_voltage"] =  (serialize.deserialize_uint16(bytes[9:11]))/100.0
        self.return_params["Y_voltage"] =  (serialize.deserialize_uint16(bytes[11:13]))/100.0
        self.return_params["B_voltage"] =  (serialize.deserialize_uint16(bytes[13:15]))/100.0
        self.return_params["R_phase_current"] =  (serialize.deserialize_uint16(bytes[15:17]))/100.0
        self.return_params["Y_phase_current"] =  (serialize.deserialize_uint16(bytes[17:19]))/100.0
        self.return_params["B_phase_current"] =  (serialize.deserialize_uint16(bytes[19:21]))/100.0
        self.return_params["neutral_current"] =  (serialize.deserialize_uint16(bytes[21:23]))/100.0
        self.return_params["R_avg_pf"] = (serialize.deserialize_int16(bytes[23:25]))/1000.0
        self.return_params["Y_avg_pf"] = (serialize.deserialize_int16(bytes[25:27]))/1000.0 
        self.return_params["B_avg_pf"] = (serialize.deserialize_int16(bytes[27:29]))/1000.0 
        self.return_params["T_avg_pf"] = (serialize.deserialize_int16(bytes[29:31]))/1000.0 
        self.return_params["avg_frequency"] = (serialize.deserialize_uint16(bytes[31:33]))/100.0
        self.return_params["total_real_power"] = (serialize.deserialize_int16(bytes[33:35]))/100.0
        self.return_params["DG_energy_consumed"]        =   serialize.deserialize_uint32(bytes[35:39])/100.00
        
        self.return_params["cumm_total_real_energy"] = (serialize.deserialize_uint32(bytes[39:43]))/100.0
        self.return_params["cumm_total_apparent_energy"] = (serialize.deserialize_uint32(bytes[43:47]))/100.0
        self.return_params["cumm_total_reactive_energy"] = (serialize.deserialize_uint32(bytes[47:51]))/100.0
        self.return_params["credits_left"] =  (serialize.deserialize_int32(bytes[51:55]))/100.0
        self.return_params["tamper_count"] =  (serialize.deserialize_uint24(bytes[55:58]))

        bErrorT = {
                    0 : 'OverVoltage',  1 : 'Undervoltage',  2 : 'R-Ph Missing',  3 : 'Y-Ph Missing',
                    4 : 'B-Ph Missing', 5 : 'Voltage Unbal', 6 : 'Phase Sequence',7 : 'R-Ph Reverse',
                    8 : 'Y-Ph Reverse', 9 : 'B-Ph Reverse', 10 : 'Current Unbal',11 : 'CT Bypass',
                    12: 'R-Ph CT Open', 13: 'Y-Ph CT Open', 14 : 'B-Ph CT Open', 15 : 'Overcurrent',
                    16: 'Magnet',       17: 'ND',           18 : 'Low PF',       19 : 'Overload',
                    20 : 'C-Open'
                 }
        tamper_events = (serialize.deserialize_uint24(bytes[58:61]))
        health_mask = []
        for i in range(len(bErrorT)):
            if (tamper_events&(1<<i)):
                health_mask.append(bErrorT[i])

        self.return_params["live_tamper_flags"] =  health_mask
        self.return_params["total_reactive_power"] =  (serialize.deserialize_int16(bytes[62:64]))/100.0

        occured_tampered_tamp = bytes[61]
        
        power_releated = occured_tampered_tamp & 0x0F
        

        # power_releated = occured_tampered_tamp & 0x0F00
        # power_releated = (power_releated >> 8)

        # others_related = occured_tampered_tamp & 0x00F0
        # others_related = (others_related >> 4)

        # voltage_related = occured_tampered_tamp & 0x000F

        # self.return_params["others_events"] = others_related
        self.return_params["power_events"] = power_releated
        # self.return_params["current_events"] = current_releated
        # self.return_params["voltage_events"] = voltage_related
        prepaid_type = (occured_tampered_tamp & 0xF0)>>4
        print ("prepaid_type",prepaid_type)
        print ("power_releated",power_releated)
        if (prepaid_type == 0):
            self.return_params["billType"] = "kVAh"

        soff_status = ["SWOFF_OVER_CURRENT","SWOFF_BY_REMOTE","SWOFF_ACCNT_EMPTY",
                       "SWOFF_HIGH_LOAD","SWOFF_BY_MANUAL"]

        temp = bytes[64] & 0x07
        if temp == 1:
            self.return_params["relay_state"] = "AUTO_CONTROL_ON"
        elif temp == 2:
            self.return_params["relay_state"] = "AUTO_CONTROL_OFF"
        elif temp == 3:
            self.return_params["relay_state"] = "MANUAL_CONTROL_ON"
        elif temp == 4:     
            self.return_params["relay_state"] = "MANUAL_CONTROL_OFF"

        relay_sw_off_reasons = bytes[64] & 0xF8
        relay_sw_off_reasons = relay_sw_off_reasons >> 3
        if relay_sw_off_reasons == 0:
            self.return_params["sw_off"]  = "NULL"
        else:    
            for i in range(len(soff_status)):
                if (relay_sw_off_reasons&(1<<i)):
                    self.return_params["sw_off"]  = soff_status[i]
                    break

        prepaid_flag = bytes[65]

        if (prepaid_flag & 0x80):
            self.return_params["current_tariff_grp"]   =  "EG Tariff Activated"   
        else:
            self.return_params["current_tariff_grp"]   =  "DG Tariff Activated"

        if (prepaid_flag & 0x40):
            self.return_params["prepaid_status"]       =  "Prepaid Activated"
        else:
            self.return_params["prepaid_status"]       =  "Prepaid Deactivated"

        if (prepaid_flag & 0x20):
            print ("Test Msg: Pwr_Cycle_was_occured..")

        prepaid_flag = (prepaid_flag & 0x07)

        account_status = ["ACC_NO_BALANCE","ACC_NO_BALANCE_FRIENDLY_HOURS","ACC_EMERGENCY_CREDIT",
                          "ACC_LOW_BALANCE","ACC_ENOUGH_BALANCE","ACC_PREPAID_DISABLED",
                          "ACC_DATA_NOT_AVAILABLE","ACC_NO_BALANCE_FRIENDLY_DAYS"]
        self.return_params["account_status"] = account_status[prepaid_flag]

        self.return_params["total_net_recharge"]        =   serialize.deserialize_int32(bytes[66:70])/100.00
        self.return_params["current_net_recharge"]      =   serialize.deserialize_int32(bytes[70:74])/100.00    
        self.return_params["EG_energy_consumed"]        =   serialize.deserialize_uint32(bytes[74:78])/100.00
        self.return_params["DG_energy_amount_deducted"] =   serialize.deserialize_uint32(bytes[78:82])/100.00        
        self.return_params["EG_energy_amount_deducted"] =   serialize.deserialize_uint32(bytes[82:86])/100.00        
        self.return_params["current_running_price"]     =   serialize.deserialize_uint16(bytes[86:88])/100.00

    
    def deserialize_packet_bundle_netmetering(self,payload):
        """
        Deserializes the input payload and populates the data to the default
        dictionary.This API needs to be used to retrieve information from the 
        reply bytestream.
        :param payload:input bytestream
        :return :none
        """
        bytes = bytearray()
        bytes = payload
        

        #self.return_params["meter_type"] = bytes[0]
        print ("In net metering deserialize")
        dt = datetime.datetime(1970, 1, 1) +\
                datetime.timedelta(seconds=serialize.deserialize_uint32(bytes[0:4]))
        self.return_params["date_time"] = dt
        self.return_params["Meter_Serial_Number"] = serialize.deserialize_uint24(bytes[4:7])
        version = serialize.deserialize_uint16(bytes[7:9])
        self.return_params["live_version"] = version % 10000

        version = version/10000
        if(version == 0):
            self.return_params["hw_version"] = "3PH-V-T1.0 PCB"
        elif (version == 1):
            self.return_params["hw_version"] = "3PH-V-T1.1 PCB"
        elif (version == 2):
            self.return_params["hw_version"] = "3PH-V-P1.0 PCB"
        elif (version == 3):
            self.return_params["hw_version"] = "3PH-I-P2.0 PCB"
        elif (version == 4):
            self.return_params["hw_version"] = "3PH-CAPITAL_POWER"
        else:
            self.return_params["hw_version"] = "unknown"

        self.return_params["R_voltage"] =  (serialize.deserialize_uint16(bytes[9:11]))/100.0
        self.return_params["Y_voltage"] =  (serialize.deserialize_uint16(bytes[11:13]))/100.0
        self.return_params["B_voltage"] =  (serialize.deserialize_uint16(bytes[13:15]))/100.0
        self.return_params["R_phase_current"] =  (serialize.deserialize_uint16(bytes[15:17]))/100.0
        self.return_params["Y_phase_current"] =  (serialize.deserialize_uint16(bytes[17:19]))/100.0
        self.return_params["B_phase_current"] =  (serialize.deserialize_uint16(bytes[19:21]))/100.0
        self.return_params["neutral_current"] =  (serialize.deserialize_uint16(bytes[21:23]))/100.0
        self.return_params["R_avg_pf"] = (serialize.deserialize_int16(bytes[23:25]))/1000.0
        self.return_params["Y_avg_pf"] = (serialize.deserialize_int16(bytes[25:27]))/1000.0 
        self.return_params["B_avg_pf"] = (serialize.deserialize_int16(bytes[27:29]))/1000.0 
        self.return_params["T_avg_pf"] = (serialize.deserialize_int16(bytes[29:31]))/1000.0 
        self.return_params["avg_frequency"] = (serialize.deserialize_uint16(bytes[31:33]))/100.0
        self.return_params["total_real_power"] = (serialize.deserialize_int16(bytes[33:35]))/100.0
        self.return_params["DG_energy_consumed"]        =   serialize.deserialize_uint32(bytes[35:39])/100.00
        
        self.return_params["cumm_total_real_energy"] = (serialize.deserialize_uint32(bytes[39:43]))/100.0
        self.return_params["cumm_total_apparent_energy"] = (serialize.deserialize_uint32(bytes[43:47]))/100.0
        self.return_params["cumm_total_real_energy_export"] = (serialize.deserialize_uint32(bytes[47:51]))/100.0
        self.return_params["credits_left"] =  (serialize.deserialize_int32(bytes[51:55]))/100.0
        self.return_params["tamper_count"] =  (serialize.deserialize_uint24(bytes[55:58]))

        bErrorT = {
                    0 : 'OverVoltage',  1 : 'Undervoltage',  2 : 'R-Ph Missing',  3 : 'Y-Ph Missing',
                    4 : 'B-Ph Missing', 5 : 'Voltage Unbal', 6 : 'Phase Sequence',7 : 'R-Ph Reverse',
                    8 : 'Y-Ph Reverse', 9 : 'B-Ph Reverse', 10 : 'Current Unbal',11 : 'CT Bypass',
                    12: 'R-Ph CT Open', 13: 'Y-Ph CT Open', 14 : 'B-Ph CT Open', 15 : 'Overcurrent',
                    16: 'Magnet',       17: 'ND',           18 : 'Low PF',       19 : 'Overload',
                    20 : 'C-Open'
                 }
        tamper_events = (serialize.deserialize_uint24(bytes[58:61]))
        health_mask = []
        for i in range(len(bErrorT)):
            if (tamper_events&(1<<i)):
                health_mask.append(bErrorT[i])

        self.return_params["live_tamper_flags"] =  health_mask
        self.return_params["total_reactive_power"] =  (serialize.deserialize_int16(bytes[62:64]))/100.0

        occured_tampered_tamp = bytes[61]
        
        power_releated = occured_tampered_tamp & 0x0F
        

        # power_releated = occured_tampered_tamp & 0x0F00
        # power_releated = (power_releated >> 8)

        # others_related = occured_tampered_tamp & 0x00F0
        # others_related = (others_related >> 4)

        # voltage_related = occured_tampered_tamp & 0x000F

        # self.return_params["others_events"] = others_related
        self.return_params["power_events"] = power_releated
        # self.return_params["current_events"] = current_releated
        # self.return_params["voltage_events"] = voltage_related
        prepaid_type = (occured_tampered_tamp & 0xF0)>>4
        print ("prepaid_type",prepaid_type)
        print ("power_releated",power_releated)
        if (prepaid_type == 0):
            self.return_params["billType"] = "kVAh"

        soff_status = ["SWOFF_OVER_CURRENT","SWOFF_BY_REMOTE","SWOFF_ACCNT_EMPTY",
                       "SWOFF_HIGH_LOAD","SWOFF_BY_MANUAL"]

        temp = bytes[64] & 0x07
        if temp == 1:
            self.return_params["relay_state"] = "AUTO_CONTROL_ON"
        elif temp == 2:
            self.return_params["relay_state"] = "AUTO_CONTROL_OFF"
        elif temp == 3:
            self.return_params["relay_state"] = "MANUAL_CONTROL_ON"
        elif temp == 4:     
            self.return_params["relay_state"] = "MANUAL_CONTROL_OFF"

        relay_sw_off_reasons = bytes[64] & 0xF8
        relay_sw_off_reasons = relay_sw_off_reasons >> 3
        if relay_sw_off_reasons == 0:
            self.return_params["sw_off"]  = "NULL"
        else:    
            for i in range(len(soff_status)):
                if (relay_sw_off_reasons&(1<<i)):
                    self.return_params["sw_off"]  = soff_status[i]
                    break

        prepaid_flag = bytes[65]

        if (prepaid_flag & 0x80):
            self.return_params["current_tariff_grp"]   =  "EG Tariff Activated"   
        else:
            self.return_params["current_tariff_grp"]   =  "DG Tariff Activated"

        if (prepaid_flag & 0x40):
            self.return_params["prepaid_status"]       =  "Prepaid Activated"
        else:
            self.return_params["prepaid_status"]       =  "Prepaid Deactivated"

        if (prepaid_flag & 0x20):
            print ("Test Msg: Pwr_Cycle_was_occured..")

        prepaid_flag = (prepaid_flag & 0x07)

        account_status = ["ACC_NO_BALANCE","ACC_NO_BALANCE_FRIENDLY_HOURS","ACC_EMERGENCY_CREDIT",
                          "ACC_LOW_BALANCE","ACC_ENOUGH_BALANCE","ACC_PREPAID_DISABLED",
                          "ACC_DATA_NOT_AVAILABLE","ACC_NO_BALANCE_FRIENDLY_DAYS"]
        self.return_params["account_status"] = account_status[prepaid_flag]

        self.return_params["cumm_total_apparent_energy_export"]    =   serialize.deserialize_uint32(bytes[66:70])/100.00
        self.return_params["EG_energy_consumed"]      =   serialize.deserialize_int32(bytes[70:74])/100.00    
        self.return_params["DG_energy_amount_deducted"]        =   serialize.deserialize_uint32(bytes[74:78])/100.00
        self.return_params["EG_energy_amount_deducted"] =   serialize.deserialize_uint32(bytes[78:82])/100.00        
        self.return_params["current_running_price"] =   serialize.deserialize_uint16(bytes[82:84])/100.00        
        # self.return_params["current_running_price"]     =   serialize.deserialize_uint16(bytes[86:88])/100.00    
    
                    
    
    def get_packet_bundle(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("Date & time                   : {}\n"
                "Meter Serial Number           : {}\n"
                "Prepaid Bill Type             : {}\n"
                "Firmware version              : {}\n"
                "Hardware version              : {}\n"
                "R-Ph Avg Voltage              : {} V\n"
                "Y-Ph Avg Voltage              : {} V\n"
                "B-Ph Avg Voltage              : {} V\n"
                "R-Ph Avg Current              : {} A\n"
                "Y-Ph Avg Current              : {} A\n"
                "B-Ph Avg Current              : {} A\n"
                "Neutral Avg current           : {} A\n"
                "R-Ph Avg PF                   : {}\n"
                "Y-Ph Avg PF                   : {}\n"
                "B-Ph Avg PF                   : {}\n"
                "Total Avg PF                  : {}\n"
                "Frequency                     : {} Hz\n"
                "Active Power                  : {} kW\n"
                "Apparent Power                : {} kVA\n"   
                "Reactive Power                : {} kVAr\n"
                "Cumm Active Energy            : {} kWh\n"
                "Cumm Apparent Energy          : {} kVAh\n"
                "Cumm Reactive Energy          : {} kVArh\n"
                "Active Energy Export          : {} kWh\n"
                "Apparent Energy Export        : {} kVAh\n"
                "Tampers Count                 : {}\n"
                "Live Tampers                  : {}\n"
                "No Of Current Related Events  : {}\n"
                "No Of Power Related Events    : {}\n"
                "No Of Others Related Events   : {}\n"
                "No Of Voltage Related Events  : {}\n"
                "Relay State                   : {}\n"
                "Switch Off Reason             : {}\n"
                "Activated Tariff Group        : {}\n"
                "Prepaid Status                : {}\n"
                "Account Status                : {}\n"
                "Credits Left                  : {} Rs\n"
                "Total Net Recharge            : {} Rs\n"
                "Current Net Recharge          : {} Rs\n"
                "DG Energy Consumed            : {} {}\n"
                "EG Energy Consumed            : {} {}\n"                     
                "DG Energy Deducted Amount     : {} Rs\n"                     
                "EG Energy Deducted Amount     : {} Rs\n"                     
                "Current Running Price         : {} Rs\n"
                "Cummulative Total FD Cost     : {} Rs")\
                .format(self.return_params["date_time"],
                        self.return_params["Meter_Serial_Number"],
                        self.return_params["billType"],
                        self.return_params["live_version"],
                        self.return_params["hw_version"],
                        self.return_params["R_voltage"],
                        self.return_params["Y_voltage"],
                        self.return_params["B_voltage"],
                        self.return_params["R_phase_current"],
                        self.return_params["Y_phase_current"],
                        self.return_params["B_phase_current"],
                        self.return_params["neutral_current"],
                        self.return_params["R_avg_pf"],
                        self.return_params["Y_avg_pf"],
                        self.return_params["B_avg_pf"],
                        self.return_params["T_avg_pf"],
                        self.return_params["avg_frequency"],
                        self.return_params["total_real_power"],
                        self.return_params["total_apparent_power"],
                        self.return_params["total_reactive_power"],
                        self.return_params["cumm_total_real_energy"],
                        self.return_params["cumm_total_apparent_energy"],
                        self.return_params["cumm_total_reactive_energy"], 
                        self.return_params["cumm_total_real_energy_export"],
                        self.return_params["cumm_total_apparent_energy_export"],
                        self.return_params["tamper_count"],
                        self.return_params["live_tamper_flags"],
                        self.return_params["current_events"],
                        self.return_params["power_events"],
                        self.return_params["others_events"],
                        self.return_params["voltage_events"],
                        self.return_params["relay_state"],
                        self.return_params["sw_off"],
                        self.return_params["current_tariff_grp"],
                        self.return_params["prepaid_status"],
                        self.return_params["account_status"],
                        self.return_params["credits_left"],
                        self.return_params["total_net_recharge"],
                        self.return_params["current_net_recharge"],
                        self.return_params["DG_energy_consumed"],self.return_params["billType"],
                        self.return_params["EG_energy_consumed"],self.return_params["billType"],
                        self.return_params["DG_energy_amount_deducted"],
                        self.return_params["EG_energy_amount_deducted"],
                        self.return_params["current_running_price"],
                        self.return_params["cummulative_FDCost"])

if __name__ == "__main__":
    hexfile = {'0': 0,
               '1': 1,
               '2': 2,
               '3': 3,
               '4': 4,
               '5': 5,
               '6': 6,
               '7': 7,
               '8': 8,
               '9': 9,
               'a': 10,
               'b': 11,
               'c': 12,
               'd': 13,
               'e': 14,
               'f': 15
               }
    data = bytearray()
    b="6400000000000000000000000000000000006301000018180000020000e80300000000000000000000000000000000000000008813e80300000000e803000000000000000000000000ef5ce9824d9d047f5fd664"
    pLen = len(b)
    print (pLen)

    index = 0
    while (index < pLen):
        num = 0
        msb = hexfile[b[index]]
        index += 1
        lsb = hexfile[b[index]]
        index += 1

        num = (msb * 10) + lsb
        data.append(num)

    bdl = DCUBundlePacket()
    try:
        bdl.deserialize_packet_bundle(data)                    
    except Exception as err:
        print ("Error", str(err))
    print (bdl.get_packet_bundle())

                        

