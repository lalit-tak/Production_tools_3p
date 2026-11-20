import datetime
from gp_node.utils import TamperFlag
import gp_node.utils.serialize as serialize

class SyncstreamBundle(object):

    def __init__(self):
        self.beat_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.voltage = 0
        self.current = 0
        self.active_power = 0
        self.power_factor = 0
        self.frequency = 0
        self.active_energy = 0
        self.reactive_energy = 0
        self.apparent_energy = 0
        # self.credits = 0
        # self.energy_per_credit = 0
        self.tamper_flags = []
        

    def __str__(self):
        return ("beat_time: {} \n"
                "voltage: {} V\n"
                "current: {} A\n"
                "active_power: {} W\n"
                "power_factor: {}\n"
                "frequency: {}\n"
                "active_energy: {} Wh\n"
                "reactive_energy: {} VArh\n"
                "apparent_energy: {} VAh\n"
                # "credits: {}\n"
                # "energy_per_credit: {}\n"
                "tamper_flags: {}").format(self.beat_time,
                                             self.voltage,
                                             self.current,
                                             self.active_power,
                                             self.power_factor,
                                             self.frequency,
                                             self.active_energy,
                                             self.reactive_energy,
                                             self.apparent_energy,
                                             # self.credits,
                                             # self.energy_per_credit,
                                             self.tamper_flags)

    def serialize(self):
        # TODO: Implement this
        raise Exception("Not implemented.")


    def deserialize(self, payload):
        """
        It is assumed that payload size is 30
        """
        buf = payload

        unix_str_time = str(serialize.deserialize_uint32(buf[1:5]))
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.beat_time = unix_time_zero + datetime.timedelta(0, unix_time)

        self.voltage = serialize.deserialize_int32(buf[5:9])/1000.0 # mV -> V
        self.current = serialize.deserialize_int32(buf[9:13])/1000.0 # mA -> A
        self.active_power = serialize.deserialize_int32(buf[13:17])/1000.0 # mW -> W
        self.power_factor = serialize.deserialize_int16(buf[17:19])/1000.0 # p.f.
        self.frequency = serialize.deserialize_int16(buf[19:21])/10.0 # Hz*10 -> Hz
        self.active_energy = serialize.deserialize_int32(buf[21:25])/1.0 # Wh
        self.reactive_energy = serialize.deserialize_int32(buf[25:29])/1.0 # VArh
        self.apparent_energy = serialize.deserialize_int32(buf[29:33])/1.0 # VAh

        # self.credits = serialize.deserialize_int32(buf[33:37]) # credits
        # self.energy_per_credit = serialize.deserialize_int32(buf[37:41]) # energy per credit

        flag_byte = buf[33]
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