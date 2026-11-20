import datetime
import gp_node.utils.serialize as serialize
import ctypes

#from gp_node.utils.serialize import deserialize_uint16
#from gp_node.utils.serialize import deserialize_uint8
#from gp_node.utils.serialize import deserialize_int8
#from gp_node.utils.serialize import deserialize_uint32

#from gp_node.utils.serialize import deserialize_uint8
#from gp_node.utils.serialize import deserialize_uint16
#from gp_node.utils.serialize import deserialize_uint32


class EventRecordPacket3P(object):
    VALID_EVENT_NAMES = {   0 :'EVT_NONE',
                            #Table 32 in IS15959
                            1  : 'EVT_R_PHASE_MISSING_OCCURRENCE',
                            2  : 'EVT_R_PHASE_MISSING_RESTORATION',
                            3  : 'EVT_Y_PHASE_MISSING_OCCURRENCE',
                            4  : 'EVT_Y_PHASE_MISSING_RESTORATION',
                            5  : 'EVT_B_PHASE_MISSING_OCCURRENCE',
                            6  : 'EVT_B_PHASE_MISSING_RESTORATION',
                            7  : 'EVT_OVER_VOLTAGE_OCCUENCE',
                            8  : 'EVT_OVER_VOLTAGE_RESTORATION',
                            9  : 'EVT_LOW_VOLTAGE_OCCURENCE',
                            10 : 'EVT_LOW_VOLTAGE_RESTORATION',
                            11 : 'EVT_VOLTAGE_UNBALANCE_OCCURENCE',
                            12 : 'EVT_VOLTAGE_UNBALANCE_RESTORATION',
                            13 : 'EVT_PHASE_SEQUENCE_REVERSE_OCCURENCE',
                            14 : 'EVT_PHASE_SEQUENCE_REVERSE_RESTORATION',
                            #Table 33 in IS15959
                            51 :'EVT_R_PHASE_REVERSE_OCCURENCE',
                            52 :'EVT_R_PHASE_REVERSE_RESTORATION',
                            53 :'EVT_Y_PHASE_REVERSE_OCCURENCE',
                            54 :'EVT_Y_PHASE_REVERSE_RESTORATION',
                            55 :'EVT_B_PHASE_REVERSE_OCCURENCE',
                            56 :'EVT_B_PHASE_REVERSE_RESTORATION',
                            57 :'EVT_R_PHASE_CT_OPEN_OCCURENCE',
                            58 :'EVT_R_PHASE_CT_OPEN_RESTORATION',
                            59 :'EVT_Y_PHASE_CT_OPEN_OCCURENCE',
                            60 :'EVT_Y_PHASE_CT_OPEN_RESTORATION',
                            61 :'EVT_B_PHASE_CT_OPEN_OCCURENCE',
                            62 :'EVT_B_PHASE_CT_OPEN_RESTORATION',
                            63 :'EVT_CURRENT_UNBALANCE_OCCURENCE',
                            64 :'EVT_CURRENT_UNBALANCE_RESTORATION',
                            65 :'EVT_CURRENT_BYPASS_OCCURRENCE',
                            66 :'EVT_CURRENT_BYPASS_RESTORATION',
                            67 :'EVT_OVER_CURRENT_OCCURENCE',
                            68 :'EVT_OVER_CURRENT_RESTORATION',
                            71 :'EVT_HIGH_NEUTRAL_CURRENT_OCCURENCE',
                            72 :'EVT_HIGH_NEUTRAL_CURRENT_RESTORATION',
                            #Table 34 in IS15959
                            101:'EVT_POWER_FAILURES_OCCURENCE',
                            102:'EVT_POWER_FAILURES_RESTORATION',
                            #Table 36 in IS15959
                            151:'EVT_RTC',
                            152:'EVT_DEMAND_INTEGRATION_PERIOD',
                            153:'EVT_PROFILE_CAPTURE_PERIOD',
                            154:'EVT_SA_BILLING_SCHEULE',
                            155:'EVT_ACTIVE_CALENDER_TZ',
                            156:'EVT_RS485_DEVICE_ADDRESS',
                            #Table 36 in IS15959
                            201:'EVT_MAGNETIC_TAMPER_OCCURENCE',
                            202:'EVT_MAGNETIC_TAMPER_RESTORATION',
                            203:'EVT_NEUTRAL_DISTURBANCE_OCCURENCE',
                            204:'EVT_NEUTRAL_DISTURBANCE_RESTORATION',
                            205:'EVT_LOW_PF_OCCURENCE',
                            206:'EVT_LOW_PF_RESTORATION',
                            209:'EVT_PLUG_OUT_MODULE',
                            210:'EVT_PLUG_IN_MODULE',
                            #Table 37 in IS15959
                            251:'EVT_METER_COVER_OPEN',
                            #Table 38 in IS15959
                            301:'EVT_METER_LOAD_DISCONENNECTED',
                            302:'EVT_METER_LOAD_CONENNECTED',
                            # Invalid Event for errors
                            512:'INVALID_EVT'}

    
    
    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        dt = datetime.datetime(1970, 1, 1)
        self.return_params = {"event":0,"event_id":0,"date_time":dt,
                "r_phase_voltage":0.00,"y_phase_voltage":0.00,
                "b_phase_voltage":0.00,"r_phase_current":0.00,
                "y_phase_current":0.00,"b_phase_current":0.00,
                "nuetral_current":0.0,"r_phase_pf":0.0,"y_phase_pf":0.0,
                "b_phase_pf":0.0,"total_real_energy":0.00}

    def __str__(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("Event             : {}  \n"
                "Event ID          : {}  \n"
                "Date & Time       : {}  \n"
                "R phase voltage   : {} V\n"
                "Y phase voltage   : {} V\n"
                "B phase voltage   : {} V\n"
                "R phase current   : {} A\n"
                "Y phase current   : {} A\n"
                "B phase current   : {} A\n"
                "Nuetral current   : {} A\n"
                "R phase pf        : {} \n"
                "Y phase pf        : {} \n"
                "B phase pf        : {} \n"
                "Total Real Energy : {}kWh\n")\
                .format(self.return_params["event"],
                        self.return_params["event_id"],
                        self.return_params["date_time"],
                        self.return_params["r_phase_voltage"],
                        self.return_params["y_phase_voltage"],
                        self.return_params["b_phase_voltage"],
                        self.return_params["r_phase_current"],
                        self.return_params["y_phase_current"],
                        self.return_params["b_phase_current"],
                        self.return_params["nuetral_current"],
                        self.return_params["r_phase_pf"],
                        self.return_params["y_phase_pf"],
                        self.return_params["b_phase_pf"],
                        self.return_params["total_real_energy"])

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
                    datetime.timedelta(seconds=((bytes[2]<<24) +\
                    (bytes[3]<<16) + (bytes[4]<<8) + bytes[5]))
        self.return_params["date_time"] = dt
        index = ((bytes[1]<<8) +bytes[0])
        try:
            self.return_params["event"] = self.VALID_EVENT_NAMES[index]
            self.return_params["event_id"] = index
        except:
            self.return_params["event_code"] = self.VALID_EVENT_NAMES[512]
            self.return_params["event_id"] = 512

        self.return_params["r_phase_current"]= ((bytes[6]<<24) +(bytes[7]<<16) + (bytes[8]<<8) + bytes[9])/1000.0
        self.return_params["y_phase_current"]= ((bytes[10]<<24) +(bytes[11]<<16) + (bytes[12]<<8) + bytes[13])/1000.0
        self.return_params["b_phase_current"]= ((bytes[14]<<24) +(bytes[15]<<16) + (bytes[16]<<8) + bytes[17])/1000.0
        self.return_params["nuetral_current"]= ((bytes[18]<<24) +(bytes[19]<<16) + (bytes[20]<<8) + bytes[21])/1000.0
        self.return_params["r_phase_voltage"]= ((bytes[22]<<24) +(bytes[23]<<16) + (bytes[24]<<8) + bytes[25])/1000.0
        self.return_params["y_phase_voltage"]= ((bytes[26]<<24) +(bytes[27]<<16) + (bytes[28]<<8) + bytes[29])/1000.0
        self.return_params["b_phase_voltage"]= ((bytes[30]<<24) +(bytes[31]<<16) + (bytes[32]<<8) + bytes[33])/1000.0

        short_int = ctypes.c_short((bytes[34]<<8) +bytes[35])
        temp =  short_int.value/10000.0
        self.return_params["r_phase_pf"] = temp
        short_int = ctypes.c_short((bytes[36]<<8) +bytes[37])
        temp =  short_int.value/10000.0
        self.return_params["y_phase_pf"] = temp
        short_int = ctypes.c_short((bytes[38]<<8) +bytes[39])
        temp =  short_int.value/10000.0
        self.return_params["b_phase_pf"] = temp
        self.return_params["total_real_energy"] = ((bytes[40]<<24) +(bytes[41]<<16) + (bytes[42]<<8) + bytes[43])/100.0
       
    def serialize(self, payload):
        print ("not implemented")

    def get_data_dictionary(self):
        """
        Returns the dictionary used to store the ecop data
        """
        return self.return_params

class EventRecordNumber3P(object):
    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        self.return_params = {
                "voltage_events":0,"current_events":0,
                "power_events":0,"transactoin_events":0,
                "no_rolover_event":0,"control_event":0,
                "other_event":0, "total_events":0}

    def __str__(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return ("No of Voltage Related Events        :{}\n"
                "No of Current Related Events        :{}\n"
                "No of Power Related Events          :{}\n"
                "No of Transaction Realted Events    :{}\n"
                "No of Non Rolover Related Events    :{}\n"
                "No of Control Related Events        :{}\n"
                "No of Other Events                  :{}\n"
                "Total No of Events                  :{}\n")\
                .format(self.return_params["voltage_events"],
                        self.return_params["current_events"],
                        self.return_params["power_events"],
                        self.return_params["transactoin_events"],
                        self.return_params["no_rolover_event"],
                        self.return_params["control_event"],
                        self.return_params["other_event"],
                        self.return_params["total_events"])

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
        self.return_params["voltage_events"]= ((bytes[0]<<24) +(bytes[1]<<16) + (bytes[2]<<8) + bytes[3])
        self.return_params["current_events"]= ((bytes[4]<<24) +(bytes[5]<<16) + (bytes[6]<<8) + bytes[7])
        self.return_params["power_events"]= ((bytes[8]<<24) +(bytes[9]<<16) + (bytes[10]<<8) + bytes[11])
        self.return_params["transactoin_events"]= ((bytes[12]<<24) +(bytes[13]<<16) + (bytes[14]<<8) + bytes[15])
        self.return_params["no_rolover_event"]= ((bytes[16]<<24) +(bytes[17]<<16) + (bytes[18]<<8) + bytes[19])
        self.return_params["control_event"]= ((bytes[20]<<24) +(bytes[21]<<16) + (bytes[22]<<8) + bytes[23])
        self.return_params["other_event"]= ((bytes[24]<<24) +(bytes[25]<<16) + (bytes[26]<<8) + bytes[27])
        self.return_params["total_events"] =self.return_params["voltage_events"]+self.return_params["current_events"]+\
                        self.return_params["power_events"]+self.return_params["transactoin_events"]+\
                        self.return_params["no_rolover_event"]+ self.return_params["control_event"]+\
                        self.return_params["other_event"]
        
       
    def serialize(self, payload):
        print ("not implemented")

    def get_data_dictionary(self):
        """
        Returns the dictionary used to store the ecop data
        """
        return self.return_params
