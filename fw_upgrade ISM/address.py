import re

class Address:

    """ Represents the address of a node. The constructor argument
    is checked for the right formatting. 
    The format of the string in the constructor should follow IPv4 address formatting
    
    Usage: addr = Address("0.0.3.34")

    TODO: stronger type checking, presently, an address 999.999.999.999 is also valid
    """

    def __init__(self, address_string="0.0.0.0", address_integer=0):
        # if not isinstance(address_string, str):
        #     raise TypeError("address_string should be a string")
        # if not isinstance(address_integer, int):
        #     raise TypeError("address_integer should be a string integer")
        if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', address_string) != None:
            self.address_string = address_string
        else:
            error_string = "Format of string is inconsistent: " + address_string
            raise ValueError(error_string)
        if address_integer != 0:
            self.load_from_integer(address_integer)

    def __eq__(self, other):
        return (self.address_string == other.address_string)

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __str__(self):
        return self.address_string

    def __hash__(self):
        return self.dump_to_integer()

    def load_from_integer(self, integer):
        """
        Converts integer address into string. For example, this function
        is used if we want to deserialize the address in TAP packet.

        :param int integer: integer representation of the address. Should be in range
            0 to 0xFFFFFFFF (else ValueError would be raised). If integer is 0x12345678,
            then it corresponds to the address 12.34.45.67
        """
        if (integer < 0) or (integer > 0xFFFFFFFF):
            raise ValueError("Given integer cannot is out of range")
        self.address_string = ''
        self.address_string += str((integer & 0xFF000000) >> 24)+'.'
        self.address_string += str((integer & 0x00FF0000) >> 16)+'.'
        self.address_string += str((integer & 0x0000FF00) >> 8)+'.'
        self.address_string += str((integer & 0x000000FF) >> 0)

    def dump_to_integer(self):
        """
        Converts string address into integer. For example, this function
        is used if we want to serialize the address to be sent in a TAP packet.

        :return: integer corresponding to this address. For example, if address
            is 0.0.2.44, then the returned integer would be 0x00000244
        """
        d = self.address_string.split('.')
        return (int(d[0])<<24)+(int(d[1])<<16)+(int(d[2])<<8)+(int(d[3])<<0)