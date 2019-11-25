# Introduction
This is a simple python-based implementation of a distributed file system.

# How to launch the system?
Kusal will write here.

# How to use it?
Kusal will write here

# Architectural Diagrams
**High-level Overview**:
![image](https://user-images.githubusercontent.com/26818010/69574658-a4b9d100-0fc0-11ea-8135-6bd87533294d.png)

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
Used for symmetrical remote procedure calls and distributed computing.
