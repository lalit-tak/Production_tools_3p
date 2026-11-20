import time
import gp_node.utils.serialize as serialize
import datetime

class TamperRecordPacket:


    def __init__(self, tamper_type):
        self.tamper_type = tamper_type
        self.tamper_count = 0
        self.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.end_time = datetime.datetime(1970, 1, 1, 0, 0, 0)

    def __str__(self):
        return ("tamper_type: {}\n"
                "tamper_count: {}\n"
                "start_time: {}\n"
                "end_time: {}\n").format(self.tamper_type,
                                       self.tamper_count,
                                       self.start_time,
                                       self.end_time)

    def deserialize(self, payload):
        """
        It is assumed that payload size is 18
        """
        # byte reverse odd and even entries because of the way (char*)(tamper_record_t) works
        # in node_fw
        new_payload = bytearray()
        for i in range(9):
            new_payload.append(payload[2*i+1])
            new_payload.append(payload[2*i])
        self.tamper_count = serialize.deserialize_uint16(new_payload[0:2])
        year_tmp = serialize.deserialize_uint16(new_payload[2:4])
        month_tmp = serialize.deserialize_uint8(payload[4:5])
        day_tmp = serialize.deserialize_uint8(payload[5:6])
        hour_tmp = serialize.deserialize_uint8(payload[7:8])
        minute_tmp = serialize.deserialize_uint8(payload[8:9])
        second_tmp = serialize.deserialize_uint8(payload[9:10])
        try:
            self.start_time = datetime.datetime(year_tmp, month_tmp, day_tmp,
                                                hour_tmp, minute_tmp, second_tmp)
        except Exception as e:
            print (e)
            self.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)

        year_tmp = serialize.deserialize_uint16(new_payload[10:12])
        month_tmp = serialize.deserialize_uint8(payload[12:13])
        day_tmp = serialize.deserialize_uint8(payload[13:14])
        hour_tmp = serialize.deserialize_uint8(payload[15:16])
        minute_tmp = serialize.deserialize_uint8(payload[16:17])
        second_tmp = serialize.deserialize_uint8(payload[17:18])
        try:
            self.end_time = datetime.datetime(year_tmp, month_tmp, day_tmp,
                                              hour_tmp, minute_tmp, second_tmp)
        except Exception as e:
            print (e)
            self.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)

