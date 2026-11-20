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
import easygui
import logging


# START_ADDRESS = 0x0100
# METER_ADDRESS = "255.255.255.255" ##"6.0.7.self.Len0"
# DCU_NUMBER_Ver = 0

class TestCasePCTMCT():
    def __init__(self,ser,portID,RETRIES, NIC_PCB_LENGTH): 
        # Thread.__init__(self) 
        # self.portID = portID 
        # self.cfg = cfg
        self.network_api = NetworkAPI(ser, portID, "irda")
        self.Len = RETRIES
        self.nic_pcb_len=NIC_PCB_LENGTH
        self.dcu_time = ""
        self.live_version_V = 0
        self.Pass = 'Pass'
        self.Fail = 'Fail'
        self.METER_ADDRESS = "255.255.255.255"

    def set_unicast_address(self, address):
        self.METER_ADDRESS = address
        print("Unicast address", self.METER_ADDRESS, address)

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
        print("\nSending command to set ip time")
        for i in range(self.Len):
            try:
                SetTime = self.network_api.set_ip_time(Address(self.METER_ADDRESS),"now")
                print("Set_meter_Time:",SetTime)
                if SetTime == 'ok':
                    return self.return_dictionary_value(i,self.Pass)
                    
                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    def Set_md_reset(self):
        print("\nSending command to do MD Reset")
        for i in range(self.Len):
            try:
                set_md_Reset = self.network_api.md_reset(Address(self.METER_ADDRESS))
                print("Set_md_Reset:",set_md_Reset)
                if set_md_Reset == 'ok':
                    return self.return_dictionary_value(i,self.Pass)
                    
                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)


    def Verify_time_val(self):
        print("\nSending command to verify time")
        return_dict = {}
        for i in range(self.Len):
            try:
                GetTime = self.network_api.get_time(Address(self.METER_ADDRESS))
                print("Get_Time:",GetTime)
                timeDiff = (datetime.datetime.now() - GetTime).total_seconds()
                print("meter time Diff",timeDiff)
                self.dcu_time = GetTime
                if timeDiff >= -20 and timeDiff < 20  :
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)
                    
            except:
                print("Retry")
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def get_apparent_led_status(self):
        print("\nSending command to get Apparent Led Status")
        logging.info("Retrieving apparent LED status")
        for i in range(self.Len):
            try:
                app_led = self.network_api.get_apprent_led(Address(self.METER_ADDRESS))
                print("\nApparent Led status",app_led)
                logging.info(f"Retrieved apparent LED status: {app_led}")
                if(str(app_led) == '0xAA'):
                    return {"Result": "Pass", "Retries": i+1, "Apparent_LED_Status": app_led}
                    # return self.return_dictionary_value(i,self.Pass)
                else:
                    # return self.return_dictionary_value(i,self.Fail)
                    return {"Result": "Fail", "Retries": i+1, "Apparent_LED_Status": app_led}
                
            except Exception as e:
                logging.error(f"Error occurred while retrieving apparent LED status: {e}")
                if ((i+1)==self.Len):
                    # return self.return_dictionary_value(i,self.Fail)
                    return {"Result": "Fail", "Retries": i+1, "Apparent_LED_Status": None}
                

    def Factory_reset_val(self):
        print("\nSending command to do factory reset")
        logging.info("Performing factory reset")
        for i in range(self.Len):
            try:
                FactoryInit = self.network_api.factory_init_1(Address(self.METER_ADDRESS))
                logging.info(f"Factory reset result: {FactoryInit}")
                print("FactoryInit:",FactoryInit)
                if FactoryInit == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)
                
            except Exception as e:
                logging.error(f"Error occurred during factory reset: {e}")    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Meter_Relay_On(self):
        print("\nSending command to do turn relay ON")
        for i in range(self.Len):
            try:
                RelayON = self.network_api.turn_relay_on(Address(self.METER_ADDRESS))
                print("turn relay ON:",RelayON)
                if RelayON == 'relay turned on':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Meter_Relay_OFF(self):
        print("\nSending command to do turn relay OFF")
        for i in range(self.Len):
            try:
                RelayOFF = self.network_api.turn_relay_off(Address(self.METER_ADDRESS))
                print("turn relay OFF:",RelayOFF)
                if RelayOFF == 'relay turned off':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)   
    def metering_mode_set(self,mode):
        if (mode==1):
            print("\n sending command to set metering mode 1")
        else:
            print("\n sending command to set metering mode 0")
        metering_mode_Set = self.network_api.set_metering_mode(Address(self.METER_ADDRESS),mode)
        if metering_mode_Set == 'ok' or  metering_mode_Set == 'Okay':
            print("metering mode is changed ")
        else:
            print("metering mode is not changed")


    def relay_mode_set(self,mode):
        print("\nsending command to set relay state 5")
        for i in range(self.Len):
            try:
                metering_mode_Set = self.network_api.set_relay_mode(Address(self.METER_ADDRESS),mode)
                print("metering mode changed:",metering_mode_Set)
                if metering_mode_Set == 'ok' or  metering_mode_Set == 'params rejected':
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)  

    def Verify_active_power(self):
        print("\nSending command to do verify Active Power")
        for i in range(self.Len):
            try:
                Current = self.network_api.get_1p_metering_data(Address(self.METER_ADDRESS))
                active_power=Current.return_params["active_power"]   
                if (active_power):
                    return float(active_power*1000)
                else:
                    return float(0.0)    
            except:    
                if ((i+1)==self.Len):
                    return float(0.0)


    def Verify_Current(self,Minvalue,Maxvalue,IsOff = False):
        print("\nSending command to do verify current")
        for i in range(self.Len):
            try:
                Current = self.network_api.get_1p_metering_data(Address(self.METER_ADDRESS))
                CurrentV = Current.return_params["phase_current"]
                CurrentN = Current.return_params["neutral_current"]
                live_tamper=Current.return_params["tamper_event"]

                print("Verify Phase Current:   ",CurrentV)
                print("Verify Neutral Current: ",CurrentN)
                print("Verify live tamper: ",live_tamper)
                if (IsOff == True):
                    # print ("hlo")
                    if ((Minvalue <= CurrentV <= Maxvalue) and (Minvalue <= CurrentN <= Maxvalue)) and ('CURRENT_REVERSE' not in live_tamper):
                        return self.return_dictionary_value(i,self.Pass)

                    else:
                        return self.return_dictionary_value(i,self.Fail)     

                elif (IsOff == False):
                    # print ("hi")
                    if ((Minvalue <= CurrentV <= Maxvalue) and (Minvalue <= CurrentN <= Maxvalue)) and ('CURRENT_REVERSE' not in live_tamper):
                        return self.return_dictionary_value(i,self.Pass)

                    else:
                        return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    
    def Verify_Voltage(self,Minvalue,Maxvalue):
        print("\nSending command to do verify voltage")
        for i in range(self.Len):
            try:
                Voltage = self.network_api.get_1p_metering_data(Address(self.METER_ADDRESS))
                VoltageV = Voltage.return_params["voltage"]
                print("Verify voltage:",VoltageV)
                if VoltageV >= Minvalue and VoltageV <= Maxvalue:
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)   

    def Verify_Energy_value(self):
        print("\nSending command to do verify energy")
        for i in range(self.Len):
            try:
                energy = self.network_api.get_1p_metering_data(Address(self.METER_ADDRESS))
                VoltageV = energy.return_params["activeHr_energy_imp"]
                print("Verify energy:",VoltageV)
                if float(VoltageV) <= (0.1):
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)                

    def Calibration_unLock(self):
        print("\nSending command to do Calibration_unLock")
        for i in range(self.Len):
            try:
                arg_val = "0x600,2,bc 5a"
                Calib = self.network_api.eeprom_write(Address(self.METER_ADDRESS),arg_val)
                logging.info(f"Calibration unlock command sent, response: {Calib}")
                arg_val2 = "0x600,2,b0 5a"
                time.sleep(0.5)
                Calib2 = self.network_api.eeprom_write(Address(self.METER_ADDRESS),arg_val2)
                logging.info(f"Calibration unlock command sent, response: {Calib2}")
                print("Calib Unlock:",Calib,Calib2)
                if Calib == 'ok' and Calib2 == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except Exception as e:    
                logging.error(f"Error occurred while performing calibration unlock: {e}")
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    def lag_only_mode_write(self):
        print("\nSending command to set lag only mode")
        for i in range(self.Len):
            try:
                arg_val = "0x314,1,1"
                Calib = self.network_api.eeprom_write(Address(self.METER_ADDRESS),arg_val)
                print("Lag only mode set :",Calib)
                if Calib == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Calibration_Status(self,IsUnlock =False):
        print("\nSending command to do verify Calibration state")
        if IsUnlock == True:
            calibStr = 'Calib Unlocked !!!'
        else:
            calibStr = 'Calib Locked !!!'
        for i in range(self.Len):
            try:
                CalibS = self.network_api.get_calib_status(Address(self.METER_ADDRESS))
                print("Verify Calibration State:",CalibS)
                if CalibS == calibStr:
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
                                      

    def Verify_Relay_State(self):
        print("\nSending command to do verify Relay state")
        for i in range(self.Len):
            try:
                Relay = self.network_api.relay_state(Address(self.METER_ADDRESS))
                print("Verify Relay State:",Relay)
                if Relay == 'MANUAL_CONTROL_ON':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail) 

    def Set_Meter_serial_number(self,SrNumber):
        print("\nSending command to do Set serial number")
        logging.info(f"Setting meter serial number: {SrNumber}")
        for i in range(self.Len):
            try:
                SrNumbER = self.network_api.set_serial_number(Address(self.METER_ADDRESS),SrNumber)
                print("Set Meter Serial number:",SrNumbER)
                logging.info(f"Set meter serial number response: {SrNumbER}")
                if SrNumbER == 'ok':
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except Exception as e:
                logging.error(f"Error occurred while setting meter serial number: {e}")    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    def Set_nic_pcb_no(self,nic_pcb_no):
        print("\nSending command to do Set nic pcb number")
        for i in range(self.Len):
            try:
                Sr_num_nic = self.network_api.set_nic_pcb_no(Address(self.METER_ADDRESS),nic_pcb_no)
                print("Set nic pcb number:",nic_pcb_no)
                if Sr_num_nic == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def set_tunnel_mode(self, Mode = '0xBB'):
        print("\nSending command to do Set Tunnel Mode", Mode)
        # for i in range(self.Len):
        try:
            Mode = self.network_api.set_debug_print(Address(self.METER_ADDRESS), Mode)
            print("Set Tunnel Mode: ",Mode)
            if( Mode.lower() == 'ok') or (Mode.lower() == 'okay'):
                return self.return_dictionary_value(0,self.Pass)
            elif( Mode.lower() == '?'):
                return self.return_dictionary_value(0,self.Fail)
            else:
                return self.return_dictionary_value(0,self.Fail)
            
        except Exception as e:    
            print("Exception in set_tunnel_mode", e)
            if ((self.Len)==self.Len):
                return self.return_dictionary_value(0,self.Fail)


    def Verify_Serial_number(self):
        print("\nSending command to do verify Serial number")
        logging.info("Verifying meter serial number")
        for i in range(self.Len):
            try:
                SERIAL_NUMBER = self.network_api.get_meter_serial_no(Address(self.METER_ADDRESS))
                # print("SERIAL_NUMBER",SERIAL_NUMBER)
                SERIAL_NUMBER_V = SERIAL_NUMBER.split('UID 1')
                SERIAL_NUMBER_V2 = SERIAL_NUMBER_V[0].split(':')
                # print("SERIAL_NUMBER",SERIAL_NUMBER_V2)
                SerialNumber = SERIAL_NUMBER_V2[1].split(' ')[1]
                print("get_meter_serial_no",SerialNumber)
                logging.info(f"Retrieved meter serial number: {SerialNumber}")
                if ((SerialNumber != '98765432') and (SerialNumber != '987654')):
                    return SerialNumber
                    # return self.return_dictionary_value(i,self.Pass)

                else:
                    print ("Serial No not set in Meter")
                    return SerialNumber
                    # return self.return_dictionary_value(i,self.Fail)    
                
            except Exception as e:
                logging.error(f"Error occurred while verifying meter serial number: {e}")    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    def Verify_Serial_number2(self):
        print("\nSending command to do verify Serial number")
        for i in range(self.Len):
            try:
                SERIAL_NUMBER = self.network_api.get_meter_serial_no(Address(self.METER_ADDRESS))
                # print("SERIAL_NUMBER",SERIAL_NUMBER)
                SERIAL_NUMBER_V = SERIAL_NUMBER.split('UID 1')
                SERIAL_NUMBER_V2 = SERIAL_NUMBER_V[0].split(':')
                # print("SERIAL_NUMBER",SERIAL_NUMBER_V2)
                SerialNumber = SERIAL_NUMBER_V2[1].split(' ')[1]
                print("get_meter_serial_no",SerialNumber)
                if((SerialNumber != '98765432') and (SerialNumber != '987654') and ('R161' not in SerialNumber) and ('r161' not in SerialNumber) and ('R154' not in SerialNumber) and ('r154' not in SerialNumber)):
                    # return SerialNumber
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)  

    def Nic_PCB_No(self, nic_start_address):
        logging.info("Retrieving NIC PCB number")
        print("Retrieving NIC PCB number")
        for i in range(self.Len):
            try:
                Nic_PCB_NUMBER = str(self.network_api.get_nic_pcb_serial_no(Address(self.METER_ADDRESS), nic_start_address))
                logging.info(f"Retrieved NIC PCB number: {Nic_PCB_NUMBER}")
                Nic_PCB_NUMBER1 = Nic_PCB_NUMBER.split("\0")[0]
                if Nic_PCB_NUMBER1.replace("\xff", "") == "":
                    Nic_PCB_NUMBER1 = "0"
                print("Nic_serial_no",Nic_PCB_NUMBER1)
                if str(Nic_PCB_NUMBER1)!='':
                    return Nic_PCB_NUMBER1
            except Exception as e:
                logging.error(f"Error occurred while retrieving NIC PCB number: {e}")
                pass

    def get_Meter_address(self):
        print("\nSending command to get meter address")
        logging.info("Retrieving meter address")
        for i in range(self.Len):
            try:
                MtrAddr = str(self.network_api.get_address(Address(self.METER_ADDRESS)))
                print("get Meter address:",MtrAddr)
                logging.info(f"Retrieved meter address: {MtrAddr}")
                # cal_address=self.make_address(serialnum_mct)
                if MtrAddr:
                    return MtrAddr
                    # return self.return_dictionary_value(i,self.Pass)
                else:
                    print("did not get meter address")
                    logging.warning("Meter address retrieval failed")
                    return MtrAddr
                    # return self.return_dictionary_value(i,self.Fail)    
                
            except Exception as e:
                logging.error(f"Error occurred while retrieving meter address: {e}")    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)


    def get_Meter_address2(self,serialnum_mct):
        print("\nSending command to get meter address")
        logging.info("Retrieving meter address")
        for i in range(self.Len):
            try:
                MtrAddr = self.network_api.get_address(Address(self.METER_ADDRESS))
                print("get Meter address:",MtrAddr)
                logging.info(f"Retrieved meter address: {MtrAddr}")
                cal_address=self.make_address(serialnum_mct)
                if str(MtrAddr) == cal_address:
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except Exception as e:
                logging.error(f"Error occurred while retrieving meter address: {e}")    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Verify_Meter_address(self,MetrAddress):
        print("\nSending command to do Get meter address")
        for i in range(self.Len):
            try:
                MtrAddr = self.network_api.get_address(Address(self.METER_ADDRESS),0)
                print("Get Meter address:",MtrAddr)
                if str(MtrAddr) == str(MetrAddress):
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)                                              

    def Verify_Batt_volt(self):
        print("\nSending command to Get Battery Voltage")
        for i in range(self.Len):
            try:
                print(1)
                batt_volt = self.network_api.get_battery_volt_params(Address(self.METER_ADDRESS))
                print("Battery Voltage is :",batt_volt)
                print(batt_volt)
                print(type(batt_volt))
                if (batt_volt >= float(3.5)):
                    print("hi")
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    print("hello")
                    return self.return_dictionary_value(i,self.Fail)    
            
            except:    
                if ((i+1)==self.Len):
                    print("hiiii")
                    return self.return_dictionary_value(i,self.Fail)     

    def Set_Meter_PCB_serial_number(self,SrNumber):
        print("\nSending command to do Set PCB serial number")
        for i in range(self.Len):
            try:
                # print("in ver class")
                SrNumbER = self.network_api.set_pcb_serial_no(Address(self.METER_ADDRESS),SrNumber)
                print("Set Meter PCB Serial number:",SrNumbER)
                if SrNumbER == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Get_Meter_PCB_serial_number(self,SrNumberV):
        print("\nSending command to do Get PCB serial number")
        # for i in range(self.Len):
        #     try:
                # SrNumbER = self.network_api.get_pcb_serial_no(Address(METER_ADDRESS))
                # arg = str(SrNumbER)
                # arg1 = arg.split("\0")[0]
                # print("Get Meter PCB Serial number:",arg1)
        if str(SrNumberV) != '':
            return self.return_dictionary_value(1,self.Pass)

        else:
            return self.return_dictionary_value(1,self.Fail)    
                
            # except:    
            #     if ((i+1)==self.Len):
            #         return self.return_dictionary_value(i,self.Fail)

    def Get_pcb_serial_num(self, start_address):
        print("\nSending command to do Get PCB serial number")
        logging.info("Retrieving PCB serial number")
        for i in range(self.Len):
            try:
                pcb_serial_no = str(self.network_api.get_pcb_serial_no(Address(self.METER_ADDRESS), start_address))
                pcb_serial_no1 = pcb_serial_no.split("\0")[0]
                if pcb_serial_no1.replace("\xff", "") == "":
                    pcb_serial_no1 = "0"
                logging.info(f"Retrieved PCB serial number for meter {self.METER_ADDRESS}: {pcb_serial_no1}")
                if str(pcb_serial_no1)!='':
                    return pcb_serial_no1
            except Exception as e:
                logging.error(f"Error occurred while retrieving PCB serial number for meter {self.METER_ADDRESS}: {e}")
                pass


    def Set_Current_rating(self):
        print("\nSending command to Set current rating:",self.cfg.CURRENT_RATING)
        for i in range(self.Len):
            try:
                Setrating = self.network_api.set_current_rating_dlms(Address(self.METER_ADDRESS),str(self.cfg.CURRENT_RATING))
                print("Set_rating:", self.cfg.CURRENT_RATING)
                if Setrating == 'ok' or Setrating == 'Okay':
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    def Set_manufacturing_year(self):
        print("\nSending command to Set manufacturing year:",self.cfg.MANUFACTURING_YEAR)
        for i in range(self.Len):
            try:
                Setrating = self.network_api.set_manufacturing_year_dlms(Address(self.METER_ADDRESS),str(self.cfg.MANUFACTURING_YEAR))
                print("Set_manufacturing_year:", self.cfg.MANUFACTURING_YEAR)
                if Setrating == 'ok' or Setrating == 'Okay':
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    def Set_payment_mode(self):
        print("\nSending command to Set payment mode:",self.cfg.PAYMENT_MODE)
        for i in range(self.Len):
            try:
                Setrating = self.network_api.set_payment_mode(Address(self.METER_ADDRESS),str(self.cfg.PAYMENT_MODE))
                print("Set_payment_mode:", self.cfg.PAYMENT_MODE)
                if Setrating == 'ok' or Setrating == 'Okay' or Setrating == "params rejected":
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    def get_3p_calib_coffi(self, calib_type = 'single_point'):
        print("\nSending command to get 3p calib cofficients", calib_type)
        for i in range(self.Len):
            try:
                calib_coffi=self.network_api.get_3p_calib_cofficient(Address(self.METER_ADDRESS), calib_type)
                if calib_coffi:
                    return calib_coffi
                else:
                    return 'fail'
            except:
                if ((i+1)==self.Len):
                    return 'fail'

    def set_gprs_protocol_val(self,index_val):
        print("\nSending command to set GPRS Protocol: ",index_val)
        logging.info(f"Setting GPRS Protocol to index value: {index_val}")
        for i in range(self.Len):
            try:
                Setnum = self.network_api.set_gprs_protocol(Address(self.METER_ADDRESS),index_val)
                print("Set GPRS Protocol:",Setnum)
                logging.info(f"Set GPRS Protocol response: {Setnum}")
                if (Setnum == 'ok') or (Setnum == 'Okay'):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except Exception as e:
                logging.error(f"Error occurred while setting GPRS protocol for port: {self.METER_ADDRESS}, Error: {e}")
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    
    def get_gprs_protocol_val(self):
        print("\nSending command to get GPRS Protocol ")
        logging.info(f"Retrieving GPRS protocol for port: {self.METER_ADDRESS}")
        for i in range(self.Len):
            try:
                Setnum = self.network_api.get_gprs_protocol(Address(self.METER_ADDRESS))
                logging.info(f"GPRS protocol retrieval result for port: {self.METER_ADDRESS}: {Setnum}")
                print(f"GPRS protocol retrieval result for port: {self.METER_ADDRESS}: {Setnum}")
                if (Setnum == 0xAC14):
                    print("TCP Protocol is activated")
                    return {"Result": "Pass", "Retries": i+1, "Protocol": Setnum}
                
                else:
                    return {"Result": "Fail", "Retries": i+1, "Protocol": Setnum}

            except Exception as e:
                logging.error(f"Error occurred while retrieving GPRS protocol for port: {self.METER_ADDRESS}, Error: {e}")
                if ((i+1)==self.Len):
                    return {"Result": "Fail", "Retries": i+1, "Protocol": None}

    def Clear_Energy_Value(self):
        print("\nSending command to Clear Energy")
        for i in range(self.Len):
            try:
                ClearEnergy = self.network_api.tod_enable(Address(self.METER_ADDRESS))
                print("Clear Energy:",ClearEnergy)
                if ClearEnergy == 'ok':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)    
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def get_live_version_val(self):
        # print(datetime.datetime.now())
        print("\nSending command to get live version")
        for i in range(2):
            try:
                print( self.METER_ADDRESS)
                liveversion = self.network_api.get_live_version(Address(self.METER_ADDRESS))
                print("live_version",liveversion)
                self.live_version_V = liveversion
                if str(liveversion)!='':
                    return liveversion
            except:
                if ((i+1)==2):
                    return "Fail"
    def get_internal_version_val(self):
        print("\nSending command to get internal version")
        logging.info("Retrieving internal version")
        for i in range(self.Len):
            try:
                print(self.METER_ADDRESS)
                int_version = self.network_api.get_int_version(Address(self.METER_ADDRESS))
                print("\nINTERNAL_VERSION",int_version)
                logging.info(f"Retrieved internal version: {int_version}")
                if(int_version):
                    return str(int_version)
                
            except Exception as e:
                logging.error(f"Error occurred while retrieving internal version: {e}")
                if ((i+1)==self.Len):
                    return '0'
                    
    def get_live_version_val_check_port(self):
        # print(datetime.datetime.now())
        print("\nSending command to get live version")
        for i in range(self.Len):
            try:
                print(self.METER_ADDRESS)
                liveversion = self.network_api.get_live_version(Address(self.METER_ADDRESS))
                print("live_version",liveversion)
                self.live_version_V = liveversion

                if str(liveversion)!='':
                    return liveversion
                
            except:
                if ((i+1)==self.Len):
                    return "Fail"

    def make_address(self, SERIAL_NUM):
        hex_value = hex(SERIAL_NUM)
        desired_length=8  # Convert hex string to integer
        byte_value=self.add_leading_zeros(hex_value, desired_length)
        # print(byte_value)
        
        Address_new=str(int(byte_value[0]+byte_value[1],16))+'.'+str(int(byte_value[2]+byte_value[3],16))+'.'+str(int(byte_value[4]+byte_value[5],16))+'.'+str(int(byte_value[6]+byte_value[7],16))
        print(Address_new)
        return Address_new
         
    def add_leading_zeros(self,hex_value, desired_length):
        hex_value = hex_value.lstrip('0x')
        hex_value = hex_value.lower()
        return "{:0>{width}}".format(hex_value, width=desired_length)

    def get_time_and_version_val(self):
        return_list = []
        return_list.append(self.dcu_time)   
        return_list.append(self.live_version_V)
        # print("List of dcu time and version",return_list)
        return return_list   
    
    def set_sim_toggle(self):
        print("\nSending command to do sim toggle")
        for i in range(self.Len):
            try:
                simStatus = self.network_api.set_gprs_sim_toggle(Address(self.METER_ADDRESS))
                print("After Toggle Sim No : ",simStatus)
                if (int(simStatus)== 1) or (int(simStatus)== 2):
                    return "Pass"
                else:
                    return "Fail"
                
            except:
                if ((i+1)==self.Len):
                    return "Fail"

    def get_meter_sim_and_sim_number(self):
        print("\nSending command to verify sim number")
        return_list = []
        for i in range(self.Len):
            try:
                dcuParams = self.network_api.get_gprs_profile_by_index(Address(self.METER_ADDRESS),0,isReturn=True)
                if dcuParams["Active_Sim"] == 1 :
                    return_list.append(dcuParams["Active_Sim"])

                    sim_num1 = dcuParams["SIM1_ICCID"].strip()
                    if(sim_num1):
                        return_list.append(sim_num1)
                    else:
                        return_list.append('0')   

                    apn1_raw = dcuParams["SIM1_APN"].strip()
                    if apn1_raw:
                        apn_number1 = apn1_raw.split('"')[1] if '"' in apn1_raw else apn1_raw
                        return_list.append(apn_number1)
                    else:
                        return_list.append('0')

                    imei = str(dcuParams["IMEI"].strip())
                    return_list.append(imei)
                    return_list.append(dcuParams["Signal_Strength"])

                elif dcuParams["Active_Sim"] == 2:
                    return_list.append(dcuParams["Active_Sim"])

                    sim_num2 = dcuParams["SIM2_ICCID"].strip()
                    if(sim_num2):
                        return_list.append(sim_num2)
                    else:
                        return_list.append('0')   

                    apn2_raw = dcuParams["SIM2_APN"].strip()
                    if apn2_raw:
                        apn_number2 = apn2_raw.split('"')[1] if '"' in apn2_raw else apn2_raw
                        return_list.append(apn_number2)
                    else:
                        return_list.append('0')

                    imei = str(dcuParams["IMEI"].strip())
                    return_list.append(imei)
                    return_list.append(dcuParams["Signal_Strength"])
                    
                    print("Active_Sim:",return_list[0])
                    print("SIM_NUM2:",return_list[1])
                    print("APN2:",return_list[2])
                    print("IMEI:",return_list[3])
                    print("Signal_Strength: ",return_list[4])
                    # print("SIM_NUM2:",return_list[5])
                    # print("APN2:",return_list[6])
                    # if (20 <= return_list[4]) and (return_list[4] != 99) and (return_list[4] != 255) and ((return_list[0] == 1) or (return_list[0] == 2)):
                else:
                    return "Fail"
                print("Active_Sim:",return_list[0])
                print("SIM_NUM:",return_list[1])
                print("APN:",return_list[2])
                print("IMEI:",return_list[3])
                print("Signal_Strength: ",return_list[4])
                if return_list :
                    return return_list
                else:
                    return "Fail"
            except Exception as e:
              print("Error occurred while fetching SIM details:", str(e))
              if ((i+1)==self.Len):
                return "Fail" 

    def check_num_events(self):
        # print(datetime.datetime.now())
        print("\nSending command to check num events")
        return_list1 = []
        return_list = []
        for i in range(self.Len):
         try:
             Check_Num_Events=self.network_api.get_num_event_record(Address(self.METER_ADDRESS))
             print(Check_Num_Events)
             # print(type(Check_Num_Events))
             event1=Check_Num_Events.return_params["current_events"]
             event2=Check_Num_Events.return_params["voltage_events"]
             event3=Check_Num_Events.return_params["power_events"]
             event4=Check_Num_Events.return_params["transactions_events"]
             event5=Check_Num_Events.return_params["non_rollover_events"]
             event6=Check_Num_Events.return_params["control_events"]
             event7=Check_Num_Events.return_params["other_events"]
             event8=Check_Num_Events.return_params["RF_events"]
             event9=Check_Num_Events.return_params["total_events"]
             return_list1.append(self.check_event_list(event1))
             return_list1.append(self.check_event_list(event2))
             return_list1.append(self.check_event_list(event4))
             return_list1.append(self.check_event_list(event5))
             return_list1.append(self.check_event_list(event6))
             return_list1.append(self.check_event_list(event7))
             # print(return_list1)
             if "fail" in return_list1:
                 # return_list=self.Fail
                 return self.return_dictionary_value(i,self.Fail)
             else:
                 return self.return_dictionary_value(i,self.Pass)
                 # print("the packet is in verification class",datetime.datetime.now())
         except:
              if ((i+1)==self.Len):
                 return self.return_dictionary_value(i,self.Fail)
      # except:

             # print(return_list)
             # return return_list
            # print(event1)
      # except:
      #        if ((i+1)==self.Len):
      #            return self.return_dictionary_value(i,self.Fail)
      # except:
      #        if ((i+1)==self.Len):
      #               return self.return_dictionary_value(i,self.Fail)
            # print(Check_Num_Events[1])
            # if ("No. of current related events" in Check_Num_Events):
            #     print("yes i found")
    def dlms_Activation_check_value(self, dlms_type = "old"):
        print(f"\nSending command to check dlms activation, dlms type: {dlms_type}")
        logging.info(f"Checking DLMS activation status, dlms type: {dlms_type}")
        for i in range(self.Len):
            try:
                dlms_act = self.network_api.check_dlms_activation(Address(self.METER_ADDRESS), dlms_type)
                logging.info(f"DLMS activation check result for meter {self.METER_ADDRESS}: {dlms_act}")
                if dlms_act == 0:
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)
            except Exception as e:
                logging.error(f"Error occurred while checking DLMS activation: {e}")
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Verify_energy(self):
        print("\nSending command to do verify Energy")
        logging.info("Verifying energy")
        for i in range(self.Len):
            try:
                Current = self.network_api.get_3p_metering_data(Address(self.METER_ADDRESS))
                energyA = Current.return_params["active_energy_imp"]
                energyApp = Current.return_params["apparent_energy_imp"]
                energyR = Current.return_params["reactive_energy_q1"]

                logging.info(f"Verify Active Energy for meter {self.METER_ADDRESS}: {energyA}")
                logging.info(f"Verify Apparent Energy for meter {self.METER_ADDRESS}: {energyApp}")
                logging.info(f"Verify Reactive Energy Q1 for meter {self.METER_ADDRESS}: {energyR}")

                if ((energyA == 0.0) and (energyApp == 0.0) and (energyR == 0.0)):
                    return {"Result": "Pass", "Retries": i+1, "Active Energy": energyA, "Apparent Energy": energyApp, "Reactive Energy Q1": energyR}
                    # return self.return_dictionary_value(i,self.Pass)

                else:
                    return {"Result": "Fail", "Retries": i+1, "Active Energy": energyA, "Apparent Energy": energyApp, "Reactive Energy Q1": energyR}
                    # return self.return_dictionary_value(i,self.Fail)     

            except Exception as e:
                logging.error(f"Error occurred while verifying energy for meter {self.METER_ADDRESS}: {e}")
                if ((i+1)==self.Len):
                    # return self.return_dictionary_value(i,self.Fail)
                    return {"Result": "Fail", "Retries": i+1, "Active Energy": None, "Apparent Energy": None, "Reactive Energy Q1": None}

    def hr_energy_register(self):
        print("\nSending command to check HR Energy Register")
        for i in range(self.Len):
            try:
                hr_energy_bucket = self.network_api.get_nxp_ene_data(Address(self.METER_ADDRESS),1)
                Act_hr_energy = hr_energy_bucket.return_params["activeHr_energy_imp"]
                print("Active HR Energy : {} Kwh".format(Act_hr_energy))
                if Act_hr_energy is not None:
                    return float(Act_hr_energy)
                else:
                    return "Fail"
            except:
                if ((i+1)==self.Len):
                    return "Fail"

    def check_event_list(self,events):
        if (events == 0):
            return "pass"
        else:
            # easygui.msgbox("fail in "+events)
            return "fail"


    def get_live_tamper(self):
        print("\nSending command to get live tamper")
        for i in range(self.Len):
            try:
                live_tamper=self.network_api.get_1p_metering_data(Address(self.METER_ADDRESS))
                live_event_tamper = live_tamper.return_params["tamper_event"]
                print("live tamper: ",live_event_tamper)
                return self.return_dictionary_value(i,self.Pass)
            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)


    def Set_network_val(self,index_val):
        print("\nSending command to set network")
        for i in range(self.Len):
            try:
                Setnum = self.network_api.set_network(Address(self.METER_ADDRESS), index_val)
                print("Set_network:",Setnum)
                if (Setnum == 'ok') or (Setnum == 'Okay'):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
                
            

    def Set_channel_val(self,index_val):
        print("\nSending command to set channel")
        for i in range(self.Len):
            try:
                Setnum = self.network_api.set_channel(Address(self.METER_ADDRESS), index_val)
                print("Set_channel:",Setnum)
                if (Setnum == 'ok') or (Setnum == 'Okay'):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)


    def Get_network_val(self,index_val):
        print("\nSending command to Verify meter network")
        for i in range(self.Len):
            try:
                Setnum = self.network_api.get_network(Address(self.METER_ADDRESS))
                print("Get_network:",Setnum)
                if int(Setnum) == int(index_val):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Get_channel_val(self,index_val):
        print("\nSending command to Verify channel")
        for i in range(self.Len):
            try:
                Setnum = self.network_api.get_channel(Address(self.METER_ADDRESS))
                print("Get_channel:",Setnum)
                if int(Setnum) == int(index_val):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def set_meter_type(self, Mode):
        print("\nSending command to do Set Meter Type Mode", Mode)
        for i in range(self.Len):
            try:
                Mode = self.network_api.set_meter_type(Address(self.METER_ADDRESS), Mode)
                print("Set Meter Type :",Mode)
                if Mode == 'ok' or Mode == 'Okay' or Mode == "params rejected":
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    
    def get_meter_type(self):
        print("\nSending command to do Get Meter Type Mode")
        for i in range(self.Len):
            try:
                meter_type = self.network_api.get_meter_type(Address(self.METER_ADDRESS))
                print("Set Meter Type :",meter_type)
                if "(10-60)A" in meter_type:
                    return "(10-60)A"
                elif "(20-100)A" in meter_type:
                    return "(20-100)A"
                elif "(10-100)A" in meter_type:
                    return "(10-100)A"
                else:
                    return "Fail"
                
            except:    
                if ((i+1)==self.Len):
                    return "Fail"

    def Set_Meter_RelayMode(self, Mode):
        print("\nSending command to do Set Relay Mode", Mode)
        for i in range(self.Len):
            try:
                Mode = self.network_api.set_relay_mode(Address(self.METER_ADDRESS), Mode)
                print("Set Relay Mode :",Mode)
                if Mode == 'ok' or Mode == 'Okay' or 'params rejected':
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def set_hardware_version(self, Mode):
        print("\nSending command to do Set Hardware version", Mode)
        for i in range(self.Len):
            try:
                Mode = self.network_api.set_hw_version(Address(self.METER_ADDRESS), Mode)
                print("Set HW Version:",Mode)
                if Mode == 'ok' or Mode == 'Okay':
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)
    def get_hardware_version(self):
        print("\nSending command to do Verify Hardware version")
        for i in range(self.Len):
            try:
                hw_version = self.network_api.get_hw_version(Address(self.METER_ADDRESS))
                print("get HW Version:",hw_version)
                if hw_version == 5 :
                    return self.return_dictionary_value(i,self.Pass)

                else:
                    return self.return_dictionary_value(i,self.Fail)
                
            except:    
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)

    def Enable_Print(self):
        self.network_api.enable_print_rxtx(Address(self.METER_ADDRESS))         

    def set_mqtt_topics(self,topic,index_val):
        print("\nSending command to set mqtt topic: ",topic)
        for i in range(self.Len):
            try:
                Setnum = self.network_api.set_gprs_topic(Address(self.METER_ADDRESS),topic,index_val)
                print("set mqtt topic:",Setnum)
                if (Setnum == 'ok') or (Setnum == 'Okay'):
                    return self.return_dictionary_value(i,self.Pass)
                else:
                    return self.return_dictionary_value(i,self.Fail)

            except:
                if ((i+1)==self.Len):
                    return self.return_dictionary_value(i,self.Fail)       

    # def Get_dcu_gateway_val(self):
    #     print("\nSending command to Verify dcu gateway")
    #     return_dict = {}
    #     for i in range(self.Len):
    #         try:
    #             Setnum = self.network_api.get_dcu_gateway_mode(Address(self.METER_ADDRESS))
    #             print("Get_dcu_gateway_mode:",Setnum)
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
    #     print("\nSending command to Verify dcu protocol")
    #     return_dict = {}
    #     for i in range(self.Len):
    #         try:
    #             Setnum = self.network_api.get_dcu_protocol_mode(Address(self.METER_ADDRESS))
    #             print("Get_dcu_protocol_val:",Setnum)
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
    #             # print ("Set",Setnum)
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