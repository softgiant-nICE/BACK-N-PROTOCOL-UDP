#!/usr/bin/python

# (c) 2019, softgiant version .  

import argparse
import time
import struct
import os
import sock352
import random

def main():

    # parse all the arguments to the client
    parser = argparse.ArgumentParser(description='CS 352 Socket Server')
    parser.add_argument('-f', '--filename', help='Filename to Receiver', required=False)
    parser.add_argument('-p', '--port', help='CS 352 Socket Port (optional for part 1)', required=False)
    parser.add_argument('-u', '--udpportRx', help='UDP port to use for receiving', required=True)
    parser.add_argument('-v', '--udpportTx', help='UDP port to use for sending', required=False)

    args = vars(parser.parse_args())

    # open the file for writing
    filename = args['filename']
    udpportRx = args['udpportRx']

    if (args['udpportTx']):
        udpportTx = args['udpportTx']
    else:
        udpportTx = ''

    # the port is not used in part 1 assignment, except as a placeholder
    if (args['port']):
        port = args['port']
    else:
        port = 1111

    if (filename):
        try:
            fd = open(filename, "wb")
            usefile = True
        except:
            print ("error opening file: %s" % (filename))
            exit(-1)
    else:
        pass

    # This is where we set the transmit and receive
    # ports the server uses for the underlying UDP
    # sockets. If we are running the client and
    # server on different machines, these ports
    # need to be different, otherwise we can
    # use the same ports
    if (udpportTx):
        sock352.init(udpportTx, udpportRx)
    else:
        sock352.init(udpportRx, udpportRx)

    s = sock352.socket()

    # set the fragment size we will read on
    # MAXFRAGMENTSIZE = 16384

    # binding the host to empty allows reception on
    # all network interfaces
    s.bind(('', port))
    s.listen(5)

    # when accept returns, the client is connected
    (s2, address) = s.accept()

    # this receives the size of the file
    # as a 4 byte integer in network byte order (big endian)
    longPacker = struct.Struct("!L")
    long = s2.recv(4)
    fn = longPacker.unpack(long)
    filelen = fn[0]

    # # the MD5 computes a unique hash for all the data
    # mdhash = md5.new()

    # bytes_to_receive = filelen
    start_stamp = time.process_time()

    # main loop to receive the data from the client 
    # while (bytes_to_receive > 0):
    #     size = random.randrange(1,MAXFRAGMENTSIZE)
    #     if (bytes_to_receive >= size):
    #         # pick a random size to receive
    #         fragment = s2.recv(size)
    #     else: 
    #         fragment = s2.recv(bytes_to_receive)

    #     bytes_to_receive = bytes_to_receive - len(fragment)
    #     fd.write(fragment)
    #for this version, receiving data by one time.
    file = s2.recv(filelen)
    fd.write(file)

    end_stamp = time.process_time() 
    lapsed_seconds = end_stamp - start_stamp

 
    if (lapsed_seconds > 0.0):
        print ("server1: received %d bytes in %0.6f seconds, %0.6f MB/s " % (filelen, lapsed_seconds, (filelen/lapsed_seconds)/(1024*1024)))
    else:
        print ("server1: received %d bytes in %d seconds, inf MB/s " % (filelen, lapsed_seconds))
    fd.close()
    s2.close()
    

# create a main function in Python
if __name__ == "__main__":
    main()
