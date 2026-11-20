import datetime
from gp_node.utils import TamperFlag
import gp_node.utils.serialize as serialize
from gp_node.utils.serialize import *

class Bundle(object):

    def __init__(self):
        self.date_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.R_AvgCurrent = 0.0
        self.Y_AvgCurrent = 0.0
        self.B_AvgCurrent = 0.0
        self.R_AvgVoltage = 0.0
        self.Y_AvgVoltage = 0.0
        self.B_AvgVoltage = 0.0
        self.block_active_energy_imp = 0.0
        self.block_apparent_energy_imp = 0.0
        self.block_active_energy_exp = 0.0
        self.block_apparent_energy_exp = 0.0
        self.block_reactive_energy_quadrant1 = 0.0
        self.block_reactive_energy_quadrant2 = 0.0
        self.block_reactive_energy_quadrant3 = 0.0
        self.block_reactive_energy_quadrant4 = 0.0


    def __str__(self):
        return ("date_time                      : {} \n"
                "R-AvgCurrent                   : {} A\n"
                "Y-AvgCurrent                   : {} A\n"
                "B-AvgCurrent                   : {} A\n"
                "R-AvgVoltage                   : {} V\n"
                "Y-AvgVoltage                   : {} V\n"
                "B-AvgVoltage                   : {} V\n"
                "Block Active Energy Import     : {} KWh\n"
                "Block Apparent Energy Import   : {} KVAh\n"
                "Block Active Energy Export     : {} KWh\n"
                "Block Apparent Energy Export   : {} KVAh\n"
                "Block Reactive Energy QI       : {} KVArh\n"
                "Block Reactive Energy QII      : {} KVArh\n"
                "Block Reactive Energy QIII     : {} KVArh\n"
                "Block Reactive Energy QIV      : {} KVArh").format(self.date_time,
                                                self.R_AvgCurrent,
                                                self.Y_AvgCurrent,
                                                self.B_AvgCurrent,
                                                self.R_AvgVoltage,
                                                self.Y_AvgVoltage,
                                                self.B_AvgVoltage,
                                                self.block_active_energy_imp,
                                                self.block_apparent_energy_imp,
                                                self.block_active_energy_exp,
                                                self.block_apparent_energy_exp,
                                                self.block_reactive_energy_quadrant1,
                                                self.block_reactive_energy_quadrant2,
                                                self.block_reactive_energy_quadrant3,
                                                self.block_reactive_energy_quadrant4)

    def serialize(self):
        # TODO: Implement this
        raise Exception("Not implemented.")


    def deserialize(self, payload):
        """
        It is assumed that payload size is 30
        """
        byte = payload
        unix_str_time = serialize.deserialize_uint32(byte[0:4], "reverse")
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.date_time = unix_time_zero + datetime.timedelta(0, unix_time)
        self.block_active_energy_imp    = serialize.deserialize_uint32(byte[4:8])/100.0
        self.block_apparent_energy_imp  = serialize.deserialize_uint32(byte[8:12], "reverse")/100.0
        self.block_active_energy_exp    = serialize.deserialize_uint32(byte[12:16], "reverse")/100.0
        self.block_apparent_energy_exp  = serialize.deserialize_uint32(byte[16:20], "reverse")/100.0
        self.block_reactive_energy_quadrant1 = serialize.deserialize_uint32(byte[20:24], "reverse")/100.0
        self.block_reactive_energy_quadrant2 = serialize.deserialize_uint32(byte[24:28], "reverse")/100.0
        self.block_reactive_energy_quadrant3 = serialize.deserialize_uint32(byte[28:32], "reverse")/100.0
        self.block_reactive_energy_quadrant4 = serialize.deserialize_uint32(byte[32:36], "reverse")/100.0
        self.R_AvgVoltage = serialize.deserialize_uint32(byte[36:40], "reverse")/1000.0
        self.Y_AvgVoltage = serialize.deserialize_uint32(byte[40:44], "reverse")/1000.0
        self.B_AvgVoltage = serialize.deserialize_uint32(byte[44:48], "reverse")/1000.0
        self.R_AvgCurrent = serialize.deserialize_uint32(byte[48:52], "reverse")/1000.0
        self.Y_AvgCurrent = serialize.deserialize_uint32(byte[52:56], "reverse")/1000.0
        self.B_AvgCurrent = serialize.deserialize_uint32(byte[56:60], "reverse")/1000.0
        
