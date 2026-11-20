from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import nottest
from nose.plugins.attrib import attr
import time
import datetime
import dateutil.parser
from gp_node.request_handler._3p_tf import RequestHandler_3P,timer
import argparse
import serial
import os
import json
import re
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._3p.flash_io import FlashIOMaster_3P, FlashIOError_3P
from gp_node.utils.address import Address
import gp_node.utils.serialize as serialize
import xml.etree.cElementTree as ET
from config import MAX_CURRENT, MIN_CURRENT, SOFTWARE_VERSION, \
    OVERPOWER_LIMIT, TOTAL_ENERGY, ENERGY_TRIES, \
    TIME_DRIFT,FACTORY_TRIES,SERIAL_NO_TRIES

class InitializeApi(object):


    def __init__(self):
        self.set_default_config()
        #self.print_current_config()
        #print self.configure_environment()
        self.meter_data = {}
        self.result_data = {}

        self.data_json = {}

    def get_result_data(self):
        print "\n\n\n sending meter_data \n\n"
        return self.meter_data

    def get_result_flag(self):
        return self.result_data

    def get_data_json(self):
        return self.data_json

    def configure_environment(self):
        try:
            self.load_config_from_xml()
        except Exception as e:
            #print e
            return "Error while opening Config File"
        try:
            self.ser = serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout= self.TIME_OUT)
            #ser.close() 
        except Exception as e:
            #print e
            msg = "Error while opening Serial Port:"
            msg = msg + str(self.SERIAL_PORT)
            return msg

        network_api = NetworkAPI(self.ser, "irda")
        self.testHandler = RequestHandler_3P(network_api)
        self.print_current_config()
        return True

    def close_serial_port(self):
        try:
            self.ser.close()
        except Exception as e:
            print e
        
    def set_default_config(self):

        # Copy config settings from xml file
        self.SERIAL_PORT = "/dev/ttyUSB0"
        self.BAUD_RATE = int(9600)
        self.TIME_OUT = 3
        self.TIME_DRIFT  = 10
        self.SOFTWARE_VERSION  = 0

        # Three Phase settings
        self.MAX_NO_LOAD_CURRENT_R_PHASE_3P = 10 #in milliAmps
        self.MAX_NO_LOAD_CURRENT_Y_PHASE_3P = 10 #in milliAmps
        self.MAX_NO_LOAD_CURRENT_B_PHASE_3P = 10 #in milliAmps

        self.MIN_LOAD_CURRENT_R_PHASE_3P = 600 #in milliAmps
        self.MIN_LOAD_CURRENT_Y_PHASE_3P = 600 #in milliAmps
        self.MIN_LOAD_CURRENT_B_PHASE_3P = 600 #in milliAmps

        self.MAX_TOTAL_REAL_ENERGY_3P  = 10 #WatHour
        self.MAX_TOTAL_APPARENT_ENERGY_3P = 10 #VAH
        self.MAX_TOTAL_REACTIVE_ENERGY_3P = 10 #VARH
        self.MAX_LAG_ONLY_REACTIVE_ENERGY_3P = 10 #VARH
        self.MAX_LEAD_ONLY_REACTIVE_ENERGY_3P = 10 #VARH

        # Single Phase settings
        self.MAX_NO_LOAD_CURRENT_1P = 10 #in milliAmps
        self.MIN_LOAD_CURRENT_1P = 600 #in milliAmps
        self.MAX_TOTAL_REAL_ENERGY_1P  = 10 #WatHour

    def load_config_from_xml(self):
        config_file = os.path.join(os.path.join(os.path.expanduser('~')), 'grampower/gp_node/gp_node/mri/config/config.xml')
        #print config_file
        #tree = ET.ElementTree(file=config_file)
        tree = ET.parse(config_file)

        #tree = ET.ElementTree(file='config.xml')
        root = tree.getroot()
        # Misc Settings
        for elem in  tree.iter(tag='PortNo'):
            self.SERIAL_PORT  = str(elem.text)

        for elem in  tree.iter(tag='BaudRate'):
            self.BAUD_RATE  = int(elem.text)

        for elem in  tree.iter(tag='TimeOut'):
            self.TIME_OUT  = int(elem.text)

        for elem in  tree.iter(tag='TimeDrift'):
            self.TIME_DRIFT  = int(elem.text)

        for elem in  tree.iter(tag='SoftwareVersion'):
            self.SOFTWARE_VERSION  = int(elem.text)

        # Three Phase settings
        for elem in  tree.iter(tag='NoLoadCurrentRPhase'):
            self.MAX_NO_LOAD_CURRENT_R_PHASE_3P  = int(elem.text)
        for elem in  tree.iter(tag='NoLoadCurrentYPhase'):
            self.MAX_NO_LOAD_CURRENT_Y_PHASE_3P  = int(elem.text)
        for elem in  tree.iter(tag='NoLoadCurrentBPhase'):
            self.MAX_NO_LOAD_CURRENT_B_PHASE_3P  = int(elem.text)   
   

        for elem in  tree.iter(tag='LoadCurrentRPhase'):
            self.MIN_LOAD_CURRENT_R_PHASE_3P  = int(elem.text)
        for elem in  tree.iter(tag='LoadCurrentYPhase'):
            self.MIN_LOAD_CURRENT_Y_PHASE_3P  = int(elem.text)
        for elem in  tree.iter(tag='LoadCurrentBPhase'):
            self.MIN_LOAD_CURRENT_B_PHASE_3P  = int(elem.text)   


        for elem in  tree.iter(tag='TotalRealEnergy'):
            self.MAX_TOTAL_REAL_ENERGY_3P  = int(elem.text)
        for elem in  tree.iter(tag='TotalApparentEnergy'):
            self.MAX_TOTAL_APPARENT_ENERGY_3P  = int(elem.text)
        for elem in  tree.iter(tag='TotalReactiveEnergy'):
            self.MAX_TOTAL_REACTIVE_ENERGY_3P  = int(elem.text)
        for elem in  tree.iter(tag='LagOnlyReactiveEnergy'):
            self.MAX_LAG_ONLY_REACTIVE_ENERGY_3P  = int(elem.text)
        for elem in  tree.iter(tag='LeadOnlyReactiveEnergy'):
            self.MAX_LEAD_ONLY_REACTIVE_ENERGY_3P  = int(elem.text)


        # Single Phase settings
        for elem in  tree.iter(tag='NoLoadCurrent'):
            self.MAX_NO_LOAD_CURRENT_1P  = int(elem.text)
        for elem in  tree.iter(tag='LoadCurrent'):
            self.MIN_LOAD_CURRENT_1P  = int(elem.text)
        for elem in  tree.iter(tag='TotalRealEnergy_1p'):
            self.MAX_TOTAL_REAL_ENERGY_1P  = int(elem.text)

    def print_current_config(self):
        print "SERIAL_PORT                     ", self.SERIAL_PORT 
        print "BAUD_RATE                       ", self.BAUD_RATE 
        print "TIME_OUT                        ", self.TIME_OUT 
        print "TIME_DRIFT                      ", self.TIME_DRIFT
        print "SOFTWARE_VERSION                ", self.SOFTWARE_VERSION
        print "MAX_NO_LOAD_CURRENT_R_PHASE_3P  ", self.MAX_NO_LOAD_CURRENT_R_PHASE_3P
        print "MAX_NO_LOAD_CURRENT_Y_PHASE_3P  ", self.MAX_NO_LOAD_CURRENT_Y_PHASE_3P
        print "MAX_NO_LOAD_CURRENT_B_PHASE_3P  ", self.MAX_NO_LOAD_CURRENT_B_PHASE_3P
        print "MIN_LOAD_CURRENT_R_PHASE_3P     ", self.MIN_LOAD_CURRENT_R_PHASE_3P
        print "MIN_LOAD_CURRENT_Y_PHASE_3P     ", self.MIN_LOAD_CURRENT_Y_PHASE_3P
        print "MIN_LOAD_CURRENT_B_PHASE_3P     ", self.MIN_LOAD_CURRENT_B_PHASE_3P
        print "MAX_TOTAL_REAL_ENERGY_3P        ", self.MAX_TOTAL_REAL_ENERGY_3P
        print "MAX_TOTAL_APPARENT_ENERGY_3P    ", self.MAX_TOTAL_APPARENT_ENERGY_3P
        print "MAX_TOTAL_REACTIVE_ENERGY_3P    ", self.MAX_TOTAL_REACTIVE_ENERGY_3P 
        print "MAX_LAG_ONLY_REACTIVE_ENERGY_3P ", self.MAX_LAG_ONLY_REACTIVE_ENERGY_3P 
        print "MAX_LEAD_ONLY_REACTIVE_ENERGY_3P", self.MAX_LEAD_ONLY_REACTIVE_ENERGY_3P
        print "MAX_NO_LOAD_CURRENT_1P          ", self.MAX_NO_LOAD_CURRENT_1P
        print "MIN_LOAD_CURRENT_1P             ", self.MIN_LOAD_CURRENT_1P
        print "MAX_TOTAL_REAL_ENERGY_1P        ", self.MAX_TOTAL_REAL_ENERGY_1P

    def send_meter_dlms_to_tap(self):
        response = self.testHandler.handle_network_request("three_ph_meter_dlms_to_tap")  
        if (response != None):
            print response
            return True
        else:
            return False

    def send_dongle_dlms_to_tap(self):
        response = self.testHandler.handle_network_request("dongle_dlms_to_tap")
        if (response != None):
            print response
            return True
        else:
            return False

    def send_clear_2_cmd(self):
        print "\n  maxwell_clear_2 called \n "
        response = self.testHandler.handle_network_request("maxwell_clear_2")
        if (response != None):
            return True
        else:
            return False

    def send_turn_relay_on_1p(self):
        response = self.testHandler.handle_network_request("turn_relay_on")
        if (response != None):
            print response
            return True
        else:
            return False

    def send_turn_relay_off_1p(self):
        response = self.testHandler.handle_network_request("turn_relay_off")
        if (response != None):
            print response
            return True
        else:
            return False

    def send_relay_manual_control_1p(self):
        response = self.testHandler.handle_network_request("relay_manual_control")
        if (response != None):
            print response
            return True
        else:
            return False

