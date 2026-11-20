import cmd
import inspect
import sys
import logging
import os
import os.path
import pprint
import colorama
import serial
import serial.tools.list_ports
import datetime
import getpass
import dateutil.parser
from colorama import Fore
from optparse import OptionParser
from gp_node.network.network_api import NetworkAPI, NetworkAPIError
from gp_node.utils.address import Address
from gp_node.network.protocols.packets._1p.daily_deduction_params import DailyDeductionParams
from gp_node.network.protocols.packets._1p.load_survey_params import LoadSurveyParams

from gp_node.network.protocols.packets._1pn.load_survey_params import LoadSurveyParamsN


from gp_node.network.protocols.packets._1p.tamper_log_packet import TamperLog
from gp_node.network.circular_log._1p.log_reader import LogReader

from gp_node.network.circular_log._1p.load_survey import LoadSurveyReaderN

from gp_node.network.circular_log._1p.log_reader1 import LogReaderN

from gp_node.network.circular_log._1p.block_load_profile import BlockLoadProfileReader
from gp_node.network.circular_log._1p.daily_load_profile import DailyLoadProfileReader
from gp_node.network.circular_log._1p.event_record import EventRecordReader
from gp_node.network.circular_log._1p.tamper_log_reader import TamperLogReader

from gp_node.network.circular_log.energy_cop.data_logger import DataLogReader
from gp_node.network.protocols.packets._1p.slab_packet import SlabConfigurationPacket
from gp_node.network.protocols.packets._1p.accounting_state_packet import AccountingStatePacket
from gp_node.network.protocols.packets._1p.fixed_deduction_packet import FixedDeductionPacket
from gp_node.network.protocols.packets._3p.load_survey_params_3p import LoadSurveyParams3P
from gp_node.network.protocols.packets._3p.metering_data_params_3p import MeteringDataParams3P
from gp_node.network.protocols.packets._3p.crc_bundle_3p import CrcDataPacket3P
from gp_node.network.protocols.packets._3p.slab_packet_3p import SlabConfigurationPacket3P
from gp_node.network.protocols.packets._3p.accounting_state_packet_3p import AccountingStatePacket3P
from gp_node.network.protocols.packets._3p.fixed_deduction_packet_3p import FixedDeductionPacket3P
from gp_node.network.protocols.packets._3p.bundle_3p import MeteringDataParamsBundle3P
from gp_node.network.protocols.packets._3p.sys_params_3p import SystemsCommands3P
import logging

class NodeShell(cmd.Cmd):
    """A shell to interact with the Node board"""

    network_api = None
    address = None

    # def postcmd(self, stop, line):
    # print line
    # print stop
    # if line == "exit":
    # return  True

    def precmd(self, line):
        # print line
        self.file_logger.info("------------------------------------")
        self.file_logger.info(line)
        return line

    def set_network_api(self, network_api):
        username = getpass.getuser()
        self.network_api = network_api
        self.logger = LogReader(network_api, 4, 42)
        self.loggern = LogReaderN(network_api, 4, 42)
        self.tamper_logger = TamperLogReader(network_api, 2, 14)
        self.block_load_profile = BlockLoadProfileReader(network_api, 160, 30)
        self.daily_load_profile = DailyLoadProfileReader(network_api, 70, 14)
        self.event_record = EventRecordReader(network_api, 3, 24)
        self.dlog = DataLogReader(network_api, 232, 36)
        self.load_surveyn = LoadSurveyReaderN(network_api, 232, 32)

        #----------------------------------------------------------------
        self.file_logger = logging.getLogger(__name__)
        self.file_logger.setLevel(logging.INFO)
        # create a file handler

        # self.handler = logging.FileHandler('/home/'+username+'/.grampower/gp_node/node-shell.log')
        self.handler = logging.FileHandler('node-shell.log')
        self.handler.setLevel(logging.INFO)

        # create a logging format
        self.formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        # add the handlers to the logger
        self.file_logger.addHandler(self.handler)

    def print_command(self, func, kwargs, to_print=True):
        units_present = True
        reply = None
        try:
            reply = func(self.address, **kwargs)
        except NetworkAPIError as err:
            print(err)
            self.file_logger.info(err)
            self.file_logger.info("----------End OF CMD----------------\n")
            return None
        except Exception as err:
            print("Unknown Error:{err}".format(err=err))
            self.file_logger.info("Unknown Error:{err}".format(err=err))
            self.file_logger.info("----------End OF CMD----------------\n")
            return None

        if to_print:
            try:
                cal_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("Cmd Time :{}".format(cal_time))
                print("{reply} {units}".
                      format(reply=reply,
                             units=func.units))
                self.file_logger.info("{reply} {units}".
                                      format(reply=reply,
                                             units=func.units))
            except AttributeError as err:
                if(func == self.network_api.three_ph_get_metering_data_bundle):
                    # print "---------------------"
                    #budle_dict = reply
                    bundl = MeteringDataParamsBundle3P()
                    # for item in budle_dict:
                    # print item,budle_dict[item]

                    budle_dict = bundl.get_packet_bundle_string(reply)
                    # print budle_dict
                    reply = budle_dict
                    # print "---------------------"
                print("{reply}".format(reply=reply))
                self.file_logger.info("{reply}".format(reply=reply))
        self.file_logger.info("----------End OF CMD----------------\n")
        return reply

    def emptyline(self):
        pass
    
    
    # Gurux Profile Generic commands
    def do_get_extended_registers(self, line):
        self.print_command(self.network_api.get_extended_registers,
                           kwargs={})
    def do_md_reset(self, line):
        self.print_command(self.network_api.md_reset,
                    kwargs={})
        
    def do_clear_irtc_corrupt_count(self, line):
        self.print_command(self.network_api.clear_irtc_corrupt_count,
                    kwargs={})
        
    def do_get_current_counts(self, line):
        self.print_command(self.network_api.get_current_counts,
                           kwargs={})
        
    def do_get_irtc_corrupt_count(self, line):
        self.print_command(self.network_api.get_irtc_corrupt_count,
                           kwargs={})
    
    # TAMPER RELATED Configuration by Rahul

    def do_get_tampers_threshold(self, line):
        self.print_command(self.network_api.get_tampers_threshold,
                           kwargs={})
     
    def do_set_tampers_threshold(self, line):
        try:
            args = line
        except:
            print ("needs argument")
        else:
            self.print_command(self.network_api.set_tampers_threshold,
                           kwargs={"args": args})
            
    def do_get_event_ptime(self, line):
        self.print_command(self.network_api.get_event_ptime,
                           kwargs={})
     
    def do_set_event_ptime(self, line):
        try:
            args = line
        except:
            print( "needs argument")
        else:
            self.print_command(self.network_api.set_event_ptime,
                           kwargs={"args": args})
           
    def do_test(self, line):
        self.print_command(self.network_api.test,
                           kwargs={})

    def do_dongle_dlms_to_tap(self, line):
        self.print_command(self.network_api.dongle_dlms_to_tap,
                           kwargs={})

    def do_meter_tap_to_dlms(self, line):
        self.print_command(self.network_api.meter_tap_to_dlms,
                           kwargs={})

    def do_meter_dlms_to_tap(self, line):
        self.print_command(self.network_api.meter_dlms_to_tap,
                           kwargs={})

    def do_get_credit_limit(self, line):
        self.print_command(self.network_api.get_credit_limit,
                           kwargs={})

    def do_get_master_credits(self, line):
        self.print_command(self.network_api.get_master_credits,
                           kwargs={})

    def do_get_network(self, line):
        self.print_command(self.network_api.get_network,
                           kwargs={})

    def do_get_channel(self, line):
        self.print_command(self.network_api.get_channel,
                           kwargs={})

    def do_rf_mem_read(self, line):
        data = self.print_command(self.network_api.rf_mem_read,
                                  kwargs={"line":line},
                                  to_print=True)
    def do_get_rf_module_version(self, line):
        data = self.print_command(self.network_api.get_rf_version,
                                  kwargs={},
                                  to_print=True) 

    def do_get_rf_power(self, line):
        self.print_command(self.network_api.get_rf_power,
                           kwargs={})

    # def do_get_current(self, line):
    #     self.print_command(self.network_api.get_current,
    #                         kwargs={})

    def do_get_phase_current(self, line):
        self.print_command(self.network_api.get_phase_current,
                           kwargs={})
       

    def do_get_neutral_current(self, line):
        self.print_command(self.network_api.get_neutral_current,
                           kwargs={})

    # def do_get_active_energy(self, line):
    #     self.print_command(self.network_api.get_active_energy,
    #                         kwargs={})

    # def do_get_reactive_energy(self, line):
    #     self.print_command(self.network_api.get_reactive_energy,
    #                         kwargs={})

    # def do_get_apparent_energy(self, line):
    #     self.print_command(self.network_api.get_apparent_energy,
    #                         kwargs={})

    def do_get_live_tampers(self, line):
        self.print_command(self.network_api.get_live_tampers,
                           kwargs={})

    def do_get_int_version(self, line):
        self.print_command(self.network_api.get_int_version,
                           kwargs={})

    def do_get_cumulative_tamper_count(self, line):
        self.print_command(self.network_api.get_cumulative_tamper_count,
                           kwargs={})

    # def do_get_voltage(self, line):
    #     self.print_command(self.network_api.get_voltage,
    #                         kwargs={})

    # def do_get_active_power(self, line):
    #     self.print_command(self.network_api.get_active_power,
    #                         kwargs={})

    # def do_get_frequency(self, line):
    #     self.print_command(self.network_api.get_frequency,
    #                         kwargs={})

    # def do_get_power_factor(self, line):
    #     self.print_command(self.network_api.get_power_factor,
    #                         kwargs={})

# newly added===========================================================================
    def do_get_net_account(self, line):
        self.print_command(self.network_api.get_net_account,
                           kwargs={})
