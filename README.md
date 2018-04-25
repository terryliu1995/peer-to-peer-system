<<<<<<< HEAD
# peer-to-peer-system
=======
# peer-to-peer-system
## What is this system used for?
Internet protocol standards are defined in documents called “Requests for Comments” (RFCs). RFCs are available for download from the IETF web site (http://www.ietf.org/). Rather than using this centralized server for downloading RFCs, you will build a P2P-CI system in which peers who wish to download an RFC that they do not have in their hard drive, may download it from another active peer who does. All communication among peers or between a peer and the server will take place over TCP.  
+ There is a centralized server, running on a well-known host and listening on a well-known port, which keeps information about the active peers and maintains an index of the RFCs available at each active peer.
+ When a peer decides to join the P2P-CI system, it opens a connection to the server to register itself and provide information about the RFCs that it makes available to other peers. This connection remains open as long as the peer remains active; the peer closes the connection when it leaves the system (becomes inactive). 
+ Since the server may have connections open to multiple peers simultaneously, it spawns a new process to handle the communication to each new peer. 
+ When a peer wishes to download a specific RFC, it provides the RFC number to the server over the open connection, and in response the server provides the peer with a list of other peers who have the RFC; if no such active peer exists, an appropriate message is transmitted to the requesting peer. Additionally, each peer may at any point query the server to obtain the whole index of RFCs available at all other active peers. 
+ Each peer runs a upload server process that listens on a port specific to the peer ; in other words, this port is not known in advance to any of the peers. When a peer A needs to download an RFC from a peer B, it opens a connection to the upload port of peer B, provides the RFC number to B, and B responds by sending the (text) file containing the RFC to A over the same connection; once the file transmission is completed, the connection is closed. 
## How to run this project?
This project uses Python 2.7.10, make sure you have this version of Python.
#### 1. run the centralized server
```
  python server.py
```
#### 2. run clients
If you just have one machine, open one terminal for one client and run following command:
```
  python client.py
```
## Contributor
Zhiyu Liu @ncsu
>>>>>>> 7a9da0e40def4e724075193c08b03fb9c20e501f
