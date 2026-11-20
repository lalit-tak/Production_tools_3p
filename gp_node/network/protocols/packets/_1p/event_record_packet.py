import datetime
import time 
import gp_node.utils.serialize as serialize

class EventRecordPacket(object):

    VALID_EVENT_NAMES = {   0 :'EVT_NONE',
                            # Voltage Related
                            1   : 'EVT_R_PHASE_VOLTAGE_MISSING_OCCURRENCE',
                            2   : 'EVT_R_PHASE_VOLTAGE_MISSING_RESTORATION',
                            3   : 'EVT_Y_PHASE_VOLTAGE_MISSING_OCCURRENCE',
                            4   : 'EVT_Y_PHASE_VOLTAGE_MISSING_RESTORATION',
                            5   : 'EVT_B_PHASE_VOLTAGE_MISSING_OCCURRENCE',
                            6   : 'EVT_B_PHASE_VOLTAGE_MISSING_RESTORATION',
                            7   : 'EVT_OVER_VOLTAGE_OCCURRENCE',
                            8   : 'EVT_OVER_VOLTAGE_RESTORATION',
                            9   : 'EVT_LOW_VOLTAGE_OCCURRENCE',
                            10  : 'EVT_LOW_VOLTAGE_RESTORATION',
                            11  : 'EVT_VOLTAGE_UNBALANCE_OCCURRENCE',
                            12  : 'EVT_VOLTAGE_UNBALANCE_RESTORATION',
                            13  : 'EVT_PHASE_SEQUENCE_OCCURRENCE',
                            14  : 'EVT_PHASE_SEQUENCE_RESTORATION',
                            # Current Related
                            51  : 'EVT_R_PHASE_REVERSE_OCCURRENCE',
                            52  : 'EVT_R_PHASE_REVERSE_RESTORATION',
                            53  : 'EVT_Y_PHASE_REVERSE_OCCURRENCE',
                            54  : 'EVT_Y_PHASE_REVERSE_RESTORATION',
                            55  : 'EVT_B_PHASE_REVERSE_OCCURRENCE',
                            56  : 'EVT_B_PHASE_REVERSE_RESTORATION',
                            57  : 'EVT_R_PHASE_CT_OPEN_OCCURRENCE',
                            58  : 'EVT_R_PHASE_CT_OPEN_RESTORATION',
                            59  : 'EVT_Y_PHASE_CT_OPEN_OCCURRENCE',
                            60  : 'EVT_Y_PHASE_CT_OPEN_RESTORATION',
                            61  : 'EVT_B_PHASE_CT_OPEN_OCCURRENCE',
                            62  : 'EVT_B_PHASE_CT_OPEN_RESTORATION',
                            63  : 'EVT_CURRENT_UNBALANCE_OCCURRENCE',
                            64  : 'EVT_CURRENT_UNBALANCE_RESTORATION',
                            65  : 'EVT_CURRENT_BYPASS_OCCURRENCE',
                            66  : 'EVT_CURRENT_BYPASS_RESTORATION',
                            67  : 'EVT_OVER_CURRENT_OCCURRENCE',
                            68  : 'EVT_OVER_CURRENT_RESTORATION',
                            69  : 'EVT_EARTH_LOADING_OCCURRENCE',
                            70  : 'EVT_EARTH_LOADING_RESTORATION',
                            71  : 'EVT_HIGH_NEUTRAL_OCCURRENCE',
                            72  : 'EVT_HIGH_NEUTRAL_RESTORATION',
                            
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
                            161 :'EVT_LLS_MR_KEY_CHANGE',
                            162 :'EVT_HLS_US_KEY_CHANGE',
                            163 :'EVT_HLS_FW_KEY_CHANGE',
                            164 :'EVT_GLOBAL_KEY_CHANGE',
                            165 :'EVT_STATUS_WORD_FLAG_CHANGE', 
                            166 :'EVT_MD_RESET_OCCURENCE',
                            # Other Related
                            201 :'EVT_MAGNETIC_TAMPER_OCCURENCE',
                            202 :'EVT_MAGNETIC_TAMPER_RESTORATION',
                            203 :'EVT_ND_TAMPER_OCCURENCE',
                            204 :'EVT_ND_TAMPER_RESTORATION',
                            205 :'EVT_LOW_PF_OCCURENCE',
                            206 :'EVT_LOW_PF_RESTORATION',
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
                            1001:'ID_RF_DISCONNECTED',
                            1002:'ID_RF_CONNECTED',
                            1003:'ID_RF_GATEWAY',
                            1004:'ID_RF_CONFIG',
                            10008:'EVT_OVER_POWER_OCCURENCE',
                            10009:'EVT_OVER_POWER_RESTORATION',
                            # Invalid Event for errors
                            512:'INVALID_EVT'}

    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the event record data
        """
        full_event_log = 0
        dt = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.return_params = {"event_code":0,"date_time":dt,
                "R_current":0.00,"Y_current":0.00,"B_current":0.00,
                "R_voltage":0.00,"Y_voltage":0.00,"B_voltage":0.00,
                "R_power_factor":0.00,"Y_power_factor":0.00,"B_power_factor":0.00,
                "active_energy_imp":0.00,"active_energy_exp":0.00, "tamper_count" : 0}

    def __str__(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        :param :none
        :return :none
        """
        
        if self.full_event_log > 0 :
            return ("Event Code             : {}\n"
                    "Date & Time            : {}\n"
                    "R-Current              : {} A\n"
                    "Y-Current              : {} A\n"
                    "B-Current              : {} A\n"
                    "R-Voltage              : {} V\n"
                    "Y-Voltage              : {} V\n"
                    "B-Voltage              : {} V\n"
                    "R-PowerFactor          : {}\n"
                    "Y-PowerFactor          : {}\n"
                    "B-PowerFactor          : {}\n"
                    "Active Energy Import   : {} KWh\n"
                    "Active Energy Export   : {} KWh\n"
                    "Tamper Count           : {}\n").format(self.return_params["event_code"],
                                                            self.return_params["date_time"],
                                                            self.return_params["R_current"],
                                                            self.return_params["Y_current"],
                                                            self.return_params["B_current"],
                                                            self.return_params["R_voltage"],
                                                            self.return_params["Y_voltage"],
                                                            self.return_params["B_voltage"],
                                                            self.return_params["R_power_factor"],
                                                            self.return_params["Y_power_factor"],
                                                            self.return_params["B_power_factor"],
                                                            self.return_params["active_energy_imp"],
                                                            self.return_params["active_energy_exp"],
                                                            self.return_params["tamper_count"])
        else :
            return ("Event Code     : {}\n"
                    "Date & Time    : {}\n").format(self.return_params["event_code"],
                                                    self.return_params["date_time"])            


    def deserialize(self,payload):
        """
        Deserializes the input payload and populates the data to the default
        dictionary.This API needs to be used to retrieve information from the 
        reply bytestream.
        :param payload:input bytestream
        :return :none
        """
        bytes = payload
        index = ((bytes[1]<<8) +bytes[0])

        if (index > 0 and index<100) or (index>200 and index<217):
            self.full_event_log = 1
        else :
            self.full_event_log = 0

        try:
            self.return_params["event_code"] = self.VALID_EVENT_NAMES[index]
        except:
            self.return_params["event_code"] = self.VALID_EVENT_NAMES[512]
     
        unix_time       = serialize.deserialize_uint32(bytes[2:6],"reverse")
        unix_time_zero  = datetime.datetime(1970, 1, 1)
        dt              = unix_time_zero + datetime.timedelta(0, unix_time)

        self.return_params["date_time"]         = dt
        if(len(bytes) > 8):
            self.return_params["R_voltage"]         = serialize.deserialize_uint32(bytes[6:10],"reverse")/1000.0
            self.return_params["Y_voltage"]         = serialize.deserialize_uint32(bytes[10:14],"reverse")/1000.0
            self.return_params["B_voltage"]         = serialize.deserialize_uint32(bytes[14:18],"reverse")/1000.0
            self.return_params["R_current"]         = serialize.deserialize_uint32(bytes[18:22],"reverse")/1000.0
            self.return_params["Y_current"]         = serialize.deserialize_uint32(bytes[22:26],"reverse")/1000.0
            self.return_params["B_current"]         = serialize.deserialize_uint32(bytes[26:30],"reverse")/1000.0
            self.return_params["R_power_factor"]    = serialize.deserialize_int32(bytes[30:34],"reverse")/1000.0
            self.return_params["Y_power_factor"]    = serialize.deserialize_int32(bytes[34:38],"reverse")/1000.0 
            self.return_params["B_power_factor"]    = serialize.deserialize_int32(bytes[38:42],"reverse")/1000.0 
            self.return_params["active_energy_imp"] = serialize.deserialize_uint32(bytes[42:46],"reverse")/100.0 
            self.return_params["active_energy_exp"] = serialize.deserialize_uint32(bytes[46:50],"reverse")/100.0
            self.return_params["tamper_count"]      = serialize.deserialize_uint32(bytes[50:54],"reverse")

    def serialize(self, payload):
        print ("not implemented")

    def get_data_dictionary(self):
        """
        Returns the dictionary used to store the ecop data
        """
        return self.return_params

    # def deserializex(self,payload):
    #     """
    #     Deserializes the input payload.This API needs to be used to retrieve information from the 
    #     reply bytestream.
    #     :param payload:input bytestream
    #     :return :none
    #     """
    #     buf = payload

    #     index=0
    #     length = len(buf)

    #     if(length ==0):
    #         return "No entry found !!!"

    #     while length > 0:
    #         evtId = buf[index]

    #         unix_time = ((buf[index+4]<<24)+(buf[index+3]<<16)+(buf[index+2]<<8) +buf[index+1])
    #         unix_time_zero = datetime.datetime(1970, 1, 1)
    #         dt = unix_time_zero + datetime.timedelta(0, unix_time)

    #         print "Index : "+str(index/5)+"    Event : "+self.VALID_EVENT_NAMES[evtId]+"    TimeStamp : "+str(dt)
    #         index+=5
    #         length-=5
    #     return "Log fetch done !!!"
        

