import datetime
from gp_node.utils import TamperFlag
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
from gp_node.utils.serialize import deserialize_uint32

class Bundle(object):

    def __init__(self):
        self.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.end_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.voltage = 0
        self.current = 0
        self.demand_power = 0
        self.power_factor = 0
        self.frequency = 0
        self.consumed_active_energy = 0
        self.consumed_apparent_energy = 0
        self.credits = 0
        self.price = 0
        self.tamper_flags = []
        

    def __str__(self):
        return ("start_time: {}\n"
                "end_time: {}\n"
                "voltage: {} V\n"
                "current: {} A\n"
                "demand_power: {} W\n"
                "power_factor: {}\n"
                "frequency: {} Hz\n"
                "consumed_active_energy: {} Wh\n"
                "consumed_apparent_energy: {} VAh\n"
                "credits: {}\n"
                "price: {}\n"
                "tamper_flags: {}").format(self.start_time,
                                        self.end_time,
                                        self.voltage,
                                        self.current,
                                        self.demand_power,
                                        self.power_factor,
                                        self.frequency,
                                        self.consumed_active_energy,
                                        self.consumed_apparent_energy,
                                        self.credits,
                                        self.price,
                                        self.tamper_flags)

    def serialize(self):
        # TODO: Implement this
        raise Exception("Not implemented.")


    def deserialize(self, payload):
        """
        """
        buf = payload
        unix_str_time = str(deserialize_uint32(buf[1:5]))
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.start_time = unix_time_zero + datetime.timedelta(0, unix_time)

        unix_str_time = str(deserialize_uint32(buf[5:9]))
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        self.end_time = unix_time_zero + datetime.timedelta(0, unix_time)

        self.voltage = deserialize_int16(buf[9:11])/10.0 # dV -> V
        self.current = deserialize_int16(buf[11:13])/10.0 # dA -> A
        self.demand_power = deserialize_int16(buf[13:15])*10.0 # W
        self.power_factor = deserialize_int16(buf[15:17])/100.0 # p.f. * 100 -> p.f.
        self.frequency = deserialize_int16(buf[17:19])/10.0 # Hz
        self.consumed_active_energy = deserialize_int16(buf[19:21])*10.0 # Wh
        self.consumed_apparent_energy = deserialize_int16(buf[21:23])*10.0 # Wh
        self.credits = deserialize_int32(buf[23:27]) # credits
        energy_per_credit = int(deserialize_int32(buf[27:31])) # Ws/credit -> credits/kWh 
        self.price = round(float(3600.00*1000.00/energy_per_credit),2)

        flag_byte = buf[31]
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
