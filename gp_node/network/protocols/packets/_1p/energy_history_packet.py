from gp_node.utils.serialize import deserialize_int32

class EnergyHistoryPacket:


    def __init__(self, month):
        self.month = month
        self.energy = 0

    def __str__(self):
        return ("Month: {}\n"
                "Energy: {}\n").format(self.month - 7,
                                  self.energy)

    def deserialize(self, payload):
        """
        It is assumed that payload size is 4
        """
        
        self.energy = deserialize_int32(payload[0:4])
