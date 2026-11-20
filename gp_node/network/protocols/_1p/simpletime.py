"""
Implements master side of Simpletime protocol
"""

from gp_node.utils import Address
import time
import datetime
from gp_node.network.protocols.common.protocol import ProtocolMaster

class SimpletimeMaster(ProtocolMaster):

    """
    """
    
    SLAVE_PORT = 1
    MASTER_PORT = 1

    def broadcast_time(self):
        """
        Broadcasts the present UNIX time to 0.0.0.255.
        The nodes are not expected to reply, hence, this function always returns None
        """
        raw_time = int(time.time());
        raw_time += int(datetime.timedelta(hours=5, minutes=30).total_seconds())
        payload = bytearray()
        payload.extend(chr((raw_time & 0xFF000000) >> 24))
        payload.extend(chr((raw_time & 0x00FF0000) >> 16))
        payload.extend(chr((raw_time & 0x0000FF00) >> 8))
        payload.extend(chr((raw_time & 0x000000FF) >> 0))
        self.my_tap_handler.send_packet(self.my_address, Address("0.0.0.255"),
                                        self.SLAVE_PORT, self.MASTER_PORT, payload)
