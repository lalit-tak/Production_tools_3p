import paho.mqtt.client as paho
import datetime
import binascii
import time
import crc16
import struct
from gp_node.network.protocols.packets._1p.bundle_1p import DCUBundlePacket
from gp_node.network.protocols.packets._1p.bundle import Bundle
import gp_node.utils.serialize as serialize

try:
    tmp = raw_input("Enter Meter S.No : ")
    meter_number = int(tmp)
    print ("Meter S.No : ", meter_number)
except:
    meter_number = 0xFFFFFFFF
    print ("Meter S.No : All")
    pass

# Define event callbacks
def on_connect(client, mosq, obj, rc):
    print ("rc: ", rc )

def on_message(mosq, obj, msg):
    # data = bytearray(msg.payload)
    # data_len = len(data)
    # dcu_number = (data[data_len-4]<<24)+(data[data_len-3]<<16)+(data[data_len-2]<<8)+(data[data_len-1])
    # if(dcu_number == int(meter_number)):
    #     timestamp = datetime.datetime.now()
    #     print "\n"
    #     print ( "dcu_number: ", dcu_number),
    # print ( "topic: ",msg.topic ),
    #     print ( "Tx from DCU << " + str(datetime.datetime.now().replace(microsecond=0)) ),
    # print ( [hex(f) for f in bytearray(msg.payload)] )
    try:
        dcu_number = 0
        packet = bytearray(msg.payload)
        packet_len = len(packet)

        packet_found_f = False
        if packet_len > 14:
            for b in range(0,packet_len-13):
                if packet[b] == 0xAA:
                    packet = packet[b:]
                    packet_len = len(packet)
                    packet_found_f = True
                    break

        if packet_found_f:
            dcu_number = (packet[packet_len-4]<<24)+(packet[packet_len-3]<<16)+\
                         (packet[packet_len-2]<<8) +(packet[packet_len-1])
            if (dcu_number == meter_number) or (0xFFFFFFFF == meter_number):
                src_addr  = str(packet[1]) + "."+ str(packet[2]) + "."+ str(packet[3]) + "."+ str(packet[4])
                dest_addr = str(packet[5]) + "."+ str(packet[6]) + "."+ str(packet[7]) + "."+ str(packet[8])
                data_len  = packet[11]-4
                data_packet = packet[12:12+data_len]
                data_time = serialize.deserialize_uint32(packet[12+data_len:12+data_len+4])
                data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(data_time))

                timestamp = datetime.datetime.now()
                print ( "System time   : ", str(datetime.datetime.now().replace(microsecond=0)) )
                print ( "Topic         : ", msg.topic )
                print ( "Meter_number  : ", dcu_number)
                print ( "Meter address : ", src_addr)
                print ( "Meter Time    : ", data_time)
                print ( "payload len   : ", data_len)
                if dest_addr == '1.78.143.201':
                    bdl = Bundle()
                    try:
                        bdl.deserialize_push(data_packet)
                        print bdl.get_push_bundle(data_packet)
                    except Exception as err:
                        print ("Error: ", err)
                elif dest_addr == '111.110.234.1':
                    bdl = DCUBundlePacket()
                    try:
                        bdl.deserialize_packet_bundle(data_packet)
                        print bdl.get_packet_bundle()
                    except Exception as err:
                        print ("Error: ", err)
                else:
                    print ( [int(f) for f in packet] )
                print ("--- \n")


    except Exception as err:
        print ("Error: ", err)
        pass


