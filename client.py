import socket
import threading
import pickle
import random
import time
import platform
import os.path
import sys

class ClientNode(object):
    def __init__(self, server_name):
        # init server info
        #SERVER_NAME = socket.gethostname()
        self.SERVER_NAME = server_name
        self.SERVER_PORT = 7734
        self.SERVER_ADDR = socket.gethostbyname(self.SERVER_NAME)
        # init upload hostname and port
        self.UPLOAD_HOSTNAME = socket.gethostname()
        self.UPLOAD_PORT = 60000 + random.randint(1,500)
        # init sockets
        self.mainSocket = None
        self.uploadSocket = None
        self.downloadSocket = None
        print 'server name: ' + self.SERVER_NAME + \
                '\nserver address: ' + self.SERVER_ADDR + \
                '\nserver port: ' + str(self.SERVER_PORT) + \
                '\nupload hostname: ' + self.UPLOAD_HOSTNAME + \
                '\nupload port: ' + str(self.UPLOAD_PORT)
        # init upload listen thread stop flag
        self.client_isStop = False

    def quitUploadListen(self):
        _tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _tempSocket.connect((self.UPLOAD_HOSTNAME, self.UPLOAD_PORT))
        data = 'QUIT\n'
        _tempSocket.sendall(data)
        time.sleep(1)
        _tempSocket.close()

    def uploadConnect(self, conn, addr):
        recv_data = conn.recv(1024)
        # this is quit command sent to the upload socket
        if recv_data[:4] == 'QUIT':
            conn.close()
        # this is actual download request
        else:
            print '\nDownload request:'
            print recv_data,
            print 'From', addr
            '''
            data format:
            GET RFC 1 P2P-CI/1.0
            HOST: MARS-XPS
            OS: LINUX-3.4.0+-X86_64-WITH-UBUNTU-14.04-TRUSTY
            '''
            data = recv_data.split('\n')
            _command = data[0].split(' ')[0]
            _rfc_num = data[0].split(' ')[2]
            _version = data[0].split(' ')[3]
            _rfc_path = 'rfc%s.txt' % (_rfc_num)
            if _version != 'P2P-CI/1.0':
                # bad version
                conn.sendall('P2P-CI/1.0 505 P2P-CI Version Not Supported\n')
            elif not os.path.exists(_rfc_path):
                # file not exists
                conn.sendall('P2P-CI/1.0 404 Not Found\n')
            elif _command == 'GET':
                # start uploading
                # format response header
                line_1 = 'P2P-CI/1.0 200 OK\n'
                line_2 = 'Data: %s\n' % (time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
                line_3 = 'OS: %s\n' % (platform.platform())
                line_4 = 'Last-Modified: %s\n' % (time.strftime("%a, %d %b %Y %H:%M:%S GMT", 
                                                        time.gmtime(os.path.getmtime(_rfc_path))))
                line_5 = 'Content-Length: %s\n' % (os.path.getsize(_rfc_path))
                line_6 = 'Content-Type: text/plain\n'
                data = line_1 + line_2 + line_3 + line_4 + line_5 + line_6
                # send response header
                conn.sendall(data)

                print '\nStart uploading...'
                time.sleep(1)

                total_length = int(os.path.getsize(_rfc_path))
                count = 0
                # open file
                f = open(_rfc_path, 'r')
                data = f.read(1024)
                while data:
                    count += 1024
                    # count downloading percentage
                    percentage = float(count) / total_length
                    if percentage > 1:
                        percentage = 100
                    else:
                        percentage = int(percentage*100)
                    print 'Uploading...%d%%' % (percentage)
                    
                    conn.send(data)
                    time.sleep(0.2)

                    data = f.read(1024)
                f.close()
                print 'Finish uploading!'
                print 'Total Length: %s' % (total_length)
            else:
                # bad request
                conn.sendall('P2P-CI/1.0 400 Bad Request\n')
            conn.close()
    
    def uploadListen(self):
        # create upload socket
        self.uploadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.uploadSocket.bind((self.UPLOAD_HOSTNAME, self.UPLOAD_PORT))
        self.uploadSocket.listen(1)
        print '\nReady to upload'
        # accept connection
        while not self.client_isStop:
            conn, addr = self.uploadSocket.accept()
            t_uploadConnect = threading.Thread(target=self.uploadConnect, args=(conn, addr))
            t_uploadConnect.start()
        # wait
        t_uploadConnect.join()
        self.uploadSocket.close()
        print '\nUpload service is closed'


    def downloadPeer(self):
        rfc_num = raw_input("Please provide RFC number you wish to download: ")
        host_name = raw_input("Please provide hostname from which you wish to download: ")
        peer_upload_port = raw_input("Please provide the upload port: ")
        os_info = platform.platform()
        rfc_path = 'rfc%s.txt' % (rfc_num)
        # prepare data
        line_1 = 'GET RFC %s P2P-CI/1.0\n' % (rfc_num)
        line_2 = 'Host: %s\n' % (host_name)
        line_3 = 'OS: %s\n' % (os_info)
        data = line_1 + line_2 + line_3
        # build connection
        self.downloadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.downloadSocket.connect((host_name, int(peer_upload_port)))
        except BaseException, exc:
            print "Caught exception: %s" % exc
            return
        self.downloadSocket.sendall(data)
        print 'Download request is sent!'
        # receive response header
        recv_data = self.downloadSocket.recv(1024)
        print recv_data
        # status is 200 OK
        if recv_data.split('\n')[0].split(' ')[1] == '200':
            total_length = int(recv_data.split('\n')[4].split(' ')[1])
            count = 0
            # open file
            f = open(rfc_path,'w')
            print 'Start downloading...'
            recv_data = self.downloadSocket.recv(1024)
            while recv_data:
                count += 1024
                # count downloading percentage
                percentage = float(count) / total_length
                if percentage > 1:
                    percentage = 100
                else:
                    percentage = int(percentage*100)
                print 'Downloading...%d%%' % (percentage)

                f.write(recv_data)
                time.sleep(0.2)

                recv_data = self.downloadSocket.recv(1024)
            f.close()
            print 'Finish downloading!'
            print 'Total Length: %s' % (total_length)
        
        self.downloadSocket.close()


    def connectServer(self):
        # create client socket
        self.mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.mainSocket.connect((self.SERVER_NAME, self.SERVER_PORT))
        except BaseException, exc:
            print "Caught exception: %s" % exc
        print 'Server is connected!'
        data = 'CONNECT %s P2P-CI/1.0\n' % (str(self.UPLOAD_PORT))
        self.mainSocket.sendall(data)

    def addSever(self):
        # provide rfc numbers that are available
        num = raw_input("Please provide RFC number: ")
        title = raw_input("RFC title: ")
        # format request data
        line_1 = 'ADD RFC %s P2P-CI/1.0\n' % (num)
        line_2 = 'Host: %s\n' % (socket.gethostname())
        line_3 = 'Port: %s\n' % (self.UPLOAD_PORT)
        line_4 = 'Title: %s\n' % (title)
        data = line_1+line_2+line_3+line_4
        self.mainSocket.sendall(data)
        # receive add response
        recv_data = self.mainSocket.recv(1024)
        print recv_data


    def queryServer(self):
        data = 'QUERY\n'
        self.mainSocket.sendall(data)
        # receive query response
        recv_data = pickle.loads(self.mainSocket.recv(1024))
        print recv_data

    def lookupServer(self):
        num = raw_input("Please provide RFC number: ")
        title = raw_input("RFC title: ")
        # format request data
        line_1 = 'LOOKUP RFC %s P2P-CI/1.0\n' % (num)
        line_2 = 'Host: %s\n' % (socket.gethostname())
        line_3 = 'Port: %s\n' % (self.UPLOAD_PORT)
        line_4 = 'Title: %s\n' % (title)
        data = line_1+line_2+line_3+line_4
        self.mainSocket.sendall(data)
        # receive lookup response
        recv_data = self.mainSocket.recv(1024)
        print recv_data

    def listServer(self):
        # format request data
        line_1 = 'LIST ALL P2P-CI/1.0\n'
        line_2 = 'Host: %s\n' % (socket.gethostname())
        line_3 = 'Port: %s\n' % (self.UPLOAD_PORT)
        data = line_1+line_2+line_3
        self.mainSocket.sendall(data)
        # receive lookup response
        recv_data = self.mainSocket.recv(1024)
        print recv_data

    def quitServer(self):
        data = 'QUIT\n'
        self.mainSocket.sendall(data)

    def testSever(self):
        cmd = raw_input("Choose test type (bad1, bad2 or version): ")
        if cmd == 'bad1':
            data = 'BAD P2P-CI/1.0\n'
        elif cmd == 'bad2':
            data = 'BAD\n'
        elif cmd == 'version':
            data = 'BAD P2P-CI/2.0\n'
        else:
            print 'Test type not available'
            return
        self.mainSocket.sendall(data)
        recv_data = self.mainSocket.recv(1024)
        print recv_data
    
    def tcpClose(self):
        self.mainSocket.close()

    def main(self):
        # create a thread to deal with upload socket
        t_uploadListen = threading.Thread(target=self.uploadListen, args=())
        t_uploadListen.start()

        time.sleep(0.5)
        while True:
            cmd = raw_input('Please enter your command: ')
            '''
            cmd has types:
            1. connect
                - data format: 'CONNECT UPLOAD_PORT\n'
            2. add
                - data format: P2S application layer protocol
            3. query
                - data format: 'QUERY\n'
            4. lookup
                - data format: P2S application layer protocol
            5. list
                - data format: P2S application layer protocol
            6. quit
                - data format: 'QUIT\n'
            7. download
                - this cmd doesn't need to be transmited to server, handled locally
            '''
            if not self.mainSocket:
                if cmd == 'connect':
                    self.connectServer()
                elif cmd == 'quit':
                    self.client_isStop = True
                    self.quitUploadListen()
                    print 'Exit Successful'
                    break
                else:
                    print 'Error. Connect the server first!'
                    continue
            else:
                if cmd == 'connect':
                    print 'You have already connected the server'
                elif cmd == 'add':
                    self.addSever()
                elif cmd == 'query':
                    self.queryServer()
                elif cmd == 'lookup':
                    self.lookupServer()
                elif cmd == 'list':
                    self.listServer()
                elif cmd == 'quit':
                    self.client_isStop = True
                    self.quitServer()
                    self.quitUploadListen()
                    self.tcpClose()
                    print 'Connection terminated'
                    print 'Exit Successful'
                    break
                elif cmd == 'download':
                    self.downloadPeer()
                elif cmd == 'test':
                    self.testSever()
                else:
                    print 'Error. Invalid Command!'


if __name__ == '__main__':
    if len(sys.argv) == 2:
        hostname = sys.argv[1]
    else:
        hostname = 'localhost'
    client = ClientNode(hostname)
    client.main()

