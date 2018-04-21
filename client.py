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
        #open a thread for upload server
        upload_thread = threading.Thread(target=waitUploadConnection, args=())
        upload_thread.start()
        #wait upload listener to be prepared
        time.sleep(1)
        #handleRequest
        self.handleRequest()
    
    def handleRequest(self):
        print 'connect: connect to server\n'+
              'add: add the rfc of this client\n'+
              'query: get all active clients\n'+
              'lookup: lookup a specific rfc\n'+
              'list: list all rfcs\n'+
              'download: download specific rfc\n'
        command_dict = {'connect':self.connect_server(), 
                        'add':self.add_rfc(),
                        'query':self.query_active(),
                        'lookup':self.lookup_rfc(),
                        'list':self.list_all(),
                        'download':self.download(),
                        'quit':self.quit()}
        while True:
            request_method = raw_input('Enter your request: ')
            command_dict.setdefault(request_method, self.invalid_request())

    def connect_server(self):
        if self.serverSocket:
            print 'Already connected'
        else:
            #create socket
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.serverSocket.connect((self.SERVER_HOSTNAME, self.SERVER_PORT_NUM))
            except BaseException, exc:
                print "Caught exception: %s" % exc
            print 'Server is connected!'
            data = 'CONNECT %s P2P-CI/1.0\n' % (str(self.UPLOAD_PORT_NUM))
            self.serverSocket.sendall(data)      

    def add_rfc(self):
        # get info of rfc
        if self.serverSocket:
            rfc_num = raw_input("Enter RFC number: ")
            rfc_title = raw_input("Enter RFC title: ")
            # construct data
            data = 'ADD RFC %s P2P-CI/1.0\n' % (rfc_num)+
                'Host: %s\n' % (socket.gethostname())+
                'Port: %s\n' % (self.UPLOAD_PORT_NUM)+
                'Title: %s\n' % (rfc_title)
            self.serverSocket.sendall(data)
            # receive response
            recv_msg = self.serverSocket.recv(1024)
            print recv_msg
        else:
            print 'please connect first'
    
    def query_active(self):
        if self.serverSocket:
            data = 'QUERY\n'
            self.serverSocket.sendall(data)
            recv_data = pickle.loads(self.serverSocket.recv(1024))
            print recv_data
        else:
            print 'please connect first'

    def list_all(self):
        if self.serverSocket:
            data = 'LIST ALL P2P-CI/1.0\n'+
                   'Host: %s\n' % (socket.gethostname())+
                   'Port: %s\n' % (self.UPLOAD_PORT_NUM)
            self.serverSocket.sendall(data)
            # receive response
            recv_msg = self.serverSocket.recv(1024)
            print recv_msg
        else:
            print 'please connect first'
        

    def lookup_rfc(self):
        if self.serverSocket:
            rfc_num = raw_input("Provide RFC number: ")
            rfc_title = raw_input("Provide RFC title: ")
            # format request data
            data = 'LOOKUP RFC %s P2P-CI/1.0\n' % (rfc_num)+
                'Host: %s\n' % (socket.gethostname())+
                'Port: %s\n' % (self.UPLOAD_PORT_NUM)+
                'Title: %s\n' % (rfc_title)
            self.serverSocket.sendall(data)
            # receive response
            recv_msg = self.serverSocket.recv(1024)
            print recv_msg
        else:
            print 'please connect first'


    def download(self):
        if self.serverSocket:
            rfc_num = raw_input("Enter RFC number you wish to download: ")
            host_name = raw_input("Enter hostname from which you wish to download: ")
            peer_upload_port = raw_input("Enter the upload port: ")
            os_info = platform.platform()
            rfc_path = 'rfc%s.txt' % (rfc_num)
            data = 'GET RFC %s P2P-CI/1.0\n' % (rfc_num)+
                   'Host: %s\n' % (host_name)+
                   'OS: %s\n' % (os_info)
            self.downloadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.downloadSocket.connect((host_name, int(peer_upload_port)))
            except BaseException, exc:
                print "Caught exception: %s" % exc
                return
            self.downloadSocket.sendall(data)
            print 'requesting...'
            recv_data = self.downloadSocket.recv(1024)
            print recv_data
            
        else:
            print 'please connect first'

    def quit(self):
        if self.serverSocket:
            
        else:
            
    def invalid_request(self):
        print 'Error. Invalid Command!'

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
        