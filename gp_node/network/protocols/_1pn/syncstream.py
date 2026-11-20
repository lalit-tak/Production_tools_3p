"""
Implements the python side of the SyncstreamN protocol
"""

from gp_node.network.protocols.common.tap import TAPPacket, TAPHandler, TAPError
from gp_node.network.protocols.common.protocol import ProtocolMaster, ProtocolError
from gp_node.utils import Address, TamperFlag
from gp_node.utils.serialize import deserialize_int16
from gp_node.utils.serialize import deserialize_int32
import datetime
import math


class SyncstreamNError(ProtocolError):
    """
    Raised when any problem while reading SyncstreamN replies

    SETUP_FORMAT_ERROR: when the node believes that the SETUP request was wrongly formatted

    SETUP_TIME_DIFF_EXCEEDS_LIMIT: when the node believes that the timing between first_beat_time and its own time\
            are way off

    SETUP_START_TIME_LESS_THAN_NOW: when the node believes that the first_beat_time is less than the present time\
            of node

    SETUP_ALREADY_RUNNING: when setup command has already been called before on the node

    REQ_DATA_TIME_INTERVAL_OFF: when node belies the current_beat_time mentioned in REQ_DATA request\
            is way off from the node's perception of its time

    REQ_DATA_NOW_LT_START_TIME: when the node believes that the node's present time is less than start time

    REQ_DATA_FORMAT: when the node believes that REQ_DATA request was wrongly formatted

    REQ_DATA_SLAVE_NOT_SET_UP: raised when node believes that SETUP was not called before REQ_DATA

    REQ_DATA_LENGTH_INCORRECT: raised when reply from node to REQ_DATA is not of suficient length

    UNKNOWN_ERROR: as the name suggests!
    """

    SETUP_FORMAT_ERROR = 1
    SETUP_TIME_DIFF_EXCEEDS_LIMIT = 2
    SETUP_START_TIME_LESS_THAN_NOW = 3
    SETUP_ALREADY_RUNNING = 4
    REQ_DATA_TIME_INTERVAL_OFF = 5
    REQ_DATA_NOW_LT_START_TIME = 6
    REQ_DATA_FORMAT = 7
    REQ_DATA_SLAVE_NOT_SET_UP = 8
    REQ_DATA_LENGTH_INCORRECT = 9
    TIME_MISMATCH = 10
    BAD_PROTOCOL_VERSION = 11
    UNKNOWN_ERROR = 12


class SyncstreamNTimeMismatchError(SyncstreamNError, object):

    """
    Raised when error code is TIME_MISMATCH
    """

    def __init__(
            self,
            error_code,
            master_time,
            slave_time,
            tap_error=None,
            tap_packet=None):
        super(
            SyncstreamNTimeMismatchError,
            self).__init__(
            error_code,
            tap_error,
            tap_packet)
        self.master_time = master_time
        self.slave_time = slave_time

    def __str__(self):
        output = "\nmaster_time: " + str(self.master_time) + "\n"
        output += "slave time: " + str(self.slave_time)
        return output


