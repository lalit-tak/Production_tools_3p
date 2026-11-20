import gp_node.utils.serialize as serialize
from gp_node.utils import TamperFlag
# import time
# import datetime


class   IP_RelayPara(object):

    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        self.return_params = {"control_mode":0, 
                              "control_state": 0,
                              "relay_state": 0,
                              "switch_off_reason": 0,
                              "phase_wise_state" : [],
                              "auto_manual_state": 0,
                              "tariff_type":0}


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

        a = bytes[0]
        self.return_params["control_mode"]          =  "Mode " + str(a)

        a = bytes[1]
        if (1 == a):
            self.return_params["control_state"]     =  "CONNECTED"
        elif (2 == a):
            self.return_params["control_state"]     =  "READY FOR RE-CONNECTION"
        elif (0 == a):
            self.return_params["control_state"]     =  "DISCONNECTED"

        a = bytes[2]
        if (1 == a):
            self.return_params["relay_state"]     =  "ON"
        elif (0 == a):
            self.return_params["relay_state"]     =  "OFF"

        a = bytes[3]
        if (0 == a):
            self.return_params["switch_off_reason"]     =  "none"
        elif (1 == (a & 0x01)):
            self.return_params["switch_off_reason"]     =  "Over Power"
        elif (2 == (a & 0x02)):
            self.return_params["switch_off_reason"]     =  "Cover Open"
        elif (4 == (a & 0x04)):
            self.return_params["switch_off_reason"]     =  "Over Current"
        elif (8 == (a & 0x08)):
            self.return_params["switch_off_reason"]     =  "Remote"
        elif (16 == (a & 0x10)):
            self.return_params["switch_off_reason"]     =  "Account Empty"
        elif (32 == (a & 0x20)):
            self.return_params["switch_off_reason"]     =  "High Load"
        elif (64 == (a & 0x40)):
            self.return_params["switch_off_reason"]     =  "Manual"
        elif (128 == (a & 0x80)):
            self.return_params["switch_off_reason"]     =  "Manual On with Acc Empty"

    
    def get_packet_bundle(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return (" Control Mode      : {} \n"
                " Control State     : {} \n"
                " Output State      : {} \n"
                " Off Reason        : {} \n"
                )\
                .format(self.return_params["control_mode"],
                        self.return_params["control_state"],
                        self.return_params["relay_state"],
                        self.return_params["switch_off_reason"])

    def deserialize_ph_packet_bundle(self,payload):
        """
        Deserializes the input payload and populates the data to the default
        dictionary.This API needs to be used to retrieve information from the 
        reply bytestream.
        :param payload:input bytestream
        :return :none
        """
        bytes = bytearray()
        bytes = payload

        self.return_params["control_mode"]          =  "Mode " + str(bytes[0])

        if (1 == bytes[1]):
            self.return_params["control_state"]     =  "CONNECTED"
        elif (2 == bytes[1]):
            self.return_params["control_state"]     =  "READY FOR RE-CONNECTION"
        elif (0 == bytes[1]):
            self.return_params["control_state"]     =  "DISCONNECTED"

        if (1 == bytes[2]):
            self.return_params["relay_state"]     =  "ON"
        elif (0 == bytes[2]):
            self.return_params["relay_state"]     =  "OFF"

        a = bytes[3]
        if (0 == a):
            self.return_params["switch_off_reason"]     =  "none"
        elif (1 == (a & 0x01)):
            self.return_params["switch_off_reason"]     =  "Over Power"
        elif (2 == (a & 0x02)):
            self.return_params["switch_off_reason"]     =  "Cover Open"
        elif (4 == (a & 0x04)):
            self.return_params["switch_off_reason"]     =  "Over Current"
        elif (8 == (a & 0x08)):
            self.return_params["switch_off_reason"]     =  "Remote"
        elif (16 == (a & 0x10)):
            self.return_params["switch_off_reason"]     =  "Account Empty"
        elif (32 == (a & 0x20)):
            self.return_params["switch_off_reason"]     =  "High Load"
        elif (64 == (a & 0x40)):
            self.return_params["switch_off_reason"]     =  "Manual"
        elif (128 == (a & 0x80)):
            self.return_params["switch_off_reason"]     =  "Manual On with Acc Empty"

        sts = bytes[4]
        state = []
        flag = 0
        while flag < 3:
            temp = sts & (1 << flag)
            if(temp):
                if(flag == 0):
                    state.append("R-Phase ON")
                elif(flag == 1):
                    state.append("Y-Phase ON")
                else:
                    state.append("B-Phase ON")
            else:
                temp = sts & (1 << (flag+4))
                if(temp):
                    if(flag == 0):
                        state.append("R-Phase OFF")
                    elif(flag == 1):
                        state.append("Y-Phase OFF")
                    else:
                        state.append("B-Phase OFF")
            flag = flag + 1
        self.return_params["phase_wise_state"] = state

        if (1 == bytes[5]):
            self.return_params["auto_manual_state"]     =  "AUTO_CONTROL_ON"
        elif (2 == bytes[5]):
            self.return_params["auto_manual_state"]     =  "AUTO_CONTROL_OFF"
        elif (3 == bytes[5]):
            self.return_params["auto_manual_state"]     =  "MANUAL_CONTROL_ON"
        elif (4 == bytes[5]):
            self.return_params["auto_manual_state"]     =  "MANUAL_CONTROL_OFF"
        else:
            self.return_params["auto_manual_state"]     =  "UNKNOWN"

        self.return_params["tariff_type"] = "DG_TARIFF"
        if (1 == bytes[6]&0x01):
            self.return_params["tariff_type"] = "EB_TARIFF"


    
    def get_ph_packet_bundle(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return (" Control Mode      : {} \n"
                " Control State     : {} \n"
                " Output State      : {} \n"
                " Off Reason        : {} \n"
                " Phase wise State  : {} \n"
                " Relay State       : {} \n"
                " Tariff Type       : {} \n"
                )\
                .format(self.return_params["control_mode"],
                        self.return_params["control_state"],
                        self.return_params["relay_state"],
                        self.return_params["switch_off_reason"],
                        self.return_params["phase_wise_state"],
                        self.return_params["auto_manual_state"],
                        self.return_params["tariff_type"])