import socket, os, threading

class FTPServer():
    def __init__(self, controlConnection, ipAddress):
        self.controlConnection = controlConnection
        self.ipAddress = ipAddress
        self.dataSocket = None
        self.type = None

        self.run()
    def run(self):
        self.USER()
        while True:
            data = self.controlConnection.recv(8192).decode()
            if not data:
                break

            command = self.getCommnand(data)
            info = self.getInfo(data)
            if command=="PASV":
                self.PASV()
            elif command=="LIST":
                self.LIST()
            elif command=="PWD ":
                self.PWD()
            elif command=="CWD ":
                self.CWD(info)
            elif command=="TYPE":
                self.TYPE(info)
            elif command=="RETR":
                self.RETR(info)
            elif command=="STOR":
                self.STOR(info)
            elif command=="NOOP":
                self.NOOP()
            elif command=="QUIT":
                self.QUIT()
            elif command=="RMD ":
                self.RMD(info)
            elif command=="MKD ":
                self.MKD(info)
            elif command=="DELE":
                self.DELE(info)
            elif command=="PORT":
                self.PORT(info)
            elif command=="SYST":
                self.SYST()
            else:
                self.UNKNOWN()


    def USER(self):
        message = "220 Server socket established\r\n"
        print(message)
        self.controlConnection.send(message.encode())
        print(message)
        data = self.controlConnection.recv(1024).decode()
        username = data[5:].strip()
        if self.checkUserExists(username):
            self.PASS(username)
        else:
            message = "530 Unknown user\r\n"
            self.controlConnection.send(message.encode())

    def PASS(self, username):
        message = "331 Password required\r\n"
        self.controlConnection.send(message.encode())
        data = self.controlConnection.recv(1024).decode()
        password = data[5:].strip()
        if self.checkPassword(username, password):
            message = "230 Login successful\r\n"
            self.controlConnection.send(message.encode())
        else:
            message = "530 Incorrect Password\r\n"
            self.controlConnection.send(message.encode())

    def checkUserExists(self, username):
        return True

    def checkPassword(self, username, password):
        return True

    def getCommnand(self, data):
        command = data[:4]
        return command

    def getInfo(self, data):
        info = data[data.find(' ')+1:data.find('\r\n')]
        return info

    def PASV(self):
        address = socket.gethostbyname(socket.gethostname())
        address = address.split(".")
        address = ','.join(address)
        address = "("+address+",30,60)"
        message = "227 Passive Mode " + address +"\r\n"
        self.getDataSocket(socket.gethostbyname(socket.gethostname()), 7740)
        self.controlConnection.send(message.encode())
        print("Passive data connection set up ")

    def PORT(self, data):
        print("start port")
        data = data.split(",")
        dataHost = '.'.join(data[0:4])
        dataPort = data[-2:]
        dataPort = (int(dataPort[0]) * 256) + int(dataPort[1])
        self.getDataSocket(dataHost, dataPort)
        message = "200 PORT command successful.\r\n"
        self.controlConnection.send(message.encode())

    def getDataSocket(self, host, port):
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.bind((host, port))
        self.dataSocket.listen(1)

    def LIST(self):
        message = "150 Here comes the directory listing...\r\n"
        self.controlConnection.send(message.encode())
        dataConnection, address = self.dataSocket.accept()
        listing = ""
        # detect the current working directory
        path = os.getcwd()

        # read the entries
        with os.scandir(path) as listOfEntries:
            for entry in listOfEntries:
                # print all entries that are files
                if entry.is_file():
                    listing = listing + '\t' + entry.name
        print(listing)
        dataConnection.send(listing.encode())
        dataConnection.close()
        message = "226 Listing transfer complete.\r\n"
        self.controlConnection.send(message.encode())
        self.dataSocket.close()
        self.dataSocket = None
        return

    def PWD(self):
        pwd = os.getcwd()
        message = "257 " + pwd + " is the current working directory.\r\n"
        self.controlConnection.send(message.encode())

    def CWD(self, path):
         if os.path.exists(path):
             os.chdir(path)
             message = "250 Working directory changed.\r\n"
             self.controlConnection.send(message.encode())
         else:
             message = "550 The path name specified could not be found.\r\n"
             self.controlConnection.send(message.encode())

    def RMD(self, dir):
        if os.path.exists(dir):
            print("true")
            os.rmdir(dir)
            message = "250 Directory removed.\r\n"
            self.controlConnection.send(message.encode())
        else:
            message = "550 Directory does not exist.\r\n"
            self.controlConnection.send(message.encode())

    def MKD(self, newDir):
        if os.path.exists(newDir):
            message="521 Directory already exists.\r\n"
            self.controlConnection.send(message.encode())
        else:
            os.mkdir(newDir)
            message="257 Directory created.\r\n"
            self.controlConnection.send(message.encode())

    def DELE(self, pathName):
        if os.path.exists(pathName):
            os.remove(pathName)
            message = "250 File deleted.\r\n"
            self.controlConnection.send(message.encode())
        else:
            message = "450 Requested file could not be deleted.\r\n"
            self.controlConnection.send(message.encode())

    def TYPE(self, type):
        if type=='A':
            message = "200 ascii mode activated.\r\n"
            self.controlConnection.send(message.encode())
            self.type='A'
        elif type=='I':
            message = "200 binary mode activated.\r\n"
            self.controlConnection.send(message.encode())
            self.type='I'
        else:
            print("no type found")

    def RETR(self, filename):
        message = "150 Opening data connection"
        self.controlConnection.send(message.encode())
        dataConnection, address = self.dataSocket.accept()

        if self.type=='A':
            file = open(filename, 'r')
            fileData = file.read(8192)

            while fileData:
                print("reading file")
                dataConnection.send((fileData+'\r\n').encode())
                fileData = file.read(8192)

            file.close()
            dataConnection.close()
            message = "226 file transfer completed successfully.\r\n"
            self.controlConnection.send(message.encode())

        elif self.type=='I':
            file = open(filename, 'rb')
            fileData = file.read(8192)

            while fileData:
                print("reading file")
                dataConnection.send(fileData)
                fileData = file.read(8192)

        file.close()
        dataConnection.close()
        self.dataSocket.close()
        self.dataSocket = None
        message = "226 file transfer completed successfully.\r\n"
        self.controlConnection.send(message.encode())

    def STOR(self, filename):
        message = "150 Opening data connection"
        self.controlConnection.send(message.encode())

        dataConnection, address = self.dataSocket.accept()

        if self.type=='A':
            file = open(filename, 'w')
            fileData = self.dataSocket.recv(8192).decode()

            while fileData:
                print("writing file - A")
                file.write(fileData)
                fileData = self.dataSocket.recv(8192).decode()

            file.close()
            dataConnection.close()
            self.dataSocket.close()
            self.dataSocket = None
            message = "226 file transfer completed successfully.\r\n"
            self.controlConnection.send(message.encode())

        elif self.type=='I':
            file = open(filename, 'wb')
            fileData = dataConnection.recv(8192)

            while fileData:
                print("writing file - I")
                file.write(fileData)
                print("written stuff")
                fileData = dataConnection.recv(8192)


            print("after write")
            file.close()
            message = "226 file transfer completed successfully.\r\n"
            self.controlConnection.send(message.encode())
            dataConnection.close()
            self.dataSocket.close()
            self.dataSocket = None
            print("sent message")

    def SYST(self):
        message = "215 " + os.name + ".\r\n"
        self.controlConnection.send(message.encode())

    def NOOP(self):
        message = "200 NOOP OK\r\n"
        self.controlConnection.send(message.encode())
    def QUIT(self):
        message = "221 FTP connection terminated.\r\n"
        self.controlConnection.send(message.encode())
        self.controlConnection.close()

    def UNKNOWN(self):
        message = "202 Command not implemented.\r\n"
        self.controlConnection.send(message.encode())
def createControlSocket(host, port):
    controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controlSocket.bind((host, port))
    return controlSocket

def Main():
    host = socket.gethostbyname(socket.gethostname())
    port = 21

    print("FTP Server started")

    print("Command:", host)

    controlSocket = createControlSocket(host, port)

    controlSocket.listen(1)
    controlConnection, controlAddress = controlSocket.accept()
    FTPServer(controlConnection, controlAddress)


if __name__ == '__main__':
    Main()