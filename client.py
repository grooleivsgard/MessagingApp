#CSC3002F Assignment 1: Client
import socket
import threading
    
def main():
    FORMAT = 'utf-8'
    serverName = "192.168.56.1"
    serverPort = 12345
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    name = input("Enter your name:\n")
    clientSocket.sendto(name.encode(FORMAT), (serverName, serverPort))
    while True:
        message = input("Type a message to someone:\n")
        if message == "Quit":
            break
        else:
            clientSocket.sendto(message.encode(FORMAT), (serverName, serverPort))
            newMsg = clientSocket.recv(1024)
            print(newMsg.decode(FORMAT))
    clientSocket.close()
    
main()