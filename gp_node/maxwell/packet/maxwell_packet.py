"""
Definition of the MaxwellPacket class, used for communication between the
Maxwell meter and the Node.
"""

import gp_node.utils.serialize as serialize
from gp_node.utils import TamperFlag
from colorama import Fore
import datetime

class DeserializeError(Exception):
    def __str__(self):
        return "Could not deserialize packet."


class SerializeError(Exception):
    def __str__(self):
        return "Could not serialize packet."

class MaxwellPacket:

    """
    The MaxwellPacket implements the serialization and deserialization of
    periodic packets which are sent by the Maxwell board. This class is 
    used in the maxwell-packet-monitor for implementing the reading of
    packets sent by the Maxwell board. This class is also used in
    maxwell-simulator for simulating the packets sent by the Maxwell Board.

    :param int protocol_version: Should be the constant 2 as of now
    :param int maxwell_meter_num: Decided by meter version scheme used at Maxwell
    :param int maxwell_board_version: unused as of now
    :param datetime.datetime time: time as perceived by the Maxwell RTC
    :param float voltage: in volts
    :param float phase_current: in amps
    :param float neutral_current: in amps
    :param float active_power: in watts
    :param float reactive_power: in VAr
    :param float total_power: in VA
    :param float apparent_energy: in volt-ampere-hour
    :param float power_factor: should be in range -1.0 to 1.0
    :param float frequency: in hertz
    :param float active_energy: in watt-hour
    :param float reactive_energy: in var-hour
    :param list tamper_events: list of TamperFlag
    """

    def __init__(self):
        self.protocol_version = 0
        self.maxwell_meter_num = 0
        self.maxwell_board_version = 0
        self.time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.voltage = 0.0
        self.phase_current = 0.0
        self.neutral_current = 0.0
        self.active_power = 0.0
        self.reactive_power = 0.0
        self.total_power = 0.0
        self.apparent_energy = 0.0
        self.power_factor = 0.0
        self.frequency = 0.0
        self.active_energy = 0.0
        self.reactive_energy = 0.0
        self.tamper_events = []


    def __str__(self):
        output = ""
        output += Fore.GREEN + "protocol_version: " + Fore.WHITE + str(self.protocol_version) + "\n"
        output += Fore.GREEN + "maxwell_meter_num: " +  Fore.WHITE + str(self.maxwell_meter_num) + "\n"
        output += Fore.GREEN + "maxwell_board_version: " + Fore.WHITE +  str(self.maxwell_board_version) + "\n"
        output += Fore.GREEN + "time: " + Fore.WHITE +  str(self.time) + "\n"
        output += Fore.GREEN + "voltage: " + Fore.WHITE +  str(self.voltage) + " Volts\n"
        output += Fore.GREEN + "phase_current: " + Fore.WHITE +  str(self.phase_current) + " Amps\n"
        output += Fore.GREEN + "neutral_current: " + Fore.WHITE +  str(self.neutral_current) + " Amps\n"
        output += Fore.GREEN + "active_power: " + Fore.WHITE +  str(self.active_power) + " Watts\n"
        output += Fore.GREEN + "reactive_power: " + Fore.WHITE +  str(self.reactive_power) + " VAr\n"
        output += Fore.GREEN + "total_power: " + Fore.WHITE +  str(self.total_power) + " VA\n"
        output += Fore.GREEN + "apparent_energy: " + Fore.WHITE +  str(self.apparent_energy) + " Watts\n"
        output += Fore.GREEN + "power_factor: " + Fore.WHITE +  str(self.power_factor) + "\n"
        output += Fore.GREEN + "frequency: " + Fore.WHITE +  str(self.frequency) + " Hz\n"
        output += Fore.GREEN + "active_energy: " + Fore.WHITE +  str(self.active_energy) + " Watt-hour\n"
        output += Fore.GREEN + "reactive_energy: " + Fore.WHITE +  str(self.reactive_energy) + " VAr-hour\n"
        output += Fore.GREEN + "tamper_events: " + Fore.WHITE +  str(self.tamper_events) + "\n"
        return output


    def serialize(self):
        """
        Serializes the contents of the packets into a bytearray. This function is used
        by the maxwell-simulator for sending MaxwellPackets on the serial port.

        :returns: serialized contents of the Packet
        :rtype: bytearray()
        """
        buf = bytearray()
        try:
            date_tmp = (self.time.year) + \
                    (self.time.month)*(2**16) + (self.time.day)*(2**24)
            seconds_since_midnight = \
                    int((self.time - datetime.datetime(self.time.year,
                                                            self.time.month,
                                                            self.time.day,
                                                            0, 0, 0)).total_seconds())
            buf.extend(serialize.serialize_uint8(self.protocol_version))
            buf.extend(serialize.serialize_uint32(self.maxwell_meter_num))
            buf.extend(serialize.serialize_uint8(self.maxwell_board_version))
            buf.extend(serialize.serialize_uint32(date_tmp))
            buf.extend(serialize.serialize_uint32(seconds_since_midnight))
            buf.extend(serialize.serialize_int32(int(1000*self.voltage)))
            buf.extend(serialize.serialize_int32(int(1000*self.phase_current)))
            buf.extend(serialize.serialize_int32(int(1000*self.neutral_current)))
            buf.extend(serialize.serialize_int32(int(1000*self.active_power)))
            buf.extend(serialize.serialize_int32(int(1000*self.reactive_power)))
            buf.extend(serialize.serialize_int32(int(1000*self.total_power)))
            buf.extend(serialize.serialize_int32(int(1000*self.apparent_energy)))
            buf.extend(serialize.serialize_int16(int(1000*self.power_factor)))
            buf.extend(serialize.serialize_uint16(int(10*self.frequency)))
            buf.extend(serialize.serialize_int32(int(self.active_energy)))
            buf.extend(serialize.serialize_int32(int(self.reactive_energy)))
            tamper_integer = 0
            if TamperFlag("EARTH") in self.tamper_events:
                tamper_integer += 1
            if TamperFlag("LINE_LOAD_REVERSAL") in self.tamper_events:
                tamper_integer += 2
            if TamperFlag("MAGNETIC") in self.tamper_events:
                tamper_integer += 4
            if TamperFlag("COVER_OPEN") in self.tamper_events:
                tamper_integer += 8
            if TamperFlag("NEUTRAL_MISSING") in self.tamper_events:
                tamper_integer += 16
            if TamperFlag("NEUTRAL_DISTURBANCE") in self.tamper_events:
                tamper_integer += 32
            buf.extend(serialize.serialize_uint8(tamper_integer))
        except serialize.SerializeValueError:
            raise SerializeError
        return buf


    def deserialize(self, buf):
        """
        Deserialzes buf. Note that if the time field in the buf entry is
        not a valid timestamp (ie, timestamp cannot be converted into a
        valid datetime.datetime value), then the self.time is defaulted to
        datetime.datetime(1970, 1, 1, 0, 0, 0)

        :param buf: should be a 58 byte bytearray
        :type buf: bytearray
        """
        try:
            self.protocol_version = serialize.deserialize_uint8(buf[0:1]) 
            self.maxwell_meter_num = serialize.deserialize_uint32(buf[1:5]) 
            self.maxwell_board_version = serialize.deserialize_uint8(buf[5:6]) 
            date_tmp = serialize.deserialize_uint32(buf[6:10]) 
            seconds_since_midnight = serialize.deserialize_uint32(buf[10:14]) 
            voltage_tmp = serialize.deserialize_int32(buf[14:18]) 
            phase_current_tmp = serialize.deserialize_int32(buf[18:22]) 
            neutral_current_tmp = serialize.deserialize_int32(buf[22:26]) 
            active_power_tmp = serialize.deserialize_int32(buf[26:30]) 
            reactive_power_tmp = serialize.deserialize_int32(buf[30:34]) 
            total_power_tmp = serialize.deserialize_int32(buf[34:38]) 
            apparent_energy_tmp = serialize.deserialize_int32(buf[38:42]) 
            power_factor_tmp = serialize.deserialize_int16(buf[42:44]) 
            frequency_tmp = serialize.deserialize_uint16(buf[44:46]) 
            active_energy_tmp = serialize.deserialize_int32(buf[46:50]) 
            reactive_energy_tmp = serialize.deserialize_int32(buf[50:54]) 
            tamper_events_tmp = serialize.deserialize_int8(buf[54:55]) 

            year = (date_tmp % 2**16)
            month = (date_tmp/2**16) % 2**8
            day = (date_tmp/2**24)
            try:
                self.time = datetime.datetime(year, month, day, 0, 0, 0) + \
                        datetime.timedelta(seconds=seconds_since_midnight)
            except ValueError as err:
                self.time = datetime.datetime(1970, 1, 1, 0, 0, 0)
            self.voltage = float(voltage_tmp)/1000
            self.phase_current = float(phase_current_tmp)/1000
            self.neutral_current = float(neutral_current_tmp)/1000
            self.active_power = float(active_power_tmp)/1000
            self.reactive_power = float(reactive_power_tmp)/1000
            self.total_power = float(total_power_tmp)/1000
            self.apparent_energy = float(apparent_energy_tmp)/1000
            self.power_factor = float(power_factor_tmp)/1000
            self.frequency = float(frequency_tmp)/10
            self.active_energy = float(active_energy_tmp)
            self.reactive_energy = float(reactive_energy_tmp)

            if (tamper_events_tmp/2**0 % 2) == 1:
                self.tamper_events.append(TamperFlag("EARTH"))
            if (tamper_events_tmp/2**1 % 2) == 1:
                self.tamper_events.append(TamperFlag("LINE_LOAD_REVERSAL"))
            if (tamper_events_tmp/2**2 % 2) == 1:
                self.tamper_events.append(TamperFlag("MAGNETIC"))
            if (tamper_events_tmp/2**3 % 2) == 1:
                self.tamper_events.append(TamperFlag("COVER_OPEN"))
            if (tamper_events_tmp/2**4 % 2) == 1:
                self.tamper_events.append(TamperFlag("NEUTRAL_MISSING"))
            if (tamper_events_tmp/2**5 % 2) == 1:
                self.tamper_events.append(TamperFlag("NEUTRAL_DISTURBANCE"))

        except serialize.DeserializeValueError:
            raise DeserializeError
