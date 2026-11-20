"""
Adds meta data to TI-TXT file
"""

import argparse
import collections
import crc16
import re
import sys
import serial
from gp_node.network.network_api import NetworkAPI
import gp_node.utils.serialize as serialize
from binascii import unhexlify, hexlify
from gp_node.utils.address import Address
import os
import time
from flask.ext.mysql import MySQL
from device_address import AddressList_3P
from flask import Flask, render_template, json, request
from flask.ext.mysql import MySQL
import time

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'duldul'
app.config['MYSQL_DATABASE_DB'] = 'fw_upgrade'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306


mysql.init_app(app)

def deserialize_uint16(array):
    """
    Deserializes given bytearray into an interger

    :param bytearray array: A bytearray of length 2

    :returns: interger in range 0 to 2**16 - 1
    """
    if len(array) != 2:
        raise Exception

    return int(array[0]) + (int(array[1]) << 8)



def _get_crc(block):
    """
    This function is similar to crc16.crc16xmodem() except that it uses
    0xFFFF as the initial value (crc16.crc16xmodem() uses 0x0000 as the initial value).
    The C++ implementation of CRC in node_bsl should be changed to use 0x0000
    as the initial value; once that is done, simply replace _get_crc with crc16.crc16xmodem    

    :param bytearray block: The bytearray whose CRC is to be calculated

    :returns: CRC16-CCITT of the input block
    """
    def _bit_reverse(x):
        first_half = x%16
        second_half = x/16
        table = {0:0, 1:8, 2:4, 3:12, 4:2, 5:10, 6:6, 7:14, 8:1, 9:9, 10:5, 11:13, 12:3, 13:11, 14:7, 15:15}
        return_value = 16*table[first_half] + table[second_half]
        return return_value

    formatted_block = bytearray([])
    for byte in block:
        formatted_block.append(_bit_reverse(byte))
        formatted_block.append(0)

    crc = crc16.crc16xmodem(str(formatted_block),0)
    #print "In CRC Length of block:",len(block), hex(crc)
    return crc

def _parse_crc(crc_string):
    __crc_string = str(crc_string)
    arg = __crc_string.split("\n")
    ___crc = []
    try:
        for line_number in range(0,32):
            ___crc.append((arg[line_number].split(": ")[1]))
    except Exception as e:
        print e
    #values = int(___bundle_3p[17])
    #print "recieved Tamper Flag:", ___crc
    return ___crc


        


def run():
    parser = argparse.ArgumentParser(description="Creates image of new firmware for"
                                                 "info flash")
    parser.add_argument('-d', action="store", dest="device", 
                        type=str, help="device name, eg. /dev/ttyUSB0")
    parser.add_argument('-b', action="store", dest="baud_rate", 
                        type=str, help="baud rate")
    parser.add_argument('-t', action="store", dest="timeout", 
                        help="port time out")
    args = parser.parse_args()


    
    #----------We got chunck wise CRC also----------------
    conn = mysql.connect()
    cur = conn.cursor()
    ser = serial.Serial(args.device, args.baud_rate, timeout=int(args.timeout))
    network_api = NetworkAPI(ser, "irda")
    for i in AddressList_3P:
        crc_string = ""
        addr = str(AddressList_3P[i])
        retry_cnt = 3
        while(retry_cnt):
            retry_cnt = retry_cnt - 1
            try:
                crc_string =  network_api.three_ph_get_crc_bundle(Address(addr),4096,4096)
            except Exception as e:
                print e
                print addr, "getting crc bundle, retry cnt: ", retry_cnt
            else:
                retry_cnt = 0
                print addr, "got sector wise CRC"
                crc_sector_flash =  _parse_crc(crc_string)
                print "Address string:", addr
                d = addr.split('.')
                meter_id = (int(d[0])<<24)+(int(d[1])<<16)+(int(d[2])<<8)+(int(d[3])<<0)
                print "meter_id:", meter_id
                #--------------------Got it!!! Sectoe wise------------Put into Database-----------------
                try:
                    k=0
                    query = "SELECT * FROM crcs WHERE TYPE = '%s' AND Address =  '%d'" % ('METER_3P', meter_id)
                    cur.execute(query)
                    if(cur.rowcount != 0):
                        query = "DELETE FROM crcs WHERE Address = '%d'" % (meter_id)
                        cur.execute(query)

                    query = '''INSERT INTO crcs (TYPE,Address,sec_crc_00, sec_crc_01,sec_crc_02, sec_crc_03, sec_crc_04, sec_crc_05,\
                    sec_crc_06, sec_crc_07, sec_crc_08, sec_crc_09, sec_crc_10, sec_crc_11, sec_crc_12, sec_crc_13, sec_crc_14,\
                    sec_crc_15,sec_crc_16, sec_crc_17, sec_crc_18, sec_crc_19, sec_crc_20, sec_crc_21, sec_crc_22, sec_crc_23,\
                    sec_crc_24, sec_crc_25, sec_crc_26, sec_crc_27, sec_crc_28, sec_crc_29, sec_crc_30, sec_crc_31) \
                    VALUES('%s','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d',\
                    '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d')''' %\
                    ('METER_3P',meter_id,int(crc_sector_flash[0]),\
                        int(crc_sector_flash[1]),\
                        int(crc_sector_flash[2]),\
                        int(crc_sector_flash[3]),\
                        int(crc_sector_flash[4]),\
                        int(crc_sector_flash[5]),\
                        int(crc_sector_flash[6]),\
                        int(crc_sector_flash[7]),\
                        int(crc_sector_flash[8]),\
                        int(crc_sector_flash[9]),\
                        int(crc_sector_flash[10]),\
                        int(crc_sector_flash[11]),\
                        int(crc_sector_flash[12]),\
                        int(crc_sector_flash[13]),\
                        int(crc_sector_flash[14]),\
                        int(crc_sector_flash[15]),\
                        int(crc_sector_flash[16]),\
                        int(crc_sector_flash[17]),\
                        int(crc_sector_flash[18]),\
                        int(crc_sector_flash[19]),\
                        int(crc_sector_flash[20]),\
                        int(crc_sector_flash[21]),\
                        int(crc_sector_flash[22]),\
                        int(crc_sector_flash[23]),\
                        int(crc_sector_flash[24]),\
                        int(crc_sector_flash[25]),\
                        int(crc_sector_flash[26]),\
                        int(crc_sector_flash[27]),\
                        int(crc_sector_flash[28]),\
                        int(crc_sector_flash[29]),\
                        int(crc_sector_flash[30]),\
                        int(crc_sector_flash[31]))
                    cur.execute(query)
                    print cur.rowcount
                    conn.commit()
                except Exception as e:
                    print e


    #-----------------------------------------------------
    conn.close()



if __name__ == '__main__': 
    run()
