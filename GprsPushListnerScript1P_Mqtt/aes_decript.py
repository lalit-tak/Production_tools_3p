import sys
from Cryptodome.Cipher import AES
import binascii

# SysTitile = "GPCtitle" #for push
KEY = "bbbbbbbbbbbbbbbb"#for push




def ParsePacket(buf):
    # print "Length of Total Packet:",len(buf)
    # print "Length of E-APDU",buf[6]*256+buf[7]
    # print "SystemTitle",buf[10:10+8]
    # print "Length of C APDU",buf[18]
    # print "Invocation Counter",(buf[20]*256*256*256)+(buf[21]*256*256)+(buf[22]*256)+buf[23]
    # print "Cyphered Data", buf[24:]
        
    SysTitile = buf[10:10+8]
    IV = SysTitile+buf[20:24]
    decryptor = AES.new(key=KEY, mode=AES.MODE_GCM, nonce=IV)
    plaintext = decryptor.decrypt(buf[24:])
    print("Encrypted APDU:",binascii.hexlify(buf[24:]))
    print("Decrypted APDU:",plaintext.encode('hex'))
    return plaintext

    # print "IV",IV
    # print binascii.hexlify(IV)