import socket, os

def Main():
    print(socket.gethostname())
    host = socket.gethostbyname(socket.gethostname())
    port = 21

    controlSocket = createControlSocket(host, port)
    print("Command:", controlSocket.getsockname())
    controlSocket.listen(1)

    controlConnection, controlAddress = controlSocket.accept()
    USER(controlConnection)
    while True:
        data = controlConnection.recv(1024).decode()
        if not data:
            break

        command = getCommnad(data)
        info = getInfo(data)
        if command=="PASV":
            dataSocket = PASV(controlConnection)
        elif command=="LIST":
            LIST(controlConnection, dataSocket)

def createControlSocket(host, port):
    controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controlSocket.bind((host, port))
    return controlSocket

def USER(controlConnection):
    message = "220 Server socket established"
    controlConnection.send(message.encode())
    print(message)
    data = controlConnection.recv(1024).decode()
    username = data[5:].strip()
    if checkUserExists(username):
        PASS(controlConnection, username)
    else:
        message = "530 Unknown user"
        controlConnection.send(message.encode())

def PASS(controlConnection, username):
    message = "331 Password required"
    controlConnection.send(message.encode())
    data = controlConnection.recv(1024).decode()
    password = data[5:].strip()
    if checkPassword(username, password):
        message = "230 Login successful"
        controlConnection.send(message.encode())
    else:
        message = "530 Incorrect Password"

def checkUserExists(username):
    return True

def checkPassword(username, password):
    return True

def getCommnad(data):
    command = data[:4]
    return command

def getInfo(data):
    info = data[data.find(' ')+1:]
    return info

def PASV(controlConnection):
    address = socket.gethostbyname(socket.gethostname())
    address = address.split(".")
    address = ','.join(address)
    address = "("+address+",30,60)"
    message = "227 Passive Mode " + address
    dataSocket = getDataSocket(socket.gethostbyname(socket.gethostname()), 7740)
    controlConnection.send(message.encode())
    print("Passive data connection set up")
    return dataSocket

def getDataSocket(host, port):
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSocket.bind((host, port))
    dataSocket.listen(1)
    return dataSocket

def LIST(controlConnection, dataSocket):
    message = "150 Here comes the directory listing..."
    controlConnection.send(message.encode())
    dataConnection, address = dataSocket.accept()
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

if __name__ == '__main__':
    Main()