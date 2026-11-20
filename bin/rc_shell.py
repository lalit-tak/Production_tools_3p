import serial
import sys
import time
from gp_node.utils import Address
import os
from optparse import OptionParser


class RCShell:


    def __init__(self, ser, standalone=False):
        self.ser = ser
        self.standalone = standalone
        self.ser.flushInput();
        self.ser.flushOutput();
        self.commands = { \
            "reset": {"actions": {"do": self.do_reset}}, \
            "set_ack": {"actions": {"do": self.do_set_ACK}}, \
            "config": {"actions": {"do": self.do_config_mode}}, \
            "gateway": {"actions": {"do": self.set_gateway_mode}}, \
            "router": {"actions": {"do": self.set_router_mode}}, \
            "network": {"actions": {"set": self.set_network, "get": self.get_network}, "range": "(0-255)"}, \
            "margin": {"actions": {"set": self.set_margin, "get": self.get_margin}, "range": "(0-120)"}, \
            "timeout": {"actions": {"set": self.set_timeout, "get": self.get_timeout}, "range": "(1-25255)"}, \
            "channel": {"actions": {"set": self.set_channel, "get": self.get_channel}, "range": "(1-15)"}, \
            "strength": {"actions": {"get": self.get_signal_strength}}, \
            "temp": {"actions": {"get": self.get_temp}}, \
            "factory": {"actions": {"do": self.set_factory_default}}, \
            "tx_carrier": {"actions": {"do": self.do_tx_carrier}}, \
            "tx_power": {"actions": {"set": self.set_tx_power, "get": self.get_tx_power}, "range": "(-20, -10, 0, 5, 10)"}, \
            "exit": {"actions": {"do": self.exit_config_mode}}, \
            "packet_mode":{"actions":{"do":self.do_packet_mode}},\
            "transparent_mode":{"actions":{"do":self.do_transparent_mode}},\
            "address":{"actions":{"set":self.set_address,"get":self.get_address}},\
            "help": {"actions": {"do": self.print_help}}}; \

        self.action_symbols = { \
            "get": "?", \
            "set": "=[value]", \
            "do": ""};

    def generate_reset_string(self):
        return self.generate_command(0x0);

    def enter_config_mode(self):
        if self.standalone:
            print("Assuming device is in config mode (--standalone).");
        else:
            self.ser.write(self.generate_command(0xC));
            # This sleep is a hack...when the device first goes into config
            # mode it spits out a bunch of ">" characters, so we're waiting
            # for those to be done before getting into the actual work.
            # Need to investigate.
            print("Processing... (please wait for 1 seconds)");
            time.sleep(1.0);
        
        self.ser.flushInput();
        self.ser.flushOutput();

    def generate_command(self, command_code):
        command_string = '';
        for i in range(1, 65):
            command_string += chr(i);
        command_string += chr(command_code) + chr(command_code);
        return command_string;

    def set_byte(self, address, value):
        time.sleep(0.1);
        self.ser.write("M");
        time.sleep(0.1);
        self.ser.write(chr(address));
        self.ser.write(chr(value));
        self.ser.write(chr(0xFF));
        time.sleep(0.1);

    def get_byte(self, address):
        to_return = 0;
        time.sleep(0.1);
        self.ser.write("Y" + chr(address));
        time.sleep(0.1);
        try:
            to_return = ord(self.ser.read(self.ser.inWaiting())[0]);
        except:
            print("Error. was the gateway put into config mode ?")
            return None
        return to_return;


    def do_config_mode(self, arg):
        self.enter_config_mode();
        return "(Entered config mode.)";

    def do_reset(self, arg):
        self.ser.write(self.generate_reset_string());
        return "(Reset done.)";

    def set_gateway_mode(self, arg):
        self.enter_config_mode();
        time.sleep(0.1);
        self.ser.write("G");
        time.sleep(0.1);
        self.ser.write("X");
        return "(Gateway mode set.)";

    def set_router_mode(self, arg):
        self.enter_config_mode();
        time.sleep(0.1);
        self.ser.write("R");
        time.sleep(0.1);
        self.ser.write("X");
        return "(Router mode set.)";

    def set_network(self, arg):
        network = int(arg)
        self.enter_config_mode();
        self.set_byte(0x31, network);
        self.ser.write("X");
        return "(Network set to " + str(network) + ".)";

    def get_network(self, arg):
        network = [0, 0, 0, 0];
        base_addr = 0x31;
        self.enter_config_mode();
        for i in range(0, 4):
            network[i] = self.get_byte(base_addr + i);
        self.ser.write("X");
        return network;

    def set_margin(self, arg):
        margin = int(arg)
        self.enter_config_mode();
        self.set_byte(59, margin);
        self.ser.write("X");
        return "(Margin set to " + str(margin) + ".)";

    def get_margin(self, arg):
        margin = 0
        self.enter_config_mode();
        margin = self.get_byte(59);
        self.ser.write("X");
        return margin;

    def set_timeout(self, arg):
        timeout = int(arg)
        self.enter_config_mode();
        self.set_byte(timeout, timeout);
        self.ser.write("X");
        return "(Timeout set to " + str(timeout) + ".)";

    def get_timeout(self, arg):
        timeout = 0
        self.enter_config_mode();
        timeout = self.get_byte(13);
        self.ser.write("X");
        return timeout;

    def set_channel(self, arg):
        channel = int(arg);
        self.enter_config_mode();
        self.set_byte(0x00, channel);
        self.ser.write("X");
        return "(Channel set to " + str(channel) + ".)";

    def do_set_ACK(self, arg):
        self.enter_config_mode();
        self.set_byte(0x3A, 17);
        self.ser.write("X");
        return "(ACK set to )";

    def get_channel(self, arg):
        self.enter_config_mode();
        channel = self.get_byte(0x00);
        self.ser.write("X");
        return channel;

    def get_signal_strength(self, arg):
        self.enter_config_mode();
        self.ser.write("S");
        time.sleep(0.1);
        try:
            strength = ord(self.ser.read(self.ser.inWaiting())[0]) / 2;
        except:
            print("Error. was the gateway put into config mode ?")
            return None
        self.ser.write("X");
        return "-" + str(strength) + " dBm";

    def get_temp(self, arg):
        self.enter_config_mode();
        self.ser.write("U");
        time.sleep(0.1);
        try:
            temp = ord(self.ser.read(self.ser.inWaiting())[0]) - 128;
        except:
            print("Error. was the gateway put into config mode ?")
            return None
        self.ser.write("X");
        return str(temp) + " C";

    def get_address(self,arg):
        address = [0, 0, 0, 0];
        base_addr = 45;
        self.enter_config_mode();
        for i in range(0, 4):
            address[i] = self.get_byte(base_addr + i);
        self.ser.write("X");
        return address;

    def set_address(self,arg):
        address = arg.split('.')
        address = [int(x) for x in address]
        base_addr = 45
        self.enter_config_mode();
        for i in range(0, 4):
            self.set_byte(base_addr + i ,address[i]);
        self.ser.write("X");
        return "(Address set to " + str(address) + ".)";
        return

    def set_factory_default(self, arg):
        self.enter_config_mode();
        time.sleep(0.1);
        self.ser.write("@TM");
        time.sleep(0.1);
        self.ser.write("X");
        return "(Factory default set.)";

    def do_packet_mode(self,arg):
        self.enter_config_mode()
        time.sleep(0.1)
        self.set_byte(3,0)
        time.sleep(0.1)
        while(self.ser.read()=='>'):
            print('>')
        byte = self.get_byte(3)
        time.sleep(0.1)
        self.ser.write("X")

        if(byte == 0):
            return "(in packet mode)"
        else:
            print(byte)
            return "(failed)"

    def do_transparent_mode(self,arg):
        self.enter_config_mode()
        time.sleep(0.1)
        self.set_byte(3,1)
        time.sleep(0.1)
        while(self.ser.read()=='>'):
            print('>')
        byte = self.get_byte(3)
        time.sleep(0.1)
        self.ser.write("X")

        if(byte == 1):
            return "(in transparent mode)"
        else:
            print(byte)
            return "(failed)"

    def do_tx_carrier(self, arg):
        self.enter_config_mode();
        time.sleep(0.1);
        self.ser.write("1");
        time.sleep(0.1);
        try:
            input("(Transmitting carrier. Press enter to stop and exit...)");
        except:
            self.ser.write("X");
            return "(Carrier off.)";
        self.ser.write("X");
        return "(Carrier off.)";

    def set_tx_power(self, arg):
        power = 0;
        if (int(arg) == -20):
            power = 1;
        elif (int(arg) == -10):
            power = 2;
        elif (int(arg) == 0):
            power = 3;
        elif (int(arg) == 5):
            power = 4;
        elif (int(arg) == 10):
            power = 5;
        else:
            return "(Invalid argment. Valid power levels are " + self.commands["tx_power"]["range"] + ").";
        self.enter_config_mode();   
        self.set_byte(0x01, power);
        self.ser.write("X");
        return "(TX power set to " + arg + " dBm.)";

    def get_tx_power(self, arg):
        power = None;
        self.enter_config_mode();
        raw_power = self.get_byte(0x01);
        self.ser.write("X");
        if raw_power == 1:
            power = -20;
        elif raw_power == 2:
            power = -10;
        elif raw_power == 3:
            power = 0;
        elif raw_power == 4:
            power = 5;
        elif raw_power == 5:
            power = 10;
        else:
            return "(Power value returned was invalid: " + str(raw_power) + ")";
        return str(power) + " dBm";

    def exit_config_mode(self, arg):
        self.ser.write("X");
        return "(Exited config mode.)";

    def print_help(self, arg):
        for command in sorted(self.commands.keys()):
            valid_forms = "";
            for symbol in sorted([self.action_symbols[action] for action in self.commands[command]["actions"]]):
                valid_forms += command + symbol + " ";
            if "range" in self.commands[command]:
                valid_forms += "\n   " + self.commands[command]["range"];
            print(valid_forms);

    def execute(self, input_string):
        if (len(sys.argv) > 1):
            token = input_string;
            command = "";
            action = "";
            argument = "";
            if (token[-1] == "?"):
                command = token[0:-1];
                action = "get";
            elif "=" in token:
                command = token.partition("=")[0];
                action = "set";
                argument = token.partition("=")[2];
            else:
                command = token;
                action = "do"; 
            if command in self.commands:
                if action in self.commands[command]["actions"]:
                    print(self.commands[command]["actions"][action](argument));
                else:
                    print("Can't " + action + " \"" + command + "\". You can only:");
                    for valid_action in self.commands[command]["actions"]:
                        print("\t" + valid_action + ": " + command + self.action_symbols[valid_action]);

            else:
                print("Unknown command: " + command);
                print("Type \"help\" for a list of known self.commands.");

            print("");

    def run(self):
        while True:
            print("rc-shell $ ", end=' ')
            cmd = input()
            if cmd == "":
                pass
            elif cmd == "exit":
                sys.exit()
            elif cmd == "clear":
                os.system("clear")
            else:
                self.execute(cmd)


if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-d", "--device", dest="device", help="gateway device file")
    parser.add_option("-t", "--timeout", dest="timeout", help="uart timeout")
    parser.add_option("-b", "--baud_rate", dest="baud_rate", help="baud rate")
    parser.add_option("--standalone", dest="standalone", action='store_true', default=False, help="do not enable preamble");
    (options, args) = parser.parse_args()
    if options.device is None:
        options.device = "/dev/ttyUSB0"
    if options.baud_rate is None:
        options.baud_rate = 38400
    if options.timeout is None:
        options.timeout = 3
    if options.standalone is None:
        options.standalone = False

    print("Gateway Device: ", options.device)
    print("Baud Rate: ", options.baud_rate)
    print("Time out: ", options.timeout)
    print("Standalone: ", options.standalone)
    try:
        ser = serial.Serial(options.device, int(options.baud_rate), timeout=int(options.timeout))
    except serial.serialutil.SerialException as OSError:
        sys.exit('Error: Could not open communication port')
    rcsh = RCShell(ser, standalone=options.standalone)
    rcsh.run()
