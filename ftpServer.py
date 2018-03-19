import socket

def Main():
    print(socket.gethostname())
    host = socket.gethostbyname(socket.gethostname())
    port  = 5000

    controlSocket = createControlSocket(host, port)
    print("Command:", controlSocket.getsockname())
    controlSocket.listen(1)

    controlConnection, controlAddress = controlSocket.accept()


def createControlSocket(host, port):
    controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controlSocket.bind((host, port))
    return controlSocket













if __name__ == '__main__':
    Main()