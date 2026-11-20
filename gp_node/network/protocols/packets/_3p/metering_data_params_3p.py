import datetime
import time
import gp_node.utils.serialize as serialize
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils.serialize import deserialize_uint32
from .tamper_flag_3p import TamperFlag_3P
import gp_node.utils.serialize as serialize


class MeteringDataParams3P(object):

    def __init__(self):
        dt = datetime.datetime(1970, 1, 1)
        self.date_time = 0 
        self.serial_number = 0 
        self.r_phase_voltage = 0 
        self.y_phase_voltage = 0  
        self.b_phase_voltage = 0  
        self.r_phase_current = 0  
        self.y_phase_current = 0 
        self.b_phase_current = 0  
        self.r_phase_pf = 0
        self.y_phase_pf = 0  
        self.b_phase_pf = 0 
        self.tamper_info = [] 
        self.neutral_current = 0
        self.total_real_energy = 0
        self.total_apparent_energy = 0
        self.total_reactive_energy = 0
        self.lag_only_reactive_energy = 0
        self.lag_only_apparent_energy = 0
        self.lead_only_reactive_energy = 0
        self.lead_only_apparent_energy = 0
        self.total_active_power = 0
        self.import_active_power = 0
        self.total_apparent_power = 0
        self.total_reactive_power = 0 
        self.total_harmonic_power = 0 
        self.protocol_version = 0
        self.maxwell_software_version = 0
        self.maxwell_hardware_version = 0
        self.total_real_energy_high_res = 0
        self.total_apparent_energy_high_res = 0
        self.total_reactive_energy_high_res = 0
        self.lag_only_reactive_energy_high_res = 0
        self.lag_only_apparent_energy_high_res = 0
        self.lead_only_reactive_energy_high_res = 0
        self.lead_only_apparent_energy_high_res = 0
        self.status = 0
        self.TotalPf = 0
        self.Frequency = 0
        self.r_phase_reactive_power = 0
        self.y_phase_reactive_power = 0
        self.b_phase_reactive_power = 0
        self.power_failure_count = 0
        self.power_failure_duration = 0
        self.tamper_count = 0
        self.billing_count = 0
        self.programming_count = 0
        self.billing_date = 0
        self.MD_active_power_import = 0
        self.MD_apparent_power_import = 0  
        self.reactive_energy_quad1 = 0
        self.reactive_energy_quad2 = 0
        self.reactive_energy_quad3 = 0
        self.reactive_energy_quad4 = 0

        self.return_params = {"date_time":0, 
                                "serial_number" : 0, 
                                "r_phase_voltage" : 0,
                                "y_phase_voltage" : 0,  
                                "b_phase_voltage ": 0,  
                                "r_phase_current" : 0, 
                                "y_phase_current" : 0, 
                                "b_phase_current ": 0,  
                                "r_phase_pf ": 0,
                                "y_phase_pf ": 0,  
                                "b_phase_pf ": 0, 
                                "tamper_info ": 0, 
                                "neutral_current " : 0,
                                "total_real_energy ": 0,
                                "total_apparent_energy" : 0,
                                "total_reactive_energy ": 0,
                                "lag_only_reactive_energy" : 0,
                                "lag_only_apparent_energy ": 0,
                                "lead_only_reactive_energy ": 0,
                                "lead_only_apparent_energy ": 0,
                                "total_active_power ": 0,
                                "total_apparent_power" : 0,
                                "total_reactive_power ": 0, 
                                "total_harmonic_power ": 0, 
                                "protocol_version ": 0,
                                "maxwell_software_version" : 0,
                                "maxwell_hardware_version ": 0,
                                "total_real_energy_high_res" : 0,
                                "total_apparent_energy_high_res" : 0,
                                "total_reactive_energy_high_res ": 0,
                                "lag_only_reactive_energy_high_res" : 0,
                                "lag_only_apparent_energy_high_res ": 0,
                                "lead_only_reactive_energy_high_res ": 0,
                                "lead_only_apparent_energy_high_res" : 0,
                                "TamperFlag": [],
                                "status"    : 0,
                                "TotalPf"   : 0,
                                "Frequency" : 0,
                                "tamper_intiger":0
                                }
    
    def __str__(self):
        return ("date & time               : {}  \n"
                "Serial number             : {}  \n"
                "R phase voltage           : {} V\n"
                "Y phase voltage           : {} V\n"
                "B phase voltage           : {} V\n"
                "R phase current           : {} A\n"
                "Y phase current           : {} A\n"
                "B phase current           : {} A\n"
                "R phase PF                : {} \n"
                "Y phase PF                : {} \n"
                "B phase PF                : {} \n"
                "tamper_info               : {} \n"
                "Neutral Current           : {} A\n"
                "Total Real Energy         : {} KWH\n"
                "Total Apparent Energy     : {} KVAH\n"
                "Total Reactive Energy     : {} KVARH\n"
                "Lag Only Reactive Energy  : {} KVARH\n"
                "Lag Only Apparent Energy  : {} KVAH\n"
                "Lead Only Reactive Energy : {} KVARH\n"
                "Lead Only Apparent Energy : {} KVAH\n"
                "Total Active Power        : {} KW\n"
                "Total Apparent Power      : {} KVA\n"
                "Total Reactive Power      : {} KVAR\n"
                "Total Harmonic Power      : {} KW\n"
                "Protocol Version                       : 0x03\n",
                "maxwell_software_version               : 0X02\n",
                "maxwell_hardware_version               : 0x02\n"
                "total_real_energy_high_res             : 0.00\n",
                "total_apparent_energy_high_res         : 0.00\n",
                "total_reactive_energy_high_res         : 0.00\n", 
                "lag_only_reactive_energy_high_res      : 0.00\n",
                "lag_only_apparent_energy_high_res      : 0.00\n", 
                "lead_only_reactive_energy_high_res     : 0.00\n",
                "lead_only_apparent_energy_high_res     : 0.00\n",
                "status : 0\n",
                "TotalPf : 0.00\n",
                "Frequency : {} Hz")\
                .format(self.return_params["date_time"],
                        self.return_params["serial_number"],
                        self.return_params["r_phase_voltage"],
                        self.return_params["y_phase_voltage"],
                        self.return_params["b_phase_voltage"],
                        self.return_params["r_phase_current"],
                        self.return_params["y_phase_current"],
                        self.return_params["b_phase_current"],
                        self.return_params["r_phase_pf"],
                        self.return_params["y_phase_pf"],
                        self.return_params["b_phase_pf"],
                        self.return_params["tamper_info"],
                        self.return_params["neutral_current"],
                        self.return_params["total_real_energy"],
                        self.return_params["total_apparent_energy"],
                        self.return_params["total_reactive_energy"],
                        self.return_params["lag_only_reactive_energy"],
                        self.return_params["lag_only_apparent_energy"],
                        self.return_params["lead_only_reactive_energy"],
                        self.return_params["lead_only_apparent_energy"],
                        self.return_params["total_active_power"],
                        self.return_params["total_apparent_power"],
                        self.return_params["total_reactive_power"],
                        self.return_params["total_harmonic_power"],
                        self.return_params["protocol_version"],
                        self.return_params["maxwell_software_version"], 
                        self.return_params["maxwell_hardware_version"], 
                        self.return_params["total_real_energy_high_res"], 
                        self.return_params["total_apparent_energy_high_res"], 
                        self.return_params["total_reactive_energy_high_res"], 
                        self.return_params["lag_only_reactive_energy_high_res"],
                        self.return_params["lag_only_apparent_energy_high_res"], 
                        self.return_params["lead_only_reactive_energy_high_res"],
                        self.return_params["lead_only_apparent_energy_high_res"],
                        self.return_params["status"],
                        self.return_params["TotalPf"],
                        self.return_params["Frequency"])
     
        
    def deserialize_p1(self, payload):
        bytes = bytearray()
        bytes = payload
        dt = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[0]<<24) + (bytes[1]<<16) + (bytes[2]<<8) + bytes[3]))
        self.return_params["date_time"] = dt
        self.return_params["r_phase_voltage"] = ((bytes[4]<<24) + (bytes[5]<<16) + (bytes[6]<<8) + bytes[7])/1000.0
        self.return_params["y_phase_voltage"]= ((bytes[8]<<24) + (bytes[9]<<16) + (bytes[10]<<8) + bytes[11])/1000.0
        self.return_params["b_phase_voltage"]= ((bytes[12]<<24) + (bytes[13]<<16) + (bytes[14]<<8) + bytes[15])/1000.0
        self.return_params["r_phase_current"]= ((bytes[16]<<24) + (bytes[17]<<16) + (bytes[18]<<8) + bytes[19])/1000.0
        self.return_params["y_phase_current"]= ((bytes[20]<<24) + (bytes[21]<<16) + (bytes[22]<<8) + bytes[23])/1000.0 
        self.return_params["b_phase_current"]= ((bytes[24]<<24) + (bytes[25]<<16) + (bytes[26]<<8) + bytes[27])/1000.0
        self.return_params["r_phase_pf"] = serialize.deserialize_int16(bytes[28:30])/10000.0
        self.return_params["y_phase_pf"] = serialize.deserialize_int16(bytes[30:32])/10000.0
        self.return_params["b_phase_pf"] = serialize.deserialize_int16(bytes[32:34])/10000.0
        #self.return_params["r_phase_pf"]= int((bytes[28]<<8) + bytes[29])/10000.0
        #self.return_params["y_phase_pf"]= int((bytes[30]<<8) + bytes[31])/10000.0
        #self.return_params["b_phase_pf"]= int((bytes[32]<<8) + bytes[33])/10000.0
        self.return_params["TotalPf"]= ((bytes[34]<<8) + bytes[35])/10000.0
        self.return_params["Frequency"] = ((bytes[36]<<8) + bytes[37])/100.0
        tamper_tmp = ((bytes[38]<<8) + bytes[39])
        if(self.tamper_info.count(TamperFlag_3P("R_PHASE_MISSING"))):
            self.tamper_info.remove(TamperFlag_3P("R_PHASE_MISSING"))
        if(self.tamper_info.count(TamperFlag_3P("Y_PHASE_MISSING"))):
            self.tamper_info.remove(TamperFlag_3P("Y_PHASE_MISSING"))
        if(self.tamper_info.count(TamperFlag_3P("B_PHASE_MISSING"))):
            self.tamper_info.remove(TamperFlag_3P("B_PHASE_MISSING"))
        if(self.tamper_info.count(TamperFlag_3P("CURRENT_BYPASS"))):
            self.tamper_info.remove(TamperFlag_3P("CURRENT_BYPASS"))
        if(self.tamper_info.count(TamperFlag_3P("R_PHASE_REVERSE_CURRENT"))):
            self.tamper_info.remove(TamperFlag_3P("R_PHASE_REVERSE_CURRENT"))
        if(self.tamper_info.count(TamperFlag_3P("Y_PHASE_REVERSE_CURRENT"))):
            self.tamper_info.remove(TamperFlag_3P("Y_PHASE_REVERSE_CURRENT"))
        if(self.tamper_info.count(TamperFlag_3P("B_PHASE_REVERSE_CURRENT"))):
            self.tamper_info.remove(TamperFlag_3P("B_PHASE_REVERSE_CURRENT"))
        if(self.tamper_info.count(TamperFlag_3P("MAGNETIC"))):
            self.tamper_info.remove(TamperFlag_3P("MAGNETIC"))
        if(self.tamper_info.count(TamperFlag_3P("R_PHASE_CT_OPEN"))):
            self.tamper_info.remove(TamperFlag_3P("R_PHASE_CT_OPEN"))
        if(self.tamper_info.count(TamperFlag_3P("Y_PHASE_CT_OPEN"))):
            self.tamper_info.remove(TamperFlag_3P("Y_PHASE_CT_OPEN"))
        if(self.tamper_info.count(TamperFlag_3P("B_PHASE_CT_OPEN"))):
            self.tamper_info.remove(TamperFlag_3P("B_PHASE_CT_OPEN"))
        if(self.tamper_info.count(TamperFlag_3P("CURRENT_UNBALANCE"))):
            self.tamper_info.remove(TamperFlag_3P("CURRENT_UNBALANCE"))
        if(self.tamper_info.count(TamperFlag_3P("VOLTAGE_UNBALANCE"))):
            self.tamper_info.remove(TamperFlag_3P("VOLTAGE_UNBALANCE"))
        if(self.tamper_info.count(TamperFlag_3P("R_PHASE_ND"))):
            self.tamper_info.remove(TamperFlag_3P("R_PHASE_ND"))
        if(self.tamper_info.count(TamperFlag_3P("Y_PHASE_ND"))):
            self.tamper_info.remove(TamperFlag_3P("Y_PHASE_ND"))
        if(self.tamper_info.count(TamperFlag_3P("B_PHASE_ND"))):
            self.tamper_info.remove(TamperFlag_3P("B_PHASE_ND"))

        if ((tamper_tmp/2**0 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("R_PHASE_MISSING"))
        if ((tamper_tmp/2**1 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("Y_PHASE_MISSING"))
        if ((tamper_tmp/2**2 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("B_PHASE_MISSING"))
        if ((tamper_tmp/2**3 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("CURRENT_BYPASS"))
        if ((tamper_tmp/2**4 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("R_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**5 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("Y_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**6 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("B_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**7 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("MAGNETIC"))
        if ((tamper_tmp/2**8 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("R_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**9 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("Y_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**10 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("B_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**11 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("CURRENT_UNBALANCE"))
        if ((tamper_tmp/2**12 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("VOLTAGE_UNBALANCE"))
        if ((tamper_tmp/2**13 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("R_PHASE_ND"))
        if ((tamper_tmp/2**14 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("Y_PHASE_ND"))
        if ((tamper_tmp/2**15 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("B_PHASE_ND"))
        self.return_params["tamper_info"] = self.tamper_info

        self.return_params["neutral_current"] = ((bytes[40]<<24) + (bytes[41]<<16) + (bytes[42]<<8) + bytes[43])/1000.0

        
    
    def get_packet_p1(self):
        return("date & time      : {} \n"
                "R phase voltage : {} V\n"
                "Y phase voltage : {} V\n"
                "B phase voltage : {} V\n"
                "R phase current : {} A\n"
                "Y phase current : {} A\n"
                "B phase current : {} A\n"
                "R phase PF      : {} \n"
                "Y phase PF      : {} \n"
                "B phase PF      : {} \n"
                "Total PF        : {} \n"
                "Frequency       : {} Hz\n"
                "tamper_info     : {} \n"
                "Neutral Current : {} A\n")\
                .format(self.return_params["date_time"],
                        self.return_params["r_phase_voltage"],
                        self.return_params["y_phase_voltage"], 
                        self.return_params["b_phase_voltage"], 
                        self.return_params["r_phase_current"], 
                        self.return_params["y_phase_current"],
                        self.return_params["b_phase_current"],
                        self.return_params["r_phase_pf"], 
                        self.return_params["y_phase_pf"], 
                        self.return_params["b_phase_pf"],
                        self.return_params["TotalPf"],
                        self.return_params["Frequency"],
                        self.return_params["tamper_info"],
                        self.return_params["neutral_current"])

    def deserialize_p2(self, payload):
        bytes = bytearray()
        bytes = payload
        self.total_real_energy = ((bytes[0]<<24) +(bytes[1]<<16) + (bytes[2]<<8) + bytes[3])/100.0
        self.total_apparent_energy = ((bytes[4]<<24) +(bytes[5]<<16) + (bytes[6]<<8) + bytes[7])/100.0
        self.total_reactive_energy = ((bytes[8]<<24) +(bytes[9]<<16) + (bytes[10]<<8) + bytes[11])/100.0
        self.lag_only_reactive_energy = ((bytes[12]<<24) +(bytes[13]<<16) + (bytes[14]<<8) + bytes[15])/100.0
        self.lead_only_reactive_energy = ((bytes[16]<<24) +(bytes[17]<<16) + (bytes[18]<<8) + bytes[19])/100.0
        self.r_phase_reactive_power = ((bytes[20]<<24) +(bytes[21]<<16) + (bytes[22]<<8) + bytes[23])/1000.0
        self.y_phase_reactive_power = ((bytes[24]<<24) +(bytes[25]<<16) + (bytes[26]<<8) + bytes[27])/1000.0
        self.b_phase_reactive_power= ((bytes[28]<<24) +(bytes[29]<<16) + (bytes[30]<<8) + bytes[31])/1000.0
        self.total_active_power = ((bytes[32]<<24) +(bytes[33]<<16) + (bytes[34]<<8) + bytes[35])/1000.0
        self.total_apparent_power = ((bytes[36]<<24) +(bytes[37]<<16) + (bytes[38]<<8) + bytes[39])/1000.0
        self.total_reactive_power = serialize.deserialize_int32(bytes[40:44])/1000.0
        #self.total_reactive_power = int(((bytes[40]<<24) +(bytes[41]<<16) + (bytes[42]<<8) + bytes[43]))/1000.0

    def get_packet_p2(self):
        return ("Total Real Energy         : {} KWH\n"
                "Total Apparent Energy     : {} KVAH\n"
                "Total Reactive Energy     : {} KVARH\n"
                "Lag Only Reactive Energy  : {} KVARH\n"
                "Lead Only Reactive Energy : {} KVARH\n"
                "R Phase Reactive Power    : {} VAR\n"
                "Y Phase Reactive Power    : {} VAR\n"
                "B Phase Reactive Power    : {} VAR\n"
                "Total Active Power        : {} W\n"
                "Total Apparent Power      : {} VA\n"
                "Total Reactive Power      : {} VAR\n")\
                .format(self.total_real_energy,
                        self.total_apparent_energy,
                        self.total_reactive_energy,
                        self.lag_only_reactive_energy,
                        self.lead_only_reactive_energy,
                        self.r_phase_reactive_power,
                        self.y_phase_reactive_power,
                        self.b_phase_reactive_power,
                        self.total_active_power,
                        self.total_apparent_power,
                        self.total_reactive_power)

    def deserialize_p3(self, payload):
        bytes = bytearray()
        bytes = payload
        self.return_params["serial_number"] = ((bytes[0]<<24) + (bytes[1]<<16) + (bytes[2]<<8) + bytes[3])
        self.return_params["protocol_version"] = (bytes[4])
        self.return_params["maxwell_software_version"] = (bytes[5])
        self.return_params["maxwell_hardware_version"] = (bytes[6])
        self.total_real_energy_high_res = ((bytes[7]<<24) + (bytes[8]<<16) + (bytes[9]<<8) + bytes[10])/10000.0
        self.return_params["total_apparent_energy_high_res"] = ((bytes[11]<<24) + (bytes[12]<<16) + (bytes[13]<<8) + bytes[14])/10000.0 
        self.return_params["total_reactive_energy_high_res"] = ((bytes[15]<<24) + (bytes[16]<<16) + (bytes[17]<<8) + bytes[18])/10000.0
        self.return_params["lag_only_reactive_energy_high_res"] = ((bytes[19]<<24) + (bytes[20]<<16) + (bytes[21]<<8) + bytes[22])/10000.0 
        self.return_params["lead_only_reactive_energy_high_res"] = ((bytes[23]<<24) + (bytes[24]<<16) + (bytes[25]<<8) + bytes[26])/10000.0
        #self.return_params["TamperFlag"] = ((bytes[27]<<24) + (bytes[28]<<16) + (bytes[29]<<8) + bytes[30])
        self.return_params["status"]  = bytes[31]
        #----------------------------------------
        tamper_tmp = ((bytes[27]<<24) + (bytes[28]<<16) + (bytes[29]<<8) + bytes[30])
        if(self.tamper_info.count(TamperFlag_3P("R_PHASE_MISSING"))):
            self.tamper_info.remove(TamperFlag_3P("R_PHASE_MISSING"))
        if(self.tamper_info.count(TamperFlag_3P("Y_PHASE_MISSING"))):
            self.tamper_info.remove(TamperFlag_3P("Y_PHASE_MISSING"))
        if(self.tamper_info.count(TamperFlag_3P("B_PHASE_MISSING"))):
            self.tamper_info.remove(TamperFlag_3P("B_PHASE_MISSING"))
        if(self.tamper_info.count(TamperFlag_3P("CURRENT_BYPASS"))):
            self.tamper_info.remove(TamperFlag_3P("CURRENT_BYPASS"))
        if(self.tamper_info.count(TamperFlag_3P("R_PHASE_REVERSE_CURRENT"))):
            self.tamper_info.remove(TamperFlag_3P("R_PHASE_REVERSE_CURRENT"))
        if(self.tamper_info.count(TamperFlag_3P("Y_PHASE_REVERSE_CURRENT"))):
            self.tamper_info.remove(TamperFlag_3P("Y_PHASE_REVERSE_CURRENT"))
        if(self.tamper_info.count(TamperFlag_3P("B_PHASE_REVERSE_CURRENT"))):
            self.tamper_info.remove(TamperFlag_3P("B_PHASE_REVERSE_CURRENT"))
        if(self.tamper_info.count(TamperFlag_3P("MAGNETIC"))):
            self.tamper_info.remove(TamperFlag_3P("MAGNETIC"))
        if(self.tamper_info.count(TamperFlag_3P("R_PHASE_CT_OPEN"))):
            self.tamper_info.remove(TamperFlag_3P("R_PHASE_CT_OPEN"))
        if(self.tamper_info.count(TamperFlag_3P("Y_PHASE_CT_OPEN"))):
            self.tamper_info.remove(TamperFlag_3P("Y_PHASE_CT_OPEN"))
        if(self.tamper_info.count(TamperFlag_3P("B_PHASE_CT_OPEN"))):
            self.tamper_info.remove(TamperFlag_3P("B_PHASE_CT_OPEN"))
        if(self.tamper_info.count(TamperFlag_3P("CURRENT_UNBALANCE"))):
            self.tamper_info.remove(TamperFlag_3P("CURRENT_UNBALANCE"))
        if(self.tamper_info.count(TamperFlag_3P("VOLTAGE_UNBALANCE"))):
            self.tamper_info.remove(TamperFlag_3P("VOLTAGE_UNBALANCE"))
        if(self.tamper_info.count(TamperFlag_3P("R_PHASE_ND"))):
            self.tamper_info.remove(TamperFlag_3P("R_PHASE_ND"))
        if(self.tamper_info.count(TamperFlag_3P("Y_PHASE_ND"))):
            self.tamper_info.remove(TamperFlag_3P("Y_PHASE_ND"))
        if(self.tamper_info.count(TamperFlag_3P("B_PHASE_ND"))):
            self.tamper_info.remove(TamperFlag_3P("B_PHASE_ND"))
        if(self.tamper_info.count(TamperFlag_3P("LOW_VOLTAGE_R_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("LOW_VOLTAGE_R_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("LOW_VOLTAGE_Y_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("LOW_VOLTAGE_Y_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("LOW_VOLTAGE_B_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("LOW_VOLTAGE_B_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("OVER_VOLTAGE_R_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("OVER_VOLTAGE_R_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("OVER_VOLTAGE_Y_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("OVER_VOLTAGE_Y_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("OVER_VOLTAGE_B_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("OVER_VOLTAGE_B_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("OVER_CURRENT_R_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("OVER_CURRENT_R_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("OVER_CURRENT_Y_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("OVER_CURRENT_Y_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("OVER_CURRENT_B_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("OVER_CURRENT_B_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("LOW_PF_R_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("LOW_PF_R_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("LOW_PF_Y_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("LOW_PF_Y_PHASE"))
        if(self.tamper_info.count(TamperFlag_3P("LOW_PF_B_PHASE"))):
            self.tamper_info.remove(TamperFlag_3P("LOW_PF_B_PHASE"))


        if ((tamper_tmp/2**0 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("R_PHASE_MISSING"))
        if ((tamper_tmp/2**1 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("Y_PHASE_MISSING"))
        if ((tamper_tmp/2**2 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("B_PHASE_MISSING"))
        if ((tamper_tmp/2**3 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("CURRENT_BYPASS"))
        if ((tamper_tmp/2**4 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("R_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**5 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("Y_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**6 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("B_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**7 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("MAGNETIC"))
        if ((tamper_tmp/2**8 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("R_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**9 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("Y_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**10 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("B_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**11 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("CURRENT_UNBALANCE"))
        if ((tamper_tmp/2**12 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("VOLTAGE_UNBALANCE"))
        if ((tamper_tmp/2**13 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("R_PHASE_ND"))
        if ((tamper_tmp/2**14 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("Y_PHASE_ND"))
        if ((tamper_tmp/2**15 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("B_PHASE_ND"))
        if ((tamper_tmp/2**16 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("LOW_VOLTAGE_R_PHASE"))
        if ((tamper_tmp/2**17 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("LOW_VOLTAGE_Y_PHASE"))
        if ((tamper_tmp/2**18 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("LOW_VOLTAGE_B_PHASE"))
        if ((tamper_tmp/2**19 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("OVER_VOLTAGE_R_PHASE"))
        if ((tamper_tmp/2**20 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("OVER_VOLTAGE_Y_PHASE"))
        if ((tamper_tmp/2**21 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("OVER_VOLTAGE_B_PHASE"))
        if ((tamper_tmp/2**22 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("OVER_CURRENT_R_PHASE"))
        if ((tamper_tmp/2**23 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("OVER_CURRENT_Y_PHASE"))
        if ((tamper_tmp/2**24 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("OVER_CURRENT_B_PHASE"))
        if ((tamper_tmp/2**25 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("LOW_PF_R_PHASE"))
        if ((tamper_tmp/2**26 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("LOW_PF_Y_PHASE"))
        if ((tamper_tmp/2**27 % 2) == 1):
            self.tamper_info.append(TamperFlag_3P("LOW_PF_B_PHASE"))

        self.return_params["tamper_intiger"] = tamper_tmp
        self.return_params["TamperFlag"] = self.tamper_info
        #----------------------------------------


    def get_packet_p3(self):
        return("Serial Number                           : {}\n"
                "Protocol Version                       : {}\n"
                "maxwell_software_version               : {}\n"
                "maxwell_hardware_version               : {}\n"
                "total_real_energy_high_res             : {} KWH\n"
                "total_apparent_energy_high_res         : {} KVAH\n"
                "total_reactive_energy_high_res         : {} KVARH\n" 
                "lag_only_reactive_energy_high_res      : {} KVARH\n"
                "lead_only_reactive_energy_high_res     : {} KVARH\n"
                "Tamper Info                            : {} \n"
                "Tamper Intiger(Debug)                  : {} \n"
                "status Flag                            : {} \n")\
                .format(self.return_params["serial_number"],
                        self.return_params["protocol_version"],
                        self.return_params["maxwell_software_version"],
                        self.return_params["maxwell_hardware_version"],
                        self.total_real_energy_high_res,
                        self.return_params["total_apparent_energy_high_res"],
                        self.return_params["total_reactive_energy_high_res"],
                        self.return_params["lag_only_reactive_energy_high_res"],
                        self.return_params["lead_only_reactive_energy_high_res"],
                        self.return_params["TamperFlag"],
                        self.return_params['tamper_intiger'],
                        self.return_params["status"])
                
    def get_instant_profile_packet(self):
        return(
                "MD_active_power_import     : {} W\n"
                "MD_active_power_TOD1       : {} W\n"
                "MD_active_power_TOD2       : {} W\n"
                "MD_active_power_TOD3       : {} W\n"
                "MD_active_power_TOD4       : {} W\n"
                "MD_active_power_TOD5       : {} W\n"
                "MD_active_power_TOD6       : {} W\n"
                "MD_active_power_TOD7       : {} W\n"
                "MD_active_power_TOD8       : {} W\n"
                "MD_apparent_power_import   : {} VA\n"
                "MD_apparent_power_TOD1     : {} VA\n"
                "MD_apparent_power_TOD2     : {} VA\n"
                "MD_apparent_power_TOD3     : {} VA\n"
                "MD_apparent_power_TOD4     : {} VA\n"
                "MD_apparent_power_TOD5     : {} VA\n"
                "MD_apparent_power_TOD6     : {} VA\n"
                "MD_apparent_power_TOD7     : {} VA\n"
                "MD_apparent_power_TOD8     : {} VA\n")\
                .format(self.MD_active_power_import,
                        self.MD_active_power_TOD1, 
                        self.MD_active_power_TOD2,
                        self.MD_active_power_TOD3,
                        self.MD_active_power_TOD4,
                        self.MD_active_power_TOD5,
                        self.MD_active_power_TOD6, 
                        self.MD_active_power_TOD7, 
                        self.MD_active_power_TOD8, 
                        self.MD_apparent_power_import, 
                        self.MD_apparent_power_TOD1,
                        self.MD_apparent_power_TOD2,
                        self.MD_apparent_power_TOD3,
                        self.MD_apparent_power_TOD4,
                        self.MD_apparent_power_TOD5,
                        self.MD_apparent_power_TOD6,
                        self.MD_apparent_power_TOD7,
                        self.MD_apparent_power_TOD8)
                
    def deserialize_instant_profile_packet(self, payload):
        buf = bytearray()
        buf = payload
        self.MD_active_power_import = serialize.deserialize_uint32(buf[0:4])/1000.0
        self.MD_active_power_TOD1 = serialize.deserialize_uint32(buf[4:8])/1000.0
        self.MD_active_power_TOD2 = serialize.deserialize_uint32(buf[8:12])/1000.0
        self.MD_active_power_TOD3 = serialize.deserialize_uint32(buf[12:16])/1000.0
        self.MD_active_power_TOD4 = serialize.deserialize_uint32(buf[16:20])/1000.0
        self.MD_active_power_TOD5 = serialize.deserialize_uint32(buf[20:24])/1000.0
        self.MD_active_power_TOD6 = serialize.deserialize_uint32(buf[24:28])/1000.0
        self.MD_active_power_TOD7 = serialize.deserialize_int32(buf[28:32])/1000.0
        self.MD_active_power_TOD8 = serialize.deserialize_int32(buf[32:36])/1000.0
        self.MD_apparent_power_import = serialize.deserialize_int32(buf[36:40])/1000.0
        self.MD_apparent_power_TOD1 = serialize.deserialize_uint32(buf[40:44])/1000.0
        self.MD_apparent_power_TOD2 = serialize.deserialize_uint32(buf[44:48])/1000.0
        self.MD_apparent_power_TOD3 = serialize.deserialize_int32(buf[48:52])/1000.0
        self.MD_apparent_power_TOD4 = serialize.deserialize_int32(buf[52:56])/1000.0
        self.MD_apparent_power_TOD5 = serialize.deserialize_uint32(buf[56:60])/1000.0
        self.MD_apparent_power_TOD6 = serialize.deserialize_uint32(buf[60:64])/1000.0
        self.MD_apparent_power_TOD7 = serialize.deserialize_uint32(buf[64:68])/1000.0
        self.MD_apparent_power_TOD8 = serialize.deserialize_uint32(buf[68:72])/1000.0
                
