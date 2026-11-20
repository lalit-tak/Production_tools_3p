import gp_node.utils.serialize as serialize
from gp_node.utils import TamperFlag
# import time
# import datetime


class   IP_MeterPara(object):

    def __init__(self):
        """
        The constructor instantiates a default dictionary to store the ecop data
        """
        self.return_params = {"meter_serial_number":0, 
                              "uid1": 0,
                              "uid2": 0,
                              "uid3": 0,
                              "uid4": 0}


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
        self.return_params["meter_serial_number"]   =  serialize.deserialize_uint32(bytes[0:4])
        self.return_params["uid1"]                  =  hex(serialize.deserialize_uint32(bytes[4:8]))
        self.return_params["uid2"]                  =  hex(serialize.deserialize_uint32(bytes[8:12]))
        self.return_params["uid3"]                  =  hex(serialize.deserialize_uint32(bytes[12:16]))
        self.return_params["uid4"]                  =  hex(serialize.deserialize_uint32(bytes[16:20]))

    
    def get_packet_bundle(self):
        """
        Prints out the stored information in the dictionary.
        Useful along with print statements.
        ex: print EcopDataStreamPacket()
        :param :none
        :return :none
        """
        return (" Meter Serial Number   : {} \n"
                " UID 1                 : {} \n"
                " UID 2                 : {} \n"
                " UID 3                 : {} \n"
                " UID 4                 : {} \n"
                )\
                .format(self.return_params["meter_serial_number"],
                        self.return_params["uid1"],
                        self.return_params["uid2"],
                        self.return_params["uid3"],
                        self.return_params["uid4"])