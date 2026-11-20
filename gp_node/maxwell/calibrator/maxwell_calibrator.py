"""
Implements a shell to calibrate the Maxwell board
"""
import argparse
import datetime
import cmd
import dateutil.parser
import serial
from colorama import Fore

from calibration_commands import (ENERGY_CAL_CODE, MTRNO_CODE, 
        TIME_DATE_CODE, CLEAR_1_CODE, CLEAR_2_CODE,
        get_command_string)

class MaxwellCalibrator(cmd.Cmd):

    ser = None
    prompt = "{yellow}maxwell-calibrator {blue}${white} ".\
            format(yellow=Fore.YELLOW,
                   blue=Fore.BLUE,
                   white=Fore.WHITE)

    def set_serial(self, ser):
        self.ser = ser

    def _send_command(self, code, user_input=None):
        command_string = get_command_string(code, user_input)
        self.ser.write(command_string)

    def do_cal_energy(self, line):
        """
        Calibrates energy by compensating for the given percent error

        Example: cal_energy 0

        Example: cal_energy -2.25
        """
        error_percent = float(line)
        self._send_command(ENERGY_CAL_CODE, error_percent)

    def do_clear1(self, line):
        """
        Clears all calibration. This command should be used before beginning energy calibration
        """
        self._send_command(CLEAR_1_CODE)

    def do_clear2(self, line):
        """
        Clears all accumulated energy (does not disturb the calibration)
        """
        self._send_command(CLEAR_2_CODE)

    def do_cal_time(self, line):
        """
        Calibrates the RTC of the Maxwell board

        Example: cal_time 2014-10-02 10:30:40

        Example: cal_time now
        """
        if line == "now":
            time = datetime.datetime.now()
        else:
            time = dateutil.parser.parse(line)
        self._send_command(TIME_DATE_CODE, time)

    def do_cal_mtrno(self, line):
        """
        Sets the serial number of the Maxwell board.

        Example: cal_mtrno 564
        """
        mtrno = int(line)
        self._send_command(MTRNO_CODE, mtrno)

    def do_exit(self, line):
        return True

    def emptyline(self):
        pass

def run():
    parser = argparse.ArgumentParser( \
        description="A shell to calibrate Maxwell board directly using a FTDI cable"
    );
    parser.add_argument('-d', '--device', default='/dev/gp-gateway', \
            help='Device filename of the FTDI cable. Default is /dev/gp-gateway');
    parser.add_argument('-b', '--baud', default=2400, \
            help='Baud rate to communicate with Maxwell board. Default is 2400');
    args = parser.parse_args()
    ser = serial.Serial(args.device, args.baud, timeout=3)
    calibrator = MaxwellCalibrator()
    calibrator.set_serial(ser)
    calibrator.cmdloop()

if __name__ == "__main__":
    run()
