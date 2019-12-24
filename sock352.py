import binascii
import socket as syssock
import struct
import sys
import time
from threading import Thread,Lock 
from math import ceil
from random import randint
# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from
#define constants
SOCK352_SYN = 0x01
SOCK352_FIN = 0x02
SOCK352_ACK =0x04
SOCK352_RESET = 0x08
SOCK352_HAS_OPT = 0xA0
MAX_PAYLOAD_SIZE = 64000
HEADER_LEN = 40
PACKET_SIZE = MAX_PAYLOAD_SIZE + HEADER_LEN
PAYLOAD = 0x03  # payload_len in packet specification, must be 0~255

#  CS 352 RDP v1 packet 
version = 0x1
# opt_ptr = 0x0
protocol = 0x0
checksum = 0x0
recv_port = -1
send_port = -1
header_length = struct.calcsize('!BBBBHHLLQQLL')
sock352PktHdrData = '!BBBBHHLLQQLL' 
ack_no = None
current_seq_no = None
error = False
other_host_addr = None
fin_received = False
current_ack_no = 0
end_sending = False
full_message = ''
MAXFRAGMENT_SIZE = 60000
# window = 0x0


# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from

# this is the thread object that re-transmits the packets 
def recvThread():
    print("Started receiving ack packets for send . . .")
    global current_ack_no
    while not end_sending:
        recv_header = recv_socket.recv(header_length)
        header = struct.unpack(sock352PktHdrData, recv_header)
        current_ack_no = header[9]
    return
class sock352Thread (Thread):
    
    def __init__(self, threadID, name, delay):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = float(delay)
        
    def run(self):
        print("sock352: timeout thread starting %s delay %.3f " % (self.name,self.delay))
        recvThread()
        print("sock352: timeout thread %s Exiting " % (self.name))

#only thing done here is save ports
def init(UDPportTx,UDPportRx):   # initialize your UDP socket here 
    global send_port, recv_port
    send_port = int(UDPportTx)
    recv_port = int(UDPportRx)
# no need when use struct
# def str_to_a32(b):
#     if len(b) % 4:
#         # pad to multiple of 4
#         b += '\0' * (4 - len(b) % 4)
#     return struct.unpack('>%dI' % (len(b) / 4), b)
class socket:
    #initalize socket and fields

    def __init__(self):
        global send_socket, recv_socket
        send_socket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        recv_socket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        recv_socket.bind(('', recv_port))
        print('Returning your new 352-socket!')
        return

    def bind(self, address):
        print("******* Binding process *******\n")
        return
