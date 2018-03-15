import ftplib
import sys

connected = False

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def ll(params):
    FileStreem = []
    ftp.dir(FileStreem.append)
    for line in FileStreem:
        print("", line)


def ls(params):
    for file in ftp.nlst():
        print(file, end='\t')
    print()


def cd(params):
    ftp.cwd(params[0])


def pwd(params):
    print(ftp.pwd())


def rm(params):
    try:
        ftp.delete(params[0])
    except Exception as e:
        print(bcolors.WARNING+"Could not delete " + str(e)+bcolors.ENDC)


def mkdir(params):
    ftp.mkd(params[0])


def help(params):
    print("All possible commands are:")
    for command in runOptions.items():
        if (len(command[0]) < 4):
            print(command[0] + "\t\t" + command[1][1])
            continue
        print(command[0] + "\t" + command[1][1])


def close(params):
    ftp.quit()
    global connected
    connected = False
    result = input(
        bcolors.WARNING + bcolors.BOLD + "connection to the server has been closed. Do you want to make a new connection (Y/n)" + bcolors.ENDC)
    if result == "" or result == "Y" or result == "y":
        return
    sys.exit()


def logout(params):
    ftp.quit()
    global connected
    connected = False
    print(bcolors.WARNING + "Your session has been closed" + bcolors.ENDC)


runOptions = {
    'll': [ll,
           "List all files and folders, with permissions, size and ownership, in the current directory of the server"],
    'ls': [ls, "List all files and folders in the current directory of the server"],
    'cd': [cd, "Change Location of the server path to specified parameter. Relative paths are acceptable"],
    'pwd': [pwd, "Print the full current server path"],
    'rm': [rm, "Remove file(or folder) on server"],
    'mkdir': [mkdir, "Create a folder on server"],
    'help': [help, "Print all commands and their descriptions"],
    'close': [close, "Terminate FTP session and close application"],
    'logout': [logout, "Close current FTP session and go back to login"],
}


def userLogin():
    server = False
    global ftp
    while not server:
        try:
            serverAddress = input("ServerAddress: ")
            if serverAddress == "":
                print(bcolors.WARNING+"Please enter a server address"+bcolors.ENDC)
                continue
            ftp = ftplib.FTP(serverAddress)
            print(bcolors.OKGREEN+ "Connected to: " + serverAddress+bcolors.ENDC)
            server = True
        except Exception as e:
            print(bcolors.FAIL+"Could not connect to the server " + str(e) +bcolors.ENDC)

    login = False
    while not login:
        try:
            username = input("Username: ")
            password = input("Password: ")
            if username == "" and password == "":
                username = "anonymous"
                password = "anonymous@"
            ftp.login(username, password)
            login = True
        except Exception as e:
            print(bcolors.FAIL+ "Could not log into the server " + str(e) +bcolors.ENDC)
    if server and login:
        print(bcolors.OKGREEN+ bcolors.UNDERLINE+ "Logged into server: %s" % (serverAddress)+bcolors.ENDC)
        print(ftp.getwelcome())
        print(bcolors.OKBLUE+"Entered FTP shell"+bcolors.ENDC)
        global connected
        connected = True


while 1:  # Main program loop

    while connected:
        userInput = input("> ")
        if len(userInput) > 0:
            command = userInput.split()[0]
            if len(userInput.split()) > 1:
                params = userInput.split()[1:len(userInput)]
            else:
                params = []
            if command in runOptions:
                runOptions[command][0](params)
            else:
                print(bcolors.WARNING+"Command: " + command + " not found. Run 'help' to view all posible commands"+bcolors.ENDC)
    if not connected:
        userLogin()