class EventRecordNumber(object):
    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        self.return_params = {
                "current_events":0,"voltage_events":0,"power_events":0,
                "transactions_events":0,"other_events":0,
                "non_rollover_events":0,"control_events":0,
                "RF_events":0, "total_events":0}

    def __str__(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        :param :none
        :return :none
        """
        return ("\nNo. of current related events     : {}\n"
                "No. of voltage related Events       : {}\n"
                "No. of power related Events         : {}\n"
                "No. of transaction related events   : {}\n"
                "No. of non rollover events          : {}\n"
                "No. of control related events       : {}\n"
                "No. of other events                 : {}\n"
                "No. of RF related events            : {}\n"
                "Total no. of events                 : {}\n").format(self.return_params["current_events"],
                                                                        self.return_params["voltage_events"],
                                                                        self.return_params["power_events"],
                                                                        self.return_params["transactions_events"],
                                                                        self.return_params["non_rollover_events"],
                                                                        self.return_params["control_events"],
                                                                        self.return_params["other_events"],
                                                                        self.return_params["RF_events"],
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
        #print time.asctime(time.localtime(time.time()))
        self.return_params["current_events"]        = serialize.deserialize_uint32(bytes[0:4])
        self.return_params["voltage_events"]        = serialize.deserialize_uint32(bytes[4:8])
        self.return_params["power_events"]          = serialize.deserialize_uint32(bytes[8:12])
        self.return_params["transactions_events"]   = serialize.deserialize_uint32(bytes[12:16])
        self.return_params["non_rollover_events"]   = serialize.deserialize_uint32(bytes[16:20])
        self.return_params["control_events"]        = serialize.deserialize_uint32(bytes[20:24])
        self.return_params["other_events"]          = serialize.deserialize_uint32(bytes[24:28])
        if len(payload) > 28:
            self.return_params["RF_events"]         = serialize.deserialize_uint32(bytes[28:32])
        self.return_params["total_events"]          = self.return_params["current_events"]       +\
                                                      self.return_params["voltage_events"]       +\
                                                      self.return_params["power_events"]         +\
                                                      self.return_params["transactions_events"]  +\
                                                      self.return_params["non_rollover_events"]  +\
                                                      self.return_params["control_events"]       +\
                                                      self.return_params["other_events"]         +\
                                                      self.return_params["RF_events"]
        
       
    def serialize(self, payload):
        print ("not implemented")

    def get_data_dictionary(self):
        """
        Returns the dictionary used to store the ecop data
        """
        return self.return_params