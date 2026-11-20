from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import nottest
from nose.plugins.attrib import attr
import time
import datetime
import dateutil.parser
from _3p_tf import RequestHandler_3P,timer
import datetime
import argparse
import serial
import os
import argparse
import json
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._3p.flash_io import FlashIOMaster_3P, FlashIOError_3P
from gp_node.utils.address import Address
import gp_node.utils.serialize as serialize




def set_meter_time(testHandler):
    response = testHandler.handle_network_request("get_time")
    if (response != None):
        if not isinstance(response, datetime.datetime):
            response = dateutil.parser.parse(response)
    else:
        return
    #time_temp =datetime.strptime(response[0], '%Y-%m-%d')
    unix_time_zero = datetime.datetime(1970, 1, 1)
    seconds_since_epoch = int((response - unix_time_zero).total_seconds())
    temp = seconds_since_epoch%86400
    seconds_since_epoch = seconds_since_epoch - temp
    seconds_since_epoch = seconds_since_epoch + 86390
    seconds_since_epoch = 86400 + seconds_since_epoch
    new_time =  datetime.timedelta(seconds = seconds_since_epoch)
    new_time =  unix_time_zero+new_time
    strt = '{}{}'.format('maxwell_cal_time:',new_time)
    print strt
    print testHandler.handle_network_request(strt)
    while True:
        response = testHandler.handle_network_request("get_time",10)
        if (response != None):
            if not isinstance(response, datetime.datetime):
                response = dateutil.parser.parse(response)
                if(new_time < response):
                    print "time set"
                    break



    
def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action="store", dest="device", 
                        type=str, help="device name, eg. /dev/ttyUSB0")
    parser.add_argument('-b', action="store", dest="baud_rate", 
                        type=str, help="baud rate")

    parser.add_argument('-t', action="store", dest="timeout", 
                        help="port time out")
    args = parser.parse_args()
    if args.device is None:
        args.device = "COM6"
    if args.baud_rate is None:
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 1

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, "irda")
    starttime = datetime.datetime.now()

    print "DLMS to TAP"
    print network_api.three_ph_meter_dlms_to_tap(Address("0.0.0.255"))
    print network_api.dongle_dlms_to_tap(Address("0.0.0.255"))
    #erase_flash(network_api.my_flash_io_master_3p)
    testHandler = RequestHandler_3P(network_api)
    #print  testHandler.handle_network_request("get_time")
    network_api.dongle_dlms_to_tap(Address("0.0.0.255"))
    for i in range(0,1000):
        network_api.three_ph_meter_dlms_to_tap(Address("0.0.0.255"))
        
        print "Iteration No:",i,"-------------------------------------------------"
        #print network_api.three_ph_set_survey_interval(Address("0.0.0.255"),15)
        #print network_api.three_ph_set_MD_integration_period(Address("0.0.0.255"),15)
        #set_meter_time(testHandler)
        #time.sleep(20)
        print testHandler.handle_network_request("three_ph_system_params_profile")
        #print testHandler.handle_network_request("three_ph_system_params_data")
        print testHandler.handle_network_request("three_ph_reset",no_of_tries=1)
        time.sleep(20)
        




    EndTime = datetime.datetime.now()
    print "StartTime:",starttime
    print "EndTime:",EndTime
    print "Diff : ", EndTime - starttime


if __name__ == "__main__":
    run()



