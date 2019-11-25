# Introduction
This is a simple python-based implementation of a distributed file system.

# How to launch the system?
Kusal will write here.

# How to use it?
Kusal will write here

# Architectural Diagrams
![diagram](https://i.imgur.com/chKu2DG.jpg)
## Nameserver
Responds to client requests, continuously checks for alive storage servers by trying to connect in certain intervals
## Client
Makes requests to Nameserver to get informations about Storage servers, then performs those operations in interaction with Storage server
## Storage Server
Responds to client request and gives feedback to Nameserver about changes

# Communication Protocols used - RPyC
Used for symmetrical remote procedure calls and distributed computing.
