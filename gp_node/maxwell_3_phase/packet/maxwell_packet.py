"""
Definition of the MaxwellPacket class, used for communication between the
Maxwell meter and the Node.
"""

import gp_node.utils.serialize as serialize
from tamper_flag import TamperFlag
from status_flag import StatusFlag
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
    """

    def __init__(self):
        self.protocol_version = 0x03
        self.maxwell_meter_num = 123456
        self.time = datetime.datetime(2016, 1, 1, 0, 0, 0)
        self.date = datetime.datetime(2000, 1, 1, 0, 0, 0)
        #------------------------------------------
        self.total_real_energy = 0
        self.total_apparent_energy = 0
        self.total_reactive_energy = 0
        self.lag_only_reactive_energy = 0
        self.lag_only_apparent_energy = 0
        self.lead_only_reactive_energy = 0
        self.lead_only_apparent_energy = 0

        self.total_real_energy_high_res = 0
        self.total_apparent_energy_high_res = 0
        self.total_reactive_energy_high_res = 0
        self.lag_only_reactive_energy_high_res = 0
        self.lag_only_apparent_energy_high_res = 0
        self.lead_only_reactive_energy_high_res = 0
        self.lead_only_apparent_energy_high_res = 0
        #-----------------TAMPERS------------------
        self.tampers = []
        #-----------------STATUS BYTE--------------
        self.status = []
        self.reserved1 =0xffffffff
        self.reserved2 =0xffffffff
        self.reserved3 =0xffffffff
        self.reserved4 =0xffffffff
        self.reserved5 =0xffffffff
        #----------------PACKET2--------------------
        self.maxwell_software_version = 0x02
        self.maxwell_hardware_version = 0X02
        self.r_voltage = 0.0
        self.y_voltage = 0.0
        self.b_voltage = 0.0
        self.r_current = 0.0
        self.y_current = 0.0
        self.b_current = 0.0
        self.neutral_current = 0.0
        self.r_active_power = 0.0
        self.y_active_power = 0.0
        self.b_active_power = 0.0
        self.r_apparent_power = 0.0
        self.y_apparent_power = 0.0
        self.b_apparent_power = 0.0
        self.r_reactive_power = 0.0
        self.y_reactive_power = 0.0
        self.b_reactive_power = 0.0
        self.frequency = 0.0
        self.total_active_power = 0.0
        self.total_apparent_power = 0.0
        self.total_reactive_power = 0.0
        self.total_harmonic_power = 0.0
        self.r_pf = 0.0
        self.y_pf = 0.0
        self.b_pf = 0.0
        self.total_pf = 0.0
        

    def __str__(self):
        output = ""
        
        #output += Fore.GREEN + "---------------Packet 1----------------------------------------" + "\n"
        output += Fore.GREEN + "Protocol Version: " + Fore.WHITE + str(self.protocol_version) + "\n"
        output += Fore.GREEN + "maxwell_meter_num: " +  Fore.WHITE + str(self.maxwell_meter_num) + "\n"
        output += Fore.GREEN + "Time: " + Fore.WHITE +  str(self.time) + "\n" 
        output += Fore.GREEN + "Total real energy,         " + Fore.WHITE + "Noraml: "+ str(self.total_real_energy) + \
                ", High Res: "+str(self.total_real_energy_high_res) +" KWH\n"
        output += Fore.GREEN + "Total apparent energy,     " + Fore.WHITE + "Noraml: "+ str(self.total_apparent_energy) + \
                ", High Res: "+str(self.total_apparent_energy_high_res) +" KVAH\n"
        output += Fore.GREEN + "Total reactive energy,     " + Fore.WHITE + "Noraml: "+ str(self.total_reactive_energy) + \
                ", High Res: "+str(self.total_reactive_energy_high_res) +" KVARH\n"
        output += Fore.GREEN + "Lag only reactive energy,  " + Fore.WHITE + "Noraml: "+ str(self.lag_only_reactive_energy) + \
                ", High Res: "+str(self.lag_only_reactive_energy_high_res) +" KVARH\n"
        output += Fore.GREEN + "Lag only apparent energy,  " + Fore.WHITE + "Noraml: "+ str(self.lag_only_apparent_energy) + \
                ", High Res: "+str(self.lag_only_apparent_energy_high_res) +" KVAH\n"
        output += Fore.GREEN + "Lead only reactive energy, " + Fore.WHITE + "Noraml: "+ str(self.lead_only_reactive_energy) + \
                ", High Res: "+str(self.lead_only_reactive_energy_high_res) +" KVARH\n"
        output += Fore.GREEN + "Lead only apparent energy, " + Fore.WHITE + "Noraml: "+ str(self.lead_only_apparent_energy) + \
                ", High Res: "+str(self.lead_only_apparent_energy_high_res) +" KVAH\n"
        output += Fore.GREEN + "Tamper events: " + Fore.WHITE +  str(self.tampers) + "\n"
        output += Fore.GREEN + "Status: " + Fore.WHITE +  str(self.status) + "\n"
        
        #output += Fore.GREEN + "---------------Packet 2----------------------------------------" + "\n"
        output += Fore.GREEN + "Maxwell software version: " + Fore.WHITE +  str(self.maxwell_software_version) + "\n"
        output += Fore.GREEN + "Maxwell hardware version: " + Fore.WHITE +  str(self.maxwell_hardware_version) + "\n"
        output += Fore.GREEN + "Phase voltage,        "+ Fore.WHITE + " R:" + str(self.r_voltage) + \
             ",  Y:"+  str(self.y_voltage) + ",  B:" +  str(self.b_voltage) +" Volts\n"

        output += Fore.GREEN + "Phase Current,        "+ Fore.WHITE + " R:" + str(self.r_current) + \
             ",  Y:"+  str(self.y_current) + ",  B:" +  str(self.b_current) +" Amps\n"

        output += Fore.GREEN + "Neutral current:       " + Fore.WHITE +  str(self.neutral_current) + " Amps\n"

        output += Fore.GREEN + "Phase Active Power,   "+ Fore.WHITE + " R:" + str(self.r_active_power) + \
             ",  Y:"+  str(self.y_active_power) +    ",  B:" +  str(self.b_active_power) +" Watts\n"

        output += Fore.GREEN + "Phase Apparent Power, "+ Fore.WHITE + " R:" + str(self.r_apparent_power) + \
             ",  Y:"+  str(self.y_apparent_power) + ",  B:" +  str(self.b_apparent_power) +" VA\n"
        
        output += Fore.GREEN + "Phase Reactive Power, "+ Fore.WHITE + " R:" + str(self.r_reactive_power) + \
             ",  Y:"+  str(self.y_reactive_power) + ",  B:" +  str(self.b_reactive_power) +" VAR\n"

        output += Fore.GREEN + "Phase Power Factor,   "+ Fore.WHITE + " R:" + str(self.r_pf) + \
             ",  Y:"+  str(self.y_pf) + ",  B:" +  str(self.b_pf) +"\n"

        output += Fore.GREEN + "Total pf:              " + Fore.WHITE +  str(self.total_pf) + "\n"

        output += Fore.GREEN + "Frequency:             " + Fore.WHITE +  str(self.frequency) + " Hz\n"

        output += Fore.GREEN + "Total active power:    " + Fore.WHITE +  str(self.total_active_power) + " Watts\n"
        output += Fore.GREEN + "Total apparent power:  " + Fore.WHITE +  str(self.total_apparent_power) + " VA\n"
        output += Fore.GREEN + "Total reactive power:  " + Fore.WHITE +  str(self.total_reactive_power) + " VAR\n"
        output += Fore.GREEN + "Total harmonic power:  " + Fore.WHITE +  str(self.total_harmonic_power) + " Watts\n"


        return output


    def serialize_packet_one(self):
        """
        Serializes the contents of the packets into a bytearray. This function is used
        by the maxwell-simulator for sending MaxwellPackets on the serial port.

        :returns: serialized contents of the Packet
        :rtype: bytearray()
        """
        buf = bytearray()
        try:

            seconds_since_midnight = int((self.time - datetime.datetime(self.time.year, self.time.month, self.time.day,
                                                    0, 0, 0)).total_seconds())

            buf.extend(serialize.serialize_uint8(self.protocol_version))
            buf.extend(serialize.serialize_uint32(self.maxwell_meter_num))
            day = self.time.day
            month = self.time.month
            year = self.time.year

            buf.extend(serialize.serialize_uint8(day))
            buf.extend(serialize.serialize_uint8(month))
            buf.extend(serialize.serialize_uint16(year))
            buf.extend(serialize.serialize_uint32(seconds_since_midnight))

            temp = self.total_real_energy 
            buf.extend(serialize.serialize_uint32(int(temp/10)))
            buf.extend(serialize.serialize_uint32(int(temp*10)))

            temp = self.total_apparent_energy 
            buf.extend(serialize.serialize_uint32(int(temp/10)))
            buf.extend(serialize.serialize_uint32(int(temp*10)))


            temp = self.total_reactive_energy 
            buf.extend(serialize.serialize_uint32(int(temp/10)))
            buf.extend(serialize.serialize_uint32(int(temp*10)))

            temp = self.lag_only_reactive_energy 
            buf.extend(serialize.serialize_uint32(int(temp/10)))
            buf.extend(serialize.serialize_uint32(int(temp*10)))

            temp = self.lag_only_apparent_energy 
            buf.extend(serialize.serialize_uint32(int(temp/10)))
            buf.extend(serialize.serialize_uint32(int(temp*10)))
        
            temp = self.lead_only_reactive_energy 
            buf.extend(serialize.serialize_uint32(int(temp/10)))
            buf.extend(serialize.serialize_uint32(int(temp*10)))

            temp = self.lead_only_apparent_energy 
            buf.extend(serialize.serialize_uint32(int(temp/10)))
            buf.extend(serialize.serialize_uint32(int(temp*10)))

            tamper_integer = 0
            if TamperFlag("R_PHASE_MISSING") in self.tampers:
                tamper_integer += (2**0)
            if TamperFlag("Y_PHASE_MISSING") in self.tampers:
                tamper_integer += (2**1)
            if TamperFlag("B_PHASE_MISSING") in self.tampers:
                tamper_integer += (2**2)
            if TamperFlag("CURRENT_BYPASS") in self.tampers:
                tamper_integer += (2**3)
            if TamperFlag("R_PHASE_REVERSE_CURRENT") in self.tampers:
                tamper_integer += (2**4)
            if TamperFlag("Y_PHASE_REVERSE_CURRENT") in self.tampers:
                tamper_integer += (2**5)
            if TamperFlag("B_PHASE_REVERSE_CURRENT") in self.tampers:
                tamper_integer += (2**6)
            if TamperFlag("MAGNETIC") in self.tampers:
                tamper_integer += (2**7)
            if TamperFlag("R_PHASE_CT_OPEN") in self.tampers:
                tamper_integer += (2**8)
            if TamperFlag("Y_PHASE_CT_OPEN") in self.tampers:
                tamper_integer += (2**9)
            if TamperFlag("B_PHASE_CT_OPEN") in self.tampers:
                tamper_integer += (2**10)
            if TamperFlag("CURRENT_UNBALANCE") in self.tampers:
                tamper_integer += (2**11)
            if TamperFlag("VOLTAGE_UNBALANCE") in self.tampers:
                tamper_integer += (2**12)
            if TamperFlag("R_PHASE_ND") in self.tampers:
                tamper_integer += (2**13)
            if TamperFlag("Y_PHASE_ND") in self.tampers:
                tamper_integer += (2**14)
            if TamperFlag("B_PHASE_ND") in self.tampers:
                tamper_integer += (2**15)

            buf.extend(serialize.serialize_uint16(tamper_integer))

            status_intiger = 0
            if StatusFlag("RTC_BATTERY_FAULTY") in self.status:
                status_intiger +=1
            if StatusFlag("UC_BATTERY_FAULTY") in self.status:
                status_intiger +=2
            if StatusFlag("RELAY_OFF") in self.status:
                status_intiger +=4
            if StatusFlag("RELAY_PUMP_OFF") in self.status:
                status_intiger +=8

            buf.extend(serialize.serialize_uint8(status_intiger))
            buf.extend(serialize.serialize_uint32(self.reserved1))
            buf.extend(serialize.serialize_uint32(self.reserved2))
            buf.extend(serialize.serialize_uint32(self.reserved3))
            buf.extend(serialize.serialize_uint32(self.reserved4))
            buf.extend(serialize.serialize_uint32(self.reserved5))
        except serialize.SerializeValueError:
            raise SerializeError
        return buf

    def serialize_packet_two(self):
        """
        Serializes the contents of the packets into a bytearray. This function is used
        by the maxwell-simulator for sending MaxwellPackets on the serial port.

        :returns: serialized contents of the Packet
        :rtype: bytearray()
        """
        buf = bytearray()
        try:
            buf.extend(serialize.serialize_uint8(self.maxwell_software_version))
            buf.extend(serialize.serialize_uint8(self.maxwell_hardware_version))
            buf.extend(serialize.serialize_uint32(int(1000*self.r_voltage)))
            buf.extend(serialize.serialize_uint32(int(1000*self.y_voltage)))
            buf.extend(serialize.serialize_uint32(int(1000*self.b_voltage)))

            buf.extend(serialize.serialize_uint32(int(1000*self.r_current)))
            buf.extend(serialize.serialize_uint32(int(1000*self.y_current)))
            buf.extend(serialize.serialize_uint32(int(1000*self.b_current)))

            buf.extend(serialize.serialize_uint32(int(1000*self.neutral_current)))
            buf.extend(serialize.serialize_uint32(int(1000*self.r_active_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.y_active_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.b_active_power)))

            buf.extend(serialize.serialize_uint32(int(1000*self.r_apparent_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.y_apparent_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.b_apparent_power)))

            buf.extend(serialize.serialize_uint32(int(1000*self.r_reactive_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.y_reactive_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.b_reactive_power)))
            
            buf.extend(serialize.serialize_uint16(int(100*self.frequency)))

            buf.extend(serialize.serialize_uint32(int(1000*self.total_active_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.total_apparent_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.total_reactive_power)))
            buf.extend(serialize.serialize_uint32(int(1000*self.total_harmonic_power)))
            
            buf.extend(serialize.serialize_int16(int(10000*self.r_pf)))
            buf.extend(serialize.serialize_int16(int(10000*self.y_pf)))
            buf.extend(serialize.serialize_int16(int(10000*self.b_pf)))
            buf.extend(serialize.serialize_uint16(int(10000*self.total_pf)))
        except serialize.SerializeValueError:
            raise SerializeError
        return buf

    def deserialize_packet_one(self, buf):
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
            date_tmp = serialize.deserialize_uint32(buf[5:9]) 
            seconds_since_midnight = serialize.deserialize_uint32(buf[9:13]) 

            self.total_real_energy = serialize.deserialize_uint32(buf[13:17])/100.0 
            self.total_real_energy_high_res = serialize.deserialize_uint32(buf[17:21])/10000.0
            self.total_apparent_energy = serialize.deserialize_uint32(buf[21:25])/100.0 
            self.total_apparent_energy_high_res = serialize.deserialize_uint32(buf[25:29])/10000.0
            self.total_reactive_energy = serialize.deserialize_uint32(buf[29:33])/100.0  
            self.total_reactive_energy_high_res = serialize.deserialize_uint32(buf[33:37])/10000.0
            self.lag_only_reactive_energy = serialize.deserialize_uint32(buf[37:41])/100.0
            self.lag_only_reactive_energy_high_res = serialize.deserialize_uint32(buf[41:45])/10000.0
            self.lag_only_apparent_energy = serialize.deserialize_uint32(buf[45:49])/100.0 
            self.lag_only_apparent_energy_high_res = serialize.deserialize_uint32(buf[49:53])/10000.0
            self.lead_only_reactive_energy = serialize.deserialize_uint32(buf[53:57])/100.0 
            self.lead_only_reactive_energy_high_res = serialize.deserialize_uint32(buf[57:61])/10000.0
            self.lead_only_apparent_energy = serialize.deserialize_uint32(buf[61:65])/100.0 
            self.lead_only_apparent_energy_high_res = serialize.deserialize_uint32(buf[65:69])/10000.0
            tamper_tmp = serialize.deserialize_uint16(buf[69:71]) 
            status_tmp = serialize.deserialize_uint8(buf[71:72]) 
            self.reserved1 =serialize.deserialize_int32(buf[72:76]) 
            self.reserved2 =serialize.deserialize_int32(buf[76:80])
            self.reserved3 =serialize.deserialize_int32(buf[80:84])
            self.reserved4 =serialize.deserialize_int32(buf[84:88])
            self.reserved5 =serialize.deserialize_int32(buf[88:92]) 
            if(self.tampers.count(TamperFlag("R_PHASE_MISSING"))):
                self.tampers.remove(TamperFlag("R_PHASE_MISSING"))
            if(self.tampers.count(TamperFlag("Y_PHASE_MISSING"))):
                self.tampers.remove(TamperFlag("Y_PHASE_MISSING"))
            if(self.tampers.count(TamperFlag("B_PHASE_MISSING"))):
                self.tampers.remove(TamperFlag("B_PHASE_MISSING"))
            if(self.tampers.count(TamperFlag("CURRENT_BYPASS"))):
                self.tampers.remove(TamperFlag("CURRENT_BYPASS"))
            if(self.tampers.count(TamperFlag("R_PHASE_REVERSE_CURRENT"))):
                self.tampers.remove(TamperFlag("R_PHASE_REVERSE_CURRENT"))
            if(self.tampers.count(TamperFlag("Y_PHASE_REVERSE_CURRENT"))):
                self.tampers.remove(TamperFlag("Y_PHASE_REVERSE_CURRENT"))
            if(self.tampers.count(TamperFlag("B_PHASE_REVERSE_CURRENT"))):
                self.tampers.remove(TamperFlag("B_PHASE_REVERSE_CURRENT"))
            if(self.tampers.count(TamperFlag("MAGNETIC"))):
                self.tampers.remove(TamperFlag("MAGNETIC"))
            if(self.tampers.count(TamperFlag("R_PHASE_CT_OPEN"))):
                self.tampers.remove(TamperFlag("R_PHASE_CT_OPEN"))
            if(self.tampers.count(TamperFlag("Y_PHASE_CT_OPEN"))):
                self.tampers.remove(TamperFlag("Y_PHASE_CT_OPEN"))
            if(self.tampers.count(TamperFlag("B_PHASE_CT_OPEN"))):
                self.tampers.remove(TamperFlag("B_PHASE_CT_OPEN"))
            if(self.tampers.count(TamperFlag("CURRENT_UNBALANCE"))):
                self.tampers.remove(TamperFlag("CURRENT_UNBALANCE"))
            if(self.tampers.count(TamperFlag("VOLTAGE_UNBALANCE"))):
                self.tampers.remove(TamperFlag("VOLTAGE_UNBALANCE"))
            if(self.tampers.count(TamperFlag("R_PHASE_ND"))):
                self.tampers.remove(TamperFlag("R_PHASE_ND"))
            if(self.tampers.count(TamperFlag("Y_PHASE_ND"))):
                self.tampers.remove(TamperFlag("Y_PHASE_ND"))
            if(self.tampers.count(TamperFlag("B_PHASE_ND"))):
                self.tampers.remove(TamperFlag("B_PHASE_ND"))



            if ((tamper_tmp/2**0 % 2) == 1):
                self.tampers.append(TamperFlag("R_PHASE_MISSING"))
            if ((tamper_tmp/2**1 % 2) == 1):
                self.tampers.append(TamperFlag("Y_PHASE_MISSING"))
            if ((tamper_tmp/2**2 % 2) == 1):
                self.tampers.append(TamperFlag("B_PHASE_MISSING"))
            if ((tamper_tmp/2**3 % 2) == 1):
                self.tampers.append(TamperFlag("CURRENT_BYPASS"))
            if ((tamper_tmp/2**4 % 2) == 1):
                self.tampers.append(TamperFlag("R_PHASE_REVERSE_CURRENT"))
            if ((tamper_tmp/2**5 % 2) == 1):
                self.tampers.append(TamperFlag("Y_PHASE_REVERSE_CURRENT"))
            if ((tamper_tmp/2**6 % 2) == 1):
                self.tampers.append(TamperFlag("B_PHASE_REVERSE_CURRENT"))
            if ((tamper_tmp/2**7 % 2) == 1):
                self.tampers.append(TamperFlag("MAGNETIC"))
            if ((tamper_tmp/2**8 % 2) == 1):
                self.tampers.append(TamperFlag("R_PHASE_CT_OPEN"))
            if ((tamper_tmp/2**9 % 2) == 1):
                self.tampers.append(TamperFlag("Y_PHASE_CT_OPEN"))
            if ((tamper_tmp/2**10 % 2) == 1):
                self.tampers.append(TamperFlag("B_PHASE_CT_OPEN"))
            if ((tamper_tmp/2**11 % 2) == 1):
                self.tampers.append(TamperFlag("CURRENT_UNBALANCE"))
            if ((tamper_tmp/2**12 % 2) == 1):
                self.tampers.append(TamperFlag("VOLTAGE_UNBALANCE"))
            if ((tamper_tmp/2**13 % 2) == 1):
                self.tamper_info.append(TamperFlag("R_PHASE_ND"))
            if ((tamper_tmp/2**14 % 2) == 1):
                self.tamper_info.append(TamperFlag("Y_PHASE_ND"))
            if ((tamper_tmp/2**15 % 2) == 1):
                self.tamper_info.append(TamperFlag("B_PHASE_ND"))

            if(self.status.count(StatusFlag("RTC_BATTERY_FAULTY"))):
                 self.status.remove(StatusFlag("RTC_BATTERY_FAULTY"))
            if(self.status.count(StatusFlag("UC_BATTERY_FAULTY"))):
                 self.status.remove(StatusFlag("UC_BATTERY_FAULTY"))
            if(self.status.count(StatusFlag("RELAY_OFF"))):
                 self.status.remove(StatusFlag("RELAY_OFF"))
            if(self.status.count(StatusFlag("RELAY_PUMP_OFF"))):
                 self.status.remove(StatusFlag("RELAY_PUMP_OFF"))


            if ((status_tmp/2**0 % 2) == 1):
                self.status.append(StatusFlag("RTC_BATTERY_FAULTY"))
            if ((status_tmp/2**1 % 2) == 1):
                self.status.append(StatusFlag("UC_BATTERY_FAULTY"))
            if ((status_tmp/2**2 % 2) == 1):
                self.status.append(StatusFlag("RELAY_OFF"))
            if ((status_tmp/2**3 % 2) == 1):
                self.status.append(StatusFlag("RELAY_PUMP_OFF"))


            year = (date_tmp % 2**16)
            month = (date_tmp/2**16) % 2**8
            day = (date_tmp/2**24)
            try:
                self.time = datetime.datetime(year, month, day, 0, 0, 0) + \
                        datetime.timedelta(seconds=seconds_since_midnight)
            except ValueError as err:
                self.time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        except serialize.DeserializeValueError:
            raise DeserializeError

    def deserialize_packet_two(self, buf):
        """
        Deserialzes buf.
        """
        try:
            self.maxwell_software_version = serialize.deserialize_uint8(buf[0:1])
            self.maxwell_hardware_version = serialize.deserialize_uint8(buf[1:2])
            self.r_voltage = serialize.deserialize_uint32(buf[2:6])/1000.0
            self.y_voltage = serialize.deserialize_uint32(buf[6:10])/1000.0
            self.b_voltage = serialize.deserialize_uint32(buf[10:14])/1000.0
            self.r_current = serialize.deserialize_uint32(buf[14:18])/1000.0
            self.y_current = serialize.deserialize_uint32(buf[18:22])/1000.0
            self.b_current = serialize.deserialize_uint32(buf[22:26])/1000.0
            self.neutral_current = serialize.deserialize_uint32(buf[26:30])/1000.0
            self.r_active_power = serialize.deserialize_uint32(buf[30:34])/1000.0
            self.y_active_power = serialize.deserialize_uint32(buf[34:38])/1000.0
            self.b_active_power = serialize.deserialize_uint32(buf[38:42])/1000.0
            self.r_apparent_power = serialize.deserialize_uint32(buf[42:46])/1000.0
            self.y_apparent_power = serialize.deserialize_uint32(buf[46:50])/1000.0
            self.b_apparent_power = serialize.deserialize_uint32(buf[50:54])/1000.0
            self.r_reactive_power = serialize.deserialize_uint32(buf[54:58])/1000.0
            self.y_reactive_power = serialize.deserialize_uint32(buf[58:62])/1000.0
            self.b_reactive_power = serialize.deserialize_uint32(buf[62:66])/1000.0
            self.frequency = serialize.deserialize_uint16(buf[66:68])/100.0

            self.total_active_power = serialize.deserialize_uint32(buf[68:72])/1000.0
            self.total_apparent_power = serialize.deserialize_uint32(buf[72:76])/1000.0
            self.total_reactive_power = serialize.deserialize_uint32(buf[76:80])/1000.0
            self.total_harmonic_power = serialize.deserialize_uint32(buf[80:84])/1000.0

            self.r_pf = serialize.deserialize_int16(buf[84:86])/10000.0
            self.y_pf = serialize.deserialize_int16(buf[86:88])/10000.0
            self.b_pf = serialize.deserialize_int16(buf[88:90])/10000.0
            self.total_pf = serialize.deserialize_uint16(buf[90:92])/10000.0
        except serialize.DeserializeValueError:
            raise DeserializeError