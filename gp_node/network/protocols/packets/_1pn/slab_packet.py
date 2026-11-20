import datetime
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint32

from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint32

import gp_node.utils.serialize as serialize

class SlabConfigurationPacketN(object):

    def __init__(self):
        self.no_of_slabs = 0
        self.slab_price = [0,0,0,0,0,0]
        self.slab_limits = [0,0,0,0,0]
        self.mmc = 0

    def __str__(self):
        return ("no_of_slabs : {}\n"
                "slab_price : {} paisa\n"
                "slab_limits : {} KWh\n"
                "Monthly Minimum Charges : {} Paisa\n")\
                .format(self.no_of_slabs,
                        self.slab_price,
                        self.slab_limits,
                        self.mmc*10)

    def deserialize(self,payload):
        self.no_of_slabs = deserialize_uint16(payload[0:2],"reverse")
        for i in range(6):
            self.slab_price[i] = deserialize_uint16(payload[2+(i*2):4+(i*2)],"reverse")

        for i in range(5):
            self.slab_limits[i] = deserialize_uint16(payload[14+(i*2):16+(i*2)],"reverse")
        self.mmc = deserialize_uint16(payload[24:26],"reverse")

    def serialize(self):
        payload = bytearray()
        payload.extend(serialize.serialize_uint16(self.no_of_slabs,"reverse"))
        for index in range(len(self.slab_price)):
            payload.extend(serialize.serialize_uint16(self.slab_price[index],"reverse"))
        for index in range(len(self.slab_limits)):
            payload.extend(serialize.serialize_uint16(self.slab_limits[index],"reverse"))
        payload.extend(serialize.serialize_uint16((self.mmc/10),"reverse"))
        return payload
