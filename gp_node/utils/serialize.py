import copy
"""
Library for serializing and deserialize integers to bufs 
(representing byte arrays) in MSB order.
"""

class SerializeValueError(Exception):
    """
    Exception thrown if a certain number cannot be serialized within the
    given parameters.
    """

    def __init__(self, value, num_bytes, signed):
        self.message = str(value) + " cannot be represented in " + str(num_bytes) + \
                " byte(s) as " + ("a signed " if signed else "an unsigned ") + "integer."

    def __str__(self):
        return repr(self.message)


class DeserializeValueError(Exception):
    """
    Exception thrown if a certain bytestream cannot be deserialized within the
    given parameters
    """

    def __init__(self, buf, num_bytes, signed):
        self.message = "The bytestream 0x" + str(buf).encode('hex') + " cannot be represented in " +\
                str(num_bytes) + " byte(s) as " + ("a signed " if signed else "an unsigned ") + "integer."

    def __str__(self):
        return repr(self.message)


def _in_range(value, num_bytes, signed):
    """
    Find if the given value can be represented in the given number of bytes
    and sign.
    """
    max_value = 0
    min_value = 0
    # First, calculate the minimum and maximum values which could be represented
    # by num_bytes bytes with the given sign.
    if signed:
        max_value = (2**((num_bytes * 8) - 1)) - 1
        min_value = (-1 * (max_value + 1))
    else:
        max_value = (2**(num_bytes * 8)) - 1
        min_value = 0
    # Next, determine whether the given value lies between the calculated
    # minimum and maximum values.
    return min_value <= value <= max_value


def serialize_generic(value, num_bytes, signed, order="normal"):
    """
    This is the common function which is used in the implementation of other
    concrete serialize functions such as serialize_int32. This function is
    not supposed to be called directly. Instead, use the specific functions such as
    serialize_int32 etc.
    
    Serialize an integer with a given number of bytes and sign. Assumes 8-bit
    bytes. Throws an error if the value given cannot be represented in the
    given number of bytes and sign.

    :param int value: The number which is to be serialized

    :param int num_bytes: Number of bytes in the output bytearray

    :param bool signed: True, if output should be signed; False, if output should be unsigned

    :param str order: Can be "normal" or "reverse". If it is "normal", then\
            0x1234 would be interpreted as [0x34, 0x12] bytearray. If "reverse", then
            0x1234 would e interpreted as [0x12, 0x34] bytearray

    :rtype: bytearray
    """
    if not _in_range(value, num_bytes, signed):
        raise SerializeValueError(value, num_bytes, signed)
    shift_quantity = (num_bytes - 1) * 8
    to_return = bytearray()
    for i in range(0, num_bytes):
        to_return.append((value >> shift_quantity) & 0xFF)
        shift_quantity -= 8
    if order=="reverse":
        to_return.reverse()
    assert(isinstance(to_return, bytearray))
    return to_return


def deserialize_generic(buf, num_bytes, signed, order="normal"):
    """
    This is the common function which is used in the implementation of other
    concrete deserialize functions such as deserialize_int32. This function is
    not supposed to be called directly. Instead, use the specific functions such as
    deserialize_int32 etc.

    Deserialize an integer with a given number of bytes and sign.
    Throws an error if the value represented by the buf cannot be
    represented by the given number of bytes and sign.

    :param bytearray buf: the byte array which is to be deserialized

    :param bool signed: True, if output should be signed; False, if output should be unsigned

    :param str order: Can be "normal" or "reverse". If it is "normal", then\
            [0x12, 0x34] bytearray would be interpreted as 0x3412. If "reverse", then
            [0x12, 0x34] bytearray would be interpreted as 0x1234

    :rtype: int
    """
    assert(isinstance(buf, bytearray))
    buf_copy = copy.deepcopy(buf)
    if order == "reverse":
        buf_copy.reverse()
    if(len(buf_copy) != num_bytes):
        raise DeserializeValueError(buf_copy, num_bytes, signed)
    shift_quantity = (len(buf_copy) - 1) * 8
    to_return = 0
    for i in range(0, len(buf_copy)):
        to_return += buf_copy[i] << shift_quantity
        shift_quantity -= 8
    # Figure out whether the number is supposed to be negative
    if signed and (to_return >= 2**((len(buf_copy) * 8) - 1)):
        to_return = - 2**(len(buf_copy)*8) + to_return
    return to_return


def serialize_int8(value, order="normal"):
    """
    """
    return serialize_generic(value, 1, True, order)

def serialize_int16(value, order="normal"):
    """
    """
    return serialize_generic(value, 2, True, order)

def serialize_int24(value, order="normal"):
    """
    """
    return serialize_generic(value, 3, True, order)

def serialize_int32(value, order="normal"):
    """
    """
    return serialize_generic(value, 4, True, order)

def serialize_int64(value, order="normal"):
    """
    """
    return serialize_generic(value, 8, True, order)
def serialize_uint8(value, order="normal"):
    """
    """
    return serialize_generic(value, 1, False, order)

def serialize_uint16(value, order="normal"):
    """
    """ 
    return serialize_generic(value, 2, False, order)

def serialize_uint24(value, order="normal"):
    """
    """ 
    return serialize_generic(value,3, False, order)

def serialize_uint32(value, order="normal"):
    """
    """
    return serialize_generic(value, 4, False, order)
def serialize_uint64(value, order="normal"):
    """
    """
    return serialize_generic(value, 8, False, order)

def deserialize_int8(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 1, True, order)

def deserialize_uint8(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 1, False, order)

def deserialize_int16(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 2, True, order)

def deserialize_int24(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 3, True, order)

def deserialize_int32(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 4, True, order)

def deserialize_int64(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 8, True, order)
def deserialize_uint8(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 1, False, order)

def deserialize_uint16(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 2, False, order)

def deserialize_uint24(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 3, False, order)

def deserialize_uint32(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 4, False, order)
def deserialize_uint64(buf, order="normal"):
    """
    """
    return deserialize_generic(buf, 8, False, order)