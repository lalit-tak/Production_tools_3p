import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._3p.flash_io import FlashIOMaster_3P, FlashIOError_3P
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json
import datetime

START_ADDRESS = 0x100

def erase_flash(flash_io):
    packet_retry_cnt = 0
    for i in range(0,32):
        retry = True
        while retry:
            try:
                flash_io.erase(Address("0.0.0.255"), i)
            except FlashIOError_3P as err:
                #print err
                packet_retry_cnt = packet_retry_cnt+1
                retry = True
            else:
                print i*64*1024 ,"Bytes Erased"
                retry = False
    if (os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')
    print i*64, "KB Erased" 
    

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
        args.device = "/dev/gp-gateway"
    if args.baud_rate is None:
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 1

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, "irda")
    starttime = datetime.datetime.now()

    print "DLMS to TAP"
    print network_api.three_ph_meter_dlms_to_tap(Address("0.0.0.255"))
    #erase_flash(network_api.my_flash_io_master_3p)

    def get_time():
        retry = True
        while retry:
            try:
                meter_time = network_api.three_ph_get_time(Address("0.0.0.255"))
            except Exception as inst:
                #print err
                retry = True
            else:
                retry = False
        return meter_time


    def change_meter_time(time_in_seconds = 0):
        meter_time = get_time()

        unix_time_zero = datetime.datetime(1970, 1, 1)
        seconds_since_epoch = int((meter_time - unix_time_zero).total_seconds())
        print seconds_since_epoch
        print "Sending maxwell cal time"
        nine_hours_from_now = meter_time + datetime.timedelta(seconds = 86400)
        print network_api.maxwell_cal_time(Address("0.0.0.255"), nine_hours_from_now)




    retry = True
    while retry:
        try:
            #print network_api.three_ph_factory_init(Address("0.0.0.255"))
            pass
        except Exception as inst:
                #print err
            retry = True
            pass
        else:
            print "Factory Init Done"
            retry = False

    change_meter_time()

    EndTime = datetime.datetime.now()
    print "StartTime:",starttime
    print "EndTime:",EndTime
    print "Diff : ", EndTime - starttime


if __name__ == "__main__":
    run()
