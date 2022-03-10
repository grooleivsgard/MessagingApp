#CSC3002F Assingment 1: Client class

class Client:

    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.addr = (ip, port)
        self.name = name
        self.FORMAT = 'utf-8'
        self.is_connected = False
        self.initiateChat = False #Boolean for the server to register if someone is trying to start a chat with this person
        self.chatter = '' #Name of the person who wants to start a chat with the client

    def toString(self):
        return f"{self.name}' '{self.ip}' '{self.port}"

    def isEqual(self, other):
        if self.name == other.name:
            return True
        return False