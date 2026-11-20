import cmd
import inspect
import sys
import logging
import os
import os.path
import pprint
import colorama
import serial
import serial.tools.list_ports
import datetime
import getpass
import dateutil.parser
from colorama import Fore
from optparse import OptionParser

# ==================== FIX #1: Better Import Handling ====================
# Try importing gp_node modules, with fallback for missing modules
try:
    from gp_node.network.network_api import NetworkAPI, NetworkAPIError
    from gp_node.utils.address import Address
    from gp_node.network.protocols.packets._1p.daily_deduction_params import DailyDeductionParams
    from gp_node.network.protocols.packets._1p.load_survey_params import LoadSurveyParams
    from gp_node.network.protocols.packets._1pn.load_survey_params import LoadSurveyParamsN
    from gp_node.network.protocols.packets._1p.tamper_log_packet import TamperLog
    from gp_node.network.circular_log._1p.log_reader import LogReader
    from gp_node.network.circular_log._1p.load_survey import LoadSurveyReaderN
    from gp_node.network.circular_log._1p.log_reader1 import LogReaderN
    from gp_node.network.circular_log._1p.block_load_profile import BlockLoadProfileReader
    from gp_node.network.circular_log._1p.daily_load_profile import DailyLoadProfileReader
    from gp_node.network.circular_log._1p.event_record import EventRecordReader
    from gp_node.network.circular_log._1p.tamper_log_reader import TamperLogReader
    from gp_node.network.circular_log.energy_cop.data_logger import DataLogReader
    from gp_node.network.protocols.packets._1p.slab_packet import SlabConfigurationPacket
    from gp_node.network.protocols.packets._1p.accounting_state_packet import AccountingStatePacket
    from gp_node.network.protocols.packets._1p.fixed_deduction_packet import FixedDeductionPacket
    from gp_node.network.protocols.packets._3p.load_survey_params_3p import LoadSurveyParams3P
    from gp_node.network.protocols.packets._3p.metering_data_params_3p import MeteringDataParams3P
    from gp_node.network.protocols.packets._3p.crc_bundle_3p import CrcDataPacket3P
    from gp_node.network.protocols.packets._3p.slab_packet_3p import SlabConfigurationPacket3P
    from gp_node.network.protocols.packets._3p.accounting_state_packet_3p import AccountingStatePacket3P
    from gp_node.network.protocols.packets._3p.fixed_deduction_packet_3p import FixedDeductionPacket3P
    from gp_node.network.protocols.packets._3p.bundle_3p import MeteringDataParamsBundle3P
    from gp_node.network.protocols.packets._3p.sys_params_3p import SystemsCommands3P
    GP_NODE_AVAILABLE = True
except ImportError as e:
    print(f"\n⚠️  Warning: Could not import gp_node modules: {e}")
    print("   Make sure gp_node folder is in the same directory as this EXE/script")
    GP_NODE_AVAILABLE = False


