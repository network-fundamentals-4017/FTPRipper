import socket
import sys


def Main():
    host = '10.30.240.173'
    port = 21

    print("Begin FTP Client...")
    # Connect to the server
    try:
        controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        controlSocket.connect((host, port))
    except socket.error:
        print("Unable to reach server...")
        sys.exit()
    print("Socket established")

    data = controlSocket.recv(8192).decode()
    print("S: " + data)
    if data.startswith("220"):
        if userLogin(controlSocket):
            getList(controlSocket)
            # setMode(controlSocket)
            # setStructure(controlSocket)
            # getSystem(controlSocket)
            # setPort(controlSocket)
            # changeWorkingDirectory(controlSocket, 'files')
            # downloadBinFiles(controlSocket,'files/doc.txt')
            # deleteFile(controlSocket, 'files/doc.txt')
            # printDirectory(controlSocket)
            # removeDirectory(controlSocket, 'newDir')
            # makeDirectory(controlSocket, 'newDir')
            # getList(controlSocket)
            uploadFile(controlSocket, 'files/test2.txt', 'test2.txt')
    # printDirectory(controlSocket)
    # quit(controlSocket)
    controlSocket.close()


def userLogin(controlSocket):
    message = 'USER group10\r\n'
    controlSocket.send(message.encode())
    print("C: " + message)
    data = controlSocket.recv(8192).decode()
    print("S: " + data)
    if data.startswith("331") or data.startswith("332"):
        message = 'PASS osh4ogoo\r\n'
        controlSocket.send(message.encode())
        print("C: " + message)
        data = controlSocket.recv(8192).decode()
        print("S: " + data)
        if data.startswith("230"):
            print("Successfully logged into ftp server :)")
            return True
        if data.startswith("530"):
            print("Login failed")
            return False
    else:
        return False

def getPortNumber(controlSocket):
    message = 'PASV\r\n'
    controlSocket.send(message.encode())
    print("C: " + message)
    data = controlSocket.recv(8192).decode()
    print("S: " + data)
    data = data[data.find('(') + 1:data.find(')')]
    data = data.split(",")
    dataHost = '.'.join(data[0:4])
    dataPort = data[-2:]
    dataPort = (int(dataPort[0]) * 256) + int(dataPort[1])
    return (dataHost, dataPort)


def setupDataConnection(controlSocket, dataHost, dataPort):
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSocket.connect((dataHost, dataPort))
    return dataSocket


def setMode(controlSocket):
    message = ('MODE S\r\n')
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def setStructure(controlSocket):
    message = ('STRU F\r\n')
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def setPort(controlSocket):
    address = socket.gethostbyname(socket.gethostname())
    address = address.split('.')
    address = ','.join(address)
    address = address + ',31,60'
    message = 'PORT ' + address + '\r\n'
    print("C: " + message)
    controlSocket.send(message.encode())
    print("post send")
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def getDataSocket(controlSocket):
    dataHost, dataPort = getPortNumber(controlSocket)
    dataSocket = setupDataConnection(controlSocket, dataHost, dataPort)
    return dataSocket


def getList(controlSocket):
    dataSocket = getDataSocket(controlSocket)
    message = 'LIST\r\n'
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)
    data = dataSocket.recv(8192).decode()
    print("S: " + data)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)
    dataSocket.close()


def downloadBinFiles(controlSocket, filePath):
    message = 'TYPE I\r\n'
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)
    dataSocket = getDataSocket(controlSocket)
    message = 'RETR {}\r\n'.format(filePath)
    controlSocket.send(message.encode())
    print("S: " + controlSocket.recv(8192).decode())

    file_data = dataSocket.recv(8192)
    f = open("text.txt", 'wb')

    while file_data:
        f.write(file_data)
        file_data = dataSocket.recv(8192)
    print("File download complete")
    print("S: " + controlSocket.recv(8192).decode())


def changeWorkingDirectory(controlSocket, path):
    message = ('CWD {}\r\n'.format(path))
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def changeToParentDirectory(controlSocket):
    message = ('CDUP \r\n')
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def printDirectory(controlSocket):
    message = ('PWD \r\n')
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def makeDirectory(controlSocket, name):
    message = ('MKD {}\r\n'.format(name))
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def removeDirectory(controlSocket, name):
    message = ('RMD {}\r\n'.format(name))
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def deleteFile(controlSocket, pathName):
    message = ('DELE {}\r\n'.format(pathName))
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def uploadFile(controlSocket, destination, fileName):
    message = 'TYPE I\r\n'
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)
    dataSocket = getDataSocket(controlSocket)
    message = 'STOR {}\r\n'.format(destination)
    controlSocket.send(message.encode())
    print("S: " + controlSocket.recv(8192).decode())

    file = open('{}'.format(fileName), 'rb')
    reading = file.read(8192)

    while reading:
        dataSocket.send(reading)
        reading = file.read(8192)
    print("File upload complete")
    file.close()
    dataSocket.close()
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def getSystem(controlSocket):
    message = "SYST\r\n"
    print("C: " + message)
    controlSocket.send(message.encode())
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


def quit(controlSocket):
    message = 'QUIT\r\n'
    controlSocket.send(message.encode())
    print("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    print("S: " + controlData)


if __name__ == '__main__':
    Main()
