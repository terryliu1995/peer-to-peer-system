import socket
import threading
import pickle
import random
import time
import platform
import os.path
import sys

class Client(object):
    #initialize client infomation
    def __init__(self, centralized_server):
        #part1:server_name, server_port_num, server_address
        self.SERVER_HOSTNAME = centralized_server
        self.SERVER_PORT_NUM = 7734
        self.SERVER_ADDRESS = socket.gethostbyname(self.SERVER_HOSTNAME)
        #part2:upload_host_name, upload_port
        self.UPLOAD_HOSTNAME = socket.gethostname()
        self.UPLOAD_PORT_NUM = 50000 + random.randint(1,1000)
        #part3: 3 different sockets: for server, for upload, for download
        self.serverSocket = None
        self.uploadSocket = None
        self.downloadSocket = None
        #upload server listen flag
        self.client_active = True

    def main(self):
        print 'you are in main function'
        #open a thread for upload server
        upload_thread = threading.Thread(target=self.waitUploadConnection, args=())
        upload_thread.start()
        #wait upload listener to be prepared
        time.sleep(0.5)
        #handleRequest
        self.handleRequest()
    
    def handleRequest(self):
        print 'connect: connect to server\n'
        print 'add: add the rfc of this client\n'
        print 'query: get all active clients\n'
        print 'lookup: lookup a specific rfc\n'
        print 'list: list all rfcs\n'
        print 'download: download specific rfc\n'
        #print 'check'
        #use dict to simplify
        command_dict = {'connect':self.connect_server, 
                        'add':self.add_rfc,
                        'query':self.query_active,
                        'lookup':self.lookup_rfc,
                        'list':self.list_all,
                        'download':self.download,
                        'quit':self.quit}
        while self.client_active:
            request_method = raw_input('Enter your request: ')
            command_dict.setdefault(request_method, self.invalid_request)()
        # while self.client_active:
        #     request_method = raw_input('Enter your request: ')
        #     if request_method == 'connect':
        #         self.connect_server()
        #     elif request_method == 'quit':
        #         self.quit()
        #     elif request_method == 'add':
        #         self.add_rfc()
        #     elif request_method == 'query':
        #         self.query_active()
        #     elif request_method == 'lookup':
        #         self.lookup_rfc()
        #     elif request_method == 'list':
        #         self.list_all()
        #     elif request_method == 'download':
        #         self.download()
        #     else:
        #         self.invalid_request()

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
            l1 = 'ADD RFC %s P2P-CI/1.0\n' % (rfc_num)
            l2 = 'Host: %s\n' % (socket.gethostname())
            l3 = 'Port: %s\n' % (self.UPLOAD_PORT_NUM)
            l4 = 'Title: %s\n' % (rfc_title)
            data = l1 + l2 + l3 + l4
            self.serverSocket.sendall(data)
            # receive response
            recv_msg = self.serverSocket.recv(1024)
            print recv_msg
        else:
            print 'please connect first'
    
    def query_active(self):
        if self.serverSocket:
            data = 'QUERY P2P-CI/1.0\n'
            self.serverSocket.sendall(data)
            recv_data = pickle.loads(self.serverSocket.recv(1024))
            print recv_data
        else:
            print 'please connect first'

    def list_all(self):
        if self.serverSocket:
            l1 = 'LIST ALL P2P-CI/1.0\n'
            l2 = 'Host: %s\n' % (socket.gethostname())
            l3 = 'Port: %s\n' % (self.UPLOAD_PORT_NUM)
            data = l1 + l2 + l3
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
            l1 = 'LOOKUP RFC %s P2P-CI/1.0\n' % (rfc_num)
            l2 = 'Host: %s\n' % (socket.gethostname())
            l3 = 'Port: %s\n' % (self.UPLOAD_PORT_NUM)
            l4 = 'Title: %s\n' % (rfc_title)
            data = l1 + l2 + l3 + l4
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
            l1 = 'GET RFC %s P2P-CI/1.0\n' % (rfc_num)
            l2 = 'Host: %s\n' % (host_name)
            l3 = 'OS: %s\n' % (os_info)
            data = l1 + l2 + l3
            self.downloadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.downloadSocket.connect((host_name, int(peer_upload_port)))
            except BaseException, exc:
                print "Caught exception: %s" % exc
                return
            #send download request
            self.downloadSocket.sendall(data)
            print 'requesting...'
            #get the header
            recv_data_header = self.downloadSocket.recv(1024)
            print recv_data_header
            response = recv_data_header.split('\n')[0]
            if response == 'P2P-CI/1.0 200 OK':
                #get totel length
                total_length = int(recv_data_header.split('\n')[4].split(' ')[1])
                current_length = 0
                #create a file to store data
                rfc_file = open(rfc_path, 'w')
                print 'creating file...'
                recv_content = self.downloadSocket.recv(1024)
                while recv_content:
                    current_length += len(recv_content)
                    rfc_file.write(recv_content)
                    print 'still downloading'
                    time.sleep(0.3)
                    recv_content = self.downloadSocket.recv(1024)
                rfc_file.close()
                if current_length >= total_length:
                    print 'Download successful, data length is %s'%(current_length)
                else:
                    print 'data lost, please redownload'               
        else:
            print 'please connect first'

    def quit(self):
        if self.serverSocket:
            #stop listen,quit upload server
            self.client_active = False
            time.sleep(0.5)
            print 'upload server terminated'
            #quit from server
            data = 'QUIT P2P-CI/1.0\n'
            self.serverSocket.sendall(data)
            recv_data = self.serverSocket.recv(1024)
            print recv_data
            self.serverSocket.close()
            print 'close connection with server successfully'
            print 'Exit Successfully'
            #todo need a flag to close connection?
        else:
            self.client_active = False
            print 'Exit Successfully'
            
    def invalid_request(self):
        print 'Error. Invalid Command!'

    def waitUploadConnection(self):
        self.uploadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.uploadSocket.bind((self.UPLOAD_HOSTNAME, self.UPLOAD_PORT_NUM))
        self.uploadSocket.listen(5)
        print 'upload server is established, warting for connecting peers\n'
        #open a new thread for one peer connection
        while self.client_active:
            connection, address = self.uploadSocket.accept()
            upload_connection_thread = threading.Thread(target=self.buildConnection, args=(connection, address))
            upload_connection_thread.start()
        #join all upload connection threads and close connection
        print 'closing connections...\n'
        upload_connection_thread.join()
        self.uploadSocket.close()
        print 'upload server has been closed'

    def buildConnection(self, connection, address):
        #waiting for data from peer
        data = connection.recv(1024)
        if data == 'QUIT P2P-CI/1.0\n':
            connection.close()
        else:
            #upload logic
            print '\nDownload request:'
            print data,
            print 'From', address
            _command = data.split('\n')[0].split(' ')[0]
            _rfc_num = data.split('\n')[0].split(' ')[2]
            _version = data.split('\n')[0].split(' ')[3]
            _rfc_path = 'rfc%s.txt' % (_rfc_num)
            if _version != 'P2P-CI/1.0':
                # bad version
                connection.sendall('P2P-CI/1.0 505 P2P-CI Version Not Supported\n')
            elif not os.path.exists(_rfc_path):
                # file not exists
                connection.sendall('P2P-CI/1.0 404 Not Found\n')
            elif _command == 'GET':
                l1 = 'P2P-CI/1.0 200 OK\n'
                l2 = 'Data: %s\n' % (time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
                l3 = 'OS: %s\n' % (platform.platform())
                l4 = 'Last-Modified: %s\n' % (time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(os.path.getmtime(_rfc_path))))
                l5 = 'Content-Length: %s\n' % (os.path.getsize(_rfc_path))
                l6 = 'Content-Type: text/plain\n'
                data = l1 + l2 + l3 + l4 + l5 + l6
                connection.sendall(data)
                print 'uploading!\n'
                time.sleep(1)
                total_length = int(os.path.getsize(_rfc_path))
                current_length = 0
                rfc_file = open(_rfc_path, 'r')
                send_data = rfc_file.read(1024)
                while send_data:
                    current_length += len(send_data)
                    connection.send(send_data)
                    time.sleep(0.3)
                    send_data = rfc_file.read(1024)

                rfc_file.close()
                if current_length >= total_length:
                    print 'finish uploading!'
                else:
                    print 'upload fail, need retransimission'
            else:
                connection.sendall('P2P-CI/1.0 400 Bad Request\n')
            connection.close()
 
if __name__ == '__main__':
    hostname = raw_input("hostname: ")
    if hostname == 'default':
        hostname = 'localhost'
    client = Client(hostname)
    client.main()
        