# CSC3002F Assignment 1: Server
from http import client
import socket
import threading
import queue
import os
from time import sleep


class Server(threading.Thread):

    # Initialises the server object
    def __init__(self, host, port1, port2, port3):
        self.host = host
        self.registerPort = port1
        self.receivePort = port2
        self.sendPort = port3
        self.FORMAT = 'utf-8'
        self.MENU = "\nType 'd' to display online users\nType 'Send to' to select recipient\nType 'Create' to make a group\nType 'MENU' to view options\nType 'Quit' to exit\n"
        self.clientsOnline = ""
        self.clients = []  # List of clients connected to the server as Client objects (see below)
        self.groups = []
        self.dataQueue = queue.Queue()  # FIFO queue of data sent my clients
        self.recpQueue = queue.Queue()  # FIFO queue of recipients where data should be sent

    # Opens a socket and binds it to the IP and port number contained in the server object
    def run(self):
        print(f"[SERVER ACTIVE ON IP {self.host}] The Server is ready to receive...")
        for i in range(len(self.clients)):
            clientsOnline = clientsOnline + '\n' + self.clients[
                i].name  # Creates a string displaying all the clients connected to the user. For use later
        regThread = threading.Thread(target=self.register)  # Starts the thread that registers the clients on the server
        regThread.start()
        recvThread = threading.Thread(target=self.receive)  # Start the thread which receives messages
        recvThread.start()
        sendThread = threading.Thread(target=self.sendMsg)  # Starts the thread which sends messages to clients
        sendThread.start()

    # Registers the client's name and address (IP + port number)
    def register(self):
        regSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            regSocket.bind((self.host, self.registerPort))
        except socket.error as e:
            print(str(e))
        while True:  # Wait for clients to register
            data, addr = regSocket.recvfrom(2048)  # Receive the client's name
            messages = []
            name = data.decode(self.FORMAT)

            bTaken = False
            for i in range(len(self.clients)):  # check if username is already taken
                if self.clients[i].name == name:
                    bTaken = True

            if bTaken == True:
                message = "taken"
                regSocket.sendto(message.encode(self.FORMAT), addr)
            else:
                client = Client(addr, data.decode(self.FORMAT),
                                messages)  # Create a Client object from name and address
                client.is_connected = True
                self.clients.append(client)  # Place the client in the Server's array
                print(client.name + " is connected.")
                regSocket.sendto(self.MENU.encode(self.FORMAT), addr)

    # method to send a list of users
    def displayClients(self):
        self.clientsOnline = "Users Online:\n"
        for i in range(len(self.clients)):
            if self.clients[i].is_connected:
                self.clientsOnline = self.clientsOnline + self.clients[i].name + '\n'
        return self.clientsOnline.encode(self.FORMAT)

    # Receives a message from a client
    def receive(self):
        recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            recSocket.bind((self.host, self.receivePort))
        except socket.error as e:
            print(str(e))
        while True:
            command, addr = recSocket.recvfrom(2048)  # Receive command
            command = command.decode(self.FORMAT)
            for i in range(
                    len(command)):  # sepereates command received into command and message sent (if a message is sent)
                if command[i] == ";":
                    received = command[i + 1:len(command)]
                    command = command[0:i]
                    break

                    # receives the name of the sender
            for i in range(len(self.clients)):
                if self.clients[i].addr == addr:
                    name = self.clients[i].name

            if command == 'd':  # sends active clients to client
                clients = self.displayClients()
                recSocket.sendto(clients, addr)

            elif command == 'Quit':  # disconnects user
                print(self.onDisconnect(addr))

            elif command == "get":  # Sends messages that client has not received yet
                mess = []
                temp = []
                rcvrName = ""
                senderName = ""
                newmsg = ""
                pos = 0

                for i in range(len(self.clients)):  # finds the clients address and messages from the Client object
                    if self.clients[i].name == name:
                        address = self.clients[i].addr
                        mess = self.clients[i].messages
                        self.clients[i].messages = temp
                        break

                if len(mess) == 0:  # checks if there are any messages
                    send = "NONE"
                    recSocket.sendto(send.encode(self.FORMAT), address)

                else:
                    for j in range(len(mess)):
                        line = mess[j]

                        if line[0:2] == "s.":  # checks type of message received
                            for h in range(len(line)):
                                if line[h] == ":":
                                    pos = h
                                    break

                            for k in range(len(line)):  # Structures message to be sent
                                if line[k] == ";":
                                    if line[2:k] != name:  # Checks if message is sent to the client
                                        rcvrName = line[2:k]
                                        edited = 'Chat: ' + rcvrName
                                        edited = str.center(edited, os.get_terminal_size().columns)  # centres the line
                                        newmsg = newmsg + edited + "\n"
                                        senderName = line[k + 1:pos]

                                        if senderName == name:
                                            newmsg = newmsg + "You: " + line[pos + 1:len(line)] + "\n"

                                        else:
                                            edited = senderName + ": " + line[pos + 1:len(line)]
                                            edited = str.rjust(edited,
                                                               os.get_terminal_size().columns)  # adjusts the line to the right
                                            newmsg = newmsg + edited + "\n"

                                    else:
                                        rcvrName = line[k + 1:pos]
                                        edited = 'Chat: ' + rcvrName
                                        edited = str.center(edited, os.get_terminal_size().columns)
                                        newmsg = newmsg + edited + "\n"
                                        edited = rcvrName + ": " + line[pos + 1:len(line)]
                                        edited = str.rjust(edited, os.get_terminal_size().columns)
                                        newmsg = newmsg + edited + "\n"

                        else:
                            newmsg = line + "\n"

                    recSocket.sendto(newmsg.encode(self.FORMAT), address)


            elif command == 'Send to':
                found = False
                recipients = []
                rcvrName = ""

                for j in range(len(received)):  # seperates message into who message is being sent to and the message
                    if received[j] == ":":
                        rcvrName = received[0:j]
                        received = received[j + 1:len(received)]
                        break

                for i in range(
                        len(self.clients)):  # checks if user is on the system, if it is, adds people being sent the message to an array
                    if self.clients[i].name == rcvrName:
                        found = True
                        recipients.append(rcvrName)
                        recipients.append(name)
                        break

                if found == True:  # if user was found, sends the message to them
                    received = "s." + rcvrName + ";" + name + ":" + received
                    for i in range(len(self.clients)):
                        for j in range(len(recipients)):
                            if self.clients[i].name == recipients[j]:
                                self.dataQueue.put(received)  # Places data on queue
                                self.recpQueue.put(self.clients[i].addr)  # Places repicient on queue

                else:  # if user was not found, look if a group is being sent the message
                    for j in range(len(self.groups)):
                        if self.groups[j].name == rcvrName:
                            recipients = self.groups[j].members

                            for k in range(len(recipients)):
                                if recipients[k] == name:
                                    found = True
                                    received = "s." + rcvrName + ";" + name + ":" + received

                                    for i in range(len(self.clients)):
                                        for k in range(len(recipients)):
                                            if self.clients[i].name == recipients[k]:
                                                self.dataQueue.put(received)  # Places data on queue
                                                self.recpQueue.put(self.clients[i].addr)  # Places repicient on queue

                if found == False:  # if not found, return following message
                    self.dataQueue.put("Contact or group not found")
                    self.recpQueue.put(addr)
                sleep(2)

            # creates a group
            elif command == 'Create':
                membersTemp = []
                members = []
                members.append(name)
                grpName = ""
                pos = 0

                for i in range(len(received)):  # seperates message received and members
                    if (received[i] == ";") or (received[i] == ":"):
                        membersTemp.append(received[pos:i])
                        pos = i + 1
                        if received[i] == ":":
                            grpName = received[i + 1:len(received)]
                            break

                found = False
                notFound = []

                # checks if users to be added are found
                for i in range(len(membersTemp)):
                    for j in range(len(self.clients)):
                        if membersTemp[i] == self.clients[j].name:
                            found = True
                            members.append(membersTemp[i])

                    if found == False:
                        notFound.append(membersTemp[i])  # adds to list of users not found
                    else:
                        found = False

                group = Group(members, grpName)
                self.groups.append(group)
                message = " created group " + "\"" + group.name + "\""

                # sends notification that they have been added to a group
                for i in range(len(self.clients)):
                    for j in range(len(members)):
                        if self.clients[i].name == members[j]:
                            if self.clients[i].name != name:
                                newmsg = name + message
                                self.dataQueue.put(newmsg)  # Places data on queue
                                self.recpQueue.put(self.clients[i].addr)  # Places repicient on queue

                # sends back message to user creating the group
                if len(notFound) > 0:
                    line = ""
                    for k in range(len(notFound)):
                        if k == 0:
                            line = notFound[k]
                        else:
                            line = line + ", " + notFound[k]

                    message = "You" + message + "\nCould not add: " + line
                else:
                    message = "You" + message

                self.dataQueue.put(message)  # Places data on queue
                self.recpQueue.put(addr)  # Places repicient on queue

                sleep(2)  # gives time for the messages to be added to the queue before they are received

    # Sends a message to a client (For now just returns to the client who sent it)
    def sendMsg(self):
        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sendSocket.bind((self.host, self.sendPort))
        except socket.error as e:
            print(str(e))
        while True:
            data = self.dataQueue.get()  # Retrieve the data
            addr = self.recpQueue.get()  # Retrieve the recipient
            message = data  # Placeholder reply to show code executed correctly

            if message[0:3] == "You":  # sends message straight away to user creating the group
                sendSocket.sendto(message.encode(self.FORMAT), addr)

            else:  # adds messages to clients array of messages not received
                for i in range(len(self.clients)):
                    if self.clients[i].addr == addr:
                        self.clients[i].messages.append(message)

    def onDisconnect(self, addr):
        for i in range(len(self.clients)):
            if self.clients[i].addr == addr:
                self.clients[i].is_connected = False
                j = i
        return f"{self.clients[j].name} has disconnected"


class Client:

    def __init__(self, addr, name, messages):
        self.addr = addr
        self.name = name
        self.FORMAT = 'utf-8'
        self.is_connected = False
        self.messages = messages


class Group:
    def __init__(self, members, name):
        self.members = members
        self.name = name


server = Server("10.0.0.20", 12345, 12346, 12347)
server.run()
