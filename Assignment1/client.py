# CSC3002F Assignment 1: Client
import socket
import threading
import hashlib
import tkinter as tk


def main():
    FORMAT = 'utf-8'
    serverName = "10.0.0.20"
    registerPort = 12345
    receivePort = 12346
    displayPort = 12348
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    name = input("Enter your name:\n")
    clientSocket.sendto(name.encode(FORMAT), (serverName, registerPort))
    print(clientSocket.recv(1024).decode(FORMAT))
    while True:
        command = input("\n")
        if command == "Quit":
            break
        if command == "d":
            clientSocket.sendto(command.encode(FORMAT), (serverName, displayPort))
            clients = clientSocket.recv(1024)
            clients = clients.decode(FORMAT)
            print(clients)
        else:
            # Hash command and convert it to hexa
            hashedCommand = hashlib.md5(b'{command}').hexdigest()

            clientSocket.sendto(command.encode(FORMAT), (serverName, receivePort))
            newMsg = clientSocket.recv(1024)
            print(newMsg.decode(FORMAT))

            # Hash received message and convert it to hexa
            hashedNewMsg = hashlib.md5(b'newMsg').hexdigest()

            # Compare sent hash command and received new message
            #  If the hashes are equivalent, no errors detected
            #  If not, errors detected

            if hashedCommand == hashedNewMsg:
                print('\nNO ERRORS DETECTED')
            else:
                print('\nWARNING! ERRORS DETECTED')

    clientSocket.close()


main()
