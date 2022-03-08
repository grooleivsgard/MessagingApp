#CSC3002F Assignment 1: Client
import socket
import threading
    
def main():
    FORMAT = 'utf-8'
    serverName = "192.168.0.106"
    registerPort = 12345
    receivePort = 12346
    displayPort = 12348
    disconnectPort = 12349
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    name = input("Enter your name:\n")
    clientSocket.sendto(name.encode(FORMAT), (serverName, registerPort))
    print(clientSocket.recv(1024).decode(FORMAT))
    prompt = ""
    while True:
        command = input(prompt)
        if command == "Quit":
            clientSocket.sendto(command.encode(FORMAT), (serverName, disconnectPort))
            break
        if command == "d":
            clientSocket.sendto(command.encode(FORMAT), (serverName, displayPort))
            clients = clientSocket.recv(1024)
            clients = clients.decode(FORMAT)
            print(clients)
        else:
            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            newMsg = clientSocket.recv(1024)
            print(newMsg.decode(FORMAT))
    clientSocket.close()
    
main()