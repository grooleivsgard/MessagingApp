#CSC3002F Assignment 1: Client
import socket
import threading
from time import sleep
    
def main():
    FORMAT = 'utf-8'
    serverName = "192.168.0.56"
    registerPort = 12345
    receivePort = 12346
    #displayPort = 12348
    disconnectPort = 12349
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    name = input("Enter your name:\n")
    clientSocket.sendto(name.encode(FORMAT), (serverName, registerPort))
 
    print(clientSocket.recv(1024).decode(FORMAT))
    prompt = ""
    while True:
        command = input(prompt)
        if command == "Quit":
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            break
        elif command == "d":
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            clients = clientSocket.recv(1024)
            clients = clients.decode(FORMAT)
            print(clients)
        elif command == "Send to":
            print("Type name(s) of recipient(s) - seperate by a \';\'")
            recipients = input()
            print("Type message:")
            message = recipients + ":" + input()
            #print(message)
            clientSocket.sendto(message.encode(FORMAT), (serverName, receivePort))
            newmsg = clientSocket.recv(1024).decode(FORMAT)
            #print(newmsg, "hi")
            for i in range(len(newmsg)):
                if newmsg[i] == ":":
                    senderName = newmsg[0:i]
                    newmsg = newmsg[i+1:len(newmsg)]
                    #print(newmsg)
                    break
            if senderName == name:
                senderName = "You"

            print(senderName + ":", newmsg)
        else:
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            newMsg = clientSocket.recv(1024)
            print(newMsg.decode(FORMAT))
    clientSocket.close()
    
main()