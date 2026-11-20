import time
import gp_node.utils.serialize as serialize
import datetime

class MaximumDemandPacket:


    def __init__(self, MD_month):
        self.MD_month = MD_month
        self.MD_value = 0
        self.MD_timestamp = datetime.datetime(1970, 1, 1, 0, 0, 0)

    def __str__(self):
        return ("MD_month: {}\n"
                "MD_value: {} watts\n"
                "MD_timestamp: {}\n").format(self.MD_month - 7,
                                       self.MD_value,
                                       self.MD_timestamp)

    def deserialize(self, payload):
        """
        It is assumed that payload size is 12
        """
        
        self.MD_value = payload[0] + (payload[1] << 8) + (payload[2] << 16) + (payload[3] << 24) 
        year_tmp = serialize.deserialize_uint16(payload[4:6],"reverse")
        month_tmp = serialize.deserialize_uint8(payload[6:7])
        day_tmp = serialize.deserialize_uint8(payload[7:8])
        hour_tmp = serialize.deserialize_uint8(payload[9:10])
        minute_tmp = serialize.deserialize_uint8(payload[10:11])
        second_tmp = serialize.deserialize_uint8(payload[11:12])
        try:
            self.MD_timestamp = datetime.datetime(year_tmp, month_tmp, day_tmp,
                                                  hour_tmp, minute_tmp, second_tmp)
        except Exception as e:
            print (e)
            self.MD_timestamp = datetime.datetime(1970, 1, 1, 0, 0, 0)
