#CSC3002F: Assingment 1 Server
import socket
import threading
import queue
from obj import Client

class Server(threading.Thread):

    #Initialises the server object
    def __init__(self, host, port1, port2, port3):
        self.host = host
        self.registerPort = port1
        self.receivePort = port2
        self.chatPort = port3
        self.FORMAT = 'utf-8'
        self.MENU = "ChatApp:\nQuit(q): Exit the app\nDisplay(d): Display online users\nChat(c): Open a chat with someone\n"
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
        recvThread = threading.Thread(target=self.receive) #Start the thread which receives messages
        recvThread.start()
        chatThread = threading.Thread(target=self.startChat) #Starts the thread which initiates a chat
        chatThread.start()

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
            client.is_connected = True
            self.clients.append(client) #Place the client in the Server's array
            print(client.name + " has connected.")
            regSocket.sendto(self.MENU.encode(self.FORMAT), addr)
    
    def displayClients(self):
        self.clientsOnline = "Users Online:\n"
        for i in range(len(self.clients)):
            if self.clients[i].is_connected:
                self.clientsOnline = self.clientsOnline + self.clients[i].name + '\n'
        return self.clientsOnline.encode(self.FORMAT)

    #Receives a message from a client
    def receive(self):
        recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            recSocket.bind((self.host, self.receivePort))
        except socket.error as e:
            print(str(e))
        while True:
            command, addr = recSocket.recvfrom(2048) #Receive command
            command = command.decode(self.FORMAT)
            if command == 'd':
                clients = self.displayClients()
                recSocket.sendto(clients, addr)
            elif command == 'q':
                print(self.onDisconnect(addr))

            elif command == 'declined': #Client declines chat
                chatter = Client('1', 1, 'Null')
                for i in range(len(self.clients)):
                    if self.clients[i].addr == addr:
                        self.clients[i].initiateChat = False
                        chatterName = self.clients[i].chatter
                        self.clients[i].chatter = ''
                for j in range(len(self.clients)):
                    if self.clients[j].name == chatterName:
                        chatter = self.clients[j]
                recSocket.sendto("declined".encode(self.FORMAT), chatter.addr)

            elif command == 'accepted': #Client accepts chat
                chatter = Client('1', 1, 'Null')
                for i in range(len(self.clients)):
                    if self.clients[i].addr == addr:
                        self.clients[i].initiateChat = False
                        chatterName = self.clients[i].chatter
                        self.clients[i].chatter = ''
                for j in range(len(self.clients)):
                    if self.clients[j].name == chatterName:
                        chatter = self.clients[j]
                recSocket.sendto("accepted".encode(self.FORMAT), chatter.addr)

            elif command == 'c': #Client wants to start chat
                data, addr = recSocket.recvfrom(1024)
                for j in range(len(self.clients)): #Find client initiating chat
                    if addr == self.clients[j].addr:
                        chatter = self.clients[j].name
                        break
                recipientName = data.decode(self.FORMAT)
                for i in range(len(self.clients)): #Find the recipient
                    if recipientName == self.clients[i].name:
                        recipient = self.clients[i]
                        recipient.initiateChat = True
                        recipient.chatter = chatter
                        break

    def onDisconnect(self, addr):
        client = Client('1', 1, "null")
        for i in range(len(self.clients)):
            if self.clients[i].addr == addr:
                #self.clients[i].is_connected = False
                client = self.clients[i]
                #j = i
        self.clients.remove(client)
        return f"{client.name} has disconnected"

    def startChat(self):
        chatSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            chatSocket.bind((self.host, self.chatPort))
        except socket.error as e:
            print(str(e))
        while True:
            data, addr = chatSocket.recvfrom(1024) #Receive the address and name of the client the server is dealing with
            clientName = data.decode(self.FORMAT)
            client = Client('1', 1, "Null")
            for j in range(len(self.clients)):
                if clientName == self.clients[j].name:
                    client = self.clients[j]
            if client.initiateChat == True:
                chatSocket.sendto(client.chatter.encode(self.FORMAT), addr) #Let the client know (work in progress)
            else:
                chatSocket.sendto("NOCHAT".encode(self.FORMAT), addr) #Let the client know so they can continue as usual
                


server = Server("192.168.0.108", 12345, 12346, 12347)
server.run()    