#######################################################################################
########################################extern commands###############################
######################################################################################

    def send_factory_init_1_1p(self):
        print " \n \n factory init 1 called \n \n"
        response = self.testHandler.handle_network_request("factory_init_1")
        self.my_delay(6)

        if (response =='ok'):
            print "factory_1_response",response
            return True
        else:
            return False

    def send_reset(self):
        print " \n \n reset  called \n \n "
        response = self.testHandler.handle_network_request("reset")
        if (response != None):
            print response
            return response
        else:
            return False

    def send_factory_init_2_1p(self):
        print " \n \n factory init 2 called \n \n"
        response = self.testHandler.handle_network_request("factory_init_2")
        if (response != None):
            print 'factory_init_2_response',response
            return response
        else:
            return False

    def send_get_accounting_state(self):
        response = self.testHandler.handle_network_request("get_accounting_state")
        if (response != None):
            return response
        else:
            return False

    def send_get_active_fd_params(self):
        response = self.testHandler.handle_network_request("get_active_fd_params")
        if (response != None):
            return response
        else:
            return False
    
    def send_get_accurate_credits(self):
        response = self.testHandler.handle_network_request("get_accurate_credits")
        if (response != None):
            return response
        else:
            return False

    def send_get_credit_limit(self):
        response = self.testHandler.handle_network_request("get_credit_limit")
        if (response != None):
            return response
        else:
            return False

    def send_get_fd_update_ts(self) :
        response = self.testHandler.handle_network_request("get_fd_update_ts")
        if (response != None):
            return response
        else:
            return False

    def send_get_slab_update_ts(self) :
        response = self.testHandler.handle_network_request("get_slab_update_ts")
        if (response != None):
            return response
        else:
            return False

    def send_get_pos_recharge(self) :
        response = self.testHandler.handle_network_request("get_pos_recharge")
        if (response != None):
            return response
        else:
            return False

    def send_get_neg_recharge(self) :
        response = self.testHandler.handle_network_request("get_neg_recharge")
        if (response != None):
            return response
        else:
            return False

    def send_get_net_recharge(self) :
        response = self.testHandler.handle_network_request("get_net_recharge")
        if (response != None):
            return response
        else:
            return False

    def send_get_power_limit(self) :
        response = self.testHandler.handle_network_request("get_power_limit")
        if (response != None):
            return response
        else:
            return False

    def send_relay_state(self) :
        response = self.testHandler.handle_network_request("relay_state")
        if (response != None):
            return response
        else:
            return False

    def send_get_tamper_record_all(self) :
        response = self.testHandler.handle_network_request("get_tamper_record:all")
        if (response != None):
            return response
        else:
            return False

    def send_get_cumulative_tamper_count(self) :
        response = self.testHandler.handle_network_request("get_cumulative_tamper_count")
        if (response != None):
            return response
        else:
            return False

    def send_get_tamper_logger_period(self) :
        response = self.testHandler.handle_network_request("get_tamper_logger_period")
        if (response != None):
            return response
        else:
            return False

    def send_get_num_event_record(self) :
        response = self.testHandler.handle_network_request("get_num_event_record")
        if (response != None):
            return "numbers of events recorded",response
        else:
            return False

    def send_get_cumulative_programming_count(self) :
        response = self.testHandler.handle_network_request("get_cumulative_programming_count")
        if (response != None):
            return response
        else:
            return False

    def send_get_billing_date_all(self) :
        response = self.testHandler.handle_network_request("get_billing_date:all")
        if (response != None):
            return response
        else:
            return False

    def send_get_billing_timestamp(self) :
        response = self.testHandler.handle_network_request("get_billing_timestamp")
        if (response != None):
            return response
        else:
            return False

    def send_get_billing_power_on_time_all(self) :
        response = self.testHandler.handle_network_request("get_billing_power_on_time:all")
        if (response != None):
            return response
        else:
            return False

    def send_get_system_power_factor_all(self) :
        response = self.testHandler.handle_network_request("get_system_power_factor:all")
        if (response != None):
            return response
        else:
            return False

    def send_get_cumulative_billing_count(self) :
        response = self.testHandler.handle_network_request("get_cumulative_billing_count")
        if (response != None):
            return response
        else:
            return False

    def send_get_cumulative_power_on_time(self) :  
        response = self.testHandler.handle_network_request("get_cumulative_power_on_time")
        if (response != None):
            return response
        else:
            return False

    def send_get_power_failure_duration(self) :
        response = self.testHandler.handle_network_request("get_power_failure_duration")
        if (response != None):
            return response
        else:
            return False

    def send_get_power_failure_count(self) :
        response = self.testHandler.handle_network_request("get_power_failure_count")
        if (response != None):
            return response
        else:
            return False

    def send_get_MD_avg_period(self) :
        response = self.testHandler.handle_network_request("get_MD_avg_period")
        if (response != None):
            return response
        else:
            return False

    def send_get_block_load_profile_params(self) :
        response = self.testHandler.handle_network_request("get_block_load_profile_params")
        if (response != None):
            return response
        else:
            return False

    def send_get_num_block_load_profile(self) :
        response = self.testHandler.handle_network_request("get_num_block_load_profile")
        if (response != None):
            return response
        else:
            return False

    def send_get_num_daily_load_profile(self) :
        response = self.testHandler.handle_network_request("get_num_daily_load_profile")
        if (response != None):
            return response
        else:
            return False

    def seconds_between(self,d1, d2,aw):
        d1 = datetime.datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
        d2 = datetime.datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
        differ = abs(d2 - d1)
        seconds = 86400 * (differ.days) + (differ.seconds)
        if aw > seconds:
            return True
        else:
            return False

    def send_set_address_1p(self,address):
        command = '{}{}'.format('set_address:',address)
        print command
        response = self.testHandler.handle_network_request(command)
        if (response != None):
            print response
            return True
        else:
            return False

