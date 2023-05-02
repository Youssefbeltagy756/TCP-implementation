from utils import *
import time

class Server:
    def __init__(self, portNumber, congestionWindow, ipAddress):
        self.portNumber = portNumber
        self.congestionWindow = congestionWindow
        self.ipAdress = ipAddress
        self.outmessage = None
        self.inmessage = None
        self.address = None
        self.connectionServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connectionServer.bind((self.ipAdress, self.portNumber))

    def open_connection(self):
        self.connectionServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connectionServer.bind((self.ipAdress, self.portNumber))

    def listenToClient(self):
        #waiting for connection
        message, clientPortNumber = self.receiveMessage(0,2)
        if message==0:
            return 0
        # When client sends a SYN Message
        print("Syn Message recieved")
        synAck = Message(9999, clientPortNumber[1], 0, 1, 5, 0, 18, 1, 0, 0, "")
        #################################################
        ##   TEST CASE 1: COMMENT FOLLOWING LINE       ##
        #################################################
        self.sendMessage(synAck)

        #wait for Ack Message
        message,clientPortNumber = self.receiveMessage(1,16,2)
        if message == 0:
            return 0

        #Ack message recieved
        print("ack message rcieved")    
        print("Connection Established ... Wating for request from client")
        return 1

    def sendMessage(self, message):
        temp = struct.pack("!HHIIBBHH", message.src_port, message.dest_port, message.seq_num, message.ACK_num, message.data_offset + message.reserved, message.flags, message.window_size, message.urgent_ptr)
        temp2 = temp + message.data.encode('utf-8') 
        chksum = calculateChecksum(temp2)
        self.outmessage = struct.pack("!HHIIBBHIH", message.src_port, message.dest_port, message.seq_num, message.ACK_num, message.data_offset + message.reserved, message.flags, message.window_size,chksum ,message.urgent_ptr)
        self.outmessage += message.data.encode('utf-8')
        self.connectionServer.sendto(self.outmessage, self.address)

    def receiveMessage(self,expectedSeqNum,expectedFlags,timer=None):
        try:
            self.inmessage, self.address = self.connectionServer.recvfrom(1024)
            udp_header = self.inmessage[:22]
            vector = struct.unpack("!HHIIBBHIH", udp_header)
            Data = self.inmessage[22:]
            udp_header = struct.unpack("!HHIIBBHIH", udp_header)
            seqNum = vector[2]
            flag = vector[5]
            temp = struct.pack("!HHIIBBHH",vector[0],vector[1],vector[2],vector[3],vector[4],vector[5],vector[6],vector[8])
            temp2 = temp + Data
            messageChksum = calculateChecksum(temp2)
            if (seqNum==expectedSeqNum and flag==expectedFlags and vector[7]==messageChksum):
                print("Correct seq Num, flags, checksum ... msg received")
                return self.inmessage,self.address
            else:
                print("incorrect seqNum or flags or checksum ... asking for retransmsion")
                return 0,0
        except socket.timeout:
            print("timeout")
            return 0,0  

    def receiveMessage2(self,expectedSeqNum,expectedFlags, mode=2):
        self.inmessage, self.address = self.connectionServer.recvfrom(1024)
        udp_header = self.inmessage[:22]
        vector = struct.unpack("!HHIIBBHIH", udp_header)
        Data = self.inmessage[22:]
        udp_header = struct.unpack("!HHIIBBHIH", udp_header)
        seqNum = vector[2]
        flag = vector[5]
        temp = struct.pack("!HHIIBBHH",vector[0],vector[1],vector[2],vector[3],vector[4],vector[5],vector[6],vector[8])
        temp2 = temp + Data
        messageChksum = calculateChecksum(temp2)
        if (seqNum==expectedSeqNum and flag==expectedFlags and vector[7]==messageChksum):
            print("Correct seq Num, flags, checksum ... msg received")
            ackmsg = Message(9999, self.address[1], seqNum+1, seqNum, 5, 3, 0, 1, 1, 1, "")
            if mode == 2: self.sendMessage(ackmsg)
            return self.inmessage,self.address
        else:
            print("incorrect seqNum or flags or checksum ... asking for retransmsion")
            if mode == 1: return 0,0
            else:
                ackmsg = Message(9999, self.address[1], seqNum+1, invertSeqNum(seqNum), 5, 3, 0, 1, 1, 1, "")
                self.sendMessage(ackmsg)
                self.receiveMessage(expectedSeqNum,expectedFlags,mode)    

    def closeConnection(self):
        #wating for Fin wait message
        message, clientPortNumber = self.receiveMessage(0,1)
        if message == 0:
            return 0
        print("Fin wait Message recieved")
        closeWait = Message(9999, clientPortNumber[1], 1, 1, 5, 0, 16, 1, 0, 0, "")
        #################################################
        ##   TEST CASE 2: COMMENT FOLLOWING LINE       ##
        #################################################
        self.sendMessage(closeWait)
        time.sleep(1.6)

        lastAck = Message(9999, clientPortNumber[1], 1, 0, 5, 0, 1, 1, 0, 0, "")
        #################################################
        ##   TEST CASE 3: COMMENT FOLLOWING LINE       ##
        #################################################
        self.sendMessage(lastAck)

        #wait for Timed Wait Message
        message,clientPortNumber = self.receiveMessage(0,16,2)
        if message == 0:
            return 0
        #Ack message recieved
        print("timed wait message rcieved")    
        print("Connection Closed")
        return 1


portNumber = 9999 
congestionWindow = 3
ipAddress = "127.0.0.1"
server = Server(portNumber, congestionWindow, ipAddress)
# server.listenToClient()
# server.closeConnection()



seq_num = 1
while True:
    while server.listenToClient()!=1:
        print("re-establishing connection")
    seq_num = invertSeqNum(seq_num)
    message, clientPortNumber = server.receiveMessage2(seq_num, 0, mode=2)
    print(f"Server recieved msg: {message[22:]} with seq num {seq_num}")
    while server.closeConnection()!=1:
        print("retrying to close connection")