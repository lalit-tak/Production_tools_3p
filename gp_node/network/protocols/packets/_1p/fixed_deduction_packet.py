import datetime
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint32

from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint32

import gp_node.utils.serialize as serialize

class FixedDeductionPacket(object):

    def __init__(self):
        self.amount = 0
        self.type_of_deduction = ""
        self.enabled = ""
        self.enabled_fd_set = 0

    def __str__(self):
        return ("amount : {} paisa\n"
            "type_of_deduction : {}\n"
            "fixed deduction is : {}\n"
            "Enabled fd set : {}").format(self.amount,
                                self.type_of_deduction,
                                self.enabled,
                                self.enabled_fd_set)

    def deserialize(self,payload):
        self.amount = deserialize_uint32(payload[0:4],"reverse")
        temp = deserialize_uint16(payload[4:6],"reverse")
        if temp == 0:
            self.type_of_deduction = "daily"
        elif temp == 1:
            self.type_of_deduction = "monthly"
        else:
            raise Exception()
        self.enabled_fd_set = deserialize_uint8(payload[6:7],"reverse")
        isenabled = deserialize_uint8(payload[7:8],"reverse")
        if(isenabled == 1):
           self.enabled = "enabled"
        else:
           self.enabled = "disabled"

    def serialize(self):
        payload = bytearray()
        payload.extend(serialize.serialize_uint32(self.amount,"reverse"))
        if self.type_of_deduction == "daily":
            payload.extend(serialize.serialize_uint16(0,"reverse"))
        elif self.type_of_deduction == "monthly":
            payload.extend(serialize.serialize_uint16(1,"reverse"))
        else:
            raise Exception()
        return payload
