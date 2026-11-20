import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io_new import FlashIOMasterNew, FlashIOErrorNew
from gp_node.utils.address import Address

import serial
import gp_node.utils.serialize as serialize
import json
import datetime
import time

# START_ADDRESS = 0x0100
# METER_ADDRESS = "255.255.255.255" ##"6.0.7.self.Len0"
# DCU_NUMBER_Ver = 0

class TestCasePCTMCT():
    def __init__(self,ser,portID,cfg): 
        # Thread.__init__(self) 
        # self.portID = portID 
        self.cfg = cfg
        self.network_api = NetworkAPI(ser, portID, "irda")
        self.Len = cfg.RETRIES
        self.dcu_time = ""
        self.live_version_V = 0
        self.Pass = 'Pass'
        self.Fail = 'Fail'
        self.METER_ADDRESS = "255.255.255.255"

    def set_unicast_address(self, address):
        self.METER_ADDRESS = address
        print "Unicast address", self.METER_ADDRESS, address

    def return_dictionary_value(self,RetryV,ResultS): 
        return_dict = {} 
        if (ResultS == 'Pass'):
            return_dict["Result"] = 'Pass'
            return_dict["Retries"] = RetryV+1
            return return_dict 

        else:
            return_dict["Result"] = 'Fail'
            return_dict["Retries"] = RetryV+1
            return return_dict      
    
        

    def Set_time_val(self):
        print "\nSending command to set ip time"
        for i in range(self.Len):
            try:
                SetTime = self.network_api.set_ip_time(Address(self.METER_ADDRESS),"now")
                print "Set_meter_Time:",SetTime
                if SetTime == 'ok':
                    return self.return_dictionary_value(i,self.Pass)
                    
                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Verify_time_val(self):
        return_dict = {}
        for i in range(self.Len):
            try:
                print "\nSending command to verify time"
                GetTime = self.network_api.get_time(Address(self.METER_ADDRESS))
                print "Get_Time:",GetTime
                timeDiff = (datetime.datetime.now() - GetTime).total_seconds()
                print "meter time Diff",timeDiff
                self.dcu_time = GetTime
                if timeDiff >= -20 and timeDiff < 200  :
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    if i == (self.Len-1):
                        return self.return_dictionary_value(i,self.Fail)
                    
            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
                

    def Factory_reset_val(self):
        print "\nSending command to do factory reset"
        for i in range(self.Len):
            try:
                FactoryInit = self.network_api.factory_init_1(Address(self.METER_ADDRESS))
                print "FactoryInit:",FactoryInit
                if FactoryInit == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Meter_Relay_On(self):
        print "\nSending command to do turn relay ON"
        for i in range(self.Len):
            try:
                RelayON = self.network_api.turn_relay_on(Address(self.METER_ADDRESS))
                print "turn relay ON:",RelayON
                if RelayON == 'relay turned on':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Meter_Relay_OFF(self):
        print "\nSending command to do turn relay OFF"
        for i in range(self.Len):
            try:
                RelayOFF = self.network_api.turn_relay_off(Address(self.METER_ADDRESS))
                print "turn relay OFF:",RelayOFF
                if RelayOFF == 'relay turned off':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)      

    def Verify_Current(self,Maxvalue,IsOff = False):
        print "\nSending command to do verify current"
        for i in range(self.Len):
            try:
                Current = self.network_api.get_3p_metering_data(Address(self.METER_ADDRESS))
                CurrentV = Current.return_params["phase_current"]
                CurrentN = Current.return_params["neutral_current"]
                print "Verify Phase Current:   ",CurrentV
                print "Verify Neutral Current: ",CurrentN
                if (IsOff == True):
                    if CurrentV <= Maxvalue and CurrentN <= Maxvalue:
                        return self.return_dictionary_value(i,self.Pass)

                    else:
                        return self.return_dictionary_value(i,self.Fail)     

                elif (IsOff == False):
                    if CurrentV >= Maxvalue and CurrentN >= Maxvalue:
                        return self.return_dictionary_value(i,self.Pass)

                    else:
                        return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    
    def Verify_Voltage(self,Minvalue,Maxvalue):
        print "\nSending command to do verify voltage"
        for i in range(self.Len):
            try:
                Voltage = self.network_api.get_3p_metering_data(Address(self.METER_ADDRESS))
                VoltageV = Voltage.return_params["voltage"]
                print "Verify voltage:",VoltageV
                if VoltageV >= Minvalue and VoltageV <= Maxvalue:
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)   

    def Verify_Energy_value(self):
        print "\nSending command to do verify energy"
        for i in range(self.Len):
            try:
                energy = self.network_api.get_3p_metering_data(Address(self.METER_ADDRESS))
                VoltageV = energy.return_params["activeHr_energy_imp"]
                print "Verify energy:",VoltageV
                if float(VoltageV) <= (0.1):
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)                

    def Calibration_unLock(self):
        print "\nSending command to do Calibration_unLock"
        for i in range(self.Len):
            try:
                arg_val = "0x300,2,bc 5a"
                Calib = self.network_api.eeprom_write(Address(self.METER_ADDRESS),arg_val)
                arg_val2 = "0x300,2,b0 5a"
                time.sleep(1)
                Calib2 = self.network_api.eeprom_write(Address(self.METER_ADDRESS),arg_val2)
                print "Calib Unlock:",Calib,Calib2
                if Calib == 'ok' and Calib2 == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Calibration_Status(self,IsUnlock =False):
        print "\nSending command to do verify Calibration state"
        if IsUnlock == True:
            calibStr = 'Calib Unlocked !!!'
        else:
            calibStr = 'Calib Locked !!!'
        for i in range(self.Len):
            try:
                CalibS = self.network_api.get_calib_status(Address(self.METER_ADDRESS))
                print "Verify Calibration State:",CalibS
                if CalibS == calibStr:
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
                                      

    def Verify_Relay_State(self):
        print "\nSending command to do verify Relay state"
        for i in range(self.Len):
            try:
                Relay = self.network_api.relay_state(Address(self.METER_ADDRESS))
                print "Verify Relay State:",Relay
                if Relay == 'MANUAL_CONTROL_ON':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail) 

    def Set_Meter_serial_number(self,SrNumber):
        print "\nSending command to do Set serial number"
        for i in range(self.Len):
            try:
                SrNumbER = self.network_api.set_serial_number(Address(self.METER_ADDRESS),SrNumber)
                print "Set Meter Serial number:",SrNumbER
                if SrNumbER == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Verify_Serial_number(self,SrNumber):
        print "\nSending command to do verify Serial number"
        for i in range(self.Len):
            try:
                SERIAL_NUMBER = self.network_api.get_meter_serial_no(Address(self.METER_ADDRESS))
                # print "SERIAL_NUMBER",SERIAL_NUMBER
                SERIAL_NUMBER_V = SERIAL_NUMBER.split('UID 1')
                SERIAL_NUMBER_V2 = SERIAL_NUMBER_V[0].split(':')
                # print "SERIAL_NUMBER",SERIAL_NUMBER_V2
                SerialNumber = SERIAL_NUMBER_V2[1].split(' ')[1]
                print "get_meter_serial_no",SerialNumber
                if str(SerialNumber) == str(SrNumber):
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)  

    def Set_Meter_address(self,MetrAddress):
        print "\nSending command to do Set meter address"
        for i in range(self.Len):
            try:
                MtrAddr = self.network_api.set_address(Address(self.METER_ADDRESS),str(MetrAddress))
                print "Set Meter address:",MtrAddr
                if MtrAddr == 'ok' or MtrAddr == 'Okay':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Verify_Meter_address(self,MetrAddress):
        for i in range(self.Len):
            try:
                print "\nSending command to do Get meter address"
                MtrAddr = self.network_api.get_address(Address(self.METER_ADDRESS))
                print "Get Meter address:",MtrAddr
                if str(MtrAddr) == str(MetrAddress):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    if i == (self.Len-1):
                        return self.return_dictionary_value(i,self.Fail)
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Set_Meter_PCB_serial_number(self,SrNumber):
        print "\nSending command to do Set PCB serial number"
        for i in range(self.Len):
            try:
                SrNumbER = self.network_api.set_pcb_serial_no(Address(self.METER_ADDRESS),SrNumber)
                print "Set Meter PCB Serial number:",SrNumbER
                if SrNumbER == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Get_Meter_PCB_serial_number(self,SrNumberV):
        print "\nSending command to do Get PCB serial number"
        for i in range(self.Len):
            try:
                SrNumbER = self.network_api.get_pcb_serial_no(Address(self.METER_ADDRESS))
                arg = str(SrNumbER)
                arg1 = arg.split("\0")[0]
                print "Get Meter PCB Serial number:",arg1
                if arg1 == str(SrNumberV):
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)


    def Clear_Energy_Value(self):
        print "\nSending command to Clear Energy"
        for i in range(self.Len):
            try:
                ClearEnergy = self.network_api.tod_enable(Address(self.METER_ADDRESS))
                print "Clear Energy:",ClearEnergy
                if ClearEnergy == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def get_live_version_val(self):
        
        for i in range(self.Len):
            try:
                print "\nSending command to get live version"
                liveversion = self.network_api.get_live_version(Address(self.METER_ADDRESS))
                print "live_version",liveversion
                self.live_version_V = liveversion
                if str(liveversion)!='':
                    return liveversion
                
            except:
                pass
                
         

    def get_time_and_version_val(self):
        return_list = []
        return_list.append(self.dcu_time)   
        return_list.append(self.live_version_V)
        # print "List of dcu time and version",return_list
        return return_list   

    def get_meter_sim_and_sim_number(self):
        return_list = []
        for i in range(self.Len):
            try:
                print "\nSending command to verify sim number"
                dcuParams = self.network_api.get_gprs_ip(Address(self.METER_ADDRESS))
                print "dcuParams",dcuParams
                arg = dcuParams.split(",")
                if (len(arg) > 3):
                    return_list.append(arg[3].decode())
                    return_list.append('1')
                    return_list.append(arg[2].decode())
                    print "SIM_NUM:",return_list[0]
                    print "Active_Sim:",return_list[1]
                    print "APN:",return_list[2]
                    return return_list
                # if (dcuParams["Active_Sim"] == 1 or dcuParams["Active_Sim"] == 2):
                #     return_list.append(dcuParams["SIM_NUM"].decode())
                #     return_list.append(dcuParams["Active_Sim"])
                #     apn_number = str(dcuParams["APN"].decode())
                #     apn_number = apn_number.split('"')[1]
                #     return_list.append(apn_number)
                #     print "SIM_NUM:",return_list[0]
                #     print "Active_Sim:",return_list[1]
                #     print "APN:",return_list[2]
                #     return return_list
    
            except:
                pass
        return return_list  
        
    def Set_network_val(self,index_val):
        print "\nSending command to set network"
        for i in range(self.Len):
            try:
                Setnum = self.network_api.set_network(Address(self.METER_ADDRESS), index_val)
                print "Set_network:",Setnum
                if (Setnum == 'ok') or (Setnum == 'Okay'):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
                
            

    def Set_channel_val(self,index_val):
        print "\nSending command to set channel"
        for i in range(self.Len):
            try:
                Setnum = self.network_api.set_channel(Address(self.METER_ADDRESS), index_val)
                print "Set_channel:",Setnum
                if (Setnum == 'ok') or (Setnum == 'Okay'):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    # def Set_router_val(self):
    #     print "\nSending command to set router mode"
    #     for i in range(self.Len):
    #         try:
    #             Setnum = self.network_api.set_gateway_mode(Address(self.METER_ADDRESS), 0)
    #             print "Set_router_mode:",Setnum
    #             if (Setnum == 'ok') or (Setnum == 'Okay'):
    #                 return self.return_dictionary_value(i,self.Pass)
    #             else:
    #                 return self.return_dictionary_value(i,self.Fail)

    #         except:
    #             if ((i+1)==self.Len):
    #                 return self.return_dictionary_value(i,self.Fail)

    def Get_network_val(self,index_val):
        print "\nSending command to Verify meter network"
        for i in range(self.Len):
            try:
                Setnum = self.network_api.get_network(Address(self.METER_ADDRESS))
                print "Get_network:",Setnum
                if int(Setnum) == int(index_val):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Get_channel_val(self,index_val):
        print "\nSending command to Verify channel"
        for i in range(self.Len):
            try:
                Setnum = self.network_api.get_channel(Address(self.METER_ADDRESS))
                print "Get_channel:",Setnum
                if int(Setnum) == int(index_val):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Set_Current_rating(self,index_val):
        print "\nSending command to Set current rating", self.cfg.CURRENT_RATING
        for i in range(self.Len):
            try:
                Setrating = self.network_api.set_current_rating_dlms(Address(self.METER_ADDRESS),
                                                                     self.cfg.CURRENT_RATING)
                print "Set_rating:", self.cfg.CURRENT_RATING
                if (Setrating == 'ok') or (Setrating == 'Okay'):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Enable_Print(self):
        self.network_api.enable_print_rxtx(Address(self.METER_ADDRESS))                

    # def Get_dcu_gateway_val(self):
    #     print "\nSending command to Verify dcu gateway"
    #     return_dict = {}
    #     for i in range(self.Len):
    #         try:
    #             Setnum = self.network_api.get_dcu_gateway_mode(Address(self.METER_ADDRESS))
    #             print "Get_dcu_gateway_mode:",Setnum
    #             if int(Setnum) == 1:
    #                 return_dict["Result"] = 'Pass'
    #                 return_dict["Retries"] = i+1
    #                 return return_dict
    #             else:
    #                 return_dict["Result"] = 'Fail'
    #                 return_dict["Retries"] = i+1
    #                 return return_dict    
    #         except:
    #             if ((i+1)==self.Len):
    #                 return_dict["Result"] = 'Fail'
    #                 return_dict["Retries"] = i+1
                
    #     return return_dict 

    # def Get_dcu_protocol_val(self):
    #     print "\nSending command to Verify dcu protocol"
    #     return_dict = {}
    #     for i in range(self.Len):
    #         try:
    #             Setnum = self.network_api.get_dcu_protocol_mode(Address(self.METER_ADDRESS))
    #             print "Get_dcu_protocol_val:",Setnum
    #             if int(Setnum) == 1:
    #                 return_dict["Result"] = 'Pass'
    #                 return_dict["Retries"] = i+1
    #                 return return_dict
    #             else:
    #                 return_dict["Result"] = 'Fail'
    #                 return_dict["Retries"] = i+1
    #                 return return_dict    
    #         except:
    #             if ((i+1)==self.Len):
    #                 return_dict["Result"] = 'Fail'
    #                 return_dict["Retries"] = i+1
                
    #     return return_dict 

    # def Set_dcu_address_val(self,index_val):
    #     return_dict = {}
    #     for i in range(self.Len):
    #         try:
    #             Setnum = self.network_api.set_dcu_address(Address(self.METER_ADDRESS), index_val)
    #             # print "Set",Setnum
    #             if (Setnum == 'ok') or (Setnum == 'Okay'):
    #                 return_dict["Result"] = 'Pass'
    #                 return_dict["Retries"] = i+1
    #                 return return_dict
    #             else:
    #                 return_dict["Result"] = 'Fail'
    #                 return_dict["Retries"] = i+1
    #                 return return_dict    
    #         except:
    #             if ((i+1)==self.Len):
    #                 return_dict["Result"] = 'Fail'
    #                 return_dict["Retries"] = i+1
                
    #     return return_dict 

    # def SetRfModuleType(self, RfmoduleType):
    #     erase_block  = False # erase multiple of 0x10000
    #     erase_sector = True  # erase multiple of 0x1000
    #     MAGIC_ADDRESS = 0x00fdb000   #address of RF module type store
    #     flash_io_dcu = self.network_api.my_flash_io_master_dcu

    #     flash_io_dcu.erase(Address("255.255.255.255"), 4059, erase_sector) 
    #     time.sleep(1)
    #     if RfmoduleType == 'TM':
    #         Mod = ['T','M','M','T']
    #         magicPck=bytearray(Mod)
    #     else:
    #         Mod = ['W','P','P','W']
    #         magicPck=bytearray(Mod) 
    #     for j in range(self.Len):       
    #         value =  flash_io_dcu.writeData(Address("255.255.255.255"), start_address = MAGIC_ADDRESS, data = magicPck)
    #         if (value == 'ok') or (value == 'Okay'):
    #             time.sleep(1)
    #             returnData = flash_io_dcu.read(Address("255.255.255.255"), start_address = MAGIC_ADDRESS,length = 4) 
    #             for i in range(4,8):
    #                 if hex(returnData[i]) == hex(ord(Mod[i-4])):
    #                     if i == 9:
    #                         j = j + self.Len
                                    



#     