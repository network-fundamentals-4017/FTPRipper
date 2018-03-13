import asyncore, asynchat
import re, socket

port = 21
print("Begin FTP Process")
#Contact the FTP server at port 21 using TCP
class controlConnection(asynchat.async_chat):

    def __init__(self, host):
        asynchat.async_chat.__init__(self)

        self.commands = ["USER anonymous", "PASS anonymous@", "PWD", "QUIT"]
        print("Initializing")
        self.set_terminator("\n")
        self.data=""

        # connect to ftp server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, 21))

    def handle_connect(self):
        #connection succeeded
        pass
    def handle_expt(self):
        #connection failed
        self.close()
    def collect_incoming_data(self, data):
        #receive some incoming data
        self.data = self.data + data
    def found_terminator(self):
        #got a response line
        data = self.data
        if data.endswith("\r"):
            data = data[:-1]
        self.data = ""

        print("S:" + str(data))

        if re.match("\d\d\d ", data):
            #this was the last line in this response, send the next command to the server
            try:
                command = self.commands.pop(0)
            except IndexError:
                pass #no more commands
            else:
                print("C:", command)
                self.push(command + "\r\n")

controlConnection("ftp.python.org")
asyncore.loop()