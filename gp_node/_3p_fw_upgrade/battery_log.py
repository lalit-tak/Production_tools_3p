
# paste your output from battery_logs
output = "AA 01 16 21 04 00 00 01 02 04 04 0D 01 07 00 00 01 00 00 00 00 40 92 E0 55 4A B6"

# ----------------------------------------------------------------------------------------------------

temp = output.split(" ")

buf = []

for x in range(12,25):
    buf.append(int(temp[x], 16))

wakeup = {
            0 : 'None', 1 : 'Push Button', 2 : 'C-Open',
            3 : 'NM', 4 : 'WDog reset', 5 : 'Unwanted wakeup'
         }

wakeupReason = {
                0 : 'LLWU_0'  , 1  : 'LLWU_1' , 2  : 'LLWU_2',
                3 : 'LLWU_3'  , 4  : 'LLWU_4' , 5  : 'LLWU_5',
                6 : 'LLWU_6'  , 7  : 'LLWU_7' , 8  : 'LLWU_8',
                9 : 'LLWU_9'  , 10 : 'LLWU_10', 11 : 'LLWU_11',
                12: 'LLWU_12' , 13 : 'LLWU_13', 14 : 'LLWU_14',
                15: 'LLWU_15' , 16 : 'LLWU_16', 17 : 'LLWU_17',
                18: 'LLWU_18' , 19 : 'LLWU_19', 20 : 'LLWU_20',
                21: 'LLWU_21' , 22 : 'LLWU_22', 23 : 'LLWU_23',
                24: 'LPTMR_NM', 25 : 'RTC-ALM', 26 : 'CMP0'   ,
                27: 'IRQ_COPN', 28 : 'CMP1'   , 29 : 'MAINS'  ,
                30: 'PUSH-BTN', 31 : 'LLWU_31'
              }

resetReason = {
                0 : 'LLWU_WAKEUP'  , 1 : 'LOW_VOLT_DETECT' ,
                2 : 'LOSS_OF_CLOCK', 3 : 'LOSS OF PLL'     ,
                5 : 'WATCH_DOG'    , 6 : 'RESET EXT PIN'   ,
                7 : 'POWER_DETECT' , 9 : 'LOCKUP'          ,
                10: 'SYSTEM_RESET' , 11: 'HOST_DEBUGGER'   ,
                13: 'FAILURE_OF_PERIPHERAL(s)'             ,
                4 : 'RESERVED', 8 : 'RESERVED', 12 : 'RESERVED',
                14: 'RESERVED', 15: 'RESERVED'
              }

if buf[12]==0x55:
    print "type                   : valid data"
else:
    print "type                   : invalid data"

print "latest wakeup          : " + wakeup[buf[0]]
print "valid wakeup counts    : " + str(buf[1])
print "wdog reset counts      : " + str(buf[2])
print "unwanted wakeup counts : " + str(buf[3])

resetR  = (buf[5]<<8) + buf[4]
wakeupR = (buf[9]<<24)+(buf[8]<<16)+(buf[7]<<8)+buf[6]

RMSG = []
for i in range(16):
    if resetR & 1<<i:
        RMSG.append(resetReason[i])

WMSG = []
for i in range(32):
    if wakeupR & 1<<i:
        WMSG.append(wakeupReason[i])      

print "total reset reasons    : " + str(hex(resetR))  + " " + str(RMSG)

print "total wakeup reasons   : " + str(hex(wakeupR)) + " " + str(WMSG)