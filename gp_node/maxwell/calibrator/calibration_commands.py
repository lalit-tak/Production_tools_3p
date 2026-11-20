"""
Used to calibrate the Maxwell board directly using the FTDI cable.
Note that the Maxwell board is calibrated by sending certain commands
to the Maxwell board on the UART line of the 12 pin connector. These
commands can be sent either by the Node Board or directly using a Python
script (by using an FTDI cable attached). In both the cases, this module
is used to get the exact command which is to be sent over the serial port.

If the Node board is used for calibrating, then the C++ MaxwellBridgeApp is used.
The payload to this application is built using this module.
This module is used by network_api to construct the appropriate for the
Maxwell Bridge protocol
"""
import datetime

# Code identifiers for calibration

TIME_DATE_CODE = 1      # To calibrate the RTC of maxwell board
MTRNO_CODE = 3          # To set the serial number of the maxwell board
CLEAR_1_CODE = 4        # To clear the calibration of the maxwell board
CLEAR_2_CODE = 85       # To clear the accumulated energy etc. of the maxwell board
ENERGY_CAL_CODE = 11    # To calibrate the power/voltage/current with a 240V, 10A supply
VICAL_CODE = 13         # To calibrate voltage,phase current & neutral current separately

def get_command_string(code, user_input=None):
    """
    Returns the byte array to be sent to the Maxwell's board to calibrate it
    (for the given code).

    :param code: should be one of CLEAR_1_CODE, CLEAR_2_CODE,\
            TIME_DATE_CODE, MTRNO_CODE, ENERGY_CAL

    :param user_input: certain calibration commands such as MTRNO_CODE requires\
            additional parameters (such as the meter serial number), which is used to
            construct the exact bytes which should be sent to the Maxwell board

    :type user_input:
            When code is MTRNO_CODE, user_input should be of type int;
            When code is TIME_DATE_CODE, user_input should be of type datetime.datetime;
            When code is CLEAR_1_CODE, user_input is ignored;
            When code is CLEAR_2_CODE, user_input is ignored;
            When code is ENERGY_CAL_CODE, user_input should be type float;

    :returns: the bytearray which should be sent to the Maxwell Board
    :rtype: bytearay
    """
    output = bytearray()
    if code in [CLEAR_1_CODE, CLEAR_2_CODE]:
        output.extend(chr(code))
        output.extend(chr(code))
    elif code in [TIME_DATE_CODE, MTRNO_CODE, ENERGY_CAL_CODE, VICAL_CODE]:
        output.extend(chr(code))
        if code == TIME_DATE_CODE:
            data = construct_command_for_cal_time(user_input)
        elif code == MTRNO_CODE:
            mtrno = int(user_input)
            data = construct_command_for_cal_mtrno(mtrno)
        elif code == ENERGY_CAL_CODE:
            error_percent = float(user_input)
            data = construct_command_for_cal_energy(error_percent)
        elif code == VICAL_CODE:
            mode = user_input
            data = construct_command_for_vi_cal(mode)
        output.extend(data)
        data_sum = sum(output) % 256
        output.extend(chr(data_sum))
    return output


def construct_command_for_cal_time(cal_time=None):
    """
    Helper function, should not be used directly

    :returns: the command to be sent to calibrate the RTC of\
            the Maxwell board.
    :rtype: bytearray
    """

    def convert(num):
        if (num >= 10):
            return (num/10)*16 + (num%10)
        else:
            return num

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


def construct_command_for_cal_mtrno(mtrno):
    """
    Helper function, should not be used directly

    :returns: the command to be sent to set the serial number\
            of the Maxwell board.
    :rtype: bytearray
    """
    data = bytearray()
    mtrno_string = "{0:0=8d}".format(int(mtrno))
    for char in bytearray(mtrno_string):
        data.extend(chr(char-0x30))
    return data

def construct_command_for_cal_energy(error_percent):
    """
    Helper function, should not be used directly

    :returns: the command to be sent to calibrate the voltage,\
            current and power of the meter. The term "cal_energy" is\
            kind of a misnomer, but that is what is the convention used\
            at Maxwell and Asdaq systems
    :rtype: bytearray
    """
    if error_percent >= 0:
        temp = int(error_percent*100)
    else:
        temp = 65536 + int(error_percent*100)
    error_string = bytearray("{0:0=8d}".format(temp))
    data = bytearray()
    for char in error_string:
        data.extend(chr(char-0x30))
    return data


def construct_command_for_vi_cal(mode):
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


