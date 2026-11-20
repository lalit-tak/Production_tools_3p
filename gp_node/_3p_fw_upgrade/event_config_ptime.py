from gp_node.utils.serialize import deserialize_uint16

import gp_node.utils.serialize as serialize

# Occurance and Restore time will be in seconds
# Note: Please do not change the order of events
# Required setup.py install after every changes made in this file...

event_ptime_configuration_list = [
    #------------------------------------------------
    #EVENT ID            , OCCUR PTIME, RESTORE PTIME
    #------------------------------------------------
    # ['OVER_VOLTAGE'   ,         300,         300],
    # ['LOW_VOLTAGE'    ,         300,         300],
    # ['MISSING_R_PHASE',         300,         300],
    # ['MISSING_Y_PHASE',         300,         300],
    # ['MISSING_B_PHASE',         300,         300],
    # ['VOLTAGE_UNB'    ,         300,         300],
    # ['REVERSE_R_PHASE',         300,         300],
    # ['REVERSE_Y_PHASE',         300,         300],
    # ['REVERSE_B_PHASE',         300,         300],
    # ['CURRENT_UNB'    ,         300,         300],
    # ['CURRENT_BYPASS' ,         300,         300],
    # ['R_CTOPEN'       ,         300,         300],
    # ['Y_CTOPEN'       ,         300,         300],
    # ['B_CTOPEN'       ,         300,         300],
    # ['OVER_CURRENT'   ,         300,         300],
    # ['MAGNET'         ,          15,          15],
    # ['NEUTAL_DIST'    ,         300,         300],
    # ['LOW_PF'         ,         300,         300],
    # ['OVERLOAD'       ,         300,         300],
    #--------------------------------------------------
    #['OVER_VOLTAGE'   ,         61,         20],
    #['LOW_VOLTAGE'    ,         62,         21],
    #['MISSING_R_PHASE',         63,         22],
    #['MISSING_Y_PHASE',         64,         23],
    #['MISSING_B_PHASE',         65,         24],
    #['VOLTAGE_UNB'    ,         66,         25],
    #['REVERSE_R_PHASE',         67,         26],
    #['REVERSE_Y_PHASE',         68,         27],
    #['REVERSE_B_PHASE',         69,         28],
    #['CURRENT_UNB'    ,         61,         29],
    #['CURRENT_BYPASS' ,         62,         20],
    #['R_CTOPEN'       ,         63,         21],
    #['Y_CTOPEN'       ,         64,         22],
    #['B_CTOPEN'       ,         65,         23],
    #['OVER_CURRENT'   ,         66,         24],
    #['MAGNET'         ,         15,        s 15],
    #['NEUTAL_DIST'    ,         67,         25],
    #['LOW_PF'         ,         68,         26],
    #['OVERLOAD'       ,         69,         27],
    #--------------------------------------------------
     ['OVER_VOLTAGE'   ,         30,         30],
     ['LOW_VOLTAGE'    ,         30,         30],
     ['MISSING_R_PHASE',         30,         30],
     ['MISSING_Y_PHASE',         30,         30],
     ['MISSING_B_PHASE',         30,         30],
     ['VOLTAGE_UNB'    ,         30,         30],
     ['PHASE_REVERSE'  ,          1,          1],
     ['REVERSE_R_PHASE',         30,         30],
     ['REVERSE_Y_PHASE',         30,         30],
     ['REVERSE_B_PHASE',         30,         30],
     ['CURRENT_UNB'    ,         30,         30],
     ['CURRENT_BYPASS' ,         30,         30],
     ['R_CTOPEN'       ,         30,         30],
     ['Y_CTOPEN'       ,         30,         30],
     ['B_CTOPEN'       ,         30,         30],
     ['OVER_CURRENT'   ,         30,         30],
     ['HIGH_N_CURRENT' ,         30,         30],
     ['MAGNET'         ,         15,         15],
     ['NEUTAL_DIST'    ,         30,         30],
     ['LOW_PF'         ,         30,         30],
     ['MODULE_PLUG_IN_OUT' ,      5,          5],
     ['COVER_OPEN'     ,          1,          1]
]


