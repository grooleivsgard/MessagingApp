#CSC3002F Assignment 1: Server
import socket
import threading
import queue

class Server(threading.Thread):

    #Initialises the server object
    def __init__(self, host, port1, port2, port3, port4):
        self.host = host
        self.registerPort = port1
        self.receivePort = port2
        self.sendPort = port3
        self.dsplPort = port4
        self.FORMAT = 'utf-8'
        self.MENU = "Press 'd' to display online users"
        self.clientsOnline = ""
        self.clients = [] #List of clients connected to the server as Client objects (see below)
        self.dataQueue = queue.Queue() #FIFO queue of data sent my clients
        self.recpQueue = queue.Queue() #FIFO queue of recipients where data should be sent

    #Opens a socket and binds it to the IP and port number contained in the server object
    def run(self):
        print(f"[SERVER ACTIVE ON IP {self.host}] The Server is ready to receive...")
        for i in range(len(self.clients)):
            clientsOnline = clientsOnline + '\n' + self.clients[i].name #Creates a string displaying all the clients connected to the user. For use later    
        regThread = threading.Thread(target=self.register) #Starts the thread that registers the clients on the server
        regThread.start()
        dsplThread = threading.Thread(target=self.displayClients) #Starts the thread that displays the clients on the server
        dsplThread.start()
        recvThread = threading.Thread(target=self.receive) #Start the thread which receives messages
        recvThread.start()
        sendThread = threading.Thread(target=self.sendMsg) #Starts the thread which sends messages to clients
        sendThread.start()

    #Registers the client's name and address (IP + port number)
    def register(self):
        regSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            regSocket.bind((self.host, self.registerPort))
        except socket.error as e:
            print(str(e))
        while True: #Wait for clients to register
            data, addr = regSocket.recvfrom(2048) #Receive the client's name 
            client = Client(addr[0], addr[1], data.decode(self.FORMAT)) #Creat a Client object from name and address
            self.clients.append(client) #Place the client in the Server's array
            self.clientsOnline = ""
            for i in range(len(self.clients)):
                self.clientsOnline += self.clients[i].name
            print(client.name + " is connected.")
            regSocket.sendto(self.MENU.encode(self.FORMAT), addr)
    
    def displayClients(self):
        dsplSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            dsplSocket.bind((self.host, self.dsplPort))
        except socket.error as e:
            print(str(e))
        while True:
            data, addr = dsplSocket.recvfrom(2048) #Receive message
            command = data.decode(self.FORMAT)
            if command == 'd':
                dsplSocket.sendto(self.clientsOnline.encode(self.FORMAT), addr)
            else:
                continue

    #Receives a message from a client
    def receive(self):
        recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            recSocket.bind((self.host, self.receivePort))
        except socket.error as e:
            print(str(e))
        while True:
            data, addr = recSocket.recvfrom(2048) #Receive message
            self.dataQueue.put(data) #Places data on queue
            self.recpQueue.put(addr) #Places repicient on queue

    #Sends a message to a client (For now just returns to the client who sent it)
    def sendMsg(self):
        sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sendsocket.bind((self.host, self.sendPort))
        except socket.error as e:
            print(str(e))            
        while True:
            data = self.dataQueue.get() #Retrieve the data
            addr = self.recpQueue.get() #Retrieve the recipient
            data = data.decode(self.FORMAT)
            message = f"You said: {data}" #Placeholder reply to show code executed correctly
            sendsocket.sendto(message.encode(self.FORMAT), addr)


class Client:

    def __init__(self, IP, port, name):
        self.IP = IP
        self.port = port
        self.FORMAT = 'utf-8'
        self.name = name

server = Server("192.168.0.106", 12345, 12346, 12347, 12348)
server.run()