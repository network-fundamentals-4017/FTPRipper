import ftplib
import sys

connected=False

def ll(params):
    FileStreem = []
    ftp.dir(FileStreem.append)
    for line in FileStreem:
        print("", line)

def cd(path):
    ftp.cwd(path[0])

def pwd(args):
    print(ftp.pwd())

def close(args):
    ftp.quit()
    global connected
    connected=False
    result = input("connection to the server has been closed. Do you want to make a new connection (Y/n)")
    if result == "" or result == "Y" or result == "y":
        return
    sys.exit()

runOptions = {
    'll': ll,
    'cd': cd,
    'pwd': pwd,
    'close': close
}

def userLogin():

    server = False
    global ftp
    while not server:
        try:
            serverAddress = input("ServerAddress: ")
            ftp = ftplib.FTP(serverAddress)
            print("connected to: " + serverAddress)
            server = True
        except:
            print("Could not connect to the server"+ sys.exc_info()[0])

    login = False
    while not login:
        try:
            username = input("Username: ")
            password = input("Password: ")
            if username=="" and password == "":
                username="anonymous"
                password="anonymous@"
            ftp.login(username,password)
            login = True
        except:
            print("Could not log into the server" + str(sys.exc_info()[0]))
    if server and login:
        print("Logged into server: %s" %(serverAddress))
        print(ftp.getwelcome())
        print("In FTP shell")
        global connected
        connected=True


while 1: #Main program loop

    while connected:
        userInput = input("> ")
        command = userInput.split()[0]

        if len(userInput.split())>1:
            params = userInput.split()[1:len(userInput)]
        else:
            params=[]
        runOptions[command](params)
    if not connected:
        userLogin()