import datetime
import gp_node.utils.serialize as serialize
import time
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils.serialize import deserialize_uint32

class CrcDataPacket3P(object):

    def __init__(self):
        self.return_params = {  "crc_block_01"   : 0,
                                "crc_block_02"   : 0,
                                "crc_block_03"   : 0,
                                "crc_block_04"   : 0,
                                "crc_block_05"   : 0,
                                "crc_block_06"   : 0,
                                "crc_block_07"   : 0,
                                "crc_block_08"   : 0,
                                "crc_block_09"   : 0,
                                "crc_block_10"   : 0,
                                "crc_block_11"   : 0,
                                "crc_block_12"   : 0,
                                "crc_block_13"   : 0,
                                "crc_block_14"   : 0,
                                "crc_block_15"   : 0,
                                "crc_block_16"   : 0,
                                "crc_block_17"   : 0,
                                "crc_block_18"   : 0,
                                "crc_block_19"   : 0,
                                "crc_block_20"   : 0,
                                "crc_block_21"   : 0,
                                "crc_block_22"   : 0,
                                "crc_block_23"   : 0,
                                "crc_block_24"   : 0,
                                "crc_block_25"   : 0,
                                "crc_block_26"   : 0,
                                "crc_block_27"   : 0,
                                "crc_block_28"   : 0,
                                "crc_block_29"   : 0,
                                "crc_block_30"   : 0,
                                "crc_block_31"   : 0,
                                "crc_block_32"   : 0
                                }


    def __str__(self):
        return ("crc_block_01   : {}\n"
                "crc_block_02   : {}\n"
                "crc_block_03   : {}\n"   
                "crc_block_04   : {}\n"    
                "crc_block_05   : {}\n"    
                "crc_block_06   : {}\n"    
                "crc_block_07   : {}\n"    
                "crc_block_08   : {}\n"    
                "crc_block_09   : {}\n"    
                "crc_block_10   : {}\n"     
                "crc_block_11   : {}\n"     
                "crc_block_12   : {}\n"     
                "crc_block_13   : {}\n"     
                "crc_block_14   : {}\n"   
                "crc_block_15   : {}\n"   
                "crc_block_16   : {}\n"
                "crc_block_17   : {}\n"
                "crc_block_18   : {}\n"
                "crc_block_19   : {}\n"   
                "crc_block_20   : {}\n"    
                "crc_block_21   : {}\n"    
                "crc_block_22   : {}\n"    
                "crc_block_23   : {}\n"    
                "crc_block_24   : {}\n"    
                "crc_block_25   : {}\n"    
                "crc_block_26   : {}\n"     
                "crc_block_27   : {}\n"     
                "crc_block_28   : {}\n"     
                "crc_block_29   : {}\n"     
                "crc_block_30   : {}\n"   
                "crc_block_31   : {}\n"   
                "crc_block_32   : {}\n")\
                .format(self.return_params["crc_block_01"],
                        self.return_params["crc_block_02"],
                        self.return_params["crc_block_03"], 
                        self.return_params["crc_block_04"],
                        self.return_params["crc_block_05"],
                        self.return_params["crc_block_06"], 
                        self.return_params["crc_block_07"], 
                        self.return_params["crc_block_08"], 
                        self.return_params["crc_block_09"], 
                        self.return_params["crc_block_10"], 
                        self.return_params["crc_block_11"], 
                        self.return_params["crc_block_12"], 
                        self.return_params["crc_block_13"],
                        self.return_params["crc_block_14"], 
                        self.return_params["crc_block_15"],
                        self.return_params["crc_block_16"],
                        self.return_params["crc_block_17"],
                        self.return_params["crc_block_18"],
                        self.return_params["crc_block_19"], 
                        self.return_params["crc_block_20"],
                        self.return_params["crc_block_21"],
                        self.return_params["crc_block_22"], 
                        self.return_params["crc_block_23"], 
                        self.return_params["crc_block_24"], 
                        self.return_params["crc_block_25"], 
                        self.return_params["crc_block_26"], 
                        self.return_params["crc_block_27"], 
                        self.return_params["crc_block_28"], 
                        self.return_params["crc_block_29"],
                        self.return_params["crc_block_30"], 
                        self.return_params["crc_block_31"],
                        self.return_params["crc_block_32"])

    def deserialize_crc_packet1(self,payload):
        bytes = bytearray()
        bytes = payload
        self.return_params["crc_block_01"]  = serialize.deserialize_uint16(bytes[0:2])
        self.return_params["crc_block_02"]  = serialize.deserialize_uint16(bytes[2:4]) 
        self.return_params["crc_block_03"]  = serialize.deserialize_uint16(bytes[4:6])  
        self.return_params["crc_block_04"]  = serialize.deserialize_uint16(bytes[6:8])
        self.return_params["crc_block_05"]  = serialize.deserialize_uint16(bytes[8:10]) 
        self.return_params["crc_block_06"]  = serialize.deserialize_uint16(bytes[10:12]) 
        self.return_params["crc_block_07"]  = serialize.deserialize_uint16(bytes[12:14])  
        self.return_params["crc_block_08"]  = serialize.deserialize_uint16(bytes[14:16]) 
        self.return_params["crc_block_09"]  = serialize.deserialize_uint16(bytes[16:18]) 
        self.return_params["crc_block_10"]  = serialize.deserialize_uint16(bytes[18:20]) 
        self.return_params["crc_block_11"]  = serialize.deserialize_uint16(bytes[20:22]) 
        self.return_params["crc_block_12"]  = serialize.deserialize_uint16(bytes[22:24])
        self.return_params["crc_block_13"]  = serialize.deserialize_uint16(bytes[24:26]) 
        self.return_params["crc_block_14"]  = serialize.deserialize_uint16(bytes[26:28]) 
        self.return_params["crc_block_15"]  = serialize.deserialize_uint16(bytes[28:30])
        self.return_params["crc_block_16"]  = serialize.deserialize_uint16(bytes[30:32])
        self.return_params["crc_block_17"]  = serialize.deserialize_uint16(bytes[32:34])
        self.return_params["crc_block_18"]  = serialize.deserialize_uint16(bytes[34:36]) 
        self.return_params["crc_block_19"]  = serialize.deserialize_uint16(bytes[36:38])  
        self.return_params["crc_block_20"]  = serialize.deserialize_uint16(bytes[38:40])
        self.return_params["crc_block_21"]  = serialize.deserialize_uint16(bytes[40:42]) 
        self.return_params["crc_block_22"]  = serialize.deserialize_uint16(bytes[42:44]) 
        self.return_params["crc_block_23"]  = serialize.deserialize_uint16(bytes[44:46])  
        self.return_params["crc_block_24"]  = serialize.deserialize_uint16(bytes[46:48]) 
        self.return_params["crc_block_25"]  = serialize.deserialize_uint16(bytes[48:50]) 
        self.return_params["crc_block_26"]  = serialize.deserialize_uint16(bytes[50:52]) 
        self.return_params["crc_block_27"]  = serialize.deserialize_uint16(bytes[52:54]) 
        self.return_params["crc_block_28"]  = serialize.deserialize_uint16(bytes[54:56])
        self.return_params["crc_block_29"]  = serialize.deserialize_uint16(bytes[56:58]) 
        self.return_params["crc_block_30"]  = serialize.deserialize_uint16(bytes[58:60]) 
        self.return_params["crc_block_31"]  = serialize.deserialize_uint16(bytes[60:62])
        self.return_params["crc_block_32"]  = serialize.deserialize_uint16(bytes[62:64])


    def get_crc_packet1(self):
        return ("crc_block_01   : {}\n"
                "crc_block_02   : {}\n"
                "crc_block_03   : {}\n"   
                "crc_block_04   : {}\n"    
                "crc_block_05   : {}\n"    
                "crc_block_06   : {}\n"    
                "crc_block_07   : {}\n"    
                "crc_block_08   : {}\n"    
                "crc_block_09   : {}\n"    
                "crc_block_10   : {}\n"     
                "crc_block_11   : {}\n"     
                "crc_block_12   : {}\n"     
                "crc_block_13   : {}\n"     
                "crc_block_14   : {}\n"   
                "crc_block_15   : {}\n"   
                "crc_block_16   : {}\n"
                "crc_block_17   : {}\n"
                "crc_block_18   : {}\n"
                "crc_block_19   : {}\n"   
                "crc_block_20   : {}\n"    
                "crc_block_21   : {}\n"    
                "crc_block_22   : {}\n"    
                "crc_block_23   : {}\n"    
                "crc_block_24   : {}\n"    
                "crc_block_25   : {}\n"    
                "crc_block_26   : {}\n"     
                "crc_block_27   : {}\n"     
                "crc_block_28   : {}\n"     
                "crc_block_29   : {}\n"     
                "crc_block_30   : {}\n"   
                "crc_block_31   : {}\n"   
                "crc_block_32   : {}\n")\
                .format(self.return_params["crc_block_01"],
                        self.return_params["crc_block_02"],
                        self.return_params["crc_block_03"], 
                        self.return_params["crc_block_04"],
                        self.return_params["crc_block_05"],
                        self.return_params["crc_block_06"], 
                        self.return_params["crc_block_07"], 
                        self.return_params["crc_block_08"], 
                        self.return_params["crc_block_09"], 
                        self.return_params["crc_block_10"], 
                        self.return_params["crc_block_11"], 
                        self.return_params["crc_block_12"], 
                        self.return_params["crc_block_13"],
                        self.return_params["crc_block_14"], 
                        self.return_params["crc_block_15"],
                        self.return_params["crc_block_16"],
                        self.return_params["crc_block_17"],
                        self.return_params["crc_block_18"],
                        self.return_params["crc_block_19"], 
                        self.return_params["crc_block_20"],
                        self.return_params["crc_block_21"],
                        self.return_params["crc_block_22"], 
                        self.return_params["crc_block_23"], 
                        self.return_params["crc_block_24"], 
                        self.return_params["crc_block_25"], 
                        self.return_params["crc_block_26"], 
                        self.return_params["crc_block_27"], 
                        self.return_params["crc_block_28"], 
                        self.return_params["crc_block_29"],
                        self.return_params["crc_block_30"], 
                        self.return_params["crc_block_31"],
                        self.return_params["crc_block_32"])
