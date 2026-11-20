from gp_node.network.network_api import NetworkAPI
from gp_node.utils.address import Address
import datetime
import time
import logging


class TestCase():
    def __init__(self,ser,portID, retries, serial_len):
        # Thread.__init__(self) 
        # self.portID = portID 
        # self.cfg = cfg
        self.network_api = NetworkAPI(ser, portID, "irda")
        self.Len = retries
        self.nic_pcb_len = serial_len
        self.dcu_time = ""
        self.live_version_V = 0
        self.Pass = 'Pass'
        self.Fail = 'Fail'
        self.METER_ADDRESS = "255.255.255.255"

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

    def Get_pcb_serial_num(self, com_port):
        logging.debug(f"Sending command to do Get PCB serial number for com: {com_port}")
        for i in range(self.Len):
            try:
                pcb_serial_no = self.network_api.get_pcb_serial_no(Address(self.METER_ADDRESS))
                pcb_serial_no1 = pcb_serial_no.split("\0")[0]
                logging.debug(f"PCB serial number for com {com_port}: {pcb_serial_no1}")
                if str(pcb_serial_no1)!='':
                    return pcb_serial_no1
            except Exception as e:
                logging.error(f"Error in get pcb serial number for com {com_port}: {str(e)}")
                return None

    def check_port(self, com_port):
        logging.debug(f"Sending command to check com port status for com: {com_port}")
        for i in range(2):
            try:
                liveversion = self.network_api.get_live_version(Address(self.METER_ADDRESS))
                logging.debug(f"Live version for com {com_port}: {liveversion}")
                self.live_version_V = liveversion
                if str(liveversion)!='':
                    return liveversion
                
            except Exception as e:
                logging.error(f"Error in check port for com {com_port}: {str(e)}")
                if ((i+1)==2):
                    return "Fail"
    
    def Verify_Serial_number(self, com_port):
        logging.debug(f"Verify serial number for com: {com_port}")
        for i in range(self.Len):
            try:
                SERIAL_NUMBER = self.network_api.get_meter_serial_no(Address(self.METER_ADDRESS))
                SERIAL_NUMBER_V = SERIAL_NUMBER.split('UID 1')
                SERIAL_NUMBER_V2 = SERIAL_NUMBER_V[0].split(':')
                SerialNumber = SERIAL_NUMBER_V2[1].split(' ')[1]
                logging.debug(f"Serial number: {SerialNumber}, for com: {com_port}")
                if  SerialNumber != '98765432':
                    return {'status': 'pass', 'sr_number': SerialNumber }
                else:
                    return {'status': 'fail', 'sr_number': SerialNumber }
            except Exception as e:
                logging.error(f"Error in verify serial number in testcaseverf func: {str(e)}, for com: {com_port}")    
                if ((i+1)==self.Len):
                    return {'status': 'fail', 'sr_number': None }

    def Verify_Serial_number2(self, com_port):
        logging.debug(f"Sending command to do verify Serial number: {com_port}")
        for i in range(self.Len):
            try:
                SERIAL_NUMBER = self.network_api.get_meter_serial_no(Address(self.METER_ADDRESS))
                SERIAL_NUMBER_V = SERIAL_NUMBER.split('UID 1')
                SERIAL_NUMBER_V2 = SERIAL_NUMBER_V[0].split(':')
                SerialNumber = SERIAL_NUMBER_V2[1].split(' ')[1]
                logging.debug(f"Serial number: {SerialNumber}, for com: {com_port}")
                if  SerialNumber != '98765432':
                    return {'status': 'pass', 'sr_number': SerialNumber }
                else:
                    return {'status': 'fail', 'sr_number': SerialNumber }
            except Exception as e:
                logging.error(f"Error in testcaseverf func in verify serial number2: {str(e)}, for com: {com_port}")    
                if ((i+1)==self.Len):
                    return {'status': 'fail', 'sr_number': None }

    def get_live_version_val(self, com_port):
        logging.debug(f"Sending command to get live version for com: {com_port}")
        for i in range(2):
            try:
                liveversion = self.network_api.get_live_version(Address(self.METER_ADDRESS))
                logging.debug(f"live_version: {liveversion}, for com: {com_port}")
                if str(liveversion)!='':
                    return liveversion
                
            except Exception as e:
                logging.error(f"Error in get live version in testcaseverif func: {str(e)}, for com: {com_port}")
                if ((i+1)==2):
                        return "Fail"

    def Nic_PCB_No(self, com_port):
        logging.debug(f"Sending command to do verify Nic PCB number, for com: {com_port}")
        for i in range(self.Len):
            try:
                Nic_PCB_NUMBER = str(self.network_api.get_nic_pcb_serial_no(Address(self.METER_ADDRESS)))
                logging.debug(f"get_Nic_Pcb_no: {Nic_PCB_NUMBER[0:self.nic_pcb_len]}, for com: {com_port}")
                if Nic_PCB_NUMBER[0:self.nic_pcb_len]:
                    return {'status': 'pass', 'nic_pcb_number': Nic_PCB_NUMBER[0:self.nic_pcb_len] }
                else:
                    return {'status': 'fail', 'nic_pcb_number': Nic_PCB_NUMBER[0:self.nic_pcb_len] }
            except Exception as e:
                logging.error(f"Error in testcaseverf func in get nic pcb number: {str(e)}, for com: {com_port}")    
                if ((i+1)==self.Len):
                    return {'status': 'fail', 'nic_pcb_number': None }

    def add_leading_zeros(self,hex_value, desired_length):
        hex_value = hex_value.lstrip('0x')
        hex_value = hex_value.lower()
        return "{:0>{width}}".format(hex_value, width=desired_length)

    def make_address(self, SERIAL_NUM, com_port):
        hex_value = hex(SERIAL_NUM)
        desired_length=8  # Convert hex string to integer
        byte_value=self.add_leading_zeros(hex_value, desired_length)
        
        Address_new=str(int(byte_value[0]+byte_value[1],16))+'.'+str(int(byte_value[2]+byte_value[3],16))+'.'+str(int(byte_value[4]+byte_value[5],16))+'.'+str(int(byte_value[6]+byte_value[7],16))
        logging.debug(f"new Address: {Address_new} for com: {com_port}")
        return Address_new

    def get_Meter_address(self, com_port):
        logging.debug(f"Sending command to get meter address for com: {com_port}")
        for i in range(self.Len):
            try:
                MtrAddr = str(self.network_api.get_address(Address(self.METER_ADDRESS)))
                logging.debug(f"get Meter address: {MtrAddr}, for com: {com_port}")
                if MtrAddr:
                    return {'status': 'pass', 'mtr_address': MtrAddr }
                else:
                    logging.debug("did not get meter address")
                    return {'status': 'fail', 'mtr_address': MtrAddr }
            except Exception as e:
                logging.error(f"Error in testcaseverif func in get meter address: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {'status': 'fail', 'mtr_address': None }

    def get_Meter_address2(self,serialnum_mct, com_port):
        logging.debug(f"Sending command to get meter address2 for com: {com_port}")
        for i in range(self.Len):
            try:
                MtrAddr = self.network_api.get_address(Address(self.METER_ADDRESS))
                cal_address = self.make_address(serialnum_mct, com_port)
                logging.debug(f"get Meter address: {MtrAddr}, calculated address: {cal_address}, for com: {com_port}")
                
                if str(MtrAddr) == cal_address:
                    return {'status': 'pass', 'mtr_address': cal_address }
                else:
                    return {'status': 'fail', 'mtr_address': cal_address }
                
            except Exception as e:
                logging.error(f"Error in testcaseverif func in get meter address2: {str(e)}, for com: {com_port}")    
                if ((i+1)==self.Len):
                    return {'status': 'fail', 'mtr_address': None}

    def get_internal_version_val(self, com_port):
        logging.debug(f"Sending command to get internal version for com: {com_port}")
        for i in range(self.Len):
            try:
                int_version = self.network_api.get_int_version(Address(self.METER_ADDRESS))
                logging.debug(f"INTERNAL_VERSION: {int_version} for com: {com_port}")
                if(int_version):
                    return {'status': 'pass', 'int_version': str(int_version)}
                else:
                    return {'status': 'fail', 'int_version': str(int_version)}
            except Exception as e:
                logging.error(f"Error in testcaseverif func in get internal version: {str(e)}, for com: {com_port}")    
                if ((i+1)==self.Len):
                    return {'status': 'fail', 'int_version': None}

    def Set_time_val(self, com_port):
        logging.debug(f"Sending command to set ip time for com: {com_port}")
        for i in range(self.Len):
            try:
                SetTime_status = self.network_api.set_ip_time(Address(self.METER_ADDRESS),"now")
                logging.debug(f"Set_meter_Time: {SetTime_status}, for com: {com_port}")
                if SetTime_status == 'ok':
                    return {"status": 'pass', "Retries": i+1, "Set_time": "now"}
                else:
                    return {"status": 'fail', "Retries": i+1, "Set_time": "now"}
            except Exception as e:
                logging.error(f"Error in testcaseverif func in set time: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1, "Set_time": None}

    def Verify_time_val(self, com_port):
        logging.debug(f"Sending command to verify time for com: {com_port}")
        return_dict = {}
        for i in range(self.Len):
            try:
                GetTime = self.network_api.get_time(Address(self.METER_ADDRESS))
                logging.debug(f"Get_Time: {GetTime}, for com: {com_port}")
                timeDiff = (datetime.datetime.now() - GetTime).total_seconds()
                logging.debug(f"meter time Diff: {timeDiff}, for com: {com_port}")
                self.dcu_time = GetTime
                if timeDiff >= -20 and timeDiff < 200  :
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}
                    
            except Exception as e:
                logging.debug(f"Error in testcaseverf func in verify time val: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def Calibration_unLock(self, com_port):
        logging.debug(f"Sending command to do Calibration_unLock for com: {com_port}")
        for i in range(self.Len):
            try:
                arg_val = "0x600,2,bc 5a"
                Calib = self.network_api.eeprom_write(Address(self.METER_ADDRESS),arg_val)
                arg_val2 = "0x600,2,b0 5a"
                time.sleep(0.5)
                Calib2 = self.network_api.eeprom_write(Address(self.METER_ADDRESS),arg_val2)
                logging.debug(f"Calib Unlock:{Calib},{Calib2} for com: {com_port}")
                if Calib.lower() == 'ok' and Calib2.lower() == 'ok':
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}
            except Exception as e:
                logging.error(f"Error in testcaseverf func in calibration unlock: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def Clear_Energy_Value(self, com_port):
        logging.debug(f"Sending command to Clear Energy for com: {com_port}")
        for i in range(self.Len):
            try:
                ClearEnergy = self.network_api.tod_enable(Address(self.METER_ADDRESS))
                logging.debug(f"Clear Energy:{ClearEnergy} for com: {com_port}")
                if ClearEnergy == 'ok':
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}
                
            except Exception as e:
                logging.error(f"Error in testcaseverf func in clear energy value: {str(e)}, for com: {com_port}")    
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def Set_payment_mode(self, com_port, payment_mode = 1):
        logging.debug(f"Sending command to Set payment mode: {payment_mode}, for com: {com_port}")
        for i in range(self.Len):
            try:
                set_pytment_res = self.network_api.set_payment_mode(Address(self.METER_ADDRESS),str(payment_mode))
                logging.debug(f"Set_payment_mode: {payment_mode}, for com:{com_port}")
                if (set_pytment_res == 'ok') or (set_pytment_res == 'Okay') or (set_pytment_res == "params rejected"):
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}
            except Exception as e:
                logging.error(f"Error in testcaseverf func in set payment mode: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def get_hardware_version(self, com_port):
        logging.debug(f"Sending command to do Verify Hardware version for com: {com_port}")
        for i in range(self.Len):
            try:
                hw_version = self.network_api.get_hw_version(Address(self.METER_ADDRESS))
                logging.debug(f"get HW Version: {hw_version}, for com: {com_port}")
                if hw_version == 5 :
                    return {"status": 'pass', "Retries": i+1, "hw_version": 5}
                else:
                    return {"status": 'fail', "Retries": i+1, "hw_version": hw_version}
            except Exception as e:
                logging.error(f"Error in testcaseverf func in get hardware version: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1, "hw_version": "None"}

    def dlms_Activation_check_value(self, com_port, dlms_type = 'old_dlms'):
        logging.debug(f"Sending command to check dlms activation for com: {com_port}")
        for i in range(self.Len):
            try:
                dlms_act = self.network_api.check_dlms_activation(Address(self.METER_ADDRESS), dlms_type)
                if dlms_act == 0:
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}
            except Exception as e:
                logging.error(f"Error in testcaseverf func in DLMS activation check: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def hr_energy_register(self, com_port):
        logging.debug(f"Sending command to check HR Energy Register for com: {com_port}")
        for i in range(self.Len):
            try:
                hr_energy_bucket = self.network_api.get_nxp_ene_data(Address(self.METER_ADDRESS),1)
                Act_hr_energy = hr_energy_bucket.return_params["activeHr_energy_imp"]
                logging.debug(f"Active HR Energy : {Act_hr_energy} Kwh, for com: {com_port}")
                if Act_hr_energy is not None:
                    return {"status": 'pass', "Retries": i+1, "energy": float(Act_hr_energy)}
                else:
                    return {"status": 'fail', "Retries": i+1, "energy": None}
            except Exception as e:
                logging.error(f"Error in testcaseverf func in hr energy register activation check: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1, "energy": None}

    def Factory_reset_val(self, com_port):
        logging.debug(f"Sending command to do factory reset for com: {com_port}")
        for i in range(self.Len):
            try:
                FactoryInit = self.network_api.factory_init_1(Address(self.METER_ADDRESS))
                logging.debug(f"FactoryInit: {FactoryInit}, for com: {com_port}")
                if FactoryInit == 'ok':
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}
            except Exception as e:
                logging.error(f"Error in testcaseverf func in factory reset check: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def check_event_list(self, events):
        if (events == 0):
            return "pass"
        else:
            return "fail"

    def check_num_events(self, com_port):
        logging.debug(f"Sending command to check num events for com: {com_port}")
        return_list1 = []
        return_list = []
        for i in range(self.Len):
         try:
             Check_Num_Events=self.network_api.get_num_event_record(Address(self.METER_ADDRESS))
             logging.debug(f"Check_Num_Events: {Check_Num_Events}, for com: {com_port}")
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
             if "fail" in return_list1:
                return {"status": 'fail', "Retries": i+1}
             else:
                return {"status": 'pass', "Retries": i+1}
         except Exception as e:
                logging.error(f"Error in testcaseverf func in check num events check: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def get_apparent_led_status(self, com_port):
        logging.debug(f"\nSending command to get Apparent Led Status for com: {com_port}")
        for i in range(self.Len):
            try:
                app_led = self.network_api.get_apprent_led(Address(self.METER_ADDRESS))
                logging.info(f"\nApparent Led status for com {com_port}: {app_led}")
                if(str(app_led) == '0xAA'):
                    return {"status":"pass", "value": str(app_led)}
                else:
                    return {"status":"fail", "value": str(app_led)}
                
            except Exception as e:
                logging.error(f"Error in testcasefunc in Get Apparent Led Status: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status":"fail", "value": None}

    def _clean(self, val):
        """Remove NUL bytes / quotes / surrounding whitespace from a meter string field."""
        if val is None:
            return None
        return str(val).replace('\x00', '').replace('"', '').strip()

    def get_meter_sim_and_sim_number(self, com_port):
        logging.debug(f"Sending command to verify sim number for com: {com_port}")
        return_list = []
        for i in range(self.Len):
            try:
                return_list = []
                dcuParams = self.network_api.get_gprs_profile_by_index(Address(self.METER_ADDRESS), 0, isReturn=True)
                logging.debug(f"Get sim details result: {dcuParams}, for com: {com_port}")
                if (dcuParams.get("Active_Sim") == 1) or (dcuParams.get("Active_Sim") == 2):
                    return_list.append(dcuParams["Active_Sim"])

                    # ---- SIM1 ICCID ----
                    sim_num1 = self._clean(dcuParams.get("SIM1_ICCID"))
                    return_list.append(sim_num1 if sim_num1 else 0)

                    # ---- SIM1 APN ----
                    apn1_raw = dcuParams.get("SIM1_APN")
                    if apn1_raw:
                        apn1_raw = self._clean(str(apn1_raw))
                        apn_number1 = apn1_raw.replace('"','') if '"' in apn1_raw else apn1_raw
                        return_list.append(apn_number1)
                    else:
                        return_list.append(0)

                    imei = self._clean(str(dcuParams["IMEI"]))
                    return_list.append(imei)
                    return_list.append(dcuParams["Signal_Strength"])

                    # ---- SIM2 ICCID ----
                    sim_num2 = self._clean(dcuParams.get("SIM2_ICCID"))
                    return_list.append(sim_num2 if sim_num2 else 0)

                    # ---- SIM2 APN ----
                    apn2_raw = dcuParams.get("SIM2_APN")
                    if apn2_raw:
                        apn2_raw = self._clean(str(apn2_raw))
                        apn_number2 = apn2_raw.replace('"','') if '"' in apn2_raw else apn2_raw
                        return_list.append(apn_number2)
                    else:
                        return_list.append(0)

                    logging.debug(f"Sim result: {return_list}, for com: {com_port}")
                    signal = int(return_list[4])
                    active_sim = int(return_list[0])
                    return {'Result': 'pass', 'sim_result_value': return_list}
                    # if (10 <= signal) and (signal != 99) and (signal != 255) and (active_sim in (1, 2)):
                    #     return {'Result': 'pass', 'sim_result_value': return_list}
                    # else:
                    #     return {'Result': 'fail', 'sim_result_value': return_list}
                else:
                    return_list = [
                        dcuParams.get("Active_Sim", 0),
                        dcuParams.get("SIM1_ICCID", 0),
                        str(dcuParams.get("SIM1_APN", "None")),
                        str(dcuParams.get("IMEI", "None")),
                        dcuParams.get("Signal_Strength", 0),
                        dcuParams.get("SIM2_ICCID", 0),
                        str(dcuParams.get("SIM2_APN", "None")),
                    ]
                    return {'Result': 'fail', 'sim_result_value': return_list}
            except Exception as e:
                logging.error(f"Error in testcaseveriffunc in get sim details: {str(e)}, for com: {com_port}")
                print(f"Error in testcaseveriffunc in get sim details: {str(e)}, for com: {com_port}")
                if (i + 1) == self.Len:
                    return_list = ['0', '0', 'None', 'None', '0', '0', 'None']
                    return {'Result': 'fail', 'sim_result_value': return_list}

    def set_sim_toggle(self, com_port):
        print("\nSending command to do sim toggle")
        logging.debug(f"Sending command to toggle sim for com: {com_port}")
        for i in range(self.Len):
            try:
                simStatus = self.network_api.set_gprs_sim_toggle(Address(self.METER_ADDRESS))
                print("After Toggle Sim No : ",simStatus)
                if (int(simStatus)== 1) or (int(simStatus)== 2):
                    return "Pass"
                else:
                    return "Fail"
                
            except Exception as e:
                logging.error(f"Error in testcaseveriffunc in sim toggle : {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return "Fail"

    def get_3p_calib_coffi(self, com_port, calib_type = 'single_point'):
        logging.debug(f"Sending command to get 3p calib cofficients for com: {com_port}, calib_type: {calib_type}")
        for i in range(self.Len):
            try:
                calib_coffi=self.network_api.get_3p_calib_cofficient(Address(self.METER_ADDRESS),calib_type)
                logging.debug(f"fetched 3p calib cofficient: {calib_coffi}, for com: {com_port}")
                if calib_coffi:
                    return calib_coffi
                else:
                    return 'Fail'
            except Exception as e:
                logging.error(f"Error in testcasefunc in get 3p calib cofficient: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return 'Fail'

    def start_phase_calib(self, com_port):
        logging.debug(f"Sending command to start the phase calibration for com: {com_port}")
        for i in range(self.Len):
            try:
                calib = self.network_api.calib_3p_phase_start(Address(self.METER_ADDRESS))
                logging.debug(f"Result of phase calibration: {calib}, for com: {com_port}")
                if str(calib).lower() == 'string_calib_started':
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}
            except Exception as e:
                logging.error(f"Error in phase calibration stating: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def start_nuetral_calib(self, com_port):
        logging.debug(f"Sending command to start the neutral calibration for com: {com_port}")
        for i in range(self.Len):
            try:
                calib = self.network_api.calib_3p_neu_start(Address(self.METER_ADDRESS))
                logging.debug(f"Result of neutral calibration: {calib}, for com: {com_port}")
                if str(calib).lower() == 'string_calib_started':
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}
            except Exception as e:
                logging.error(f"Error in neutral calibration stating: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def set_gprs_host(self,host,port, com_port):
        logging.debug(f"Sending command to set GPRS Host: {host}, Port: {port}, for com: {com_port}")
        for i in range(self.Len):
            try:
                line = f"{host},{port}"
                Sethost = self.network_api.set_gprs_broker(Address(self.METER_ADDRESS),line)
                logging.debug(f"set GPRS Host: {Sethost}, for com: {com_port}")
                if (Sethost == 'ok') or (Sethost == 'Okay'):
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}

            except Exception as e:
                logging.error(f"Error in testcaseverffunc function in set gprs host: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def set_gprs_cred(self,user,password, com_port):
        logging.debug(f"Sending command to set GPRS Credentials, User: {user}, Password: {password}, for com: {com_port}")
        for i in range(self.Len):
            try:
                line = f"{user},{password}"
                Setcred = self.network_api.set_gprs_credentials(Address(self.METER_ADDRESS),line)
                logging.debug(f"set GPRS Credentials: {Setcred}, for com: {com_port}")
                if (Setcred == 'ok') or (Setcred == 'Okay'):
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}

            except Exception as e:
                logging.error(f"Error in testcaseverffunc function in set gprs credentials: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def verify_Meter_gprs_broker(self, input_host, input_port, com_port): 
        logging.debug(f"Sending command to Get GPRS Host for com: {com_port}")
        for i in range(self.Len):
            try:
                host, port = self.network_api.get_gprs_broker(Address(self.METER_ADDRESS))
                logging.debug(f"Get GPRS Host: {host}, Port: {port}")
                if host != None and port != None:
                    if (str(host) == str(input_host)) and (str(port) == str(input_port)):
                        return {"status": 'pass', "Retries": i+1}
                    else:
                        return {"status": 'fail', "Retries": i+1}

                else:
                    return {"status": 'fail', "Retries": i+1}    
                
            except Exception as e:
                logging.error(f"Error in testcaseverffunc function in verify METER GPRS broker: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}

    def Verify_Meter_gprs_credentials(self, input_user, intput_password, com_port   ): 
        logging.debug(f"Sending command to Get GPRS Credentials, for com: {com_port}")
        for i in range(self.Len):
            try:
                user, password = self.network_api.get_gprs_credentials(Address(self.METER_ADDRESS))
                logging.debug(f"Get GPRS credentials: {user}, {password}")
                if user != None and password != None:
                    if (str(user).strip() == str(input_user).strip()) and (str(password).strip() == str(intput_password).strip()):
                        return {"status": 'pass', "Retries": i+1}
                    else:
                        return {"status": 'fail', "Retries": i+1}

                else:
                    return {"status": 'fail', "Retries": i+1}    
                
            except Exception as e:
                logging.error(f"Error in testcaseverffunc function in verify METER GPRS credentials: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}


    def meter_reset(self, com_port, interval = 30):
        logging.debug(f"Sending command to reset meter with interval: {interval} seconds, for com: {com_port}")
        for i in range(self.Len):
            try:
                reset_status = self.network_api.reset(Address(self.METER_ADDRESS),interval)
                logging.debug(f"Meter reset status: {reset_status}, for com: {com_port}")
                if (reset_status == 'ok') or (reset_status == 'Okay'):
                    return {"status": 'pass', "Retries": i+1}
                else:
                    return {"status": 'fail', "Retries": i+1}

            except Exception as e:
                logging.error(f"Error in testcaseverffunc function in meter reset: {str(e)}, for com: {com_port}")
                if ((i+1)==self.Len):
                    return {"status": 'fail', "Retries": i+1}