#client side of three way handshake
    def connect(self, address):
        global recv_socket, ack_no, current_seq_no,  other_host_addr
        print("Getting started a conection on %s" % (send_port) )
        other_host_addr = (address[0], send_port)
        #  a new sequence number
        current_seq_no = randint(20, 100)
        #  creating a new packet header with the SYN bit set in the flags and set the other fields (e.g sequence #)
        s_header = self.configureHeader(SOCK352_SYN, current_seq_no, 0, 0)
        send_socket.sendto(s_header, other_host_addr)
        recv_packet = recv_socket.recv(header_length)
        recv_header = struct.unpack(sock352PktHdrData, recv_packet)
        if SOCK352_SYN == recv_header[1] and current_seq_no == recv_header[9]:
            ack_no = recv_header[8]
        else:
            raise RuntimeError("broken socket")
        send_socket.connect(other_host_addr)
        print('Successfully connected')
        return


    def accept(self):
        global recv_socket, ack_no, current_seq_no, other_host_addr
        print('Waiting for a connection on %s\n' % (recv_port) )
        recv_packet, address = recv_socket.recvfrom(header_length)
        other_host_addr = (address[0], send_port)
        new_header = struct.unpack(sock352PktHdrData, recv_packet)
        if SOCK352_SYN == new_header[1]:
            ack_no = new_header[8]
            current_seq_no = randint(20, 100) 
            s_header = self.configureHeader(SOCK352_SYN, current_seq_no, ack_no, 0)
            send_socket.sendto(s_header, other_host_addr)  
            guest_socket = self
        else:
            raise RuntimeError("broken socket by SOCK352_SYN")
        print("Got a connection. Asking for new instance")
        return (guest_socket, other_host_addr)

    def close(self): # fill in your code here 
        # self.socket.settimeout(0.2)
        # send a FIN packet (flags with FIN bit set)
        print("Close the connection")
        terminal_no = randint(7,19)
        # header = self.configureHeader(0x02, terminal_no, 0, 0)
        # SOCK352_ACK = -1
        # while(SOCK352_ACK != terminal_no):
        #     try:
        #         recv_socket.sendto(header, other_host_addr)
        #     except TypeError:
        #         recv_socket.send(header)
        recv_socket.close()

    def listen(self, backlog):
        return

    def send(self, buffer):
        global recv_socket, current_ack_no, end_sending
        current_ack_no = 0
        fragments = 0
        packets = list()
        extra_val = 0
        size = len(buffer)  #a message length
        go_back_n = False
        i = 0
        bytes_sent = 0
        fragment = 0
        is_start = 0
        end_sending = False
        print("Sending data .....")
        if size > MAXFRAGMENT_SIZE:
            fragments = (len(buffer) - (len(buffer) % MAXFRAGMENT_SIZE)) / MAXFRAGMENT_SIZE
            extra_val = len(buffer) % MAXFRAGMENT_SIZE
            size = MAXFRAGMENT_SIZE

        while i <= fragments or go_back_n:
            total_sent = 0
            print('current_ack_no')
            print(current_ack_no)
            print('i')
            print(i)
            if go_back_n:
                i = current_ack_no + 1
                print("GO-BACK-N PROCESSING!")
                size = len(packets[i])
                go_back_n = False
            elif fragments > 0:
                if i == fragments and extra_val > 0:
                    size = extra_val
                    fragment = buffer[bytes_sent:]
                elif i == fragments and extra_val == 0:
                    break
                else:
                    fragment = buffer[bytes_sent:bytes_sent + MAXFRAGMENT_SIZE]  
            else:
                fragment = buffer[:] # reading the whole data from buffer
            if i == len(packets):
                header = self.configureHeader(PAYLOAD, i, 0, size)
                packets.append(header+fragment)
            while total_sent < len(packets[i]):
                sent_num = send_socket.sendto((packets[i])[total_sent:], other_host_addr)
                if sent_num == 0:
                    raise RuntimeError("socket broken")
                else:
                    print("One segment of %d whole bytes was sent." % sent_num)
                    total_sent += sent_num

            if i >= current_ack_no:
                bytes_sent += total_sent - header_length
            if is_start > 0:
                if current_ack_no == i - 1 or current_ack_no == i:
                    is_start = time.time()
                    # print('11111')
                elif current_ack_no > i:
                    # print('22222')
                    i = current_ack_no
                elif current_ack_no < i - 1 and time.time() - is_start >= 0.2:  
                    go_back_n = True
                    # print('33333')
            else:
                is_start = time.time()
                # print('is_start')
                # print(is_start)
                thread1 = sock352Thread(1, "Thread-1", 0.2)
                # exit when the main thread does. 
                thread1.daemon = True
                # run the thread 
                thread1.start()
            i += 1
        end_sending = True
        return bytes_sent



    def recv(self, nbytes):
        global recv_socket, current_seq_no
        print("Starting the recv() function.....")
        i = 0
        fragments = 0
        extra_val = 0
        full_message = b''
        if nbytes > MAXFRAGMENT_SIZE:
            fragments = nbytes / MAXFRAGMENT_SIZE
            extra_val = nbytes % MAXFRAGMENT_SIZE
        print('Total fragment Num: ' + str(fragments))
        if fragments == 0:
            fragment = recv_socket.recv(nbytes+header_length)
            packet, sub_data = fragment[:header_length], fragment[header_length:]
            print('Header length: ' + str(header_length))
            print('Length of  current packet: ' + str(len(packet)))
            packet = struct.unpack(sock352PktHdrData, packet)  
            full_message = sub_data
        while i < int(fragments):
            fragment = ''
            size = MAXFRAGMENT_SIZE + header_length

            while size > 0:
                print('Received data size: ' + str(size) + ' No: ' + str(i))
                if size >= MAXFRAGMENT_SIZE+header_length:
                    fragment = recv_socket.recv(MAXFRAGMENT_SIZE+header_length)
                else:
                    fragment = recv_socket.recv(size)
                    # print('printing  else')
                size -= len(fragment)
                # print('printing  after elif')
            packet, sub_data = fragment[:header_length], fragment[header_length:]
            packet = struct.unpack(sock352PktHdrData, packet)
            if i == packet[8]:
                full_message += sub_data  
                ack_packet = self.configureHeader(SOCK352_ACK, 0, i, 0)
                send_socket.sendto(ack_packet, other_host_addr)
                i += 1
        # print('printing before returnin data')
        if extra_val > 0:
            fragment = ''
            size = extra_val + header_length
            while size > 0:
                if size >= extra_val+header_length:
                    fragment = recv_socket.recv(header_length+extra_val)
                else:
                    fragment = recv_socket.recv(size)
                size -= len(fragment)
                # Getting a packet and message from the fragment
            packet, sub_data = fragment[:header_length], fragment[header_length:]
            packet = struct.unpack(sock352PktHdrData, packet)
            if i == packet[8]:
                full_message += sub_data
                ack_packet = self.configureHeader(SOCK352_ACK, 0, i, 0)
                send_socket.sendto(ack_packet, other_host_addr)
        print("End of receiving")
        return full_message

    def configureHeader(self, flags, seq_no, ack_no, payload_len):
        global recv_socket, sock352PktHdrData, other_host_addr
        packet_header = struct.Struct(sock352PktHdrData)
        return packet_header.pack(version, flags, 0x0, 0x0, header_length, 0x0, 0x0, 0x0, seq_no, ack_no, 0x0, payload_len)

# def scan_for_timeouts(delay):
#     global list_of_all_sockets
#     time.sleep(delay)
#     timeoutCnt = len(list_of_all_sockets) > 0
#     # there is a global socket list, although only 1 socket is supported for now 
#     while timeoutCnt:

#         time.sleep(delay)
#         print(1, 'sock352: Scanning for timeouts')
#         # example 
#         for sock in list_of_all_sockets: 
#             pktDets = sock.sent_sk_buffs
#             for pktDetails in pktDets:
#                 current_time = time.time()
#                 time_diff = float(current_time) - float(pktDetails.transmissionTime)
#                 if time_diff > delay:
#                     sock.transmit(pktDetails)
#         timeoutCnt = len(list_of_all_sockets) > 0

