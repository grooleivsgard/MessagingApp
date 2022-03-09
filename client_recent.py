#CSC3002F Assignment 1: Client
import socket
import threading
import os
from time import sleep
from tkinter import CENTER
    
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
        if command == "MENU":
            print("\nType 'd' to display online users\nType 'Send to' to select recipient\nType 'Create' to make a group\nType 'MENU' to view options\nType 'Quit' to exit")
        elif command == "Quit":
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            break
        elif command == "d":
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            clients = clientSocket.recv(1024)
            clients = clients.decode(FORMAT)
            print(clients)
        elif command == "Send to":
            print("\nType name of recipient or group")
            recipients = input()
            print("\nType message:")
            message = "Send to;" + recipients + ":" + input()
            #print(message)
            clientSocket.sendto(message.encode(FORMAT), (serverName, receivePort))
            newmsg = clientSocket.recv(1024).decode(FORMAT)

            #print(newmsg, "hi")
            title = ""
            pos = 0
            
            for i in range(len(newmsg)):
                if newmsg[i] == ";":
                    title = 'Chat: ' + newmsg[0:i]
                    print("\n" + title.center(os.get_terminal_size().columns))
                    pos = i
                elif newmsg[i] == ":":
                    senderName = newmsg[pos+1:i]                    
                    if senderName == name:
                        senderName = "You"
                        #print(senderName)
                    newmsg = senderName + ": " + newmsg[i+1:len(newmsg)]
                    #print(newmsg)
                    break

            #strCent = str.center(35)
            
            print("\n" + newmsg)

        elif command == "Create":
            print("\nCreate a group name")
            grpName = input()

            print("\nType the names of members to add seperated by a ';'")
            members = input()

            message = "Create;" + members + ":" + grpName
            clientSocket.sendto(message.encode(FORMAT), (serverName, receivePort))

            newmsg = clientSocket.recv(2048).decode(FORMAT)
            for i in range(len(newmsg)):
                if newmsg[i] == " ":
                    if newmsg[0:i] == name:
                        newmsg = name + " " + newmsg[i+1:len(newmsg)]
                    break
            print("\n" + newmsg)


            #else:
         #   clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
          #  newMsg = clientSocket.recv(1024)
           # print(newMsg.decode(FORMAT))
    clientSocket.close()
    
main()