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
import threading
from threading import Thread 
import time
import socket
import paho.mqtt.client as mqtt
import datetime
import signal
import sys
import os
from config import config
from Test_cases_verificationClass import TestCasePCTMCT

# import #easygui


START_ADDRESS = 0x0100
METER_ADDRESS = "255.255.255.255" ##"6.0.7.40"
DCU_NUMBER_Ver = 0
toolName = 'PCT'
show_msg = 'NA'


class CasesThread(Thread):
    def __init__(self,ser,portID): 
        Thread.__init__(self) 
        self.portID = portID 
        self.ser = ser
        # self.dcu_number = dcu_number

    def GetResultMsg(self):
        global toolName
        global show_msg
        Return_list = []
        Return_list.append(show_msg)
        Return_list.append(toolName)
        return Return_list
        

    def run(self):
    
    #     network_api = NetworkAPI(self.ser, self.portID, "irda")
        global toolName
        global show_msg
        starttime = datetime.datetime.now()
        cfg = config()
        cfg.verify_config_json()
        cases = TestCasePCTMCT(self.ser,self.portID,cfg)

        serial_num = 0 # Initialization of meter serial number 
        address = 0 # Initialization of 
        is_excel_file_present = True
        meter_type = "Ulka_3PH"
        TOOL_TYPE = cfg.TOOL_TYPE
        print "TOOL_TYPE",TOOL_TYPE
        #Meter type selection done---------------------------------------------
        bookName = meter_type+"_"+TOOL_TYPE+"_LOG.xlsx"
        fileName = TOOL_TYPE+"_DATA_LOG"
        toolName = str(meter_type)
        toolName += str(TOOL_TYPE)
        toolName += "  || GRAMPOWER ||"
        Toolver = "Garud RF and MQTT RV5.8"
        cfg.is_excel_present()

        mac = cfg.get_system_mac_address()    
        for k in range(1):
            for l in range(1):
                starttime = datetime.datetime.now()
                os.system('cls' if os.name == 'nt' else 'clear')
                displayDashboard(TOOL_TYPE,Toolver)
                displayList = "NONE"
                print "\nSystem setup completed\n"
                result_list = []
                MeterInfo = []
                TOPIC_TEST = []
                case_for_RF = "\n"
                message = []
                serial_num = 'NA'
                address = 'NA'
                arg_val = 'NA'
            
                if(("RTI" == TOOL_TYPE) or ("RTT" == TOOL_TYPE)):
                    serial_num = cfg.enterSrNum(toolName)
                    address = cfg.getAddress(toolName,serial_num)
                    if address == False:
                        show_msg = "Meter Serial Number and Address not present in excel"
                        break
                    cases.set_unicast_address(address)
                    MeterInfo.append(serial_num)
                    addDefaultRTTLog(cfg,bookName,fileName)
                    RTT_Fail_list = ["Fail in Verify time","Fail in Verify address"]
                    # cases.Enable_Print()
                    result_list.append(cases.Verify_time_val()) 
                    time.sleep(1)
                    # print "result_list",result_list 
                    if (result_list[0]["Result"] == "Fail") and (result_list[0]["Retries"] == cfg.RETRIES):
                        if (cfg.IS_RF_WORKING == False):
                            show_msg = 'GPRS Not Responding'
                        else:
                            show_msg = 'RF Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Verify_Meter_address(str(address)))
                    time.sleep(1)
                    if (result_list[1]["Result"] == "Fail") and (result_list[1]["Retries"] == cfg.RETRIES):
                        if (cfg.IS_RF_WORKING == False):
                            show_msg = 'GPRS Not Responding'
                        else:
                            show_msg = 'RF Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    MeterInfo.append(str(address))
                    if (cfg.IS_RF_WORKING == False):
                        current_sim_and_number = cases.get_meter_sim_and_sim_number()
                        for val in range(0,len(current_sim_and_number)):
                            MeterInfo.append(current_sim_and_number[val])

                    time.sleep(1)
                    cases.get_live_version_val()
                    time.sleep(1)
                    version_and_time = cases.get_time_and_version_val()    

                elif(("MRI" == TOOL_TYPE) or ("MCT" == TOOL_TYPE)):
                    serial_num = cfg.enterSrNum(toolName)
                    address = cfg.getAddress(toolName,serial_num)
                    print "Check Address ",address,type(address)
                    if address == False:
                        show_msg = "Meter Serial Number and Address not present in excel"
                        break
                    MeterInfo.append(serial_num)
                    addDefaultMriLog(cfg,bookName,fileName)
                    MCT_Fail_list = ["Fail in Calib Unlock","Fail in Verify Calib Status","Fail in Verify time","Fail in Verify Set meter serial number","Fail in Clear Energy","Fail in Verify Energy","Fail in Set address","Fail in Verify address",\
                                     "Fail in Factory reset","Fail in Verify current","Fail in Verify relay state","Fail in Verify Serial number","Fail in Verify calibration status"]
                    result_list.append(cases.Calibration_unLock())
                    time.sleep(1)
                    if (result_list[0]["Result"] == "Fail") and (result_list[0]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Calibration_Status(IsUnlock = True))
                    time.sleep(1)
                    if (result_list[1]["Result"] == "Fail") and (result_list[1]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Verify_time_val()) 
                    time.sleep(1)
                    if (result_list[2]["Result"] == "Fail") and (result_list[2]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Set_Meter_serial_number(int(serial_num)))
                    time.sleep(1)
                    if (result_list[3]["Result"] == "Fail") and (result_list[3]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Clear_Energy_Value())  
                    time.sleep(1)
                    if (result_list[4]["Result"] == "Fail") and (result_list[4]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Verify_Energy_value())
                    time.sleep(1)
                    if (result_list[5]["Result"] == "Fail") and (result_list[5]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Set_Meter_address(str(address)))
                    time.sleep(1)
                    if (result_list[6]["Result"] == "Fail") and (result_list[6]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Verify_Meter_address(str(address)))
                    time.sleep(1)
                    if (result_list[7]["Result"] == "Fail") and (result_list[7]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Factory_reset_val())
                    if (result_list[8]["Result"] == "Fail") and (result_list[8]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(9)
                    result_list.append(cases.Verify_Current(.50))
                    if (result_list[9]["Result"] == "Fail") and (result_list[9]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    result_list.append(cases.Verify_Relay_State())
                    if (result_list[10]["Result"] == "Fail") and (result_list[10]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    result_list.append(cases.Verify_Serial_number(str(serial_num)))
                    if (result_list[11]["Result"] == "Fail") and (result_list[11]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    result_list.append(cases.Calibration_Status(IsUnlock = False))
                    if (result_list[12]["Result"] == "Fail") and (result_list[12]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    version_live = cases.get_live_version_val()
                    time.sleep(1)
                    version_and_time = cases.get_time_and_version_val()
                    MeterInfo.append(str(version_live)) 
                
                elif("PCT" == TOOL_TYPE):
                    Check_flag = True
                    while Check_flag:
                        arg_val = str(raw_input("Please eneter PCB serial number: "))
                        if len(arg_val) > 1:
                            Check_flag = False
                        else:
                            print "Please enter upto 32 character"
                    serial_num = arg_val
                    MeterInfo.append(serial_num) 
                    addDefaultPCTLog(cfg,bookName,fileName)
                    # MeterInfo.append(cfg.PROJECT)
                    # MeterInfo.append(cfg.RF_MODULE)
                    PCT_Fail_list = ["Fail In Set Time","Fail in Verify Time","Fail in Factory reset","Fail in relay off",\
                    "Fail in varify current with relay Off condition","Fail in relay ON","Fail in varify current with relay ON condition",\
                    "Fail in calibration unlock","Fail in Verify calibration status","Fail in Verify relay state",\
                    "Fail in set pcb serial number","Fail in Verify PCB number"]
                    result_list.append(cases.Set_time_val())
                    time.sleep(1)
                    if (result_list[0]["Result"] == "Fail") and (result_list[0]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    result_list.append(cases.Verify_time_val())
                    if (result_list[1]["Result"] == "Fail") and (result_list[1]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break 
                    time.sleep(1)
                    result_list.append(cases.Factory_reset_val())
                    if (result_list[2]["Result"] == "Fail") and (result_list[2]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(9)
                    result_list.append(cases.Meter_Relay_OFF())
                    if (result_list[3]["Result"] == "Fail") and (result_list[3]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(3)
                    result_list.append(cases.Verify_Current(.005,IsOff=True))
                    if (result_list[4]["Result"] == "Fail") and (result_list[4]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    result_list.append(cases.Meter_Relay_On())
                    if (result_list[5]["Result"] == "Fail") and (result_list[5]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(3)
                    result_list.append(cases.Verify_Current(0.50))
                    if (result_list[6]["Result"] == "Fail") and (result_list[6]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    result_list.append(cases.Calibration_unLock())
                    if (result_list[7]["Result"] == "Fail") and (result_list[7]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    result_list.append(cases.Calibration_Status(IsUnlock = True))
                    if (result_list[8]["Result"] == "Fail") and (result_list[8]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    result_list.append(cases.Verify_Relay_State())
                    if (result_list[9]["Result"] == "Fail") and (result_list[9]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)
                    # result_list.append(cases.Set_Meter_serial_number(int(serial_num)))
                    # time.sleep(1)
                    # result_list.append(cases.Verify_Serial_number(str(serial_num)))
                    # time.sleep(1)
                
                    result_list.append(cases.Set_Meter_PCB_serial_number(arg_val))
                    if (result_list[10]["Result"] == "Fail") and (result_list[10]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break  
                    time.sleep(1)
                    result_list.append(cases.Get_Meter_PCB_serial_number(str(arg_val)))
                    if (result_list[11]["Result"] == "Fail") and (result_list[11]["Retries"] == cfg.RETRIES):
                        show_msg = 'IR Not Responding'
                        #easygui.msgbox(show_msg,toolName)
                        break
                    time.sleep(1)  
                    cases.get_live_version_val()
                    time.sleep(1)
                    version_and_time = cases.get_time_and_version_val()
                    if cfg.RF_NETWORK_CHANNEL_SET == True:
                        PCT_Fail_list.extend("Fail in set network ")
                        PCT_Fail_list.extend("Fail in get network ")
                        PCT_Fail_list.extend("Fail in set channel ")
                        PCT_Fail_list.extend("Fail in get channel ")
                        result_list.append(cases.Set_network_val(cfg.NETWORK))
                        time.sleep(1)
                        result_list.append(cases.Get_network_val(cfg.NETWORK))
                        time.sleep(1)
                        result_list.append(cases.Set_channel_val(cfg.CHANNEL))
                        time.sleep(1)
                        result_list.append(cases.Get_channel_val(cfg.CHANNEL))

                    
                
                final_result = []
                ResultFinal = []
                FailResult = []
                for j in range(len(result_list)):
                    # print "final_response",result_list[j]
                    final_result.append(result_list[j]["Result"])
                    final_result.append(result_list[j]["Retries"])
                    if result_list[j]["Result"] == 'Fail':
                        ResultFinal.append('Fail')
                        if(("MRI" == TOOL_TYPE) or ("MCT" == TOOL_TYPE)):
                            FailResult.append(MCT_Fail_list[j])
                        elif("PCT" == TOOL_TYPE):
                            FailResult.append(PCT_Fail_list[j])
                        else:   
                            FailResult.append(RTT_Fail_list[j]) 

                if (len(ResultFinal) > 0):
                    message.append(ResultFinal[0])
                    message.append(FailResult)
                    MeterInfo.append(ResultFinal[0])
                    if (int(version_and_time[1]) == int(cfg.LIVE_VERSION)):
                        ResultFinal.append('Pass') 
                        final_result.append("Pass")
                        final_result.append("1")
                    else:
                        ResultFinal.append('Fail') 
                        FailResult.append("Live version mismatch")
                        final_result.append("Fail")
                        final_result.append("1")
    
                else:
                    if (int(version_and_time[1]) == int(cfg.LIVE_VERSION)):
                        ResultFinal.append('Pass') 
                        final_result.append("Pass")
                        final_result.append("1")
                        message.append(ResultFinal[0])
                    else:
                        ResultFinal.append('Fail') 
                        FailResult.append("Live version mismatch")
                        final_result.append("Fail")
                        final_result.append("1")
                        message.append(ResultFinal[0])
                        message.append(FailResult)
                        
                    MeterInfo.append(ResultFinal[0]) 
  


            
                # if (message[0]=="PASS:"):
                #     MeterInfo.append("PASS")
                # else: 
                #     MeterInfo.append("Failed")    
                cfg.add_log_xlsc(mac,MeterInfo,final_result,bookName,fileName)
            

            

                EndTime = datetime.datetime.now()
                print "\nStartTime:",starttime
                print "EndTime:",EndTime
                print "Diff : ", EndTime - starttime
                line ="\nStartTime:"+str(starttime)
                line1 ="EndTime:"+str(EndTime)
                line2="Diff:"+str(EndTime - starttime)
                if ("PCT" == TOOL_TYPE):
                    serial_num = "\nPCB_serial_num:"+str(serial_num)

                else:
                    serial_num = "\nSerial_num:"+str(serial_num)    
        
                dcu_time = "Meter time:"+str(version_and_time[0])
                dcu_LiveVersion = "Meter live version:"+str(version_and_time[1])
                message.append(line)
                message.append(line1)
                message.append(line2)
                message.append(serial_num)
                message.append(dcu_time)
                message.append(dcu_LiveVersion)
                if ((cfg.TOOL_TYPE == 'RTT') or (cfg.TOOL_TYPE == 'RTI') and cfg.IS_RF_WORKING == False):
                    try: 
                        SimNum = "SIM NUM: "+str(current_sim_and_number[0])
                        currentSim = "Current Sim: "+str(current_sim_and_number[1])
                    except:
                        SimNum = "SIM NUM: Not Found" 
                        currentSim = "Current Sim: Not Found"  
                show_msg = ''
                for i in range(0, len(message)):
                    show_msg += str(message[i])+'\n'
                try:
                    # print "Show msg",show_msg, toolName
                    # #easygui.msgbox(show_msg,toolName)
                    del cfg
                    # print "Return "
                except Exception as err:
                    print ("Error is ",str(err))
                
                return
            # if (cfg.TOOL_TYPE == 'RTT') or (cfg.TOOL_TYPE == 'RTI'):
            #     clecthread.exit()

        # os._exit(0)

    # case = test_case_procedures(cfg, ser)
    # case.load_no_load_test_case() 

def displayDashboard(toolType,Toolver):    
    print "****************************************************************"
    print "****************************************************************"
    print "\n"
    print str(toolType)+" "+str(Toolver)#METER CUSTOMISATION TOOL V - ", MCT_SOFTWARE_VERSION
    print "\n"
    print "****************************************************************"
    print "****************************************************************" 

def addDefaultRTTLog(cfg,bookName,fileName):
    if False == cfg.verify_log_xlsc(bookName,fileName):
        print "xlsx file for log not found. creating one to store test report"
        mac = "MAC_ADDR"
        if cfg.IS_RF_WORKING == False :
            MeterInfo = ['Index','SERIAL_NUM','Address','Current SIM NUMBER','Current SIM Slot','APN','OVER ALL RESULT'] 
        else:
            MeterInfo = ['Index','SERIAL_NUM','Address','OVER ALL RESULT'] 
        # = bytearray()
    
    
        # UID = {'UID1','UID2','UID3','UID4'}
        # result = []
        result = ["Verify time","Retry","Verify address","Retry","Live version match","retry"]#,"MTR_ADDRESS","NET_CHAN","LIVE_VER",\
        # "SET_TIME_ZONE","UI_DISPLAY_STATUS","LOAD TEST","FACTORY_RESET","RELAY_STATE","PUSHED_INDEX"]
        # print "UID = ",MeterInfo
        # print "Result = ",result
    
        cfg.add_log_xlsc(mac,MeterInfo,result,bookName,fileName)     

def addDefaultMriLog(cfg,bookName,fileName):
    if False == cfg.verify_log_xlsc(bookName,fileName):
        print "xlsx file for log not found. creating one to store test report"
        mac = "MAC_ADDR"
        MeterInfo = ['Index','PCB SERIAL_NUM','Live Version','OVER ALL RESULT'] 
        # = bytearray()
    
    
        # UID = {'UID1','UID2','UID3','UID4'}
        # result = []
        result = ["Verify time","Retry","Set meter serial number","Retry","Clear Energy","Retry","Verify Energy","Retry","Set address","Retry","Verify address","Retry",\
                  "Factory reset","Retry","Verify current","Retry","Verify relay state","Retry","Verify Serial number","Retry","Verify calibration status","Retry","Live version match","retry"]
        # "SET_TIME_ZONE","UI_DISPLAY_STATUS","LOAD TEST","FACTORY_RESET","RELAY_STATE","PUSHED_INDEX"]
        # print "UID = ",MeterInfo
        # print "Result = ",result
    
        cfg.add_log_xlsc(mac,MeterInfo,result,bookName,fileName)
         # if log file is not present or corrupted 
                                                # than create a new log file
        # cfg.add_index_of_pushed_data(1,bookName,fileName)
    # return "METER CUSTOMIZATION TOOL - (MCT) V - "  

def addDefaultPCTLog(cfg,bookName,fileName):
    if False == cfg.verify_log_xlsc(bookName,fileName):
        print "xlsx file for log not found. creating one to store test report"
        mac = "MAC_ADDR"
        MeterInfo = ['Index','SERIAL_NUM','OVER ALL RESULT'] 
        # = bytearray()
    
    
        # UID = {'UID1','UID2','UID3','UID4'}
        # result = []
        # if (RF_MODULEV == 'TM'):
        result = ["Set Time","Retry","Verify Time","Retry","Factory reset","Retry","Relay off","Retry",\
                "Varify current with relay Off condition","Retry","Relay ON","Retry","Varify current with relay ON condition","Retry",\
                "Calibration unlock","Retry","Verify calibration status","Retry","Verify relay state","Retry",\
                "set pcb serial number","Retry","Verify PCB number","Retry","Live version match","retry"]
        # else:
        #     result = ["Set dcu time","Retry","Verify DCU time","Retry","Set dcu Number","Retry","Verify dcu Serial number","Retry","Set DCU Topic","Retry","Verify DCU Collection Topic","Retry","Verify DCU Data Pushing Topic","Retry","Verify DCU Remote command Topic","Retry","Do DCU factory reset","Retry"]#,"MTR_ADDRESS","NET_CHAN","LIVE_VER",\
        # "SET_TIME_ZONE","UI_DISPLAY_STATUS","LOAD TEST","FACTORY_RESET","RELAY_STATE","PUSHED_INDEX"]
        # print "UID = ",MeterInfo
        # print "Result = ",result
    
        cfg.add_log_xlsc(mac,MeterInfo,result,bookName,fileName)    
     

        
        # signal.signal(signal.SIGINT, handler)


# if __name__ == "__main__":
#     run()
