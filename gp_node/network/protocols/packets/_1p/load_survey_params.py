import datetime
import time
from gp_node.utils import TamperFlag
import gp_node.utils.serialize as serialize
from gp_node.utils.serialize import deserialize_uint32


class LoadSurveyParams(object):

    def __init__(self):
        self.interval = 0
        self.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        # self.status = 0

    def __str__(self):
        # if self.status == 0:
        #     isenabled = "survey disabled"
        # else:
        #     isenabled = "survey enabled"
        return "start_time: {}\ninterval: {}".format(self.start_time, self.interval)

    def serialize(self):
        payload = bytearray()
        seconds_since_epoch = int((self.start_time - datetime.datetime(1970,1,1)).total_seconds())
        payload.extend(serialize.serialize_uint32(seconds_since_epoch, "reverse"))
        payload.extend(serialize.serialize_uint8(self.status))
        payload.extend(serialize.serialize_uint32(self.interval))
        #payload.extend(serialize.serialize_uint8(self.status))
        return payload

    def deserialize(self, payload):
        unix_str_time = str(deserialize_uint32(payload[0:4], "reverse"))
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.start_time = unix_time_zero + datetime.timedelta(0, unix_time)
        self.interval = serialize.deserialize_uint8(payload[4:5], "reverse")
        #self.status = serialize.deserialize_uint8(payload[5:6])


