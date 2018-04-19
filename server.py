import socket
import threading
import pickle

class CentralizedServer(object):
    #initialize the CI server infomation
    def __init__(self, servername):
        #infomation: host_name
        # well know prot number
        # list of active clients
        # list of rfcs
        self.H_NAME = servername
        self.PORT_NUM = 7734
        #this is a hashmap, key is address, value is a pair of{upload port, rfc dictionary}
        self.active_peer = {}
        #elements of rfcs are lists, each element is a list
        self.rfcs = {}
    
    def main(self):
        #initialize socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(self.H_NAME, self.PORT)
        #has maximum 5 connections
        s.listen(5)
        print 'Server is listening connections'

        while 1:
            #one connection, ont thread
            connection, address = s.accept()
            thread = threading.Thread(target=self.buildConnect, arg=(connection, address))
            thread.start()

    def buildConnect(self, connection, address):
        #when build a connection, print this line
        print 'Server just accept a client, adress is ', address
        while 1:
            data = connection.recv(1024)
            '''
            format of the data
            method <sp> RFC number <sp> version <cr> <lf>
            header field name <sp> value <cr> <lf>
            header field
            '''
            #find tht method
            data = data.split('\n')
            request_method = data[0].split(' ')[0]
            #check version
            version = data[0].split(' ')[-1]
            if version != 'P2P-CI/1.0':
                connection.sendall('P2P-CI/1.0 505 P2P-CI Version Not Supported\n')
            else:
                if request_method == 'CONNECT':
                    _upload_server_port = int(data[0].split(' ')[1])
                    self.active_peer[addr] = [_upload_server_port, {}]
                elif request_method == 'QUIT':
                    if self.client_quit(address):
                        break
                elif request_method == 'ADD':
                    self.add_rfc(data, address, connection)
                    
        connection.close()
                        
                    
    def client_quit(self, address)
        _quit_client = self.active_peer.pop(address)
        # _quit_client = pair {upload port, {rfc:rfc_index}}
        for _rfc in _quit_client[1]:
            rfc_index = _quit_client[1][_rfc]
            self.rfcs[_rfc].remove(rfc_index)
            if not self.rfcs[_rfc]:
                # list of this rfc is empty
                self.rfc.pop(_rfc)
        # return True  to close the socket
        return True

    #add rfc    
    def add_rfc(self, data, address, connection):
        _rfc_num = data[0].split(' ')[2]
        _new_rfc = (data[1].split(' ')[1], data[2].split(' ')[1], data[3].split(' ')[1])
        self.rfcs.setdefault(_rfc_num, [])
        self.rfcs[_rfc_num].append(_new_rfc)
        #update active_peer
        self.active_peer[address][1][_rfc_num] = _new_rfc
        #response
        data = 'P2P-CI/1.0 200 OK\n' + 'RFC %s %s %s %s\n' % (_num, _title, _host, _upload_port)
        connection.sendall(data)
    


if __name__ == '__main__':
    hotname = 'localhost'
    server = CentralizedServer(hostname)
    server.main()  