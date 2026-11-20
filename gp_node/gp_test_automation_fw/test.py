
import serialize
from serialize import deserialize_generic


a = bytearray()
a.extend(chr(0x00)) 
a.extend(chr(0x03))
a.extend(chr(0x07)) 
a.extend(chr(0xf7))
b = deserialize_generic(a, 4, signed = False, order="normal")
print b