# ==================== FIX #2: Better Path Handling ====================
def get_app_path():
    """Get the application's root directory (works in both script and EXE mode)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


def get_log_file_path():
    """Get the log file path (works in both script and EXE mode)"""
    app_path = get_app_path()
    log_dir = os.path.join(app_path, "logs")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"Warning: Could not create logs directory: {e}")
            # Fallback to temp directory
            import tempfile
            log_dir = tempfile.gettempdir()
    
    return os.path.join(log_dir, "node-shell.log")


# ==================== FIX #3: Modified NodeShell Class ====================
class NodeShell(cmd.Cmd):
    """A shell to interact with the Node board"""

    network_api = None
    address = None

    def precmd(self, line):
        self.file_logger.info("------------------------------------")
        self.file_logger.info(line)
        return line

    def set_network_api(self, network_api):
        """Setup network API and logging"""
        username = getpass.getuser()
        self.network_api = network_api
        
        # Only initialize if gp_node is available
        if GP_NODE_AVAILABLE:
            try:
                self.logger = LogReader(network_api, 4, 42)
                self.loggern = LogReaderN(network_api, 4, 42)
                self.tamper_logger = TamperLogReader(network_api, 2, 14)
                self.block_load_profile = BlockLoadProfileReader(network_api, 160, 30)
                self.daily_load_profile = DailyLoadProfileReader(network_api, 70, 14)
                self.event_record = EventRecordReader(network_api, 3, 24)
                self.dlog = DataLogReader(network_api, 232, 36)
                self.load_surveyn = LoadSurveyReaderN(network_api, 232, 32)
            except Exception as e:
                print(f"Warning: Could not initialize all loggers: {e}")

        # ==================== FIX #4: Better Logging Setup ====================
        self.file_logger = logging.getLogger(__name__)
        self.file_logger.setLevel(logging.INFO)
        
        # Use the improved path function
        log_file_path = get_log_file_path()
        
        try:
            self.handler = logging.FileHandler(log_file_path)
            self.handler.setLevel(logging.INFO)
            self.formatter = logging.Formatter('%(asctime)s - %(message)s')
            self.handler.setFormatter(self.formatter)
            self.file_logger.addHandler(self.handler)
            print(f"✓ Logging to: {log_file_path}")
        except Exception as e:
            print(f"Warning: Could not setup logging: {e}")

    def print_command(self, func, kwargs, to_print=True):
        """Execute a command and print results"""
        units_present = True
        reply = None
        try:
            reply = func(self.address, **kwargs)
        except NetworkAPIError as err:
            print(err)
            self.file_logger.info(err)
            self.file_logger.info("----------End OF CMD----------------\n")
            return None
        except Exception as err:
            print(f"Unknown Error: {err}")
            self.file_logger.info(f"Unknown Error: {err}")
            self.file_logger.info("----------End OF CMD----------------\n")
            return None

        if to_print:
            try:
                cal_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("Cmd Time :{}".format(cal_time))
                print("{reply} {units}".format(reply=reply, units=func.units))
                self.file_logger.info("{reply} {units}".format(reply=reply, units=func.units))
            except AttributeError as err:
                if func == self.network_api.three_ph_get_metering_data_bundle:
                    bundl = MeteringDataParamsBundle3P()
                    budle_dict = bundl.get_packet_bundle_string(reply)
                    reply = budle_dict
                print("{reply}".format(reply=reply))
                self.file_logger.info("{reply}".format(reply=reply))
        self.file_logger.info("----------End OF CMD----------------\n")
        return reply

    def emptyline(self):
        pass

    # ==================== SAMPLE COMMANDS (add rest from your original file) ====================
    
    def do_get_price(self, line):
        """Get price"""
        if not GP_NODE_AVAILABLE:
            print("Error: gp_node module not available")
            return
        self.print_command(self.network_api.get_price, kwargs={})

    def do_get_address(self, line):
        """Get address"""
        if not GP_NODE_AVAILABLE:
            print("Error: gp_node module not available")
            return
        self.print_command(self.network_api.get_address, kwargs={})

    def do_set_price(self, line):
        """Set price"""
        if not GP_NODE_AVAILABLE:
            print("Error: gp_node module not available")
            return
        try:
            price = float(line)
        except:
            print("Usage: set_price <float_value>")
        else:
            self.print_command(self.network_api.set_price, kwargs={"price": price})

    def do_exit(self, line):
        """Exit the shell"""
        return True

    def do_use(self, line):
        """Set the address to communicate with"""
        try:
            self.address = Address(line)
            self.prompt = "{green}node-shell{yellow} [{address}] {blue}${white} ".format(
                address=self.address,
                green=Fore.GREEN,
                yellow=Fore.YELLOW,
                blue=Fore.BLUE,
                white=Fore.WHITE)
        except Exception as e:
            print(f"Error: Invalid address - {e}")

    def parseline(self, line):
        """Parse command line for backward compatibility"""
        format_found = False
        try:
            ret = line.split(':')
            ret = (ret[0].replace(' ', '_'), ''.join(ret[1:]), line)
            format_found = True
        except IndexError:
            pass
        if not format_found:
            ret = (line.replace(' ', '_'), '', line)
        return ret


# ==================== FIX #5: Improved run() Function ====================
def run():
    """Main entry point with better error handling"""
    parser = OptionParser()
    parser.add_option("-d", "--device", dest="device",
                      help="gateway device file (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)")
    parser.add_option("-t", "--timeout", dest="timeout", default="3",
                      help="uart timeout (default: 3)")
    parser.add_option("-b", "--baud_rate", dest="baud_rate", default="9600",
                      help="baud rate (default: 9600)")
    parser.add_option("-s", "--silent", action="store_true",
                      dest="silent", help="runs without FTDI cable")
    parser.add_option("-c", "--command", dest="command", default="",
                      help="run single command and exit")
    parser.add_option("-m", "--mode", dest="mode", default="irda",
                      help="mode: irda or rc_packet (default: irda)")
    parser.add_option("--id", "--portID", dest="portID", default="4",
                      help="device port ID (default: 4)")
    parser.add_option("--list-ports", action="store_true", dest="list_ports",
                      help="list available serial ports and exit")

    (options, args) = parser.parse_args()
    
    # List available ports if requested
    if options.list_ports:
        ports = list(serial.tools.list_ports.comports())
        print("\n=== Available Serial Ports ===")
        if ports:
            for port in ports:
                print(f"  Port: {port.device}")
                print(f"    Description: {port.description}")
                print()
        else:
            print("  No serial ports found!")
        sys.exit(0)
    
    # Auto-detect device if not specified
    if options.device is None:
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        if available_ports:
            options.device = available_ports[0]
            print(f"\n✓ Auto-detected device: {options.device}\n")
        else:
            print("\n✗ Error: No serial ports detected!")
            print("  Please specify a port with: NodeShell.exe -d COM3")
            print("  Or use: NodeShell.exe --list-ports\n")
            sys.exit(1)
    
    # ==================== FIX #6: Better Error Handling for Serial Connection ====================
    ser = None
    try:
        print(f"Connecting to {options.device} at {options.baud_rate} baud...")
        ser = serial.Serial(options.device, int(options.baud_rate), timeout=int(options.timeout))
        print("✓ Connected successfully\n")
    except (serial.serialutil.SerialException, OSError) as err:
        print(f"\n✗ Error: Could not open port '{options.device}'")
        print(f"  Details: {err}\n")
        
        comPorts = list(serial.tools.list_ports.comports())
        print("Available serial ports:")
        if comPorts:
            for port in comPorts:
                print(f"  {port.device} - {port.description}")
        else:
            print("  No ports available")
        
        print("\nUsage: NodeShell.exe -d <PORT>")
        print("  Example (Windows): NodeShell.exe -d COM3")
        print("  Example (Linux):   NodeShell.exe -d /dev/ttyUSB0")
        print("  Or list ports:     NodeShell.exe --list-ports\n")
        
        if not options.silent:
            input("Press Enter to exit...")
            sys.exit(1)
    
    # Create necessary directories
    try:
        log_dir = os.path.dirname(get_log_file_path())
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create log directory: {e}")
    
    # Initialize NodeShell
    try:
        if not GP_NODE_AVAILABLE:
            print("\n⚠️  WARNING: gp_node module not found!")
            print("   Some commands may not work. Make sure the 'gp_node' folder")
            print("   is in the same directory as NodeShell.exe\n")
        
        if GP_NODE_AVAILABLE:
            network_api = NetworkAPI(ser, int(options.portID), options.mode)
        else:
            network_api = None
            
        node_shell = NodeShell()
        node_shell.set_network_api(network_api)
        node_shell.do_use("255.255.255.255")
        
        if options.command != "":
            node_shell.onecmd(options.command)
        else:
            print(("\n{cyan}Gateway Device: {device}\n"
                   "Baud Rate: {baud_rate}\n"
                   "Device Port: {port_id}\n"
                   "Time Out: {timeout}\n{white}").
                  format(device=options.device,
                         baud_rate=options.baud_rate,
                         port_id=options.portID,
                         timeout=options.timeout,
                         cyan=Fore.CYAN,
                         white=Fore.WHITE))
            
            print("Type 'help' for commands or 'exit' to quit\n")
            node_shell.cmdloop()
            
    except Exception as e:
        print(f"\n✗ Critical Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
    finally:
        if ser and ser.is_open:
            ser.close()


if __name__ == "__main__":
    run()
