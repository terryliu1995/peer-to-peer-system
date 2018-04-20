import socket
import threading
import pickle
import random
import time
import platform
import os.path
import sy

class Client(object):
    #initialize client infomation
    def __init__(self, centralized_server):
        #part1:server_name, server_port_num, server_address
        self.SERVER_HOSTNAME = centralized_server
        self.SERVER_PORT_NUM = server_port_num
        self.SERVER_ADDRESS = socket.gethostbyname(self.SERVER_HOSTNAME)
        #part2:upload_host_name, upload_port
        self.UPLOAD_HOSTNAME = socket.gethostname()
        self.UPLOAD_PORT_NUM = 50000 + randon.randint(1,1000)
        #part3: 3 different sockets: for server, for upload, for download
        self.serverSocket = None
        self.uploadSocket = None
        self.downloadSocket = None

    def main(self):
        print 'You has connected to server %s, address is %s \n' % (self.SERVER_HOSTNAME, self.SERVER_ADDRESS)
        upload_thread = threading.Thread(target=waitUploadConnection, args=())
        upload_thread.start()
        #wait upload listener to be prepared
        time.sleep(1)
        #handleRequest
        self.handleRequest()
    
    def handleRequest(self):
        

    def waitUploadConnection(self):
        self.uploadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.uploadSocket.bind((self.UPLOAD_HOSTNAME, self.UPLOAD_PORT))
        self.uploadSocket.listen(5)
        print 'upload server is established, warting for connecting peers\n'
        #open a new thread for one peer connection
        while self.active_flag:
            connection, address = self.uploadSocket.accept()
            upload_connection_thread = threading.Thread(target=self.buildConnection, args=(connection, address))
            upload_connection_thread.start()
        #join all upload connection threads and close connection
        print 'closing connections...\n'
        upload_connection_thread.join()
        self.uploadSocket.close()
        print 'upload server has been closed'

    def buildConnection(self, connection, address):





if __name__ == '__main__':
    hostname = raw_input("hostname: ")
    if hostname == 'default':
        hostname = 'localhost'
    client = Clientz(hostname)
    client.main()
        