import serial
import copy
import os
import serial.tools.list_ports
# from serialize import deserialize_generic
from copy import deepcopy
import copy
import datetime
from dateutil import relativedelta
from datetime import timedelta
import dateutil.parser
from datetime import timedelta
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

def get_time():
    LIST1=[0xAA,0x00,0x00,0x01,0x02,0xFF,0xFF,0xFF,0xFF,0x04,0x04,0x02,0x4E,0x28,0x98,0x42]
    ser.write(LIST1)
    # print "gaya"
def receive_time():
    # print "aaya"
    list=[]
    list.append(ser.read(19))
    print list
    buf = bytearray()
    for i in range(0,len(list)):
        buf.extend((list[i]))
    # print len(buf)
    temp=bytearray()
    index = 13
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))                         
    # for i in range(0,int(datatype)):
    #     buf.extend(chr(list[index+i]))

    a = deserialize_generic(temp, datatype,False)
    outdata=datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=a)
    print "meter time",outdata
    metering_data()
   
def metering_data():
    list=[0xAA,0x00,0x00,0x01,0x02,0xFF,0xFF,0xFF,0xFF,0x04,0x04,0x02,0xAC,0x49,0x58,0xD6]
    read_data()
def read_data():
    list1=[]
    list1.append(ser.read(41))
    buf = bytearray()
    for i in range(0,len(list1)):
        buf.extend((list1[i]))
    temp=bytearray()
    index = 12
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))
    a = deserialize_generic(temp, datatype,False)
    print "voltage",a
    index = 16
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))
    b = deserialize_generic(temp, datatype,False)
    print "phase current :",(b/1000.0)
    index = 20
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))
    c = deserialize_generic(temp, datatype,False)
    print "neutral current",(c/1000.0)
    index = 24
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))
    d = deserialize_generic(temp, datatype,False)
    print "active power",(c/1000000.0)
    index = 28
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))
    e= deserialize_generic(temp, datatype,False)
    print "apperent power:",(e/1000000.0)
    index = 32
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))
    f= deserialize_generic(temp, datatype,False)
    print "reactive power:",(f/1000000.0)
    index = 36
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))
    f= deserialize_generic(temp, datatype,False)
    print "frequency:",(f/100.0)
    index = 40
    datatype= 4
    temp_list=[]  
    for i in range(0,int(datatype)):
        temp.extend(chr(buf[index+i]))
    f= deserialize_generic(temp, datatype,False)
    print "power factor:",(f/1000.0)
    




def clear_engine():
    temp_list=[]
    index=0
    datatype=0

if __name__ == "__main__":
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'USB-SERIAL CH340 ' in p.description:
            print(p)
        # Connection to port
            ser = serial.Serial(port=p.device, baudrate=9600)
    # get_time()
    # receive_time()
    metering_data()
    read_data()





