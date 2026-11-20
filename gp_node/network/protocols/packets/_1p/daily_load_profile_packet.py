import datetime
from gp_node.utils import TamperFlag
import gp_node.utils.serialize as serialize
from gp_node.utils.serialize import *

class DailyLoadProfilePacket(object):

    def __init__(self):
        self.date_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.daily_real_energy_imp = 0
        self.daily_apparent_energy_imp = 0
        self.daily_active_energy_exp = 0
        self.daily_apparent_energy_exp = 0
        

    def __str__(self):
        return ("date_time                      : {} \n"
                "Daily Active Energy Import     : {} KWh\n"
                "Daily Apparent Energy Import   : {} KVAh\n"
                "Daily Active Energy Export     : {} KWh\n"
                "Daily Apparent Energy Export   : {} KVAh").format(self.date_time,
                                                self.daily_real_energy_imp,
                                                self.daily_apparent_energy_imp,
                                                self.daily_active_energy_exp,
                                                self.daily_apparent_energy_exp)

    def serialize(self):
        # TODO: Implement this
        raise Exception("Not implemented.")


    def deserialize(self, payload):
        """
        It is assumed that payload size is 14
        """
        byte = payload
        unix_time = serialize.deserialize_uint32(byte[0:4], "reverse")
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.date_time = unix_time_zero + datetime.timedelta(0, unix_time)
        self.daily_real_energy_imp = serialize.deserialize_uint32(byte[4:8], "reverse")/100.0
        self.daily_apparent_energy_imp = serialize.deserialize_uint32(byte[8:12], "reverse")/100.0
        self.daily_active_energy_exp = serialize.deserialize_uint32(byte[12:16], "reverse")/100.0
        self.daily_apparent_energy_exp = serialize.deserialize_uint32(byte[16:20], "reverse")/100.0
