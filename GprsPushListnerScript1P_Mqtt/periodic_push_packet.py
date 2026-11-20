"""
Definition of the MaxwellPacket class, used for communication between the
Maxwell meter and the Node.
"""

import gp_node.utils.serialize as serialize
from gp_node.utils import TamperFlag
# from colorama import Fore
import datetime
import calendar
import binascii
from dateutil import parser

class DeserializeError(Exception):
    def __str__(self):
        return "Could not deserialize packet."


class SerializeError(Exception):
    def __str__(self):
        return "Could not serialize packet."

class PeriodicPushPacket:


    def __init__(self):
        self.Time = 0
        self.DeviceID = 0
        self.PushSetup = 0
        self.Voltage = 0
        self.PCurrent = 0
        self.NCurrent = 0
        self.PF = 0
        self.Frequency = 0
        self.AppPowewr = 0
        self.ActPower = 0
        self.CumEnegyKWH = 0
        self.TamperCount = 0
        self.BillingCount = 0


    def __str__(self):
        output = ""
        output += "Time        : " + binascii.hexlify(self.Time)         +" <> "+ self.string1  +"\n"
        output += "DeviceID    : " + binascii.hexlify(self.DeviceID)     +" <> "+ self.DeviceID +"\n"
        output += "PushSetup   : " + binascii.hexlify(self.PushSetup)    +"\n"
        output += "Voltage     : " + binascii.hexlify(self.Voltage)      +" <> "+ str(float(int(binascii.hexlify(self.Voltage)     , 16))/1000)+ " V" + "\n"
        output += "PCurrent    : " + binascii.hexlify(self.PCurrent)     +" <> "+ str(float(int(binascii.hexlify(self.PCurrent)    , 16))/1000)+ " A" + "\n"
        output += "NCurrent    : " + binascii.hexlify(self.NCurrent)     +" <> "+ str(float(int(binascii.hexlify(self.NCurrent)    , 16))/1000)+ " A" + "\n"
        output += "P F         : " + binascii.hexlify(self.PF)           +" <> "+ str(float(int(binascii.hexlify(self.PF)          , 16))/1000)+ "\n"
        output += "Frequency   : " + binascii.hexlify(self.Frequency)    +" <> "+ str(float(int(binascii.hexlify(self.Frequency)   , 16))/1000)+ " Hz" + "\n"
        output += "AppPower    : " + binascii.hexlify(self.AppPowewr)    +" <> "+ str(float(int(binascii.hexlify(self.AppPowewr)   , 16))/1000)+ " kVA" + "\n"
        output += "ActPower    : " + binascii.hexlify(self.ActPower)     +" <> "+ str(float(int(binascii.hexlify(self.ActPower)    , 16))/1000)+ " kW" + "\n"
        output += "CumEnegyKWH : " + binascii.hexlify(self.CumEnegyKWH)  +" <> "+ str(float(int(binascii.hexlify(self.CumEnegyKWH) , 16))/100) + " kWh" + "\n"
        output += "TamperCount : " + binascii.hexlify(self.TamperCount)  +" <> "+ str(int(binascii.hexlify(self.TamperCount) , 16)) +"\n"
        output += "BillingCount: " + binascii.hexlify(self.BillingCount) +" <> "+ str(int(binascii.hexlify(self.BillingCount), 16)) +"\n"
        return output

        # output = ""
        # output += Fore.GREEN + "Time        : " + Fore.WHITE + binascii.hexlify(self.Time) + " <> "+Fore.BLUE+self.string1+"\n"
        # output += Fore.GREEN + "DeviceID    : " + Fore.WHITE + binascii.hexlify(self.DeviceID) + " <> " + Fore.BLUE + self.DeviceID +"\n"
        # output += Fore.GREEN + "PushSetup   : " + Fore.WHITE + binascii.hexlify(self.PushSetup) +"\n"
        # output += Fore.GREEN + "Voltage     : " + Fore.WHITE + binascii.hexlify(self.Voltage) +" <> "+Fore.BLUE +str(int(binascii.hexlify(self.Voltage), 16))+"\n"
        # output += Fore.GREEN + "PCurrent    : " + Fore.WHITE + binascii.hexlify(self.PCurrent) +" <> "+Fore.BLUE +str(int(binascii.hexlify(self.PCurrent), 16))+"\n"
        # output += Fore.GREEN + "NCurrent    : " + Fore.WHITE + binascii.hexlify(self.NCurrent) +" <> "+Fore.BLUE +str(int(binascii.hexlify(self.NCurrent), 16))+"\n"
        # output += Fore.GREEN + "P F         : " + Fore.WHITE + binascii.hexlify(self.PF) +" <> "+Fore.BLUE +str(int(binascii.hexlify(self.PF), 16))+"\n"
        # output += Fore.GREEN + "Frequency   : " + Fore.WHITE + binascii.hexlify(self.Frequency)+" <> "+Fore.BLUE +str(int(binascii.hexlify(self.Frequency), 16) )+"\n"
        # output += Fore.GREEN + "AppPower    : " + Fore.WHITE + binascii.hexlify(self.AppPowewr) +" <> "+Fore.BLUE +str(int(binascii.hexlify(self.AppPowewr), 16))+"\n"
        # output += Fore.GREEN + "ActPower    : " + Fore.WHITE + binascii.hexlify(self.ActPower)+" <> "+Fore.BLUE +str(int(binascii.hexlify(self.ActPower), 16) )+"\n"
        # output += Fore.GREEN + "CumEnegyKWH : " + Fore.WHITE + binascii.hexlify(self.CumEnegyKWH)+" <> "+Fore.BLUE +str(int(binascii.hexlify(self.CumEnegyKWH), 16)) +"\n"
        # output += Fore.GREEN + "TamperCount : " + Fore.WHITE + binascii.hexlify(self.TamperCount)+" <> "+Fore.BLUE +str(int(binascii.hexlify(self.TamperCount), 16)) +"\n"
        # output += Fore.GREEN + "BillingCount: " + Fore.WHITE + binascii.hexlify(self.BillingCount)+" <> "+Fore.BLUE +str(int(binascii.hexlify(self.BillingCount), 16))+Fore.WHITE+"\n"
        # return output



    def deserialize(self, buf):
        self.DeviceID = buf[22:22+10]
        self.PushSetup = buf[34:34+6]
        self.Time = buf[42:42+12]
        self.time1=self.timeformat(self.Time)
        self.Voltage = buf[55:55+4]
        self.PCurrent = buf[60:60+4]
        self.NCurrent = buf[65:65+4]
        self.PF = buf[70:70+4]
        self.Frequency = buf[75:75+4]
        self.AppPowewr = buf[80:80+4]
        self.ActPower = buf[85:85+4]
        self.CumEnegyKWH = buf[90:90+4]
        self.TamperCount = buf[95:95+4]
        self.BillingCount = buf[100:100+4]

    def timeformat(self,buf):
        a=buf.encode("hex")
        # print "ddddddddddd",a
        year=int(   a[0:4],16)
        month=int(a[4:6],16)
        date=int(a[6:8],16)
        day=int(a[8:10],16)
        hour=int(a[10:12],16)
        minute=int(a[12:14],16)
        second=int(a[14:16],16)
        today = datetime.datetime(int(year),int(month),int(date))
        # print "dfhss",today,type(today)
        day=calendar.day_name[today.weekday()]
        # print day


        self.string1=str(str(year)+"-"+str(month)+"-"+str(date)+" "+str(day)+" "+str(hour)+":"+str(minute)+":"+str(second))
        # print self.string1


