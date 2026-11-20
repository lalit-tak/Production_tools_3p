import datetime
import gp_node.utils.serialize as serialize

class LogPacketN:

    def __init__(self):
        self.timestamp = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.message = ""

    def __str__(self):
        return "{}: {}".format(self.timestamp, self.message)

    def deserialize(self, payload):
        new_payload = bytearray()
        new_payload.append(payload[1])
        new_payload.append(payload[0])
        year_tmp = serialize.deserialize_uint16(new_payload[0:2])
        month_tmp = serialize.deserialize_uint8(payload[2:3])
        day_tmp = serialize.deserialize_uint8(payload[3:4])
        hour_tmp = serialize.deserialize_uint8(payload[5:6])
        minute_tmp = serialize.deserialize_uint8(payload[6:7])
        second_tmp = serialize.deserialize_uint8(payload[7:8])
        try:
            self.timestamp = datetime.datetime(year_tmp, month_tmp, day_tmp,
                                                hour_tmp, minute_tmp, second_tmp)
        except:
            self.timestamp = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.message = str(payload[8:])
