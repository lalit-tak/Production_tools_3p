import datetime
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint32

from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint32
from gp_node.network.protocols.packets._3p.slab_packet_3p import SlabConfigurationPacket3P


class AccountingStatePacket3P(object):

    def __init__(self):
        self.slabContainer = SlabConfigurationPacket3P()
        self.current_slab = 0
        self.enabled_slab_set = 0
        self.isenabled = ""

    def __str__(self):
        return ("slab_info : \n{}\n"
                "enabled_slab : {} \n"
                "enabled_slab_set : {}\n"
                 "{}")\
                .format(self.slab_info,
                        self.current_slab,
                        self.enabled_slab_set,
                        self.isenabled)

    def deserialize(self,payload):
        self.slabContainer.deserialize(payload[0:26])
        self.slab_info = self.slabContainer
        self.current_slab =  deserialize_uint8(payload[26:27],"reverse")
        self.enabled_slab_set = int(payload[27])
        if int(payload[28]) == 1:
            self.isenabled = "slab enabled"
        else:
            self.isenabled = "slab disabled"
        #print "_______" + str(len(payload))

    def serialize(self, payload):
        print ("not implemented")
