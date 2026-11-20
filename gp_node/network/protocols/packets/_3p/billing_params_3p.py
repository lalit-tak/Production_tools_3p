import datetime
import time
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils.serialize import deserialize_uint32
from gp_node.utils import TamperFlag
import gp_node.utils.serialize as serialize


class BillingParams3P(object):

    def __init__(self):
        self.num_of_billing_log = 0
        self.num_of_billing_history = 0
        self.billing_date = 0
        self.integration_period = 0
        self.billing_count = 0

        self.currentMD_timestamp = 0
        self.totalRealEnergy = 0
        self.totalApparentEnergy = 0
        self.activeMD = 0
        self.activeMDTimeStamp = 0
        self.apparentMD = 0
        self.apparentMDTimeStamp = 0

        self.billingTimestamp = 0
        self.sys_power_factor = 0
        self.lagOnlyReactiveEnergy = 0
        self.leadOnlyReactiveEnergy = 0
        self.total_power_on_duration = 0

        self.instantanious_md = 0;
        self.instantanious_apparent_md = 0;

        self.reset_time = 0
        self.current_time = 0
        self.total_power_on_duaration_d = 0
        self.billing_power_on_duaration_d = 0
        self.total_power_off_duaration = 0
        self.total_power_on_duaration = 0

        self.occurence_time = 0
        self.restoration_time = 0
        self.over_power_limit = 0
        self.relay_control_mode = 0

        # We have to change this variables into some new files
        self.debug_dlms_1 = 0
        self.debug_dlms_2 = 0
        self.debug_dlms_3 = 0



    def __str__(self):
        return "Hello....."
        
        
    def deserialize_billing_params(self, payload):
        bytes = bytearray()
        bytes = payload
    
        self.num_of_billing_history = ((bytes[0]<<24) + (bytes[1]<<16) + (bytes[2]<<8) + bytes[3])
        self.billing_date = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[4]<<24) + (bytes[5]<<16) + (bytes[6]<<8) + bytes[7]))
        self.integration_period = ((bytes[8]<<24) + (bytes[9]<<16) + (bytes[10]<<8) + bytes[11])
        self.billing_count = ((bytes[12]<<24) + (bytes[13]<<16) + (bytes[14]<<8) + bytes[15])
        self.activeMD = ((bytes[16]<<24) + (bytes[17]<<16) + (bytes[18]<<8) + bytes[19])*10
        self.activeMDTimeStamp = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[20]<<24) + (bytes[21]<<16) + (bytes[22]<<8) + bytes[23]))
        self.apparentMD = ((bytes[24]<<24) + (bytes[25]<<16) + (bytes[26]<<8) + bytes[27])*10
        self.apparentMDTimeStamp = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[28]<<24) + (bytes[29]<<16) + (bytes[30]<<8) + bytes[31]))
    
    def get_billing_params_packet(self):
        return( "No of Billing History     :{}\n"
                "Next Billing Date         :{} \n"
                "MD Integration Period     :{} Minutes\n"
                "Billing Count             :{} \n"
                "Active MD                 :{} W\n"
                "Active MD Time Stamp      :{} \n"
                "Apparent MD               :{} VA\n"
                "Apparent MD Time Stamp    :{} \n")\
                .format(self.num_of_billing_history,
                        self.billing_date, 
                        self.integration_period, 
                        self.billing_count,
                        self.activeMD, 
                        self.activeMDTimeStamp,
                        self.apparentMD, 
                        self.apparentMDTimeStamp)

                
    def deserialize_billing_log_packet(self, payload):
        bytes = bytearray()
        bytes = payload
        self.currentMD_timestamp = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[0]<<24) + (bytes[1]<<16) + (bytes[2]<<8) + bytes[3]))
        self.totalRealEnergy = ((bytes[4]<<24) + (bytes[5]<<16) + (bytes[6]<<8) + bytes[7])/100.0
        self.totalApparentEnergy = ((bytes[8]<<24) + (bytes[9]<<16) + (bytes[10]<<8) + bytes[11])/100.0
        self.activeMD = ((bytes[12]<<24) + (bytes[13]<<16) + (bytes[14]<<8) + bytes[15])*10
        self.activeMDTimeStamp = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[16]<<24) + (bytes[17]<<16) + (bytes[18]<<8) + bytes[19]))
        self.apparentMD = ((bytes[20]<<24) + (bytes[21]<<16) + (bytes[22]<<8) + bytes[23])*10
        self.apparentMDTimeStamp = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[24]<<24) + (bytes[25]<<16) + (bytes[26]<<8) + bytes[27]))
        self.instantanious_md =((bytes[28]<<24) + (bytes[29]<<16) + (bytes[30]<<8) + bytes[31])*10
        self.instantanious_apparent_md = ((bytes[32]<<24) + (bytes[33]<<16) + (bytes[34]<<8) + bytes[35])*10
 

    def get_billing_log_packet(self):
        return( "Instantanious MD time stamp     :   {} \n"
                "Initial Real Energy             :   {} KWH\n"
                "Initial Apparent Energy         :   {} KVAH\n"
                "Active MD                       :   {} W\n"
                "Active MD Time Stamp            :   {} \n"
                "Apparent MD                     :   {} VA\n"
                "Apparent MD Time Stamp          :   {} \n"
                "Instantanious MD                :   {} W\n"
                "Instantanious Apparent MD       :   {} VA\n")\
                .format(self.currentMD_timestamp,
                        self.totalRealEnergy,
                        self.totalApparentEnergy, 
                        self.activeMD, 
                        self.activeMDTimeStamp,
                        self.apparentMD, 
                        self.apparentMDTimeStamp,
                        self.instantanious_md,
                        self.instantanious_apparent_md)

    def deserialize_billing_history_packet(self, payload):
        bytes = bytearray()
        bytes = payload
        self.billingTimestamp = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[0]<<24) + (bytes[1]<<16) + (bytes[2]<<8) + bytes[3]))
        self.sys_power_factor = ((bytes[4]<<24) + (bytes[5]<<16) + (bytes[6]<<8) + bytes[7])/10000.0
        self.totalRealEnergy = ((bytes[8]<<24) + (bytes[9]<<16) + (bytes[10]<<8) + bytes[11])/100.0
        self.lagOnlyReactiveEnergy = ((bytes[12]<<24) + (bytes[13]<<16) + (bytes[14]<<8) + bytes[15])/100.0
        self.leadOnlyReactiveEnergy = ((bytes[16]<<24) + (bytes[17]<<16) + (bytes[18]<<8) + bytes[19])/100.0
        self.totalApparentEnergy = ((bytes[20]<<24) + (bytes[21]<<16) + (bytes[22]<<8) + bytes[23])/100.0 
        self.activeMD = ((bytes[24]<<24) + (bytes[25]<<16) + (bytes[26]<<8) + bytes[27])*10
        self.apparentMD = ((bytes[28]<<24) + (bytes[29]<<16) + (bytes[30]<<8) + bytes[31])*10
        self.activeMDTimeStamp = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[32]<<24) + (bytes[33]<<16) + (bytes[34]<<8) + bytes[35]))
        self.apparentMDTimeStamp = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[36]<<24) + (bytes[37]<<16) + (bytes[38]<<8) + bytes[39]))
        self.total_power_on_duration = ((bytes[40]<<24) + (bytes[41]<<16) + (bytes[42]<<8) + bytes[43])/60.0
 

    def get_billing_history_packet(self):
        return( "Billing Date                          :   {} \n"
                "System Power factor                   :   {} \n"
                "Cumulative Real Energy                :   {} KWH\n"
                "Cumulative Real Energy (TZ1)          :   {} KWH\n"
                "Cumulative Real Energy TZ(2 -8)       :   {} KWH\n"
                "Cumulative Lag Only Reactive Energy   :   {} KVARH\n"
                "Cumulative Lead Only Reactive Energy  :   {} KVARH\n"
                "Cumulative Apparent Energy            :   {} KVAH\n"
                "Cumulative Apparent Energy for TZ1    :   {} KVAH\n"
                "Cumulative Apparent Energy TZ(2 -8)   :   {} KVAH\n"
                "Active MD                             :   {} W\n"
                "Active MD(TZ1)                        :   {} W\n"
                "Active MDTZ(2-8)                      :   {} W\n"
                "Apparent MD                           :   {} VA\n"
                "Apparent MD(TZ1)                      :   {} VA\n"
                "Apparent MDTZ(2-8)                    :   {} VA\n"
                "Active MD Time stamp                  :   {} \n"
                "Apparent MD Time stamp                :   {} \n"
                "Total Power on Duration               :   {} Minutes\n")\
                .format(self.billingTimestamp,
                        self.sys_power_factor,
                        self.totalRealEnergy, 
                        self.totalRealEnergy,
                        0.0,
                        self.lagOnlyReactiveEnergy,
                        self.leadOnlyReactiveEnergy,
                        self.totalApparentEnergy,
                        self.totalApparentEnergy,
                        0.0,
                        self.activeMD,
                        self.activeMD,
                        0.0,
                        self.apparentMD,
                        self.apparentMD,
                        0.0,
                        self.activeMDTimeStamp,
                        self.apparentMDTimeStamp,
                        self.total_power_on_duration)


    def deserialize_sys_params(self, payload):
        bytes = bytearray()
        bytes = payload
        self.reset_time = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[0]<<24) + (bytes[1]<<16) + (bytes[2]<<8) + bytes[3]))
        self.current_time = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[4]<<24) + (bytes[5]<<16) + (bytes[6]<<8) + bytes[7]))
        self.total_power_on_duaration_d = ((bytes[8]<<24) + (bytes[9]<<16) + (bytes[10]<<8) + bytes[11])
        self.billing_power_on_duaration_d = ((bytes[12]<<24) + (bytes[13]<<16) + (bytes[14]<<8) + bytes[15])
        self.total_power_off_duaration = ((bytes[16]<<24) + (bytes[17]<<16) + (bytes[18]<<8) + bytes[19])
        self.total_power_on_duaration = ((bytes[20]<<24) + (bytes[21]<<16) + (bytes[22]<<8) + bytes[23])
        self.occurence_time = ((bytes[24]<<24) + (bytes[25]<<16) + (bytes[26]<<8) + bytes[27])*3
        self.restoration_time = ((bytes[28]<<24) + (bytes[29]<<16) + (bytes[30]<<8) + bytes[31])*3
        self.over_power_limit =((bytes[32]<<24) + (bytes[33]<<16) + (bytes[34]<<8) + bytes[35])/1000.0
        self.relay_control_mode = int(bytes[36])
        print (self.relay_control_mode)
        if (self.relay_control_mode == 0):
            self.relay_control_mode = "Relay in Auto Controll Mode"
        else:
            self.relay_control_mode = "Relay in Manual Control Mode"


    def get_sys_packet(self):
        return( "Reset Time                         :{} \n"
                "Current Time                       :{} \n"
                "Total Power ON Duation(D)          :{} Seconds\n"
                "Billing Power ON Duration(D)       :{} Seconds\n"
                "Total Power OFF Duration           :{} Seconds\n"
                "Total Power ON Duration            :{} Seconds\n"
                "P time Occurence                   :{} Seconds\n"
                "P time Restoration                 :{} Seconds\n"
                "Over Power Limit                   :{} Watts\n"
                "Relay Control Mode                 :{}\n")\
                .format(self.reset_time,
                        self.current_time, 
                        self.total_power_on_duaration_d, 
                        self.billing_power_on_duaration_d,
                        self.total_power_off_duaration, 
                        self.total_power_on_duaration,
                        self.occurence_time,
                        self.restoration_time,
                        self.over_power_limit,
                        self.relay_control_mode)


    def deserialize_dlms_params(self, payload):
        bytes = bytearray()
        bytes = payload
        self.debug_dlms_1 = (bytes[0]<<8) + bytes[1]
        self.debug_dlms_2 = (bytes[2]<<8) + bytes[3]
        self.debug_dlms_3 = (bytes[4]<<8) + bytes[5]
        self.debug_dlms_4 = (bytes[6]<<8) + bytes[7]
        self.debug_dlms_5 = (bytes[8]<<8) + bytes[9]
    
    def get_dlms_debug_packet(self):
        return( "Wrong RX CRC [0]               :{} \n"
                "RX Good [1]                    :{} \n"
                "RX Incomplete [2]              :{} \n"
                "TX Good [3]                    :{} \n"
                "TX Resent [4]                  :{} \n")\
                .format(self.debug_dlms_1,
                        self.debug_dlms_2, 
                        self.debug_dlms_3,
                        self.debug_dlms_4,
                        self.debug_dlms_5)

