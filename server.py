import socket
import threading
import pickle

class CentralizedServer(object):
    #initialize the CI server infomation
    def __init__(self):
        #infomation: host_name
        # well know prot number
        # list of active clients
        # list of rfcs
        self.HOST_NAME = ''
        self.PORT_NUM = 7734
        #this is a hashmap, key is address, value is a pair of{upload port, rfc dictionary}
        self.active_peer = {}
        #elements of rfcs are lists, each element is a list
        self.rfcs = {}
    
    def main(self):
        #initialize socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.HOST_NAME, self.PORT_NUM))
        #has maximum 5 connections
        self.serverSocket.listen(1)
        print 'Server is listening connections'
        while True:
            #one connection, ont thread
            connection, address = self.serverSocket.accept()
            thread = threading.Thread(target=self.buildConnect, args=(connection, address))
            thread.start()

    def buildConnect(self, connection, address):
        #when build a connection, print this line
        print 'Server just accept a client, adress is ', address
        while True:
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
                    self.active_peer[address] = [_upload_server_port, {}]
                elif request_method == 'QUIT':
                    if self.client_quit(address):
                        break
                elif request_method == 'QUERY':
                    data = pickle.dumps(self.active_peer)
                    connection.sendall(data)
                elif request_method == 'ADD':
                    self.add_rfc(data, address, connection)
                elif request_method == 'LOOKUP':
                    #find peers who has the rfc i want
                    self.client_lookup(data, connection)
                elif request_method == 'LIST':
                    self.client_list(data, connection)
                else:
                    connection.sendall('P2P-CI/1.0 400 Bad Request\n')
        #when client chooses quit, connection close
        connection.close()
                        
                    
    def client_quit(self, address):
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
        data = 'P2P-CI/1.0 200 OK\n' + 'RFC %s %s %s %s\n' % (_rfc_num, _new_rfc[0], _new_rfc[1], _new_rfc[2])
        connection.sendall(data)
    
    #client look up some specific rfc
    def client_lookup(self, data, connection):
        _rfc_num = data[0].split(' ')[2]
        if _rfc_num in self.rfcs:
            data = 'P2P-CI/1.0 200 OK\n'
            #write data of this rfc into send buffer
            for record in self.rfcs[_rfc_num]:
                data += 'RFC %s %s %s %s\n' % (_rfc_num, record[2], record[0], record[1])
        else:
            data = 'P2P-CI/1.0 404 Not Found\n'
        connection.sendall(data)
    
    def client_list(self, data, connection):
        if self.rfcs:
            data = 'P2P-CI/1.0 200 OK\n'
            for _rfc_num in self.rfcs:
                for record in self.rfcs[_rfc_num]:
                    data += 'RFC %s %s %s %s\n' % (_rfc_num, record[2], record[0], record[1])
        else:
            data = 'P2P-CI/1.0 404 Not Found\n'
        connection.sendall(data)

if __name__ == '__main__':
    server = CentralizedServer()
    server.main()  