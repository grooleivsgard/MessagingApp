#CSC3002F Assignmnet 1 Client
import socket
import threading
from obj import Client

def startChat(msg): #Function to receive indication from the server if another clients wants to chat with them
    if msg == "NOCHAT":
        return False
    else:
        return True

def main():
    FORMAT = 'utf-8'
    serverName = "192.168.0.108"
    registerPort = 12345
    receivePort = 12346
    chatPort = 12347
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chatSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    name = input("Enter your name:\n")
    clientSocket.sendto(name.encode(FORMAT), (serverName, registerPort))
    print(clientSocket.recv(1024).decode(FORMAT)) #Print input menu
    prompt = ""
    while True:
        chatSocket.sendto(name.encode(FORMAT), (serverName, chatPort)) #Send the server the current client's address
        initiateChat = chatSocket.recvfrom(1024)[0].decode(FORMAT) #Server checks if another client is trying to start a chat, sends back result
        if startChat(initiateChat):
            print(f"{initiateChat} wants to chat")
        command = input(prompt)
        if command == "q":
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            break
        elif command == "d":
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            clients = clientSocket.recv(1024)
            clients = clients.decode(FORMAT)
            print(clients)
        elif command == 'c':
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            recipientName = input("Type the name of the user you would like to chat with:\n")
            clientSocket.sendto(recipientName.encode(FORMAT), (serverName, receivePort))
    clientSocket.close()

main()