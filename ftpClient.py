import asyncore, asynchat
import re, socket

port = 21
print("Begin FTP Process")
#Contact the FTP server at port 21 using TCP
class controlConnection(asynchat.async_chat):

    def __init__(self, host):
        asynchat.async_chat.__init__(self)
        self.host = host
        self.commands = ["PWD", "QUIT"]
        print("Initializing")
        self.set_terminator("\n")
        self.data=""
        self.username = "username"
        self.password = "123"

        self.response = []

        self.handler = self.ftp_handle_connect

        # connect to ftp server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.host, 21))
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
        self.response.append(data)
        if not re.match("\d\d\d ", data):
            return

        response = self.response
        self.response = []

        for line in response:
            print("S: ", line)
        #this was the last line in the response, check if special treatment is needed

        #process response
        if self.handler:
            #call the response handler
            handler = self.handler
            self.handler = None

            handler(response)
            if self.handler:
                return #follow-up command in progress

        #send next command from queue
        try:
            print("C: " + self.commands[0])
            self.push(self.conmmands.pop(0) + "\r\n")
        except IndexError:
            pass  # no more commands

    def ftp_handle_connect(self, response):
        code = response[-1][:3]
        if code == "220":
            self.push("USER " + self.username + "\r\n")
            self.handler = self.ftp_handle_user_response
        else:
            raise Exception("ftp login failed")

    def ftp_handle_user_response(self, response):
        code = response[-1][:3]
        if code == "230":
            return #user accepted
        elif code == "331" or code == 332:
            self.push("PASS " + self.password + "\r\n")
            self.handler = self.ftp_handle_pass_response
        else:
            raise Exception("ftp login failed: password not accepted")

    def ftp_handle_pass_response(self, response):
        code = response[-1][:3]
        if code == "230":
            return #username and password accepted
        else:
            raise Exception("ftp login failed: username/password not accepted")

controlConnection("ftp.python.org")
asyncore.loop()