import copy

from termcolor import colored

from colorama import init
init()
# import copy
# """
# Library for serializing and deserialize integers to bufs 
# (representing byte arrays) in MSB order.
# """

# # class SerializeValueError(Exception):
# #     """
# #     Exception thrown if a certain number cannot be serialized within the
# #     given parameters.
# #     """

# #     def __init__(self, value, num_bytes, signed):
# #         self.message = str(value) + " cannot be represented in " + str(num_bytes) + \
# #                 " byte(s) as " + ("a signed " if signed else "an unsigned ") + "integer."

# #     def __str__(self):
# #         return repr(self.message)


# # class DeserializeValueError(Exception):
# #     """
# #     Exception thrown if a certain bytestream cannot be deserialized within the
# #     given parameters
# #     """

# #     def __init__(self, buf, num_bytes, signed):
# #         self.message = "The bytestream 0x" + str(buf).encode('hex') + " cannot be represented in " +\
# #                 str(num_bytes) + " byte(s) as " + ("a signed " if signed else "an unsigned ") + "integer."

# #     def __str__(self):
# #         return repr(self.message)


# def _in_range(value, num_bytes, signed):
#     """
#     Find if the given value can be represented in the given number of bytes
#     and sign.
#     """
#     max_value = 0
#     min_value = 0
#     # First, calculate the minimum and maximum values which could be represented
#     # by num_bytes bytes with the given sign.
#     if signed:
#         max_value = (2**((num_bytes * 8) - 1)) - 1
#         min_value = (-1 * (max_value + 1))
#     else:
#         max_value = (2**(num_bytes * 8)) - 1
#         min_value = 0
#     # Next, determine whether the given value lies between the calculated
#     # minimum and maximum values.
#     return min_value <= value <= max_value

def deserialize_generic(buf, num_bytes, signed,order="normal"):

    
    print "hello"
    assert(isinstance(buf, bytearray))
    buf_copy = copy.deepcopy(buf)
    print  buf_copy
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


if __name__ == "__main__":
    print colored("Failed Hello World",'red')
    buf = bytearray()
    index = 0
    datatype= 4


    temp_list = [0x00,0x33,0x04,0x4A,0x03]                                  
    for i in range(0,int(datatype)):
        buf.extend(chr(temp_list[index+i]))

    a = deserialize_generic(buf, datatype,False)

    print a , type(a)
    
    # 0x01,0x02,0x03,0x04,0x00,0x00,0x01,0x02,0x04,0xFF,0x41,