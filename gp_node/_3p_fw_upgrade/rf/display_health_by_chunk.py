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
    conn = mysql.connect()
    cur = conn.cursor()
    query = "SELECT * FROM crcs WHERE TYPE = '%s' " % ('FW_3P')
    cur.execute(query)
    crc_sector_flash_db = {}
    results = cur.fetchall()
    for row in results:
        for i in range (0,32):
            crc_sector_flash_db[i] = row[i+3]


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
        no_of_corrupted_chunk = 0
        for row in results:
            for i in range (0,32):
                if(crc_sector_flash_db[i] == row[i+3]):
                    print "Sector ", i ,"EQUAL"
                else:
                    query = "SELECT * FROM crc_chunk_64 WHERE TYPE = '%s' AND sector_no = '%d' " % ('FW_3P',i)
                    cur.execute(query)
                    crc_chnk_flash_db = {}
                    results = cur.fetchall()
                    for row in results:
                        for k in range (0,64):
                            crc_chnk_flash_db[k] = row[k+3]
                    print "Sector ", i ,"NOT EQUAL"
                    query = "SELECT * FROM crc_chunk_64 WHERE Address = '%d' AND sector_no = '%d' " % (meter_id,i)
                    cur.execute(query)
                    #print "No of row :", cur.rowcount
                    results = cur.fetchall()
                    if(cur.rowcount==1):
                        for row in results:
                            for m in range (0,64):
                                #print crc_chnk_flash_db[m],row[m+3]
                                if(crc_chnk_flash_db[m] == row[m+3]):
                                    #print "Chunk ", m ,"EQUAL"
                                    pass
                                else:
                                    no_of_corrupted_chunk = no_of_corrupted_chunk + 1
                                    #pass
                                    #print "Chunk ", m ,"NOT EQUAL"
                    else:
                        print "Not Available",i,"Sector"

            print "No of correpted sector :",no_of_corrupted_chunk, addr




    #-----------------------------------------------------
    conn.close()



if __name__ == '__main__': 
    run()
