#!/usr/bin/python

# This is the CS 352 Spring 2017 Client for the 1st programming
# project

# (c) 2019, Ankit version . 

import argparse
import time
import struct
from hashlib import md5
import os
import sock352


def main():
    # parse all the arguments to the client
    parser = argparse.ArgumentParser(description='CS 352 Socket Client')
    parser.add_argument('-f', '--filename', help='File to Send', required=False)
    parser.add_argument('-d', '--destination', help='Destination IP Host', required=True)
    parser.add_argument('-p', '--port', help='remote sock352 port', required=False)
    parser.add_argument('-u', '--udpportRx', help='UDP port to use for receiving', required=True)
    parser.add_argument('-v', '--udpportTx', help='UDP port to use for sending', required=False)

    # get the arguments into local variables
    args = vars(parser.parse_args())
    filename = args['filename']
    destination = args['destination']
    udpportRx = args['udpportRx']

    if (args['udpportTx']):
        udpportTx = args['udpportTx']
    else:
        udpportTx = ''

    # the port is not used in part 1 assignment, except as a placeholder
    if (args['port']):
        port = args['port']
    else:
        port = 5555

    # open the file to send to the server for reading
    if (filename):
        try:
            filesize = os.path.getsize(filename)
            fd = open(filename, "rb")
            usefile = True
        except:
            print ("error opening file: %s" % (filename))
            exit(-1)
    else:
        pass

    # This is where we set the transmit and receive
    # ports the client uses for the underlying UDP
    # sockets. If we are running the client and
    # server on the same machine, these ports
    # need to be different. If they are running on
    # different machines, we can re-use the same
    # ports. 
    if (udpportTx):
        sock352.init(udpportTx, udpportRx)
    else:
        sock352.init(udpportRx, udpportRx)

    # create a socket and connect to the remote server
    s = sock352.socket()
    s.connect((destination, port))
    #mesure the start stamp
    start_stamp = time.process_time()
    #load the whole file into memory
    whole_file = fd.read()
    #mesure its length
    filesize = len(whole_file)
    longPacker = struct.Struct("!L")
    fileLenPacked = longPacker.pack(filesize);
    s.send(fileLenPacked)

    sent = s.send(whole_file)
    if (sent != filesize):
        raise RuntimeError("socket broken")

    end_stamp = time.process_time() 
    lapsed_seconds = end_stamp - start_stamp
    
    if (lapsed_seconds > 0.0):
        print ("client1: sent %d bytes in %0.6f seconds, %0.6f MB/s " % (filesize, lapsed_seconds, (filesize/lapsed_seconds)/(1024*1024)))
    else:
        print ("client1: sent %d bytes in %d seconds, inf MB/s " % (filesize, lapsed_seconds))        

    fd.close()
    s.close()
# this gives a main function in Python
if __name__ == "__main__":
    main()