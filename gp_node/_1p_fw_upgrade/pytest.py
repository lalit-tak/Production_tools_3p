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

# print Angles[3]
# print CosTable[4]

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

def set_whole_phase_shift_p(shift):
    shift = int(shift)
    if(shift>20):
        return
    cal_params = get_cal_params()
    cal_params['pVoltageShift']  = int(shift)
    update_cal_params(cal_params)

def set_whole_phase_shift_n(shift):
    shift = int(shift)
    if(shift>20):
        return
    cal_params = get_cal_params()
    cal_params['nVoltageShift']  = int(shift)
    update_cal_params(cal_params)

def set_fractional_phase_shift_p(shift):
    cal_params = get_cal_params()
    voltage_frac_shift = int(cal_params['voltagePreload'])
    shift = int(shift)
    if((shift>255) or (shift<voltage_frac_shift)):
        return
    cal_params['pCurrentPreload']  = int(shift)
    update_cal_params(cal_params)

def set_fractional_phase_shift_n(shift):
    cal_params = get_cal_params()
    voltage_frac_shift = int(cal_params['voltagePreload'])
    shift = int(shift)
    if((shift>255) or (shift<voltage_frac_shift)):
        return
    cal_params['nCurrentPreload']  = int(shift)
    update_cal_params(cal_params)

def set_fractional_voltage_shift(shift):
    cal_params = get_cal_params()
    shift = int(shift)
    if(shift>255):
        return
    cal_params['voltagePreload']  = int(shift)
    update_cal_params(cal_params)


def get_p_active_power(metering_params_str):
    pActivePower = 0
    metering_params_str = str(metering_params_str)
    arg = metering_params_str.split("\n")
    profile_params = []
    try:
        for line_number in range(0,17):
            profile_params.append(arg[line_number].split(": ")[1])
        pActivePower = float(profile_params[6].split(' ')[0])*100
    except Exception as e:
        print e
    return pActivePower


def get_n_active_power(metering_params_str):
    nActivePower = 0
    metering_params_str = str(metering_params_str)
    arg = metering_params_str.split("\n")
    profile_params = []
    try:
        for line_number in range(0,17):
            profile_params.append(arg[line_number].split(": ")[1])
        nActivePower = float(profile_params[7].split(' ')[0])*100
    except Exception as e:

        print e
    return nActivePower


def get_p_apparent_power(metering_params_str):
    pAppPower = 0
    metering_params_str = str(metering_params_str)
    arg = metering_params_str.split("\n")
    profile_params = []
    try:
        for line_number in range(0,17):
            profile_params.append(arg[line_number].split(": ")[1])
        pAppPower = float(profile_params[8].split(' ')[0])*100
    except Exception as e:
        print e
    return pAppPower


def get_n_apparent_power(metering_params_str):
    nAppPower = 0
    metering_params_str = str(metering_params_str)
    arg = metering_params_str.split("\n")
    profile_params = []
    try:
        for line_number in range(0,17):
            profile_params.append(arg[line_number].split(": ")[1])
        nAppPower = float(profile_params[9].split(' ')[0])*100
    except Exception as e:
        print e
    return nAppPower
def get_dummy_metering_string():
    string = "date & time                   : 2018-04-23 14:39:50.583000\n"+\
    "Phase Voltage                 : 224.37 V\n"+\
    "Phase Current                 : 6.0 mA\n"+\
    "Neutral current               : 8.0 mA\n"+\
    "Phase Pf                      : 0.0\n"+\
    "Neutral Pf                    : 0.0\n"+\
    "Phase Active Power            : 100000.12 W\n"+\
    "Neutral Active Power          : -0.12 W\n"+\
    "Phase Apparent Power          : 1.34 VA\n"+\
    "Neutral Apparent Power        : 1.79 VA\n"+\
    "Phase Reactive Power          : 0.0 VAr\n"+\
    "Neutral Reactive Power        : 0.0 VAr\n"+\
    "Active Energy                 : 0.0025 KWH\n"+\
    "Reactive  Energy              : 0.0 KVARH\n"+\
    "Apparent  Energy              : 0.0 KVAH\n"+\
    "Tampers                       : 1 \n"+\
    "Frequency                     : 50.94Hz\n"
    return string


def process_phase():
    return
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
        args.timeout = 3.0

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, "irda")
    starttime = datetime.datetime.now()
    print network_api.dongle_dlms_to_tap(Address('0.0.0.255'))
    print network_api.meter_dlms_to_tap(Address('0.0.0.255'))
    print network_api.meter_dlms_to_tap(Address('0.0.0.255'))
    print network_api.meter_dlms_to_tap(Address('0.0.0.255'))

    cal_params = get_cal_params()
    RefApparentPower = cal_params['calibVoltage']*cal_params['calibCurrent']
    WHOLE_SHIFT_P = 15
    set_fractional_voltage_shift(128)
    set_whole_phase_shift_n(WHOLE_SHIFT_P)
    set_whole_phase_shift_p(0)
    PowerLimit = CosTable[WHOLE_SHIFT_P-1]
    shift = 130
    step = 1
    nActivePower = 0
    while (shift<256):
        try:
            metering_params_str = network_api.get_ip_metering_data(Address('0.0.0.255'))
            # print metering_params_str
            set_fractional_phase_shift_n(shift)
            shift = shift + step
            nActivePower = get_n_active_power(metering_params_str)
            print shift, nActivePower, (nActivePower/RefApparentPower)*100000,PowerLimit*10000
            print network_api.set_calib_params(Address('0.0.0.255'))
            time.sleep(5)

        except Exception as e:
            print e

 
    print cal_params

    RefApparentPower = cal_params['calibVoltage']*cal_params['calibCurrent']
    # print RefApparentPower
    # print cal_params
if __name__ == "__main__":
    run()