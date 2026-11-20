import datetime
import gp_node.utils.serialize as serialize
import time
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils.serialize import deserialize_uint32
from .tamper_flag_3p import TamperFlag_3P

class MeteringDataParamsBundle3P(object):

    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        dt = datetime.datetime(1970, 1, 1)
        tamper_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.return_params = {"date_time":dt,
                "serial_number":000000,
                "r_phase_voltage":0.00,"y_phase_voltage":0.00,
                "b_phase_voltage":0.00,"r_phase_current":0.000,
                "y_phase_current":0.000,"b_phase_current":0.000,
                "r_phase_pf":0.00,"y_phase_pf":0.00,"b_phase_pf":0.00,
                "total_pf":0.00,"total_real_energy ":0.000, "total_apparent_energy ":0.000,
                "total_real_power ":0.000,"total_apparent_power ": 0.000,
                "tamper_index":0,"tamper_time_stamp":tamper_time,"tamper_flags":[],"frequency":0,"neutral_current":0.00,
                "reactive_power":0.00,"reactive_energy":0.00,"tamper_count":0.00, "data_valid":0}

    def __str__(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("date & time     : {}  \n"
                "Serial number   : {}  \n"
                "R phase voltage : {} V\n"
                "Y phase voltage : {} V\n"
                "B phase voltage : {} V\n"
                "R phase current : {} A\n"
                "Y phase current : {} A\n"
                "B phase current : {} A\n"
                "R phase PF : {}\n"
                "Y phase PF : {}\n"
                "B phase PF : {}\n"
                "TotalPf : {}\n"
                "Total Real Energy     : {} KWH\n"
                "Total Apparent Energy : {} KVAH\n"
                "Total Real Power      : {} KW\n"
                "Total Apparent Power  : {} KVA\n"   
                "Tamper Time stamp : {}\n"
                "Frequency : {} Hz\n"
                "Neutral current : {}\n"
                "Reactive power : {}\n"
                "Reactive energy : {}\n"
                "Tamper count : {}\n"
                "Data Valid  : {}")\
                .format(self.return_params["serial_number"],
                        self.return_params["date_time"],
                        self.return_params["r_phase_voltage"],
                        self.return_params["y_phase_voltage"],
                        self.return_params["b_phase_voltage"],
                        self.return_params["r_phase_current"],
                        self.return_params["y_phase_current"],
                        self.return_params["b_phase_current"],
                        self.return_params["r_phase_pf"],
                        self.return_params["y_phase_pf"],
                        self.return_params["b_phase_pf"],
                        self.return_params["total_pf"],
                        self.return_params["total_real_energy"],
                        self.return_params["total_apparent_energy"],
                        self.return_params["total_real_power"],
                        self.return_params["total_apparent_power"],                       
                        self.return_params["tamper_time_stamp"],
                        self.return_params["frequency"],
                        self.return_params["neutral_current"],
                        self.return_params["reactive_power"],
                        self.return_params["reactive_energy"],
                        self.return_params["tamper_count"],
                        self.return_params["data_valid"])

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
        dt = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[0]<<24) +\
                    (bytes[1]<<16) + (bytes[2]<<8) + bytes[3]))
        self.return_params["date_time"] = dt
        self.return_params["serial_number"] = (bytes[4]<<24) + (bytes[5]<<16) + (bytes[6]<<8) + bytes[7]
        self.return_params["r_phase_voltage"]= ((bytes[8]<<8) + bytes[9])/10.0 
        self.return_params["y_phase_voltage"]= ((bytes[10]<<8) + bytes[11])/10.0
        self.return_params["b_phase_voltage"]= ((bytes[12]<<8) + bytes[13])/10.0
        self.return_params["r_phase_current"]= ((bytes[14]<<8) + bytes[15])/100.0 
        self.return_params["y_phase_current"]= ((bytes[16]<<8) + bytes[17])/100.0 
        self.return_params["b_phase_current"]= ((bytes[18]<<8) + bytes[19])/100.0 
        self.return_params["r_phase_pf"]= (serialize.deserialize_int16(bytes[20:22]))/10000.0
        self.return_params["y_phase_pf"]= (serialize.deserialize_int16(bytes[22:24]))/10000.0
        self.return_params["b_phase_pf"]= (serialize.deserialize_int16(bytes[24:26]))/10000.0
        self.return_params["TotalPf"]= ((bytes[26]<<8) + bytes[27])/10000.0 
        self.return_params["frequency"] = ((bytes[28]<<8) + bytes[29])/100.00
        self.return_params["neutral_current"] = ((bytes[30]<<8) + bytes[31])/100.00
        self.return_params["total_real_energy"] = ((bytes[32]<<24) +(bytes[33]<<16) + (bytes[34]<<8) + bytes[35])/100.0
        self.return_params["total_apparent_energy"]= ((bytes[36]<<24) +(bytes[37]<<16) + (bytes[38]<<8) + bytes[39])/100.0
        self.return_params["total_real_power"]= ((bytes[40]<<24) +(bytes[41]<<16) + (bytes[42]<<8) + bytes[43])/1000.0
        self.return_params["total_apparent_power"]= ((bytes[44]<<24) +(bytes[45]<<16) + (bytes[46]<<8) + bytes[47])/1000.0
        tamper_tmp = (bytes[48]<<24) +(bytes[49]<<16) + (bytes[50]<<8) + bytes[51]
        self.return_params["tamper_time_stamp"] = tamper_tmp
        self.return_params["reactive_power"]= (serialize.deserialize_int32(bytes[52:56]))/1000.0
        self.return_params["reactive_energy"] = ((bytes[56]<<24) +(bytes[57]<<16) + (bytes[58]<<8) + bytes[59])/100.0
        self.return_params["tamper_count"] = ((bytes[60]<<8) + bytes[61])
        self.return_params["data_valid"] = ((bytes[62]<<8) + bytes[63])
        if(int(self.return_params["data_valid"])!= 0):
            self.return_params["data_valid"] = "DATA_VALID"
        else:
            self.return_params["data_valid"] = "DATA_INVALID"

        tampers = []
        if ((tamper_tmp/2**0 % 2) == 1):
            tampers.append(TamperFlag_3P("LOW_VOLTAGE"))
        if ((tamper_tmp/2**1 % 2) == 1):
            tampers.append(TamperFlag_3P("LOAD_CONNECTED"))
        if ((tamper_tmp/2**2 % 2) == 1):
           tampers.append(TamperFlag_3P("LOAD_DISCONNECTED"))
        if ((tamper_tmp/2**3 % 2) == 1):
            tampers.append(TamperFlag_3P("OVER_VOLTAGE"))
        if ((tamper_tmp/2**4 % 2) == 1):
            tampers.append(TamperFlag_3P("COVER_OPEN"))
        if ((tamper_tmp/2**5 % 2) == 1):
            tampers.append(TamperFlag_3P("POWER_FAILURE_RESTORATION"))
        if ((tamper_tmp/2**6 % 2) == 1):
            tampers.append(TamperFlag_3P("OVER_CURRENT"))
        if ((tamper_tmp/2**7 % 2) == 1):
            tampers.append("UNKNOWN-1")
        if ((tamper_tmp/2**8 % 2) == 1):
            tampers.append("UNKNOWN-2")
        if ((tamper_tmp/2**9 % 2) == 1):
            tampers.append(TamperFlag_3P("LOW_PF"))
        if ((tamper_tmp/2**10 % 2) == 1):
            tampers.append(TamperFlag_3P("EVT_RTC"))
        if ((tamper_tmp/2**11 % 2) == 1):
            tampers.append(TamperFlag_3P("EVT_DEMAND_INTEGRATION_PERIOD"))
        if ((tamper_tmp/2**12 % 2) == 1):
            tampers.append(TamperFlag_3P("EVT_PROFILE_CAPTURE_PERIOD"))
        if ((tamper_tmp/2**13 % 2) == 1):
            tampers.append(TamperFlag_3P("EVT_SA_BILLING_SCHEULE"))
        if ((tamper_tmp/2**14 % 2) == 1):
            tampers.append(TamperFlag_3P("EVT_ACTIVE_CALENDER_TZ"))
        if ((tamper_tmp/2**15 % 2) == 1):
            tampers.append(TamperFlag_3P("EVT_RS485_DEVICE_ADDRESS"))

        if ((tamper_tmp/2**16 % 2) == 1):
            tampers.append(TamperFlag_3P("R_PHASE_MISSING"))
        if ((tamper_tmp/2**17 % 2) == 1):
            tampers.append(TamperFlag_3P("Y_PHASE_MISSING"))
        if ((tamper_tmp/2**18 % 2) == 1):
           tampers.append(TamperFlag_3P("B_PHASE_MISSING"))
        if ((tamper_tmp/2**19 % 2) == 1):
            tampers.append(TamperFlag_3P("CURRENT_BYPASS"))
        if ((tamper_tmp/2**20 % 2) == 1):
            tampers.append(TamperFlag_3P("R_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**21 % 2) == 1):
            tampers.append(TamperFlag_3P("Y_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**22 % 2) == 1):
            tampers.append(TamperFlag_3P("B_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**23 % 2) == 1):
            tampers.append(TamperFlag_3P("MAGNETIC"))
        if ((tamper_tmp/2**24 % 2) == 1):
            tampers.append(TamperFlag_3P("R_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**25 % 2) == 1):
            tampers.append(TamperFlag_3P("Y_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**26 % 2) == 1):
            tampers.append(TamperFlag_3P("B_PHASE_CT_OPEN"))
        if ((tamper_tmp/2**27 % 2) == 1):
            tampers.append(TamperFlag_3P("CURRENT_UNBALANCE"))
        if ((tamper_tmp/2**28 % 2) == 1):
            tampers.append(TamperFlag_3P("VOLTAGE_UNBALANCE"))
        if ((tamper_tmp/2**29 % 2) == 1):
            tampers.append(TamperFlag_3P("NEUTRAL_DISTURBANCE"))
        if ((tamper_tmp/2**30 % 2) == 1):
            tampers.append("UNKNOWN-3")
        if ((tamper_tmp/2**31 % 2) == 1):
            tampers.append("UNKNOWN-4")

        self.return_params["tamper_flags"] = tampers
        


    def get_packet_bundle(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        _3p_bundle = {}
        _3p_bundle['date_time']            =    self.return_params["date_time"]
        _3p_bundle['serial_number']        =    self.return_params["serial_number"]
        _3p_bundle['r_phase_voltage']      =    self.return_params["r_phase_voltage"]
        _3p_bundle['y_phase_voltage']      =    self.return_params["y_phase_voltage"]
        _3p_bundle['b_phase_voltage']      =    self.return_params["b_phase_voltage"]
        _3p_bundle['r_phase_current']      =    self.return_params["r_phase_current"]
        _3p_bundle['y_phase_current']      =    self.return_params["y_phase_current"]
        _3p_bundle['b_phase_current']      =    self.return_params["b_phase_current"]
        _3p_bundle['r_phase_pf']           =    self.return_params["r_phase_pf"]
        _3p_bundle['y_phase_pf']           =    self.return_params["y_phase_pf"]
        _3p_bundle['b_phase_pf']           =    self.return_params["b_phase_pf"]
        _3p_bundle['total_pf']             =    self.return_params["TotalPf"]
        _3p_bundle['total_real_energy']    =    self.return_params["total_real_energy"]
        _3p_bundle['total_apparent_energy']=    self.return_params["total_apparent_energy"]
        _3p_bundle['total_real_power']     =    self.return_params["total_real_power"]
        _3p_bundle['total_apparent_power'] =    self.return_params["total_apparent_power"]
        _3p_bundle['tamper_int_d']         =    self.return_params["tamper_time_stamp"]
        _3p_bundle['tampers']              =    self.return_params["tamper_flags"]
        _3p_bundle['frequency']            =    self.return_params["frequency"]
        _3p_bundle['neutral_current']      =    self.return_params["neutral_current"]
        _3p_bundle['reactive_power']       =    self.return_params["reactive_power"]
        _3p_bundle['reactive_energy']      =    self.return_params["reactive_energy"]
        _3p_bundle['tamper_count']         =    self.return_params["tamper_count"]
        _3p_bundle['data_valid']           =    self.return_params["data_valid"]

        #print _3p_bundle
        return _3p_bundle

    def get_packet_bundle_string(self, _3p_bundle):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("Date & Time           : {}  \n"
                "Serial number         : {}  \n"
                "R phase voltage       : {} V\n"
                "Y phase voltage       : {} V\n"
                "B phase voltage       : {} V\n"
                "R phase current       : {} A\n"
                "Y phase current       : {} A\n"
                "B phase current       : {} A\n"
                "R phase PF            : {}\n"
                "Y phase PF            : {}\n"
                "B phase PF            : {}\n"
                "TotalPf               : {}\n"
                "Total Real Energy     : {} KWH\n"
                "Total Apparent Energy : {} KVAH\n"
                "Total Real Power      : {} W\n"
                "Total Apparent Power  : {} VA\n"   
                "Tamper intiger        : {}\n"
                "Tamper                : {}\n"
                "Frequency             : {} Hz\n"
                "Neutral current       : {}\n"
                "Reactive power        : {}\n"
                "Reactive energy       : {}\n"
                "Tamper count          : {}\n"
                "Data Valid            : {}\n")\
                .format(_3p_bundle['date_time'],
                        _3p_bundle['serial_number'],        
                        _3p_bundle['r_phase_voltage'],      
                        _3p_bundle['y_phase_voltage'],      
                        _3p_bundle['b_phase_voltage'],      
                        _3p_bundle['r_phase_current'],      
                        _3p_bundle['y_phase_current'],      
                        _3p_bundle['b_phase_current'],      
                        _3p_bundle['r_phase_pf'],           
                        _3p_bundle['y_phase_pf'],           
                        _3p_bundle['b_phase_pf'],           
                        _3p_bundle['total_pf'],             
                        _3p_bundle['total_real_energy'],    
                        _3p_bundle['total_apparent_energy'],
                        _3p_bundle['total_real_power'],     
                        _3p_bundle['total_apparent_power'], 
                        _3p_bundle['tamper_int_d'],         
                        _3p_bundle['tampers'],              
                        _3p_bundle['frequency'],            
                        _3p_bundle['neutral_current'],      
                        _3p_bundle['reactive_power'],       
                        _3p_bundle['reactive_energy'],      
                        _3p_bundle['tamper_count'],
                        _3p_bundle['data_valid'])

                