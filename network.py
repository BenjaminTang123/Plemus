#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket

class Network:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('127.0.0.1', 12345))

    def recvAll(self, data_length):
        recv_length = 0
        recv_data = b''
        while data_length > recv_length:
            data = self.s.recv(data_length-recv_length)
            recv_data += data
            recv_length = len(recv_data)
        return recv_data
 
    def get(self, usingEncoding=True):
        length = int(self.s.recv(1024).decode(encoding='utf-8'))
        self.s.send("ok".encode(encoding='utf-8'))
        if usingEncoding == True:
            data = self.recvAll(length).decode(encoding='utf-8')
        else:
            data = self.recvAll(length)
        return data
    
    def send(self, information):
        self.s.sendall(str(len(information.encode(encoding='utf-8'))).encode(encoding='utf-8'))
        if self.s.recv(2).decode(encoding='utf-8') == "ok":
            self.s.sendall(information.encode(encoding='utf-8'))
    
    def close(self):
        self.s.close()
