import datetime
import array
from gp_node.utils.serialize import deserialize_uint16
from gp_node.utils.serialize import deserialize_uint8
from gp_node.utils.serialize import deserialize_uint32

import gp_node.utils.serialize as serialize

class TodConfigurationPacket(object):
    def __init__(self):
        self.season_profile = self.SeasonProfile() 
        self.day_profile = self.DayProfile()
        self.week_profile = self.WeekProfile()
        self.numActSeason = 0
        self.numActWeek = 0
        self.numActdayId = 0
        self.seasonLen = 0
        self.seasonStartTS = 0
        self.seasonName = "" * 4
        self.seasonWeekName = "" * 4
        self.seasonWeekLen = 0
        self.weekLen = 0
        self.weekName = "" * 4
        self.weekDaysId = array.array('B', [0] * 7)
        self.dayId = 0
        self.numOfTOD = 0
        self.timeStamp =  array.array('H', [0] * 8)
        self.tarrif = array.array('B', [0] * 8)    

    #4,4,SE-1,4,1730,WE-1,4,SE-2,1730
    def deserialize(self, payload):
        buf = bytearray()
        buf = payload
        index = 0
        
        print("*************************************************************************************")
        print("-----------------------------------SEASON PROFILE------------------------------------")
        print("*************************************************************************************")
        
        self.numActSeason = serialize.deserialize_uint8(buf[index:index+1])
        index += 1
        
        print("\nName   Start                   Week Name")
        print("----------------------------------------")
        
        for i in range(self.numActSeason): 
            self.seasonName = "".join(chr(b) for b in buf[index:index+4])
            index+=4 
            
            self.seasonStartTS = serialize.deserialize_uint32(buf[index:index+4])
            self.seasonStartTS = datetime.datetime.utcfromtimestamp(self.seasonStartTS).strftime("%d/%m/%Y %H:%M:%S")
            self.seasonStartTS = self.seasonStartTS[:index+1] + "**" + self.seasonStartTS[index+5:]  # Keeps correct format
            index+=4        
            
            self.seasonWeekName = "".join(chr(b) for b in buf[index:index+4]) 
            index+=4
            
            print("{}   {}       {}".format(self.seasonName, self.seasonStartTS, self.seasonWeekName))  
                
        print("\n\n*************************************************************************************")
        print("--------------------------------------WEEK PROFILE-----------------------------------")
        print("*************************************************************************************")
        self.numActWeek = serialize.deserialize_uint8(buf[index:index+1])
        index+=1
        print("\nName   Mon   Tue   Wed  Thur  Fri  Sat  Sun")
        print("----------------------------------------------")
        
        for i in range(self.numActWeek):
              
            self.weekName = "".join(chr(b) for b in buf[index:index+4]) 
            index+=4
            
            for j in range(7):
                self.weekDaysId[j] = serialize.deserialize_uint8(buf[index:index+1])           
                index+=1
     
            # Create a list to store non-zero values
            non_zero_days = [day for day in self.weekDaysId if day != 0]

            # Print only when `non_zero_days` has valid entries
            if non_zero_days:
                print("{}   {}".format(self.weekName, "   ".join(map(str, non_zero_days))))

            # Check if weekName is empty before continuing
            #if  self.weekName.strip():  
            #    print("{}   {}     {}     {}    {}     {}    {}    {}".format(self.weekName, self.weekDaysId[0], self.weekDaysId[1], self.weekDaysId[2], self.weekDaysId[3], self.weekDaysId[4], self.weekDaysId[5], self.weekDaysId[6]))
            
                 
        #7,8,start_time,selector,start_time,selector
        print("\n\n*************************************************************************************")
        print("---------------------------------------DAY PROFILE-----------------------------------")
        print("*************************************************************************************")
        self.numActdayId = serialize.deserialize_uint8(buf[index:index+1])
        index+=1
                
        for i in range(self.numActdayId):
            self.numOfTOD = serialize.deserialize_uint8(buf[index:index+1])
            index+=1
            print("\nDayId : {}".format(i+1))
            print("\nStart Time                    Selector")
            print("----------------------------------------")
              
            for j in range(self.numOfTOD):
                self.timeStamp[j] = serialize.deserialize_uint16(buf[index:index+2])
                index+=2
                self.tarrif[j] = serialize.deserialize_uint8(buf[index:index+1])
                index+=1
                
                hours, remaining_minutes = divmod(self.timeStamp[j], 60)  # Convert minutes to hours & minutes
                formatted_time = "{:02d}:{:02d}:00".format(hours, remaining_minutes)  # HH:MM:SS format
                if (self.tarrif[j] != 0):
                    print("{}                      {}".format(formatted_time, self.tarrif[j]))
                else:
                    break
    
    
    # Day PROFILE          
    class DayProfile:
        
        def __init__(self):
            self.dayId = 0
            self.numberOfTOD = 0
            self.timeStamp = array.array('H', [0] * 8)  # unsigned short (2 bytes each)
            self.tarrif = array.array('B', [0] * 8)     # unsigned char (1 byte each)
        
        
        def serialize(self):
            payload = bytearray()
            payload.extend(serialize.serialize_uint8(self.dayId))
            payload.extend(serialize.serialize_uint8(self.numberOfTOD))
            
            for i in range(self.numberOfTOD):
                payload.extend(serialize.serialize_uint16(self.timeStamp[i]))
            for i in range(self.numberOfTOD):
                payload.extend(serialize.serialize_uint8(self.tarrif[i]))
                
            return payload
           
       
    #WEEK PROFILE     
    class WeekProfile:
        #1,4,WE-1,1,1,2,1,3,1,4,1,5,1,6,1,7,1
        def __init__(self):
            self.weekNum = 0
            self.weekLen = 0
            self.weekName = "" * 4
            self.weekDaysId = array.array('B', [0] * 7) #1 Byte
            
        #def __len__(self):
        #    return len(self.weekName)  # Returns number of stored items
        
        def serialize(self):
            payload = bytearray()
            payload.extend(serialize.serialize_uint8(self.weekNum))
            payload.extend(serialize.serialize_uint8(self.weekLen))  
            payload.extend(self.weekName.encode("utf-8"))
            for i in range(7):
                payload.extend(serialize.serialize_uint8(self.weekDaysId[i]))
                
            return payload

        
    #SEASON PROFILE     
    class SeasonProfile:
        #SET_TOD_SEASON_PROFILE:4,4,SE-D,1736380800,4,WE-4
        def __init__(self):
            self.seasonNum = 0
            self.seasonLen = 0
            self.seasonStartTS = 0
            self.weekLen = 0
            self.seasonName = "" * 4
            self.weekName = "" * 4
            
        def __len__(self):
            return len(self.weekName)  # Returns number of stored items
        
        def serialize(self):
            payload = bytearray()
            payload.extend(serialize.serialize_uint8(self.seasonNum))
            payload.extend(serialize.serialize_uint8(self.seasonLen)) 
            payload.extend(self.seasonName.encode("utf-8")) 
            payload.extend(serialize.serialize_uint32(self.seasonStartTS))
            payload.extend(serialize.serialize_uint8(self.weekLen)) 
            payload.extend(self.weekName.encode("utf-8"))
                
            return payload
         
