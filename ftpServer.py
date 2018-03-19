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









if __name__ == '__main__':
    Main()