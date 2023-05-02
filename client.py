from utils import *
import http.server
import socketserver


global seq_num
seq_num = 1

class Client:
    def __init__(self):
        self.connectionServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = ("127.0.0.1",9999)
        self.outmessage = None
        self.inmessage = None

    def open_connection(self):
        self.connectionServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = ("127.0.0.1",9999)

    def initializeConnection(self):
        #Sending Syn Message
        #################################################
        ##   TEST CASE 5: SEND INVALID FLAGS change 2  ##
        #################################################
        synMessage = Message(8080, 9999, 0, 0, 5, 0, 2, 1, 0, 0, "")
        self.sendMessage(synMessage)

        # Waiting for Syn Ack Message
        flag = self.receiveMessage(1,18,3)
        if flag == 0:
            return 0
        #SynAck Message recieved
        print("SynAck Message received")
        #Send Ack Message
        ackMessage = Message(8080, 9999, 1, 1, 5, 0, 16, 1, 0, 0, "")
        self.sendMessage(ackMessage)
        return 1
        
    def sendMessage(self,message):
        temp = struct.pack("!HHIIBBHH", message.src_port, message.dest_port, message.seq_num, message.ACK_num, message.data_offset + message.reserved, message.flags, message.window_size, message.urgent_ptr)
        temp2 = temp + message.data.encode('utf-8') 
        #################################################
        ##   TEST CASE 6: Send incorrect checksum      ##
        #################################################
        chksum = calculateChecksum(temp2)
        self.outmessage = struct.pack("!HHIIBBHIH", message.src_port, message.dest_port, message.seq_num, message.ACK_num, message.data_offset + message.reserved, message.flags, message.window_size,chksum ,message.urgent_ptr)
        self.outmessage += message.data.encode('utf-8')
        self.connectionServer.sendto(self.outmessage, self.address)

    def receiveMessage(self,expectedSeqNum,expectedFlags,timer=None):
        try:
            self.connectionServer.settimeout(timer)
            self.inmessage, clientaddress = self.connectionServer.recvfrom(1024)
            udp_header = self.inmessage[:22]
            vector = struct.unpack("!HHIIBBHIH", udp_header)
            Data = self.inmessage[22:]
            udp_header = struct.unpack("!HHIIBBHIH", udp_header)
            ackNum = vector[3]
            flag = vector[5]
            temp = struct.pack("!HHIIBBHH",vector[0],vector[1],vector[2],vector[3],vector[4],vector[5],vector[6],vector[8])
            temp2 = temp + Data
            messageChksum = calculateChecksum(temp2)
            if (ackNum==expectedSeqNum and flag==expectedFlags and vector[7]==messageChksum):
                print("Correct seq Num ... msg received")
                return 1
            else:
                print("invalid")
                return 0
        except socket.timeout:
            print("timeout")
            return 0

    def receiveMessage2(self,expectedSeqNum,expectedFlags,previousMessage=None,timer=None, mode=2):
        try:
            self.connectionServer.settimeout(timer)
            self.inmessage, clientaddress = self.connectionServer.recvfrom(1024)
            udp_header = self.inmessage[:22]
            vector = struct.unpack("!HHIIBBHIH", udp_header)
            Data = self.inmessage[22:]
            udp_header = struct.unpack("!HHIIBBHIH", udp_header)
            ackNum = vector[3]
            flag = vector[5]
            temp = struct.pack("!HHIIBBHH",vector[0],vector[1],vector[2],vector[3],vector[4],vector[5],vector[6],vector[8])
            temp2 = temp + Data
            messageChksum = calculateChecksum(temp2)
            if (ackNum==expectedSeqNum and flag==expectedFlags and vector[7]==messageChksum):
                print("Correct seq Num ... msg received")
                if mode == 1: return 1
                else: return self.inmessage, clientaddress
            else:
                print("incorrect ACK")
                if mode == 1: return 0
                else:
                    self.sendMessage(previousMessage)
                    self.receiveMessage(expectedSeqNum,previousMessage,timer,mode)
        except socket.timeout:
            print("timeout")
            if mode == 1: return 0
            else: 
                self.sendMessage(previousMessage)
                self.receiveMessage(expectedSeqNum,previousMessage,timer,mode)

    def CloseConnection(self):
        #################################################
        ##   TEST CASE 7: invert seq num   from 0 to 1 ##
        #################################################
        synWait = Message(8080, 9999, 0, 0, 5, 0, 1, 1, 0, 0, "")
        self.sendMessage(synWait)
        flag = self.receiveMessage(1,16,3)
        if flag == 0:
            return 0
        #Close wait message recieved
        print("Close wait Message recieved")

        flag = self.receiveMessage(0,1,3)
        if flag == 0:
            return 0
        #Last Ack message recieved
        print("Last Ack Message recieved")

        timedWait = Message(8080, 9999, 0, 0, 5, 0, 16, 1, 0, 0, "")
        #################################################
        ##   TEST CASE 4: COMMENT FOLLOWING LINE       ##
        #################################################
        self.sendMessage(timedWait)
        return 1

class MyHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.client = Client()
        super().__init__(request, client_address, server)

    def setup(self):
        super().setup()
        while self.client.initializeConnection()!=1:
            print("re-initializing connection")
        
    # overwriting the GET method    
    def do_GET(self):
        global seq_num
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)
        seq_num = invertSeqNum(seq_num)
        print("sending msgeeeee")
        synMessage = Message(8080, 9999, seq_num, 15, 5, 3, 0, 1, 1, 1, "")
        self.client.sendMessage(synMessage)
        message, clientPortNumber = self.client.receiveMessage2(seq_num, 0, synMessage)

    # overwriting the POST method
    def do_POST(self):
        global seq_num
        content_length = int(self.headers.get("Content-Length"))
        body = self.rfile.read(content_length).decode()
        HTTP_message = body.split("=")[1]
        self.send_response(200)
        self.end_headers()
        # sending data to server
        seq_num = invertSeqNum(seq_num)
        synMessage = Message(8080, 9999, seq_num, 15, 5, 3, 0, 1, 1, 1, HTTP_message)
        self.client.sendMessage(synMessage)
        print(f"Client sent msg with seq num {seq_num}")
        message, clientPortNumber = self.client.receiveMessage2(seq_num, 0, synMessage)
        print("msg with seq num 0 recieved from client")
        # displaying data on browser
        self.wfile.write(f"Message received: {HTTP_message}".encode())

    def handle(self):
        super().handle()
        while self.client.CloseConnection()!=1:
            print("reclosing connection")
        print("finished")
        

PORT = 8000
HOST = "192.168.1.7"

Handler = MyHandler

with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()