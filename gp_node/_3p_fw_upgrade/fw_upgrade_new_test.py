import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io_new import FlashIOMasterNew, FlashIOErrorNew
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json
import datetime
import time


START_ADDRESS = 0x0100
METER_ADDRESS = "255.255.255.255" ##"6.0.7.40"

header={
    "magic_number"     : 0,
    "protocol_version" : 0,
    "firmware_version" : 0,
    "allocation_table" : {
                            "storage_address": [],
                            "flash_address"  : [],
                            "data_len"       : [],
                            "data_crc"       : [],
                            "data_index"     : [],
                         },
    "crc"              : 0
}

def header_data(file):
    header["magic_number"]       = file[0]+(file[1]<<8)
    print "magic_number", header["magic_number"]
    header["protocol_version"]   = file[2]+(file[3]<<8)
    print "protocol_version", header["protocol_version"]
    header["firmware_version"]   = file[4]+(file[5]<<8)
    print "firmware_version", header["firmware_version"]

    index = 0
    header["allocation_table"]["storage_address"].append(START_ADDRESS)
    header["allocation_table"]["flash_address"].append(START_ADDRESS)
    header["allocation_table"]["data_len"].append(1484)
    header["allocation_table"]["data_crc"].append(0x0000)
    header["allocation_table"]["data_index"].append(index)

    print 0, "store_addr", hex(START_ADDRESS), "flash_addr", hex(START_ADDRESS),\
         "len", hex(1484), "crc", hex(0x0000), "index", hex(0)
    l = 6
    for b in range(1,124):
        index += header["allocation_table"]["data_len"][b-1]
        store_addr = (file[l])+(file[l+1]<<8)+(file[l+2]<<16)+(file[l+3]<<24)
        if (store_addr > 0):
            store_addr += START_ADDRESS
        header["allocation_table"]["storage_address"].append(store_addr)

        l += 4
        flash_addr = (file[l])+(file[l+1]<<8)+(file[l+2]<<16)+(file[l+3]<<24)
        header["allocation_table"]["flash_address"].append(flash_addr)

        l += 4
        data_len = (file[l])+(file[l+1]<<8)
        header["allocation_table"]["data_len"].append(data_len)

        l += 2
        data_crc = (file[l])+(file[l+1]<<8)
        header["allocation_table"]["data_crc"].append(data_crc)

        l += 2
        header["allocation_table"]["data_index"].append(index)

        print b, "store_addr", hex(store_addr), "flash_addr", hex(flash_addr),\
         "len", hex(data_len), "crc", hex(data_crc), "index", hex(index)
    header["crc"] = file[1482]+(file[1483]<<8)
    print "crc", hex(header["crc"])
    return header

