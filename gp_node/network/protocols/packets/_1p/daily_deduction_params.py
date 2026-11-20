import time
import gp_node.utils.serialize as serialize
import datetime


class DailyDeductionParams(object):

    def __init__(self):
        self.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.days_per_deduction = 0
        self.min_credits_per_deduction = 0

    def __str__(self):
        return ("start_time: {}\n"
                "min_credits_per_deduction: {}\n"
                "days_per_deduction: {}").format(self.start_time,
                                                self.min_credits_per_deduction,
                                                self.days_per_deduction)

    def serialize(self):
        payload = bytearray()
        temp = serialize.serialize_uint16(self.start_time.year)
        payload.append(temp[1])
        payload.append(temp[0])
        payload.extend(serialize.serialize_uint8(self.start_time.month))
        payload.extend(serialize.serialize_uint8(self.start_time.day))
        payload.extend(serialize.serialize_uint8(0))
        payload.extend(serialize.serialize_uint8(self.start_time.hour))
        payload.extend(serialize.serialize_uint8(self.start_time.minute))
        payload.extend(serialize.serialize_uint8(self.start_time.second))

        temp = serialize.serialize_uint16(self.min_credits_per_deduction)
        payload.append(temp[1])
        payload.append(temp[0])

        temp = serialize.serialize_uint16(self.days_per_deduction)
        payload.append(temp[1])
        payload.append(temp[0])
        return payload


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
        self.start_time = datetime.datetime(year_tmp, month_tmp, day_tmp,
                                            hour_tmp, minute_tmp, second_tmp)
        new_payload = bytearray()
        new_payload.append(payload[9])
        new_payload.append(payload[8])
        new_payload.append(payload[11])
        new_payload.append(payload[10])
        self.min_credits_per_deduction = serialize.deserialize_uint16(new_payload[0:2])
        self.days_per_deduction = serialize.deserialize_uint16(new_payload[2:4])

