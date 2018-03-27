from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from fuzzyfinder import fuzzyfinder
import ftplib
import sys
import os
import socket

global connected
global runOnServer
connected = False
runOnServer = True

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


class mainCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=False)
        currentLine = document.current_line



        if (" " in currentLine):
            options=[]
        if(currentLine[0:1]=='!'):
            global runOnServer
            runOnServer = False
            try:
                options=osOptions
            except:
                osCommands("")
                options=osOptions
        else:
            runOnServer = True
            options = runOptions
        matches = fuzzyfinder(word_before_cursor, options)
        for m in matches:
            yield Completion(m, start_position=-len(word_before_cursor))

def osls(params):
    print(os.getcwd())

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
    try:
        ftp.cwd(params[0])
    except Exception as e:
        print("Failed to change directory " + str(e))


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

def push(params):
    file = params[0]
    ext = os.path.splitext(file)[1]
    try:
        if ext in (".txt", ".htm", ".html"):
            ftp.storlines("STOR " + file, open(file))
        else:
            ftp.storbinary("STOR " + file, open(file, "rb"), 1024)
        print(bcolors.OKGREEN+"Upload Successful!"+bcolors.ENDC)
    except Exception as e:
        print(bcolors.FAIL+"Upload failed with error " + str(e) + bcolors.ENDC)

def get(params):
    filename=params[0]
    try:
        print("Retrieving file...")
        ftp.retrbinary("RETR " + filename ,open(filename, 'wb').write)
        print(bcolors.OKGREEN+"File retrieved successfully"+bcolors.ENDC)
    except Exception as e:
        print (bcolors.FAIL+"Error occured when getting File: " +str(e)+bcolors.ENDC)

def logout(params):
    ftp.quit()
    global connected
    connected = False
    print(bcolors.WARNING + "Your session has been closed" + bcolors.ENDC)


def osCommands(userInput):

    def oscd(params):
        print(params)
        os.chdir(params[0])

    def ospwd(params):
        print(os.getcwd())

    def osls(params):
        if len(params)==0: #if the user did not spesify a path of files to print, use current directory
            path=os.getcwd()
        else:
            path=params[0]
        print(path)
        fileList = os.listdir(path)
        for file in fileList:
            print(file, end="\t")
        print()

    def oshelp(params):
        print("All possible commands for system calls (defined by !) are:")
        for command in osOptions.items():
            if (len(command[0]) < 4):
                print(command[0] + "\t\t" + command[1][1])
                continue
            print(command[0] + "\t" + command[1][1])

    global osOptions
    osOptions = {
        'cd': [oscd,"Change the current working directory"],
        'pwd': [ospwd,"List the current working directory path"],
        'ls': [osls,"List the files in a directory"],
        'help': [oshelp,"List help of system based commands"]
    }
    if len(userInput) > 0:
        command = userInput[0]
        if len(userInput) > 1:
            params = userInput[1:len(userInput)]
        else:
            params = []
        if command in osOptions:
            osOptions[command][0](params)
        else:
            print(bcolors.WARNING + "Command: '" + command + "' not found. Run 'help' to view all posible commands" + bcolors.ENDC)


runOptions = {
    'll': [ll,"List all files and folders, with permissions, size and ownership, in the current directory of the server"],
    'ls': [ls, "List all files and folders in the current directory of the server"],
    '!': [osCommands,"Any command proceeded by a bang will be run on the local machine(type !help for more)."],
    'cd': [cd, "Change Location of the server path to specified parameter. Relative paths are acceptable"],
    'pwd': [pwd, "Print the full current server path"],
    'rm': [rm, "Remove file(or folder) on server"],
    'download': [get, "Retrives a file from the remote server to current location on local machine"],
    'upload': [push,"Upload file from local machine to the remote server"],
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
        userInput = prompt(u'>',
                            history=FileHistory('history.txt'),
                            auto_suggest=AutoSuggestFromHistory(),
                            completer=mainCompleter(),
                            )
        if len(userInput) > 0:
            command = userInput.split()[0]
            if len(userInput.split()) > 1:
                params = userInput.split()[1:len(userInput)]
            else:
                params = []
            if command in runOptions:
                runOptions[command][0](params)
            else:
                print(bcolors.WARNING+"Command: '" + command + "' not found. Run 'help' to view all posible commands"+bcolors.ENDC)
    if not connected:
        userLogin()