def program(hexfile_payload, hexfile_header, flash_io, flash_sector):
    if flash_sector == 151:
        print "Erasing : BLOCK"
        flash_io.erase(Address(METER_ADDRESS), 0)
        # flash_io.erase(Address("255.255.255.255"), 1)
        # flash_io.erase(Address("255.255.255.255"), 2)
        # flash_io.erase(Address("255.255.255.255"), 3)
        # Here we have to do erase sector command
        for b in range(0,124):
            if hexfile_header["allocation_table"]["data_len"][b] > 0:
                start_addr = hexfile_header["allocation_table"]["storage_address"][b]
                data_len   = hexfile_header["allocation_table"]["data_len"][b]
                data_index = hexfile_header["allocation_table"]["data_index"][b]
                data_load  = hexfile_payload[data_index:data_index+data_len]
                print "Flashing : ", hex(start_addr), hex(data_len),
                print str(b+1)+"/124"
                flash_io.burn(Address(METER_ADDRESS), start_addr, data_load, to_print=True)
            else:
                break
    elif flash_sector < 124:
        flash_sector += 1
        start_addr = hexfile_header["allocation_table"]["storage_address"][flash_sector]
        data_len   = hexfile_header["allocation_table"]["data_len"][flash_sector]
        data_index = hexfile_header["allocation_table"]["data_index"][flash_sector]
        data_load  = hexfile_payload[data_index:data_index+data_len]
        sectorid = start_addr/4096
        print "Erasing Sector: ", hex(start_addr), sectorid
        flash_io.erase(Address(METER_ADDRESS), sectorid, sector_erase = True)
        print "Flashing : ", hex(start_addr), hex(data_len)
        flash_io.burn(Address(METER_ADDRESS), start_addr, data_load, to_print=True)

        if (flash_sector%2) == 0:
            flash_sector += 1
        else:
            flash_sector -= 1
        start_addr = hexfile_header["allocation_table"]["storage_address"][flash_sector]
        data_len   = hexfile_header["allocation_table"]["data_len"][flash_sector]
        data_index = hexfile_header["allocation_table"]["data_index"][flash_sector]
        data_load  = hexfile_payload[data_index:data_index+data_len]
        sectorid = start_addr/4096
        print "Flashing : ", hex(start_addr), hex(data_len)
        flash_io.burn(Address(METER_ADDRESS), start_addr, data_load, to_print=True)
    # flash_io.burn(Address(METER_ADDRESS), START_ADDRESS, hexfile_payload, to_print=True)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action="store", dest="device", 
                        type=str, help="device name, eg. /dev/ttyUSB0")
    parser.add_argument('-b', action="store", dest="baud_rate", 
                        type=str, help="baud rate")
    parser.add_argument('-p', action="store", dest="hex_file", 
                        help="programs new hex file")
    parser.add_argument('-V', action="store", dest="version", 
                        help="options are 'live' and 'ext'")
    parser.add_argument('-t', action="store", dest="timeout",type=int, 
                        help="port time out")
    parser.add_argument("--id",action="store", dest="portID",
                      help="device id")
    parser.add_argument("--sector", action="store", dest="sectorId",type=int,
                      help="Image Transfer of particular sector")
    
    args = parser.parse_args()
    if args.device is None:
        args.device = "/dev/gp-gateway"
    if args.baud_rate is None:
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 3
    if args.portID is None:
        args.portID = 4
    if args.sectorId is None:
        args.sectorId = 151

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, args.portID, "irda")
    starttime = datetime.datetime.now()
    print starttime
    # network_api.enable_print_rxtx(Address(METER_ADDRESS))
    # print "Live Version: ", network_api.get_live_version(Address(METER_ADDRESS))
    if args.hex_file is not None:
        binary_file = open(args.hex_file, "rb")
        block = binary_file.read()
        hexfile_payload = bytearray()
        for ch in block:
            hexfile_payload.append(ch)

        hexfile_header = header_data(hexfile_payload)
        program(hexfile_payload, hexfile_header,
            network_api.my_flash_io_master_new, args.sectorId)
        print network_api.initiate_fw_upgrade(Address(METER_ADDRESS))
        time.sleep(60)
        print network_api.get_bootloader_logs(Address(METER_ADDRESS))
        print network_api.get_live_version(Address(METER_ADDRESS))
        # auto_correct_flag = True
        # while auto_correct_flag:
        #     try:
        #         isupgrade = network_api.initiate_fw_upgrade(Address(METER_ADDRESS))
        #         if isupgrade is "ok":
        #             time.sleep(60)
        #             while True:
        #                 try:
        #                     ext_version = network_api.get_ext_version(Address(METER_ADDRESS))
        #                     print ext_version
        #                     if ext_version is not hexfile_header["firmware_version"]:
        #                         crc_error_table_no = network_api.get_bootloader_logs(Address(METER_ADDRESS))
        #                         program(hexfile_payload, hexfile_header,
        #                             network_api.my_flash_io_master_new, crc_error_table_no+1)
        #                     else:
        #                         auto_correct_flag = False
        #                         break
        #                 except:
        #                     time.sleep(1)
        #                     pass

        #         else:
        #             auto_correct_flag = False
        #     except:
        #         time.sleep(1)
        #         pass


    EndTime = datetime.datetime.now()
    print "\nStartTime:",starttime
    print "EndTime:",EndTime
    print "Diff : ", EndTime - starttime


if __name__ == "__main__":
    run()