# ====================================================================================== 
    def do_get_net_recharge(self, line):
        self.print_command(self.network_api.get_net_recharge,
                           kwargs={})

    def do_get_neg_recharge(self, line):
        self.print_command(self.network_api.get_neg_recharge,
                           kwargs={})

    def do_get_pos_recharge(self, line):
        self.print_command(self.network_api.get_pos_recharge,
                           kwargs={})

    def do_get_credits(self, line):
        self.print_command(self.network_api.get_credits,
                           kwargs={})

    def do_get_power_limit(self, line):
        self.print_command(self.network_api.get_power_limit,
                           kwargs={})

    def do_get_dg_power_limit(self, line):
        self.print_command(self.network_api.get_Dgpower_limit,
                           kwargs={})


    def do_get_time_left(self, line):
        self.print_command(self.network_api.get_time_left,
                            kwargs={})

    def do_get_energy_limit(self, line):
        self.print_command(self.network_api.get_energy_limit,
                           kwargs={})

    def do_get_price(self, line):
        self.print_command(self.network_api.get_price,
                           kwargs={})

    def do_get_address(self, line):
        self.print_command(self.network_api.get_address,
                           kwargs={})

    def do_get_tamper_record(self, line):
        self.print_command(self.network_api.get_tamper_record,
                           kwargs={"tamper_type": line})

    def do_get_dd_params(self, line):
        self.print_command(self.network_api.get_dd_params,
                           kwargs={})

    def do_get_accounting_state(self, line):
        self.print_command(self.network_api.get_accounting_state,
                           kwargs={})

    def do_get_slab_update_ts(self, line):
        self.print_command(self.network_api.get_slab_update_ts,
                           kwargs={})

    def do_get_block_load_profile_params(self, line):
        self.print_command(self.network_api.get_block_load_profile_params,
                           kwargs={})

    def do_get_hw_version(self, line):
        self.print_command(self.network_api.get_hw_version,
                           kwargs={})

    def do_get_health_status(self, line):
        self.print_command(self.network_api.get_health_status,
                           kwargs={})
    
    def do_get_self_diagnostic(self, line):
        self.print_command(self.network_api.get_self_diagnostic,
                           kwargs={})

    def do_get_live_version(self, line):
        self.print_command(self.network_api.get_live_version,
                           kwargs={})
        
    def do_get_int_version(self, line):
        self.print_command(self.network_api.get_int_version,
                           kwargs={})

    def do_get_ext_version(self, line):
        self.print_command(self.network_api.get_ext_version,
                           kwargs={})

    def do_get_newest_block_load_profile(self, line):
        self.print_command(self.network_api.get_newest_block_load_profile,
                           kwargs={})

    def do_get_oldest_block_load_profile(self, line):
        self.print_command(self.network_api.get_oldest_block_load_profile,
                           kwargs={})

    def do_get_newest_daily_load_profile(self, line):
        self.print_command(self.network_api.get_newest_daily_load_profile,
                           kwargs={})

    def do_get_oldest_daily_load_profile(self, line):
        self.print_command(self.network_api.get_oldest_daily_load_profile,
                           kwargs={})

    def do_get_block_load_profile_by_index(self, line):
        index = int(line)
        self.print_command(self.network_api.get_block_load_profile_by_index,
                           kwargs={"index": index})

    def do_get_block_load_profile_by_index1(self, line):
        index = int(line)
        self.print_command(self.network_api.get_block_load_profile_by_index1,
                           kwargs={"index": index})

    def do_get_daily_load_profile_by_index(self, line):
        index = int(line)
        self.print_command(self.network_api.get_daily_load_profile_by_index,
                           kwargs={"index": index})
        
    def do_get_daily_load_profile_by_datetime(self, line):
        self.print_command(self.network_api.get_daily_load_profile_by_datetime,
                           kwargs={"line": line})

    def do_get_block_load_profile_by_datetime(self, line):
        self.print_command(self.network_api.get_block_load_profile_by_datetime,
                           kwargs={"line": line})
        
    def do_get_num_block_load_profile(self, line):
        self.print_command(self.network_api.get_num_block_load_profile,
                           kwargs={})

    def do_get_num_instant_data_profile(self, line):
        self.print_command(self.network_api.get_num_instant_data_profile,
                           kwargs={})

    def do_get_num_daily_load_profile(self, line):
        self.print_command(self.network_api.get_num_daily_load_profile,
                           kwargs={})
        
    def do_get_num_block_load_profile_datetime(self, line):
        self.print_command(self.network_api.get_num_block_load_profile_datetime,
                           kwargs={"line": line})

    def do_get_num_daily_load_profile_datetime(self, line):
        self.print_command(self.network_api.get_num_daily_load_profile_datetime,
                           kwargs={"line": line})

    def do_get_newest_log(self, line):
        self.print_command(self.network_api.get_newest_log,
                           kwargs={})

    def do_get_oldest_log(self, line):
        self.print_command(self.network_api.get_oldest_log,
                           kwargs={})

    def do_get_num_logs(self, line):
        self.print_command(self.network_api.get_num_logs,
                           kwargs={})

    def do_get_time(self, line):
        self.print_command(self.network_api.get_time,
                           kwargs={})
        
    def do_get_factory_time(self, line):
        self.print_command(self.network_api.get_factory_time,
                           kwargs={})

    def do_get_timeformat(self, line):
        self.print_command(self.network_api.get_timeformat,
                           kwargs={"cal_time": line})

    def do_get_ref_time(self, line):
        self.print_command(self.network_api.get_ref_time,
                           kwargs={})

    def do_get_last_poweroff_time(self, line):
        self.print_command(self.network_api.get_last_poweroff_time,
                           kwargs={})

    def do_set_ref_time(self, line):
        self.print_command(self.network_api.set_ref_time,
                           kwargs={"cal_time": line})

    def do_set_last_poweroff_time(self, line):
        self.print_command(self.network_api.set_last_poweroff_time,
                           kwargs={"cal_time": line})

    def do_get_energy_consumed_today(self, line):
        self.print_command(self.network_api.get_energy_consumed_today,
                           kwargs={})

    def do_get_unlock_validity(self, line):
        self.print_command(self.network_api.get_unlock_validity,
                           kwargs={})

    def do_get_time_since_unlock(self, line):
        self.print_command(self.network_api.get_time_since_unlock,
                           kwargs={})

    def do_get_last_unlock_timestamp(self, line):
        self.print_command(self.network_api.get_last_unlock_timestamp,
                           kwargs={})

    def do_get_active_energy_offset(self, line):
        self.print_command(self.network_api.get_active_energy_offset,
                           kwargs={})

    def do_get_reactive_energy_offset(self, line):
        self.print_command(self.network_api.get_reactive_energy_offset,
                           kwargs={})

    def do_get_apparent_energy_offset(self, line):
        self.print_command(self.network_api.get_apparent_energy_offset,
                           kwargs={})

    def do_get_digital_input_status(self, line):
        self.print_command(self.network_api.get_digital_input_status,
                           kwargs={})

    # Fix
    def do_get_block_load_profile_interval(self, line):
        self.print_command(self.network_api.get_block_load_profile_interval,
                           kwargs={})

    def do_get_accurate_credits(self, line):
        self.print_command(self.network_api.get_accurate_credits,
                           kwargs={})

    def do_set_master_credits(self, line):
        self.print_command(self.network_api.set_master_credits,
                           kwargs={"amount": int(line)})


    def do_set_address(self, line):
        try:
            address = Address(line)
        except Exception as e:
            print ("Usage: do_set_address:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.set_address,
                           kwargs={"address": address})

    # def do_set_channel(self, line):
    #     channel = int(line)
    #     self.print_command(self.network_api.set_channel,
    #                        kwargs={"channel": channel})

    def do_set_channel(self, line):
        try:
            channel = int(line)
        except Exception as e:
            print ("Usage: do_set_channel:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.set_channel,
                           kwargs={"channel": channel})



    def do_set_rf_power(self, line):
        rf_power = int(line)
        self.print_command(self.network_api.set_rf_power,
                           kwargs={"rf_power": rf_power})

    # def do_set_network(self, line):
    #     network = int(line)
    #     self.print_command(self.network_api.set_network,
    #                        kwargs={"network": network})

    def do_set_network(self, line):
        try:
            network = int(line)
        except Exception as e:
            print ("Usage: do_set_network:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.set_network,
                           kwargs={"network": network})
        

    def do_set_rc_buffer_margin(self, line):
        margin = int(line)
        self.print_command(self.network_api.set_rc_buffer_margin,
                           kwargs={"margin": margin})

    def do_set_rc_timeout(self, line):
        rc_timeout = int(line)
        self.print_command(self.network_api.set_rc_timeout,
                           kwargs={"rc_timeout": rc_timeout})

    def do_set_power_limit(self, line):
        power_limit = int(line)
        self.print_command(self.network_api.set_power_limit,
                           kwargs={"power_limit": power_limit})

    def do_set_dg_power_limit(self, line):
        power_limit = int(line)
        self.print_command(self.network_api.set_Dgpower_limit,
                           kwargs={"power_limit": power_limit})

    def do_set_lockdown_period(self, line):
        period = int(line)
        self.print_command(self.network_api.set_lockdown_period,
                           kwargs={"period": period})

    def do_reset_lockdown_period(self, line):
        self.print_command(self.network_api.reset_lockdown_period,
                           kwargs={})

    def do_enable_power_limiter(self, line):
        self.print_command(self.network_api.enable_power_limiter,
                           kwargs={})

    def do_disable_power_limiter(self, line):
        self.print_command(self.network_api.disable_power_limiter,
                           kwargs={})

    def do_get_lockdown_period(self, line):
        self.print_command(self.network_api.get_lockdown_period,
                           kwargs={})

    def do_power_limit_status(self, line):
        self.print_command(self.network_api.power_limit_status,
                           kwargs={},to_print=False)

    def do_set_power_limit_on_time(self, line):
        period = int(line)
        self.print_command(self.network_api.set_power_limit_on_time,
                           {"period": period})   

    def do_set_power_limit_off_time(self, line):
        period = int(line)
        self.print_command(self.network_api.set_power_limit_off_time,
                           {"period": period})  

    def do_get_power_limit_on_time(self, line):
        self.print_command(self.network_api.get_power_limit_on_time,
                           kwargs={})  
    def do_get_power_limit_off_time(self, line):
        self.print_command(self.network_api.get_power_limit_off_time,
                           kwargs={}) 

    def do_set_manufaturing_year(self, line):
        year = int(line)
        self.print_command(self.network_api.set_manufaturing_year,
                           {"year": year})  

    def do_get_manufaturing_year(self, line):
        self.print_command(self.network_api.get_manufaturing_year,
                           kwargs={})   

    def do_set_nm_control_status(self, line):
        try:
            period = int(line)
        except Exception as e:
            print ("Usage: set_nm_control_status:1(enable)/0(disable)")
        else:    
            self.print_command(self.network_api.set_nm_control_status,
                           {"period": period})

    def do_get_nm_control_status(self, line):
        self.print_command(self.network_api.get_nm_control_status,
                           kwargs={}) 

    def do_set_debug_print(self, line):   
        self.print_command(self.network_api.set_debug_print,
                        {"period": line})

    def do_get_debug_print(self, line):
        self.print_command(self.network_api.get_debug_print,
                           kwargs={})
    def do_get_gprs_health_status(self, line):
        self.print_command(self.network_api.get_gprs_health_status,
                           kwargs={})

    def do_set_gprs_reset_retry_count(self, line):
        self.print_command(self.network_api.set_gprs_reset_retry_count,
                           {"count": line})  

    def do_get_gprs_reset_retry_count(self, line):
        self.print_command(self.network_api.get_gprs_reset_retry_count,
                           kwargs={})

    def do_set_gprs_credentials(self, line):
        self.print_command(self.network_api.set_gprs_credentials,
                           kwargs={"line": line})
    def do_get_gprs_credentials(self, line):
        self.print_command(self.network_api.get_gprs_credentials,
                           kwargs={})

    def do_set_gprs_broker(self, line):
        self.print_command(self.network_api.set_gprs_broker,
                           kwargs={"line": line})
    def do_reset_rtc_calib(self, line):
        self.print_command(self.network_api.reset_rtc_calib,
                            kwargs={"line": line})
    def do_get_gprs_broker(self, line):
        self.print_command(self.network_api.get_gprs_broker,
                           kwargs={})

    def do_set_gprs_protocol(self, line):
        self.print_command(self.network_api.set_gprs_protocol,
                           kwargs={"line": line})
    def do_get_gprs_protocol(self, line):
        self.print_command(self.network_api.get_gprs_protocol,
                           kwargs={})

    def do_get_gprs_ip(self, line):
        self.print_command(self.network_api.get_gprs_ip,
                           kwargs={})

    def do_set_gprs_tap_cmdexe_topic(self, line):
        self.print_command(self.network_api.set_gprs_topic,
                           kwargs={"line": line,"index": 1})
    def do_set_gprs_tap_collection_topic(self, line):
        self.print_command(self.network_api.set_gprs_topic,
                           kwargs={"line": line,"index": 2})
    def do_set_gprs_tap_push_topic(self, line):
        self.print_command(self.network_api.set_gprs_topic,
                           kwargs={"line": line,"index": 3})
    def do_get_gprs_tap_topics(self, line):
        self.print_command(self.network_api.get_gprs_topic,
                           kwargs={"index": 1})
    def do_set_gprs_dlms_pull_topic(self, line):
        self.print_command(self.network_api.set_gprs_topic,
                           kwargs={"line": line,"index": 4})
    def do_set_gprs_dlms_push_topic(self, line):
        self.print_command(self.network_api.set_gprs_topic,
                           kwargs={"line": line,"index": 5})
    def do_get_gprs_dlms_topics(self, line):
        self.print_command(self.network_api.get_gprs_topic,
                           kwargs={"index": 2})

    def do_get_num_gprs_profile(self, line):
        self.print_command(self.network_api.get_num_gprs_profile,
                           kwargs={})
    def do_get_pcb_serial_no(self, line):
        self.print_command(self.network_api.get_pcb_serial_no,
                           kwargs={"start_address": 3079})

    def do_set_pcb_serial_no(self, line):
        self.print_command(self.network_api.set_pcb_serial_no,
                           kwargs={"line":line, "start_address": 3079})
    def do_get_nic_pcb_serial_no(self, line):
        self.print_command(self.network_api.get_nic_pcb_serial_no,
                           kwargs={"start_address": 3111})

    def do_set_nic_pcb_serial_no(self, line):
        self.print_command(self.network_api.set_nic_pcb_serial_no,
                           kwargs={"line":line, "start_address": 3111})

    def do_set_ppm_rtc(self, line):
        self.print_command(self.network_api.set_ppm_rtc,kwargs={"line": line})

    def do_get_rtc_ppm(self, line):
        self.print_command(self.network_api.get_rtc_ppm,
                        kwargs={}) 

    def do_get_gprs_profile_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_gprs_profile_by_index:index(int)")
        else:
            self.print_command(self.network_api.get_gprs_profile_by_index,
                                kwargs={"index": index})

    def do_gprs_profile_print_direct(self, line):
        self.print_command(self.network_api.gprs_profile_print_direct,
                            kwargs={})

    def do_set_gprs_sim_toggle(self, line):
        self.print_command(self.network_api.set_gprs_sim_toggle,
                           kwargs={})

    def do_set_gprs_apn(self, line):
        self.print_command(self.network_api.set_gprs_apn,
                           kwargs={"line": line})
    def do_set_metering_mode(self, line):
        mode = int(line)
        self.print_command(self.network_api.set_metering_mode,
                           {"mode": mode})
    def do_set_meter_type(self, line):
        mode = int(line)
        self.print_command(self.network_api.set_meter_type,
                           {"mode": mode})
    def do_set_ct_ratio(self, line):
        mode = int(line)
        self.print_command(self.network_api.set_ct_ratio,
                           {"mode": mode})  
        
    def do_swap_apperent_Led(self, line):
        self.print_command(self.network_api.set_apprent_led,
                           kwargs={"data":line})

    def do_get_metering_mode(self, line):
        self.print_command(self.network_api.get_metering_mode,
                           kwargs={})
    def do_get_meter_type(self, line):
        self.print_command(self.network_api.get_meter_type,
                           kwargs={})
    def do_get_ct_ratio(self, line):
        self.print_command(self.network_api.get_ct_ratio,
                           kwargs={})
        
    def do_get_swaped_apperent_Led(self, line):
        self.print_command(self.network_api.get_apprent_led,
                           kwargs={})      
                           
    def do_get_instant_config_time(self, line):
        self.print_command(self.network_api.get_instant_config_time,
                           kwargs={})
    def do_set_metering_load(self, line):
        mode = int(line)
        self.print_command(self.network_api.set_metering_load,
                           {"mode": mode})  

    def do_get_metering_load(self, line):
        self.print_command(self.network_api.get_metering_load,
                           kwargs={})
    def do_calib_3p_phase_start(self, line):
        self.print_command(self.network_api.calib_3p_phase_start,
                           kwargs={})
    def do_calib_3p_phase_fu_start(self, line):
        self.print_command(self.network_api.calib_3p_phase_fu_start,
                           kwargs={})
    def do_calib_3p_phase_fl_start(self, line):
        self.print_command(self.network_api.calib_3p_phase_fl_start,
                           kwargs={})
    def do_calib_3p_neu_start(self, line):
        self.print_command(self.network_api.calib_3p_neu_start,
                           kwargs={})

    def do_set_calib_led2(self, line):
        try:
            period = int(line)
        except Exception as e:
            print ("Usage: set_calib_led2:1(kVAh) / 0(kVArh)")
        else:    
            self.print_command(self.network_api.set_calib_led2,
                           {"period": period})

    def do_get_calib_led2(self, line):
        self.print_command(self.network_api.get_calib_led2,
                           kwargs={}) 

    def do_set_freq_ph_err(self, line):
        self.print_command(self.network_api.set_freq_ph_err,
                           kwargs={"line": line})

    def do_get_solarRiseTime(self, line):
        self.print_command(self.network_api.get_solarRiseTime,
                           kwargs={"cal_time": line})

    def do_get_solarSetTime(self, line):
        self.print_command(self.network_api.get_solarSetTime,
                           kwargs={"cal_time": line})

    def do_get_auto_reg_push(self, line):
        self.print_command(self.network_api.get_auto_reg_push,
                           kwargs={}) 

    def do_set_auto_reg_push(self, line):
        self.print_command(self.network_api.set_auto_reg_push,
                           kwargs={"line": line})
    def do_get_pulse_count_flag(self, line):
        self.print_command(self.network_api.get_pulse_count_flag,
                           kwargs={}) 

    def do_set_pulse_count_flag(self, line):
        self.print_command(self.network_api.set_pulse_count_flag,
                           kwargs={"line": line})
    def do_get_kwh_pulse_counter(self, line):
        self.print_command(self.network_api.get_kwh_pulse_counter,
                           kwargs={})
    def do_get_kvah_pulse_counter(self, line):
        self.print_command(self.network_api.get_kvah_pulse_counter,
                           kwargs={})



    def do_set_solarPosition(self, line):
        args = line.split(",")
        latitude = float(args[0])
        longitude= float(args[1])
        self.print_command(self.network_api.set_solarPosition,
                           kwargs={"latitude": latitude, "longitude": longitude})

    def do_get_solarPosition(self, line):
        self.print_command(self.network_api.get_solarPosition,
                           kwargs={})

    def do_set_solarOffset(self, line):
        args = line.split(",")
        rise = int(args[0])
        sset= int(args[1])
        self.print_command(self.network_api.set_solarOffset,
                           kwargs={"sunrise": rise, "sunset": sset})    

    def do_get_solarOffset(self, line):
        self.print_command(self.network_api.get_solarOffset,
                           kwargs={})

    def do_get_num_fw_packets(self, line):
        self.print_command(self.network_api.get_num_fw_packets,
                           kwargs={})

    def do_get_fw_packet_status(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_fw_packet_status:value(int)")
        else:
            self.print_command(self.network_api.get_fw_packet_status, kwargs={"index": index})

    def do_get_flash_read(self, line):
        self.print_command(self.network_api.get_flash_read,
                                  kwargs={"line":line},
                                  to_print=True)

    def do_get_live_display_version(self, line):
        self.print_command(self.network_api.get_live_display_version,
                           kwargs={})

    def do_get_ext_display_version(self, line):
        self.print_command(self.network_api.get_ext_display_version,
                           kwargs={})

    def do_dc_cal_v1(self, line):
        voltage = int(line)
        self.print_command(self.network_api.dc_cal_v1,
                           kwargs={"voltage": voltage})

    def do_dc_cal_v2(self, line):
        voltage = int(line)
        self.print_command(self.network_api.dc_cal_v2,
                           kwargs={"voltage": voltage})

    def do_dc_cal_i(self, line):
        current = int(line)
        self.print_command(self.network_api.dc_cal_i,
                           kwargs={"current": current})

    def do_get_flash_erase_sector(self, line):
        self.print_command(self.network_api.get_flash_erase_sector,
                                  kwargs={"line":line},to_print=False)

    def do_set_active_energy_offset(self, line):
        try:
            active_offset = int(line)
        except:
            print ("Usage: do_set_active_energy_offset:int(value)")
        else:
            self.print_command(self.network_api.set_active_energy_offset,
                           kwargs={"active_offset": active_offset})

    def do_set_reactive_energy_offset(self, line):
        try:
            reactive_offset = int(line)
        except:
            print ("Usage: do_set_reactive_energy_offset:int(value)")
        else:
            self.print_command(self.network_api.set_reactive_energy_offset,
                           kwargs={"reactive_offset": reactive_offset})

    def do_set_apparent_energy_offset(self, line):
        try:
            apparent_offset = int(line)
        except:
            print ("Usage: do_set_apparent_energy_offset:int(value)")
        else:
            self.print_command(self.network_api.set_apparent_energy_offset,
                           kwargs={"apparent_offset": apparent_offset})

    def do_get_billing_info(self, line):
        self.print_command(self.network_api.get_billing_info, 
                                        kwargs={})

    def do_get_billing_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_billing_by_index:value(int)")
        else:
            self.print_command(self.network_api.get_billing_by_index, kwargs={"index": index})

    def do_get_billing_tod_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_tod_billing_by_index:value(int)")
        else:
            self.print_command(self.network_api.get_billing_tod_by_index, kwargs={"index": index, "flag": 0})

    def do_get_billing_tod_exp_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_tod_billing_by_index:value(int)")
        else:
            self.print_command(self.network_api.get_billing_tod_by_index, kwargs={"index": index, "flag": 1})

    def do_get_billing_data_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_billing_data_by_index:value(int)")
        else:
            self.print_command(self.network_api.get_billing_data_by_index, kwargs={"index": index})          
            
    def do_set_credit_limit(self,line):
        try:
            credit_limit = int(line)
        except:
            print ("Usage:do_set_credit_limit:int(value)")
        else:
            self.print_command(self.network_api.set_credit_limit, 
                           kwargs={"credit_limit":credit_limit})

    def do_set_energy_limit(self, line):
        try:
            energy_limit = int(line)
        except:
            print ("Usage:do_set_energy_limit:int(value)")
        else:
            self.print_command(self.network_api.set_energy_limit,
                           kwargs={"energy_limit": energy_limit})

    def do_unlock(self, line):
        unlock_validity = int(line)
        self.print_command(self.network_api.unlock,
                           kwargs={"unlock_validity": unlock_validity})

    def do_recharge(self, line):
        self.print_command(self.network_api.recharge,
                           kwargs={"arg": str(line)})

    def do_get_num_recharge_token(self, line):
        self.print_command(self.network_api.get_num_recharge_token,
                           kwargs={})

    def do_get_recharge_token_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_recharge_token_by_index:index(int)")
        else:
            self.print_command(self.network_api.get_recharge_token_by_index,
                                kwargs={"index": index})

    def do_get_num_recharge_entries(self, line):
        self.print_command(self.network_api.get_num_recharge_entries,
                           kwargs={})

    def do_get_recharge_entries_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_recharge_entries_by_index:index(int)")
        else:
            self.print_command(self.network_api.get_recharge_entries_by_index,
                                kwargs={"index": index})

    def do_recharge_fract(self, line):
        try:
            amount = float(line)
        except:
            print ("Usage:do_recharge_fract:float(value)")
        else:
            self.print_command(self.network_api.recharge_fract,
                           kwargs={"amount": amount})      

    def do_enable_lock(self, line):
        self.print_command(self.network_api.enable_lock,
                           kwargs={})

    def do_disable_lock(self, line):
        self.print_command(self.network_api.disable_lock,
                           kwargs={})

    def do_reset_lock(self, line):
        self.print_command(self.network_api.reset_lock,
               kwargs={})

    def do_lock_state(self, line):
        self.print_command(self.network_api.lock_state,
                           kwargs={})

    def do_reset(self, line):
        try:
            if line == "":
                line = 65
            interval = int(line)
        except:
            print ("Usage:- reset:seconds")
        else:
            self.print_command(self.network_api.reset,
                           kwargs={"interval": interval})

    def do_gateway(self, line):
        self.print_command(self.network_api.gateway,
                           kwargs={})

    def do_router(self, line):
        self.print_command(self.network_api.router,
                           kwargs={})

    def do_assert_false(self, line):
        self.print_command(self.network_api.assert_false,
                           kwargs={})

    def do_clear_nvm(self, line):
        self.print_command(self.network_api.clear_nvm,
                           kwargs={})

    def do_clear_account(self, line):
        self.print_command(self.network_api.clear_account,
                           kwargs={})

    def do_clear_recharges(self, line):
        self.print_command(self.network_api.clear_recharges,
                           kwargs={})

    def do_deassert(self, line):
        self.print_command(self.network_api.deassert,
                           kwargs={})

#    def do_turn_ui_on(self, line):
#        self.print_command(self.network_api.turn_ui_on,
#                           kwargs={})
#
#    def do_turn_ui_off(self, line):
#        self.print_command(self.network_api.turn_ui_off,
#                           kwargs={})

    def do_dc_cal_i_ofs(self, line):
        self.print_command(self.network_api.dc_cal_i_ofs,
                           kwargs={})

    def do_reset_tamper_latch(self, line):
        self.print_command(self.network_api.reset_tamper_latch,
                           kwargs={})

    def do_turn_relay_on(self, line):
        self.print_command(self.network_api.turn_relay_on,
                           kwargs={})

    def do_turn_relay_off(self, line):
        self.print_command(self.network_api.turn_relay_off,
                           kwargs={})

    def do_relay_manual_control(self, line):
        self.print_command(self.network_api.relay_manual_control,
                           kwargs={})

    def do_relay_auto_control(self, line):
        self.print_command(self.network_api.relay_auto_control,
                           kwargs={})

    def do_relay_state(self, line):
        self.print_command(self.network_api.relay_state,
                           kwargs={})

    def do_syncstream_reset(self, line):
        self.print_command(self.network_api.syncstream_reset,
                           kwargs={})

    def do_clear_log(self, line):
        self.print_command(self.network_api.clear_log,
                           kwargs={})

    def do_clear_block_load_profile(self, line):
        self.print_command(self.network_api.clear_block_load_profile,
                           kwargs={})

    def do_clear_daily_load_profile(self, line):
        self.print_command(self.network_api.clear_daily_load_profile,
                           kwargs={})

    def do_allow_negative_credits(self, line):
        self.print_command(self.network_api.allow_negative_credits,
                           kwargs={})

    def do_forbid_negative_credits(self, line):
        self.print_command(self.network_api.forbid_negative_credits,
                           kwargs={})

    def do_reset_tamper_record(self, line):
        self.print_command(self.network_api.reset_tamper_record,
                           kwargs={"tamper_type": str(line)})

    def do_request_recharge(self, line):
        self.print_command(self.network_api.request_recharge,
                           kwargs={})

    def do_set_price(self, line):
        try:
            price = float(line)
        except:
            print ("Usage:do_set_price:flaot(value)")
        else:
            self.print_command(self.network_api.set_price,
                           kwargs={"price": price})

    def do_enable_elimiter(self, line):
        self.print_command(self.network_api.enable_elimiter,
                           kwargs={})

    def do_disable_elimiter(self, line):
        self.print_command(self.network_api.disable_elimiter,
                           kwargs={})

    def do_enable_load_profile(self, line):
        self.print_command(self.network_api.enable_load_profile,
                           kwargs={})

    def do_disable_load_profile(self, line):
        self.print_command(self.network_api.disable_load_profile,
                           kwargs={})

    def do_slab_reset(self, line):
        self.print_command(self.network_api.slab_reset,
                           kwargs={})

    def do_factory_init_1(self, line):
        self.print_command(self.network_api.factory_init_1,
                           kwargs={})

    def do_factory_init_2(self, line):
        self.print_command(self.network_api.factory_init_2,
                           kwargs={})

    def do_factory_init_app(self, line):
        try:
            number = int(line)
        except:
            print ("Expected command: factory_init_app:value(1 to 8)")
            print ("1: Billing Record Clear")
            print ("2: DLMS Log Clear")
            print ("3: Event Records Clear")
            print ("4: Load Survey Logs Clear")
            print ("5: Power Limit Params Reset")
            print ("6: Relay Controller Reset")
            print ("7: Recharge Token Clear")
            print ("8: Prepaid Logs Clear")
        else: 
            self.print_command(self.network_api.factory_init_app,
                           kwargs={"number": number})

    def do_clear_event_by_category(self, line):
        try:
            number = int(line)
        except:
            print ("Expected command: event_by_category:value(1 to 7)")
            print ("1: Current related Record Clear")
            print ("2: Voltage related Record Clear")
            print ("3: Power related Record Clear")
            print ("4: Transation related Record Clear")
            print ("5: C-open Record Clear")
            print ("6: Control related Record Clear")
            print ("7: Other related Record Clear")
        else:     
            self.print_command(self.network_api.clear_event_by_category,
                           kwargs={"number": number})

    def do_set_dd_params(self, line):
        ddp = DailyDeductionParams()
        args = line.split(',')
        if (args[0].strip(' ') == "now"):
            ddp.start_time = datetime.datetime.now()
        else:
            ddp.start_time = dateutil.parser.parse(args[0])
        ddp.min_credits_per_deduction = int(args[1])
        ddp.days_per_deduction = int(args[2])
        self.print_command(self.network_api.set_dd_params,
                           kwargs={"ddp": ddp})

    def do_set_block_load_profile_params(self, line):
        try:
            args = line.split(",")
            if "now" in args[0]:
                delta = int(args[0].split("+")[1])
                start_time = datetime.datetime.now() + datetime.timedelta(seconds=delta)
            else:
                start_time = dateutil.parser.parse(args[0].strip(' '))
            interval = int(args[1])
            status = int(args[2])
            lsp = LoadSurveyParams()
            lsp.start_time = start_time
            lsp.interval = interval
            lsp.status = status
        except:
            print ("Usage:do_set_block_load_profile_params:time_stamp,survey_period,enable/disable")
        else:
            self.print_command(self.network_api.set_block_load_profile_params,
                           kwargs={"lsp": lsp})

    def do_set_slab_params(self, line):
        try:
            args = line
        except:
            print ("Usage:do_set_slab_params:no_od_slabs,slab_price,slab_limits,mmc")
        else:
            self.print_command(self.network_api.set_slab_params,
                           kwargs={"args": args})

    def do_set_slab_update_ts(self, line):
        try:
            args=line
        except:
            print ("Usage:do_set_slab_update_ts:time_stamp")
        else:
            self.print_command(self.network_api.set_slab_update_ts,
                           kwargs={"args": args})

    def do_slab_enable_on_update(self, line):
        self.print_command(self.network_api.slab_enable_on_update,
                           kwargs={})

    def do_slab_enable(self, line):
        self.print_command(self.network_api.slab_enable,
                           kwargs={})

    def do_slab_disable(self, line):
        self.print_command(self.network_api.slab_disable,
                           kwargs={})

    def do_fd_enable(self, line):
        self.print_command(self.network_api.fd_enable,
                           kwargs={})

    def do_fd_disable(self, line):
        self.print_command(self.network_api.fd_disable,
                           kwargs={})

    def do_fd_reset(self, line):
        self.print_command(self.network_api.fd_reset,
                           kwargs={})

    def do_set_fd_params(self, line):
        try:
            args = line
        except:
            print ("Usage:do_set_fd_params:amount,type")
        else:
            self.print_command(self.network_api.set_fd_params,
                           kwargs={"args": args})

    def do_get_fd_update_ts(self, line):
        self.print_command(self.network_api.get_fd_update_ts,
                           kwargs={})

    def do_get_active_fd_params(self, line):
        self.print_command(self.network_api.get_active_fd_params,
                           kwargs={})

    def do_set_fd_update_ts(self, line):
        try:
            args = line
        except:
            "Usage:do_set_fd_update_ts:time_stamp"
        else:
            self.print_command(self.network_api.set_fd_update_ts,
                           kwargs={"args": args})

    def do_broadcast_time(self, line):
        self.print_command(self.network_api.broadcast_time,
                           kwargs={})

    def do_syncstream_bundle(self, line):
        self.print_command(self.network_api.syncstream_bundle,
                           kwargs={})

    def do_non_dlms_syncstream_bundle(self, line):
        self.print_command(self.network_api.non_dlms_syncstream_bundle,
                           kwargs={})

    def do_syncstream_setup(self, line):
        interval = int(line)
        self.print_command(self.network_api.syncstream_setup,
                           kwargs={"interval": interval})

    def do_syncstream_params(self, addr):
        self.print_command(self.network_api.syncstream_params,
                           kwargs={})  


    def do_beat_time(self, line):
        self.print_command(self.network_api.beat_time,
                           kwargs={})

    def do_mem_write(self, line):
        self.print_command(self.network_api.mem_write,
                           kwargs={"line": line})

    def do_mem_read(self, line):
        data = self.print_command(self.network_api.mem_read,
                                  kwargs={"line": line},
                                  to_print=False)
        data_string = ""
        if data is not None:   
            for ch in data:                
                if (int(ch)<16):
                    data_string += "0" + str(hex(ch)[2:] )+ " " 
                else:
                    data_string += hex(ch)[2:] + " " 
            data_string_length =len(data_string)
            if(data_string_length<48):         
                    print (data_string)
            else:
                cnt=data_string_length/48
                mod=data_string_length%48
                i=0
                while(i<cnt):
                    print (data_string[(i*48):((i+1)*48)-1])
                    i = i+1
                    if((i==cnt) & mod!=0):
                        print (data_string[(i*48):])



    def do_mem_erase_block(self, line):
        mem_block_id = int(line)
        self.print_command(self.network_api.mem_erase_block,
                           kwargs={"line": line}) 

    def do_mem_erase_sector(self, line):
        mem_block_id = int(line)
        self.print_command(self.network_api.three_ph_mem_erase_sector,
                           kwargs={"line": line})

    def do_eeprom_write(self, line):
        self.print_command(self.network_api.eeprom_write,
                           kwargs={"line": line})        
    def do_eeprom_read(self, line):
        data = self.print_command(self.network_api.eeprom_read,
                                  kwargs={"line":line},
                                  to_print=False)

    def do_set_alarm_events(self, line):
        self.print_command(self.network_api.set_alarm_events,
                           kwargs={"line": line})        
    def do_get_alarm_events(self, line):
        self.print_command(self.network_api.get_alarm_events,
                                  kwargs={})

    def do_set_event_ptime2(self, line):
        self.print_command(self.network_api.set_event_ptime2,
                           kwargs={})        
    def do_get_event_ptime2(self, line):
        self.print_command(self.network_api.get_event_ptime2,
                                  kwargs={})

    def do_check_dlms_activation(self, line):
        data = self.print_command(self.network_api.check_dlms_activation,
                                  kwargs={})

    def do_1p_ui_config(self, line):
        arg = line.split("\n")
        file_name = str(arg[0])
        self.print_command(self.network_api.one_ph_ui_config,
                           kwargs={"main_txt_file_path":file_name}) 

    def do_set_dcu_push_interval(self, line):
        try:
            push_interval = int(line)
        except:
            print ("Usage:do_set_dcu_push_interval:int(value)")
        else:
            self.print_command(self.network_api.set_push_interval,
                           kwargs={"push_interval": push_interval})

    def do_push_disable(self, line):
        self.print_command(self.network_api.push_disable,
               kwargs={})

    def do_set_ip_time(self, line):
        self.print_command(self.network_api.set_ip_time,
                           kwargs={"cal_time": line})
    def do_calib_unlock(self,line):
        self.print_command(self.network_api.calib_unlock,
                           kwargs={"calib_number": line})   
    def do_initiate_fw_upgrade(self, line):
        self.print_command(self.network_api.initiate_fw_upgrade,
                           kwargs={})

    def do_initiate_ui_upgrade(self, line):
        self.print_command(self.network_api.initiate_ui_upgrade,
                           kwargs={})

    def do_tod_enable(self, line):
        self.print_command(self.network_api.tod_enable,
               kwargs={})

    # def do_tod_disable(self, line):
    #     self.print_command(self.network_api.tod_disable,
    #            kwargs={})

    # def do_tod_reset(self, line):
    #     self.print_command(self.network_api.tod_reshdule,
    #            kwargs={})

    # def do_set_tod_params(self, line):
    #     try:
    #         args = line
    #     except:
    #         print "needs argument"
    #     else:
    #         self.print_command(self.network_api.set_tod_params,
    #                        kwargs={"args": args})

    def do_tod_enable(self, line):
        self.print_command(self.network_api.tod_enable,
               kwargs={})

    def do_tod_disable(self, line):
        self.print_command(self.network_api.tod_disable,
               kwargs={})

    def do_enable_fixed_billing(self, line):
        self.print_command(self.network_api.enable_fixed_billing,
               kwargs={})

    def do_disable_fixed_billing(self, line):
        self.print_command(self.network_api.disable_fixed_billing,
               kwargs={})

    def do_set_tod_power_limit(self, line):
        try:
            args = line
        except:
            print ("needs argument")
        else:
            self.print_command(self.network_api.set_tod_power_limit,
                           kwargs={"args": args})
    
    def do_get_tod_power_limit(self, line):
        self.print_command(self.network_api.get_tod_power_limit,
                            kwargs={})

    def do_set_power_limit_params(self, line):
        try:
            args = line
        except:
            print ("needs argument")
        else:
            self.print_command(self.network_api.set_power_limit_params,
                           kwargs={"args": args})
    
    def do_get_power_limit_params(self, line):
        self.print_command(self.network_api.get_power_limit_params,
                            kwargs={})

    def do_get_power_event_logs(self, line):
        self.print_command(self.network_api.get_power_event_logs,
                            kwargs={"index":line})


    def do_get_battery_logs(self, line):
        self.print_command(self.network_api.get_battery_logs,
                            kwargs={})    

    def do_clear_battery_logs(self, line):
        self.print_command(self.network_api.clear_battery_logs,
               kwargs={})

    def do_get_bootloader_logs(self, line):
        self.print_command(self.network_api.get_bootloader_logs,
                            kwargs={})
    def do_get_battery_volt_params(self, line):
        self.print_command(self.network_api.get_battery_volt_params,
                            kwargs={})

    def do_get_nameplate(self, line):
        self.print_command(self.network_api.get_nameplate,
                            kwargs={})

    def do_set_prepaid_billing_type(self, line):
        self.print_command(self.network_api.set_prepaid_billing_type,
                           {"line": line})  

    def do_get_prepaid_billing_type(self, line):
        self.print_command(self.network_api.get_prepaid_billing_type,
                           kwargs={})

    def do_set_dg_phase_type(self, line):
        self.print_command(self.network_api.set_dg_phase_type,
                           {"line": line})  

    def do_get_dg_phase_type(self, line):
        self.print_command(self.network_api.get_dg_phase_type,
                           kwargs={})

    def do_set_prepaid_auto_switch(self, line):
        self.print_command(self.network_api.set_prepaid_auto_switch,
                           {"line": line})  

    def do_get_prepaid_auto_switch(self, line):
        self.print_command(self.network_api.get_prepaid_auto_switch,
                           kwargs={})

    def do_set_friendly_holidays(self, line):
        self.print_command(self.network_api.set_friendly_holidays,
                           kwargs={"cal_time": line})

    def do_get_friendly_holidays(self, line):
        self.print_command(self.network_api.get_friendly_holidays,
                           kwargs={})

    def do_set_friendly_weekday(self, line):
        self.print_command(self.network_api.set_friendly_weekday,
                           {"line": line})

    def do_get_friendly_weekday(self, line):
        self.print_command(self.network_api.get_friendly_weekday,
                           kwargs={})


    def do_set_tod_params(self, line):
        try:
            args = line
        except:
            print ("needs argument")
        else:
            self.print_command(self.network_api.set_tod_params,
                           kwargs={"args": args})

    def do_get_tod_params(self, line):
        self.print_command(self.network_api.get_tod_params,
                            kwargs={})

    def do_get_fixed_billing_status(self, line):
        self.print_command(self.network_api.get_disable_fixed_billing_status,
                            kwargs={})


    def do_maxwell_cal_time(self, line):
        if line == "":
            cal_time = 0
        elif line.strip(' ') == "now":
            cal_time = datetime.datetime.now()
        else:
            cal_time = dateutil.parser.parse(line)
        self.print_command(self.network_api.maxwell_cal_time,
                           kwargs={"cal_time": cal_time})

    def do_set_pulse(self, line):
        self.print_command(self.network_api.set_pulse,
                           kwargs={"cal_time": line})        

    def do_maxwell_cal_mtrno(self, line):
        self.print_command(self.network_api.maxwell_cal_mtrno,
                           kwargs={"serial_num": line})

    def do_maxwell_clear_1(self, line):
        self.print_command(self.network_api.maxwell_clear_1,
                           kwargs={})

    def do_maxwell_clear_2(self, line):
        self.print_command(self.network_api.maxwell_clear_2,
                           kwargs={})

    def do_maxwell_cal_energy(self, line):
        self.print_command(self.network_api.maxwell_cal_energy,
                           kwargs={"error_percent": float(line)})

    def do_maxwell_cal_v(self, line):
        self.print_command(self.network_api.maxwell_cal_v,
                           kwargs={})

    def do_maxwell_cal_ip(self, line):
        self.print_command(self.network_api.maxwell_cal_ip,
                           kwargs={})

    def do_maxwell_cal_in(self, line):
        self.print_command(self.network_api.maxwell_cal_in,
                           kwargs={})

    def do_maxwell_meter_lock(self, line):
        self.print_command(self.network_api.maxwell_meter_lock,
                           kwargs={})

    def do_get_meter_serial_no(self, line):
        self.print_command(self.network_api.get_meter_serial_no,
                           kwargs={})
    def do_check_dlms_activation(self, line):
        data = self.print_command(self.network_api.check_dlms_activation,
                                  kwargs={})
    def do_exit(self, line):
        return True

    def do_use(self, line):
        self.address = Address(line)
        self.prompt = "{green}node-shell{yellow} [{address}] {blue}${white} ".\
            format(address=self.address,
                   green=Fore.GREEN,
                   yellow=Fore.YELLOW,
                   blue=Fore.BLUE,
                   white=Fore.WHITE)

    def do_log_print_direct(self, line):
        self.logger.update_header()
        self.logger.print_log_from_node()

    def do_log_dump_bin(self, line):
        self.logger.update_header()
        self.logger.dump("log.bin")
        self.logger.dump_header_to_file("header.json")

    def do_log_print_bin(self, line):
        self.logger.load_header_from_file("header.json")
        self.logger.print_log_from_bin("log.bin")

    def do_log_header(self, line):
        self.logger.update_header()
        self.logger.dump_header_to_file("header.json")
        print (self.logger.header)

    def do_block_load_profile_print_direct(self, line):
        self.print_command(self.network_api.block_load_print_direct,
                            kwargs={"line":line})
    def do_instant_data_profile_print_direct(self, line):
        self.print_command(self.network_api.instant_load_print_direct,
                            kwargs={"line":line})

    def do_daily_load_profile_print_direct(self, line):
        self.print_command(self.network_api.daily_load_profile_print_direct,
                            kwargs={})

    def do_block_load_profile_store_file(self, line):
        self.block_load_profile.update_header()
        self.block_load_profile.store_block_profile_in_file()

    def do_daily_load_profile_store_file(self, line):
        self.daily_load_profile.update_header()
        self.daily_load_profile.store_daily_profile_in_file()

    def do_block_load_profile_dump_bin(self, line):
        self.block_load_profile.update_header()
        self.block_load_profile.dump("block_load_profile.bin")
        self.block_load_profile.dump_header_to_file("header.json")

    def do_daily_load_profile_dump_bin(self, line):
        self.daily_load_profile.update_header()
        self.daily_load_profile.dump("daily_load_profile.bin")
        self.daily_load_profile.dump_header_to_file("header.json")

    def do_block_load_profile_print_bin(self, line):
        self.block_load_profile.load_header_from_file("header.json")
        self.block_load_profile.print_block_profile_from_bin(
            "block_load_profile.bin")

    def do_daily_load_profile_print_bin(self, line):
        self.daily_load_profile.load_header_from_file("header.json")
        self.daily_load_profile.print_daily_profile_from_bin(
            "daily_load_profile.bin")

    def do_block_load_profile_header(self, line):
        self.block_load_profile.update_header()
        self.block_load_profile.dump_header_to_file("header.json")
        print (self.block_load_profile.header)

    def do_daily_load_profile_header(self, line):
        self.daily_load_profile.update_header()
        self.daily_load_profile.dump_header_to_file("header.json")
        print (self.daily_load_profile.header)

    def do_block_load_profile_to_store(self, line):
        self.block_load_profile.block_load_profile_to_store(
            "block_load_profile.bin")
    def do_set_config_time(self, line):
        self.print_command(self.network_api.set_config_time,
                            kwargs={"num":line})
    def do_set_enable_write_data(self, line):
        self.print_command(self.network_api.set_enable_write_data,
                            kwargs={"num":line})

    def do_daily_load_profile_to_store(self, line):
        self.daily_load_profile.daily_load_profile_to_store(
            "daily_load_profile.bin")

    # rf packet mode commands
    def do_trace_path(self, line):
        self.print_command(self.network_api.trace_path,
                           kwargs={})

    # E-cop commands
    def do_get_metering_data(self, line):
        self.print_command(self.network_api.get_metering_data,
                           kwargs={})

    def do_get_calib_status(self, line):
        self.print_command(self.network_api.get_calib_status,
                           kwargs={})

    def do_ecop_cal_time(self, line):
        if line.strip(' ') == "now":
            date_time = datetime.datetime.now()
        else:
            date_time = dateutil.parser.parse(line)
        self.print_command(self.network_api.ecop_cal_time,
                           kwargs={"date_time": date_time})

    def do_set_dlog_params(self, line):
        args = line.split(",")
        if "now" in args[0]:
            delta = int(args[0].split("+")[1])
            start_time = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            start_time = dateutil.parser.parse(args[0].strip(' '))
        interval = int(args[1])
        lsp = LoadSurveyParams()
        lsp.start_time = start_time
        lsp.interval = interval
        self.print_command(self.network_api.set_dlog_params,
                           kwargs={"lsp": lsp})

    def do_get_dlog_params(self, line):
        self.print_command(self.network_api.get_dlog_params,
                           kwargs={})

    def do_get_newest_dlog(self, line):
        self.print_command(
            self.network_api.get_newest_dlog, kwargs={
                "interval": self.network_api.get_survey_interval(
                    self.address)})

    def do_get_oldest_dlog(self, line):
        self.print_command(
            self.network_api.get_oldest_dlog, kwargs={
                "interval": self.network_api.get_survey_interval(
                    self.address)})

    def do_get_num_dlog(self, line):
        self.print_command(self.network_api.get_num_dlog,
                           kwargs={})

    def do_get_dlog_interval(self, line):
        self.print_command(self.network_api.get_dlog_interval,
                           kwargs={})

    def do_clear_dlog(self, line):
        self.print_command(self.network_api.clear_dlog,
                           kwargs={})

    def do_enable_dlog(self, line):
        self.print_command(self.network_api.enable_dlog,
                           kwargs={})

    def do_disable_dlog(self, line):
        self.print_command(self.network_api.disable_dlog,
                           kwargs={})

    def do_dlog_print_direct(self, line):
        self.dlog.update_header()
        self.dlog.print_survey_from_node()

    def parseline(self, line):
        # This function exists to maintain backward compatibility with the
        # syntax typically used in node-shell.
        # For example, if "set price: 50" is used, it is interpreted
        # as "set_price 50"
        format_found = False
        try:
            ret = line.split(':')
            ret = (ret[0].replace(' ', '_'), ''.join(ret[1:]), line)
            format_found = True
        except IndexError as err:
            pass
        if not format_found:
            ret = (line.replace(' ', '_'), '', line)

        return ret

    # Billing Profile Commands
    def do_clear_active_MD_month(self, line):
        self.print_command(self.network_api.clear_active_MD_month,
                           kwargs={"MD_month": line})

    def do_clear_reactive_MD_month(self, line):
        self.print_command(self.network_api.clear_reactive_MD_month,
                           kwargs={"MD_month": line})

    def do_clear_apparent_MD_month(self, line):
        self.print_command(self.network_api.clear_apparent_MD_month,
                           kwargs={"MD_month": line})

    def do_clear_active_energy_history(self, line):
        self.print_command(self.network_api.clear_active_energy_history,
                           kwargs={"month": line})

    def do_clear_reactive_lead_energy_history(self, line):
        self.print_command(self.network_api.clear_reactive_lead_energy_history,
                           kwargs={"month": line})

    def do_clear_reactive_lag_energy_history(self, line):
        self.print_command(self.network_api.clear_reactive_lag_energy_history,
                           kwargs={"month": line})

    def do_clear_apparent_energy_history(self, line):
        self.print_command(self.network_api.clear_apparent_energy_history,
                           kwargs={"month": line})

    def do_clear_billing_date(self, line):
        self.print_command(self.network_api.clear_billing_date,
                           kwargs={"month": line})

    def do_clear_system_power_factor(self, line):
        self.print_command(self.network_api.clear_system_power_factor,
                           kwargs={"month": line})

    def do_clear_cumulative_billing_count(self, line):
        self.print_command(self.network_api.clear_cumulative_billing_count,
                           kwargs={})

    def do_clear_billing_power_on_time(self, line):
        self.print_command(self.network_api.clear_billing_power_on_time,
                           kwargs={"month": line})

    def do_clear_cumulative_power_on_time(self, line):
        self.print_command(self.network_api.clear_cumulative_power_on_time,
                           kwargs={})

    def do_clear_cumulative_programming_count(self, line):
        self.print_command(self.network_api.clear_cumulative_programming_count,
                           kwargs={})

    def do_get_instantaneous_active_MD(self, line):
        self.print_command(self.network_api.get_instantaneous_active_MD,
                           kwargs={})

    def do_get_current_active_MD(self, line):
        self.print_command(self.network_api.get_current_active_MD,
                           kwargs={})

    def do_get_past_active_MD(self, line):
        self.print_command(self.network_api.get_past_active_MD,
                           kwargs={"MD_month": line})

    def do_get_instantaneous_reactive_MD(self, line):
        self.print_command(self.network_api.get_instantaneous_reactive_MD,
                           kwargs={})

    def do_get_current_reactive_MD(self, line):
        self.print_command(self.network_api.get_current_reactive_MD,
                           kwargs={})

    def do_get_past_reactive_MD(self, line):
        self.print_command(self.network_api.get_past_reactive_MD,
                           kwargs={"MD_month": line})

    def do_get_instantaneous_apparent_MD(self, line):
        self.print_command(self.network_api.get_instantaneous_apparent_MD,
                           kwargs={})

    def do_get_current_apparent_MD(self, line):
        self.print_command(self.network_api.get_current_apparent_MD,
                           kwargs={})

    def do_get_past_apparent_MD(self, line):
        self.print_command(self.network_api.get_past_apparent_MD,
                           kwargs={"MD_month": line})

    def do_get_active_energy_history(self, line):
        self.print_command(self.network_api.get_active_energy_history,
                           kwargs={"month": line})

    def do_get_reactive_lead_energy_history(self, line):
        self.print_command(self.network_api.get_reactive_lead_energy_history,
                           kwargs={"month": line})

    def do_get_reactive_lag_energy_history(self, line):
        self.print_command(self.network_api.get_reactive_lag_energy_history,
                           kwargs={"month": line})

    def do_get_apparent_energy_history(self, line):
        self.print_command(self.network_api.get_apparent_energy_history,
                           kwargs={"month": line})

    def do_get_billing_date(self, line):
        self.print_command(self.network_api.get_billing_date,
                           kwargs={"month": line})

    def do_get_system_power_factor(self, line):
        self.print_command(self.network_api.get_system_power_factor,
                           kwargs={"month": line})

    def do_get_cumulative_billing_count(self, line):
        self.print_command(self.network_api.get_cumulative_billing_count,
                           kwargs={})

    def do_get_billing_power_on_time(self, line):
        self.print_command(self.network_api.get_billing_power_on_time,
                           kwargs={"month": line})

    def do_get_cumulative_power_on_time(self, line):
        self.print_command(self.network_api.get_cumulative_power_on_time,
                           kwargs={})

    def do_get_cumulative_programming_count(self, line):
        self.print_command(self.network_api.get_cumulative_programming_count,
                           kwargs={})

    def do_get_billing_timestamp(self, line):
        self.print_command(self.network_api.get_billing_timestamp,
                           kwargs={})

    def do_get_MD_avg_period(self, line):
        self.print_command(self.network_api.get_MD_avg_period,
                           kwargs={})

    def do_set_billing_timestamp(self, line):
        if line == "":
            billing_timestamp = 0
        elif line.strip(' ') == "now":
            billing_timestamp = datetime.datetime.now()
        else:
            billing_timestamp = dateutil.parser.parse(line)
        self.print_command(self.network_api.set_billing_timestamp,
                           kwargs={"billing_timestamp": billing_timestamp})

    def do_set_MD_avg_period(self, line):
        try:
            avg_period = int(line)
        except:
            print ("Usage:do_set_MD_avg_period:int(value) ")
        else:
            self.print_command(self.network_api.set_MD_avg_period,
                               kwargs={"avg_period": avg_period})

    def do_get_MD_LCD_display(self, line):
        self.print_command(self.network_api.get_MD_LCD_display,
                           kwargs={})

    def do_set_MD_LCD_display(self, line):
        past_display = int(line)
        self.print_command(self.network_api.set_MD_LCD_display,
                           kwargs={"past_display": past_display})

    # Tamper Logger Commands
    def do_tamper_log_print_direct(self, line):
        self.tamper_logger.update_header()
        self.tamper_logger.print_tamper_log_from_node()

    def do_clear_tamper_log(self, line):
        self.print_command(self.network_api.clear_tamper_log,
                           kwargs={})

    def do_get_tamper_logger_period(self, line):
        self.print_command(self.network_api.get_tamper_logger_period,
                           kwargs={})

    def do_get_num_tamper_logs(self, line):
        self.print_command(self.network_api.get_num_tamper_logs,
                           kwargs={})

    def do_set_tamper_logger_period(self,line):
        try:
            persistence_period = int(line)
        except:
            print ("Usage:do_set_tamper_logger_period:int(value)")
        else:
            self.print_command(self.network_api.set_tamper_logger_period, 
                          kwargs={"persistence_period": persistence_period})

    # Undervoltage Threshold Commands
    def do_get_undervoltage_threshold(self, line):
        self.print_command(self.network_api.get_undervoltage_threshold,
                           kwargs={})

    def do_set_undervoltage_threshold(self,line):
        try:
            threshold = int(line)
        except:
            print ("Usage:do_set_undervoltage_threshold:int(value)")
        else:
            self.print_command(self.network_api.set_undervoltage_threshold, 
                          kwargs={"threshold": threshold})

    # Power Failure Commands
    def do_clear_power_failure_duration(self, line):
        self.print_command(self.network_api.clear_power_failure_duration,
                           kwargs={})

    def do_clear_power_failure_count(self, line):
        self.print_command(self.network_api.clear_power_failure_count,
                           kwargs={})

    def do_get_power_failure_duration(self, line):
        self.print_command(self.network_api.get_power_failure_duration,
                           kwargs={})

    def do_get_power_failure_count(self, line):
        self.print_command(self.network_api.get_power_failure_count,
                           kwargs={})

    # Event Record Commands
    def do_clear_event_record(self, line):
        self.print_command(self.network_api.clear_event_record,
                           kwargs={})

    def do_enable_event_record(self, line):
        self.print_command(self.network_api.enable_event_record,
                           kwargs={})

    def do_disable_event_record(self, line):
        self.print_command(self.network_api.disable_event_record,
                           kwargs={})

    def do_get_newest_event_record(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_get_newest_event_record:event_category(int)")
        else:
            self.print_command(self.network_api.get_newest_event_record,
                           kwargs={"index": index})

    def do_get_oldest_event_record(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_get_oldest_event_record:event_category(int)")
        else:
            self.print_command(self.network_api.get_oldest_event_record,
                               kwargs={"index": index})

    def do_get_num_event_record(self, line):
        self.print_command(self.network_api.get_num_event_record,
                           kwargs={})

    def do_get_event_record_by_index(self, line):
        try:
            arg = line.split(",")
            event_category = int(arg[0])
            print ("Event Category: " + str(event_category))
            index = int(arg[1])
            print ("Index: " + str(index))
        except Exception as e:
            print ("Expected command:   get_event_record_by_index:event_category(int),index(int)")
            print ("Event category should be in the range of 1 to 8. \n 1. Current Related Events \n 2. Voltage Related Events \n 3. Power Related Events \n 4. Transaction Related Events \n 5. Non-roll over Related Events \n 6. Control Related Events \n 7. Other Related Events\n 8. RF Related Events")
            print ("Index should be within the entries.")
        else:
            self.print_command(self.network_api.get_event_record_by_index, kwargs={
                               "index": index, "event_category": event_category})

    def do_event_record_print_direct(self, line):
        try:
            index = int(line)
        except:
            print ("Expected command:  event_record_print_direct:int(Event category)")
            print ("Event category should be in the range of 1 to 8.\n 1. Current Related Events \n 2. Voltage Related Events \n 3. Power Related Events \n 4. Transaction Related Events \n 5. Non-roll over Related Events \n 6. Control Related Events \n 7. Other Related Events\n 8. RF Related Events")
        else:
            self.print_command(self.network_api.event_record_print_direct,
                           kwargs={"index": index})


    def do_get_metering_record_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_metering_record_by_index:value(int)")
        else:
            self.print_command(self.network_api.get_metering_record_by_index, kwargs={"index": index})

    def do_get_num_metering_record(self, line):
        self.print_command(self.network_api.get_num_metering_record, kwargs={})

    def do_clear_metering_record(self, line):
        self.print_command(self.network_api.clear_metering_record, kwargs={})

    def do_get_metering_record_interval(self, line):
        self.print_command(self.network_api.get_metering_record_interval,
                           kwargs={}) 

    def do_set_metering_record_interval(self, line):
        self.print_command(self.network_api.set_metering_record_interval,
                           {"line": line})

    def do_get_metering_samples_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: get_metering_samples_by_index:value(int)")
        else:
            self.print_command(self.network_api.get_metering_samples_by_index, kwargs={"index": index})

    def do_get_num_metering_samples_record(self, line):
        self.print_command(self.network_api.get_num_metering_samples_record, kwargs={})

    def do_clear_metering_samples_record(self, line):
        self.print_command(self.network_api.clear_metering_samples_record, kwargs={})

    def do_metering_record_print_direct(self, line):
        self.print_command(self.network_api.metering_record_print_direct,
                           kwargs={})

    # 1P Metering Data Commands
    def do_get_3p_metering_data(self, line):
        self.print_command(self.network_api.get_3p_metering_data,
                           kwargs={})
    
    def do_get_THD_data(self, line):
        self.print_command(self.network_api.get_THD_data,
                           kwargs={})
    def do_get_3p_metering_data2(self, line):
        self.print_command(self.network_api.get_3p_metering_data2,
                           kwargs={})
    def do_get_3p_HR_energy_values(self, line):
        self.print_command(self.network_api.get_3p_HR_energy_values,
                           kwargs={})

    def do_get_3p_dcu_bundle(self,line):
        self.print_command(self.network_api.dcu_data_bundle,
                           kwargs={})
    def do_get_3p_calib_cofficient(self,line):
        self.print_command(self.network_api.get_3p_calib_cofficient,
                           kwargs={})

    # Syncstream Commands
    def do_get_syncstream_interval(self, line):
        self.print_command(self.network_api.  get_syncstream_interval,
                           kwargs={})

    def do_set_syncstream_interval(self, line):
        syncstream_interval = int(line)
        self.print_command(self.network_api.set_syncstream_interval,
                           kwargs={"syncstream_interval": syncstream_interval})

    def do_get_syncstream_bundle(self, line):
        self.print_command(self.network_api.get_syncstream_bundle,
                           kwargs={})
    def do_set_relay_mode(self,line):
        self.print_command(self.network_api.set_relay_mode,
                           kwargs={"calib_number": line}) 
    def do_get_ipv6_address(self, line):
        self.print_command(self.network_api.get_ipv6_address,
                            kwargs={})

    def do_set_ipv6_address(self, line):
        args = line
        self.print_command(self.network_api.set_ipv6_address,
                           kwargs={"args": args})
						   
    def do_set_serial_number(self,line):
        serial_number = int(line)
        self.print_command(self.network_api.set_serial_number,
                           kwargs={"serial_number": serial_number})

    def do_clear_energy_registers(self, line):
        self.print_command(self.network_api.tod_enable,
                           kwargs={})
    
    def do_enable_print_rxtx(self, line):
        self.print_command(self.network_api.enable_print_rxtx,
                           kwargs={}) 
    def do_disable_print_rxtx(self, line):
        self.print_command(self.network_api.disable_print_rxtx,
                           kwargs={})   
    def do_get_relay_status(self, line):
        self.print_command(self.network_api.get_relay_status,
                           kwargs={})

    def do_get_3p_relay_status(self, line):
        self.print_command(self.network_api.get_3p_relay_status,
                           kwargs={})  
    #--------------------------------------------------------------------------------------------------#
    #--------------------------------------------------------------------------------------------------#
    #-------------------------------------3 Phase Commands Start Here----------------------------------#
    #--------------------------------------------------------------------------------------------------#
    #--------------------------------------------------------------------------------------------------#
    '''
    3 phase things start from here
    '''
    ''''-----TARIFF-SLAB-RELATED-THREE-PHASE-COMMANDS--------------------'''
    ''''-----------------------------------------------------------------'''

    def do_3p_set_slab_params(self, line):
        args = line
        self.print_command(self.network_api.three_ph_set_slab_params,
                           kwargs={"args": args})

    def do_3p_set_slab_update_ts(self, line):
        args = line
        self.print_command(self.network_api.three_ph_set_slab_update_ts,
                           kwargs={"args": args})

    def do_3p_slab_enable_on_update(self, line):
        self.print_command(self.network_api.three_ph_slab_enable_on_update,
                           kwargs={})

    def do_3p_slab_enable(self, line):
        self.print_command(self.network_api.three_ph_slab_enable,
                           kwargs={})

    def do_3p_slab_disable(self, line):
        self.print_command(self.network_api.three_ph_slab_disable,
                           kwargs={})

    def do_3p_get_accounting_state(self, line):
        self.print_command(self.network_api.three_ph_get_accounting_state,
                           kwargs={})

    def do_3p_get_slab_update_ts(self, line):
        self.print_command(self.network_api.three_ph_get_slab_update_ts,
                           kwargs={})

    def do_3p_slab_reset(self, line):
        self.print_command(self.network_api.three_ph_slab_reset,
                           kwargs={})
    '''
    ''''--------FIXED-DEDUCTION-RELEATED-THREE-PHASE-COMMANDS------------'''
    ''''------------------------------------------------------------------'''

    def do_3p_fd_enable(self, line):
        self.print_command(self.network_api.three_ph_fd_enable,
                           kwargs={})

    def do_3p_fd_disable(self, line):
        self.print_command(self.network_api.three_ph_fd_disable,
                           kwargs={})

    def do_3p_fd_reset(self, line):
        self.print_command(self.network_api.three_ph_fd_reset,
                           kwargs={})

    def do_3p_set_fd_params(self, line):
        args = line
        self.print_command(self.network_api.three_ph_set_fd_params,
                           kwargs={"args": args})

    def do_3p_get_fd_update_ts(self, line):
        self.print_command(self.network_api.three_ph_get_fd_update_ts,
                           kwargs={})

    def do_3p_get_active_fd_params(self, line):
        self.print_command(self.network_api.three_ph_get_active_fd_params,
                           kwargs={})

    def do_3p_set_fd_update_ts(self, line):
        args = line
        self.print_command(self.network_api.three_ph_set_fd_update_ts,
                           kwargs={"args": args})

    '''
    ''''------PREPAID-ACCOUNT-RELEATED-THREE-PHASE-COMMANDS-----------'''
    '''----------------------------------------------------------------'''

    def do_3p_clear_account(self, line):
        self.print_command(self.network_api.three_ph_clear_account,
                           kwargs={})

    def do_3p_allow_negative_credits(self, line):
        self.print_command(self.network_api.three_ph_allow_negative_credits,
                           kwargs={})

    def do_3p_forbid_negative_credits(self, line):
        self.print_command(self.network_api.three_ph_forbid_negative_credits,
                           kwargs={})

    def do_3p_get_credit_limit(self, line):
        self.print_command(self.network_api.three_ph_get_credit_limit,
                           kwargs={})

    def do_3p_get_accurate_credits(self, line):
        self.print_command(self.network_api.three_ph_get_accurate_credits,
                           kwargs={})

    def do_3p_get_credits(self, line):
        self.print_command(self.network_api.three_ph_get_credits,
                           kwargs={})

    def do_3p_set_credit_limit(self, line):
        credit_limit = int(line)
        self.print_command(self.network_api.three_ph_set_credit_limit,
                           kwargs={"credit_limit": credit_limit})

    def do_3p_set_price(self, line):
        price = float(line)
        self.print_command(self.network_api.three_ph_set_price,
                           kwargs={"price": price})

    def do_3p_get_price(self, line):
        self.print_command(self.network_api.three_ph_get_price,
                           kwargs={})

    ''''--------RECHARGE-CLIENT-RELEATED-THREE-PHASE-COMMANDS----------'''
    '''-----------------------------------------------------------------'''

    # =================================================================================
    def do_3p_get_net_account(self, line):
        self.print_command(self.network_api.three_ph_get_net_account,
                           kwargs={})
    #==================================================================================

    def do_3p_get_net_recharge(self, line):
        self.print_command(self.network_api.three_ph_get_net_recharge,
                           kwargs={})

    def do_3p_get_neg_recharge(self, line):
        self.print_command(self.network_api.three_ph_get_neg_recharge,
                           kwargs={})

    def do_3p_get_pos_recharge(self, line):
        self.print_command(self.network_api.three_ph_get_pos_recharge,
                           kwargs={})

    def do_3p_recharge_fract(self, line):
        self.print_command(self.network_api.three_ph_recharge_fract,
                           kwargs={"amount": float(line)})

    def do_3p_clear_recharges(self, line):
        self.print_command(self.network_api.three_ph_clear_recharges,
                           kwargs={})

    def do_3p_request_recharge(self, line):
        self.print_command(self.network_api.three_ph_request_recharge,
                           kwargs={})

    ''''------LOAD-SURVEY-THINGS-STARTS-HERE-----------------------------'''
    ''''-----------------------------------------------------------------'''

    def do_3p_get_survey_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_3p_get_survey_by_index:value(int)")
        else:
            self.print_command(self.network_api.three_ph_get_survey_by_index,
                               kwargs={"index": index})

    def do_3p_get_daily_profile_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_3p_get_daily_profile_by_index:value(int)")
        else:
            self.print_command(
                self.network_api.three_ph_get_daily_profile_by_index,
                kwargs={
                    "index": index})

    def do_3p_survey_print_direct(self, line):
        self.print_command(self.network_api.three_ph_survey_print_direct,
                           kwargs={})

    def do_3p_daily_profile_print_direct(self, line):
        self.print_command(
            self.network_api.three_ph_daily_profile_print_direct,
            kwargs={})

    def do_3p_clear_load_survey(self, line):
        self.print_command(self.network_api.three_ph_clear_load_survey,
                           kwargs={})

    def do_3p_clear_daily_profile(self, line):
        self.print_command(self.network_api.three_ph_clear_daily_profile,
                           kwargs={})

    def do_3p_get_num_surveys(self, line):
        self.print_command(self.network_api.three_ph_get_num_surveys,
                           kwargs={})

    def do_3p_get_num_daily_profile(self, line):
        self.print_command(self.network_api.three_ph_get_num_daily_profile,
                           kwargs={})

    def do_3p_get_survey_interval(self, line):
        self.print_command(self.network_api.three_ph_get_survey_interval,
                           kwargs={})

    def do_3p_set_survey_interval(self, line):
        try:
            survey_interval = int(line)
        except:
            print ("Usage: do_3p_set_survey_interval:value(int)")
        else:
            self.print_command(self.network_api.three_ph_set_survey_interval,
                               kwargs={"survey_interval": survey_interval})
    '''------LOAD-SURVEY-THINGS-END-HERE-----------------------------------
    ''''------------------------------------------------------------------'''

    def do_3p_clear_event_logs(self, line):
        self.print_command(self.network_api.three_ph_clear_event_record,
                           kwargs={})

    def do_3p_get_newest_event_log(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_3p_get_newest_event_log:value(int)")
        else:
            self.print_command(
                self.network_api.three_ph_get_newest_event_record,
                kwargs={
                    "index": index})

    def do_3p_get_oldest_event_log(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_3p_get_oldest_event_log:value(int)")
        else:
            self.print_command(
                self.network_api.three_ph_get_oldest_event_record,
                kwargs={
                    "index": index})

    def do_3p_get_num_event_logs(self, line):
        self.print_command(self.network_api.three_ph_get_num_event_record,
                           kwargs={})

    def do_3p_get_event_logs_by_index(self, line):
        try:
            arg = line.split(",")
            event_category = int(arg[0])
            print ("Event Category " + str(event_category))
            index = int(arg[1])
            print ("Index " + str(index))
        except Exception as e:
            print ("Usage: do_3p_get_event_logs_by_index:value(int),vlaue(int)")
            print (e)
        else:
            self.print_command(
                self.network_api.three_ph_get_event_record_by_index, kwargs={
                    "index": index, "event_category": event_category})

    def do_3p_event_logs_print_direct(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_3p_event_logs_print_direct:int(value)")
        else:
            self.print_command(
                self.network_api.three_ph_event_record_print_direct,
                kwargs={
                    "index": index})

    def do_3p_set_persistance_time(self, line):
        try:
            arg = line.split(",")
            occurence_time = int(arg[0])
            print ("Occurence time : " + str(occurence_time) + " Seconds")
            restoration_time = int(arg[1])
            print ("Restoration time : " + str(restoration_time) + " Seconds")
        except Exception as e:
            print ("Usage: 3p_set_persistance_time:int(value),int(value)")
            print (e)
        else:
            self.print_command(
                self.network_api.three_ph_set_persistance_time,
                kwargs={
                    "occurence_time": occurence_time,
                    "restoration_time": restoration_time})

    def do_3p_get_cumulative_tamper_count(self, line):
        self.print_command(
            self.network_api.three_ph_get_cumulative_tamper_count,
            kwargs={})

    def do_3p_get_metering_data_ip(self, line):
        self.print_command(self.network_api.three_ph_get_metering_data_ip,
                           kwargs={})

    def do_3p_get_metering_data_energy(self, line):
        self.print_command(self.network_api.three_ph_get_metering_data_energy,
                           kwargs={})

    def do_3p_get_metering_data_resolution(self, line):
        self.print_command(
            self.network_api.three_ph_get_metering_data_resoultion,
            kwargs={})
    "------------CHANGE METER PROTOCOL RELEATED COMMANDS-----------"
    "---------------------------------------------------------------"

    def do_dongle_dlms_to_tap(self, line):
        self.print_command(self.network_api.dongle_dlms_to_tap,
                           kwargs={})

    def do_3p_meter_tap_to_dlms(self, line):
        self.print_command(self.network_api.three_ph_meter_tap_to_dlms,
                           kwargs={})

    def do_meter_dlms_to_tap(self, line):
        self.print_command(self.network_api.meter_dlms_to_tap,
                           kwargs={})

    def do_3p_turn_relay_on(self, line):
        self.print_command(self.network_api.three_ph_turn_relay_on,
                           kwargs={})

    def do_3p_turn_relay_off(self, line):
        self.print_command(self.network_api.three_ph_turn_relay_off,
                           kwargs={})
    """
    def do_3p_get_relay_status(self, line):
        self.print_command(self.network_api.three_ph_get_relay_status,
                           kwargs={})
    """
    ##########################################################################

    def do_3p_recharge(self, line):
        self.print_command(self.network_api.three_ph_recharge,
                           kwargs={"amount": int(line)})
    ##########################################################################

    def do_3p_clear_billing_log(self, line):
        self.print_command(self.network_api.three_ph_clear_billing_log,
                           kwargs={})

    def do_3p_clear_billing_history(self, line):
        self.print_command(self.network_api.three_ph_clear_billing_history,
                           kwargs={})

    def do_3p_set_MD_integration_period(self, line):
        try:
            interval = int(line)
        except:
            print ("Usage: 3p_set_MD_integration_period:value(int)")
        else:
            self.print_command(
                self.network_api.three_ph_set_MD_integration_period,
                kwargs={
                    "interval": interval})

    def do_3p_set_billing_date(self, line):
        if line == "":
            billing_timestamp = 0
        elif line.strip(' ') == "now":
            billing_timestamp = datetime.datetime.now()
        else:
            billing_timestamp = dateutil.parser.parse(line)
        self.print_command(self.network_api.three_ph_set_billing_date,
                           kwargs={"billing_timestamp": billing_timestamp})
    """
    def do_3p_get_billing_params(self, line):
        self.print_command(self.network_api.three_ph_get_billing_params,
                           kwargs={})
    """

    def do_3p_get_billing_log_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_3p_get_billing_log_by_index:value(int)")
        else:
            self.print_command(
                self.network_api.three_ph_get_billing_log_by_index,
                kwargs={
                    "index": index})

    def do_3p_get_billing_history_by_index(self, line):
        try:
            index = int(line)
        except:
            print ("Usage: do_3p_get_billing_history_by_index:value(int)")
        else:
            self.print_command(
                self.network_api.three_ph_get_billing_history_by_index,
                kwargs={
                    "index": index})

    def do_3p_print_billing_history(self, line):
        self.print_command(self.network_api.three_ph_print_billing_history,
                           kwargs={})

    def do_3p_get_num_billing_debug_logs(self, line):
        self.print_command(
            self.network_api.three_ph_get_num_billing_debug_logs,
            kwargs={})

    def do_3p_factory_init(self, line):
        self.print_command(self.network_api.three_ph_factory_init,
                           kwargs={})

    def do_3p_print_billing_log(self, line):
        self.print_command(self.network_api.three_ph_print_billing_log,
                           kwargs={})

    def do_3p_meter_dlms_to_tap(self, line):
        self.print_command(self.network_api.three_ph_meter_dlms_to_tap,
                           kwargs={})
    """
    def do_3p_get_system_params(self,line):
        self.print_command(self.network_api.three_ph_get_system_params,
                           kwargs={})
    """

    def do_3p_get_system_params_data(self, line):
        self.print_command(self.network_api.three_ph_system_params_data,
                           kwargs={})

    def do_3p_get_system_params_profile(self, line):
        self.print_command(self.network_api.three_ph_system_params_profile,
                           kwargs={})

    def do_3p_get_dlms_dbg_info(self, line):
        self.print_command(self.network_api.three_ph_get_dlms_dbg_info,
                           kwargs={})

    def do_3p_set_power_limit(self, line):
        power_limit = int(line)
        self.print_command(self.network_api.three_ph_set_power_limit,
                           kwargs={"power_limit": power_limit})

    def do_3p_set_relay_manual_control(self, line):
        self.print_command(self.network_api.three_ph_relay_manual_control,
                           kwargs={})

    def do_3p_set_relay_auto_control(self, line):
        self.print_command(self.network_api.three_ph_relay_auto_control,
                           kwargs={})

    def do_3p_get_serial_no(self, line):
        self.print_command(self.network_api.three_ph_get_serial_no,
                           kwargs={})
    """
    def do_3p_erase_flash_sector(self, line):
        flash_sector = int(line)
        self.print_command(self.network_api.three_ph_erase_flash_sector,
                           kwargs={"flash_sector":flash_sector})
    """

    def do_3p_ui_config(self, line):
        arg = line.split("\n")
        file_name = str(arg[0])
        self.print_command(self.network_api.three_ph_ui_config,
                           kwargs={"main_txt_file_path": file_name})
    """
    def do_3p_get_ext_flash_crc(self, line):
        try:
            arg = line.split(",")
            ext_flash_address = int(arg[0])
            #print "Ext Flash Address: "+str(ext_flash_address)
            length_of_payload = int(arg[1])
            #print "Pay Load Length is: "+str(length_of_payload) +" Bytes"
        except Exception as e:
            print "Usage: do_3p_get_ext_flash_crc:int(value),int(value)"
            print e
        else:
            self.print_command(self.network_api.three_ph_get_ext_flash_crc,
                           kwargs={"ext_flash_address": ext_flash_address,"length_of_payload":length_of_payload})
    """

    def do_3p_get_crc_bundle(self, line):
        try:
            arg = line.split(",")
            ext_flash_start_address = int(arg[0])
            length_of_payload = int(arg[1])
        except Exception as e:
            print ("Usage: do_3p_get_crc_bundle:int(value),int(value)")
            print (e)
        else:
            self.print_command(
                self.network_api.three_ph_get_crc_bundle,
                kwargs={
                    "ext_flash_start_address": ext_flash_start_address,
                    "length_of_payload": length_of_payload})

    def do_3p_rc_transmit_mode_on(self, line):
        self.print_command(self.network_api.rc_transmit_mode_on,
                           kwargs={})

    def do_3p_rc_transmit_mode_off(self, line):
        self.print_command(self.network_api.rc_transmit_mode_off,
                           kwargs={})

    def do_3p_mem_write(self, line):
        self.print_command(self.network_api.three_ph_mem_write,
                           kwargs={"line": line})

    def do_3p_mem_read(self, line):
        data = self.print_command(self.network_api.three_ph_mem_read,
                                  kwargs={"line": line},
                                  to_print=False)
        data_string = ""
        if data is not None:
            for ch in data:
                data_string += hex(ch) + " "
            print (data_string)

    def do_3p_mem_erase_block(self, line):
        mem_block_id = int(line)
        self.print_command(self.network_api.three_ph_mem_erase_block,
                           kwargs={"line": line})

    def do_3p_mem_erase_sector(self, line):
        mem_block_id = int(line)
        self.print_command(self.network_api.three_ph_mem_erase_sector,
                           kwargs={"line": line})

    def do_3p_get_bundle(self, line):
        self.print_command(self.network_api.three_ph_get_metering_data_bundle,
                           kwargs={})

    def do_3p_get_network(self, line):
        self.print_command(self.network_api.three_ph_get_network,
                           kwargs={})

    def do_3p_get_channel(self, line):
        self.print_command(self.network_api.three_ph_get_channel,
                           kwargs={})

    def do_3p_get_rf_power(self, line):
        self.print_command(self.network_api.three_ph_get_rf_power,
                           kwargs={})

    def do_3p_get_address(self, line):
        self.print_command(self.network_api.three_ph_get_address,
                           kwargs={})

    def do_3p_get_time(self, line):
        self.print_command(self.network_api.three_ph_get_time,
                           kwargs={})

    def do_3p_get_live_version(self, line):
        self.print_command(self.network_api.three_ph_get_live_version,
                           kwargs={})

    def do_3p_get_ext_version(self, line):
        self.print_command(self.network_api.three_ph_get_ext_version,
                           kwargs={})

    # Command related to Activity Calender
    def do_set_tod_day_profile(self, line):
        try:
            args = line
        except Exception as e:
            print ("Usage : set_tod_day_profile:1,8,200,360,540,720,900,1080,1260,1380,1,2,3,4,5,6,7,8")
            print (e)
        else:
            self.print_command(self.network_api.set_tod_day_profile,
                               kwargs={"args": args})
    
    def do_set_tod_week_profile(self, line):
        try:
            args = line
        except Exception as e:
            print ("Usage : set_tod_week_profile:4,4,SE-D,1736380800,4,WE-4")
            print (e)
        else:
            self.print_command(self.network_api.set_tod_week_profile,
                               kwargs={"args": args})
            
    def do_set_tod_season_profile(self, line):
        try:
            args = line
        except Exception as e:
            print ("Usage : set_tod_seasson_profile:1,4,WE-1,2,3,4,5,6,7")
            print (e)
        else:
            self.print_command(self.network_api.set_tod_season_profile,
                               kwargs={"args": args})
            
    def do_get_passive_calender(self, line):
        self.print_command(self.network_api.get_passive_calender,
                               kwargs={})
            
    def do_get_active_calender(self, line):
        self.print_command(self.network_api.get_active_calender,
                               kwargs={})
    
    def do_3p_set_address(self, line):
        try:
            address = Address(line)
        except Exception as e:
            print ("Usage: do_3p_set_address:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.three_ph_set_address,
                               kwargs={"address": address})

    def do_3p_set_channel(self, line):
        try:
            channel = int(line)
        except Exception as e:
            print ("Usage: do_3p_set_channel:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.three_ph_set_channel,
                               kwargs={"channel": channel})

    def do_3p_set_rf_power(self, line):
        try:
            rf_power = int(line)
        except Exception as e:
            print ("Usage: do_3p_set_rf_power:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.three_ph_set_rf_power,
                               kwargs={"rf_power": rf_power})

    def do_3p_set_network(self, line):
        try:
            network = int(line)
        except Exception as e:
            print ("Usage: do_3p_set_network:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.three_ph_set_network,
                               kwargs={"network": network})

    def do_3p_set_rc_buffer_margin(self, line):
        try:
            rc_buffer_margin = int(line)
        except Exception as e:
            print ("Usage: do_3p_set_rc_buffer_margin:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.three_ph_set_rc_buffer_margin,
                               kwargs={"rc_buffer_margin": rc_buffer_margin})

    def do_3p_set_rc_timeout(self, line):
        try:
            rc_timeout = int(line)
        except Exception as e:
            print ("Usage: do_3p_set_rc_timeout:int(value)")
            print (e)
        else:
            self.print_command(self.network_api.three_ph_set_rc_timeout,
                               kwargs={"rc_timeout": rc_timeout})

    def do_3p_rc_revert_to_factory(self, line):
        self.print_command(self.network_api.rc_revert_to_factory,
                           kwargs={})

    def do_3p_reset(self, line):
        self.print_command(self.network_api.three_ph_reset,
                           kwargs={})

    def do_3p_gateway(self, line):
        self.print_command(self.network_api.three_ph_gateway,
                           kwargs={})

    def do_3p_router(self, line):
        self.print_command(self.network_api.three_ph_router,
                           kwargs={})
#==========================================================================================#
#               Single Phase Non-dlms commands started from here.                          #
#==========================================================================================#

    def do_non_dlms_get_credit_limit(self, line):
        self.print_command(self.network_api.non_dlms_get_credit_limit,
                           kwargs={})

    def do_non_dlms_get_master_credits(self, line):
        self.print_command(self.network_api.non_dlms_get_master_credits,
                           kwargs={})

    def do_non_dlms_get_network(self, line):
        self.print_command(self.network_api.non_dlms_get_network,
                           kwargs={})

    def do_non_dlms_get_channel(self, line):
        self.print_command(self.network_api.non_dlms_get_channel,
                           kwargs={})

    def do_non_dlms_get_rf_power(self, line):
        self.print_command(self.network_api.non_dlms_get_rf_power,
                           kwargs={})

    def do_non_dlms_get_current(self, line):
        self.print_command(self.network_api.non_dlms_get_current,
                           kwargs={})

    def do_non_dlms_get_phase_current(self, line):
        self.print_command(self.network_api.non_dlms_get_phase_current,
                           kwargs={})

    def do_non_dlms_get_neutral_current(self, line):
        self.print_command(self.network_api.non_dlms_get_neutral_current,
                           kwargs={})

    def do_non_dlms_get_active_energy(self, line):
        self.print_command(self.network_api.non_dlms_get_active_energy,
                           kwargs={})

    def do_non_dlms_get_reactive_energy(self, line):
        self.print_command(self.network_api.non_dlms_get_reactive_energy,
                           kwargs={})

    def do_non_dlms_get_apparent_energy(self, line):
        self.print_command(self.network_api.non_dlms_get_apparent_energy,
                           kwargs={})

    def do_non_dlms_get_live_tampers(self, line):
        self.print_command(self.network_api.non_dlms_get_live_tampers,
                           kwargs={})

    def do_non_dlms_get_voltage(self, line):
        self.print_command(self.network_api.non_dlms_get_voltage,
                           kwargs={})

    def do_non_dlms_get_active_power(self, line):
        self.print_command(self.network_api.non_dlms_get_active_power,
                           kwargs={})

    def do_non_dlms_get_frequency(self, line):
        self.print_command(self.network_api.non_dlms_get_frequency,
                           kwargs={})

    def do_non_dlms_get_power_factor(self, line):
        self.print_command(self.network_api.non_dlms_get_power_factor,
                           kwargs={})

    # =======================================================================
    def do_non_dlms_get_net_account(self, line):
        self.print_command(self.network_api.non_dlms_get_net_account,
                           kwargs={})
    # =======================================================================

    def do_non_dlms_get_net_recharge(self, line):
        self.print_command(self.network_api.non_dlms_get_net_recharge,
                           kwargs={})

    def do_non_dlms_get_neg_recharge(self, line):
        self.print_command(self.network_api.non_dlms_get_neg_recharge,
                           kwargs={})

    def do_non_dlms_get_pos_recharge(self, line):
        self.print_command(self.network_api.non_dlms_get_pos_recharge,
                           kwargs={})

    def do_non_dlms_get_credits(self, line):
        self.print_command(self.network_api.non_dlms_get_credits,
                           kwargs={})

    def do_non_dlms_get_power_limit(self, line):
        self.print_command(self.network_api.non_dlms_get_power_limit,
                           kwargs={})

    def do_non_dlms_get_energy_limit(self, line):
        self.print_command(self.network_api.non_dlms_get_energy_limit,
                           kwargs={})

    def do_non_dlms_get_price(self, line):
        self.print_command(self.network_api.non_dlms_get_price,
                           kwargs={})

    def do_non_dlms_get_address(self, line):
        self.print_command(self.network_api.non_dlms_get_address,
                           kwargs={})

    def do_non_dlms_get_tamper_record(self, line):
        self.print_command(self.network_api.non_dlms_get_tamper_record,
                           kwargs={"tamper_type": line})

    def do_non_dlms_get_dd_params(self, line):
        self.print_command(self.network_api.non_dlms_get_dd_params,
                           kwargs={})

    def do_non_dlms_get_accounting_state(self, line):
        self.print_command(self.network_api.non_dlms_get_accounting_state,
                           kwargs={})

    def do_non_dlms_get_slab_update_ts(self, line):
        self.print_command(self.network_api.non_dlms_get_slab_update_ts,
                           kwargs={})

    def do_non_dlms_get_survey_params(self, line):
        self.print_command(self.network_api.non_dlms_get_survey_params,
                           kwargs={})

    def do_non_dlms_get_live_version(self, line):
        self.print_command(self.network_api.non_dlms_get_live_version,
                           kwargs={})

    def do_non_dlms_get_ext_version(self, line):
        self.print_command(self.network_api.non_dlms_get_ext_version,
                           kwargs={})

    def do_non_dlms_get_newest_survey(self, line):
        self.print_command(self.network_api.non_dlms_get_newest_survey,
                           kwargs={})

    def do_non_dlms_get_oldest_survey(self, line):
        self.print_command(self.network_api.non_dlms_get_oldest_survey,
                           kwargs={})

    def do_non_dlms_get_num_surveys(self, line):
        self.print_command(self.network_api.non_dlms_get_num_surveys,
                           kwargs={})

    def do_non_dlms_get_newest_log(self, line):
        self.print_command(self.network_api.non_dlms_get_newest_log,
                           kwargs={})

    def do_non_dlms_get_oldest_log(self, line):
        self.print_command(self.network_api.non_dlms_get_oldest_log,
                           kwargs={})

    def do_non_dlms_get_num_logs(self, line):
        self.print_command(self.network_api.non_dlms_get_num_logs,
                           kwargs={})

    def do_non_dlms_get_time(self, line):
        self.print_command(self.network_api.non_dlms_get_time,
                           kwargs={})

    def do_non_dlms_get_energy_consumed_today(self, line):
        self.print_command(self.network_api.non_dlms_get_energy_consumed_today,
                           kwargs={})

    def do_non_dlms_get_unlock_validity(self, line):
        self.print_command(self.network_api.non_dlms_get_unlock_validity,
                           kwargs={})

    def do_non_dlms_get_time_since_unlock(self, line):
        self.print_command(self.network_api.non_dlms_get_time_since_unlock,
                           kwargs={})

    def do_non_dlms_get_last_unlock_timestamp(self, line):
        self.print_command(self.network_api.non_dlms_get_last_unlock_timestamp,
                           kwargs={})

    def do_non_dlms_get_active_energy_offset(self, line):
        self.print_command(self.network_api.non_dlms_get_active_energy_offset,
                           kwargs={})

    def do_non_dlms_get_reactive_energy_offset(self, line):
        self.print_command(
            self.network_api.non_dlms_get_reactive_energy_offset,
            kwargs={})

    def do_non_dlms_get_apparent_energy_offset(self, line):
        self.print_command(
            self.network_api.non_dlms_get_apparent_energy_offset,
            kwargs={})

    # Fix
    def do_non_dlms_get_survey_interval(self, line):
        self.print_command(self.network_api.non_dlms_get_survey_interval,
                           kwargs={})

    def do_non_dlms_get_accurate_credits(self, line):
        self.print_command(self.network_api.non_dlms_get_accurate_credits,
                           kwargs={})

    def do_non_dlms_set_master_credits(self, line):
        self.print_command(self.network_api.non_dlms_set_master_credits,
                           kwargs={"amount": int(line)})

    def do_non_dlms_set_address(self, line):
        address = Address(line)
        self.print_command(self.network_api.non_dlms_set_address,
                           kwargs={"address": address})

    def do_non_dlms_set_channel(self, line):
        channel = int(line)
        self.print_command(self.network_api.non_dlms_set_channel,
                           kwargs={"channel": channel})

    def do_non_dlms_set_rf_power(self, line):
        rf_power = int(line)
        self.print_command(self.network_api.non_dlms_set_rf_power,
                           kwargs={"rf_power": rf_power})

    def do_non_dlms_set_network(self, line):
        network = int(line)
        self.print_command(self.network_api.non_dlms_set_network,
                           kwargs={"network": network})

    def do_non_dlms_set_rc_buffer_margin(self, line):
        margin = int(line)
        self.print_command(self.network_api.non_dlms_set_rc_buffer_margin,
                           kwargs={"margin": margin})

    def do_non_dlms_set_rc_timeout(self, line):
        rc_timeout = int(line)
        self.print_command(self.network_api.non_dlms_set_rc_timeout,
                           kwargs={"rc_timeout": rc_timeout})

    def do_non_dlms_set_power_limit(self, line):
        power_limit = int(line)
        self.print_command(self.network_api.non_dlms_set_power_limit,
                           kwargs={"power_limit": power_limit})

    def do_non_dlms_dc_cal_v1(self, line):
        voltage = int(line)
        self.print_command(self.network_api.non_dlms_dc_cal_v1,
                           kwargs={"voltage": voltage})

    def do_non_dlms_dc_cal_v2(self, line):
        voltage = int(line)
        self.print_command(self.network_api.non_dlms_dc_cal_v2,
                           kwargs={"voltage": voltage})

    def do_non_dlms_dc_cal_i(self, line):
        current = int(line)
        self.print_command(self.network_api.non_dlms_dc_cal_i,
                           kwargs={"current": current})

    def do_non_dlms_set_active_energy_offset(self, line):
        active_offset = int(line)
        self.print_command(self.network_api.non_dlms_set_active_energy_offset,
                           kwargs={"active_offset": active_offset})

    def do_non_dlms_set_reactive_energy_offset(self, line):
        reactive_offset = int(line)
        self.print_command(
            self.network_api.non_dlms_set_reactive_energy_offset, kwargs={
                "reactive_offset": reactive_offset})

    def do_non_dlms_set_apparent_energy_offset(self, line):
        apparent_offset = int(line)
        self.print_command(
            self.network_api.non_dlms_set_apparent_energy_offset, kwargs={
                "apparent_offset": apparent_offset})

    def do_non_dlms_set_credit_limit(self, line):
        credit_limit = int(line)
        self.print_command(self.network_api.non_dlms_set_credit_limit,
                           kwargs={"credit_limit": credit_limit})

    def do_non_dlms_set_energy_limit(self, line):
        energy_limit = int(line)
        self.print_command(self.network_api.non_dlms_set_energy_limit,
                           kwargs={"energy_limit": energy_limit})

    def do_non_dlms_unlock(self, line):
        unlock_validity = int(line)
        self.print_command(self.network_api.non_dlms_unlock,
                           kwargs={"unlock_validity": unlock_validity})

    def do_non_dlms_recharge(self, line):
        self.print_command(self.network_api.non_dlms_recharge,
                           kwargs={"amount": int(line)})

    def do_non_dlms_recharge_fract(self, line):
        self.print_command(self.network_api.non_dlms_recharge_fract,
                           kwargs={"amount": float(line)})

    def do_non_dlms_enable_lock(self, line):
        self.print_command(self.network_api.non_dlms_enable_lock,
                           kwargs={})

    def do_non_dlms_disable_lock(self, line):
        self.print_command(self.network_api.non_dlms_disable_lock,
                           kwargs={})

    def do_non_dlms_reset_lock(self, line):
        self.print_command(self.network_api.non_dlms_reset_lock,
                           kwargs={})

    def do_non_dlms_lock_state(self, line):
        self.print_command(self.network_api.non_dlms_lock_state,
                           kwargs={})

    def do_non_dlms_reset(self, line):
        self.print_command(self.network_api.non_dlms_reset,
                           kwargs={})

    def do_non_dlms_gateway(self, line):
        self.print_command(self.network_api.non_dlms_gateway,
                           kwargs={})

    def do_non_dlms_router(self, line):
        self.print_command(self.network_api.non_dlms_router,
                           kwargs={})

    def do_non_dlms_assert_false(self, line):
        self.print_command(self.network_api.non_dlms_assert_false,
                           kwargs={})

    def do_non_dlms_clear_nvm(self, line):
        self.print_command(self.network_api.non_dlms_clear_nvm,
                           kwargs={})

    def do_non_dlms_clear_account(self, line):
        self.print_command(self.network_api.non_dlms_clear_account,
                           kwargs={})

    def do_non_dlms_clear_recharges(self, line):
        self.print_command(self.network_api.non_dlms_clear_recharges,
                           kwargs={})

    def do_non_dlms_deassert(self, line):
        self.print_command(self.network_api.non_dlms_deassert,
                           kwargs={})

#    def do_non_dlms_turn_ui_on(self, line):
#        self.print_command(self.network_api.non_dlms_turn_ui_on,
#                           kwargs={})
#
#    def do_non_dlms_turn_ui_off(self, line):
#        self.print_command(self.network_api.non_dlms_turn_ui_off,
#                           kwargs={})

    def do_non_dlms_dc_cal_i_ofs(self, line):
        self.print_command(self.network_api.non_dlms_dc_cal_i_ofs,
                           kwargs={})

    def do_non_dlms_reset_tamper_latch(self, line):
        self.print_command(self.network_api.non_dlms_reset_tamper_latch,
                           kwargs={})

    def do_non_dlms_turn_relay_on(self, line):
        self.print_command(self.network_api.non_dlms_turn_relay_on,
                           kwargs={})

    def do_non_dlms_turn_relay_off(self, line):
        self.print_command(self.network_api.non_dlms_turn_relay_off,
                           kwargs={})

    def do_non_dlms_relay_manual_control(self, line):
        self.print_command(self.network_api.non_dlms_relay_manual_control,
                           kwargs={})

    def do_non_dlms_relay_auto_control(self, line):
        self.print_command(self.network_api.non_dlms_relay_auto_control,
                           kwargs={})

    def do_non_dlms_relay_state(self, line):
        self.print_command(self.network_api.non_dlms_relay_state,
                           kwargs={})

    def do_non_dlms_syncstream_reset(self, line):
        self.print_command(self.network_api.non_dlms_syncstream_reset,
                           kwargs={})

    def do_non_dlms_clear_log(self, line):
        self.print_command(self.network_api.non_dlms_clear_log,
                           kwargs={})

    def do_non_dlms_clear_load_survey(self, line):
        self.print_command(self.network_api.non_dlms_clear_load_survey,
                           kwargs={})

    def do_non_dlms_allow_negative_credits(self, line):
        self.print_command(self.network_api.non_dlms_allow_negative_credits,
                           kwargs={})

    def do_non_dlms_forbid_negative_credits(self, line):
        self.print_command(self.network_api.non_dlms_forbid_negative_credits,
                           kwargs={})

    def do_non_dlms_reset_tamper_record(self, line):
        self.print_command(self.network_api.non_dlms_reset_tamper_record,
                           kwargs={"tamper_type": str(line)})

    def do_non_dlms_request_recharge(self, line):
        self.print_command(self.network_api.non_dlms_request_recharge,
                           kwargs={})

    def do_non_dlms_set_price(self, line):
        price = float(line)
        self.print_command(self.network_api.non_dlms_set_price,
                           kwargs={"price": price})

    def do_non_dlms_enable_elimiter(self, line):
        self.print_command(self.network_api.non_dlms_enable_elimiter,
                           kwargs={})

    def do_non_dlms_disable_elimiter(self, line):
        self.print_command(self.network_api.non_dlms_disable_elimiter,
                           kwargs={})

    def do_non_dlms_enable_survey(self, line):
        self.print_command(self.network_api.non_dlms_enable_survey,
                           kwargs={})

    def do_non_dlms_disable_survey(self, line):
        self.print_command(self.network_api.non_dlms_disable_survey,
                           kwargs={})

    def do_non_dlms_slab_reset(self, line):
        self.print_command(self.network_api.non_dlms_slab_reset,
                           kwargs={})

    def do_non_dlms_factory_init(self, line):
        self.print_command(self.network_api.non_dlms_factory_init,
                           kwargs={})

    def do_non_dlms_set_dd_params(self, line):
        ddp = DailyDeductionParams()
        args = line.split(',')
        if (args[0].strip(' ') == "now"):
            ddp.start_time = datetime.datetime.now()
        else:
            ddp.start_time = dateutil.parser.parse(args[0])
        ddp.min_credits_per_deduction = int(args[1])
        ddp.days_per_deduction = int(args[2])
        self.print_command(self.network_api.non_dlms_set_dd_params,
                           kwargs={"ddp": ddp})

    def do_non_dlms_set_survey_params(self, line):
        args = line.split(",")
        if "now" in args[0]:
            delta = int(args[0].split("+")[1])
            start_time = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        else:
            start_time = dateutil.parser.parse(args[0].strip(' '))
        interval = int(args[1])
        status = int(args[2])

        if status != 0 and status != 1:
            print ("Status (third parameter) can only be 0 or 1!")
        else:
            lsp = LoadSurveyParamsN()
            lsp.start_time = start_time
            lsp.interval = interval
            lsp.status = status
            self.print_command(self.network_api.non_dlms_set_survey_params,
                               kwargs={"lsp": lsp})

    def do_non_dlms_set_slab_params(self, line):
        args = line
        self.print_command(self.network_api.non_dlms_set_slab_params,
                           kwargs={"args": args})

    def do_non_dlms_set_slab_update_ts(self, line):
        args = line
        self.print_command(self.network_api.non_dlms_set_slab_update_ts,
                           kwargs={"args": args})

    def do_non_dlms_slab_enable_on_update(self, line):
        self.print_command(self.network_api.non_dlms_slab_enable_on_update,
                           kwargs={})

    def do_non_dlms_slab_enable(self, line):
        self.print_command(self.network_api.non_dlms_slab_enable,
                           kwargs={})

    def do_non_dlms_slab_disable(self, line):
        self.print_command(self.network_api.non_dlms_slab_disable,
                           kwargs={})

    def do_non_dlms_fd_enable(self, line):
        self.print_command(self.network_api.non_dlms_fd_enable,
                           kwargs={})

    def do_non_dlms_fd_disable(self, line):
        self.print_command(self.network_api.non_dlms_fd_disable,
                           kwargs={})

    def do_non_dlms_fd_reset(self, line):
        self.print_command(self.network_api.non_dlms_fd_reset,
                           kwargs={})

    def do_non_dlms_set_fd_params(self, line):
        args = line
        self.print_command(self.network_api.non_dlms_set_fd_params,
                           kwargs={"args": args})

    def do_non_dlms_get_fd_update_ts(self, line):
        self.print_command(self.network_api.non_dlms_get_fd_update_ts,
                           kwargs={})

    def do_non_dlms_get_active_fd_params(self, line):
        self.print_command(self.network_api.non_dlms_get_active_fd_params,
                           kwargs={})

    def do_non_dlms_set_fd_update_ts(self, line):
        args = line
        self.print_command(self.network_api.non_dlms_set_fd_update_ts,
                           kwargs={"args": args})

    def do_non_dlms_broadcast_time(self, line):
        self.print_command(self.network_api.non_dlms_broadcast_time,
                           kwargs={})

    def do_non_dlms_syncstream_bundle(self, line):
        self.print_command(self.network_api.non_dlms_syncstream_bundle,
                           kwargs={})

    def do_non_dlms_syncstream_setup(self, line):
        interval = int(line)
        self.print_command(self.network_api.non_dlms_syncstream_setup,
                           kwargs={"interval": interval})

    def do_non_dlms_syncstream_params(self, addr):
        self.print_command(self.network_api.non_dlms_syncstream_params,
                           kwargs={})

    def do_non_dlms_beat_time(self, line):
        self.print_command(self.network_api.non_dlms_beat_time,
                           kwargs={})

    def do_non_dlms_mem_write(self, line):
        self.print_command(self.network_api.non_dlms_mem_write,
                           kwargs={"line": line})

    def do_non_dlms_mem_read(self, line):
        data = self.print_command(self.network_api.non_dlms_mem_read,
                                  kwargs={"line": line},
                                  to_print=False)
        data_string = ""
        if data is not None:
            for ch in data:
                data_string += hex(ch) + " "
            print (data_string)

    def do_non_dlms_mem_erase_block(self, line):
        mem_block_id = int(line)
        self.print_command(self.network_api.non_dlms_mem_erase_block,
                           kwargs={"line": line})

    def do_non_dlms_maxwell_cal_time(self, line):
        if line == "":
            cal_time = 0
        elif line.strip(' ') == "now":
            cal_time = datetime.datetime.now()
        else:
            cal_time = dateutil.parser.parse(line)
        self.print_command(self.network_api.non_dlms_maxwell_cal_time,
                           kwargs={"cal_time": cal_time})

    def do_non_dlms_maxwell_cal_mtrno(self, line):
        self.print_command(self.network_api.non_dlms_maxwell_cal_mtrno,
                           kwargs={"serial_num": line})

    def do_non_dlms_maxwell_clear_1(self, line):
        self.print_command(self.network_api.non_dlms_maxwell_clear_1,
                           kwargs={})

    def do_non_dlms_maxwell_clear_2(self, line):
        self.print_command(self.network_api.non_dlms_maxwell_clear_2,
                           kwargs={})

    def do_non_dlms_maxwell_cal_energy(self, line):
        self.print_command(self.network_api.non_dlms_maxwell_cal_energy,
                           kwargs={"error_percent": float(line)})

    def do_non_dlms_maxwell_cal_v(self, line):
        self.print_command(self.network_api.non_dlms_maxwell_cal_v,
                           kwargs={})

    def do_non_dlms_maxwell_cal_ip(self, line):
        self.print_command(self.network_api.non_dlms_maxwell_cal_ip,
                           kwargs={})

    def do_non_dlms_maxwell_cal_in(self, line):
        self.print_command(self.network_api.non_dlms_maxwell_cal_in,
                           kwargs={})

    def do_non_dlms_maxwell_meter_lock(self, line):
        self.print_command(self.network_api.non_dlms_maxwell_meter_lock,
                           kwargs={})

    # def do_non_dlms_maxwell_meter_unlock(self, line):
    #     self.print_command(self.network_api.non_dlms_maxwell_meter_unlock,
    #                        kwargs={"password": line})

    # def do_non_dlms_set_maxwell_meter_password(self, line):
    #     try:
    #         args = line.split(',')
    #         args[0] = int(args[0])
    #         args[1] = int(args[1])
    #     except:
    #         print "Usage: set_maxwell_meter_password:current_password(int), new_password(int)"
    #     else:
    #         if args[0] < 10000 or args[0] > 65535 or args[1] < 10000 or args[1] > 65535:
    #             print "Incorrect input! The entered passwords must be between 10000 and 65535!"
    #         else:
    #             self.print_command(self.network_api.non_dlms_set_maxwell_meter_password,
    # kwargs={"current_password": args[0],"new_password": args[1]})

    def do_non_dlms_get_meter_serial_no(self, line):
        self.print_command(self.network_api.non_dlms_get_meter_serial_no,
                           kwargs={})

    def do_non_dlms_exit(self, line):
        return True

    def do_non_dlms_use(self, line):
        self.address = Address(line)
        self.prompt = "{green}node-shell{yellow} [{address}] {blue}${white} ".\
            format(address=self.address,
                   green=Fore.GREEN,
                   yellow=Fore.YELLOW,
                   blue=Fore.BLUE,
                   white=Fore.WHITE)


    def do_non_dlms_log_print_direct(self, line):
        self.print_command(self.network_api.non_dlms_log_print_direct,
                           kwargs={})

    def do_non_dlms_log_dump_bin(self, line):
        self.print_command(self.network_api.non_dlms_log_dump_bin,
                           kwargs={})

    def do_non_dlms_log_print_bin(self, line):
        self.print_command(self.network_api.non_dlms_log_print_bin,
                           kwargs={})

    def do_non_dlms_log_header(self, line):
        self.print_command(self.network_api.non_dlms_log_header,
                           kwargs={})

    def do_non_dlms_survey_print_direct(self, line):
        self.print_command(self.network_api.non_dlms_survey_print_direct,
                           kwargs={})

    def do_non_dlms_survey_store_file(self, line):
        self.print_command(self.network_api.non_dlms_survey_store_file,
                           kwargs={})

    def do_non_dlms_survey_dump_bin(self, line):
        self.print_command(self.network_api.non_dlms_survey_dump_bin,
                           kwargs={})

    def do_non_dlms_survey_print_bin(self, line):
        self.print_command(self.network_api.non_dlms_survey_print_bin,
                           kwargs={})

    def do_non_dlms_survey_header(self, line):
        self.print_command(self.network_api.non_dlms_survey_header,
                           kwargs={})

    def do_non_dlms_survey_to_store(self, line):
        self.print_command(self.network_api.non_dlms_survey_to_store,
                           kwargs={})

#####################################################

    # rf packet mode commands
    def do_non_dlms_trace_path(self, line):
        self.print_command(self.network_api.non_dlms_trace_path,
                           kwargs={})

#   MD caommands
    def do_non_dlms_clear_MD_month(self, line):
        self.print_command(self.network_api.non_dlms_clear_MD_month,
                           kwargs={"MD_month": line})

    def do_non_dlms_get_instantaneous_MD(self, line):
        self.print_command(self.network_api.non_dlms_get_instantaneous_MD,
                           kwargs={})

    def do_non_dlms_get_current_MD(self, line):
        self.print_command(self.network_api.non_dlms_get_current_MD,
                           kwargs={})

    def do_non_dlms_get_past_MD(self, line):
        self.print_command(self.network_api.non_dlms_get_past_MD,
                           kwargs={"MD_month": line})

    def do_non_dlms_get_MD_avg_period(self, line):
        self.print_command(self.network_api.non_dlms_get_MD_avg_period,
                           kwargs={})

    def do_non_dlms_set_MD_avg_period(self, line):
        avg_period = int(line)
        self.print_command(self.network_api.non_dlms_set_MD_avg_period,
                           kwargs={"avg_period": avg_period})

    def do_non_dlms_get_MD_LCD_display(self, line):
        self.print_command(self.network_api.non_dlms_get_MD_LCD_display,
                           kwargs={})

    def do_non_dlms_set_MD_LCD_display(self, line):
        past_display = int(line)
        self.print_command(self.network_api.non_dlms_set_MD_LCD_display,
                           kwargs={"past_display": past_display})
#=========================================================================
# End of 1p non dlms commANDS
#=========================================================================

    # OYO prepaid commands ================================================
    
    def do_get_prepaid_info(self, line):
        self.print_command(self.network_api.get_prepaid_info,
                           kwargs={})

    def do_get_num_assign_deassign_logs(self, line):
        self.print_command(self.network_api.get_num_prepaid_logs,
                           kwargs={})

    def do_get_assign_deassign_logs_by_index(self, line):
        try:
            if line == "":
                index = 0
            else:
                index = int(line)
        except:
            print ("Usage: get_prepaid_logs_by_index:value(int)")
        else:
            self.print_command(self.network_api.get_prepaid_logs_by_index, kwargs={"index": index})

    def do_assign(self, line):
        self.print_command(self.network_api.assign,
                       kwargs={})

    def do_deassign(self, line):
        self.print_command(self.network_api.deassign,
                       kwargs={})        

    def do_enable_dg_tariff(self, line):
        self.print_command(self.network_api.enable_dg_tariff,
                       kwargs={})        

    def do_enable_eg_tariff(self, line):
        self.print_command(self.network_api.enable_eg_tariff,
                       kwargs={}) 


    def do_get_dg_tariff_group_info(self, line):
        self.print_command(self.network_api.get_tariff_group_info,
                           kwargs={"groupNo":int(1)})

    def do_get_eg_tariff_group_info(self, line):
        self.print_command(self.network_api.get_tariff_group_info,
                           kwargs={"groupNo":int(2)})

    def do_set_dg_tariff_params(self, line):
        try:
            args = line
        except Exception as e:            
            print (e)
        else:
            self.print_command(self.network_api.set_dg_tariff_params,
                           kwargs={"args": args})
    def do_set_eg_tariff_params(self, line):
        try:
            args = line
        except Exception as e:            
            print (e)
        else:
            self.print_command(self.network_api.set_eg_tariff_params,
                           kwargs={"args": args})

    def do_set_fd_tariff(self, line):
        try:
            args = line
        except Exception as e:            
            print (e)
        else:
            self.print_command(self.network_api.set_fd_tariff,
                           kwargs={"args": args})


def run():
    parser = OptionParser()
    parser.add_option("-d", "--device", dest="device",
                      help="gateway device file")
    parser.add_option("-t", "--timeout", dest="timeout",
                      help="uart timeout")
    parser.add_option("-b", "--baud_rate", dest="baud_rate",
                      help="baud rate")
    parser.add_option("-s", "--silent", action="store_true",
                      dest="silent", help="runs without FTDI cable")
    parser.add_option("-c", "--command", dest="command",
                      help="run command")
    parser.add_option("-m", "--mode", dest="mode",
                      help="use irda with dongle and rc_packet with dongle")
    parser.add_option("--id", "--portID", dest="portID",
                      help="device id")

    (options, args) = parser.parse_args()
    if options.device is None:
        # options.device = "COM"+str(port)
        options.device = "/dev/gp-gateway"
    if options.baud_rate is None:
        options.baud_rate = 9600
    if options.timeout is None:
        options.timeout = 3
    if options.silent is None:
        options.silent = False
    if options.command is None:
        options.command = ""
    if options.mode is None:
        options.mode = "irda" #"rc_packet"
    if options.portID is None:
        options.portID = 4
    mode = options.mode
    portID = options.portID
    ser = None
    try:
        ser = serial.Serial(options.device, int(options.baud_rate),
                            timeout=int(options.timeout))
    except (serial.serialutil.SerialException, OSError) as err:
        print(err)
        # get list of all devices connected through serial port
        comPorts = list(serial.tools.list_ports.comports())
        print ("List of devices connected on com ports : ")
        print ([b for b in comPorts])

        # get number of com ports used
        numPortsUsed = len(comPorts)
        print ("Number of com ports used in system : ", numPortsUsed)
        if not options.silent:
            sys.exit('Error: Could not open communication port')
    try:
        os.makedirs(os.path.expanduser("~/.grampower/gp_node"))
    except:
        pass
    open(os.path.expanduser("~/.grampower/gp_node/node_shell.log"), "a").close()
    network_api = NetworkAPI(ser, portID, mode)
    node_shell = NodeShell()
    node_shell.set_network_api(network_api)
    node_shell.do_use("255.255.255.255")
    if options.command != "":
        node_shell.onecmd(options.command)
    else:
        print(("\n{cyan}Gateway Device: {device}\n"
               "Baud Rate: {baud_rate}\n"
               "Device Port: {port_id}\n"
               "Time Out: {timeout}\n{white}").
              format(device=options.device,
                     baud_rate=options.baud_rate,
                     port_id=options.portID,
                     timeout=options.timeout,
                     cyan=Fore.CYAN,
                     white=Fore.WHITE))
    node_shell.cmdloop()


if __name__ == "__main__":
    # com = raw_input("Eneter the com port Number(Ex- 1,2,3 etc.) : ")
    run()