class EventsPtimePacket(object):

    def __init__(self):
        self.OVER_VOLTAGE = 0
        self.LOW_VOLTAGE = 0
        self.MISSING_R_PHASE = 0
        self.MISSING_Y_PHASE = 0
        self.MISSING_B_PHASE = 0
        self.VOLTAGE_UNB = 0
        self.PHASE_REVERSE = 0
        self.REVERSE_R_PHASE = 0
        self.REVERSE_Y_PHASE = 0
        self.REVERSE_B_PHASE = 0
        self.CURRENT_UNB = 0
        self.CURRENT_BYPASS = 0
        self.R_CTOPEN = 0
        self.Y_CTOPEN = 0
        self.B_CTOPEN = 0
        self.OVER_CURRENT = 0
        self.HIGH_N_CURRENT = 0
        self.MAGNET = 0
        self.NEUTAL_DIST = 0
        self.LOW_PF = 0
        self.MODULE_PLUG_IN_OUT = 0
        self.COVER_OPEN = 0
        self.OVERLOAD = 0
        self.POWER_FAILURE = 0

        
    def __str__(self):
         return ("OVER_VOLTAGE :        {}  Sec      \n"
                 "LOW_VOLTAGE:          {}  Sec      \n"
                 "MISSING_R_PHASE:      {}  Sec      \n"
                 "MISSING_Y_PHASE:      {}  Sec      \n"
                 "MISSING_B_PHASE:      {}  Sec      \n"
                 "VOLTAGE_UNB:          {}  Sec      \n"
                 "PHASE_REVERSE:        {}  Sec      \n"
                 "REVERSE_R_PHASE:      {}  Sec      \n"
                 "REVERSE_Y_PHASE:      {}  Sec      \n"
                 "REVERSE_B_PHASE:      {}  Sec      \n"
                 "CURRENT_UNB:          {}  Sec      \n"
                 "CURRENT_BYPASS:       {}  Sec      \n"
                 "R_CTOPEN:             {}  Sec      \n"
                 "Y_CTOPEN:             {}  Sec      \n"
                 "B_CTOPEN:             {}  Sec      \n"
                 "OVER_CURRENT:         {}  Sec      \n"
                 "HIGH_N_CURRENT:       {}  Sec      \n"
                 "MAGNET:               {}  Sec      \n"
                 "NEUTAL_DIST:          {}  Sec      \n"
                 "LOW_PF:               {}  Sec      \n"
                 "MODULE_PLUG_IN_OUT:   {}  Sec      \n" 
                 "COVER_OPEN:           {}  Sec      \n" 
                 "OVERLOAD:             {}  Sec      \n"
                 "POWER_FAILURE:        {}  Sec      \n"  
                )\
                .format(    self.OVER_VOLTAGE,
                            self.LOW_VOLTAGE,
                            self.MISSING_R_PHASE,
                            self.MISSING_Y_PHASE,
                            self.MISSING_B_PHASE,
                            self.VOLTAGE_UNB,
                            self.PHASE_REVERSE, 
                            self.REVERSE_R_PHASE,
                            self.REVERSE_Y_PHASE,
                            self.REVERSE_B_PHASE,
                            self.CURRENT_UNB,
                            self.CURRENT_BYPASS,
                            self.R_CTOPEN,
                            self.Y_CTOPEN,
                            self.B_CTOPEN,
                            self.OVER_CURRENT,
                            self.HIGH_N_CURRENT,
                            self.MAGNET,
                            self.NEUTAL_DIST,
                            self.LOW_PF,
                            self.MODULE_PLUG_IN_OUT,
                            self.COVER_OPEN,
                            self.OVERLOAD,
                            self.POWER_FAILURE)
                
    def getEventsPtime(self):
        return ( "OVER_VOLTAGE :        {}  Sec      \n"
                 "LOW_VOLTAGE:          {}  Sec      \n"
                 "MISSING_R_PHASE:      {}  Sec      \n"
                 "MISSING_Y_PHASE:      {}  Sec      \n"
                 "MISSING_B_PHASE:      {}  Sec      \n"
                 "VOLTAGE_UNB:          {}  Sec      \n"
                 "PHASE_REVERSE:        {}  Sec      \n"
                 "REVERSE_R_PHASE:      {}  Sec      \n"
                 "REVERSE_Y_PHASE:      {}  Sec      \n"
                 "REVERSE_B_PHASE:      {}  Sec      \n"
                 "CURRENT_UNB:          {}  Sec      \n"
                 "CURRENT_BYPASS:       {}  Sec      \n"
                 "R_CTOPEN:             {}  Sec      \n"
                 "Y_CTOPEN:             {}  Sec      \n"
                 "B_CTOPEN:             {}  Sec      \n"
                 "OVER_CURRENT:         {}  Sec      \n"
                 "HIGH_N_CURRENT:       {}  Sec      \n"
                 "MAGNET:               {}  Sec      \n"
                 "NEUTAL_DIST:          {}  Sec      \n"
                 "LOW_PF:               {}  Sec      \n"
                 "MODULE_PLUG_IN_OUT:   {}  Sec      \n" 
                 "COVER_OPEN:           {}  Sec      \n" 
                 "OVERLOAD:             {}  Sec      \n"
                 "POWER_FAILURE:        {}  Sec      \n"           
                )\
                .format(  self.OVER_VOLTAGE,
                          self.LOW_VOLTAGE,
                          self.MISSING_R_PHASE,
                          self.MISSING_Y_PHASE,
                          self.MISSING_B_PHASE,
                          self.VOLTAGE_UNB,
                          self.PHASE_REVERSE,
                          self.REVERSE_R_PHASE,
                          self.REVERSE_Y_PHASE,
                          self.REVERSE_B_PHASE,
                          self.CURRENT_UNB,
                          self.CURRENT_BYPASS,
                          self.R_CTOPEN,
                          self.Y_CTOPEN,
                          self.B_CTOPEN,
                          self.OVER_CURRENT,
                          self.HIGH_N_CURRENT,
                          self.MAGNET,
                          self.NEUTAL_DIST,
                          self.LOW_PF,
                          self.MODULE_PLUG_IN_OUT,
                          self.COVER_OPEN,
                          self.OVERLOAD,
                          self.POWER_FAILURE)

    def deserialize(self, payload):  # For Get Event Ptimes
        buf = bytearray()
        buf = payload
        self.OVER_VOLTAGE = serialize.deserialize_uint16(buf[0:2])
        self.LOW_VOLTAGE = serialize.deserialize_uint16(buf[2:4])
        self.MISSING_R_PHASE = serialize.deserialize_uint16(buf[4:6])
        self.MISSING_Y_PHASE = serialize.deserialize_uint16(buf[6:8])
        self.MISSING_B_PHASE = serialize.deserialize_uint16(buf[8:10])
        self.VOLTAGE_UNB = serialize.deserialize_uint16(buf[10:12])
        self.PHASE_REVERSE = serialize.deserialize_uint16(buf[12:14])
        self.REVERSE_R_PHASE = serialize.deserialize_uint16(buf[14:16])
        self.REVERSE_Y_PHASE = serialize.deserialize_uint16(buf[16:18])
        self.REVERSE_B_PHASE = serialize.deserialize_uint16(buf[18:20])
        self.CURRENT_UNB = serialize.deserialize_uint16(buf[20:22])
        self.CURRENT_BYPASS = serialize.deserialize_uint16(buf[22:24])
        self.R_CTOPEN = serialize.deserialize_uint16(buf[24:26])
        self.Y_CTOPEN = serialize.deserialize_uint16(buf[26:28])
        self.B_CTOPEN = serialize.deserialize_uint16(buf[28:30])
        self.OVER_CURRENT = serialize.deserialize_uint16(buf[30:32])
        self.HIGH_N_CURRENT = serialize.deserialize_uint16(buf[32:34])
        self.MAGNET = serialize.deserialize_uint16(buf[34:36])
        self.NEUTAL_DIST = serialize.deserialize_uint16(buf[36:38])
        self.LOW_PF = serialize.deserialize_uint16(buf[38:40])
        self.MODULE_PLUG_IN_OUT = serialize.deserialize_uint16(buf[40:42])
        self.COVER_OPEN = serialize.deserialize_uint16(buf[42:44])
        self.OVERLOAD = serialize.deserialize_uint16(buf[44:46])
        self.POWER_FAILURE = serialize.deserialize_uint16(buf[46:48])