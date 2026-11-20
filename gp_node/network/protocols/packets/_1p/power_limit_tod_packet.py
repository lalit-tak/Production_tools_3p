import datetime
from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint32

import gp_node.utils.serialize as serialize

class PowerLimitTodPacket(object):
    def __init__(self):
        self.highPowerLimit     = 0  
        self.overPowerLimit     = 0
        self.retryDelay5Sec     = 0
        self.maxRetryCount      = 0
        self.hiOrOvrpwrOccPtime = 0
        self.overVoltLimit      = 0
        self.overVoltOccPtime   = 0
        self.overVoltResPtime   = 0
        
    def __str__(self):
        return ( "highPowerLimit    : {} watt\n"    
                 "overPowerLimit    : {} watt\n"    
                 "retryDelay5Sec    : {} second\n"    
                 "maxRetryCount     : {} \n"   
                 "hiOrOvrpwrOccPtime: {} second\n"
                 "overVoltLimit     : {} volt\n"       
                 "overVoltOccPtime  : {} second\n" 
                 "overVoltResPtime  : {} second\n") \
                .format (
                        self.highPowerLimit     ,
                        self.overPowerLimit     ,
                        self.retryDelay5Sec     ,
                        self.maxRetryCount      ,
                        self.hiOrOvrpwrOccPtime ,
                        self.overVoltLimit      ,
                        self.overVoltOccPtime   ,
                        self.overVoltResPtime
                        )

    def deserialize(self,payload):
        # print hex(payload[0])
        self.highPowerLimit     = (deserialize_uint16(payload[0:2],"reverse"))
        self.overPowerLimit     = (deserialize_uint16(payload[2:4],"reverse"))
        self.retryDelay5Sec     = (deserialize_uint8(payload[4:5],"reverse"))*5
        self.maxRetryCount      = (deserialize_uint8(payload[5:6],"reverse"))
        self.hiOrOvrpwrOccPtime = (deserialize_uint8(payload[6:7],"reverse"))
        self.overVoltLimit      = (deserialize_uint8(payload[7:8],"reverse"))+200
        self.overVoltOccPtime   = (deserialize_uint8(payload[8:9],"reverse"))
        self.overVoltResPtime   = (deserialize_uint8(payload[9:10],"reverse"))

    def serialize(self):
        payload = bytearray()
        payload.extend(serialize.serialize_uint16((self.highPowerLimit),"reverse"))
        payload.extend(serialize.serialize_uint16((self.overPowerLimit),"reverse"))
        payload.extend(serialize.serialize_uint8((self.retryDelay5Sec),"reverse"))
        payload.extend(serialize.serialize_uint8((self.maxRetryCount),"reverse"))
        payload.extend(serialize.serialize_uint8((self.hiOrOvrpwrOccPtime),"reverse"))
        payload.extend(serialize.serialize_uint8((self.overVoltLimit),"reverse"))
        payload.extend(serialize.serialize_uint8((self.overVoltOccPtime),"reverse"))
        payload.extend(serialize.serialize_uint8((self.overVoltResPtime),"reverse"))
        return payload



class PowerLimitParamsPacket(object):
    def __init__(self):
        self.EgPower     = 0  
        self.DgPower     = 0
        self.Lockperiod  = 0
        self.OccPtime    = 0
        self.ResPtime    = 0
        self.RetryCount  = 0
        self.StatusF     = 0
        self.StateF      = 0
        self.PLstatus    = " "
        self.remainCount = 0
        self.PLstate     = " "

    def __str__(self):
        return ( "Eg Power Limit        : {} watt\n"    
                 "Dg Power Limit        : {} watt\n"    
                 "Lockdown Period       : {} seconds\n"    
                 "On time Interval      : {} seconds\n"   
                 "Off time Interval     : {} seconds\n"
                 "Max RetryCount        : {} \n"       
                 "Power Limit           : {} \n" 
                 "Remaining Retrycount  : {} \n"
                 "Current Status        : {} \n") \
                .format (
                        self.EgPower     ,
                        self.DgPower     ,
                        self.Lockperiod  ,
                        self.OccPtime   ,
                        self.ResPtime   ,
                        self.RetryCount  ,
                        self.PLstatus    ,
                        self.remainCount ,
                        self.PLstate
                        )

    def deserialize(self,payload):
        # print hex(payload[0])
        self.EgPower     = (deserialize_uint32(payload[0:4],"reverse"))
        self.DgPower     = (deserialize_uint32(payload[4:8],"reverse"))
        self.Lockperiod  = (deserialize_uint16(payload[8:10],"reverse"))
        self.OccPtime    = (deserialize_uint16(payload[10:12],"reverse"))
        self.ResPtime    = (deserialize_uint16(payload[12:14],"reverse"))
        self.RetryCount  = (deserialize_uint8(payload[14:15],"reverse"))
        self.StatusF     = (deserialize_uint8(payload[15:16],"reverse"))
        if(self.StatusF == 0):
            self.PLstatus = "Disable"
        else:
            self.PLstatus = "Enable"    
        self.StateF      = (deserialize_uint8(payload[16:17],"reverse"))

        if  (self.StateF&0x03 == 1):
            self.PLstate = "OFF: Over load"
        elif(self.StateF&0x03 == 2):
            self.PLstate = "OFF: Over Current"
        elif(self.StateF&0x03 == 3):
            self.PLstate = "OFF: Over Load, Over Current"
        else:
            self.PLstate = "ON"

        self.remainCount = (self.StateF>>4)&0x3F        

    def serialize(self):
        payload = bytearray()
        payload.extend(serialize.serialize_uint32((self.EgPower),"reverse"))
        payload.extend(serialize.serialize_uint32((self.DgPower),"reverse"))
        payload.extend(serialize.serialize_uint16((self.Lockperiod),"reverse"))
        payload.extend(serialize.serialize_uint8((self.OccPtime),"reverse"))
        payload.extend(serialize.serialize_uint8((self.ResPtime),"reverse"))
        payload.extend(serialize.serialize_uint8((self.RetryCount),"reverse"))
        payload.extend(serialize.serialize_uint8((self.StatusF),"reverse"))
        return payload
