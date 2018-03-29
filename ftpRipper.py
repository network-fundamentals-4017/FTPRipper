#!/usr/bin/env python
from __future__ import unicode_literals

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, Align, Float, FloatContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.completion import Completer, Completion
from fuzzyfinder import fuzzyfinder
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea, SearchToolbar
from prompt_toolkit.layout.dimension import LayoutDimension as D
import prompt_toolkit
import sys
import os
import socket

global controlSocket
global connected
global runOnServer
tab = "    "
connected = False
runOnServer = True

def get_statusbar_text():
    if runOnServer:
        return [
            ('class:title', ' Server Mode...'),
            ('class:title', ' (Press [Ctrl-Q] to quit.)'),
            ('class:title', ' (Press [Ctrl-S] to toggle client and server mode)'),

        ]
    if not runOnServer:
        return [
            ('class:title', ' Client Mode...'),
            ('class:title', ' (Press [Ctrl-Q] to quit.)'),

        ]

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

def ll(params):
    FileStreem = []
    ftp.dir(FileStreem.append)
    outputLine = ""
    for line in FileStreem:
        outputLine+=line +"\n"
    printSystemOuput(outputLine)


def ls(params):
    dataSocket = getDataSocket()
    message = 'LIST\r\n'
    controlSocket.send(message.encode())
    printResponceOutput ("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    printResponceOutput("S: " + controlData)
    data = dataSocket.recv(8192).decode()
    printSystemOuput("S: " + data)
    controlData = controlSocket.recv(8192).decode()
    dataSocket.close()

def getDataSocket():
	dataHost, dataPort = getPortNumber()
	dataSocket = setupDataConnection(dataHost, dataPort)
	return dataSocket


def getPortNumber():
    message = 'PASV\r\n'
    controlSocket.send(message.encode())
    printResponceOutput("C: " + message)
    data = controlSocket.recv(8192).decode()
    printResponceOutput("S: " + data)
    data = data[data.find('(') + 1:data.find(')')]
    data = data.split(",")
    dataHost = '.'.join(data[0:4])
    dataPort = data[-2:]
    dataPort = (int(dataPort[0]) * 256) + int(dataPort[1])
    return (dataHost, dataPort)


def setupDataConnection(dataHost, dataPort):
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSocket.connect((dataHost, dataPort))
    return dataSocket


def cd(params):
    message = ('CWD {}\r\n'.format(params[0]))
    controlSocket.send(message.encode())
    printResponceOutput ("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    printResponceOutput("S: " + controlData)

def pwd(params):
    message = ('PWD \r\n')
    controlSocket.send(message.encode())
    printResponceOutput ("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    printSystemOuput("S: " + controlData)


def rm(params):
    message = ('RMD {}\r\n'.format(params[0]))
    controlSocket.send(message.encode())
    printResponceOutput ("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    printResponceOutput ("S: " + controlData)

def mkdir(params):
    if params[0]=="":
        printResponceOutput("No folder name spesified")
        return
    message = ('MKD {}\r\n'.format(params[0]))
    controlSocket.send(message.encode())
    printResponceOutput ("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    printResponceOutput("S: " + controlData)

def help(params):
    printSystemOuput("All possible commands are:")
    for command in runOptions.items():
        if (len(command[0]) < 4):
            printSystemOuput(command[0] + "\t\t" + command[1][1])
            continue
        printSystemOuput(command[0] + "\t" + command[1][1])

def close(params):
    ftp.quit()
    global connected
    connected = False
    result = input(
        "connection to the server has been closed. Do you want to make a new connection (Y/n)")
    if result == "" or result == "Y" or result == "y":
        return
    sys.exit()

def push(params):
    message = 'TYPE I\r\n'
    controlSocket.send(message.encode())
    printResponceOutput("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    dataSocket = getDataSocket()
    message = 'STOR {}\r\n'.format(params[1])
    controlSocket.send(message.encode())
    printResponceOutput("S: " + controlSocket.recv(8192).decode())

    file = open('{}'.format(params[0]), 'rb')
    reading = file.read(8192)

    while reading:
        dataSocket.send(reading)
        reading = file.read(8192)
    printSystemOuput("File upload complete")
    controlData = controlSocket.recv(8192).decode()
    printResponceOutput("S: " + controlData)
    file.close()
    dataSocket.close()


def get(params):
    message = 'TYPE I\r\n'
    controlSocket.send(message.encode())
    printResponceOutput("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    printResponceOutput("S: " + controlData)
    dataSocket = getDataSocket(controlSocket)
    message = 'RETR {}\r\n'.format(params[0])
    controlSocket.send(message.encode())
    printResponceOutput("S: " + controlSocket.recv(8192).decode())

    file_data = dataSocket.recv(8192)
    f = open("text.txt", 'wb')

    while file_data:
        f.write(file_data)
        file_data = dataSocket.recv(8192)
    printSystemOuput("File download complete")
    printResponceOutput("S" + controlSocket.recv(8192).decode())

def logout(params):
    message = 'QUIT\r\n'
    controlSocket.send(message.encode())
    printResponceOutput ("C: " + message)
    controlData = controlSocket.recv(8192).decode()
    printResponceOutput("S: " + controlData)

def osCommands(userInput):

    def oscd(params):
        printSystemOuput(params)
        os.chdir(params[0])

    def ospwd(params):
        printSystemOuput(os.getcwd())

    def osls(params):
        if len(params)==0: #if the user did not spesify a path of files to printSystemOuput, use current directory
            path=os.getcwd()
        else:
            path=params[0]
        fileList = os.listdir(path)
        outPut = ""
        for file in fileList:
            outPut += file + tab
        printSystemOuput(outPut)

    def oshelp(params):
        printSystemOuput("All possible commands for system calls (defined by !) are:")
        for command in osOptions.items():
            if (len(command[0]) < 4):
                printSystemOuput(command[0] + "\t\t" + command[1][1])
                continue
            printSystemOuput(command[0] + "\t" + command[1][1])

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
            printSystemOuput("Command: '" + command + "' not found. Run 'help' to view all posible commands")


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
    global controlSocket
    while not server:
        try:
            serverAddress = input("ServerAddress: ")
            if serverAddress == "":
                print("Please enter a server address")
                continue
            controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            controlSocket.connect((serverAddress, 21))
            print("Socket established")
            print("Connected to: " + serverAddress)
            server = True
        except Exception as e:
            print("Could not connect to the server " + str(e))

    data = controlSocket.recv(8192).decode()
    printResponceOutput("S: " + data)
    if data.startswith("220"):
        login = False
        while not login:
            try:
                username = input("Username: ")
                password = input("Password: ")
                if username == "" and password == "":
                    username = "anonymous"
                    password = "anonymous@"

                message = 'USER {}\r\n'.format(username)
                controlSocket.send(message.encode())
                printResponceOutput("C: " + message)
                data = controlSocket.recv(8192).decode()
                printResponceOutput("S: " + data)
                # if data.startswith("331") or data.startswith("332"):
                message = 'PASS {}\r\n'.format(password)
                controlSocket.send(message.encode())
                printResponceOutput("C: " + message)
                data = controlSocket.recv(8192).decode()
                printResponceOutput("S: " + data)
                if data.startswith("230"):
                    print("Successfully logged into ftp server :)")
                if data.startswith("530"):
                    print("Login failed")

                login = True
            except Exception as e:
                print( "Could not log into the server " + str(e))
        if server and login:
            print("Logged into server: %s" % (serverAddress))
            print("Entered FTP shell")
            global connected
            connected = True

def runCommand(_):
    splitUserInput = _.text.splitlines()
    userInput = splitUserInput[len(splitUserInput)-1]
    if userInput[0]!="!":
        runOnServer = True
        printResponceOutput("Server Command: " + userInput)

    if userInput[0]=="!":
        runOnServer = False
        printResponceOutput("Client Command: " + userInput)
    if len(userInput) > 0:
        command = userInput.split()[0]
        if len(userInput.split()) > 1:
            params = userInput.split()[1:len(userInput)]
        else:
            params = []
        if command in runOptions:
            runOptions[command][0](params)
        else:
            printResponceOutput(
                        "Command: '" + command + "' not found. Run 'help' to view all posible commands")
    left_buffer.insert_line_below()

left_buffer = Buffer(accept_handler=runCommand,
                     multiline=False,
                     completer=mainCompleter(),
                     history=FileHistory('history.txt'),
                     complete_while_typing=True
                     )

left_window = Window(BufferControl(buffer=left_buffer))

responseOutput = TextArea(
    text="FTP Communication Responses(and commands)",
    scrollbar=True,
    line_numbers=True,
    )

systemOutput = TextArea(
    text="System Output",
    scrollbar=True,
    line_numbers=True,
    )

def printResponceOutput(text):
    currentText=responseOutput.document.text
    newText = currentText+"\n"+text
    tempDoc = prompt_toolkit.document.Document(text=newText)
    responseOutput.document = tempDoc


def printSystemOuput(text):
    currentText=systemOutput.document.text
    newText = currentText+"\n"+text
    tempDoc = prompt_toolkit.document.Document(text=newText)
    systemOutput.document = tempDoc

body = FloatContainer(
    content=VSplit([
    left_window,

    # A vertical line in the middle. We explicitly specify the width, to make
    # sure that the layout engine will not try to divide the whole width by
    # three for all these windows.
    Window(width=1, char='|', style='class:line'),

    # Display the Result buffer on the right.
        responseOutput,
        systemOutput,
]),
    floats=[
        Float(xcursor=True,
              ycursor=True,
              content=CompletionsMenu(max_height=16, scroll_offset=1))
    ]
)

root_container = HSplit([
    # The titlebar.
    Window(content=FormattedTextControl(
        get_statusbar_text),
        height=D.exact(1),
        style='class:status'),

    # Horizontal separator.
    Window(height=1, char='-', style='class:line'),

    # The 'body', like defined above.
    body,
])

kb = KeyBindings()

@kb.add('c-c', eager=True)
@kb.add('c-q', eager=True)
def _(event):
    event.app.set_result(None)

@kb.add('c-s', eager=True)
def _(event):
    addModifier()


def addModifier():
    currentBuffer = left_buffer.text
    splitBuffer = currentBuffer.splitlines()
    newCommand = "! " + splitBuffer[len(splitBuffer)-1]
    newBuffer = ""
    for index, command in enumerate(splitBuffer):
        if index!=len(splitBuffer)-1:
            newBuffer +=command + "\n"
        if index==len(splitBuffer)-1:
            newBuffer += newCommand
    left_buffer.text=newBuffer


def default_buffer_changed(_):
    pass
    # right_buffer.text += "1"

application = Application(
    layout=Layout(root_container, focused_element=left_window),
    key_bindings=kb,
    mouse_support=True,
    full_screen=True)


def run():
    application.run()


if __name__ == '__main__':
    userLogin()
    run()
