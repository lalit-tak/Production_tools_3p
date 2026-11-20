import datetime
import gp_node.utils.serialize as serialize

#from gp_node.utils.serialize import deserialize_uint16
#from gp_node.utils.serialize import deserialize_uint8
#from gp_node.utils.serialize import deserialize_int8
#from gp_node.utils.serialize import deserialize_uint32

#from gp_node.utils.serialize import deserialize_uint8
#from gp_node.utils.serialize import deserialize_uint16
#from gp_node.utils.serialize import deserialize_uint32


class LoadSurveyPacket3P(object):

    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        dt = datetime.datetime(1970, 1, 1)
        self.return_params = {"date_time":dt,
                "r_phase_voltage":0.00,"y_phase_voltage":0.00,
                "b_phase_voltage":0.00,"r_phase_current":0.000,
                "y_phase_current":0.000,"b_phase_current":0.000,
                "active_energy":0.00,"lag_only_reactive_energy":0.00,
                "lead_only_reactive_energy":0.00,
                "total_apparent_energy":0.00}
        self.daily_profile = {"date_time":dt,
                "real_energy":0.00,"lag_only_reactive_energy":0.00,
                "lead_only_reactive_energy":0.00,
                "total_apparent_energy":0.00}

    def __str__(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("Date & Time     : {}  \n"
                "R phase voltage : {} V\n"
                "Y phase voltage : {} V\n"
                "B phase voltage : {} V\n"
                "R phase current : {} A\n"
                "Y phase current : {} A\n"
                "B phase current : {} A\n"
                "Block Active Energy : {} Kwh\n"
                "Block Lag only Reactive Energy : {} KVARh\n"
                "Block Lead only Reactive Energy : {} KVARh\n"
                "Total Apparent Energy: {} KVAh")\
                .format(self.return_params["date_time"],
                        self.return_params["r_phase_voltage"],
                        self.return_params["y_phase_voltage"],
                        self.return_params["b_phase_voltage"],
                        self.return_params["r_phase_current"],
                        self.return_params["y_phase_current"],
                        self.return_params["b_phase_current"],
                        self.return_params["active_energy"],
                        self.return_params["lag_only_reactive_energy"],
                        self.return_params["lead_only_reactive_energy"],
                        self.return_params["total_apparent_energy"])

    def deserialize(self,payload):
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

        self.return_params["r_phase_voltage"]= ((bytes[4]<<24) +(bytes[5]<<16) + (bytes[6]<<8) + bytes[7])/1000.0
        self.return_params["y_phase_voltage"]= ((bytes[8]<<24) +(bytes[9]<<16) + (bytes[10]<<8) + bytes[11])/1000.0
        self.return_params["b_phase_voltage"]= ((bytes[12]<<24) +(bytes[13]<<16) + (bytes[14]<<8) + bytes[15])/1000.0
        self.return_params["r_phase_current"]= ((bytes[16]<<24) +(bytes[17]<<16) + (bytes[18]<<8) + bytes[19])/1000.0
        self.return_params["y_phase_current"]= ((bytes[20]<<24) +(bytes[21]<<16) + (bytes[22]<<8) + bytes[23])/1000.0
        self.return_params["b_phase_current"]= ((bytes[24]<<24) +(bytes[25]<<16) + (bytes[26]<<8) + bytes[27])/1000.0
        self.return_params["active_energy"] = ((bytes[28]<<24) +(bytes[29]<<16) + (bytes[30]<<8) + bytes[31])/100.0
        self.return_params["lag_only_reactive_energy"] = ((bytes[32]<<24) +(bytes[33]<<16) + (bytes[34]<<8) + bytes[35])/100.0
        self.return_params["lead_only_reactive_energy"] = ((bytes[36]<<24) +(bytes[37]<<16) + (bytes[38]<<8) + bytes[39])/100.0
        self.return_params["total_apparent_energy"] = ((bytes[40]<<24) +(bytes[41]<<16) + (bytes[42]<<8) + bytes[43])/100.0


    def deserialize_daily_profile(self,payload):
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
        self.daily_profile["date_time"] = dt
        self.daily_profile["real_energy"] = ((bytes[4]<<24) +(bytes[5]<<16) + (bytes[6]<<8) + bytes[7])/100.0
        self.daily_profile["lag_only_reactive_energy"] = ((bytes[8]<<24) +(bytes[9]<<16) + (bytes[10]<<8) + bytes[11])/100.0
        self.daily_profile["lead_only_reactive_energy"] = ((bytes[12]<<24) +(bytes[13]<<16) + (bytes[14]<<8) + bytes[15])/100.0
        self.daily_profile["total_apparent_energy"] = ((bytes[16]<<24) +(bytes[17]<<16) + (bytes[18]<<8) + bytes[19])/100.0


    def get_daily_profile_packet(self):
        return ("Date & Time                : {}  \n"
                "Real Energy                : {} Kwh\n"
                "Lag only Reactive Energy   : {} KVARh\n"
                "Lead only Reactive Energy  : {} KVARh\n"
                "Apparent Energy            : {} KVAh")\
                .format(self.daily_profile["date_time"],
                        self.daily_profile["real_energy"],
                        self.daily_profile["lag_only_reactive_energy"],
                        self.daily_profile["lead_only_reactive_energy"],
                        self.daily_profile["total_apparent_energy"])


    def serialize(self, payload):
        print ("not implemented")

    def get_data_dictionary(self):
        """
        Returns the dictionary used to store the ecop data
        """
        return self.return_params