import datetime
import time
import gp_node.utils.serialize as serialize
from gp_node.utils.serialize import *

class BillingMdPacket(object):

    def __init__(self):
        self.total_billing_count = 0    
        self.demand_integration_period = 0
        self.total_meter_power_up_count = 0
        self.total_programming_count = 0
        self.power_on_timestamp = 0
        self.power_off_timestamp = 0
        self.first_power_up_timestamp = 0
        self.power_failure_duration = 0
        self.total_meter_on_duration = 0

        self.billing_timestamp = 0
        self.real_MD_timestamp = 0
        self.real_MD_value = 0
        self.apparent_MD_timestamp = 0
        self.apparent_MD_value = 0
        self.real_energy_snap = 0
        self.apparent_energy_snap = 0
        self.real_energy_export_snap = 0
        self.apparent_energy_export_snap = 0
        self.reactive_energy_q1_snap = 0
        self.reactive_energy_q2_snap = 0
        self.reactive_energy_q3_snap = 0
        self.reactive_energy_q4_snap = 0
        self.system_power_factor = 0
        self.total_billing_duration = 0

        self.num_of_tods_present = 0
        self.tod1_start_time = 0
        self.tod1_real_energy_cumulative = 0
        self.tod1_apparent_energy_cumulative = 0
        self.tod2_start_time = 0
        self.tod2_real_energy_cumulative = 0
        self.tod2_apparent_energy_cumulative = 0
        self.tod3_start_time = 0
        self.tod3_real_energy_cumulative = 0
        self.tod3_apparent_energy_cumulative = 0
        self.tod4_start_time = 0
        self.tod4_real_energy_cumulative = 0
        self.tod4_apparent_energy_cumulative = 0
        self.tod5_start_time = 0
        self.tod5_real_energy_cumulative = 0
        self.tod5_apparent_energy_cumulative = 0
        self.tod6_start_time = 0
        self.tod6_real_energy_cumulative = 0
        self.tod6_apparent_energy_cumulative = 0
        self.tod7_start_time = 0
        self.tod7_real_energy_cumulative = 0
        self.tod7_apparent_energy_cumulative = 0
        self.tod8_start_time = 0
        self.tod8_real_energy_cumulative = 0
        self.tod8_apparent_energy_cumulative = 0

        self.instantaneous_real_demand = 0
        self.instantaneous_apparent_demand = 0
        self.last_demand_timestamp = 0

        self.tod1_real_MD_timestamp = 0
        self.tod1_real_MD_value = 0
        self.tod2_real_MD_timestamp = 0
        self.tod2_real_MD_value = 0
        self.tod3_real_MD_timestamp = 0
        self.tod3_real_MD_value = 0
        self.tod4_real_MD_timestamp = 0
        self.tod4_real_MD_value = 0
        self.tod5_real_MD_timestamp = 0
        self.tod5_real_MD_value = 0
        self.tod6_real_MD_timestamp = 0
        self.tod6_real_MD_value = 0
        self.tod7_real_MD_timestamp = 0
        self.tod7_real_MD_value = 0
        self.tod8_real_MD_timestamp = 0
        self.tod8_real_MD_value = 0

        self.tod1_apparent_MD_timestamp = 0
        self.tod1_apparent_MD_value = 0
        self.tod2_apparent_MD_timestamp = 0
        self.tod2_apparent_MD_value = 0
        self.tod3_apparent_MD_timestamp = 0
        self.tod3_apparent_MD_value = 0
        self.tod4_apparent_MD_timestamp = 0
        self.tod4_apparent_MD_value = 0
        self.tod5_apparent_MD_timestamp = 0
        self.tod5_apparent_MD_value = 0
        self.tod6_apparent_MD_timestamp = 0
        self.tod6_apparent_MD_value = 0
        self.tod7_apparent_MD_timestamp = 0
        self.tod7_apparent_MD_value = 0
        self.tod8_apparent_MD_timestamp = 0
        self.tod8_apparent_MD_value = 0
        self.meter_serial_number = 0


    def deserialize_billing_info(self, payload):
        byte = bytearray(payload)
        self.total_billing_count = serialize.deserialize_uint8(byte[0:1], "reverse")
        self.demand_integration_period = serialize.deserialize_uint8(byte[1:2], "reverse")
        self.total_programming_count = serialize.deserialize_uint8(byte[2:3], "reverse")
        self.total_meter_power_up_count = serialize.deserialize_uint16(byte[3:5], "reverse")         

        temp = serialize.deserialize_uint32(byte[5:9], "reverse")
        self.first_power_up_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))

        temp = serialize.deserialize_uint32(byte[9:13], "reverse")
        self.power_on_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))

        self.total_meter_on_duration = serialize.deserialize_uint32(byte[13:17], "reverse")
        self.power_failure_duration = serialize.deserialize_uint32(byte[17:21], "reverse")
        
    def get_billing_info_packet(self):
      return("Total  Billing Count             : {} \n"
             "Total  Programming Count         : {} \n"
             "Total  Meter Power-Up Count      : {} \n"
             "Power  On Timestamp              : {} \n"
             "First  Power Up Timestamp        : {} \n"
             "Last   Power Failure Duration    : {} \n"
             "Total  Power On Duration         : {} \n"
             "Demand Integration Period (Mins) : {} \n")\
             .format(self.total_billing_count,
                     self.total_programming_count,
                     self.total_meter_power_up_count,
                     self.power_on_timestamp,
                     self.first_power_up_timestamp,
                     self.display_duration(self.power_failure_duration),
                     self.display_duration(self.total_meter_on_duration),
                     self.demand_integration_period)

    def deserialize_billing_by_index(self, payload):
        byte = bytearray(payload)
        temp = serialize.deserialize_uint32(byte[0:4], "reverse")
        self.billing_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        
        temp = serialize.deserialize_uint32(byte[4:8], "reverse")
        self.real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        
        self.real_MD_value = (serialize.deserialize_uint32(byte[8:12], "reverse"))/100.0
        
        temp = serialize.deserialize_uint32(byte[12:16], "reverse")
        self.apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        
        self.apparent_MD_value = (serialize.deserialize_uint32(byte[16:20], "reverse"))/100.0
        self.real_energy_snap = serialize.deserialize_uint32(byte[20:24], "reverse")/100.0
        self.apparent_energy_snap = serialize.deserialize_uint32(byte[24:28], "reverse")/100.0
        self.real_energy_export_snap = serialize.deserialize_uint32(byte[28:32], "reverse")/100.0
        self.apparent_energy_export_snap = serialize.deserialize_uint32(byte[32:36], "reverse")/100.0
        self.reactive_energy_q1_snap = serialize.deserialize_uint32(byte[36:40], "reverse")/100.0
        self.reactive_energy_q2_snap = serialize.deserialize_uint32(byte[40:44], "reverse")/100.0
        self.reactive_energy_q3_snap = serialize.deserialize_uint32(byte[44:48], "reverse")/100.0
        self.reactive_energy_q4_snap = serialize.deserialize_uint32(byte[48:52], "reverse")/100.0
        # self.system_power_factor = serialize.deserialize_uint32(byte[52:56], "reverse") / 1000.0
        # self.total_billing_duration = serialize.deserialize_uint32(byte[56:60], "reverse")


    def get_billing_by_index_packet(self):
        return("Billing Timestamp            : {} \n"
               "Active MD Timestamp          : {} \n"
               "Active MD Value              : {} kW\n"
               "Apparent MD Timestamp        : {} \n"
               "Apparent MD Value            : {} kVA\n"
               "Active Energy Import         : {} kWh\n"
               "Apparent Energy Import       : {} kVAh\n"
               "Active Energy Export         : {} kWh\n"
               "Apparent Energy Export       : {} kVAh\n"
               "Reactive Energy QI           : {} kVArh\n"
               "Reactive Energy QII          : {} kVArh\n"
               "Reactive Energy QIII         : {} kVArh\n"
               "Reactive Energy QIV          : {} kVArh\n"
               # "System Power Factor          : {} \n"
               # "Total Billing Duration       : {} \n"
               ).format(self.billing_timestamp,
                        self.real_MD_timestamp,
                        self.real_MD_value,
                        self.apparent_MD_timestamp,
                        self.apparent_MD_value,
                        self.real_energy_snap,
                        self.apparent_energy_snap,
                        self.real_energy_export_snap,
                        self.apparent_energy_export_snap,
                        self.reactive_energy_q1_snap,
                        self.reactive_energy_q2_snap,
                        self.reactive_energy_q3_snap,
                        self.reactive_energy_q4_snap,
                        # self.system_power_factor,
                        # self.display_duration(self.total_billing_duration)
                        )

    def deserialize_tod_params(self, payload):
        byte = bytearray(payload)

        # ENE TOD ---------------------------------------------------------------------------------------
        temp = serialize.deserialize_uint16(byte[0:2], "reverse")
        self.tod1_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod1_real_energy_cumulative = serialize.deserialize_uint32(byte[2:6], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[6:10], "reverse")
        self.tod1_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod1_real_MD_value = serialize.deserialize_uint32(byte[10:14], "reverse")/100.0
        self.tod1_apparent_energy_cumulative = serialize.deserialize_uint32(byte[14:18], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[18:22], "reverse")
        self.tod1_apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod1_apparent_MD_value = serialize.deserialize_uint32(byte[22:26], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[26:28], "reverse")
        self.tod2_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod2_real_energy_cumulative = serialize.deserialize_uint32(byte[28:32], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[32:36], "reverse")
        self.tod2_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod2_real_MD_value = serialize.deserialize_uint32(byte[36:40], "reverse")/100.0
        self.tod2_apparent_energy_cumulative = serialize.deserialize_uint32(byte[40:44], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[44:48], "reverse")
        self.tod2_apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod2_apparent_MD_value = serialize.deserialize_uint32(byte[48:52], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[52:54], "reverse")
        self.tod3_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod3_real_energy_cumulative = serialize.deserialize_uint32(byte[54:58], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[58:62], "reverse")
        self.tod3_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod3_real_MD_value = serialize.deserialize_uint32(byte[62:66], "reverse")/100.0
        self.tod3_apparent_energy_cumulative = serialize.deserialize_uint32(byte[66:70], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[70:74], "reverse")
        self.tod3_apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod3_apparent_MD_value = serialize.deserialize_uint32(byte[74:78], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[78:80], "reverse")
        self.tod4_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod4_real_energy_cumulative = serialize.deserialize_uint32(byte[80:84], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[84:88], "reverse")
        self.tod4_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod4_real_MD_value = serialize.deserialize_uint32(byte[88:92], "reverse")/100.0
        self.tod4_apparent_energy_cumulative = serialize.deserialize_uint32(byte[92:96], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[96:100], "reverse")
        self.tod4_apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod4_apparent_MD_value = serialize.deserialize_uint32(byte[100:104], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[104:106], "reverse")
        self.tod5_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod5_real_energy_cumulative = serialize.deserialize_uint32(byte[106:110], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[110:114], "reverse")
        self.tod5_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod5_real_MD_value = serialize.deserialize_uint32(byte[114:118], "reverse")/100.0
        self.tod5_apparent_energy_cumulative = serialize.deserialize_uint32(byte[118:122], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[122:126], "reverse")
        self.tod5_apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod5_apparent_MD_value = serialize.deserialize_uint32(byte[126:130], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[130:132], "reverse")
        self.tod6_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod6_real_energy_cumulative = serialize.deserialize_uint32(byte[132:136], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[136:140], "reverse")
        self.tod6_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod6_real_MD_value = serialize.deserialize_uint32(byte[140:144], "reverse")/100.0
        self.tod6_apparent_energy_cumulative = serialize.deserialize_uint32(byte[144:148], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[148:152], "reverse")
        self.tod6_apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod6_apparent_MD_value = serialize.deserialize_uint32(byte[152:156], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[156:158], "reverse")
        self.tod7_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod7_real_energy_cumulative = serialize.deserialize_uint32(byte[158:162], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[162:166], "reverse")
        self.tod7_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod7_real_MD_value = serialize.deserialize_uint32(byte[166:170], "reverse")/100.0
        self.tod7_apparent_energy_cumulative = serialize.deserialize_uint32(byte[170:174], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[174:178], "reverse")
        self.tod7_apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod7_apparent_MD_value = serialize.deserialize_uint32(byte[178:182], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[182:184], "reverse")
        self.tod8_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod8_real_energy_cumulative = serialize.deserialize_uint32(byte[184:188], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[188:192], "reverse")
        self.tod8_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod8_real_MD_value = serialize.deserialize_uint32(byte[192:196], "reverse")/100.0
        self.tod8_apparent_energy_cumulative = serialize.deserialize_uint32(byte[196:200], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[200:204], "reverse")
        self.tod8_apparent_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod8_apparent_MD_value = serialize.deserialize_uint32(byte[204:208], "reverse")/100.0


    def get_tod_params(self):
      return("\n"
             "{:<19}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # head of table
             "{:<19}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # underline of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<10}{} \n"  # 8 Entries of table
             )\
             .format(
                    "TOD TimeZone",
                    "Cumm. Act Ene",
                    "kW MD",
                    "kW MD Timestamp",
                    "Cumm. App Ene",
                    "kVA MD",
                    "kVA MD Timestamp",

                    "------------",
                    "-------------",
                    "-----",
                    "-------------------",
                    "-------------",
                    "------",
                    "-------------------",

                    "TOD-1 ",self.tod1_start_time,
                     self.tod1_real_energy_cumulative,
                     self.tod1_real_MD_value,
                     self.tod1_real_MD_timestamp,
                     self.tod1_apparent_energy_cumulative,
                     self.tod1_apparent_MD_value,
                     self.tod1_apparent_MD_timestamp,

                    "TOD-2 ",self.tod2_start_time,
                     self.tod2_real_energy_cumulative,
                     self.tod2_real_MD_value,
                     self.tod2_real_MD_timestamp,
                     self.tod2_apparent_energy_cumulative,
                     self.tod2_apparent_MD_value,
                     self.tod2_apparent_MD_timestamp,

                    "TOD-3 ",self.tod3_start_time,
                     self.tod3_real_energy_cumulative,
                     self.tod3_real_MD_value,
                     self.tod3_real_MD_timestamp,
                     self.tod3_apparent_energy_cumulative,
                     self.tod3_apparent_MD_value,
                     self.tod3_apparent_MD_timestamp,

                    "TOD-4 ",self.tod4_start_time,
                     self.tod4_real_energy_cumulative,
                     self.tod4_real_MD_value,
                     self.tod4_real_MD_timestamp,
                     self.tod4_apparent_energy_cumulative,
                     self.tod4_apparent_MD_value,
                     self.tod4_apparent_MD_timestamp,

                    "TOD-5 ",self.tod5_start_time,
                     self.tod5_real_energy_cumulative,
                     self.tod5_real_MD_value,
                     self.tod5_real_MD_timestamp,
                     self.tod5_apparent_energy_cumulative,
                     self.tod5_apparent_MD_value,
                     self.tod5_apparent_MD_timestamp,

                    "TOD-6 ",self.tod6_start_time,
                     self.tod6_real_energy_cumulative,
                     self.tod6_real_MD_value,
                     self.tod6_real_MD_timestamp,
                     self.tod6_apparent_energy_cumulative,
                     self.tod6_apparent_MD_value,
                     self.tod6_apparent_MD_timestamp,

                    "TOD-7 ",self.tod7_start_time,
                     self.tod7_real_energy_cumulative,
                     self.tod7_real_MD_value,
                     self.tod7_real_MD_timestamp,
                     self.tod7_apparent_energy_cumulative,
                     self.tod7_apparent_MD_value,
                     self.tod7_apparent_MD_timestamp,

                    "TOD-8 ",self.tod8_start_time,
                     self.tod8_real_energy_cumulative,
                     self.tod8_real_MD_value,
                     self.tod8_real_MD_timestamp,
                     self.tod8_apparent_energy_cumulative,
                     self.tod8_apparent_MD_value,
                     self.tod8_apparent_MD_timestamp
                     )

    def get_tod_exp_params(self):
      return("\n"
             "{:<17}{:<17}{:<11}{:<23}{:<17}{:<12}{} \n"  # head of table
             "{:<17}{:<17}{:<11}{:<23}{:<17}{:<12}{} \n"  # underline of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<12}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<12}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<12}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<12}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<12}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<12}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<12}{} \n"  # 8 Entries of table
             "{:<7}{:<12}{:<17}{:<9}{:<23}{:<17}{:<12}{} \n"  # 8 Entries of table
             )\
             .format(
                    "TOD TimeZone",
                    "Cumm. ActE Exp",
                    "kW MD Exp",
                    "kW MD Exp Timestamp",
                    "Cumm. AppE Exp",
                    "kVA Exp MD",
                    "kVA Exp MD Timestamp",

                    "------------",
                    "--------------",
                    "---------",
                    "-------------------",
                    "--------------",
                    "----------",
                    "--------------------",

                    "TOD-1 ",self.tod1_start_time,
                     self.tod1_real_energy_cumulative,
                     self.tod1_real_MD_value,
                     self.tod1_real_MD_timestamp,
                     self.tod1_apparent_energy_cumulative,
                     self.tod1_apparent_MD_value,
                     self.tod1_apparent_MD_timestamp,

                    "TOD-2 ",self.tod2_start_time,
                     self.tod2_real_energy_cumulative,
                     self.tod2_real_MD_value,
                     self.tod2_real_MD_timestamp,
                     self.tod2_apparent_energy_cumulative,
                     self.tod2_apparent_MD_value,
                     self.tod2_apparent_MD_timestamp,

                    "TOD-3 ",self.tod3_start_time,
                     self.tod3_real_energy_cumulative,
                     self.tod3_real_MD_value,
                     self.tod3_real_MD_timestamp,
                     self.tod3_apparent_energy_cumulative,
                     self.tod3_apparent_MD_value,
                     self.tod3_apparent_MD_timestamp,

                    "TOD-4 ",self.tod4_start_time,
                     self.tod4_real_energy_cumulative,
                     self.tod4_real_MD_value,
                     self.tod4_real_MD_timestamp,
                     self.tod4_apparent_energy_cumulative,
                     self.tod4_apparent_MD_value,
                     self.tod4_apparent_MD_timestamp,

                    "TOD-5 ",self.tod5_start_time,
                     self.tod5_real_energy_cumulative,
                     self.tod5_real_MD_value,
                     self.tod5_real_MD_timestamp,
                     self.tod5_apparent_energy_cumulative,
                     self.tod5_apparent_MD_value,
                     self.tod5_apparent_MD_timestamp,

                    "TOD-6 ",self.tod6_start_time,
                     self.tod6_real_energy_cumulative,
                     self.tod6_real_MD_value,
                     self.tod6_real_MD_timestamp,
                     self.tod6_apparent_energy_cumulative,
                     self.tod6_apparent_MD_value,
                     self.tod6_apparent_MD_timestamp,

                    "TOD-7 ",self.tod7_start_time,
                     self.tod7_real_energy_cumulative,
                     self.tod7_real_MD_value,
                     self.tod7_real_MD_timestamp,
                     self.tod7_apparent_energy_cumulative,
                     self.tod7_apparent_MD_value,
                     self.tod7_apparent_MD_timestamp,

                    "TOD-8 ",self.tod8_start_time,
                     self.tod8_real_energy_cumulative,
                     self.tod8_real_MD_value,
                     self.tod8_real_MD_timestamp,
                     self.tod8_apparent_energy_cumulative,
                     self.tod8_apparent_MD_value,
                     self.tod8_apparent_MD_timestamp
                     )


    def deserialize_billing_data_params(self, payload):
        byte = bytearray(payload)

        self.meter_serial_number = serialize.deserialize_uint32(byte[0:4], "reverse")
        temp = serialize.deserialize_uint32(byte[4:8], "reverse")
        self.billing_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.real_energy_snap = serialize.deserialize_uint32(byte[8:12], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[12:16], "reverse")
        self.real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        
        self.real_MD_value = (serialize.deserialize_uint32(byte[16:20], "reverse"))/100.0

        # ENE TOD ---------------------------------------------------------------------------------------
        temp = serialize.deserialize_uint16(byte[20:22], "reverse")
        self.tod1_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod1_real_energy_cumulative = serialize.deserialize_uint32(byte[22:26], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[26:30], "reverse")
        self.tod1_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod1_real_MD_value = serialize.deserialize_uint32(byte[30:34], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[34:36], "reverse")
        self.tod2_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod2_real_energy_cumulative = serialize.deserialize_uint32(byte[36:40], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[40:44], "reverse")
        self.tod2_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod2_real_MD_value = serialize.deserialize_uint32(byte[44:48], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[48:50], "reverse")
        self.tod3_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod3_real_energy_cumulative = serialize.deserialize_uint32(byte[50:54], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[54:58], "reverse")
        self.tod3_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod3_real_MD_value = serialize.deserialize_uint32(byte[58:62], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[62:64], "reverse")
        self.tod4_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod4_real_energy_cumulative = serialize.deserialize_uint32(byte[64:68], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[68:72], "reverse")
        self.tod4_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod4_real_MD_value = serialize.deserialize_uint32(byte[72:76], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[76:78], "reverse")
        self.tod5_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod5_real_energy_cumulative = serialize.deserialize_uint32(byte[78:82], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[82:86], "reverse")
        self.tod5_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod5_real_MD_value = serialize.deserialize_uint32(byte[86:90], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[90:92], "reverse")
        self.tod6_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod6_real_energy_cumulative = serialize.deserialize_uint32(byte[92:96], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[96:100], "reverse")
        self.tod6_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod6_real_MD_value = serialize.deserialize_uint32(byte[100:104], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[104:106], "reverse")
        self.tod7_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod7_real_energy_cumulative = serialize.deserialize_uint32(byte[106:110], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[110:114], "reverse")
        self.tod7_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod7_real_MD_value = serialize.deserialize_uint32(byte[114:118], "reverse")/100.0

        temp = serialize.deserialize_uint16(byte[118:120], "reverse")
        self.tod8_start_time = str(temp/60) + ":" + str(temp%60) + ":00"
        self.tod8_real_energy_cumulative = serialize.deserialize_uint32(byte[120:124], "reverse")/100.0
        temp = serialize.deserialize_uint32(byte[124:128], "reverse")
        self.tod8_real_MD_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))
        self.tod8_real_MD_value = serialize.deserialize_uint32(byte[128:132], "reverse")/100.0

        self.system_power_factor = serialize.deserialize_uint32(byte[132:136], "reverse") / 1000.0
        self.total_billing_duration = serialize.deserialize_uint32(byte[136:140], "reverse")

    def get_billdata_params(self):
      return(
             "Meter Serial Number               : {} \n"
             "Billing Timestamp                 : {} \n"
             "Real Energy Snap                  : {} kWh\n"
             "Real MD Timestamp                 : {} \n"
             "Real MD Value                     : {} kW\n"
             "System Power Factor               : {} \n"
             "Total Billing Duration            : {} \n\n"
             "{:<15}{:<20}{:<30}{:<20}{} \n"  # head of table
             "{:<15}{:<20}{:<30}{:<20}{} \n"  # underline of table
             "{:<15}{:<20}{:<30}{:<20}{} \n"  # 8 Entries of table
             "{:<15}{:<20}{:<30}{:<20}{} \n"
             "{:<15}{:<20}{:<30}{:<20}{} \n"
             "{:<15}{:<20}{:<30}{:<20}{} \n"
             "{:<15}{:<20}{:<30}{:<20}{} \n"
             "{:<15}{:<20}{:<30}{:<20}{} \n"
             "{:<15}{:<20}{:<30}{:<20}{} \n"
             "{:<15}{:<20}{:<30}{:<20}{} \n"
             )\
             .format(
                     self.meter_serial_number,
                     self.billing_timestamp,
                     self.real_energy_snap,
                     self.real_MD_timestamp,
                     self.real_MD_value,
                     self.system_power_factor,
                     self.display_duration(self.total_billing_duration),

                     "TOD List",
                     "Start Timestamp",
                     "Cumm. Active Energy (kWh)",
                     "MD Value (kW)",
                     "MD Timestamp",

                     "--------",
                     "---------------",
                     "-------------------------",
                     "-------------",
                     "-------------------",

                     "TOD-1", self.tod1_start_time,
                     self.tod1_real_energy_cumulative,
                     self.tod1_real_MD_value,
                     self.tod1_real_MD_timestamp,

                     "TOD-2", self.tod2_start_time,
                     self.tod2_real_energy_cumulative,
                     self.tod2_real_MD_value,
                     self.tod2_real_MD_timestamp,

                     "TOD-3", self.tod3_start_time,
                     self.tod3_real_energy_cumulative,
                     self.tod3_real_MD_value,
                     self.tod3_real_MD_timestamp,

                     "TOD-4", self.tod4_start_time,
                     self.tod4_real_energy_cumulative,
                     self.tod4_real_MD_value,
                     self.tod4_real_MD_timestamp,

                     "TOD-5", self.tod5_start_time,
                     self.tod5_real_energy_cumulative,
                     self.tod5_real_MD_value,
                     self.tod5_real_MD_timestamp,

                     "TOD-6", self.tod6_start_time,
                     self.tod6_real_energy_cumulative,
                     self.tod6_real_MD_value,
                     self.tod6_real_MD_timestamp,

                     "TOD-7", self.tod7_start_time,
                     self.tod7_real_energy_cumulative,
                     self.tod7_real_MD_value,
                     self.tod7_real_MD_timestamp,

                     "TOD-8", self.tod8_start_time,
                     self.tod8_real_energy_cumulative,
                     self.tod8_real_MD_value,
                     self.tod8_real_MD_timestamp
                     )


    def deserialize_get_instantaneous_demand(self, payload):
        byte = bytearray(payload)

        self.instantaneous_real_demand = (serialize.deserialize_uint32(byte[0:4], "reverse"))/10.0
        self.instantaneous_apparent_demand = (serialize.deserialize_uint32(byte[4:8], "reverse"))/10.0

        temp = serialize.deserialize_uint32(byte[8:12], "reverse")
        self.last_demand_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(temp))

    def get_instantaneous_demand_packet(self):
      return("Last Demand Timestamp            : {} \n"
             "Instantaneous Real Demand(W)     : {} \n"
             "Instantaneous Apparent Demand(W) : {} \n")\
             .format(self.last_demand_timestamp,
                     self.instantaneous_real_demand,
                     self.instantaneous_apparent_demand)

    def display_duration(self, duration):
        duration_day = duration/86400
        duration -= duration_day*86400
        duration_hour = duration/3600
        duration -= duration_hour*3600
        duration_min = duration/60
        duration -= duration_min*60
        duration_sec = duration
        return "{} d {} h {} m {} s".format(duration_day, duration_hour, duration_min, duration_sec)
