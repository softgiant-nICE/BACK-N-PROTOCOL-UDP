created by softgiant....
This is 352 Reliable Data Protocol (RDP) version 1 (352 RDP v1) which is based on UDP, but functions samely like TCP.

#################################################
It contains three files, server2.py, client2.py and sock352.py.

#################################################
The building system is Python 3.7.4.
sock352.py is a library which contains some functions for implementing CS 352 sockets.
Here, the data packet is as follows:
udpPkt_hdr_data = struct.Struct(sock352PktHdrData) header = udpPkt_header_data.pack(version, flags, opt_ptr, protocol, checksum, source_port, dest_port, sequence_no, ack_no, window, payload_len) 

#################################################
To run this programe, execute the following codes in order.

server2.py -f savedFile.pdf -​u 8888 -​v 9999 
client2.py -d localhost ​-f sendFile.pdf -​u 9999 -​v 8888 

#################################################
This program functions as follows:
1. After running server2.py, it prints a connection messsage and waits for connection with the client. 
2. When executing client2.py, the client searches for the given port and tries to connect to the server.
Here, the client tries to send a flag, SOCK352_SYN, current_seq_no via connect function and receive these values and
ack_no from the server's response. The Server responds to this request with the return of the 3 values above via accept function.
3. After making connection with the server, the client starts to send and receive data.
Unlike UDP, the most important thing here is that this data transition is relialbe data transition which means the server and
client communicate one anothe during data transition via a variable, ack_no.
There are 2 problems which should be considered.
In the case when the buffer is empty, the function, recv() is called.
In the case when the buffer is filled (when there is no room), the function, send() is called.
These issues should be controlled in this protocol.
4. For this lossless data transition, A thread and GO-BACK-N method were used.
A new thread which is produced by the function, send() is responsible for accepting the varialbe, ack_no until the client
thread is terminated. If current iteration is far away from ack_no or timeouts is larger than 0.2s, then GO-BACK-N process
is done to avoid data loss.
The server main thread sends the reasonable ack_no after receiving a segment from client.
5. Through this process, after sending and receiving the whole data, the client and server thread are terminated simultaneously..
When the server and client thread are started, we use syssock.SOCK_DGRAM rather than syssock.SOCK_STREAM which is used for TCP
process.
We did one extra experiment in which BUFFERSIZE=262kb were set in client and server fiies.
In this case, it works fine, but the problem is that low speed.
Although this RDP protocol needs more execution time compared to TCP, it is very useful as this is lossless coummincation.
