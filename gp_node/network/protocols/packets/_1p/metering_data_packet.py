import datetime
import time
import gp_node.utils.serialize as serialize


class MeteringDataPacket(object):

    def __init__(self):
        self.return_params = {  "meter_serial_number"   : 0,
                                "realDatetime"          : datetime.datetime(1970, 1, 1, 0, 0, 0),
                                "R_voltage"             : 0.0,
                                "Y_voltage"             : 0.0,
                                "B_voltage"             : 0.0,
                                "R_phase_current"       : 0.0,
                                "Y_phase_current"       : 0.0,
                                "B_phase_current"       : 0.0,
                                "neutral_current"       : 0.0,
                                "calcNeutral_current"   : 0.0,
                                "R_phase_angle"         : 0.0,
                                "Y_phase_angle"         : 0.0,
                                "B_phase_angle"         : 0.0,
                                "active_power"          : 0.0,
                                "R_active_power"        : 0.0,
                                "Y_active_power"        : 0.0,
                                "B_active_power"        : 0.0,
                                "apparent_power"        : 0.0,
                                "reactive_power"        : 0.0,
                                "R_reactive_power"      : 0.0,
                                "Y_reactive_power"      : 0.0,
                                "B_reactive_power"      : 0.0,
                                "frequency"             : 0.0,
                                "R_power_factor"        : 0.0,
                                "Y_power_factor"        : 0.0,
                                "B_power_factor"        : 0.0,
                                "T_power_factor"        : 0.0,
                                "active_energy_imp"     : 0.0,
                                "active_energy_exp"     : 0.0,
                                "apparent_energy_imp"   : 0.0,
                                "apparent_energy_exp"   : 0.0,
                                "reactive_energy_q1"    : 0.0,
                                "reactive_energy_q2"    : 0.0,
                                "reactive_energy_q3"    : 0.0,
                                "reactive_energy_q4"    : 0.0,
                                "thd_R_voltage"         : 0.0,
                                "thd_Y_voltage"         : 0.0,
                                "thd_B_voltage"         : 0.0,
                                "thd_R_current"         : 0.0,
                                "thd_Y_current"         : 0.0,
                                "thd_B_current"         : 0.0,
                                "tamper_event"          : [],
                                "ACTI_ENERGY_HR"        : 0.0,   
                                "ACTE_ENERGY_HR"        : 0.0,   
                                "REACTIACTI_ENERGY_HR"  : 0.0,   
                                "REACTIACTE_ENERGY_HR"  : 0.0,   
                                "REACTEACTE_ENERGY_HR"  : 0.0,   
                                "REACTEACTI_ENERGY_HR"  : 0.0,   
                                "APPI_ENERGY_HR"        : 0.0,
                                "APPE_ENERGY_HR"        : 0.0
                                }

    def __str__(self):
        return ("Meter Serial Number        : {}        \n"
                "Meter Date Time            : {}        \n"
                "Frequency                  : {} Hz     \n"
                "R-Voltage                  : {} V      \n"
                "Y-Voltage                  : {} V      \n"
                "B-Voltage                  : {} V      \n"
                "R-Current                  : {} A      \n"
                "Y-Current                  : {} A      \n"
                "B-Current                  : {} A      \n"
                "Neutral Current            : {} A      \n"
                "Active Power               : {} KW     \n"
                "Apparent Power             : {} KVA    \n"
                "Reactive Power             : {} KVAr   \n"
                "R-PowerFactor              : {}        \n"
                "Y-PowerFactor              : {}        \n"
                "B-PowerFactor              : {}        \n"
                "Avg PowerFactor            : {}        \n"
                "Active Energy Import       : {} KWh    \n"
                "Active Energy Export       : {} KWh    \n"
                "Apparent Energy Import     : {} KVAh   \n"
                "Apparent Energy Export     : {} KVAh   \n"
                "Reactive Energy QI         : {} KVArh  \n"
                "Reactive Energy QII        : {} KVArh  \n"
                "Reactive Energy QIII       : {} KVArh  \n"
                "Reactive Energy QIV        : {} KVArh  \n"
                "No of Power fail count     : {}\n"
                "power_failure_duration     : {}\n"
                "tamper_count               : {}\n"
                "billing_count              : {}\n"
                "programming_count          : {}\n"
                "billing_date               : {}\n"
                "MD_active_power_import     : {} W\n"
                "MD_apparent_power_import   : {} VA\n"
                
                "Live Tampers               : {}        \n"
                )\
                .format(    self.return_params["meter_serial_number"],
                            self.return_params["realDatetime"],
                            self.return_params["frequency"],
                            self.return_params["R_voltage"],
                            self.return_params["Y_voltage"],
                            self.return_params["B_voltage"],
                            self.return_params["R_phase_current"],
                            self.return_params["Y_phase_current"],
                            self.return_params["B_phase_current"],
                            self.return_params["neutral_current"],
                            self.return_params["active_power"],
                            self.return_params["apparent_power"],
                            self.return_params["reactive_power"],
                            self.return_params["R_power_factor"],
                            self.return_params["Y_power_factor"],
                            self.return_params["B_power_factor"],
                            self.return_params["T_power_factor"],
                            self.return_params["active_energy_imp"],
                            self.return_params["active_energy_exp"],
                            self.return_params["apparent_energy_imp"],
                            self.return_params["apparent_energy_exp"],
                            self.return_params["reactive_energy_q1"],
                            self.return_params["reactive_energy_q2"],
                            self.return_params["reactive_energy_q3"],
                            self.return_params["reactive_energy_q4"],
                            self.return_params["power_failure_count"],
                            self.return_params["power_failure_duration"],
                            self.return_params["tamper_count"],
                            self.return_params["billing_count"],
                            self.return_params["programming_count"],
                            self.return_params["billing_date"],
                            self.return_params["MD_apparent_power_import"],
                            self.return_params["MD_active_power_import"],
                            self.return_params["tamper_event"])

    def serialize(self):
        # TODO: Implement this
        raise Exception("Not implemented.")

    def deserialize(self, payload):
        """
        It is assumed that payload size is 29
        """
        if len(payload) < 88:
            return self.deserialize_wp(payload)

        liveTamper = [  "OVERVOLTAGE",
                        "LOWVOLTAGE",
                        "R_PHASE_MISSING",
                        "Y_PHASE_MISSING",
                        "B_PHASE_MISSING",
                        "VOLTAGE_UNBALANCE",
                        "VOLTAGE_PHASE_REVERSE",
                        "R_CUR_REVERSE",
                        "Y_CUR_REVERSE",
                        "B_CUR_REVERSE",
                        "CURRENT_UNBALANCE",
                        "CT_BYPASS",
                        "R_CTOPEN",
                        "Y_CTOPEN",
                        "B_CTOPEN",
                        "OVERCURRENT",
                        "HIGH_NEUTRAL_CUR",
                        "MAGNET",
                        "NDIST",
                        "LOWPF",
                        "COPEN",
                        "OVERLOAD",                       
                        "LOW_BALANCE",
                        "PLUG_IN_OUT",
                        "FREQ_MALFUN",
                        "SWITCH_WELD",
                        "N_CUR_REVERSE"]

        buf = bytearray()
        buf = payload

        self.return_params["meter_serial_number"]    = serialize.deserialize_uint32(buf[0:4])
        self.return_params["realDatetime"]           = datetime.datetime(1970, 1, 1) +\
                                                       datetime.timedelta(seconds=serialize.deserialize_uint32(buf[4:8]))
        self.return_params["frequency"]              = serialize.deserialize_uint32(buf[8:12])/1000.0
        self.return_params["R_voltage"]              = serialize.deserialize_uint32(buf[12:16])/1000.0
        self.return_params["Y_voltage"]              = serialize.deserialize_uint32(buf[16:20])/1000.0
        self.return_params["B_voltage"]              = serialize.deserialize_uint32(buf[20:24])/1000.0
        self.return_params["R_phase_current"]        = serialize.deserialize_int32(buf[24:28])/1000.0
        self.return_params["Y_phase_current"]        = serialize.deserialize_int32(buf[28:32])/1000.0
        self.return_params["B_phase_current"]        = serialize.deserialize_int32(buf[32:36])/1000.0
        self.return_params["neutral_current"]        = serialize.deserialize_uint32(buf[36:40])/1000.0
        self.return_params["R_power_factor"]         = serialize.deserialize_int32(buf[40:44])/1000.0
        self.return_params["Y_power_factor"]         = serialize.deserialize_int32(buf[44:48])/1000.0
        self.return_params["B_power_factor"]         = serialize.deserialize_int32(buf[48:52])/1000.0
        self.return_params["T_power_factor"]         = serialize.deserialize_int32(buf[52:56])/1000.0
        self.return_params["active_power"]           = serialize.deserialize_int32(buf[56:60])/1000000.0
        self.return_params["reactive_power"]         = serialize.deserialize_int32(buf[60:64])/1000000.0
        self.return_params["apparent_power"]         = serialize.deserialize_uint32(buf[64:68])/1000000.0
        self.return_params["active_energy_imp"]      = serialize.deserialize_uint32(buf[68:72])/100.0
        self.return_params["active_energy_exp"]      = serialize.deserialize_uint32(buf[72:76])/100.0
        self.return_params["reactive_energy_q1"]     = serialize.deserialize_uint32(buf[76:80])/100.0
        self.return_params["reactive_energy_q2"]     = serialize.deserialize_uint32(buf[80:84])/100.0
        self.return_params["reactive_energy_q3"]     = serialize.deserialize_uint32(buf[84:88])/100.0
        self.return_params["reactive_energy_q4"]     = serialize.deserialize_uint32(buf[88:92])/100.0
        self.return_params["apparent_energy_imp"]    = serialize.deserialize_uint32(buf[92:96])/100.0
        self.return_params["apparent_energy_exp"]    = serialize.deserialize_uint32(buf[96:100])/100.0   
        self.return_params["power_failure_count"]    = serialize.deserialize_uint32(buf[100:104])
        self.return_params["power_failure_duration"]  = serialize.deserialize_uint32(buf[104:108])
        self.return_params["tamper_count"]            = serialize.deserialize_uint32(buf[108:112])
        self.return_params["billing_count"]           = serialize.deserialize_uint32(buf[112:116])
        self.return_params["programming_count"]       = serialize.deserialize_uint32(buf[116:120])
        self.return_params["billing_date"]            = datetime.datetime(1970, 1, 1) +\
                                                       datetime.timedelta(seconds=serialize.deserialize_uint32(buf[120:124]))
        self.return_params["MD_active_power_import"]  = serialize.deserialize_uint32(buf[124:128])/1000.0
        self.return_params["MD_apparent_power_import"]= serialize.deserialize_uint32(buf[128:132])/1000.0
        
        temp = serialize.deserialize_uint32(buf[132:136])
        live = []
        if(temp == 0):
            live.append("None")
        else:
            for i in range(len(liveTamper)):
                if (0 != temp&(1<<i)):
                    live.append(liveTamper[i])

        self.return_params["tamper_event"]           = live

    def deserialize_wp(self, payload):
        """
        It is assumed that payload size is 29
        """

        liveTamper = [  "OVERVOLTAGE",
                        "LOWVOLTAGE",
                        "R_PHASE_MISSING",
                        "Y_PHASE_MISSING",
                        "B_PHASE_MISSING",
                        "VOLTAGE_UNBALANCE",
                        "VOLTAGE_PHASE_REVERSE",
                        "R_CUR_REVERSE",
                        "Y_CUR_REVERSE",
                        "B_CUR_REVERSE",
                        "CURRENT_UNBALANCE",
                        "CT_BYPASS",
                        "R_CTOPEN",
                        "Y_CTOPEN",
                        "B_CTOPEN",
                        "OVERCURRENT",
                        "MAGNET",
                        "NDIST",
                        "LOWPF",
                        "OVERLOAD",
                        "COPEN"]

        buf = bytearray()
        buf = payload

        self.return_params["meter_serial_number"]    = serialize.deserialize_uint32(buf[0:4])
        self.return_params["realDatetime"]           = datetime.datetime(1970, 1, 1) +\
                                                       datetime.timedelta(seconds=serialize.deserialize_uint32(buf[4:8]))
        self.return_params["frequency"]              = serialize.deserialize_uint16(buf[8:10])/1000.0
        self.return_params["R_voltage"]              = serialize.deserialize_uint24(buf[10:13])/1000.0
        self.return_params["Y_voltage"]              = serialize.deserialize_uint24(buf[13:16])/1000.0
        self.return_params["B_voltage"]              = serialize.deserialize_uint24(buf[16:19])/1000.0
        self.return_params["R_phase_current"]        = serialize.deserialize_uint24(buf[19:22])/1000.0
        self.return_params["Y_phase_current"]        = serialize.deserialize_uint24(buf[22:25])/1000.0
        self.return_params["B_phase_current"]        = serialize.deserialize_uint24(buf[25:28])/1000.0
        self.return_params["neutral_current"]        = serialize.deserialize_uint24(buf[28:31])/1000.0
        self.return_params["R_power_factor"]         = serialize.deserialize_int16(buf[31:33])/1000.0
        self.return_params["Y_power_factor"]         = serialize.deserialize_int16(buf[33:35])/1000.0
        self.return_params["B_power_factor"]         = serialize.deserialize_int16(buf[35:37])/1000.0
        self.return_params["T_power_factor"]         = serialize.deserialize_int16(buf[37:39])/1000.0
        self.return_params["active_power"]           = serialize.deserialize_int32(buf[39:43])/1000000.0
        self.return_params["reactive_power"]         = serialize.deserialize_int32(buf[43:47])/1000000.0
        self.return_params["apparent_power"]         = serialize.deserialize_uint32(buf[47:51])/1000000.0
        self.return_params["active_energy_imp"]      = serialize.deserialize_uint32(buf[51:55])/100.0
        self.return_params["active_energy_exp"]      = serialize.deserialize_uint32(buf[55:59])/100.0
        self.return_params["reactive_energy_q1"]     = serialize.deserialize_uint32(buf[59:63])/100.0
        self.return_params["reactive_energy_q2"]     = serialize.deserialize_uint32(buf[63:67])/100.0
        self.return_params["reactive_energy_q3"]     = serialize.deserialize_uint32(buf[67:71])/100.0
        self.return_params["reactive_energy_q4"]     = serialize.deserialize_uint32(buf[71:75])/100.0
        self.return_params["apparent_energy_imp"]    = serialize.deserialize_uint32(buf[75:79])/100.0
        self.return_params["apparent_energy_exp"]    = serialize.deserialize_uint32(buf[79:83])/100.0
        
        temp = serialize.deserialize_uint32(buf[83:87])
        live = []
        if(temp == 0):
            live.append("None")
        else:
            for i in range(len(liveTamper)):
                if (0 != temp&(1<<i)):
                    live.append(liveTamper[i])

        self.return_params["tamper_event"]           = live    

    def deserializePacket2(self,payload):
        buf = bytearray()
        # print ">>>>>>>>>>>>>>>>>>>>>>>."
        buf = payload
        nCur = serialize.deserialize_uint32(buf[0:4])/1000.0
        if nCur < 0:
            nCur = -nCur
        self.return_params["calcNeutral_current"] = nCur
        self.return_params["R_phase_angle"]   = serialize.deserialize_int16(buf[4:6])/100.0
        self.return_params["Y_phase_angle"]   = serialize.deserialize_int16(buf[6:8])/100.0
        self.return_params["B_phase_angle"]   = serialize.deserialize_int16(buf[8:10])/100.0
        self.return_params["R_active_power"]   = serialize.deserialize_int32(buf[10:14])/1000.0
        self.return_params["Y_active_power"]   = serialize.deserialize_int32(buf[14:18])/1000.0
        self.return_params["B_active_power"]   = serialize.deserialize_int32(buf[18:22])/1000.0
        self.return_params["active_power"]   = serialize.deserialize_int32(buf[22:26])/1000.0
        self.return_params["R_reactive_power"]   = serialize.deserialize_int32(buf[26:30])/1000.0
        self.return_params["Y_reactive_power"]   = serialize.deserialize_int32(buf[30:34])/1000.0
        self.return_params["B_reactive_power"]   = serialize.deserialize_int32(buf[34:38])/1000.0
        self.return_params["reactive_power"]   = serialize.deserialize_int32(buf[38:42])/1000.0
        if len(buf) > 42:
            self.return_params["thd_R_voltage"]   = serialize.deserialize_int16(buf[42:44])/100.0
            self.return_params["thd_Y_voltage"]   = serialize.deserialize_int16(buf[44:46])/100.0
            self.return_params["thd_B_voltage"]   = serialize.deserialize_int16(buf[46:48])/100.0
            self.return_params["thd_R_current"]   = serialize.deserialize_int16(buf[48:50])/100.0
            self.return_params["thd_Y_current"]   = serialize.deserialize_int16(buf[50:52])/100.0
            self.return_params["thd_B_current"]   = serialize.deserialize_int16(buf[52:54])/100.0
            self.return_params["reactive_HR_energy_q1"]     = serialize.deserialize_uint32(buf[54:58])/1000000.0
            self.return_params["reactive_HR_energy_q2"]     = serialize.deserialize_uint32(buf[58:62])/1000000.0
            self.return_params["reactive_HR_energy_q3"]     = serialize.deserialize_uint32(buf[62:66])/1000000.0
            self.return_params["reactive_HR_energy_q4"]     = serialize.deserialize_uint32(buf[66:70])/1000000.0
            self.return_params["Temperature"] = serialize.deserialize_uint32(buf[70:74])/1000.0
            self.return_params["Angle_V1_V2"]   = serialize.deserialize_uint16(buf[74:76])
            self.return_params["Angle_V1_V3"]   = serialize.deserialize_uint16(buf[76:78])
            self.return_params["Angle_I1_I2"]   = serialize.deserialize_uint16(buf[78:80])
            self.return_params["Angle_I1_I3"]   = serialize.deserialize_uint16(buf[80:82])
            self.return_params["Defraud_Energy"] = serialize.deserialize_uint32(buf[82:86])/100.0



    def getMeterpacket2(self):
        return ("Calc Neutral Current               : {} A\n"
                "R Phase Angle                      : {} degree\n"
                "Y Phase Angle                      : {} degree\n"
                "B Phase Angle                      : {} degree\n"
                "R Active Power                     : {} W\n"
                "Y Active Power                     : {} W\n"
                "B Active Power                     : {} W\n"
                "Active Power                       : {} W\n"
                "R Reactive Power                   : {} VAr\n"
                "Y Reactive Power                   : {} VAr\n"
                "B Reactive Power                   : {} VAr\n"
                "Reactive Power                     : {} VAr\n"
                "THD R_Voltage                      : {} %\n"
                "THD Y_Voltage                      : {} %\n"
                "THD B_Voltage                      : {} %\n"
                "THD R_Current                      : {} %\n"
                "THD Y_Current                      : {} %\n"
                "THD B_Current                      : {} %\n"
                "Reactive HR Energy QI              : {} KVArh  \n"
                "Reactive HR Energy QII             : {} KVArh  \n"
                "Reactive HR Energy QIII            : {} KVArh  \n"
                "Reactive HR Energy QIV             : {} KVArh  \n"
                "Temperature                        : {} Celsius \n"
                "V1 and V2 Angle                    : {} degree\n"
                "V1 and V3 Angle                    : {} degree\n"
                "I1 and I2 Angle                    : {} degree\n"
                "I1 and I3 Angle                    : {} degree\n"
                "Defraud Energy                     : {} Kwh  \n"
                ).format(self.return_params["calcNeutral_current"],
                        self.return_params["R_phase_angle"],
                        self.return_params["Y_phase_angle"],
                        self.return_params["B_phase_angle"],
                        self.return_params["R_active_power"],
                        self.return_params["Y_active_power"],
                        self.return_params["B_active_power"],
                        self.return_params["active_power"],
                        self.return_params["R_reactive_power"],
                        self.return_params["Y_reactive_power"],
                        self.return_params["B_reactive_power"],
                        self.return_params["reactive_power"],
                        self.return_params["thd_R_voltage"],
                        self.return_params["thd_Y_voltage"],
                        self.return_params["thd_B_voltage"],
                        self.return_params["thd_R_current"],
                        self.return_params["thd_Y_current"],
                        self.return_params["thd_B_current"],
                        self.return_params["reactive_HR_energy_q1"],
                        self.return_params["reactive_HR_energy_q2"],
                        self.return_params["reactive_HR_energy_q3"],
                        self.return_params["reactive_HR_energy_q4"],
                        self.return_params["Temperature"],
                        self.return_params["Angle_V1_V2"],
                        self.return_params["Angle_V1_V3"],
                        self.return_params["Angle_I1_I2"],
                        self.return_params["Angle_I1_I3"],
                        self.return_params["Defraud_Energy"],
                        )


    def deserializePacket4(self,payload):
        buf = bytearray()
        # print ">>>>>>>>>>>>>>>>>>>>>>>."
        buf = payload
        unix_str_time = serialize.deserialize_uint32(buf[0:4], "reverse")
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.return_params["realDatetime"]      = unix_time_zero + datetime.timedelta(0, unix_time)
        self.return_params["R_current"]         = serialize.deserialize_uint32(buf[4:8], "reverse")/1000.0
        self.return_params["Y_current"]         = serialize.deserialize_uint32(buf[8:12], "reverse")/1000.0
        self.return_params["B_current"]         = serialize.deserialize_uint32(buf[12:16], "reverse")/1000.0
        self.return_params["R_voltage"]      = serialize.deserialize_uint32(buf[16:20], "reverse")/1000.0
        self.return_params["Y_voltage"]         = serialize.deserialize_uint32(buf[20:24], "reverse")/1000.0
        self.return_params["B_voltage"]         = serialize.deserialize_uint32(buf[24:28], "reverse")/1000.0
        self.return_params["R_power_factor"]     =  serialize.deserialize_uint32(buf[28:32], "reverse")/1000.0
        self.return_params["Y_power_factor"]     = serialize.deserialize_uint32(buf[32:36], "reverse")/1000.0
        self.return_params["B_power_factor"]     = serialize.deserialize_uint32(buf[36:40], "reverse")/1000.0
        self.return_params["frequency"]     =  serialize.deserialize_uint32(buf[40:44], "reverse")/1000.0
        self.return_params["apparent_power"]         = serialize.deserialize_uint32(buf[44:48], "reverse")/1000.0
        self.return_params["active_power"]       = serialize.deserialize_int32(buf[48:52],"reverse")/1000.0
        self.return_params["reactive_power"]        = serialize.deserialize_int32(buf[52:56],"reverse")/1000.0
        self.return_params["active_energy_imp"]      = serialize.deserialize_uint32(buf[56:60],"reverse")/1000.0
        self.return_params["active_energy_exp"]      = serialize.deserialize_uint32(buf[60:64],"reverse")/1000.0
        self.return_params["apparent_energy_imp"]    = serialize.deserialize_uint32(buf[64:68],"reverse")/1000.0
        self.return_params["apparent_energy_exp"]    = serialize.deserialize_uint32(buf[68:72],"reverse")/1000.0


    def getMeterpacket4(self):
        return ("Meter Time                         : {} \n"
                "R_Voltage                          : {} V\n"
                "Y_Voltage                          : {} V\n"
                "B_Voltage                          : {} V\n"
                "R_Current                          : {} A\n"
                "Y_Current                          : {} A\n"
                "B_Current                          : {} A\n"
                "R_power_factor                     : {} \n"
                "Y_power_factor                     : {} \n"
                "B_power_factor                     : {} \n"
                "frequency                          : {} Hz\n"
                "Active Power                       : {} KW\n"
                "Reactive Power                     : {} KVAr\n"
                "Apparent Power                     : {} KVA  \n"
                "active_energy_imp                  : {} Kwh  \n"
                "active_energy_exp                  : {} Kwh  \n"
                "apparent_energy_imp                : {} KVAh  \n"
                "apparent_energy_imp                : {} KVAh  \n"
                ).format(
                        self.return_params["realDatetime"],      
                        self.return_params["R_voltage"],      
                        self.return_params["Y_voltage"] ,  
                        self.return_params["B_voltage"] , 
                        self.return_params["R_current"]  ,    
                        self.return_params["Y_current"]   ,   
                        self.return_params["B_current"]    ,  
                        self.return_params["R_power_factor"] , 
                        self.return_params["Y_power_factor"]  ,
                        self.return_params["B_power_factor"]  ,
                        self.return_params["frequency"]  ,
                        self.return_params["active_power"]   ,
                        self.return_params["reactive_power"]  ,   
                        self.return_params["apparent_power"]   ,  
                        self.return_params["active_energy_imp"] , 
                        self.return_params["active_energy_exp"]  ,
                        self.return_params["apparent_energy_imp"],
                        self.return_params["apparent_energy_exp"],)


    def deserializePacket3(self,payload):
        buf = bytearray()
        buf = payload
        self.return_params["ACTI_ENERGY_HR"]   = serialize.deserialize_uint64(buf[0:8])/1000000000.0
        self.return_params["ACTE_ENERGY_HR"]   = serialize.deserialize_uint64(buf[8:16])/1000000000.0
        self.return_params["REACTIACTI_ENERGY_HR"]   = serialize.deserialize_uint64(buf[16:24])/1000000000.0
        self.return_params["REACTIACTE_ENERGY_HR"]   = serialize.deserialize_uint64(buf[24:32])/1000000000.0
        self.return_params["REACTEACTE_ENERGY_HR"]   = serialize.deserialize_uint64(buf[32:40])/1000000000.0
        self.return_params["REACTEACTI_ENERGY_HR"]   = serialize.deserialize_uint64(buf[40:48])/1000000000.0
        self.return_params["APPI_ENERGY_HR"]   = serialize.deserialize_uint64(buf[48:56])/1000000000.0
        self.return_params["APPE_ENERGY_HR"]   = serialize.deserialize_uint64(buf[56:64])/1000000000.0



    def getMeterpacket3(self):
        return ("Active Import Cumulative HR               : {:.9f} \n"
                "Active Export Cumulative HR               : {:.9f} \n"
                "Reactive Import Lag (Q1) HR               : {:.9f} \n"
                "Reactive Export Lead (Q2) HR              : {:.9f} \n"
                "Reactive Export Lag (Q3) HR               : {:.9f} \n"
                "Reactive Import Lead (Q4) HR              : {:.9f} \n"
                "Cumlative Apparent Energy Import HR       : {:.9f} \n"
                "Cumlative Apparent Energy Export HR       : {:.9f} \n"
                ).format(self.return_params["ACTI_ENERGY_HR"],
                        self.return_params["ACTE_ENERGY_HR"],
                        self.return_params["REACTIACTI_ENERGY_HR"],
                        self.return_params["REACTIACTE_ENERGY_HR"],
                        self.return_params["REACTEACTE_ENERGY_HR"],
                        self.return_params["REACTEACTI_ENERGY_HR"],
                        self.return_params["APPI_ENERGY_HR"],
                        self.return_params["APPE_ENERGY_HR"],
                        )



    def deserializeRecord(self,payload):
        buf = bytearray()
        # print ">>>>>>>>>>>>>>>>>>>>>>>."
        buf = payload
        unix_time = serialize.deserialize_uint32(buf[0:4], "reverse")
        self.return_params["realDatetime"]     = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(unix_time))
        self.return_params["frequency"]        = serialize.deserialize_uint32(buf[4:8], "reverse")/1000.0
        self.return_params["R_voltage"]        = serialize.deserialize_uint32(buf[8:12], "reverse")/1000.0
        self.return_params["Y_voltage"]        = serialize.deserialize_uint32(buf[12:16], "reverse")/1000.0
        self.return_params["B_voltage"]        = serialize.deserialize_uint32(buf[16:20], "reverse")/1000.0
        self.return_params["R_phase_current"]  = serialize.deserialize_uint32(buf[20:24], "reverse")/1000.0
        self.return_params["Y_phase_current"]  = serialize.deserialize_uint32(buf[24:28], "reverse")/1000.0
        self.return_params["B_phase_current"]  = serialize.deserialize_uint32(buf[28:32], "reverse")/1000.0
        self.return_params["neutral_current"]  = serialize.deserialize_uint32(buf[32:36], "reverse")/1000.0
        self.return_params["R_active_power"]   = serialize.deserialize_int32(buf[36:40], "reverse")/1000000.0
        self.return_params["Y_active_power"]   = serialize.deserialize_int32(buf[40:44], "reverse")/1000000.0
        self.return_params["B_active_power"]   = serialize.deserialize_int32(buf[44:48], "reverse")/1000000.0
        self.return_params["R_power_factor"]   = serialize.deserialize_int32(buf[48:52], "reverse")/1000.0
        self.return_params["Y_power_factor"]   = serialize.deserialize_int32(buf[52:56], "reverse")/1000.0
        self.return_params["B_power_factor"]   = serialize.deserialize_int32(buf[56:60], "reverse")/1000.0

    def getMeterRecord(self):
        return ("Meter Date Time            : {}        \n"
                "Frequency                  : {} Hz     \n"
                "R-Voltage                  : {} V      \n"
                "Y-Voltage                  : {} V      \n"
                "B-Voltage                  : {} V      \n"
                "R-Current                  : {} A      \n"
                "Y-Current                  : {} A      \n"
                "B-Current                  : {} A      \n"
                "Neutral Current            : {} A      \n"
                "R Active Power             : {} W      \n"
                "Y Active Power             : {} W      \n"
                "B Active Power             : {} W      \n"
                "R-PowerFactor              : {}        \n"
                "Y-PowerFactor              : {}        \n"
                "B-PowerFactor              : {}"
                )\
                .format(    self.return_params["realDatetime"],
                            self.return_params["frequency"],
                            self.return_params["R_voltage"],
                            self.return_params["Y_voltage"],
                            self.return_params["B_voltage"],
                            self.return_params["R_phase_current"],
                            self.return_params["Y_phase_current"],
                            self.return_params["B_phase_current"],
                            self.return_params["neutral_current"],
                            self.return_params["R_active_power"],
                            self.return_params["Y_active_power"],  
                            self.return_params["B_active_power"],
                            self.return_params["R_power_factor"],
                            self.return_params["Y_power_factor"],
                            self.return_params["B_power_factor"])

    def printMeterRecord(self,payload):
        return ("{:<2}{:<6}{:<21}{:<8}{:<8}{:<9}{:<8}{:<7}{:<12}{:<9}{:<8}{:<7}{:<12}{:<9}{:<8}{:<7}{}")\
                .format(" ",payload,
                            self.return_params["realDatetime"],
                            self.return_params["frequency"],
                            self.return_params["neutral_current"],
                            self.return_params["R_voltage"],
                            self.return_params["R_phase_current"],
                            self.return_params["R_power_factor"],
                            self.return_params["R_active_power"],
                            self.return_params["Y_voltage"],
                            self.return_params["Y_phase_current"],
                            self.return_params["Y_power_factor"],
                            self.return_params["Y_active_power"],  
                            self.return_params["B_voltage"],
                            self.return_params["B_phase_current"],
                            self.return_params["B_power_factor"],
                            self.return_params["B_active_power"])
    def deserializeTHD(self,payload):
        buf = bytearray()
        # print ">>>>>>>>>>>>>>>>>>>>>>>."
        buf = payload

        self.return_params["FUN_R_voltage"]        = serialize.deserialize_uint32(buf[0:4]) / 1000.0
        self.return_params["FUN_Y_voltage"]        = serialize.deserialize_uint32(buf[4:8]) / 1000.0
        self.return_params["FUN_B_voltage"]        = serialize.deserialize_uint32(buf[8:12]) / 1000.0
        self.return_params["FUN_R_phase_current"]  = serialize.deserialize_uint32(buf[12:16]) / 1000.0
        self.return_params["FUN_Y_phase_current"]  = serialize.deserialize_uint32(buf[16:20]) / 1000.0
        self.return_params["FUN_B_phase_current"]  = serialize.deserialize_uint32(buf[20:24]) / 1000.0

        self.return_params["THD_R_voltage"]        = serialize.deserialize_uint32(buf[24:28]) / 100000.0
        self.return_params["THD_Y_voltage"]        = serialize.deserialize_uint32(buf[28:32]) / 100000.0
        self.return_params["THD_B_voltage"]        = serialize.deserialize_uint32(buf[32:36]) / 100000.0
        self.return_params["THD_R_phase_current"]  = serialize.deserialize_uint32(buf[36:40]) / 100000.0
        self.return_params["THD_Y_phase_current"]  = serialize.deserialize_uint32(buf[40:44]) / 100000.0
        self.return_params["THD_B_phase_current"]  = serialize.deserialize_uint32(buf[44:48]) / 100000.0

        self.return_params["THD_R_phase_active"]   = serialize.deserialize_int32(buf[48:52]) / 100000.0
        self.return_params["THD_Y_phase_active"]   = serialize.deserialize_int32(buf[52:56]) / 100000.0
        self.return_params["THD_B_phase_active"]   = serialize.deserialize_int32(buf[56:60]) / 100000.0

        self.return_params["THD_R_phase_reactive"] = serialize.deserialize_int32(buf[60:64]) / 100000.0
        self.return_params["THD_Y_phase_reactive"] = serialize.deserialize_int32(buf[64:68]) / 100000.0
        self.return_params["THD_B_phase_reactive"] = serialize.deserialize_int32(buf[68:72]) / 100000.0

        self.return_params["THD_R_phase_apparent"] = serialize.deserialize_int32(buf[72:76]) / 100000.0
        self.return_params["THD_Y_phase_apparent"] = serialize.deserialize_int32(buf[76:80]) / 100000.0
        self.return_params["THD_B_phase_apparent"] = serialize.deserialize_int32(buf[80:84]) / 100000.0

        self.return_params["active_energy_imp"]    = serialize.deserialize_uint32(buf[84:88]) / 100.0
        self.return_params["active_energy_exp"]    = serialize.deserialize_uint32(buf[88:92]) / 100.0
        self.return_params["reactive_energy_q1"]   = serialize.deserialize_uint32(buf[92:96]) / 100.0
        self.return_params["reactive_energy_q2"]   = serialize.deserialize_uint32(buf[96:100]) / 100.0
        self.return_params["reactive_energy_q3"]   = serialize.deserialize_uint32(buf[100:104]) / 100.0
        self.return_params["reactive_energy_q4"]   = serialize.deserialize_uint32(buf[104:108]) / 100.0
        self.return_params["apparent_energy_imp"]  = serialize.deserialize_uint32(buf[108:112]) / 100.0
        self.return_params["apparent_energy_exp"]  = serialize.deserialize_uint32(buf[112:116]) / 100.0


    def getMeterpacketTHD(self):
        return ("FUN R_voltage               :  {} V\n"    
                "FUN Y_voltage               :  {} V\n"    
                "FUN B_voltage               :  {} V\n"  
                "FUN R_phase_current         :  {} A\n"    
                "FUN Y_phase_current         :  {} A\n"    
                "FUN B_phase_current         :  {} A\n"  
                "THD R_voltage               :  {} %\n"  
                "THD Y_voltage               :  {} % \n"  
                "THD B_voltage               :  {} % \n "  
                "THD R_phase_current         :  {} % \n"  
                "THD Y_phase_current         :  {} % \n"  
                "THD B_phase_current         :  {} % \n"
                "THD R_phase_active          :  {} W \n"   
                "THD Y_phase_active          :  {} W \n"   
                "THD B_phase_active          :  {} W\n"  
                "THD R_phase_reactive        :  {} VAR\n"  
                "THD Y_phase_reactive        :  {} VAR\n"  
                "THD B_phase_reactive        :  {} VAR\n"
                "THD R_phase_apparent        :  {} VA\n"   
                "THD Y_phase_apparent        :  {} VA\n"   
                "THD B_phase_apparent        :  {} VA\n" 
                "FUN active_energy_imp       :  {} kWh\n"  
                "FUN active_energy_exp       :  {} kWh\n"  
                "FUN reactive_energy_q1      :  {} kvarh\n"
                "FUN reactive_energy_q2      :  {} kvarh\n"
                "FUN reactive_energy_q3      :  {} kvarh\n"
                "FUN reactive_energy_q4      :  {} kvarh\n"
                "FUN apparent_energy_imp     :  {} kVAh\n"
                "FUN apparent_energy_exp     :  {} kVAh\n"

                ).format(   self.return_params["FUN_R_voltage"] ,
                            self.return_params["FUN_Y_voltage"]       ,
                            self.return_params["FUN_B_voltage"]       ,
                            self.return_params["FUN_R_phase_current"] ,
                            self.return_params["FUN_Y_phase_current"] ,
                            self.return_params["FUN_B_phase_current"] ,
                            self.return_params["THD_R_voltage"]       ,
                            self.return_params["THD_Y_voltage"]       ,
                            self.return_params["THD_B_voltage"]       ,
                            self.return_params["THD_R_phase_current"] ,
                            self.return_params["THD_Y_phase_current"] ,
                            self.return_params["THD_B_phase_current"] ,
                            self.return_params["THD_R_phase_active"]  ,
                            self.return_params["THD_Y_phase_active"]  ,
                            self.return_params["THD_B_phase_active"]  ,
                            self.return_params["THD_R_phase_reactive"],
                            self.return_params["THD_Y_phase_reactive"],
                            self.return_params["THD_B_phase_reactive"],
                            self.return_params["THD_R_phase_apparent"],
                            self.return_params["THD_Y_phase_apparent"],
                            self.return_params["THD_B_phase_apparent"],
                            self.return_params["active_energy_imp"]   ,
                            self.return_params["active_energy_exp"]   ,
                            self.return_params["reactive_energy_q1"]  ,
                            self.return_params["reactive_energy_q2"]  ,
                            self.return_params["reactive_energy_q3"]  ,
                            self.return_params["reactive_energy_q4"]  ,
                            self.return_params["apparent_energy_imp"] ,
                            self.return_params["apparent_energy_exp"]
                        )

    #def print_summary(self):
        # print("FUN R-Voltage       : %8.3f V" % self.return_params["FUN R_voltage"])
        # print("FUN Y-Voltage       : %8.3f V" % self.return_params["FUN Y_voltage"])
        # print("FUN B-Voltage       : %8.3f V\n" % self.return_params["FUN B_voltage"])
        # print("FUN R-Current       : %8.3f A" % self.return_params["FUN R_phase_current"])
        # print("FUN Y-Current       : %8.3f A" % self.return_params["FUN Y_phase_current"])
        # print("FUN B-Current       : %8.3f A\n" % self.return_params["FUN B_phase_current"])
        # print("THD R-Voltage       : %8.5f %% " % self.return_params["THD R_voltage"])
        # print("THD Y-Voltage       : %8.5f %% " % self.return_params["THD Y_voltage"])
        # print("THD B-Voltage       : %8.5f %% " % self.return_params["THD B_voltage"])
        # print("THD R-Current       : %8.5f %% " % self.return_params["THD R_phase_current"])
        # print("THD Y-Current       : %8.5f %% " % self.return_params["THD Y_phase_current"])
        # print("THD B-Current       : %8.5f %% \n" % self.return_params["THD B_phase_current"])
        # print("THD R Active Power  : %8.5f W" % self.return_params["THD R_phase_active"])
        # print("THD Y Active Power  : %8.5f W" % self.return_params["THD Y_phase_active"])
        # print("THD B Active Power  : %8.5f W\n" % self.return_params["THD B_phase_active"])
        # print("THD R Reactive Power: %8.5f VAR" % self.return_params["THD R_phase_reactive"])
        # print("THD Y Reactive Power: %8.5f VAR" % self.return_params["THD Y_phase_reactive"])
        # print("THD B Reactive Power: %8.5f VAR\n" % self.return_params["THD B_phase_reactive"])
        # print("THD R Apparent Power: %8.5f VA" % self.return_params["THD R_phase_apparent"])
        # print("THD Y Apparent Power: %8.5f VA" % self.return_params["THD Y_phase_apparent"])
        # print("THD B Apparent Power: %8.5f VA\n" % self.return_params["THD B_phase_apparent"])
        # print("Active Energy (Imp) : %8.2f kWh" % self.return_params["active_energy_imp"])
        # print("Active Energy (Exp) : %8.2f kWh" % self.return_params["active_energy_exp"])
        # print("Reactive Energy Q1  : %8.2f kvarh" % self.return_params["reactive_energy_q1"])
        # print("Reactive Energy Q2  : %8.2f kvarh" % self.return_params["reactive_energy_q2"])
        # print("Reactive Energy Q3  : %8.2f kvarh" % self.return_params["reactive_energy_q3"])
        # print("Reactive Energy Q4  : %8.2f kvarh" % self.return_params["reactive_energy_q4"])
        # print("Apparent Energy (Imp): %8.2f kVAh" % self.return_params["apparent_energy_imp"])
        # print("Apparent Energy (Exp): %8.2f kVAh\n\n\n\n" % self.return_params["apparent_energy_exp"]) 

