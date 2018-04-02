# ELEN 4017 – Network Fundamentals Project
For detailed description of how the application was designed, features implemented and critical analysis of the solution, see the report within the report folder of this repository. The readme file aims to outline how to install and run the application as well as explaining what each of the files do within the repo.

The primary files of interest are the ftpServer.py and ftpRipper.py. These are the main files for the server and client. the dummyClient.py and dummyServer.py files correspond to the testing client and server applications that were set up using standard python libraries. the ftpClient.py file is a testing client, used to test server functionality. it does not provide any user interaction but rather has hard coded functionality to programmatically test the server.

## Server
Running of the server code is relatively simple:
```
python3 ftpServer.py
```

If you get a permissioning problem running the server, you might need to elevate the process as it uses port 21. If this is the case, run:
```
sudo python3 ftpServer.py
```
## Client
Running the client is a bit more complex due to the custom libraries used in setting up the user interface. A virtual python environment is highly recommended in this to keep things within the right scope. The installation process for this is defined by running the following:
```
virtualenv venv
source venv/bin/activate
```

this will: create a virtual environment, and then activate the venv. Next, required the python libraries are installed with:

```
pip install -r requirements.txt
```

At this point all but one libraries have been installed. The last one is the python-prompt-toolkit. Unfortunately, this has to be installed from source as the developers have not put the latest version onto pip yet. To install this, run the following commands (from within the venv created before, and from the root folder of the ftp ripper repo directory):

```
git clone https://github.com/jonathanslenders/python-prompt-toolkit
cd python-prompt-toolkit
pip install . 
```

To ensure that the correct version of python-prompt-toolkit has been installed, run from within the venv:
```
pip list | grep "prompt-toolkit" 
```

This should show version 2.x. If this is correctly installed. If so, the client can now be run with:
```
python3 ftpRipper.py
```