# def on_message(mosq, obj, msg):
#     # if(msg.topic == "gp211975"):
#     #     timestamp = datetime.datetime.now()
#     #     print "\n"
#     #     print ( "topic: ",msg.topic ),
#     #     print ( "Rx on DCU << " + str(datetime.datetime.now().replace(microsecond=0)) ),
#     #     print ( [hex(f) for f in bytearray(msg.payload)] )
#     #     return
#     data = bytearray(msg.payload)
#     data_len = len(data)
#     dcu_number = (data[data_len-4]<<24)+(data[data_len-3]<<16)+(data[data_len-2]<<8)+(data[data_len-1])
#     if(dcu_number == int(meter_number)):
#         timestamp = datetime.datetime.now()
#         print "\n"
#         print ( "dcu_number: ", dcu_number),
#         print ( "topic: ",msg.topic ),
#         print ( "Tx from DCU << " + str(datetime.datetime.now().replace(microsecond=0)) ),
#         print ( [hex(f) for f in bytearray(msg.payload)] )
#         try:
#             pckt = bytearray()
#             start_byte = 0
#             byteF = True
#             while(byteF):
#                 if(data[start_byte] == 0xAA):
#                     byteF = False
#             for b in range(start_byte,start_byte+11):
#                 pckt.append(data[b])
#             pckt_len = data[start_byte+11]
#             response_ok = True
#             if (pckt_len >= 4):
#                 pckt_len = pckt_len - 4
#                 response_ok = False
#             pckt.append(pckt_len)
#             if response_ok == False:
#                 for b in range(start_byte+12,start_byte+12+pckt_len):
#                     pckt.append(data[b])
#             else:
#                 for b in range(start_byte+12,start_byte+12+pckt_len):
#                     pckt.append(data[b])
#                 # response_o = "o"
#                 # pckt.append(response_o)
#                 # response_o = "k"
#                 # pckt.append(response_o)
#             #CRC is calculated for even bytes to be in sync with the embedded part
#             #If data bytes is odd.'0' is appended and then CRC is calculated
#             if (len(pckt[1:]) % 2) != 0:
#                 pckt.append(0)
#                 crc = crc16.crc16xmodem(str(pckt[1:]))
#                 pckt = pckt[:-1]
#             else:
#                 crc = crc16.crc16xmodem(str(pckt[1:]))
#             crc_l = crc/256
#             crc_h = crc%256
#             pckt.append(crc_l)
#             pckt.append(crc_h)
#             print ( "\nSend to node-shell >>" ),
#             # ser.write(pckt)
#             print ( [hex(f) for f in bytearray(pckt)] )
#         except Exception as err:
#             print ("Error: ", err)
#     else:
#         print ( "dcu_number: ", dcu_number),
#         print ( "topic: ",msg.topic )

def on_subscribe(mosq, obj, mid, granted_qos):
    print ( "Subscribed: ", mid, " ", granted_qos )
    print ("\n")

def run():
    print ( "Initialization of Script to connect node-shell(COM1) to meter on mqtt ..." )
    # ser=serial.Serial('COM2',9600, timeout = 3)
    while True:
        try:
            mqttc = paho.Client()
            # Assign event callbacks
            mqttc.on_message = on_message
            mqttc.on_connect = on_connect
            mqttc.on_subscribe = on_subscribe
            # Connect
            print ( "connect to username: gpbroker and pass: grampower4321@" )
            mqttc.username_pw_set('gpbroker', 'grampower4321@')
            print ( "connecting...." )
            mqttc.connect('broker.grampower.com', 1883)
            # Start subscribe, with QoS level 0
            if (meter_number > 9999) and (meter_number < 100000):
                # print ( "Subscribe to : ipcl/vdcuDataPushingTPWM, vdcuCollectionTPWM, vdcuRCTPWM, gpxxxxxx")
                # mqttc.subscribe([("ipcl/vdcuDataPushingTPWM", 1),("vdcuCollectionTPWM", 1),("vdcuRCTPWM", 1), (pub_topic, 1)])
                print ("Subscribe to : ipcl/vdcuDataPushingTPWM")
                mqttc.subscribe("ipcl/vdcuDataPushingTPWM", 1)
            else:
                print ( "Subscribe to : gpgprsTAPPush, gpgprsCollectionTPWM" )
                mqttc.subscribe([("gpgprsCollectionTPWM", 1), ("gpgprsTAPPush", 1)])

            # mqttc.subscribe([("vdcuRCTPWM", 1),("vdcuDataPushingTPWM", 1),("gp211975", 1),("vdcuCollectionTPWM", 1)])
            # Data Collection Topic:vdcuCollectionTPWM
            # Data Pushing Topic:vdcuDataPushingTPWM
            # Remote Command Topic:vdcuRCTPWM
            print ( "waiting...." )
            # Continue the network loop, exit when an error occurs
            rc = 0
            while rc == 0:
                # tmp_buf=bytearray()
                # if ser.inWaiting() > 0:
                #     while ser.inWaiting() > 0:
                #         tmp_buf.extend(ser.read())
                #     print ( "\nRx from node-shell << " + str(datetime.datetime.now().replace(microsecond=0)) ),
                #     print ( [hex(f) for f in tmp_buf] )
                rc = mqttc.loop()
                # time.sleep(3)
                # if(len(tmp_buf) > 0):
                #     mqttc.publish(pub_topic, tmp_buf)
                #     print ( "Send to meter on mqtt:",pub_topic,">>" )
                # publish(mqttc)
            print ( "rc: ", rc )
        except Exception as err:
            print ( "Error" + str(err) )
            pass
        time.sleep(1)

run()

