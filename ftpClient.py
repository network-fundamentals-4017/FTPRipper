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
        self.password = "123"

        # connect to ftp server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, 21))
        self.last_command = None

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

        if not re.match("\d\d\d ", data):
            return
        #this was the last line in the response, check if special treatment is needed

        if self.last_command == None:
            #handle connection
            if data.startswith("220"):
                self.last_command = "USER"
                self.push("USER anonymous\r\n")
                return
            else:
                raise Exception("ftp login failed")
        elif self.last_command == "USER":
            #handle user response
            if data.startswith("230"):
                pass #user accepted
            elif data.startswith("331") or data.startswith("333"):
                self.last_command = "PASS"
                self.push("PASS " +self.password + "\r\n")
                return
            else:
                raise Exception("ftp login failed")
        elif self.last_command == "PASS":
            if data.startswith("230"):
                pass
            else:
                raise Exception("ftp login failed")

        #send the next command to the server
        try:
            self.push(self.conmmands.pop(0) + "\r\n")
        except IndexError:
            pass #no more commands

controlConnection("ftp.python.org")
asyncore.loop()