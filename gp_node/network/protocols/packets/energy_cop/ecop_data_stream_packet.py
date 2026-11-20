import datetime
import gp_node.utils.serialize as serialize

#from gp_node.utils.serialize import deserialize_uint16
#from gp_node.utils.serialize import deserialize_uint8
#from gp_node.utils.serialize import deserialize_int8
#from gp_node.utils.serialize import deserialize_uint32

#from gp_node.utils.serialize import deserialize_uint8
#from gp_node.utils.serialize import deserialize_uint16
#from gp_node.utils.serialize import deserialize_uint32


class EcopDataStreamPacket(object):
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
        self.return_params = {"serial_number":000000,"active_energy":00000,
                "reactive_energy":000.000,"date_time":dt,
                "r_phase_voltage":0.00,"y_phase_voltage":0.00,
                "b_phase_voltage":0.00,"r_phase_current":0.000,
                "y_phase_current":0.000,"b_phase_current":0.000,
                "r_phase_pf":0.00,"y_phase_pf":0.00,"b_phase_pf":0.00,
                "instaneous_load":0.00000,"tamper_info":[],"timeout":True}

    def __str__(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("Serial number   : {}  \n"
                "Active Energy   : {} KWh\n"
                "Reactive Energy : {} Kvarh\n"
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
                "instaneous load: {} Watts\n"
                "tampers : {}")\
                .format(self.return_params["serial_number"],
                        self.return_params["active_energy"],
                        self.return_params["reactive_energy"],
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
                        self.return_params["instaneous_load"],
                        self.return_params["tamper_info"])

    def deserialize(self,payload):
        """
        Deserializes the input payload and populates the data to the default
        dictionary.This API needs to be used to retrieve information from the 
        reply bytestream.
        :param payload:input bytestream
        :return :none
        """
        bytes = payload
        self.return_params["r_phase_voltage"]= ((bytes[0]<<8) + bytes[1])/100.00
        self.return_params["y_phase_voltage"]= ((bytes[2]<<8) + bytes[3])/100.00
        self.return_params["b_phase_voltage"]= ((bytes[4]<<8) + bytes[5])/100.00
        self.return_params["r_phase_current"]= ((bytes[6]<<8) + bytes[7])/1000.000
        self.return_params["y_phase_current"]= ((bytes[8]<<8) + bytes[9])/1000.000
        self.return_params["b_phase_current"]= ((bytes[10]<<8) + bytes[11])/1000.000
        self.return_params["r_phase_pf"] = float(int(bytes[12]))/100.00
        self.return_params["y_phase_pf"] = float(int(bytes[13]))/100.00
        self.return_params["b_phase_pf"] = float(int(bytes[14]))/100.00
        self.return_params["instaneous_load"] = ((bytes[15]<<24) +\
                    (bytes[16]<<16) + (bytes[17]<<8) + bytes[18]) /1000.00
        self.return_params["serial_number"] = (bytes[19]<<24) +\
                    (bytes[20]<<16) + (bytes[21]<<8) + bytes[22]
        self.return_params["active_energy"] = ((bytes[23]<<24) +\
                    (bytes[24]<<16) + (bytes[25]<<8) + bytes[26])/100.00
        self.return_params["reactive_energy"] = ((bytes[27]<<24) +\
                    (bytes[28]<<16) + (bytes[29]<<8) + bytes[30])/100.00
        dt = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[31]<<24) +\
                    (bytes[32]<<16) + (bytes[33]<<8) + bytes[34]))
        self.return_params["date_time"] = dt

        if(bytes[35] & self.CURRENT_BYPASS_TAMPER):
            self.return_params["tamper_info"].append("CURRENT_BYPASS_TAMPER")
        if(bytes[35] & self.R_PHASE_MISSING_TAMPER):
            self.return_params["tamper_info"].append("R_PHASE_MISSING_TAMPER")
        if(bytes[35] & self.Y_PHASE_MISSING_TAMPER):
            self.return_params["tamper_info"].append("Y_PHASE_MISSING_TAMPER")
        if(bytes[35] & self.B_PHASE_MISSING_TAMPER):
            self.return_params["tamper_info"].append("B_PHASE_MISSING_TAMPER")
        if(bytes[35] & self.REVERSE_CURRENT_TAMPER):
            self.return_params["tamper_info"].append("REVERSE_CURRENT_TAMPER")
        if(bytes[35] & self.MAGNET_TAMPER):
            self.return_params["tamper_info"].append("MAGNET_TAMPER")
        self.return_params["timeout"] = False;


    def serialize(self, payload):
        print ("not implemented")

    def get_data_dictionary(self):
        """
        Returns the dictionary used to store the ecop data
        """
        return self.return_params