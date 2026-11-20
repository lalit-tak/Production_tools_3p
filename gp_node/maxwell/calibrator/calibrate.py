import argparse
import binascii
import datetime
import serial

# Code identifiers

TIME_DATE_CODE = 1
MTRNO_CODE = 3
CLEAR_1_CODE = 4
CLEAR_2_CODE = 85
CUPOEN_CODE = 14
INST_CODE = 80
ENERGY_CAL_CODE = 11
VICAL_CODE = 13


# Communication port settings

BAUD_RATE = 2400

def get_command_string(code, user_input=None):
    """
    Returns the byte array to be sent to the Maxwell's board
    """
    print "test 1"
    output = bytearray()
    if code in [CLEAR_1_CODE, CLEAR_2_CODE, CUPOEN_CODE]:
        output.extend(chr(code))
        output.extend(chr(code))
    elif code in [TIME_DATE_CODE, MTRNO_CODE, ENERGY_CAL_CODE, VICAL_CODE]:
        output.extend(chr(code))
        if code == TIME_DATE_CODE:
            data = get_time_date_data(user_input)
        elif code == MTRNO_CODE:
            mtrno = int(user_input)
            data = get_mtrno_data(mtrno)
        elif code == ENERGY_CAL_CODE:
            power_error = float(user_input)
            data = get_energy_cal_data(power_error)
        elif code == VICAL_CODE:
            print "foo"
            mode = user_input
            data = get_vical_data(mode)
        output.extend(data)
        data_sum = sum(output) % 256
        output.extend(chr(data_sum))
    return output


def get_time_date_data(cal_time=None):
    """
    Expected format is 'DD/MM/YY hh:mm:yy'
    """
    if cal_time is None:
        cal_time = datetime.datetime.now()
    data = bytearray()
    data.extend(chr(convert(cal_time.day)))
    data.extend(chr(convert(cal_time.month)))
    data.extend(chr(convert(cal_time.year%100)))
    data.extend(chr(convert(cal_time.hour)))
    data.extend(chr(convert(cal_time.minute)))
    data.extend(chr(convert(cal_time.second)))
    return data

def convert(num):
    if (num >= 10):
        return (num/10)*16 + (num%10)
    else:
        return num

def get_mtrno_data(mtrno):
    data = bytearray()
    mtrno_string = "{0:0=8d}".format(int(mtrno))
    for char in bytearray(mtrno_string):
        data.extend(chr(char-0x30))
    return data

def get_vical_data(mode):
    if mode not in ["v", "ip", "in"]:
        raise ValueError("Incorrect mode")
    data = bytearray()
    for i in range(7):
        data.append(chr(0))
    if mode == "v":
        data.append(chr(1))
    if mode == "ip":
        data.append(chr(2))
    if mode == "in":
        data.append(chr(4))
    return data

def get_energy_cal_data(power_error):
    """
    Always use 0 for power_error
    This necessarily assumes 240V and 10A source.
    It won't work for any other voltage or current source (+-10% error)
    """
    if power_error >= 0:
        temp = int(power_error*100)
    else:
        temp = 65536 + int(power_error*100)
    error_string = bytearray("{0:0=8d}".format(temp))
    data = bytearray()
    for char in error_string:
        data.extend(chr(char-0x30))
    return data

def run():
    parser = argparse.ArgumentParser( \
        description="Used to calibrate Maxwell board directly using a FTDI cable"
    );
    parser.add_argument('-d', '--device', default='/dev/gp-gateway', \
            help='The serial device to which Node is atached.');
    parser.add_argument('-b', '--baud', default=2400, \
            help='Baud rate of serial device');
    parser.add_argument('-c', '--code', default='vical', \
            help='Calibration code: options are vi, energy, clear1, clear2, time, mtrno');
    parser.add_argument('-v', '--value', default=None, \
            help='Value to be passed along with the code');
    args = parser.parse_args()
    ser = serial.Serial("/dev/gp-gateway", 2400, timeout=3)
    code_table = {'vical': VICAL_CODE, 'energy': ENERGY_CAL_CODE, 'clear1': CLEAR_1_CODE, 
                  'clear2': CLEAR_2_CODE, 'time': TIME_DATE_CODE, 'mtrno': MTRNO_CODE}
    command_string = get_command_string(code_table[args.code], args.value)
    for entry in command_string:
        print entry
    ser.write(command_string)


if __name__ == "__main__":
    run()
