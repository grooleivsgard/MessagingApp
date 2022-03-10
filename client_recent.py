#CSC3002F Assignment 1: Client
import socket
import threading
import os
from time import sleep
from tkinter import CENTER
    
class Client(threading.Thread):

    def __init__(self):
        self.FORMAT = 'utf-8'
        self.serverName = "172.20.10.5"
        self.registerPort = 12345
        self.receivePort = 12346
        self.sendPort = 12347
        #displayPort = 12348
        self.disconnectPort = 12349
        
    
    def run(self):  
        self.lock = threading.Lock()   #creates a lock for the threads
        inputThread = threading.Thread(target=self.input) #Starts the thread that registers the clients on the server
        inputThread.start()
        

    def input(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        name = input("Enter your name:\n")    
        self.clientSocket.sendto(name.encode(self.FORMAT), (self.serverName, self.registerPort))
    
        recvd = self.clientSocket.recv(1024).decode(self.FORMAT)
        if recvd == "taken":
            while recvd == "taken":
                print("Username taken, please enter a new one")
                name = input("Enter your name:\n")    
                self.clientSocket.sendto(name.encode(self.FORMAT), (self.serverName, self.registerPort))    
                recvd = self.clientSocket.recv(1024).decode(self.FORMAT)

        print(recvd)

        prompt = ""
        listenThread = threading.Thread(target=self.listen) #Starts the thread that registers the clients on the server
        listenThread.start()
        while True:            
            command = input(prompt)       #checks for input from user     
            self.lock.acquire()            #attains the lock so that listen thread does not interrupt
            
            if command == "MENU":       #displays options
                print("\nType 'd' to display online users\nType 'Send to' to select recipient\nType 'Create' to make a group\nType 'MENU' to view options\nType 'Quit' to exit\n")
                self.lock.release()     #releases lock for listen thread to use

            elif command == "Quit":     #exits the program
                self.clientSocket.sendto(command.encode(self.FORMAT), (self.serverName, self.receivePort))
                self.clientSocket.close()
                os._exit(0)             #exits system

            elif command == "d":        #displays active users
                self.clientSocket.sendto(command.encode(self.FORMAT), (self.serverName, self.receivePort))
                clients = self.clientSocket.recv(1024)
                clients = clients.decode(self.FORMAT)

                print(clients)
                self.lock.release()

            elif command == "Send to":      #sends message to user or group
                print("\nType name of recipient or group")      
                recipients = input()

                print("\nType message:")
                message = "Send to;" + recipients + ":" + input()   #creates message for server to decipher
                self.clientSocket.sendto(message.encode(self.FORMAT), (self.serverName, self.receivePort))

                com = "get"
                self.clientSocket.sendto(com.encode(self.FORMAT), (self.serverName, self.receivePort))  #sends command to retrieve message sent
                newmsg = self.clientSocket.recv(1024).decode(self.FORMAT)
                
                print(newmsg)
                self.lock.release()

            elif command == "Create":
                print("\nCreate a group name")
                grpName = input()

                print("\nType the names of members to add seperated by a ';'")
                members = input()

                message = "Create;" + members + ":" + grpName
                self.clientSocket.sendto(message.encode(self.FORMAT), (self.serverName, self.receivePort))

                newmsg = self.clientSocket.recv(2048).decode(self.FORMAT)
                for i in range(len(newmsg)):
                    if newmsg[i] == " ":
                        if newmsg[0:i] == name:
                            newmsg = name + " " + newmsg[i+1:len(newmsg)]
                        break

                print("\n" + newmsg)
                self.lock.release()

            else:
                print("Command does not exist")
                self.lock.release()
            
        self.clientSocket.close()
    
    #checks for new messages
    def listen(self):
        while True:
            command = "get"
            sleep(3)    #sleeps in case user inputs command
            self.lock.acquire()    #acquires a lock to run without interuption    

            self.clientSocket.sendto(command.encode(self.FORMAT), (self.serverName, self.receivePort))            
            output = self.clientSocket.recv(2048).decode(self.FORMAT)   
            
            if output != "NONE":    #checks if there is any new messages, if there is, prints it
                print("\n" + output)
            self.lock.release() #releases lock to allow user to enter a command
            
       

client = Client()
client.run()