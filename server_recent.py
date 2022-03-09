#CSC3002F Assignment 1: Server
from http import client
import socket
import threading
import queue

class Server(threading.Thread):

    #Initialises the server object
    def __init__(self, host, port1, port2, port3):
        self.host = host
        self.registerPort = port1
        self.receivePort = port2
        self.sendPort = port3
        self.FORMAT = 'utf-8'
        self.MENU = "\nType 'd' to display online users\nType 'Send to' to select recipient\nType 'Create' to make a group\nType 'MENU' to view options"
        self.clientsOnline = ""
        self.clients = [] #List of clients connected to the server as Client objects (see below)
        self.groups = []
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
            client = Client(addr, data.decode(self.FORMAT)) #Create a Client object from name and address
            client.is_connected = True
            self.clients.append(client) #Place the client in the Server's array
            print(client.name + " is connected.")
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
            for i in range(len(command)):
                if command[i] == ";":
                    received = command[i+1:len(command)]
                    command = command[0:i]
                    break           
            

            for i in range(len(self.clients)):
                    if self.clients[i].addr == addr:
                        name = self.clients[i].name
                        

            #print(command)
            #print(received)
            if command == 'd':
                clients = self.displayClients()
                recSocket.sendto(clients, addr)
            elif command == 'Quit':
                print(self.onDisconnect(addr))
                
            elif command == 'Send to':
                found = False                
                recipients = []                              
                rcvrName = ""
                #print(received)

                for j in range(len(received)):
                    if received[j] == ":": 
                        rcvrName = received[0:j] 
                        received = received[j+1:len(received)]
                        break

                #print(rcvrName)     

                for i in range(len(self.clients)):
                    if self.clients[i].name == rcvrName:
                        found == True                      
                        recipients.append(rcvrName)
                        recipients.append(name) 
                
                if found == True:
                    received = rcvrName + ";" + name + ":" + received
                    for i in range(len(self.clients)):
                        for j in range(len(recipients)):
                            if self.clients[i].name == recipients[j]:
                                self.dataQueue.put(received) #Places data on queue
                                self.recpQueue.put(self.clients[i].addr) #Places repicient on queue
                else:
                    for j in range(len(self.groups)):
                        #print(self.groups[j].name, rcvrName)
                        if self.groups[j].name == rcvrName:
                            recipients = self.groups[j].members
                            for k in range(len(recipients)):
                                if recipients[k] == name:
                                    found == True
                                    received = rcvrName + ";" + name + ":" + received
                                    for i in range(len(self.clients)):
                                        for k in range(len(recipients)):
                                            if self.clients[i].name == recipients[k]:
                                                self.dataQueue.put(received) #Places data on queue
                                                self.recpQueue.put(self.clients[i].addr) #Places repicient on queue
                if found == False:
                    self.dataQueue.put("Contact or group not found")
                    self.recpQueue.put(addr)                    
                
                
            elif command == 'Create':
                members = []
                members.append(name)
                grpName  = ""
                pos = 0
                #print(received)

                for i in range(len(received)):
                    if (received[i] == ";") or (received[i] == ":"):
                        #print(received[pos:i])
                        members.append(received[pos:i])
                        pos = i+1                        
                        if received[i] == ":":
                            grpName = received[i+1:len(received)]
                            break
                
                #for i in range(len(members)):
                # print(members[i])

                group = Group(members, grpName)
                self.groups.append(group)
                message = " created group " +"\"" + group.name + "\""
                #print(message)
                for i in range(len(self.clients)):
                    for j in range(len(members)):
                        if self.clients[i].name == members[j]:
                            #print(members[j])
                            if members[j] == name:
                                message = "You" + message
                            else:
                                message = name + message

                            self.dataQueue.put(message) #Places data on queue
                            self.recpQueue.put(self.clients[i].addr) #Places repicient on queue   


    #Sends a message to a client (For now just returns to the client who sent it)
    def sendMsg(self):
        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sendSocket.bind((self.host, self.sendPort))
        except socket.error as e:
            print(str(e))            
        while True:
            data = self.dataQueue.get() #Retrieve the data
            addr = self.recpQueue.get() #Retrieve the recipient
            message = data #Placeholder reply to show code executed correctly
            sendSocket.sendto(message.encode(self.FORMAT), addr)

    def onDisconnect(self, addr):
        for i in range(len(self.clients)):
            if self.clients[i].addr == addr:
                self.clients[i].is_connected = False
                j = i
        return f"{self.clients[j].name} has disconnected"

class Client:

    def __init__(self, addr, name):
        self.addr = addr
        self.name = name
        self.FORMAT = 'utf-8'
        self.is_connected = False

class Group:
    def __init__(self, members, name):
        self.members = members
        self.name = name

server = Server("192.168.0.56", 12345, 12346, 12347)
server.run()