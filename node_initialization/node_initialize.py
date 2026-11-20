#!/usr/bin/python
import cmd
import inspect
import sys
import logging
import os
import os.path
import pprint
import colorama
import serial
import datetime
import time
import dateutil.parser
from colorama import Fore
from optparse import OptionParser
from gp_node.network.network_api import NetworkAPI, NetworkAPIError
from gp_node.utils.address import Address
from gp_node.network.protocols.packets.daily_deduction_params import DailyDeductionParams
from gp_node.network.protocols.packets.load_survey_params import LoadSurveyParams
from gp_node.network.circular_log.log_reader import LogReader



ADDRESS = Address("0.0.0.255")

     

def run():
    parser = OptionParser()
    parser.add_option("-d", "--device", dest="device",
                      help="gateway device file")
    parser.add_option("-t", "--timeout", dest="timeout",
                      help="uart timeout")
    parser.add_option("-b", "--baud_rate", dest="baud_rate",
                      help="baud rate")
    parser.add_option("-f", "--command_file_path", dest="command_file_path",
                      help="command_file_path")
    parser.add_option("-s", "--start_address", dest="start_address",
                      help="start_address")
    (options, args) = parser.parse_args()
    if options.device is None:
        options.device = "/dev/gp-gateway"
    if options.baud_rate is None:
        options.baud_rate = 38400
    if options.timeout is None:
        options.timeout = 3
    if options.command_file_path is None:
        options.command_file_path = "command.txt"
    if options.start_address is not None:
        auto_addressing_enable = True
        try:
            start_address = Address(options.start_address) 
        except Exception as e:
            print e
    else:
        auto_addressing_enable = False

                

    command_file = open("command.txt", "r")
    data_from_file = command_file.read()

    command_list = data_from_file.rstrip().split('\n')
    
    try:
        ser = serial.Serial(options.device, int(options.baud_rate),
            timeout=int(options.timeout))
    except (serial.serialutil.SerialException, OSError) as err:
        print(err)
        sys.exit('Error: Could not open communication port')

    networkApi = NetworkAPI(ser)

    should_continue = True

    while(should_continue):
        print "------------------------start-------------------------------------"
        address_offset = input("Enter the meter address offset: ")
                
        try:
            current_meter_address = Address()
            d = start_address.address_string.split('.')
            temp = (int(d[0])<<24)+(int(d[1])<<16)+(int(d[2])<<8)+(int(d[3])<<0)
            current_meter_address.load_from_integer(temp + int(address_offset))
        except Exception as e:
            print e
            return

        networkApi.set_address(ADDRESS,current_meter_address)

        for command in command_list:
            try:
                print command   
                print networkApi.handle_function_request(ADDRESS,command)
            except NetworkAPIError as e:
                print e    
            time.sleep(0.5)
    
        if(raw_input("Continue with more meters y/n: ") is 'n'):
            should_continue = False
     
    print "---------------------------end----------------------------"       
 
   
if __name__ == "__main__":
    run() 
 
