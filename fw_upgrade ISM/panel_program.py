import os
import threading
import json
import serial
import datetime
import  time
import multiprocessing
def program(port,baudrate,ser_timeout, hex_file):

    programming_str = "python fw_upgrade.py -d " + str(port) + " -b " + \
                        str(baudrate) +  " -p " + str(hex_file) #+ " -t " + str(ser_timeout)
    print(programming_str)
    try:
        os.system(programming_str)
    except Exception as e:
        print("Programming file issue : ", str(e))
    print(port," : Programming....")

def run():

    PORT = {}
    with open("port_config.json", 'r+') as file:
        json_data = file.read()
        file.close()
        try:        
            fw_json = json.loads(json_data)

            PORT[0] = fw_json["PORT18"]
            PORT[1] = fw_json["PORT2"]
            PORT[2] = fw_json["PORT3"]
            PORT[3] = fw_json["PORT4"]
            PORT[4] = fw_json["PORT5"]
            PORT[5] = fw_json["PORT6"]
            PORT[6] = fw_json["PORT7"]
            PORT[7] = fw_json["PORT8"]
            PORT[8] = fw_json["PORT9"]
            PORT[9] = fw_json["PORT10"]
            timeout = int(fw_json["timeout"])
            baudrate = int(fw_json["baudrate"])
            hex_file_name = fw_json["hex_file"]
        
        except Exception as e:
            print("Configuration file corrupted, ERROR: ", str(e))
        else:
            jobs = []
            NUMBER_OF_SESSIONS=2
            for i in range( NUMBER_OF_SESSIONS ):
                p = multiprocessing.Process(target=program,
                                            argument=port[0],9600,3,out.bin)
                jobs.append(p)
                p.start()
            
           


            # for x in xrange(0,len(PORT)):
            #     print "I am here 2"
            #     t1 = threading.Thread(target=program,args = (PORT[x], baudrate, timeout, hex_file_name))
            #     t1.start()
            #     # t1.join()
                

if __name__ == "__main__":
    run()
    

