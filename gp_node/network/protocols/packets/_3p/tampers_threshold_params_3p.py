from gp_node.utils.serialize import deserialize_uint8

import gp_node.utils.serialize as serialize

class TampersThresholdPacket(object):

    def __init__(self):
        self.Volt_Unb_Volt_Threhold = 0
        self.Volt_Unb_Percentage_Threhold = 0 
        self.Ovr_Volt_Min_Threshold = 0
        self.Ovr_Volt_Max_Threshold = 0
        self.Low_Volt_Min_Threshold = 0
        self.Low_Volt_Max_Threshold = 0
        self.Phase_Miss_Ocr_Volt_Threshold = 0
        self.Curr_Rev_Volt_Threshold = 0
        self.Curr_Rev_Curr_Threshold = 0
        self.Curr_Unb_Volt_Threhold = 0
        self.Curr_Unb_Percentage_Threhold = 0
        self.Curr_Unb_Curr_Threhold = 0
        self.OvrCurr_Volt_Threshold = 0
        self.Ovr_Neutral_Curr_Threshold = 0
        self.Low_Pf_Curr_Threshold = 0
        self.Magnet_Tamper_Volt_Threshold = 0
        self.ND_Volt_Threshold = 0
        self.ND_Res_Volt_Threshold = 0
        self.Phase_Seq_Rev_Volt_Threshold = 0
        self.Ovr_Curr_Threshold = 0
        self.CT_Bypass_Volt_Threshold = 0
        self.CT_Bypass_Curr_Threshold = 0
        self.CT_Bypass_VectorSum_Threshold = 0
        self.CT_Bypass_Diif_VectorSum_Threshold = 0
        self.OverLoad_Threshold = 0

    def deserialize(self, payload):  # For Get Tampers Threshold
        buf = bytearray()
        buf = payload
        
        payload_length = len(buf)
        print (payload_length)
        if (payload_length == 25):
            self.Volt_Unb_Volt_Threhold = serialize.deserialize_uint8(buf[0:1])
            self.Volt_Unb_Percentage_Threhold = serialize.deserialize_uint8(buf[1:2])
            self.Ovr_Volt_Min_Threshold = serialize.deserialize_uint8(buf[2:3])
            self.Ovr_Volt_Max_Threshold = serialize.deserialize_uint8(buf[3:4])
            self.Low_Volt_Min_Threshold = serialize.deserialize_uint8(buf[4:5])
            self.Low_Volt_Max_Threshold = serialize.deserialize_uint8(buf[5:6])
            self.Phase_Miss_Ocr_Volt_Threshold = serialize.deserialize_uint8(buf[6:7])
            self.Curr_Rev_Volt_Threshold = serialize.deserialize_uint8(buf[7:8])   
            self.Curr_Rev_Curr_Threshold = serialize.deserialize_uint8(buf[8:9]) 
            self.Curr_Unb_Volt_Threhold = serialize.deserialize_uint8(buf[9:10])
            self.Curr_Unb_Percentage_Threhold = serialize.deserialize_uint8(buf[10:11])
            self.Curr_Unb_Curr_Threhold = serialize.deserialize_uint8(buf[11:12])
            self.OvrCurr_Volt_Threshold = serialize.deserialize_uint8(buf[12:13])
            self.Ovr_Neutral_Curr_Threshold = serialize.deserialize_uint8(buf[13:14])
            self.Low_Pf_Curr_Threshold = serialize.deserialize_uint8(buf[14:15])
            self.Magnet_Tamper_Volt_Threshold = serialize.deserialize_uint8(buf[15:16])
            self.ND_Volt_Threshold = serialize.deserialize_uint8(buf[16:17])
            self.ND_Res_Volt_Threshold = serialize.deserialize_uint8(buf[17:18])
            self.Phase_Seq_Rev_Volt_Threshold = serialize.deserialize_uint8(buf[18:19])
            self.Ovr_Curr_Threshold = serialize.deserialize_uint8(buf[19:20])
            self.CT_Bypass_Volt_Threshold = serialize.deserialize_uint8(buf[20:21])
            self.CT_Bypass_Curr_Threshold = serialize.deserialize_uint8(buf[21:22])
            self.CT_Bypass_VectorSum_Threshold = serialize.deserialize_uint8(buf[22:23])
            self.CT_Bypass_Diif_VectorSum_Threshold = serialize.deserialize_uint8(buf[23:24])
            self.OverLoad_Threshold = serialize.deserialize_uint8(buf[24:25])
            
            print("Voltage_Unbalance_Voltage_Threhold :        %d  %%      \n"
                "Voltage_Unbalance_Percentage_Threhold:      %d  %%      \n"
                "Over_Voltage_Minimum_Threshold:             %d  %%      \n"
                "Over_Voltage_Maximum_Threshold:             %d  %%      \n"
                "Low_Voltage_Minimum_Threshold:              %d  %%      \n"
                "Low_Voltage_Maximum_Threshold:              %d  %%      \n"
                "Phase_Miss_Voltage_Threshold:               %d  %%      \n"
                "Current_Reverse_Voltage_Threshold:          %d  %%      \n"
                "Current_Reverse_Current_Threshold:          %d  %%      \n"
                "Current_Unbalance_Voltage_Threhold:         %d  %%      \n"
                "Current_Unbalance_Percentage_Threhold:      %d  %%      \n"
                "Current_Unbalance_Current_Threhold:         %d  %%      \n"
                "OverCurrent_Voltage_Threshold:              %d  %%      \n"
                "Over_Neutral_Current_Threshold:             %d  %%      \n"
                "Low_Pf_Current_Threshold:                   %d  %%      \n"
                "Magnet_Tamper_Voltage_Threshold:            %d  %%      \n"
                "ND_Voltage_Threshold:                       %d  %%      \n"
                "ND_Restore_Voltage_Threshold:               %d  %%      \n"
                "Phase_Seq_Reverse_Voltage_Threshold:        %d  %%      \n"
                "Over_Current_Threshold:                     %d  %%      \n"
                "CT_Bypass_Voltage_Threshold:                %d  %%      \n"
                "CT_Bypass_Current_Threshold:                %d  %%      \n"
                "CT_Bypass_VectorSum_Threshold:              %d  %%      \n"
                "CT_Bypass_Diif_VectorSum_Threshold:         %d  %%      \n" 
                "OverLoad_Threshold                          %d  %%      \n"% (
                self.Volt_Unb_Volt_Threhold,
                self.Volt_Unb_Percentage_Threhold,
                self.Ovr_Volt_Min_Threshold,
                self.Ovr_Volt_Max_Threshold,
                self.Low_Volt_Min_Threshold,
                self.Low_Volt_Max_Threshold,
                self.Phase_Miss_Ocr_Volt_Threshold,
                self.Curr_Rev_Volt_Threshold,
                self.Curr_Rev_Curr_Threshold,
                self.Curr_Unb_Volt_Threhold,
                self.Curr_Unb_Percentage_Threhold,
                self.Curr_Unb_Curr_Threhold,
                self.OvrCurr_Volt_Threshold,
                self.Ovr_Neutral_Curr_Threshold,
                self.Low_Pf_Curr_Threshold,
                self.Magnet_Tamper_Volt_Threshold,
                self.ND_Volt_Threshold,
                self.ND_Res_Volt_Threshold,
                self.Phase_Seq_Rev_Volt_Threshold,
                self.Ovr_Curr_Threshold,
                self.CT_Bypass_Volt_Threshold,
                self.CT_Bypass_Curr_Threshold,
                self.CT_Bypass_VectorSum_Threshold,
                self.CT_Bypass_Diif_VectorSum_Threshold,
                self.OverLoad_Threshold
            ))

        else:
            self.Volt_Unb_Volt_Threhold = serialize.deserialize_uint8(buf[0:1])
            self.Volt_Unb_Percentage_Threhold = serialize.deserialize_uint8(buf[1:2])
            self.Ovr_Volt_Min_Threshold = serialize.deserialize_uint8(buf[2:3])
            self.Ovr_Volt_Max_Threshold = serialize.deserialize_uint8(buf[3:4])
            self.Low_Volt_Min_Threshold = serialize.deserialize_uint8(buf[4:5])
            self.Low_Volt_Max_Threshold = serialize.deserialize_uint8(buf[5:6])
            self.Phase_Miss_Ocr_Volt_Threshold = serialize.deserialize_uint8(buf[6:7])
            self.Phase_Miss_Res_Volt_Threshold = serialize.deserialize_uint8(buf[7:8])
            self.Phase_Miss_Rem_Volt_Threshold = serialize.deserialize_uint8(buf[8:9])
            self.Curr_Rev_Volt_Threshold = serialize.deserialize_uint8(buf[9:10])
            self.Curr_Rev_Curr_Threshold = serialize.deserialize_uint8(buf[10:11])
            self.Curr_Unb_Volt_Threhold = serialize.deserialize_uint8(buf[11:12])
            self.Curr_Unb_Percentage_Threhold = serialize.deserialize_uint8(buf[12:13])
            self.Curr_Unb_Ocr_Avg_Curr_Threhold = serialize.deserialize_uint8(buf[13:14])
            self.Curr_Unb_Res_Avg_Curr_Threhold = serialize.deserialize_uint8(buf[14:15])
            self.Curr_Unb_N_Curr_Threhold = serialize.deserialize_uint8(buf[15:16])
            self.Curr_Unb_Residual_Curr_Threhold = serialize.deserialize_uint8(buf[16:17])
            self.OvrCurr_Volt_Threshold = serialize.deserialize_uint8(buf[17:18])
            self.Ovr_Neutral_Curr_Threshold = serialize.deserialize_uint8(buf[18:19])
            self.Low_Pf_Curr_Threshold = serialize.deserialize_uint8(buf[19:20])
            self.Magnet_Tamper_Volt_Threshold = serialize.deserialize_uint8(buf[20:21])
            self.ND_Volt_Threshold = serialize.deserialize_uint8(buf[21:22])
            self.ND_Res_Volt_Threshold = serialize.deserialize_uint8(buf[22:23])
            self.Phase_Seq_Rev_Volt_Threshold = serialize.deserialize_uint8(buf[23:24])
            self.Ovr_Curr_Threshold = serialize.deserialize_uint8(buf[24:25])
            self.CT_Bypass_Volt_Threshold = serialize.deserialize_uint8(buf[25:26])
            self.CT_Bypass_Curr_Threshold = serialize.deserialize_uint8(buf[26:27])
            self.CT_Bypass_Avg_Curr_Threshold = serialize.deserialize_uint8(buf[27:28])
            self.CT_Bypass_Residual_Curr_Threshold = serialize.deserialize_uint8(buf[28:29])
            self.OverLoad_Threshold = serialize.deserialize_uint8(buf[29:30])
                
            print("Voltage_Unbalance_Voltage_Threhold :       %d  %%      \n"
                "Voltage_Unbalance_Percentage_Threhold:      %d  %%      \n"
                "Over_Voltage_Minimum_Threshold:             %d  %%      \n"
                "Over_Voltage_Maximum_Threshold:             %d  %%      \n"
                "Low_Voltage_Minimum_Threshold:              %d  %%      \n"
                "Low_Voltage_Maximum_Threshold:              %d  %%      \n"
                "Phase_Miss_Ocr_Voltage_Threshold:           %d  %%      \n"
                "Phase_Miss_Res_Voltage_Threshold:           %d  %%      \n"
                "Phase_Miss_Rem_Voltage_Threshold:           %d  %%      \n"
                "Current_Reverse_Voltage_Threshold:          %d  %%      \n"
                "Current_Reverse_Current_Threshold:          %d  %%      \n"
                "Current_Unbalance_Voltage_Threhold:         %d  %%      \n"
                "Current_Unbalance_Percentage_Threhold:      %d  %%      \n"
                "Current_Unbalance_Ocr_Ave_Current_Threhold: %d  %%      \n"
                "Current_Unbalance_Res_Ave_Current_Threhold: %d  %%      \n"
                "Current_Unbalance_Neu_Current_Threhold:     %d  %%      \n"
                "Current_Unbalance_Resi_Current_Threhold:    %d  %%      \n"
                "OverCurrent_Voltage_Threshold:              %d  %%      \n"
                "Over_Neutral_Current_Threshold:             %d  %%      \n"
                "Low_Pf_Current_Threshold:                   %d  %%      \n"
                "Magnet_Tamper_Voltage_Threshold:            %d  %%      \n"
                "ND_Voltage_Threshold:                       %d  %%      \n"
                "ND_Restore_Voltage_Threshold:               %d  %%      \n"
                "Phase_Seq_Reverse_Voltage_Threshold:        %d  %%      \n"
                "Over_Current_Threshold:                     %d  %%      \n"
                "CT_Bypass_Voltage_Threshold:                %d  %%      \n"
                "CT_Bypass_Current_Threshold:                %d  %%      \n"
                "CT_Bypass_Average_Current_Threshold:        %d  %%      \n"
                "CT_Bypass_Residual_Current_Threshold:       %d  %%      \n"
                "OverLoad_Threshold                          %d  %%      \n" % (
                self.Volt_Unb_Volt_Threhold,
                self.Volt_Unb_Percentage_Threhold,
                self.Ovr_Volt_Min_Threshold,
                self.Ovr_Volt_Max_Threshold,
                self.Low_Volt_Min_Threshold,
                self.Low_Volt_Max_Threshold,
                self.Phase_Miss_Ocr_Volt_Threshold,
                self.Phase_Miss_Res_Volt_Threshold,
                self.Phase_Miss_Rem_Volt_Threshold,
                self.Curr_Rev_Volt_Threshold,
                self.Curr_Rev_Curr_Threshold,
                self.Curr_Unb_Volt_Threhold,
                self.Curr_Unb_Percentage_Threhold,
                self.Curr_Unb_Ocr_Avg_Curr_Threhold,
                self.Curr_Unb_Res_Avg_Curr_Threhold,
                self.Curr_Unb_N_Curr_Threhold,
                self.Curr_Unb_Residual_Curr_Threhold,
                self.OvrCurr_Volt_Threshold,
                self.Ovr_Neutral_Curr_Threshold,
                self.Low_Pf_Curr_Threshold,
                self.Magnet_Tamper_Volt_Threshold,
                self.ND_Volt_Threshold,
                self.ND_Res_Volt_Threshold,
                self.Phase_Seq_Rev_Volt_Threshold,
                self.Ovr_Curr_Threshold,
                self.CT_Bypass_Volt_Threshold,
                self.CT_Bypass_Curr_Threshold,
                self.CT_Bypass_Avg_Curr_Threshold,
                self.CT_Bypass_Residual_Curr_Threshold,
                self.OverLoad_Threshold
            ))


