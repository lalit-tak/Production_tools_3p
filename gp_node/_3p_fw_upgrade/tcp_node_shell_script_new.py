import contextlib
import socket
import serial
import time
import crc16
import datetime
import sys

print "Opened serial COM2 for listening from node-shell"
ser=serial.Serial("COM2",9600)

host = "::"
port = 9999
try:
    host = input("Enter IPv6 IP: ")
    port = input("Enter Port: ")
except Exception as err:
    print ( "Error" + str(err) )
    sys.exit()
# -----------------------------------------------------

try:
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    print "trying to connect with ", host, port
    s.connect((host, port))
    print "Connected to ", host, port
    msg = 0
    while True:
        if ser.inWaiting() > 0:
            tmp_buf=bytearray()
            while ser.inWaiting() > 0:
                tmp_buf.extend(ser.read())

            currentTS = datetime.datetime.now()
            print(currentTS.strftime("%c"))
            print ("TCP_OUT>>" , "Len : ", len(tmp_buf), [hex(f) for f in tmp_buf])
            s.send(tmp_buf)
            # msg, addr = s.recvfrom(540)
            try:
                s.settimeout(5.0)
                msg = s.recv(1024)
            except:
                print "Recv timeout"
                pass
            if msg:
                tmp_buf=bytearray(msg)
                print ("TCP_IN<<" , "Len : ", len(tmp_buf), [hex(f) for f in tmp_buf])
                data = tmp_buf
                data_len = len(data)
                dcu_number = (data[data_len-4]<<24)+(data[data_len-3]<<16)+(data[data_len-2]<<8)+(data[data_len-1])
                print "Meter Number: ", dcu_number
                try:
                    pckt = bytearray()
                    start_byte = 0
                    byteF = True
                    while(byteF):
                        if(data[start_byte] == 0xAA):
                            byteF = False
                    for b in range(start_byte,start_byte+11):
                        pckt.append(data[b])
                    pckt_len = data[start_byte+11]
                    response_ok = True
                    if (pckt_len >= 4):
                        pckt_len = pckt_len - 4
                        response_ok = False
                    pckt.append(pckt_len)
                    if response_ok == False:
                        for b in range(start_byte+12,start_byte+12+pckt_len):
                            pckt.append(data[b])
                    else:
                        for b in range(start_byte+12,start_byte+12+pckt_len):
                            pckt.append(data[b])
                        # response_o = "o"
                        # pckt.append(response_o)
                        # response_o = "k"
                        # pckt.append(response_o)
                    #CRC is calculated for even bytes to be in sync with the embedded part
                    #If data bytes is odd.'0' is appended and then CRC is calculated
                    if (len(pckt[1:]) % 2) != 0:
                        pckt.append(0)
                        crc = crc16.crc16xmodem(str(pckt[1:]))
                        pckt = pckt[:-1]
                    else:
                        crc = crc16.crc16xmodem(str(pckt[1:]))
                    crc_l = crc/256
                    crc_h = crc%256
                    pckt.append(crc_l)
                    pckt.append(crc_h)
                    print ( "\nSend to node-shell >>" ),
                    ser.write(pckt)
                    print ( [hex(f) for f in bytearray(pckt)] )
                except Exception as err:
                    print ("Error: ", err)
                # ser.write(tmp_buf)
                msg = 0
except Exception as err:
    print ( "Error" + str(err) )
    sys.exit()