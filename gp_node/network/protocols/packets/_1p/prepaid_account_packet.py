import datetime
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32

import gp_node.utils.serialize as serialize


class PrepaidAccountPacket(object):

    def __init__(self):
        self.whole_credits = 0
        self.allow_negative_credits = "true"
        self.fractional_energy_remaining = 0
        self.energy_per_credit = 0

    def __str__(self):
        float_credits = self.whole_credits + \
                float(self.fractional_energy_remaining)/self.energy_per_credit
        return ("allow_negative_credits : {}\n"
                "whole_credits : {}\n"
                "energy_per_credit : {} watt-seconds\n"
                "accurate_credits : {}\n"
                "fractional_energy_remaining : {} Watt-seconds")\
                .format(self.allow_negative_credits,
                        self.whole_credits,
                        self.energy_per_credit,
                        float_credits,
                        self.fractional_energy_remaining)

    def deserialize(self,payload):
        self.whole_credits = deserialize_int32(payload[0:4],"reverse")
        temp_allow_negative_credits = deserialize_int16(payload[4:6],"reverse")
        self.fractional_energy_remaining = deserialize_int32(payload[6:10],"reverse")
        self.energy_per_credit = deserialize_int32(payload[10:14],"reverse")	
        if temp_allow_negative_credits == 0:
            self.allow_negative_credits = "false"


    def serialize(self):
        raise Exception("Not implemented.")

