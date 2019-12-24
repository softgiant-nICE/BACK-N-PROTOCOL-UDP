#!/usr/bin/python

# This is the CS 352 Spring 2017 Client for the 1st programming
# project

# (c) 2017, R. P. Martin, under the GPL version 2. 

import argparse
import time
import struct 
from hashlib import md5
import os 
import sock352

def main():
    
    # parse all the arguments to the client 
    parser = argparse.ArgumentParser(description='CS 352 Socket Server')
    parser.add_argument('-f','--filename', help='Filename to Receiver', required=False)
    parser.add_argument('-p','--port', help='CS 352 Socket Port (optional for part 1)', required=False)
    parser.add_argument('-u','--udpportRx', help='UDP port to use for receiving', required=True)
    parser.add_argument('-v','--udpportTx', help='UDP port to use for sending', required=False)

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
            print ( "error opening file: %s" % (filename))
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
        sock352.init(udpportTx,udpportRx)
    else:
        sock352.init(udpportRx,udpportRx)

    s = sock352.socket()

    # set the buffer size we will read on 
    BUFFERSIZE = 268288

    s.bind(('',port))
    s.listen(5)

    # when accept returns, the client is connected 
    (s2,address) = s.accept() 
    # this receives the size of the file
    # as a 4 byte integer in network byte order (big endian)
    longPacker = struct.Struct("!L")
    long = s2.recv(4)
    fn = longPacker.unpack(long)
    filelen = fn[0]
    mdhash = md5()
    bytes_to_receive = filelen
    start_stamp = time.process_time()
    while (bytes_to_receive > 0):
        if (bytes_to_receive >= BUFFERSIZE): 
            buff = s2.recv(BUFFERSIZE)
        else: 
            buff = s2.recv(bytes_to_receive)
        mdhash.update(buff)
        bytes_to_receive = bytes_to_receive - len(buff)
        fd.write(buff)
    end_stamp = time.process_time() 
    lapsed_seconds = end_stamp - start_stamp
    local_digest = mdhash.digest()
    dl = longPacker.unpack(s2.recv(4))
    digestlen = dl[0]
    remote_digest = s2.recv(digestlen)
    if (len(remote_digest) != digestlen):
        raise RuntimeError("socket error")
    status = "SUCCESS"
    for i, server_byte in enumerate(local_digest):
        client_byte = remote_digest[i]
        if (client_byte != server_byte):
            print( "Failure on digeting at byte %d %c %c " % (i,client_byte,server_byte))
            status = "FAILURE"
    if (lapsed_seconds > 0.0):
        print ("server2: %s : received %d bytes in %0.6f seconds, %0.6f MB/s " % (status,filelen, lapsed_seconds, (filelen/lapsed_seconds)/(1024*1024)))
    else:
        print ("server2: %s : received %d bytes in %d seconds, inf MB/s " % (status,filelen, lapsed_seconds))
    fd.close()
    s2.close()

if __name__ == "__main__":
    main()
