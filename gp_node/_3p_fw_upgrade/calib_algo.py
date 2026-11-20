import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io import FlashIOMaster, FlashIOError
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json
import datetime
import time


Angles = {0:0, 1:4.39453125, 2:8.7890625, 3:13.18359375, 4:17.578125, 5:21.97265625, 6:26.3671875,
            7:30.76171875, 8:35.15625, 9:39.55078125, 10:43.9453125, 11:48.33984375, 12:52.734375,
            13:57.12890625, 14:61.5234375, 15:65.91796875, 16:70.3125, 17:74.70703125, 18:79.1015625,
            19:83.49609375, 20:87.890625 }

CosTable = {0 :1, 1:0.99706007, 2:0.988257568, 3:0.97364425, 4:0.95330604, 5:0.927362526, 6:0.89596625,
            7:0.859301818,  8:0.817584813,  9:0.771060524,  10:0.720002508, 11:0.664710978, 12:0.605511041,
            13:0.542750785, 14:0.47679923, 15:0.408044163, 16:0.336889853, 17:0.263754679, 18:0.189068664,
            19:0.113270952, 20:0.036807223}



def get_cal_params():
    data_file = open('C:\Users\Shahul\Desktop\calib.json','r')
    cal_params = json.load(data_file)
    data_file.close()
    return cal_params

def update_cal_params(cal_params):
    data_file = open('C:\Users\Shahul\Desktop\calib.json','w')
    data = json.dumps(cal_params)
    data_file.write(data)
    data_file.close()

def program_p(step=2):

    #desktop =  os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    #path = os.path.join(os.path.join(desktop), 'calib.json')
    data_file = open('C:\Users\Shahul\Desktop\calib.json','r')
    cal_params = json.load(data_file)
    data_file.close()
    temp = int(cal_params['pCurrentPreload'])
    temp = temp + step
    if(temp>255):
        return 256
    cal_params['pCurrentPreload'] = cal_params['pCurrentPreload']+step
    data_file = open('C:\Users\Shahul\Desktop\calib.json','w')
    data = json.dumps(cal_params)
    data_file.write(data)
    data_file.close()
    # print cal_params
    return cal_params['pCurrentPreload']

def program_n(step=2):

    #desktop =  os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    #path = os.path.join(os.path.join(desktop), 'calib.json')
    data_file = open('C:\Users\Shahul\Desktop\calib.json','r')
    cal_params = json.load(data_file)
    data_file.close()
    temp = int(cal_params['nCurrentPreload'])
    temp = temp + step
    if(temp>255):
        return 256
    cal_params['nCurrentPreload'] = cal_params['nCurrentPreload']+step
    data_file = open('C:\Users\Shahul\Desktop\calib.json','w')
    data = json.dumps(cal_params)
    data_file.write(data)
    data_file.close()
    # print cal_params
    return cal_params['nCurrentPreload']

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action="store", dest="device", 
                        type=str, help="device name, eg. /dev/ttyUSB0")
    parser.add_argument('-b', action="store", dest="baud_rate", 
                        type=str, help="baud rate")
    parser.add_argument('-p', action="store", dest="hex_file", 
                        help="programs new hex file")
    parser.add_argument('-V', action="store", dest="version", 
                        help="options are 'live' and 'ext'")
    parser.add_argument('-t', action="store", dest="timeout", 
                        help="port time out")
    args = parser.parse_args()
    if args.device is None:
        args.device = "com16"
    if args.baud_rate is None:
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 0.6

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, "irda")
    starttime = datetime.datetime.now()
    print network_api.dongle_dlms_to_tap(Address('0.0.0.255'))
    print network_api.meter_dlms_to_tap(Address('0.0.0.255'))
    print network_api.meter_dlms_to_tap(Address('0.0.0.255'))
    
    data_file = open('C:\Users\Shahul\Desktop\calib.json','r')
    cal_params = json.load(data_file)
    data_file.close()
    print cal_params.keys()
    log_file = open('C:\Users\Shahul\Desktop\calib_log.csv','w+')
    log_file.write('pVoltageShift,nVoltageShift,pCurrentPreload,nCurrentPreload,pActivePower,nActivePower,pAppPower,nAppPower,\n')
    while (program_n(6)<256):
        try:
            print network_api.set_calib_params(Address('0.0.0.255'))
        except Exception as e:
            print e
        

        data_file = open('C:\Users\Shahul\Desktop\calib.json','r')
        cal_params = json.load(data_file)
        data_file.close()
        log_file.write(str(cal_params['pVoltageShift']))
        log_file.write(',')
        log_file.write(str(cal_params['nVoltageShift']))
        log_file.write(',')
        log_file.write(str(cal_params['pCurrentPreload']))
        log_file.write(',')
        log_file.write(str(cal_params['nCurrentPreload']))
        log_file.write(',')
        
        # print network_api.meter_dlms_to_tap(Address('0.0.0.255'))
        time.sleep(1)

        try:
            pActivePower = 0
            nActivePower = 0
            pAppPower = 0
            nAppPower = 0

            metering_params_str = network_api.get_ip_metering_data(Address('0.0.0.255'))
            print metering_params_str
            metering_params_str = str(metering_params_str)
            arg = metering_params_str.split("\n")
            profile_params = []
            try:
                for line_number in range(0,17):
                    profile_params.append(arg[line_number].split(": ")[1])
            except Exception as e:
                print e
            pActivePower = float(profile_params[6].split(' ')[0])*100
            nActivePower = float(profile_params[7].split(' ')[0])*100
            pAppPower = float(profile_params[8].split(' ')[0])*100
            nAppPower = float(profile_params[9].split(' ')[0])*100

            log_file.write(str(float(profile_params[6].split(' ')[0])*100))
            log_file.write(',')
            log_file.write(str(float(profile_params[7].split(' ')[0])*100))
            log_file.write(',')
            log_file.write(str(float(profile_params[8].split(' ')[0])*100))
            log_file.write(',')
            log_file.write(str(float(profile_params[9].split(' ')[0])*100))
            log_file.write(',\n')
        except Exception as e:
            print e
        
        

    log_file.close()
    EndTime = datetime.datetime.now()
    
    print "StartTime:",starttime
    print "EndTime:",EndTime
    print "Diff : ", EndTime - starttime


if __name__ == "__main__":
    run()
