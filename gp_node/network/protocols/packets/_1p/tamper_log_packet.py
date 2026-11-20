import time
from gp_node.utils import TamperFlag
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils.serialize import deserialize_uint32
import datetime

class TamperLog(object):

    def __init__(self):
        self.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.end_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.energy_consumed = 0
        self.tamper_flags = []

    def __str__(self):
        return ("start_time: {}\n"
                "end_time: {}\n"
                "energy_consumed: {}\n"
                "tamper_flags: {}\n").format(self.start_time,
                                       self.end_time,
                                       self.energy_consumed,
                                       self.tamper_flags)

    def serialize(self):
        # TODO: Implement this
        raise Exception("Not implemented.")


    def deserialize(self, payload):
        """
        It is assumed that payload size is 14
        """
        unix_str_time = str(deserialize_uint32(payload[1:5]))
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.start_time = unix_time_zero + datetime.timedelta(0, unix_time)

        unix_str_time = str(deserialize_int32(payload[5:9]))
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.end_time = unix_time_zero + datetime.timedelta(0, unix_time)

        self.energy_consumed = deserialize_int32(payload[9:13])

        flag_byte = payload[13]
        self.tamper_events = []
        if flag_byte >= 128:
            raise ValueError("Bit 7 of flag_list was unexpectedly set.")
            flag_byte = flag_byte - 128
        if flag_byte >= 64:
            raise ValueError("Bit 6 of flag_list was unexpectedly set.")
            flag_byte = flag_byte - 64
        if flag_byte >= 32:
            self.tamper_events.append(TamperFlag("NEUTRAL_DISTURBANCE"))
            flag_byte = flag_byte - 32
        if flag_byte >= 16:
            self.tamper_events.append(TamperFlag("NEUTRAL_MISSING"))
            flag_byte = flag_byte - 16
        if flag_byte >= 8:
            self.tamper_events.append(TamperFlag("COVER_OPEN"))
            flag_byte = flag_byte - 8
        if flag_byte >= 4:
            self.tamper_events.append(TamperFlag("MAGNETIC"))
            flag_byte = flag_byte - 4
        if flag_byte >= 2:
            self.tamper_events.append(TamperFlag("LINE_LOAD_REVERSAL"))
            flag_byte = flag_byte - 2
        if flag_byte >= 1:
            self.tamper_events.append(TamperFlag("EARTH"))
            flag_byte = flag_byte - 1
        self.tamper_flags = self.tamper_events