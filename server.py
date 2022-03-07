#CSC3002F Assignment 1: Server
import socket
import threading

class Server(threading.Thread):

    #Initialises the server object
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.FORMAT = 'utf-8'
        self.clients = [] #List of clients connected to the server as Client objects (see below)

    #Opens a socket and binds it to the IP and port number contained in the server object
    def run(self):
        regSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            regSocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
        print(f"[SERVER ACTIVE ON IP {self.host}] The Server is ready to receive...")
        regThread = threading.Thread(target=self.register, args=(regSocket,)) #Starts the thread that registers the clients on the server
        regThread.start()

    #Registers the client's name and address (IP + port number)
    def register(self, rsocket):
        #while True: #We will need this line to make sure multiple clients can cannot but for now it breaks the code :(
        data, addr = rsocket.recvfrom(2048) #Receive the client's name 
        client = Client(addr[0], addr[1], data.decode(self.FORMAT)) #Creat a Client object from name and address
        self.clients.append(client) #Place the client in the Server's array
        print(client.name + " is connected.")
        recvThread = threading.Thread(target=self.receive) #Start the thread which receives messages
        recvThread.start()

    def receive(self):
        rsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            rsocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
        clientsOnline = ""
        for i in range(len(self.clients)):
            clientsOnline = clientsOnline + '\n' + self.clients[i].name #Creates a string displaying all the clients connected to the user. For use later
        while True:
            data, addr = rsocket.recvfrom(1024) #Receive message
            data = data.decode(self.FORMAT)
            data = f"You said: {data}" #Placeholder reply to show code executed correctly
            rsocket.sendto(data.encode(self.FORMAT), addr)

class Client:

    def __init__(self, IP, port, name):
        self.IP = IP
        self.port = port
        self.FORMAT = 'utf-8'
        self.name = name

server = Server("192.168.56.1", 12345)
server.run()