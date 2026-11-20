import datetime
import gp_node.utils.serialize as serialize
import time
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils.serialize import deserialize_uint32

class SystemsCommands3P(object):

    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        current_time = datetime.datetime(1970, 1, 1)
        reset_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        billing_date = datetime.datetime(1970, 1, 1, 0, 0, 0)
        W_MD_TS = datetime.datetime(1970, 1, 1, 0, 0, 0)
        VA_MD_TS = datetime.datetime(1970, 1, 1, 0, 0, 0)        
        self.return_params = {"current_time":current_time,
                "reset_time":reset_time,
                "total_power_off_duaration":0.00,"total_power_on_duaration":0.00,
                "over_power_limit":0.00,"relay_control_mode":0.00,"serial_number":0.00,
                "relay_status":0.00,"live version ":0.000,"relay_count":0.00,"occurence":0.00,"restoration":0.00,
                "sip":0.00,"dip":0.00,"no_of_load_surveys":0.00,"no_of_daily_surveys":0.00,
                "no_of_billiing_histories":0.00,"no_of_billing_logs":0.00,"voltage_related_events":0.00,
                "current_related_events":0.00,"power_related_events":0.00,"transaction_related_events":0.00,
                "non_rollover_related_events":0.00,"control_related_events":0.00,"other_related_events":0.00,                        
                "total_no_of_event_entries":0.00,"tc":0.00,"bc":0.00,"pc":0.00,"pfc":0.00,"billing_date":billing_date,
                "md_w":0.00,"md_w_ts":W_MD_TS ,"md_va":0.00,"md_va_ts":VA_MD_TS}

    def __str__(self):

        return ("Serial Number              : {} \n"
                "Live Version               : {} \n"
                "Current date & time        : {} \n"
                "Reset date & time          : {} \n"
                "Total Power Off Duration   : {} Seconds\n"
                "Total Power On Duration    : {} Seconds\n"
                "Over Power limit           : {} Watts\n"
                "Relay Control Mode         : {} \n"
                "Relay Status               : {} \n"
                "Relay Count                : {} \n"
                "Occurence Time             : {} \n"
                "Restoration Time           : {} \n"
                "Survey Interval            : {} \n"
                "No Of Load Surveys         : {} \n"
                "No Of Daily Surveys        : {} \n"
                "Demand Interval            : {} \n"
                "No Of Billing Logs         : {} \n"
                "No Of Billing History      : {} \n"
                "Programming Count          : {} \n"
                "Billing Count              : {} \n"
                "Billing Date               : {} \n"
                "Active MD                  : {} \n"
                "Active MD Time Stamp       : {} \n"
                "Apparent MD                : {} \n"
                "Apparent MD Time Stamp     : {} \n"
                "Voltage Related Events     : {} \n"
                "Current Related Events     : {} \n"
                "Power Related Events       : {} \n"
                "Transaction Related Events : {} \n"
                "Non Rollover Related Events: {} \n"
                "Control Related Events     : {} \n"
                "Other Related Events       : {} \n"
                "Total No Of Event Entries  : {} \n"
                "Tamper Count               : {} \n"
                "Power Failuers Count       : {} \n")\
                .format(self.return_params["serial_number"],
                        self.return_params["live_version"],
                        self.return_params["current_time"],
                        self.return_params["reset_time"],
                        self.return_params["total_power_off_duaration"],
                        self.return_params["total_power_on_duaration"],
                        self.return_params["over_power_limit"],
                        self.return_params["relay_control_mode"],
                        self.return_params["relay_status"],
                        self.return_params["relay_count"],
                        self.return_params["occurence"],
                        self.return_params["restoration"],
                        self.return_params["sip"],                  
                        self.return_params["no_of_load_surveys"],
                        self.return_params["no_of_daily_surveys"],
                        self.return_params["dip"],
                        self.return_params["no_of_billing_logs"],
                        self.return_params["no_of_billiing_histories"],
                        self.return_params["pc"],
                        self.return_params["bc"],
                        self.return_params["billing_date"],
                        self.return_params["md_w"],
                        self.return_params["md_w_ts"],
                        self.return_params["md_va"],
                        self.return_params["md_va_ts"],
                        self.return_params["voltage_related_events"],
                        self.return_params["current_related_events"],
                        self.return_params["power_related_events"],
                        self.return_params["transaction_related_events"],
                        self.return_params["non_rollover_related_events"],
                        self.return_params["control_related_events"],
                        self.return_params["other_related_events"],
                        self.return_params["total_no_of_event_entries"],
                        self.return_params["tc"],          
                        self.return_params["pfc"])


    def deserialize_sys_params_data(self, payload):
        bytes = bytearray()
        bytes = payload
        self.return_params["serial_number"] = ((bytes[0]<<24) + (bytes[1]<<16) + (bytes[2]<<8) + bytes[3])
        self.return_params["live_version"] = ((bytes[4]<<8) + bytes[5])
        self.return_params["current_time"] = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[6]<<24) + (bytes[7]<<16) + (bytes[8]<<8) + bytes[9]))
        self.return_params["reset_time"] = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[10]<<24) + (bytes[11]<<16) + (bytes[12]<<8) + bytes[13]))
        self.return_params["total_power_off_duaration"] = int(((bytes[14]<<24) + (bytes[15]<<16) + (bytes[16]<<8) + bytes[17]))/60
        self.return_params["total_power_on_duaration"] = int(((bytes[18]<<24) + (bytes[19]<<16) + (bytes[20]<<8) + bytes[21]))/60
        self.return_params["over_power_limit"]= ((bytes[22]<<24) + (bytes[23]<<16) + (bytes[24]<<8) + bytes[25])/1000.0
        self.return_params["relay_control_mode"] = int(bytes[26])
        if (self.return_params["relay_control_mode"] == 0):
            self.return_params["relay_control_mode"] = "Relay in Auto Controll Mode"
        else:
             self.return_params["relay_control_mode"] = "Relay in Manual Control Mode"
        self.return_params["relay_status"]= int(bytes[27])
        if(self.return_params["relay_status"] == 0):
            self.return_params["relay_status"] = "Relay is OFF"
        else:
            self.return_params["relay_status"] = "Relay is ON"
        self.return_params["relay_count"] = ((bytes[28]<<24) + (bytes[29]<<16) +(bytes[30]<<8) + bytes[31])
        self.return_params["relay_count"] = int(self.return_params["relay_count"]/2)
        self.return_params["occurence"] = ((bytes[32]<<24 )+ (bytes[33]<<16) + (bytes[34]<<8) + bytes[35])*3
        self.return_params["restoration"] = ((bytes[36]<<24)+ (bytes[37]<<16) + (bytes[38]<<8) + bytes[39])*3

    def get_sys_params_data(self):
        return( "Serial Number           : {} \n"
                "Live Version            : {} \n"
                "Current date & time     : {} \n"
                "Reset date & time       : {} \n"
                "Total Power Off Duration: {} Minutes\n"
                "Total Power On Duration : {} Minutes\n"
                "Over Power limit        : {} Watts\n"
                "Relay Control Mode      : {} \n"
                "Relay Status            : {} \n"
                "Relay Count             : {} \n"
                "P Occurence Time        : {} \n"
                "P Restoration Time      : {} \n")\
                .format(self.return_params["serial_number"],
                        self.return_params["live_version"],
                        self.return_params["current_time"],
                        self.return_params["reset_time"],
                        self.return_params["total_power_off_duaration"],
                        self.return_params["total_power_on_duaration"],
                        self.return_params["over_power_limit"],
                        self.return_params["relay_control_mode"],
                        self.return_params["relay_status"],
                        self.return_params["relay_count"],
                        self.return_params["occurence"],
                        self.return_params["restoration"])

    def deserialize_sys_params_profile(self, payload):
        bytes = bytearray()
        bytes = payload
        self.return_params["sip"] = ((bytes[0]<<8) + bytes[1])
        self.return_params["no_of_load_surveys"] = ((bytes[2]<<8) + bytes[3])
        self.return_params["no_of_daily_surveys"] = ((bytes[4]<<8) + bytes[5])        
        self.return_params["dip"] = ((bytes[6]<<8) + bytes[7])
        self.return_params["no_of_billing_logs"] = ((bytes[8]<<8) + bytes[9])
        self.return_params["no_of_billiing_histories"]= ((bytes[10]<<8) + bytes[11])
        self.return_params["pc"]= ((bytes[12]<<24) + (bytes[13]<<16) + (bytes[14]<<8) + bytes[15])
        self.return_params["bc"] = ((bytes[16]<<24) + (bytes[17]<<16) + (bytes[18]<<8) + bytes[19])
        self.return_params["billing_date"] = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[20]<<24) + (bytes[21]<<16) +(bytes[22]<<8) + bytes[23]))
        self.return_params["md_w"] = ((bytes[24]<<8) + bytes[25])*10
        self.return_params["md_w_ts"] = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[26]<<24) + (bytes[27]<<16) + (bytes[28]<<8) + bytes[29]))
        self.return_params["md_va"] = ((bytes[30]<<8) + bytes[31])*10
        self.return_params["md_va_ts"] = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[32]<<24) + (bytes[33]<<16) + (bytes[34]<<8) + bytes[35]))
        self.return_params["voltage_related_events"] = ((bytes[36]<<8) + bytes[37])
        self.return_params["current_related_events"] = ((bytes[38]<<8) + bytes[39])
        self.return_params["power_related_events"] = ((bytes[40]<<8) + bytes[41])
        self.return_params["transaction_related_events"] = ((bytes[42]<<8) + bytes[43])
        self.return_params["non_rollover_related_events"] = ((bytes[44]<<8) + bytes[45])
        self.return_params["control_related_events"] = ((bytes[46]<<8) + bytes[47])
        self.return_params["other_related_events"] = ((bytes[48]<<8) + bytes[49])
        self.return_params["total_no_of_event_entries"] = self.return_params["voltage_related_events"]+\
                        self.return_params["current_related_events"]+self.return_params["power_related_events"]+\
                        self.return_params["transaction_related_events"]+self.return_params["non_rollover_related_events"]+\
                        self.return_params["control_related_events"]+self.return_params["other_related_events"]
        self.return_params["tc"] = ((bytes[50]<<24) + (bytes[51]<<16) + (bytes[52]<<8) + bytes[53])
        self.return_params["pfc"] = ((bytes[54]<<24) + (bytes[55]<<16) + (bytes[56]<<8) + bytes[57])
        
      


    def get_sys_params_profile(self):
        return( "Survey Interval            : {} \n"
                "No Of Load Surveys         : {} \n"
                "No Of Daily Profiles       : {} \n"
                "Demand Interval            : {} \n"
                "No Of Billing Logs         : {} \n"
                "No Of Billing History      : {} \n"
                "Programming Count          : {} \n"
                "Billing Count              : {} \n"
                "Billing Date               : {} \n"
                "Active MD                  : {} Wats\n"
                "Active MD Time Stamp       : {} \n"
                "Apparent MD                : {} VA\n"
                "Apparent MD Time Stamp     : {} \n"
                "Voltage Related Events     : {} \n"
                "Current Related Events     : {} \n"
                "Power Related Events       : {} \n"
                "Transaction Related Events : {} \n"
                "Non Rollover Related Events: {} \n"
                "Control Related Events     : {} \n"
                "Other Related Events       : {} \n"
                "Total No Of Event Entries  : {} \n"
                "Tamper Count               : {} \n"
                "Power Failuers Count       : {} \n")\
                .format(self.return_params["sip"],                    
                        self.return_params["no_of_load_surveys"],
                        self.return_params["no_of_daily_surveys"],
                        self.return_params["dip"],
                        self.return_params["no_of_billing_logs"],
                        self.return_params["no_of_billiing_histories"],
                        self.return_params["pc"],
                        self.return_params["bc"],
                        self.return_params["billing_date"],
                        self.return_params["md_w"],
                        self.return_params["md_w_ts"],
                        self.return_params["md_va"],
                        self.return_params["md_va_ts"],
                        self.return_params["voltage_related_events"],
                        self.return_params["current_related_events"],
                        self.return_params["power_related_events"],
                        self.return_params["transaction_related_events"],
                        self.return_params["non_rollover_related_events"],
                        self.return_params["control_related_events"],
                        self.return_params["other_related_events"],
                        self.return_params["total_no_of_event_entries"],
                        self.return_params["tc"],
                        self.return_params["pfc"])

