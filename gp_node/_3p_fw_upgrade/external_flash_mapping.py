import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._3p.flash_io import FlashIOMaster_3P, FlashIOError_3P
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json
import datetime
import time
import logging
import dateutil.parser
class externalFlashMapping:
    SIZE_OF_SECTOR                                = 4096

    #Load Survey App
    BLOCK_PROFILE_NO_OF_SECTORS                   = 180
    BLOCK_PROFILE_FLASH_START_ADDRESS             = 0x00021000
    BLOCK_PROFILE_LENGTH                          = 44

    DAILY_PROFILE_NO_OF_SECTORS                   = 9
    DAILY_PROFILE_FLASH_START_ADDRESS             = (BLOCK_PROFILE_FLASH_START_ADDRESS + ((BLOCK_PROFILE_NO_OF_SECTORS + 3)*SIZE_OF_SECTOR))
    DAILY_PROFILE_LENGTH                          = 20

    # Event Record App**/
    EVENT_RECORD_NO_OF_SECTORS                    = 3
    EVT_RD_VOLTAGE_RLTD_START_ADDRESS             = (DAILY_PROFILE_FLASH_START_ADDRESS + ((DAILY_PROFILE_NO_OF_SECTORS + 3)*SIZE_OF_SECTOR))
    EVT_RD_CURRENT_RLTD_START_ADDRESS             = (EVT_RD_VOLTAGE_RLTD_START_ADDRESS + ((EVENT_RECORD_NO_OF_SECTORS + 3)*SIZE_OF_SECTOR))
    EVT_RD_POWER_RLTD_START_ADDRESS               = (EVT_RD_CURRENT_RLTD_START_ADDRESS + ((EVENT_RECORD_NO_OF_SECTORS + 3)*SIZE_OF_SECTOR))
    EVT_RD_TRANSACTION_RLTD_START_ADDRESS         = (EVT_RD_POWER_RLTD_START_ADDRESS + ((EVENT_RECORD_NO_OF_SECTORS + 3)*SIZE_OF_SECTOR))
    EVT_RD_OTHERS_RLTD_START_ADDRESS              = (EVT_RD_TRANSACTION_RLTD_START_ADDRESS + ((EVENT_RECORD_NO_OF_SECTORS + 3)*SIZE_OF_SECTOR))
    EVT_RD_NON_ROLLOVER_RLTD_START_ADDRESS        = (EVT_RD_OTHERS_RLTD_START_ADDRESS + ((EVENT_RECORD_NO_OF_SECTORS + 3)*SIZE_OF_SECTOR))
    EVT_RD_CONTROL_RLTD_START_ADDRESS             = (EVT_RD_NON_ROLLOVER_RLTD_START_ADDRESS + ((EVENT_RECORD_NO_OF_SECTORS + 3)*SIZE_OF_SECTOR))
    EVENT_RECORD_LENGTH                           = 44

    # Billing Profile App **

    BILLING_PROFILE_NO_SECTORS                    = 3
    BILLING_PROFILE_FLASH_START_ADDRESS           = (EVT_RD_CONTROL_RLTD_START_ADDRESS + ((EVENT_RECORD_NO_OF_SECTORS+3)*SIZE_OF_SECTOR))
    BILLING_PROFILE_ENTRY_LEN                     = 36
    BILLING_PROFILE_HISTORY_FLASH_START_ADDRESS   = (BILLING_PROFILE_FLASH_START_ADDRESS + ((BILLING_PROFILE_NO_SECTORS+3)*SIZE_OF_SECTOR))
    BILLING_PROFILE_HISTORY_ENTRY_LEN             = 44

    # Activity Calendar *
    ACTIVITY_CALENDAR_SECTORS                     = 2
    ACTIVE_CALENDAR_STRT_ADDR                     = (BILLING_PROFILE_HISTORY_FLASH_START_ADDRESS + ((BILLING_PROFILE_NO_SECTORS + 3)*SIZE_OF_SECTOR))
    PASSIVE_CALENDAR_STRT_ADDR                    = (ACTIVE_CALENDAR_STRT_ADDR + SIZE_OF_SECTOR)


    #UI App *
    UI_CONFIG_LENGTH                              = 1
    UI_CONFIG_SECTOR_ADDRESS                      = (PASSIVE_CALENDAR_STRT_ADDR + SIZE_OF_SECTOR)



def run():



    starttime = datetime.datetime.now()

    print "DLMS to TAP"
    #print network_api.three_ph_meter_dlms_to_tap(Address("0.0.0.255"))
    EndTime = datetime.datetime.now()
    print "StartTime:",starttime
    print "EndTime:",EndTime
    print "Diff : ", EndTime - starttime

    #if not isinstance(EndTime, datetime.datetime):
            #EndTime = dateutil.parser.parse(EndTime)

    unix_time_zero = datetime.datetime(1970, 1, 1)
    seconds_since_epoch = int((EndTime - unix_time_zero).total_seconds())
    print EndTime
    print seconds_since_epoch

    a = datetime.date(2007, 12, 5)
    b = datetime.date(2007, 12, 3)
    print a.month
    print a,b, a-b

    nine_hours_from_now = datetime.datetime.now() + datetime.timedelta(seconds = 864008365)
    print nine_hours_from_now



if __name__ == "__main__":
    run()