#######################################################################################
######################################################################################
######################################################################################

#######################################################################################
#####################################  VERIFICATION  ##################################
#######################################################################################

    def verify_tariff_slab(self):
        response_acc_state = self.send_get_accounting_state()
        response_slab_up_ts = self.send_get_slab_update_ts()

        print 'response_acc_state', response_acc_state
        print 'response_slab_up_ts', response_slab_up_ts

        self.data_json['get_accounting_state'] = response_acc_state
        self.data_json['get_accounting_state'] = response_slab_up_ts

        packet_str = str(response_acc_state)
        arg = packet_str.split("\n")
        ip_params = []
        for line_number in arg:
            try:
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)

        print 'tariff : ', ip_params

        p1 = (int(ip_params[1]) == 6)
        p2 = (map(int, ((" ".join(re.findall("[0-9]+", ip_params[2]))).split(' ')))) == [100, 200, 300, 400, 500, 600]
        p3 = (map(int, ((" ".join(re.findall("[0-9]+", ip_params[3]))).split(' ')))) == [1, 2, 3, 4, 5]
        p3 = int(ip_params[4].split(' ')[0]) == 0
        p4 = int(ip_params[6].split(' ')[0]) == 0
        p5 = int(ip_params[7].split(' ')[0]) == 1
        p6 = ip_params[-1].split(' ')[-1] == 'disabled'

        p7 = str(response_slab_up_ts) == '1970-01-01 00:00:00'

        total_result = (p1 and p2 and p3 and p4 and p5 and p6 and p7)

        result_dict = dict(zip(['no_of_slabs', 'slab_price',
                                'slab_limits', 'Monthly Minimum Charges',
                                'enabled_slab', 'enabled_slab_set',
                                'slab disabled'],
                               [p1, p2, p3, p4, p5, p6, p7]))

        if (total_result) != False:
            print 'Tariff Slab Verified'
            return True
        else:
            print 'Tariff Slab Not Verified : ',[key for key, value in result_dict.items() if value == False]
            return False

    def verify_fixed_deduction(self):
        response_actv_fd_ps = self.send_get_active_fd_params()
        response_fd_up_ts = self.send_get_fd_update_ts()

        self.data_json['get_active_fd_params'] = response_actv_fd_ps
        self.data_json['get_fd_update_ts'] = response_fd_up_ts

        packet_str = str(response_actv_fd_ps)
        arg = packet_str.split("\n")
        ip_params = []
        for line_number in arg:
            try:
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)

        p1 = int(ip_params[0].split(' ')[0]) == 0
        p2 = ip_params[1] == 'monthly'
        p3 = ip_params[2] == 'disabled'
        p4 = int(ip_params[3]) == 1

        p5 = str(response_fd_up_ts) == '1970-01-01 00:00:00'

        total_result = p1 and p2 and p3 and p4 and p5

        result_dict = dict(zip(['amount','type_of_deduction',
                                'fixed deduction is',
                                'Enabled fd set','get_fd_update_ts'],
                               [p1, p2, p3, p4, p5]))

        if (total_result) != False:
            print 'Fixed Deduction Verified'
            return True
        else:
            print 'Fixed Deduction Verified : ',[key for key, value in result_dict.items() if value == False]
            return False

    def verify_prepaid(self):
        response_acc_crdt = self.send_get_accurate_credits()
        response_crdt_limit = self.send_get_credit_limit()

        self.data_json['get_accurate_credits'] = response_acc_crdt
        self.data_json['get_credit_limit'] = response_crdt_limit

        packet_str = str(response_acc_crdt)
        arg = packet_str.split("\n")
        ip_params = []
        for line_number in arg:
            try:
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)

        print 'prepaid : ', ip_params
        print 'credit  : ', response_crdt_limit

        p1 = ip_params[0] == 'true'
        p2 =  100 >= int(ip_params[1]) >= 99
        p3 = int(ip_params[2].split(' ')[0]) == 90000
        p4 = 100 >= int(float(ip_params[3])) >= 99

        p5 = int(response_crdt_limit.split(' ')[0]) == 0

        total_result = p1 and p2 and p3 and p4 and p5

        result_dict = dict(zip(['allow_negative_credits',
                                'whole_credit','energy_per_credit',
                                'accurate_credits',
                                'fractional_energy_remaining'],
                               [p1, p2, p3, p4, p5]))

        if (total_result) != False:
            print 'Prepaid Verified'
            return True
        else:
            print 'Prepaid Not Verified : ',[key for key, value in result_dict.items() if value == False]
            return False

    def verify_recharge(self):
        response_pos_re = int(float(self.send_get_pos_recharge()))
        response_neg_re = int(float(self.send_get_neg_recharge()))
        response_net_re = int(float(self.send_get_net_recharge()))

        self.data_json['get_pos_recharge'] = response_pos_re
        self.data_json['get_neg_recharge'] = response_neg_re
        self.data_json['get_net_recharge'] = response_net_re

        p1 = response_pos_re == 0
        p2 = response_neg_re == 0
        p3 = response_net_re == 0

        total_result = p1 and p2 and p3

        result_dict = dict(zip(['get_pos_recharge',
                                'get_neg_recharge',
                                'get_net_recharge'],
                               [p1, p2, p3]))

        if (total_result) != False:
            print 'Recharge Verified'
            return True
        else:
            print 'Recharge Not Verified : ',[key for key, value in result_dict.items() if value == False]
            return False

    def verify_power_limiter(self):

        response_pwr_limit = self.send_get_power_limit()

        self.data_json['get_power_limit'] = response_pwr_limit

        print 'power_limiter : ',response_pwr_limit

        total_result = int(response_pwr_limit.split(' ')[0]) == OVERPOWER_LIMIT

        if (total_result) != False:
            print 'Power Limiter Verified'
            return True
        else:
            print 'Power Limiter Not Verified'
            return False

    def check_live_tamper(self):
        response_live_tamper = self.send_get_live_tamper_1p()
        self.data_json['get_live_tamper_1p'] = response_live_tamper
        result = response_live_tamper == '[]'        
        print 'live_tamper_present',result,response_live_tamper
        if result != False:
            print 'no live tamper'
            return True
        else:
            print 'live tamper present'
            return False

    def verify_tamper_record(self):

        response_tmpr_rcrd = self.send_get_tamper_record_all()
        response_cu_tmpr_cnt = self.send_get_cumulative_tamper_count()
        response_tmpr_lgr_pd = self.send_get_tamper_logger_period()
        response_live_tamper = self.send_get_live_tamper_1p()

        print 'response_tmpr_rcrd',response_tmpr_rcrd
        print 'response_cu_tmpr_cnt',response_cu_tmpr_cnt
        print 'response_tmpr_lgr_pd',response_tmpr_lgr_pd
        print 'response_live_tamper',response_live_tamper
        print 'response_live_tamper string type',type(response_live_tamper)

        self.data_json['get_tamper_record_all'] = response_tmpr_rcrd
        self.data_json['get_cumulative_tamper_count'] = response_cu_tmpr_cnt
        self.data_json['get_tamper_logger_period'] = response_tmpr_lgr_pd
        self.data_json['get_live_tamper_1p'] = response_live_tamper

        p1 = int(response_cu_tmpr_cnt) == 0

        print p1

        packet_str = str(response_tmpr_rcrd)
        arg = packet_str.split("\n")
        ip_params = []
        for line_number in arg:
            try:
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)

        p2 = ip_params.count('1970-01-01 00:00:00') == 12

        print p2

        p3 = int(response_tmpr_lgr_pd.split(' ')[0]) == 180

        print p3

        p4 = response_live_tamper == '[]'

        print 'p4',p4

        if p4:
            self.meter_data['live_tampers'] = '  []'
            # self.meter_data['live_tampers'] = 'No Tamper'
        else:
            self.meter_data['live_tampers'] = response_live_tamper

        # p4 = len(self.data_json['get_live_tamper_1p']) == 0

        total_result = p1 * p2 * p3 * p4

        result_dict = dict(zip(['get_tamper_record:all',
                                'get_cumulative_tamper_count',
                                'get_tamper_logger_period'
                                'get_live_tampers'],
                               [p1, p2, p3, p4]))

        if (total_result) != False:
            print 'Tamper record Verified'
            return True
        else:
            print 'Tamper record Not Verified : ', [key for key, value in result_dict.items() if value == False]
            return False

    def verify_event_record(self):
        time.sleep(10)
        response_num_evnt_rcd = self.send_get_num_event_record()
        response_cu_prgm_cnt = self.send_get_cumulative_programming_count()

        print "\n \n programming count :",response_cu_prgm_cnt

        self.data_json['get_tamper_record_all'] = response_num_evnt_rcd
        self.data_json['get_cumulative_programming_count'] = response_cu_prgm_cnt
        print "type>>>", type(response_num_evnt_rcd)
        packet_str = str(response_num_evnt_rcd[1])
        print "type of packet>>>", type(packet_str), len(packet_str), packet_str
        arg = packet_str.split('\n')
        print 'arg',len(arg),arg
        ip_params = []
        print "arg",arg
        for line_number in arg:
            try:
                print line_number,"\n"
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)
        print ip_params, len(ip_params)
        p1 = int(ip_params[-2]) == 2
        p2 = int(float(response_cu_prgm_cnt)) == 0

        total_result = p1 * p2

        result_dict = dict(zip(['get_num_event_record',
                                'get_cumulative_programming_count'],
                               [p1, p2]))

        if (response_cu_prgm_cnt and response_num_evnt_rcd) != False:
            print 'Event record Verified'
            self.meter_data['num_event_record'] = int(ip_params[-2])
            return True
        else:
            print 'Event record Verified : ',[key for key, value in result_dict.items() if value == False]
            return False



    def verify_billing(self):
        response_b_date = self.send_get_billing_date_all()
        response_b_ts = self.send_get_billing_timestamp()
        response_b_pwr_on_time = self.send_get_billing_power_on_time_all()
        response_s_pwr_fctr = self.send_get_system_power_factor_all()
        response_cu_b_cnt = self.send_get_cumulative_billing_count()
        response_cu_pwr_on_time = self.send_get_cumulative_power_on_time()
        response_pwr_fail_cnt = self.send_get_power_failure_count()
        response_pwr_fail_dur = self.send_get_power_failure_duration()
        response_md_avg_pd = self.send_get_MD_avg_period()
        self.data_json['get_billing_date_all'] = response_b_date
        self.data_json['get_billing_timestamp'] = response_b_ts
        self.data_json['get_billing_power_on_time_all'] = response_b_pwr_on_time
        self.data_json['get_system_power_factor_all'] = response_s_pwr_fctr
        self.data_json['get_cumulative_billing_count'] = response_cu_b_cnt
        self.data_json['get_cumulative_power_on_time'] = response_cu_pwr_on_time
        self.data_json['get_power_failure_count'] = response_pwr_fail_cnt
        self.data_json['get_power_failure_duration'] = response_pwr_fail_dur
        self.data_json['get_MD_avg_period'] = response_md_avg_pd

        packet_str = str(response_b_date)
        arg = packet_str.split("\n")
        ip_params = []

        for line_number in arg:
            try:
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)

        for i in ip_params[1:]:
            if i == '1970-01-01 00:00:00':
                p1 = True
            else:
                p1 = False

        if self.seconds_between(str(ip_params[0]), str(self.send_get_time()),120):
            p1 = True
        else:
            p1 = False

        response_time_stamp = str(self.send_get_time())
        date = datetime.datetime.strptime(response_time_stamp, "%Y-%m-%d %H:%M:%S")
        date = date.replace(minute=00, hour=00, second=00, month=(date.month) + 1, day=01)

        self.meter_data['next_billing_date'] = str(date)

        p2 = (str(date) == response_b_ts)

        packet_str = str(response_b_pwr_on_time)
        arg = packet_str.split("\n")
        ip_params = []

        for line_number in arg:
            try:
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)

        print 'ip_params for get power failure duration', ip_params

        for i in ip_params[1:-1]:
            if i == '0 d 0 h 0 m 0 s':
                p3 = True
            else:
                p3 = False
        
        d={}

        b= ip_params[0].split(' ')

        for i in range(0,len(b),2):
            d[b[i+1]]=i

        total_seconds = d['d']*24*60*60 + d['h']*60*60 + d['m']*60 + d['s']

        if total_seconds > 300:
            p3 = True
        else:
            p3 = False

        packet_str = str(response_s_pwr_fctr)
        arg = packet_str.split("\n")
        ip_params = []

        print 'power',packet_str

        for line_number in arg:
            try:
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)

        for i in ip_params[1:-1]:
            if int(float(i)) == 0:
                p4 = True
            else:
                p4 = False

        if int(float(ip_params[0])) == 1:
            p4 = True
        else:
            p4 = False
        
        if ((int(float(ip_params[0])) <= 1) and (int(float(ip_params[0] > 0)))):
            p4 = True
        else:
            p4 = False

        p5 = int(float(response_cu_b_cnt)) == 0

        self.meter_data['cu_billing_cnt'] = int(float(response_cu_b_cnt))

        b = str(response_cu_pwr_on_time).split(' ')

        for i in range(0, len(b), 2):
            d[b[i + 1]] = int(b[i])

        total_seconds = d['d'] * 24 * 60 * 60 + d['h'] * 60 * 60 + d['m'] * 60 + d['s']

        print 'Cumulative power on time :', total_seconds

        if total_seconds < 180:
            p6 = True
        else:
            p6 = False

        d = {}

        b = str(response_pwr_fail_dur).split(' ')

        print 'get_power_failure_duration', d

        print 'timers ', b

        for i in range(0, len(b), 2):
            d[b[i + 1]] = int(b[i])

        total_seconds = d['h'] * 60 * 60 + d['m'] * 60 + d['s']

        print 'total_time : ', total_seconds

        if total_seconds <= 15:
            p7 = True
        else:
            p7 = False

        p8 = int(float(response_pwr_fail_cnt)) == 1
        p9 = int(float(response_md_avg_pd.split(' ')[0])) == 30

        self.meter_data['DIP'] = int(float(response_md_avg_pd.split(' ')[0]))

        print p1, p2, p3, p4, p5, p6, p7, p8, p9

        total_result = p1 * p2 * p3 * p4 * p5 * p6 * p7 * p8 * p9

        result_dict = dict(zip(['get_billing_date:all',
                                'get_billing_timestamp',
                                'get_billing_power_on_time:all',
                                'get_system_power_factor:all',
                                'get_cumulative_billing_count',
                                'get_cumulative_power_on_time',
                                'get_power_failure_duration',
                                'get_power_failure_count',
                                'get_MD_avg_period'],
                               [p1, p2, p3, p4, p5, p6, p7, p8, p9]))

        if (total_result) != False:
            print 'Billing Verified'
            return True
        else:
            print 'Billing Not Verified : ',[key for key, value in result_dict.items() if value == False]
            return False

    def verify_block_load_profile(self):
        print "verifying the block load data ....."
        response_blk_ld_pfle = self.send_get_block_load_profile_params()
        response_num_blk_ld_pfle = self.send_get_num_block_load_profile()
        resopnse_daily_ld_prfle = self.send_get_num_daily_load_profile()

        self.data_json['get_block_load_profile_params'] = response_blk_ld_pfle
        self.data_json['get_num_block_load_profile'] = response_num_blk_ld_pfle
        self.data_json['get_num_daily_load_profile'] = resopnse_daily_ld_prfle

        packet_str = str(response_blk_ld_pfle)
        arg = packet_str.split("\n")
        ip_params = []
        for line_number in arg:
            try:
                ip_params.append((line_number.split(": ")[1]).strip(' '))
            except Exception as e:
                ip_params.append(line_number)
        print "p1 check ip_params[0]",ip_params[0],ip_params[1]
        dte=datetime.datetime.now()
        dte=dte.replace(hour=0,minute=0,second=0,microsecond=0)
        p1 = (ip_params[0] == (datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S'))) or (ip_params[0] == str(dte))  # neeeds to be changed
        p2 = int(ip_params[1]) == 30
        self.meter_data['SIP'] = int(ip_params[1])
        # p3 = ip_params[2].split(' ')[1] == 'enabled'
        print "p4 check get_num_blk_ld_profile",response_num_blk_ld_pfle
        p4 = int(response_num_blk_ld_pfle) <= 48

        self.meter_data['NoOfSurveysGenerated'] = int(response_num_blk_ld_pfle)
        print "get num daily ld prfle",resopnse_daily_ld_prfle,'\n\n\n'
        p5 = int(resopnse_daily_ld_prfle) == 0

        total_result = p1 and p2 and p4 and p5

        result_dict = dict(zip(['get_block_load_profile_params : start time',
                                'get_block_load_profile_params : interval',
                                'get_block_load_profile_params : status'
                                'get_num_block_load_profile',
                                'get_num_daily_load_profile'],
                               [p1, p2, p4, p5]))
        print "p1 p2 p4 p5 ",p1,p2,p4,p5
        print "total_results", total_result
        if (total_result) != False:
            print 'Block Load Profile Verified'
            self.meter_data['num_profile'] = int(resopnse_daily_ld_prfle)
            return True
        else:
            print 'Block Load Profile Verified and found Failed : ',[key for key, value in result_dict.items() if value == False]
            return False

#######################################################################################
######################################################################################
######################################################################################


    def send_get_address_1p(self):
        response = self.testHandler.handle_network_request("get_address")
        if (response != None):
            print response
            return True
        else:
            return False

    def verify_address_1p(self,address):
        response = self.testHandler.handle_network_request("get_address")
        if (response != None):
            # self.data_json['get_address']=response
            print response
            if (address == response):
                print "address are equal"
                self.meter_data['address']=response
                return True
            else:
                print "Address are not equal"
                return False

    def send_get_soft_version_1p(self):
        response = self.testHandler.handle_network_request("get_live_version")
        self.meter_data['soft_ver'] = response
        if (int(response) in SOFTWARE_VERSION):
            print "software version =",response
            return True
        else:
            return False

    def send_extra_ones(self):
        list_f_cmd = ['daily_load_profile_print_direct',
                      'get_current_active_MD',
                      'get_current_apparent_MD',
                      'get_current_reactive_MD',
                      'get_past_active_MD:all',
                      'get_past_apparent_MD:all',
                      'Get_active_energy_history:all',
                      'Get_apparent_energy_history:all',
                      'get_cumulative_programming_count']

        for i in list_f_cmd:
            try:
                response = str(self.testHandler.handle_network_request(i))
                self.data_json[i] = response
            except Exception as e:
                pass

        print self.data_json





    def send_get_live_tamper_1p(self):
        response = self.testHandler.handle_network_request("get_live_tampers")
        self.meter_data['live_tampers'] = response
        if (response != []):
            print response
            return response
        else:
            return None

    def send_set_meter_ser_no_3p(self, ser_no):

        self.data_json['serial'] = ser_no
        command = '{}{}'.format('maxwell_cal_mtrno:', ser_no)
        print command
        response = self.testHandler.handle_network_request(command)
        time.sleep(1)
        if (response != None):
            print response
            return True
        else:
            return False

    def verify_meter_ser_no_1p(self, ser_num):
        response = self.testHandler.handle_network_request("get_meter_serial_no")
        self.meter_data['serial_no'] = response
        if (response != None):
            print response,ser_num
            if(response == ser_num):
                print "ser num are equal"
                return True
            else:
                print "ser num are not equal"
                return False
        else:
            return False

    def send_get_meter_ser_no_1p(self):
        response = self.testHandler.handle_network_request("get_meter_serial_no")
        if (response != None):
            print response
            return True
        else:
            return False

    
    def update_fatcory_init_time(self):
        print " \n \n update_fatcory_init_time called \n \n"
        response = self.testHandler.handle_network_request("three_ph_meter_dlms_to_tap", no_of_tries=3)
        response = self.testHandler.handle_network_request("dongle_dlms_to_tap", no_of_tries=3)    
        response = self.testHandler.handle_network_request("get_1p_metering_data", no_of_tries=2)
        if (response != None):
            energy_packet_str = str(response)
            arg = energy_packet_str.split("\n")
            energy_params = []
            try:
                for line_number in range(0, 10):
                    energy_params.append(arg[line_number].split(": ")[1])
            except Exception as e:
                print e
            self.meter_data['factory_init_time'] = datetime.datetime.strptime(str(energy_params[8]),'%Y-%m-%d %H:%M:%S')
            print "factory_init_time  :",self.meter_data['factory_init_time']
        else:
            print "unable to fetch response for get_1p_metering_data"
            return False
            


    def verify_energy_reset_1p(self):
        print " \n \n 1p_metering_data called \n \n"
        response = self.testHandler.handle_network_request("get_1p_metering_data", no_of_tries=2)
        if (response != None):
            #print response
            #print profile_params_str
            energy_packet_str = str(response)
            #print profile_params_str
            arg = energy_packet_str.split("\n")
            energy_params = []
            try:
                for line_number in range(0, 10):
                    energy_params.append(arg[line_number].split(": ")[1])
            except Exception as e:
                print e
            values = energy_params[5].split(" ")[0]
            active_energy = float(values)

            values = energy_params[6].split(" ")[0]
            reactive_energy = float(values)

            values = energy_params[7].split(" ")[0]
            apparent_energy = float(values)

            self.meter_data['factory_init_time'] = datetime.datetime.strptime(str(energy_params[8]),'%Y-%m-%d %H:%M:%S')
            
            real_total_energy = int(active_energy + reactive_energy + apparent_energy)

            print active_energy, reactive_energy, apparent_energy

            self.meter_data['real_energy'] = active_energy
            self.meter_data['reactive_energy'] = reactive_energy
            self.meter_data['apparant_energy'] = apparent_energy

            if(active_energy != 0):
                return False
            if(reactive_energy != 0):
                return False
            if(apparent_energy != 0):
                return False
            if (active_energy >= 0) and (active_energy <= TOTAL_ENERGY):
                print 'Energy Correct'
                return True
            else:
                return False
        else:
            return False


    def verify_load_presence_1p(self):
        response = self.testHandler.handle_network_request("get_1p_metering_data")
        print ' load test output ',response
        if (response != None):
            print response
             #print profile_params_str
            instantanious_packet_str = str(response)
            arg = instantanious_packet_str.split("\n")
            ip_params = []
            try:
                for line_number in range(0,10):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                    ip_params.append(arg[line_number].split(": ")[1])
            except Exception as e:
                print e

            values = ip_params[1].split(" ")[0]
            current = float(values)

            print 'current : ',current
            print "MAX, Min",MAX_CURRENT,MIN_CURRENT
            if ( current <= MAX_CURRENT ) and ( current >= MIN_CURRENT ) :
                return True, response
            else:
                return False
        else:
            return False


    def verify_no_load_current_1p(self):
        response = self.testHandler.handle_network_request("get_1p_metering_data")
        if (response != None):
            print response
             #print profile_params_str
            instantanious_packet_str = str(response)
            arg = instantanious_packet_str.split("\n")
            ip_params = []
            try:
                for line_number in range(0,10):
                    ip_params.append(arg[line_number].split(": ")[1])
            except Exception as e:
                print e

            values = ip_params[1].split(" ")[0]
            current = float(values)

            print "\n\n\ncurrent in no load test is :",current

            if(current == 0.0):
                return True
            else:
                return False
        else:
            return False

    def send_get_time(self):
        response = self.testHandler.handle_network_request("get_time", no_of_tries=2)
        self.data_json['meter_time'] = response 
        if (response != None):
            print response
            return response
        else:
            return False

    def send_set_current_time(self):
        response = self.testHandler.handle_network_request("maxwell_cal_time:now", no_of_tries=2)
        if (response != None):
            print "rsponse for setting current system time:",response
        #     return response
        # else:
        #     return False

    def send_get_drift_time(self):

        response = str(self.testHandler.handle_network_request("get_time", no_of_tries=2))
        print 'get_time : ', response
        date = datetime.datetime.strptime(response, "%Y-%m-%d %H:%M:%S")
        Endtime = datetime.datetime.now()
        duration = int((Endtime - date).total_seconds())
        print 'time duration : ', duration
        print " system time for time drift calculation:",Endtime
        # self.meter_data['system_time'] = Endtime 
        self.data_json['system_time'] = str(Endtime)
        self.data_json['meter_time'] = str(response)
        self.meter_data['Drift'] = duration

        if (abs(duration) <= TIME_DRIFT):
            print response
            return True
        else:
            print "time drift not in range"
            return False

    def get_time(self):
        response = self.testHandler.handle_network_request("get_time", no_of_tries=2)
        if (response != None):
            print response
            return True
        else:
            return False

    def my_delay(self,delay):
        now = time.time()
        #print round(now)
        start_time = int(round(now))
        #print start_time
        delay = int(delay)
        #print "delay",delay
        flag = True
        while flag:
            current_time = time.time()
            #print current_time
            current_time = int(round(current_time))
            #print current_time
            if((current_time - start_time)>=delay):
                flag = False

    def populate_result(self):
        result_data = ''
        result_flag = ''
        for key in self.meter_data:
            #result_data += str(key)+':'+str(self.meter_data[key])+','
            result_data += str(self.meter_data[key])+','

        for key in self.result_data:
            #result_flag += str(key)+':'+str(self.result_data[key])+','
            result_flag += str(self.result_data[key])+','
        
        print result_data
        print result_flag

        resu = result_data + result_flag
        return resu
