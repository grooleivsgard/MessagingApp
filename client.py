#CSC3002F Assignmnet 1 Client
import socket
import threading
from obj import Client

class ChatApp(threading.Thread):

    def __init__(self, host, port1, port2, port3, port4):
        self.serverName = host
        self.registerPort = port1
        self.receivePort = port2
        self.startPort = port3
        self.chatPort = port4
        self.FORMAT =  'utf-8'

    def startChat(self, msg): #Function to receive indication from the server if another clients wants to chat with them
        if msg == "NOCHAT":
            return False
        else:
            return True

    # def recChat(self, name):
    #     FORMAT = 'utf-8'
    #     serverName = "192.168.0.108"
    #     chatPort = 12348
    #     while True:
    #         message = chatsock.recvfrom(2048)[0].decode(FORMAT)
    #         print(message)

    def chat(self, name, chatsock):
        prompt = "Type a message:\n"
        chatsock.sendto(name.encode(self.FORMAT), (self.serverName, self.chatPort))
        while True:
            message = input(prompt)

            if message == "!q":
                chatsock.sendto(message.encode(self.FORMAT), (self.serverName, self.chatPort))
                break
            else:
                chatsock.sendto(message.encode(self.FORMAT), (self.serverName, self.chatPort))
                prompt = ''
            reply = chatsock.recvfrom(2048)[0].decode(self.FORMAT)
            if reply == "Your recpient has disconnected":
                print(reply)
                break
            else:
                print(reply)

    def run(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        chatSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        name = input("Enter your name:\n")
        clientSocket.sendto(name.encode(self.FORMAT), (self.serverName, self.registerPort))
        print(clientSocket.recv(1024).decode(self.FORMAT)) #Print input menu
        prompt = ""
        while True:
            chatSocket.sendto(name.encode(self.FORMAT), (self.serverName, self.startPort)) #Send the server the current client's address
            initiateChat = chatSocket.recvfrom(1024)[0].decode(self.FORMAT) #Server checks if another client is trying to start a chat, sends back result
            if self.startChat(initiateChat):
                confirm = input(f"{initiateChat} wants to chat. Accept(a) or Decline(d):\n")
                if confirm == 'a':
                    print("You accepted the chat")
                    clientSocket.sendto("accepted".encode(self.FORMAT), (self.serverName, self.receivePort))
                    self.chat(name, clientSocket)
                    # recThread = threading.Thread(target=recChat, args=(name, clientSocket))
                    # recThread.start()
                else:
                    print("You declined the chat")
                    clientSocket.sendto("declined".encode(self.FORMAT), (self.serverName, self.receivePort))
            command = input(prompt)
            if command == "q":
                clientSocket.sendto(command.encode(self.FORMAT), (self.serverName, self.receivePort))
                break
            elif command == "d":
                clientSocket.sendto(command.encode(self.FORMAT), (self.serverName, self.receivePort))
                clients = clientSocket.recv(1024)
                clients = clients.decode(self.FORMAT)
                print(clients)
            elif command == 'c':
                clientSocket.sendto(command.encode(self.FORMAT), (self.serverName, self.receivePort))
                recipientName = input("Type the name of the user you would like to chat with:\n")
                clientSocket.sendto(recipientName.encode(self.FORMAT), (self.serverName, self.receivePort))
                print(f"Waiting for response from {recipientName}...")
                confirm = clientSocket.recvfrom(1024)[0].decode(self.FORMAT)
                if confirm == 'declined':
                    print("Your chat has been declined")
                elif confirm == 'accepted':
                    print("Your chat has been accepted")
                    self.chat(name, clientSocket)
                # recThread = threading.Thread(target=recChat, args=(name, clientSocket))
                # recThread.start()
        clientSocket.close()

chat = ChatApp("192.168.0.108", 12345, 12346, 12347, 12348)
chat.run()