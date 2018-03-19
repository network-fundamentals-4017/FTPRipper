import socket
import sys

def Main():
	host = '146.141.125.39'
	port = 21

	print("Begin FTP Client...")
	#Connect to the server
	try:
		controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		controlSocket.connect((host,port))
	except socket.error:
		print("Unable to reach server...")
		sys.exit()
	print("Socket established")

	data = controlSocket.recv(8192).decode()
	print ("S: " + data)
	if data.startswith("220"):
		userLogin(controlSocket)
		#getList(controlSocket)
		#downloadBinFiles(controlSocket,'files/test.txt')
		#changeWorkingDirectory(controlSocket, 'files')	
		#removeDirectory(controlSocket, 'newDir')
		#getList(controlSocket)
		#uploadFile(controlSocket,'files/test2.txt','test2.txt')
		#quit(controlSocket)
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
    if data.startswith("530"):
        print("Login failed")

def getPortNumber(controlSocket):
	message = 'PASV\r\n'
	controlSocket.send(message.encode())
	print("C: " + message)
	data = controlSocket.recv(8192).decode()
	print("S: " + data)
	data = data[data.find('(')+1:data.find(')')]
	data = data.split(",")
	dataHost = '.'.join(data[0:4])
	dataPort = data[-2:]
	dataPort = (int(dataPort[0])*256)+int(dataPort[1])
	return (dataHost, dataPort)
	
def setupDataConnection(controlSocket, dataHost, dataPort):
	dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	dataSocket.connect((dataHost, dataPort))
	return dataSocket

def getDataSocket(controlSocket):
	dataHost, dataPort = getPortNumber(controlSocket)
	dataSocket = setupDataConnection(controlSocket, dataHost, dataPort)
	return dataSocket	
	
def getList(controlSocket):
	dataSocket = getDataSocket(controlSocket)
	message = 'LIST\r\n'
	controlSocket.send(message.encode())
	print ("C: " + message)
	controlData = controlSocket.recv(8192).decode()
	print("S: " + controlData)
	data = dataSocket.recv(8192).decode()
	print("S: " + data)
	controlData = controlSocket.recv(8192).decode()
	dataSocket.close()
	
def downloadBinFiles(controlSocket, filePath):
	message = 'TYPE I\r\n'
	controlSocket.send(message.encode())
	print("C: " + message)
	controlData = controlSocket.recv(8192).decode()
	print("S123: " + controlData)
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
	print("S" + controlSocket.recv(8192).decode())
	
def changeWorkingDirectory(controlSocket, path):
	message = ('CWD {}\r\n'.format(path))
	controlSocket.send(message.encode())
	print ("C: " + message)
	controlData = controlSocket.recv(8192).decode()
	print("S: " + controlData)
	
def changeToParentDirectory(controlSocket):
	message = ('CDUP \r\n')
	controlSocket.send(message.encode())
	print ("C: " + message)
	controlData = controlSocket.recv(8192).decode()
	print("S: " + controlData)
	
def printDirectory(controlSocket):
	message = ('PWD \r\n')
	controlSocket.send(message.encode())
	print ("C: " + message)
	controlData = controlSocket.recv(8192).decode()
	print("S: " + controlData)

def makeDirectory(controlSocket, name):
	message = ('MKD {}\r\n'.format(name))
	controlSocket.send(message.encode())
	print ("C: " + message)
	controlData = controlSocket.recv(8192).decode()
	print("S: " + controlData)	
	
def removeDirectory(controlSocket, name):
	message = ('RMD {}\r\n'.format(name))
	controlSocket.send(message.encode())
	print ("C: " + message)
	controlData = controlSocket.recv(8192).decode()
	print("S: " + controlData)

def uploadFile(controlSocket,destination, fileName):
	message = 'TYPE I\r\n'
	controlSocket.send(message.encode())
	print("C: " + message)
	controlData = controlSocket.recv(8192).decode()
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
	
def quit(controlSocket):
	message = 'QUIT\r\n'
	controlSocket.send(message.encode())
	print ("C: " + message)
	controlData = controlSocket.recv(8192).decode()
	print("S: " + controlData)
	


if __name__ == '__main__':
	Main()