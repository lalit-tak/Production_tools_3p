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

    ser = serial.Serial(args.device, args.baud_rate, timeout=int(args.timeout))
    network_api = NetworkAPI(ser, "irda")

    conn = mysql.connect()
    cur = conn.cursor()
    query = "SELECT * FROM crcs WHERE TYPE = '%s' " % ('FW_3P')
    cur.execute(query)
    crc_sector_flash_db = {}
    results = cur.fetchall()
    for row in results:
        for i in range (0,32):
            crc_sector_flash_db[i] = row[i+3]

      # Now print fetched result
    print crc_sector_flash_db
    for i in AddressList_3P:
        crc_string = ""
        addr = str(AddressList_3P[i])
        print "Address string:", addr
        d = addr.split('.')
        meter_id = (int(d[0])<<24)+(int(d[1])<<16)+(int(d[2])<<8)+(int(d[3])<<0)
        query = "SELECT * FROM crcs WHERE TYPE = '%s' AND Address =  '%d'" % ('METER_3P', meter_id)
        cur.execute(query)
        print "No of row :", cur.rowcount
        
        results = cur.fetchall()
        for row in results:
            for i in range (0,32):
                if(crc_sector_flash_db[i] == row[i+3]):
                    print "Sector ", i ,"EQUAL"
                else:
                    print "Sector ", i ,"NOT EQUAL"
                    crc_chnk_mter = []
                    for k in range(0,2):
                        
                        retry_cnt = 3
                        while(retry_cnt):
                            retry_cnt = retry_cnt - 1
                            try:
                                temp_crc_string =  network_api.three_ph_get_crc_bundle(Address(addr),(4096+(i*4096)),64)
                            except Exception as e:
                                print e
                                print addr, "block-0 error, while erasing, count: ", retry_cnt
                            else:
                                retry_cnt = 0
                                #print addr, "got  CRC"
                                crc_chnk_mter +=  _parse_crc(temp_crc_string)
                    #print "sector :", i, "CRC chunk",crc_chnk_mter
                    #----------We got chunck wise CRC also----------------
                    try:
                        k=0
                        print "version no", meter_id,i
                        query = "SELECT * FROM crc_chunk_64 WHERE TYPE = '%s' AND Address =  '%d'" % ('METER_3P', meter_id)
                        cur.execute(query)
                        if(cur.rowcount != 0):
                            query = "DELETE FROM crc_chunk_64 WHERE Address = '%d' AND sector_no = '%d' " % (meter_id,i)
                            cur.execute(query)

                        query = '''INSERT INTO crc_chunk_64 (TYPE,Address,sector_no,\
                        chnk_crc_00,chnk_crc_01,chnk_crc_02,chnk_crc_03,chnk_crc_04,chnk_crc_05,chnk_crc_06,chnk_crc_07,\
                        chnk_crc_08,chnk_crc_09,chnk_crc_10,chnk_crc_11,chnk_crc_12,chnk_crc_13,chnk_crc_14,chnk_crc_15,\
                        chnk_crc_16,chnk_crc_17,chnk_crc_18,chnk_crc_19,chnk_crc_20,chnk_crc_21,chnk_crc_22,chnk_crc_23,\
                        chnk_crc_24,chnk_crc_25,chnk_crc_26,chnk_crc_27,chnk_crc_28,chnk_crc_29,chnk_crc_30,chnk_crc_31,\
                        chnk_crc_32,chnk_crc_33,chnk_crc_34,chnk_crc_35,chnk_crc_36,chnk_crc_37,chnk_crc_38,chnk_crc_39,\
                        chnk_crc_40,chnk_crc_41,chnk_crc_42,chnk_crc_43,chnk_crc_44,chnk_crc_45,chnk_crc_46,chnk_crc_47,\
                        chnk_crc_48,chnk_crc_49,chnk_crc_50,chnk_crc_51,chnk_crc_52,chnk_crc_53,chnk_crc_54,chnk_crc_55,\
                        chnk_crc_56,chnk_crc_57,chnk_crc_58,chnk_crc_59,chnk_crc_60,chnk_crc_61,chnk_crc_62,chnk_crc_63)\
                        VALUES('%s','%d','%d',\
                        '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d',\
                        '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d',\
                        '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d',\
                        '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d')'''%('METER_3P',meter_id,i,\
                            int(crc_chnk_mter[0]),int(crc_chnk_mter[1]),int(crc_chnk_mter[2]),int(crc_chnk_mter[3]),\
                            int(crc_chnk_mter[4]),int(crc_chnk_mter[5]),int(crc_chnk_mter[6]),int(crc_chnk_mter[7]),\
                            int(crc_chnk_mter[8]),int(crc_chnk_mter[9]),int(crc_chnk_mter[10]),int(crc_chnk_mter[11]),\
                            int(crc_chnk_mter[12]),int(crc_chnk_mter[13]),int(crc_chnk_mter[14]),int(crc_chnk_mter[15]),\
                            int(crc_chnk_mter[16]),int(crc_chnk_mter[17]),int(crc_chnk_mter[18]),int(crc_chnk_mter[19]),\
                            int(crc_chnk_mter[20]),int(crc_chnk_mter[21]),int(crc_chnk_mter[22]),int(crc_chnk_mter[23]),\
                            int(crc_chnk_mter[24]),int(crc_chnk_mter[25]),int(crc_chnk_mter[26]),int(crc_chnk_mter[27]),\
                            int(crc_chnk_mter[28]),int(crc_chnk_mter[29]),int(crc_chnk_mter[30]),int(crc_chnk_mter[31]),\
                            int(crc_chnk_mter[32]),int(crc_chnk_mter[33]),int(crc_chnk_mter[34]),int(crc_chnk_mter[35]),\
                            int(crc_chnk_mter[36]),int(crc_chnk_mter[37]),int(crc_chnk_mter[38]),int(crc_chnk_mter[39]),\
                            int(crc_chnk_mter[40]),int(crc_chnk_mter[41]),int(crc_chnk_mter[42]),int(crc_chnk_mter[43]),\
                            int(crc_chnk_mter[44]),int(crc_chnk_mter[45]),int(crc_chnk_mter[46]),int(crc_chnk_mter[47]),\
                            int(crc_chnk_mter[48]),int(crc_chnk_mter[49]),int(crc_chnk_mter[50]),int(crc_chnk_mter[51]),\
                            int(crc_chnk_mter[52]),int(crc_chnk_mter[53]),int(crc_chnk_mter[54]),int(crc_chnk_mter[55]),\
                            int(crc_chnk_mter[56]),int(crc_chnk_mter[57]),int(crc_chnk_mter[58]),int(crc_chnk_mter[59]),\
                            int(crc_chnk_mter[60]),int(crc_chnk_mter[61]),int(crc_chnk_mter[62]),int(crc_chnk_mter[63]) )
                        cur.execute(query)
                        conn.commit()

                    except Exception as e:
                        print e
    #-----------------------------------------------------
    conn.close()



if __name__ == '__main__': 
    run()
