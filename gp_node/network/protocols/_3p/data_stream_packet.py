import datetime
import gp_node.utils.serialize as serialize

#from tamper_flag_3p  import TamperFlag_3P
#from gp_node.network.protocols.three_ph_phase.tamper_flag_3p import TamperFlag_3P

#from gp_node.utils.serialize import deserialize_uint16
#from gp_node.utils.serialize import deserialize_uint8
#from gp_node.utils.serialize import deserialize_int8
#from gp_node.utils.serialize import deserialize_uint32

#from gp_node.utils.serialize import deserialize_uint8
#from gp_node.utils.serialize import deserialize_uint16
#from gp_node.utils.serialize import deserialize_uint32


class DataStreamPacket3P(object):
    """
    The EcopDataStreamPacket is container to deserialize,temporarly store
    and exchange data.The data is stored in dictionary format.The data is
    populated using the deserialize API.
    """
    CURRENT_BYPASS_TAMPER = 0x01
    R_PHASE_MISSING_TAMPER = 0x02
    Y_PHASE_MISSING_TAMPER = 0x04
    B_PHASE_MISSING_TAMPER = 0x08
    REVERSE_CURRENT_TAMPER = 0x10
    MAGNET_TAMPER  = 0x20
    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        dt = datetime.datetime(1970, 1, 1)
        self.return_params = {"date_time":dt,
                "serial_number":000000,
                "r_phase_voltage":0.00,"y_phase_voltage":0.00,
                "b_phase_voltage":0.00,"r_phase_current":0.000,
                "y_phase_current":0.000,"b_phase_current":0.000,
                "r_phase_pf":0.00,"y_phase_pf":0.00,"b_phase_pf":0.00,
                "tamper_info":0, "timeout":True}

    def __str__(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("Serial number   : {}  \n"
                "date & time     : {}  \n"
                "R phase voltage : {} V\n"
                "Y phase voltage : {} V\n"
                "B phase voltage : {} V\n"
                "R phase current : {} A\n"
                "Y phase current : {} A\n"
                "B phase current : {} A\n"
                "R phase PF : {}\n"
                "Y phase PF : {}\n"
                "B phase PF : {}\n"
                "tampers : {}")\
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
                        self.return_params["tamper_info"])

    def get_packet_ip(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("Serial number   : {}  \n"
                "date & time     : {}  \n"
                "R phase voltage : {} V\n"
                "Y phase voltage : {} V\n"
                "B phase voltage : {} V\n"
                "R phase current : {} A\n"
                "Y phase current : {} A\n"
                "B phase current : {} A\n"
                "R phase PF      : {}\n"
                "Y phase PF      : {}\n"
                "B phase PF      : {}\n"
                "Tampers         : {}\n"
                "Neutral Current : {} A\n")\
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
                        self.return_params["tamper_info"],
                        self.return_params["neutral_current"])

    def get_packet_energy(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("Total Real Energy         : {} KWH\n"
                "Total Apparent Energy     : {} KVAH\n"
                "Total Reactive Energy     : {} KVARH\n"
                "Lag Only Reactive Energy  : {} KVARH\n"
                "Lag Only Appanrent Energy : {} KVA\n"
                "Lead Only Reactive Energy : {} KVARH\n"
                "Lead Only Apparent Energy : {} KVAH\n"
                "Toatal Active Power       : {} KWH\n"
                "Total Apparent Power      : {} KVA\n"
                "Total Reactive Power      : {} KVAR\n"
                "Total Harmonic Power      : {} KW")\
                .format(self.return_params["total_real_energy"],
                        self.return_params["total_apparent_energy"],
                        self.return_params["total_reactive_energy"],
                        self.return_params["lag_only_reactive_energy"],
                        self.return_params["lag_only_apparent_energy"],
                        self.return_params["lead_only_reactive_energy"],
                        self.return_params["lead_only_apparent_energy"],
                        self.return_params["total_active_power"],
                        self.return_params["total_apparent_power"],
                        self.return_params["total_reactive_power"],
                        self.return_params["total_harmonic_power"])

    def deserialize_packet_ip(self,payload):
        """
        Deserializes the input payload and populates the data to the default
        dictionary.This API needs to be used to retrieve information from the 
        reply bytestream.
        :param payload:input bytestream
        :return :none
        """
        bytes = payload
        dt = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[0]<<24) +\
                    (bytes[1]<<16) + (bytes[2]<<8) + bytes[3]))
        self.return_params["date_time"] = dt
        self.return_params["serial_number"] = (bytes[4]<<24) +\
                    (bytes[5]<<16) + (bytes[6]<<8) + bytes[7]

        self.return_params["r_phase_voltage"]= ((bytes[8]<<24) +\
                    (bytes[9]<<16) + (bytes[10]<<8) + bytes[11])/1000.0 
        self.return_params["y_phase_voltage"]= ((bytes[12]<<24) +\
                    (bytes[13]<<16) + (bytes[14]<<8) + bytes[15])/1000.0
        self.return_params["b_phase_voltage"]= ((bytes[16]<<24) +\
                    (bytes[17]<<16) + (bytes[18]<<8) + bytes[19])/1000.0
        self.return_params["r_phase_current"]= ((bytes[20]<<24) +\
                    (bytes[21]<<16) + (bytes[22]<<8) + bytes[23])/1000.0 
        self.return_params["y_phase_current"]= ((bytes[24]<<24) +\
                    (bytes[25]<<16) + (bytes[26]<<8) + bytes[27])/1000.0 
        self.return_params["b_phase_current"]= ((bytes[28]<<24) +\
                    (bytes[29]<<16) + (bytes[30]<<8) + bytes[31])/1000.0 

        self.return_params["r_phase_pf"]= ((bytes[32]<<8) + bytes[33])/10000.0
        self.return_params["y_phase_pf"]= ((bytes[34]<<8) + bytes[35])/10000.0
        self.return_params["b_phase_pf"]= ((bytes[36]<<8) + bytes[37])/10000.0
        '''
        tamper_tmp = ((bytes[38]<<8) + bytes[39])
        if ((tamper_tmp/2**0 % 2) == 1):
                self.return_params["tamper_info"].append(TamperFlag_3P("R_PHASE_MISSING"))
        if ((tamper_tmp/2**1 % 2) == 1):
            self.return_params["tamper_info"].append(TamperFlag_3P("Y_PHASE_MISSING"))
        if ((tamper_tmp/2**2 % 2) == 1):
            self.return_params["tamper_info"].append(TamperFlag_3P("B_PHASE_MISSING"))
        if ((tamper_tmp/2**3 % 2) == 1):
            self.return_params["tamper_info"].append(TamperFlag_3P("CURRENT_BYPASS"))
        if ((tamper_tmp/2**4 % 2) == 1):
            self.return_params["tamper_info"].append(TamperFlag_3P("R_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**5 % 2) == 1):
            self.return_params["tamper_info"].append(TamperFlag_3P("Y_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**6 % 2) == 1):
            self.return_params["tamper_info"].append(TamperFlag_3P("B_PHASE_REVERSE_CURRENT"))
        if ((tamper_tmp/2**7 % 2) == 1):
            self.return_params["tamper_info"].append(TamperFlag_3P("MAGNETIC"))
        '''
        self.return_params["tamper_info"]= ((bytes[38]<<8) + bytes[39])
        self.return_params["neutral_current"] = ((bytes[40]<<24) +\
                    (bytes[41]<<16) + (bytes[42]<<8) + bytes[43])/1000.0 
        self.return_params["timeout"] = False;

    def deserialize_packet_energy(self,payload):
        """
        Deserializes the input payload and populates the data to the default
        dictionary.This API needs to be used to retrieve information from the 
        reply bytestream.
        :param payload:input bytestream
        :return :none
        """
        bytes = payload
        self.return_params["total_real_energy"] = ((bytes[0]<<24) +\
                    (bytes[1]<<16) + (bytes[2]<<8) + bytes[3])/100.0
        self.return_params["total_apparent_energy"] = ((bytes[4]<<24) +\
                    (bytes[5]<<16) + (bytes[6]<<8) + bytes[7])/100.0
        self.return_params["total_reactive_energy"] = ((bytes[8]<<24) +\
                    (bytes[9]<<16) + (bytes[10]<<8) + bytes[11])/100.0 
        self.return_params["lag_only_reactive_energy"]= ((bytes[12]<<24) +\
                    (bytes[13]<<16) + (bytes[14]<<8) + bytes[15])/100.0
        self.return_params["lag_only_apparent_energy"]= ((bytes[16]<<24) +\
                    (bytes[17]<<16) + (bytes[18]<<8) + bytes[19])/100.0
        self.return_params["lead_only_reactive_energy"]= ((bytes[20]<<24) +\
                    (bytes[21]<<16) + (bytes[22]<<8) + bytes[23])/100.0 
        self.return_params["lead_only_apparent_energy"]= ((bytes[24]<<24) +\
                    (bytes[25]<<16) + (bytes[26]<<8) + bytes[27])/100.0 
        self.return_params["total_active_power"]= ((bytes[28]<<24) +\
                    (bytes[29]<<16) + (bytes[30]<<8) + bytes[31])/1000.0 

        self.return_params["total_apparent_power"]= ((bytes[32]<<24) +\
                    (bytes[33]<<16) + (bytes[34]<<8) + bytes[35])/1000.0 
        self.return_params["total_reactive_power"]= ((bytes[36]<<24) +\
                    (bytes[37]<<16) + (bytes[38]<<8) + bytes[39])/1000.0 
        self.return_params["total_harmonic_power"]= ((bytes[40]<<24) +\
                    (bytes[41]<<16) + (bytes[42]<<8) + bytes[43])/1000.0 


    def serialize(self, payload):
        print ("not implemented")

    def get_data_dictionary(self):
        """
        Returns the dictionary used to store the ecop data
        """
        return self.return_params
