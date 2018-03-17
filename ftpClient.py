import socket
import sys

def Main():
    host = "speedtest.tele2.net"
    port = 21

    print("Begin FTP Client...")
    #Connect to the server
    try:
        sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sct.connect((host,port))
    except socket.error:
        print("Unable to reach server...")
        sys.exit()
    print("Socket established")

    data = sct.recv(1024).decode('latin-1')
    print ("S: " + data)
    if data.startswith("220"):
        print("Provide a user")
        userLogin(sct)

    sct.close()

def userLogin(sct):
    message = 'USER anonymous\r\n'
    sct.send(message.encode('latin-1'))
    print("C: " + message)
    data = sct.recv(1024).decode('latin-1')
    print("S: " + data)
    if data.startswith("331"):
        message = 'PASS @anonymous\r\n'
        sct.send(message.encode('latin-1'))
        print("C: " + message)
        data = sct.recv(1024).decode('latin-1')
        print("S: " + data)

if __name__ == '__main__':
    Main()