class SyncstreamNMaster(ProtocolMaster, object):
    """
    Implements the protocol to collect minified data from nodes periodically
    """

    SLAVE_PORT = 5
    MASTER_PORT = 105

    def __init__(self, slave_address, my_tap_handler):
        super(SyncstreamNMaster, self).__init__(slave_address, my_tap_handler)
        now = datetime.datetime.now()
        mod_now = now.replace(microsecond=0, second=0) + \
            datetime.timedelta(minutes=1)
        self.first_beat_time = self._get_current_time_node_formatted(mod_now)
        self.interval = 60

    def setup(self, slave_address, interval):
        """
        Initializes the specified node by sending SETUP

        :param slave_address: Address of the node which is to be added
        :type slave_address: gp_node.utils.Address

        :raises: SyncstreamNError

        :returns: the string "ok"
        :rtype: str
        """
        assert(isinstance(slave_address, Address))
        self.interval = interval
        #start_time = self.get_current_beat_time() + self.interval
        start_time = self.interval
        payload = self._fill_setup_packet(start_time, self.interval)
        self.my_tap_handler.send_packet(self.my_address, slave_address,
                                        self.MASTER_PORT, self.SLAVE_PORT,
                                        payload)
        try:
            reply_packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SyncstreamNError(SyncstreamNError.TAP_ERROR, tap_error=e)
        buf = reply_packet.data
        if buf == "ok":
            pass
        elif buf[0:13] == "error: format":
            raise SyncstreamNError(
                SyncstreamNError.SETUP_FORMAT_ERROR,
                tap_packet=reply_packet)
        elif buf[0:22] == "error: already running":
            raise SyncstreamNError(
                SyncstreamNError.SETUP_ALREADY_RUNNING,
                tap_packet=reply_packet)
        elif buf[0:22] == "error: time_diff > max":
            raise SyncstreamNError(
                SyncstreamNError.SETUP_TIME_DIFF_EXCEEDS_LIMIT,
                tap_packet=reply_packet)
        elif buf[0:23] == "error: start_time < now":
            raise SyncstreamNError(
                SyncstreamNError.SETUP_START_TIME_LESS_THAN_NOW,
                tap_packet=reply_packet)
        else:
            raise SyncstreamNError(
                SyncstreamNError.UNKNOWN_ERROR,
                tap_packet=reply_packet)
        return "ok"

    def get_params(self, slave_address):
        payload = bytearray("REQ_PARAMS ")
        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.MASTER_PORT,
            self.SLAVE_PORT,
            payload)
        try:
            reply_packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SyncstreamNError(SyncstreamNError.TAP_ERROR, tap_error=e)
        reply = {}
        if reply_packet.data[0] == ord('Y'):
            reply["running"] = True
        elif reply_packet.data[0] == ord('N'):
            reply["running"] = False
        else:
            reply["running"] = None
        if reply_packet.data[1] == ord('Y'):
            reply["started_collecting_data"] = True
        elif reply_packet.data[1] == ord('N'):
            reply["started_collecting_data"] = False
        else:
            reply["started_collecting_data"] = None
        reply["start_time"] = datetime.timedelta(seconds=deserialize_int32(
            reply_packet.data[2:6])) + datetime.datetime(1970, 1, 1)
        reply["interval"] = deserialize_int32(reply_packet.data[6:10])
        reply["beat_time"] = datetime.timedelta(seconds=deserialize_int32(
            reply_packet.data[10:14])) + datetime.datetime(1970, 1, 1)
        return reply

    def reset(self, slave_address):
        """
        Resets the node's SyncstreamN parameters. Once this command is executed,
        the setup() command should be executed to set up the new SyncstreamN protocol
        parameters on the node

        :returns: the bytearray of the reply's TAP packet
        """
        payload = bytearray("RESET ")
        self.my_tap_handler.send_packet(
            self.my_address,
            slave_address,
            self.MASTER_PORT,
            self.SLAVE_PORT,
            payload)
        try:
            reply_packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SyncstreamNError(SyncstreamNError.TAP_ERROR, tap_error=e)
        return reply_packet.data

    def get_bundle(self, slave_address):
        """
        Queries the specified node for minified data, and returns the packet data as a dictionary.

        :returns: A dictionary which contains all the minified data from the node
        :rtype: dict

        :raises: SyncstreamNError, SyncstreamNTimeMismatchError

        TODO: return Bundle() instead of a dictionary
        """
        payload = self._fill_request_data_packet(self.get_current_beat_time())
        self.my_tap_handler.send_packet(self.my_address, slave_address,
                                        self.MASTER_PORT, self.SLAVE_PORT,
                                        payload)
        try:
            reply_packet = self.my_tap_handler.get_packet_from(
                slave_address, self.SLAVE_PORT)
        except TAPError as e:
            raise SyncstreamNError(SyncstreamNError.TAP_ERROR, tap_error=e)
        buf = reply_packet.data
        if buf[0:24] == "error: time interval off":
            raise SyncstreamNError(
                SyncstreamNError.REQ_DATA_TIME_INTERVAL_OFF,
                tap_packet=reply_packet)
        if buf[0:23] == "error: now < start_time":
            raise SyncstreamNError(
                SyncstreamNError.REQ_DATA_NOW_LT_START_TIME,
                tap_packet=reply_packet)
        if buf[0:13] == "error: format":
            raise SyncstreamNError(
                SyncstreamNError.REQ_DATA_FORMAT,
                tap_packet=reply_packet)
        if buf[0:24] == "error: client not set up":
            raise SyncstreamNError(
                SyncstreamNError.REQ_DATA_SLAVE_NOT_SET_UP,
                tap_packet=reply_packet)
        if len(buf) < 29:
            raise SyncstreamNError(
                SyncstreamNError.REQ_DATA_LENGTH_INCORRECT,
                tap_packet=reply_packet)
        reply = self._parse_request_data_packet(reply_packet)
        slave_time = reply["time"]
        unix_time_zero = datetime.datetime(1970, 1, 1)
        master_time = unix_time_zero + \
            datetime.timedelta(0, self.get_current_beat_time())
        # if master_time != slave_time:
        #    raise SyncstreamNTimeMismatchError(SyncstreamNError.TIME_MISMATCH, master_time, slave_time)
        return reply

    def get_current_beat_time(self):
        """
        :returns: the most recent beat time (in units of seconds since epoch)\
            as believed by the SyncstreamNMaster
        :rtype: int
        """
        if (self.first_beat_time > self._get_current_time_node_formatted()):
            return self.first_beat_time
        num_elapsed_beats = (
            self._get_current_time_node_formatted() - self.first_beat_time) / self.interval
        current_beat_time = (
            num_elapsed_beats * self.interval) + self.first_beat_time
        return current_beat_time

    def _get_current_time_node_formatted(self, time=None):
        if time is None:
            return int(
                (datetime.datetime.now() -
                 datetime.datetime(
                    1970,
                    1,
                    1)).total_seconds())
        else:
            return int((time - datetime.datetime(1970, 1, 1)).total_seconds())

    def _parse_request_data_packet(self, tap_packet):
        if tap_packet.data[0] == 2:
            return self._parse_request_data_packet_v2(tap_packet)
        else:
            raise SyncstreamNError(
                SyncstreamNError.BAD_PROTOCOL_VERSION,
                tap_packet=tap_packet)

    def _parse_request_data_packet_v2(self, tap_packet):
        """
        Parses payload v2 for reply to REQ_DATA request.
        """
        buf = tap_packet.data
        reply = {}

        unix_str_time = str(deserialize_int32(buf[1:5]))
        unix_time = int(unix_str_time)
        unix_time_zero = datetime.datetime(1970, 1, 1)
        reply["time"] = unix_time_zero + datetime.timedelta(0, unix_time)
        reply["voltage"] = deserialize_int32(buf[5:9]) / 1000.0  # mV -> V
        reply["current"] = deserialize_int32(buf[9:13]) / 1000.0  # mA -> A
        reply["active_power"] = deserialize_int32(
            buf[13:17]) / 1000.0  # mW -> W
        # p.f.*1000 -> p.f.
        reply["power_factor"] = deserialize_int16(buf[17:19]) / 1000.0
        reply["frequency"] = deserialize_int16(
            buf[19:21]) / 10.0  # Hz*10 -> Hz
        reply["active_energy"] = deserialize_int32(buf[21:25]) / 1.0  # Wh
        reply["reactive_energy"] = deserialize_int32(buf[25:29]) / 1.0  # Wh
        reply["credits"] = deserialize_int32(buf[29:33])  # credits
        reply["price"] = float(deserialize_int32(
            buf[33:37]))  # Ws/credit -> credits/kWh
        if reply["price"] != 0:
            reply["price"] = 3600 * 1000 / int(reply["price"])

        flag_byte = buf[37]
        reply["tamper_events"] = []
        if flag_byte >= 128:
            raise ValueError("Bit 7 of flag_list was unexpectedly set.")
            flag_byte = flag_byte - 128
        if flag_byte >= 64:
            raise ValueError("Bit 6 of flag_list was unexpectedly set.")
            flag_byte = flag_byte - 64
        if flag_byte >= 32:
            reply["tamper_events"].append(TamperFlag("NEUTRAL_DISTURBANCE"))
            flag_byte = flag_byte - 32
        if flag_byte >= 16:
            reply["tamper_events"].append(TamperFlag("NEUTRAL_MISSING"))
            flag_byte = flag_byte - 16
        if flag_byte >= 8:
            reply["tamper_events"].append(TamperFlag("COVER_OPEN"))
            flag_byte = flag_byte - 8
        if flag_byte >= 4:
            reply["tamper_events"].append(TamperFlag("MAGNETIC"))
            flag_byte = flag_byte - 4
        if flag_byte >= 2:
            reply["tamper_events"].append(TamperFlag("LINE_LOAD_REVERSAL"))
            flag_byte = flag_byte - 2
        if flag_byte >= 1:
            reply["tamper_events"].append(TamperFlag("EARTH"))
            flag_byte = flag_byte - 1

        return reply

    def _fill_setup_packet(self, beat_time, interval):
        """
        Used to get the payload for SETUP request

        :param beat_time: The first beat time (UNIX time)
        :type beat_time: int

        :param interval: The interval in seconds, at which the nodes are expected\
                to store their data
        :type interval: int

        :returns: payload for SETUP request
        :rtype: bytearray
        """
        assert(isinstance(beat_time, int))
        assert(isinstance(interval, int))

        max_digits_in_interval = 2

        interval = str(interval / 10)
        digits = len(interval)
        digits = max_digits_in_interval - digits

        for i in range(digits):
            interval = "0" + interval

        payload = "SETUP " + str(beat_time) + " " + interval

        return bytearray(payload)

    def _fill_request_data_packet(self, current_beat_time):
        """
        Used to get the payload for REQ_DATA request

        :param current_beat_time: The most recent beat time (UNIX time)
        :type current_beat_time: int

        :returns: the payload for REQ_DATA request
        :rtype: bytearray
        """
        assert(isinstance(current_beat_time, int))
        payload = "REQ_DATA " + str(current_beat_time)
        return bytearray(payload)
