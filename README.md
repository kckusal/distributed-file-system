# Introduction
This is a simple python-based implementation of a distributed file system.

# How to launch the system?
Make sure you first have the following requirements met:

**For client**: Python3 with these libraries—rpyc, prompt-toolkit, prompt, tqdm (Install simply with *pip3 install \** where * refers to one of these library)

**For NameServer & StorageServers**: Python3 with rpyc

Then, run at least 2 storage servers if your replication factor is 2. It is set to 2 in our implementation and assumed that will always be >=2.

Run nameserver.py (*python3 nameserver.py*)

Finally, run the client.py script (*python3 client.py*).


# How to use it?
Kusal will write here

# Architectural Diagrams
**High-level Overview**:
![diagram](https://i.imgur.com/chKu2DG.jpg)

**Interaction/Use-case Scenario: Upload a file**:
![image](https://user-images.githubusercontent.com/26818010/69574542-586e9100-0fc0-11ea-95f4-6b26e008272f.png)

**Interaction/Use-case Scenario: Download a file**:
![image](https://user-images.githubusercontent.com/26818010/69574565-691f0700-0fc0-11ea-8343-c1a77b93f7f4.png)

### Nameserver
Responds to client requests, continuously checks for alive storage servers by trying to connect in certain intervals.

### Client
Interacts with DFS system. Makes requests to Nameserver internally to get informations about Storage servers and files, as well as puts/gets file to/from Storage servers directly internally.

### Storage Server
Responds to client request and gives feedback as well as follow command to/from Nameserver about replication and syncing.

# Communication Protocols used - RPyC
RPyC is a popular Python library used for remote procedure calls. All communications between Naming Server, Storage Servers, and the Client in our application is done using RPyC as it is simple to use and allows us to call remote methods and attributes in a local context.