# if __name__ == "__main__":
#     hexfile = {'0': 0,
#                '1': 1,
#                '2': 2,
#                '3': 3,
#                '4': 4,
#                '5': 5,
#                '6': 6,
#                '7': 7,
#                '8': 8,
#                '9': 9,
#                'a': 10,
#                'b': 11,
#                'c': 12,
#                'd': 13,
#                'e': 14,
#                'f': 15
#                }
#     data = bytearray()
#     b="6400000000000000000000000000000000006301000018180000020000e80300000000000000000000000000000000000000008813e80300000000e803000000000000000000000000ef5ce9824d9d047f5fd664"
#     pLen = len(b)
#     print pLen

#     index = 0
#     while (index < pLen):
#         num = 0
#         msb = hexfile[b[index]]
#         index += 1
#         lsb = hexfile[b[index]]
#         index += 1

#         num = (msb * 10) + lsb
#         data.append(num)

#     bdl = DCUBundlePacket()
#     try:
#         bdl.deserialize_packet_bundle(tap_packet.data)                    
#     except IndexError:
#         raise SimpletermError(SimpletermError.GET_PARAM_UNEXPECTED_PAYLOAD_LENGTH, tap_packet=tap_packet)
#     # return bdl.get_packet_dictionary_bundle()  
#     return bdl.get_packet_bundle()


        