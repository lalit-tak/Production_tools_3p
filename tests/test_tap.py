import time
import subprocess
import serial

from gp_node.network.protocols.tap import TAPHandler, TAPPacket, TAPError
from gp_node.utils import Address
from nose.tools import assert_raises


class TestTAP:

    def setup(self):
        socat_command = "socat PTY,link=/tmp/.emulate,raw,echo=0,b9600 PTY,link=/tmp/emulate,raw,echo=0,b9600"
        self.socat_process = subprocess.Popen(socat_command, shell=True);
        # Wait for the subprocess to start the bridge
        time.sleep(0.2);
        self.master_serial = serial.Serial("/tmp/.emulate", timeout=0)
        self.slave_serial = serial.Serial("/tmp/emulate", timeout=0)
        pass

    def teardown(self):
        self.socat_process.terminate();
        self.master_serial.close()
        self.slave_serial.close()
        pass

    def dump_tap_packet(self, packet):
        string = packet.serialize()
        for i in range(len(string)):
            self.master_serial.write(string)

    def test_get_packet_without_timeout(self):
        """TAP: Test TAP handler without timeouts"""
        sent_packet = TAPPacket()
        sent_packet.fill(Address("0.0.1.2"), Address("0.0.3.150"), 4, 8, 5, bytearray("12346"))
        self.dump_tap_packet(sent_packet)
        th = TAPHandler(self.slave_serial, 1)
        received_packet = th.get_packet()
        assert sent_packet == received_packet

    def test_get_packet_with_start_byte_timeout(self):
        """TAP: Test that TAP handler timeout when start byte is not provided"""
        for i in range(5):
            self.master_serial.write('y')
        th = TAPHandler(self.slave_serial, 1)
        with assert_raises(TAPError) as cm:
            received_packet = th.get_packet()
        ex = cm.exception
        print ex
        assert(ex.error_code == TAPError.TIMEOUT_START_BYTE)


    def test_get_packet_with_length_timeout(self):
        """TAP: Test TAP handler timeout when sufficient number of bytes are not received"""
        self.master_serial.write(chr(0xAA))
        for i in range(5):
            self.master_serial.write('y')
        th = TAPHandler(self.slave_serial, 1)
        with assert_raises(TAPError) as cm:
            received_packet = th.get_packet()
        ex = cm.exception
        print ex
        assert(ex.error_code == TAPError.TIMEOUT_LENGTH)

    def test_get_packet_with_stop_byte_mismatch(self):
        """TAP: Test TAP handler timeout when stop byte is not 0x55"""
        sent_packet = TAPPacket()
        sent_packet.fill(Address("0.0.1.2"), Address("0.0.3.150"), 4, 8, 5, bytearray("12346"))
        buf = sent_packet.serialize()
        buf[-1] = chr(0x11)
        for i in buf:
            self.master_serial.write(chr(i))
        th = TAPHandler(self.slave_serial, 1)
        with assert_raises(TAPError) as cm:
            received_packet = th.get_packet()
        ex = cm.exception
        print ex
        assert(ex.error_code == TAPError.STOP_BYTE_MISMATCH)

    def test_send_packet_get_packet_loop(self):
        """TAP: Tests TAP handler that a packet sent using send_packet can be parsed by get_packet"""
        sent_packet = TAPPacket()
        sent_packet.fill(Address("0.0.1.2"), Address("0.0.3.150"), 4, 8, 11, bytearray("hello world"))
        th1 = TAPHandler(self.slave_serial, 1)
        th1.send_packet(sent_packet.src_addr, sent_packet.dest_addr, sent_packet.src_port, sent_packet.dest_port, bytearray("hello world"))

        th2 = TAPHandler(self.master_serial, 1)
        received_packet = th2.get_packet()
        assert sent_packet == received_packet

    def test_flush(self):
        """TAP: Tests that TAP flushes input before receving packet"""
        sent_packet = TAPPacket()
        sent_packet.fill(Address("0.0.1.2"), Address("0.0.3.150"), 4, 8, 11, bytearray("hello world"))
        th1 = TAPHandler(self.slave_serial, 1)
        th1.send_packet(sent_packet.src_addr, sent_packet.dest_addr, sent_packet.src_port, sent_packet.dest_port, bytearray("hello world"))

        th2 = TAPHandler(self.master_serial, 1)
        received_packet = th2.get_packet()
        assert sent_packet == received_packet

    def test_get_packet_from(self):
        """TAP: Tests that get_packet_from() ignores bad packets"""
        th1 = TAPHandler(self.slave_serial, 1)
        sent_packet_1 = TAPPacket()
        sent_packet_1.fill(Address("0.0.1.2"), Address("0.0.3.150"), 4, 8, 11, bytearray("hello world"))
        sent_packet_2 = TAPPacket()
        sent_packet_2.fill(Address("0.0.0.212"), Address("0.0.3.150"), 44, 8, 11, bytearray("hello world"))
        th1.send_packet(sent_packet_1.src_addr, sent_packet_1.dest_addr, sent_packet_1.src_port, sent_packet_1.dest_port, bytearray("hello world"))
        th1.send_packet(sent_packet_2.src_addr, sent_packet_2.dest_addr, sent_packet_2.src_port, sent_packet_2.dest_port, bytearray("hello world"))
        th2 = TAPHandler(self.master_serial, 1)
        received_packet = th2.get_packet_from(Address("0.0.0.212"), 44, Address("0.0.3.150"))
        assert sent_packet_2 == received_packet


    def test_tap_packet(self):
        """TAP: tests TAP packet"""
        tp1 = TAPPacket()
        tp2 = TAPPacket()
        assert tp1 == tp2
        assert not (tp1 != tp2)
        tp1.fill(Address("0.0.1.2"), Address("0.0.2.1"), 9, 12, 2, bytearray("hi"))
        assert tp1 != tp2
        tp2.fill(Address("0.0.1.2"), Address("0.0.2.1"), 9, 12, 2, bytearray("hi"))
        assert tp1 == tp2
        assert str(tp1) == str(tp2)
        with assert_raises(AssertionError) as cm:
            tp1 == None
