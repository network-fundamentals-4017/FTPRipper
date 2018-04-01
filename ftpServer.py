import socket, os, threading, json

class FTPServer(threading.Thread):
    def __init__(self, controlConnection, ipAddress):
        threading.Thread.__init__(self)
        self.controlConnection = controlConnection
        self.ipAddress = ipAddress
        self.dataSocket = None
        self.type = None
        self.mode = 'S'
        self.stru = 'F'
        self.hasPort = False
        self.clientLoggedIn=False

    def run(self):

        while self.clientLoggedIn == False:
            self.USER()

        if self.clientLoggedIn==True:
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
                elif command=="PWD":
                    self.PWD()
                elif command=="CWD":
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
                elif command=="RMD":
                    self.RMD(info)
                elif command=="MKD":
                    self.MKD(info)
                elif command=="DELE":
                    self.DELE(info)
                elif command=="PORT":
                    self.PORT(info)
                elif command=="MODE":
                    self.MODE(info)
                elif command=="STRU":
                    self.STRU(info)
                elif command=="SYST":
                    self.SYST()
                else:
                    self.UNKNOWN()


    def USER(self):#This function notifies the client that a connection has been set up and asks them for their username.
        message = "220 Server socket established\r\n"
        print(message)
        self.controlConnection.send(message.encode())
        data = self.controlConnection.recv(1024).decode()
        print("Username received.")
        username = data[5:].strip()
        if self.checkUserExists(username):#If the username exists, the server asks the client for their password.
            print("Username exists.")
            self.PASS(username)
        else:#An error code of 530 is sent to the user if the username they supplied does not exist.
            message = "530 Unknown user\r\n"
            print("Username does not exist.")
            self.controlConnection.send(message.encode())

    def PASS(self, username):#This function handles the password communication between the server and the client.
        message = "331 Password required\r\n"
        self.controlConnection.send(message.encode())
        data = self.controlConnection.recv(1024).decode()
        print("Password received.")
        password = data[5:].strip()
        if self.checkPassword(username, password):#If the password matches the username - the user is logged in.
            message = "230 Login successful\r\n"
            print("Password accepted.")
            self.clientLoggedIn=True
            self.controlConnection.send(message.encode())
        else:
            print("Incorrect Password")
            message = "530 Incorrect Password\r\n"
            self.controlConnection.send(message.encode())

    def checkUserExists(self, username): #A check to see the the username exists.
        with open("users.txt", 'r') as f:
            users = json.load(f)
        f.close()
        if username in users.keys():
            return True
        return False

    def checkPassword(self, username, password):#Check if the password matches the username.
        with open("users.txt", 'r') as f:
            users = json.load(f)
        f.close()
        if users[username]==password:
            return True
        return False

    def getCommnand(self, data):#Extracts the command from the data received.
        command = data[:4].strip()
        return command

    def getInfo(self, data):#Extracts the additional information from the data received.
        info = data[data.find(' ')+1:data.find('\r\n')]
        return info

    def PASV(self):#sets up a data socket to allow for information transfer.
        address = socket.gethostbyname(socket.gethostname())
        address = address.split(".")
        address = ','.join(address)
        address = "("+address+",30,60)"
        message = "227 Passive Mode " + address +"\r\n"
        self.getDataSocket(socket.gethostbyname(socket.gethostname()), 7740)#creates a new socket.
        self.controlConnection.send(message.encode())
        print("Passive data connection set up.")

    def PORT(self, data):#Sets up the port requested by the user.
        print("PORT requested.")
        data = data.split(",")
        dataHost = '.'.join(data[0:4])
        dataPort = data[-2:]
        dataPort = (int(dataPort[0]) * 256) + int(dataPort[1])
        self.getDataSocket(dataHost, dataPort)
        message = "200 PORT command successful.\r\n"
        self.controlConnection.send(message.encode())
        self.hasPort = True

    def MODE(self, data): #Changes the mode of transfer - (transfer modes are not implemented)
        print("Mode check.")
        if data=='S':
            self.mode='S'
            message = "200 Transfer mode set to stream.\r\n"
            self.controlConnection.send(message.encode())
        elif data=='B':
            self.mode=='B'
            message = "200 Transfer mode set to block.\r\n"
            self.controlConnection.send(message.encode())
        elif data=='C':
            self.mode=='C'
            message = "200 Transfer mode set to compression.\r\n"
            self.controlConnection.send(message.encode())
        else:
            message = "500 Unrecognised transfer mode.\r\n"
            self.controlConnection.send(message.encode())

    def STRU(self, data):#Changes the file structure
        if data == 'F':
            self.stru = 'F'
            message = "200 Structure set to file.\r\n"
            self.controlConnection.send(message.encode())
        elif data == 'R':
            self.stru == 'R'
            message = "200 Structure set to record.\r\n"
            self.controlConnection.send(message.encode())
        elif data == 'P':
            self.stru == 'P'
            message = "200 Structure set to page.\r\n"
            self.controlConnection.send(message.encode())
        else:
            message = "500 Unrecognised structure code.\r\n"
            self.controlConnection.send(message.encode())

    def getDataSocket(self, host, port):#creates the data socket with the information supplied from the PASV or PORT commands.
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.bind((host, port))
        self.dataSocket.listen(1)

    def LIST(self):#Sends the listing of the files in the directory over the data socket.
        print("Directory listing requested.")
        message = "150 Here comes the directory listing...\r\n"
        self.controlConnection.send(message.encode())
        dataConnection, address = self.dataSocket.accept()
        listing = ""
        # detect the current working directory
        path = os.getcwd()

        # read the entries
        with os.scandir(path) as listOfEntries:
            for entry in listOfEntries:
                # print all entries that are files:
                listing = listing + '\t' + entry.name
        dataConnection.send(listing.encode())
        print("Directory listing sent.")
        dataConnection.close()
        message = "226 Listing transfer complete.\r\n"
        self.controlConnection.send(message.encode())
        self.dataSocket.close()
        self.dataSocket = None
        return

    def PWD(self):#Sends the path of the current directory.
        print("Print working directory requested.")
        pwd = os.getcwd()
        message = "257 " + pwd + " is the current working directory.\r\n"
        self.controlConnection.send(message.encode())
        print("Working directory sent.")

    def CWD(self, path):#Changes the working directory.
         print("Change working directory requested.")
         if os.path.exists(path):
             os.chdir(path)
             message = "250 Working directory changed.\r\n"
             self.controlConnection.send(message.encode())
             print("Changed working directory.")
         else:
             message = "550 The path name specified could not be found.\r\n"
             self.controlConnection.send(message.encode())
             print("Unable to change working directory")


    def RMD(self, dir):#Removes a directory.
        print("Remove directory requested.")
        if os.path.exists(dir):
            os.rmdir(dir)
            print("Directory removed.")
            message = "250 Directory removed.\r\n"
            self.controlConnection.send(message.encode())
        else:
            print("Unable to remove directory.")
            message = "550 Directory does not exist.\r\n"
            self.controlConnection.send(message.encode())

    def MKD(self, newDir):#Creates a new diretory.
        print("Make directory requested.")
        if os.path.exists(newDir):
            print("Directory already exists.")
            message="521 Directory already exists.\r\n"
            self.controlConnection.send(message.encode())
        else:
            os.mkdir(newDir)
            print("Directory created.")
            message="257 Directory created.\r\n"
            self.controlConnection.send(message.encode())

    def DELE(self, pathName):#Deletes a stored on the server.
        print("Delete file requested.")
        if os.path.exists(pathName):
            os.remove(pathName)
            print("File Deleted.")
            message = "250 File deleted.\r\n"
            self.controlConnection.send(message.encode())
        else:
            print("Unable to delete file.")
            message = "450 Requested file could not be deleted.\r\n"
            self.controlConnection.send(message.encode())

    def TYPE(self, type):#Changes the type to ascii or binary mode.
        print("Type change requested.")
        if type=='A':
            message = "200 ascii mode activated.\r\n"
            self.controlConnection.send(message.encode())
            self.type='A'
        elif type=='I':
            message = "200 binary mode activated.\r\n"
            self.controlConnection.send(message.encode())
            self.type='I'
        else:
            message = "500 unknown data type requested.\r\n"
            self.controlConnection.send(message.encode())
            print("no type found")
        print("Type changed.")

    def RETR(self, filename):#Client is able to download a file using this function
        print("Client download file requested.")
        if os.path.exists(filename):#Check that the requested file exists.

            message = "150 Opening data connection.\r\n"
            self.controlConnection.send(message.encode())

            if not self.hasPort:
                dataConnection, address = self.dataSocket.accept()

            if self.type=='A':
                file = open(filename, 'r')
                fileData = file.read(8192)

                while fileData:
                    print("reading file")
                    if not self.hasPort:
                        dataConnection.send((fileData + '\r\n').encode())
                    else:
                        self.dataSocket.send((fileData + '\r\n').encode())
                    fileData = file.read(8192)

                file.close()
                if not self.hasPort:
                    dataConnection.close()
                message = "226 file transfer completed successfully.\r\n"
                self.controlConnection.send(message.encode())

            elif self.type=='I':
                file = open(filename, 'rb')
                fileData = file.read(8192)

                while fileData:
                    print("reading file")
                    if not self.hasPort:
                        dataConnection.send(fileData)
                    else:
                        self.dataSocket.send(fileData)
                    fileData = file.read(8192)

            file.close()
            if not self.hasPort:
                dataConnection.close()
            self.dataSocket.close()
            self.dataSocket = None
            message = "226 file transfer completed successfully.\r\n"
            self.controlConnection.send(message.encode())
            print("File downloaded to client.")
        else:
            print("Requested file does not exist.")
            message = "550 File requested does not exist.\r\n"
            self.controlConnection.send(message.encode())

    def STOR(self, filename):#Function that allows the client to upload to the server
        print("Upload file requested.")
        if not os.path.exists(filename):#check is the file already exists to avoid over writing it.
            message = "150 Opening data connection"
            self.controlConnection.send(message.encode())
            if not self.hasPort:
                dataConnection, address = self.dataSocket.accept()

            if self.type=='A':
                file = open(filename, 'w')

                if not self.hasPort:
                    fileData = dataConnection.recv(8192).decode()
                else:
                    fileData = self.dataSocket.recv(8192).decode()

                while fileData:
                    print("writing file - A")
                    file.write(fileData)
                    if not self.hasPort:
                        fileData = dataConnection.recv(8192).decode()
                    else:
                        fileData = self.dataSocket.recv(8192).decode()

                file.close()
                if not self.hasPort:
                    dataConnection.close()
                self.dataSocket.close()
                self.dataSocket = None
                message = "226 file transfer completed successfully.\r\n"
                self.controlConnection.send(message.encode())

            elif self.type=='I':
                file = open(filename, 'wb')
                if not self.hasPort:
                    fileData = dataConnection.recv(8192)
                else:
                    fileData = self.dataSocket.recv(8192)

                while fileData:
                    file.write(fileData)
                    if not self.hasPort:
                        fileData = dataConnection.recv(8192)
                    else:
                        fileData = self.dataSocket.recv(8192)

                file.close()
                message = "226 file transfer completed successfully.\r\n"
                self.controlConnection.send(message.encode())
                if not self.hasPort:
                    dataConnection.close()
                self.dataSocket.close()
                self.dataSocket = None
            print("File uploaded to server.")
        else:
            print("File already exists.")
            message = "550 Filename already exists.\r\n"
            self.controlConnection.send(message.encode())

    def SYST(self):
        print("System requested.")
        message = "215 " + os.name + ".\r\n"
        self.controlConnection.send(message.encode())
        print("System sent.")

    def NOOP(self):
        print("Noop requested.")
        message = "200 NOOP OK\r\n"
        self.controlConnection.send(message.encode())
        print("Noop sent.")
    def QUIT(self):
        print("Quit requested.")
        message = "221 FTP connection terminated.\r\n"
        self.controlConnection.send(message.encode())
        self.controlConnection.close()
        print("Connection closed.")

    def UNKNOWN(self):
        print("Unknown command.")
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

    while True:
        controlSocket.listen(1)
        controlConnection, controlAddress = controlSocket.accept()
        print("New thread created.")
        thread = FTPServer(controlConnection, controlAddress)
        thread.start()


if __name__ == '__main__':
    Main()