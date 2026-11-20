import threading
import datetime
import  time
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
  
class rtc_drift:
    def __init__(self):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if 'USB-SERIAL CH340 ' in p.description:
                print(p)
                # Connection to port
                self.ser = serial.Serial(port=p.device, baudrate=9600)
        self.outdata=0
        self.temp=bytearray()
        # self.meter_time =0
    
        while(1):
            time.sleep(10)
            t1 = threading.Thread(target=self.system_time)
            t2 = threading.Thread(target=self.meter_time)
            
            # starting thread 1
            t1.start()
            # starting thread 2
            t2.start()
         
            # wait until thread 1 is completely executed
            t1.join()
            # wait until thread 2 is completely executed
            t2.join()
            self.time_difference()    
         
            # both threads completely executed
            print("Done!")

        
        

    def deserialize_generic(self,buf, num_bytes, signed,order="normal"):
        print type(buf)

    
        # print "hello"
        assert(isinstance(buf, bytearray))
        buf_copy = copy.deepcopy(buf)
        # print  buf_copy
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

    def meter_time(self):
        LIST1=[0xAA,0x00,0x00,0x01,0x02,0xFF,0xFF,0xFF,0xFF,0x04,0x04,0x02,0x4E,0x28,0x98,0x42]
        self.ser.write(LIST1)
        list=[]
        list.append(self.ser.read(19))
        # print list
        temp = bytearray()
        for i in range(0,len(list)):        
            temp.extend((list[i]))
        # print len(buf)
        buf=bytearray()
        index = 13
        datatype= 4
        temp_list=[]  
        for i in range(0,int(datatype)):
            buf.extend(chr(temp[index+i]))                         
        # for i in range(0,int(datatype)):
        #     buf.extend(chr(list[index+i]))
        print type(self.temp)
        a = self.deserialize_generic(buf,datatype,False)
        self.outdata=datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=a)
        self.real_time1 = datetime.datetime.strptime(str(self.outdata), '%Y-%m-%d %H:%M:%S')
        self.real_time=self.real_time1.time()
        print "real time",self.real_time 
        print "meter time", self.outdata

    def time_difference(self):
        s1 = str(self.real_time)
        s2 = str(self.system_time) # for example
        FMT = '%H:%M:%S'
        tdelta = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)
        if tdelta.days < 0:
            tdelta = timedelta(days=0,
                seconds=tdelta.seconds)
            print "time_difference",tdelta

# datetime.datetime(2009, 1, 6, 15, 8, 24, 78915)

# 2018-07-29 09:17:13.812189
 
    def system_time(self):
        """
        function to print cube of given num
        """
        # print("Cube: {}".format(num * num * num))
        now=datetime.datetime.now()
        self.system_time=now.strftime("%Y-%m-%d  %H:%M:%S")
        # self.system_time1 = datetime.datetime.strptime(str(self.time), '%Y-%m-%d %H:%M:%S')
        # self.system_time=self.system_time1.time()
        print "system_time :",self.system_time
    
if __name__ == "__main__":
   rtc_drift()
    
    