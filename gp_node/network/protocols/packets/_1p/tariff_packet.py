import datetime
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint32
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
import gp_node.utils.serialize as serialize



class TariffPacket(object):

    def __init__(self):

        self.nowGroup               = ""                
        self.energyAtSOM            = 0.00                  
        self.lastBillTS             = datetime.datetime(1970, 1, 1, 0, 0, 0)                  
        self.newTariffTS            = datetime.datetime(1970, 1, 1, 0, 0, 0)        
        self.prepaidModeChangeTS    = datetime.datetime(1970, 1, 1, 0, 0, 0)        
        self.tariffToActivate       = 0        
        self.prepaidEnableF         = ""      
        self.balance                = 0.00        
        self.fdPrice                = [0,0,0,0,0,0]          
        self.energyPrice            = [0,0,0,0,0,0]          
        self.energySlab             = [0,0,0,0,0]            
        self.fdType                 = ""        
        self.fdTelescopicF          = 0        
        self.mmcApplication         = 0        
        self.friendlyHours          = ""        
        self.alertLimit             = 0.00        
        self.emergencyCredit        = 0.00        
        self.topUpLimit             = 0.00        
        self.mmc                    = 0.00      
        self.CummulativePosRecharge = 0.00
        self.CummulativeNegRecharge = 0.00
        self.netRecharge            = 0.00
        self.currentACBalance       = 0.00
        self.currentFDCost          = 0.00
        self.currentEnergyCost      = 0.00
        self.status                 = ""
        self.tariffType             = int(1)
        self.currentPosRecharge     = 0.00  # new requirement data added from here
        self.currentNegRecharge     = 0.00
        self.egCharges              = 0.00
        self.dgCharges              = 0.00
        self.energyAtSOMEg          = 0.00
        self.energyAtSOMDg          = 0.00
        self.currentNetRecharge     = 0.00
        self.cummEgFdCost           = 0.00
        self.billType               = "kWh"


    def __str__(self):
        return (\
        "Fixed Deduction Prices             : {} Paisa\n"
        "Fixed Deduction Type               : {} \n"
        "Fixed Deduction Telescopic Flag    : {} \n"                
        "Slab Prices                        : {} Paisa\n"
        "Slab Energies                      : {} KWh\n"
        "Monthly Minimum Charge             : {} Rs\n"
        "Friendly Hours                     : {} \n"
        "MMC Application                    : {} \n"
        "Alert limit                        : {} \n"
        "Emergency Credits                  : {} \n"
        "Topup limit                        : {} \n")\
                .format(\
                        self.fdPrice,
                        self.fdType,
                        self.fdTelescopicF,
                        self.energyPrice,
                        self.energySlab,
                        self.mmc,
                        self.friendlyHours,
                        self.mmcApplication,                        
                        self.alertLimit,
                        self.emergencyCredit,
                        self.topUpLimit)



    def deserializePrepaidInfo(self,payload):
        if len(payload) < 82:
            self.deserializePrepaidInfo_wp(payload)
            return

        bytes = bytearray()
        # print ">>>>>>>>>>>>>>>>>>>>>>>."
        bytes = payload

        temp                            = deserialize_uint16(payload[0:2],"reverse")
        if temp == 0: 
            self.nowGroup = "DG Tariff"
        elif temp == 1:
            self.nowGroup = "EG Tariff"

        self.tariffChangeReqF           = deserialize_uint16(payload[2:4],"reverse")
        self.prepaidModeChangeReqF      = deserialize_uint16(payload[4:6],"reverse") 
        self.energyAtSOM                = (deserialize_uint32(payload[6:10],"reverse"))/100.00
        self.lastBillTS                 = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[13]<<24) + (bytes[12]<<16) +(bytes[11]<<8) + bytes[10]))                       
        
        self.newTariffTS                = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[17]<<24) + (bytes[16]<<16) +(bytes[15]<<8) + bytes[14])) 
        self.prepaidModeChangeTS        = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[21]<<24) + (bytes[20]<<16) +(bytes[19]<<8) + bytes[18])) 
        
        self.tariffToActivate                = deserialize_uint16(payload[22:24],"reverse")
        temp             = deserialize_uint16(payload[24:26],"reverse")
        if temp == 0:
            self.prepaidEnableF = "Disabled"
        elif temp == 0x55:
            self.prepaidEnableF = "Enabled"
        else:
            self.prepaidEnableF = "NA"   
        self.balance                = deserialize_int32(payload[26:30],"reverse")/100.00 
        self.CummulativePosRecharge = deserialize_uint32(payload[30:34],"reverse")/100.00 
        self.CummulativeNegRecharge = deserialize_int32(payload[34:38],"reverse")/100.00     
        self.netRecharge            = deserialize_int32(payload[38:42],"reverse")/100.00     
        self.currentACBalance       = deserialize_int32(payload[42:46],"reverse")/100.00     
        self.currentFDCost          = deserialize_uint32(payload[46:50],"reverse")/100.00     
        self.currentEnergyCost      = deserialize_uint32(payload[50:54],"reverse")/100.00         
        temp2                       = deserialize_uint16(payload[54:56],"reverse")    
        if temp2 == 0:            
            self.status             = "ACC_NO_BALANCE"        
        elif temp2 == 1:
            self.status             = "ACC_NO_BALANCE_FRIENDLY_HOURS"
        elif temp2 == 2:
            self.status             = "ACC_EMERGENCY_CREDIT"
        elif temp2 == 3:
            self.status             = "ACC_LOW_BALANCE"
        elif temp2 == 4:   
            self.status             = "ACC_ENOUGH_BALANCE"   
        elif temp2 == 5:   
            self.status             = "ACC_PREPAID_DISABLED"   
        elif temp2 == 6:   
            self.status             = "ACC_DATA_NOT_AVAILABLE"
        elif temp2 == 7:
            self.status             = "ACC_NO_BALANCE_FRIENDLY_DAYS" 
               
        self.currentPosRecharge     = deserialize_uint32(payload[56:60],"reverse")/100.00      
        self.currentNegRecharge     = deserialize_uint32(payload[60:64],"reverse")/100.00
        self.egCharges              = deserialize_uint32(payload[64:68],"reverse")/100.00
        self.dgCharges              = deserialize_uint32(payload[68:72],"reverse")/100.00
        self.energyAtSOMEg          = deserialize_uint32(payload[72:76],"reverse")/100.00
        self.energyAtSOMDg          = deserialize_uint32(payload[76:80],"reverse")/100.00
        self.currentNetRecharge     = deserialize_int32(payload[80:84],"reverse")/100.00
        if len(payload) > 84:
            self.cummEgFdCost       = deserialize_uint32(payload[84:88])/100.00
        if len(payload) > 88:
            if payload[88] == 0:
                self.billType           = "kVAh"


    def deserializePrepaidInfo_wp(self,payload):
        
        bytes = bytearray()
        # print ">>>>>>>>>>>>>>>>>>>>>>>."
        bytes = payload

        temp                            = deserialize_uint8(payload[0:1],"reverse")
        if temp == 0: 
            self.nowGroup = "DG Tariff"
        elif temp == 1:
            self.nowGroup = "EG Tariff"

        self.tariffChangeReqF           = deserialize_uint8(payload[1:2],"reverse")
        # self.prepaidModeChangeReqF      = deserialize_uint16(payload[4:6],"reverse") 
        self.energyAtSOM                = (deserialize_uint32(payload[2:6]))/100.00
        self.lastBillTS                 = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[6]<<24) + (bytes[7]<<16) +(bytes[8]<<8) + bytes[9]))                       
        
        self.newTariffTS                = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[10]<<24) + (bytes[11]<<16) +(bytes[12]<<8) + bytes[13])) 
        self.prepaidModeChangeTS        = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[14]<<24) + (bytes[15]<<16) +(bytes[16]<<8) + bytes[17])) 
        
        # self.tariffToActivate                = deserialize_uint16(payload[22:24],"reverse")
        temp             = deserialize_uint8(payload[18:19],"reverse")
        if temp == 0:
            self.prepaidEnableF = "Disabled"
        elif temp == 0x55:
            self.prepaidEnableF = "Enabled"
        else:
            self.prepaidEnableF = "NA"   
        self.balance                = deserialize_int32(payload[28:32])/100.00 
        self.CummulativePosRecharge = deserialize_uint32(payload[32:36])/100.00 
        self.CummulativeNegRecharge = deserialize_int32(payload[36:40])/100.00     
        self.netRecharge            = deserialize_int32(payload[40:44])/100.00     
        self.currentACBalance       = deserialize_int32(payload[44:48])/100.00     
        self.currentFDCost          = deserialize_uint32(payload[48:52])/100.00     
        self.currentEnergyCost      = deserialize_uint32(payload[52:56])/100.00         
        temp2                       = deserialize_uint8(payload[19:20],"reverse")    
        if temp2 == 0:            
            self.status             = "ACC_NO_BALANCE"        
        elif temp2 == 1:
            self.status             = "ACC_NO_BALANCE_FRIENDLY_HOURS"
        elif temp2 == 2:
            self.status             = "ACC_EMERGENCY_CREDIT"
        elif temp2 == 3:
            self.status             = "ACC_LOW_BALANCE"
        elif temp2 == 4:   
            self.status             = "ACC_ENOUGH_BALANCE"   
        elif temp2 == 5:   
            self.status             = "ACC_PREPAID_DISABLED"   
        elif temp2 == 6:   
            self.status             = "ACC_DATA_NOT_AVAILABLE"
               
        self.currentPosRecharge     = deserialize_uint32(payload[56:60])/100.00      
        self.currentNegRecharge     = deserialize_uint32(payload[60:64])/100.00
        self.egCharges              = deserialize_uint32(payload[64:68])/100.00
        self.dgCharges              = deserialize_uint32(payload[68:72])/100.00
        self.energyAtSOMEg          = deserialize_uint32(payload[72:76])/100.00
        self.energyAtSOMDg          = deserialize_uint32(payload[76:80])/100.00
        self.currentNetRecharge     = deserialize_int32(payload[20:24])/100.00
        # if len(payload) > 84:
        self.cummEgFdCost       = deserialize_uint32(payload[24:28])/100.00
        # if len(payload) > 88:
        if payload[80] == 0:
            self.billType           = "kVAh"        

    def getPacketPrepaidInfo(self):

        return (\
        "Prepaid Mode                       : {}\n"
        "Prepaid Billing Type               : {}\n"
        "Change Prepaid Mode Time Stamp     : {}\n"
        "Account balance                    : {} Rs\n"
        "Energy at start of month           : {} {}\n"
        "Time Stamp Of Last Prepaid Billing : {}\n"
        "New Tariff Activation Time Stamp   : {}\n"
        "Next Tariff To Activate            : {}\n"
        "Activated Tariff Group Number      : {}\n"
        "Net Positive Recharge              : {} Rs\n"
        "Net Negative Recharge              : {} Rs\n"
        "Net Recharge                       : {} Rs\n"
        "Current Account Balance            : {} Rs\n"
        "Current FD Cost                    : {} Rs\n"
        "Current Energy Cost                : {} Rs\n"
        "Status                             : {}\n"
        "Current Positive Recharge          : {} Rs\n"
        "Current Negative Recharge          : {} Rs\n"
        "EG Consumption Charge              : {} Rs\n"
        "DG Consumption Charge              : {} Rs\n"
        "EG Energy Consumed                 : {} {}\n"
        "DG Energy Consumed                 : {} {}\n"
        "Current Net Recharge               : {} Rs \n"
        "Cummulative EG FD Cost             : {} Rs \n")\
                .format(\
                        self.prepaidEnableF,
                        self.billType,
                        self.prepaidModeChangeTS,
                        self.balance,
                        self.energyAtSOM, self.billType,
                        self.lastBillTS,
                        self.newTariffTS,  
                        self.tariffToActivate,         
                        self.nowGroup,
                        self.CummulativePosRecharge,       
                        self.CummulativeNegRecharge,       
                        self.netRecharge,       
                        self.currentACBalance,  
                        self.currentFDCost,     
                        self.currentEnergyCost, 
                        self.status,
                        self.currentPosRecharge,
                        self.currentNegRecharge,
                        self.egCharges,
                        self.dgCharges,
                        self.energyAtSOMEg, self.billType,
                        self.energyAtSOMDg, self.billType,
                        self.currentNetRecharge,
                        self.cummEgFdCost)

    def deserializeTariffGroupInfo(self,payload):
        bytes = bytearray()
        bytes = payload
        temp  = deserialize_uint16(payload[0:2],"reverse")

        if temp == 0:
            self.fdType = "daily"
        elif temp == 1:
            self.fdType = "monthly"
        elif temp == 2:
            self.fdType = "slabwise"
        else:
            self.fdType = "NA"
        
        self.fdTelescopicF              = deserialize_uint16(payload[2:4],"reverse") 
        self.mmcApplication             = deserialize_uint16(payload[4:6],"reverse") 
        intFriendlyHours                = int(bytes[6])
        
        friendlyHoursAM = (intFriendlyHours & 0b00001111)
        friendlyHoursPM = (intFriendlyHours & 0b11110000)>>4

        if(friendlyHoursAM == 12):
            self.friendlyHours          = str(friendlyHoursPM) + " PM to " + str(friendlyHoursAM) + " PM"
        elif friendlyHoursAM == 0 and  friendlyHoursPM == 0:
            self.friendlyHours          = str(friendlyHoursPM) + " , " + str(friendlyHoursAM)
        else:
            self.friendlyHours          = str(friendlyHoursPM) + " PM to " + str(friendlyHoursAM) + " AM"
            
        self.alertLimit                 = int(bytes[7])
        self.emergencyCredit            = int(bytes[8])
        self.topUpLimit                 = int(bytes[9])
        self.mmc                        = deserialize_uint16(payload[10:12],"reverse")        
        for i in range(6):
            self.fdPrice[i]              = deserialize_uint32(payload[12+(i*4):16+(i*4)],"reverse")

        for i in range(6):
            self.energyPrice[i]          = (deserialize_uint16(payload[36+(i*2):38+(i*2)],"reverse"))

        for i in range(5):
            self.energySlab[i]           = deserialize_uint16(payload[48+(i*2):50+(i*2)],"reverse")  


    def getTariffGroupInfo(self):
        return (\
        "Fixed Deduction Prices             : {} Paisa\n"
        "Fixed Deduction Type               : {} \n"
        "Fixed Deduction Telescopic Flag    : {} \n"                
        "Slab Prices                        : {} Paisa\n"
        "Slab Energies                      : {} KWh\n"
        "Monthly Minimum Charge             : {} Rs\n"
        "Friendly Hours                     : {} \n"
        "MMC Application                    : {} \n"
        "Alert limit                        : {} *10 Rs\n"
        "Emergency Credits                  : {} *10 Rs\n"
        "Topup limit                        : {} *1000 Rs\n")\
                .format(\
                        self.fdPrice,
                        self.fdType,
                        self.fdTelescopicF,
                        self.energyPrice,
                        self.energySlab,
                        self.mmc,
                        self.friendlyHours,
                        self.mmcApplication,                        
                        self.alertLimit,
                        self.emergencyCredit,
                        self.topUpLimit)


    def serialize(self):

        payload = bytearray()

        payload.extend(serialize.serialize_uint16(self.fdType,"reverse"))
        payload.extend(serialize.serialize_uint16(self.fdTelescopicF,"reverse"))
        payload.extend(serialize.serialize_uint16(self.mmcApplication,"reverse"))
        payload.extend(serialize.serialize_uint8(self.friendlyHours,"reverse"))
        payload.extend(serialize.serialize_uint8(self.alertLimit,"reverse"))
        payload.extend(serialize.serialize_uint8(self.emergencyCredit,"reverse"))
        payload.extend(serialize.serialize_uint8(self.topUpLimit,"reverse"))
        payload.extend(serialize.serialize_uint16(self.mmc,"reverse"))    
        
        for index in range(len(self.fdPrice)):
            payload.extend(serialize.serialize_uint32(self.fdPrice[index],"reverse"))

        for index in range(len(self.energyPrice)):
            payload.extend(serialize.serialize_uint16(self.energyPrice[index],"reverse"))
        for index in range(len(self.energySlab)):
            payload.extend(serialize.serialize_uint16(self.energySlab[index],"reverse"))
        payload.extend(serialize.serialize_uint8(self.tariffType,"reverse"))
        return payload

    def deserializePrepaidLogs(self,payload):
        bytes = bytearray()
        # print ">>>>>>>>>>>>>>>>>>>>>>>."
        bytes = payload

        temp                            = deserialize_uint16(payload[0:2],"reverse")
        if temp == 0: 
            self.nowGroup = "DG Tariff"
        elif temp == 1:
            self.nowGroup = "EG Tariff"

        self.tariffChangeReqF           = deserialize_uint16(payload[2:4],"reverse")
        self.prepaidModeChangeReqF      = deserialize_uint16(payload[4:6],"reverse") 
        self.energyAtSOM                = (deserialize_uint32(payload[6:10],"reverse"))/100.00
        self.lastBillTS                 = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[13]<<24) + (bytes[12]<<16) +(bytes[11]<<8) + bytes[10]))                       
        
        self.newTariffTS                = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[17]<<24) + (bytes[16]<<16) +(bytes[15]<<8) + bytes[14])) 
        self.prepaidModeChangeTS        = datetime.datetime(1970, 1, 1) +\
                    datetime.timedelta(seconds=((bytes[21]<<24) + (bytes[20]<<16) +(bytes[19]<<8) + bytes[18])) 
        
        self.tariffToActivate                = deserialize_uint16(payload[22:24],"reverse")
        temp             = deserialize_uint16(payload[24:26],"reverse")
        if temp == 0:
            self.prepaidEnableF = "Disabled"
        elif temp == 0x55:
            self.prepaidEnableF = "Enabled"
        else:
            self.prepaidEnableF = "NA"

        self.balance                = deserialize_int32(payload[26:30],"reverse")/100.00
        self.CummulativePosRecharge = deserialize_uint32(payload[30:34],"reverse")/100.00
        self.CummulativeNegRecharge = deserialize_int32(payload[34:38],"reverse")/100.00
        self.currentPosRecharge     = deserialize_uint32(payload[38:42],"reverse")/100.00
        self.currentNegRecharge     = deserialize_uint32(payload[42:46],"reverse")/100.00
        self.egCharges              = deserialize_uint32(payload[46:50],"reverse")/100.00
        self.dgCharges              = deserialize_uint32(payload[50:54],"reverse")/100.00
        self.energyAtSOMEg          = deserialize_uint32(payload[54:58],"reverse")/100.00
        self.energyAtSOMDg          = deserialize_uint32(payload[58:62],"reverse")/100.00
        if payload[62] == 0:
            self.billType           = "kVAh"

    def getPacketPrepaidLogs(self):

        return (\
        "Prepaid Mode                       : {}\n"
        "Prepaid Billing Type               : {}\n"
        "Change Prepaid Mode Time Stamp     : {}\n"
        "Account balance                    : {} Rs\n"
        "Energy at start of month           : {} {}\n"
        "Time Stamp Of Last Prepaid Billing : {}\n"
        "New Tariff Activation Time Stamp   : {}\n"
        "Next Tariff To Activate            : {}\n"
        "Activated Tariff Group Number      : {}\n"
        "Net Positive Recharge              : {} Rs\n"
        "Net Negative Recharge              : {} Rs\n"
        "Current Positive Recharge          : {} Rs\n"
        "Current Negative Recharge          : {} Rs\n"
        "EG Consumption Charge              : {} Rs\n"
        "DG Consumption Charge              : {} Rs\n"
        "EG Energy Consumed                 : {} {}\n"
        "DG Energy Consumed                 : {} {}\n")\
                .format(\
                        self.prepaidEnableF,
                        self.billType,
                        self.prepaidModeChangeTS,
                        self.balance,
                        self.energyAtSOM, self.billType,
                        self.lastBillTS,
                        self.newTariffTS,  
                        self.tariffToActivate,         
                        self.nowGroup,
                        self.CummulativePosRecharge,       
                        self.CummulativeNegRecharge,
                        self.currentPosRecharge,
                        self.currentNegRecharge,
                        self.egCharges,
                        self.dgCharges,
                        self.energyAtSOMEg, self.billType,
                        self.energyAtSOMDg, self.billType)