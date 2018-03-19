import socket

def Main():
    print(socket.gethostname())
    host = socket.gethostbyname(socket.gethostname())
    port = 21

    controlSocket = createControlSocket(host, port)
    print("Command:", controlSocket.getsockname())
    controlSocket.listen(1)

    controlConnection, controlAddress = controlSocket.accept()
    requestUser(controlConnection)

    while True:
        data = controlConnection.recv(1024).decode()
        if not data:
            break

        command = getCommnad(data)
        info = getInfo(data)
        if command=="PASV":
            dataSocket = setupDataSocket(controlConnection)


def createControlSocket(host, port):
    controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controlSocket.bind((host, port))
    return controlSocket

def requestUser(controlConnection):
    message = "220 Server socket established"
    controlConnection.send(message.encode())
    print(message)
    data = controlConnection.recv(1024).decode()
    username = data[5:].strip()
    if checkUserExists(username):
        requestPassword(controlConnection, username)
    else:
        message = "530 Unknown user"
        controlConnection.send(message.encode())

def requestPassword(controlConnection, username):
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

def setupDataSocket(controlConnection):
    address = socket.gethostbyname(socket.gethostname())
    address = address.split(".")
    address = ','.join(address)
    address = "("+address+",30,60)"
    message = "227 Passive Mode " + address

    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSocket.bind((socket.gethostbyname(socket.gethostname()), 7740))
    dataSocket.listen(1)
    controlConnection.send(message.encode())
    print("Passive data connection set up")
    return dataSocket

if __name__ == '__main__':
    Main()