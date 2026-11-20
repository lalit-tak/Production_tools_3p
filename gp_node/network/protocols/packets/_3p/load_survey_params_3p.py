import datetime
import time
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils import TamperFlag
import gp_node.utils.serialize as serialize


class LoadSurveyParams3P(object):

    def __init__(self):
        self.interval = 0
        self.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.enable = False

    def __str__(self):
        return "Start_time: {}\nInterval: {}\nEnabled: {}".format(self.start_time, self.interval, self.enable)

    def serialize(self):
        payload = bytearray()
        payload.extend(serialize.serialize_uint16(self.start_time.year, "reverse"))
        payload.extend(serialize.serialize_uint8(self.start_time.month))
        payload.extend(serialize.serialize_uint8(self.start_time.day))
        payload.extend(serialize.serialize_uint8(0))
        payload.extend(serialize.serialize_uint8(self.start_time.hour))
        payload.extend(serialize.serialize_uint8(self.start_time.minute))
        payload.extend(serialize.serialize_uint8(self.start_time.second))
        payload.extend(serialize.serialize_uint32(self.interval, "reverse"))
        #payload.extend(serialize.serialize_uint8(self.enable))
        return payload

    def deserialize(self, payload):
        year_tmp = serialize.deserialize_uint16(payload[0:2], "reverse")
        month_tmp = serialize.deserialize_uint8(payload[2:3])
        day_tmp = serialize.deserialize_uint8(payload[3:4])
        hour_tmp = serialize.deserialize_uint8(payload[5:6])
        minute_tmp = serialize.deserialize_uint8(payload[6:7])
        second_tmp = serialize.deserialize_uint8(payload[7:8])
        self.start_time = datetime.datetime(year_tmp, month_tmp, day_tmp,
                                            hour_tmp, minute_tmp, second_tmp)
        
        self.interval = serialize.deserialize_uint32(payload[8:12], "reverse")
        tmp = serialize.deserialize_uint8(payload[12:13])
        if (tmp == 0):
            self.enable = False
        else:
            self.enable = True
        '''
        print self.start_time
        print self.interval
        print self.enable
        '''

