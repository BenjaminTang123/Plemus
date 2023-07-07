#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import json
import os
import time

import random as r

class Network:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect = ('0.0.0.0', 12345)
        self.s.bind(self.connect)
        self.s.listen(50)

    def recvAll(self, connection, data_length):
        recv_length = 0
        recv_data = b''
        while data_length > recv_length:
            data = connection.recv(data_length-recv_length)
            recv_data += data
            recv_length = len(recv_data)
        return recv_data
 
    def get(self, connection):
        length = int(connection.recv(1024).decode(encoding='utf-8'))
        connection.send("ok".encode(encoding='utf-8'))
        data = self.recvAll(connection, length).decode(encoding='utf-8')
        return data
    
    def send(self, connection, information):
        connection.sendall(str(len(information)).encode(encoding='utf-8'))
        if connection.recv(2).decode(encoding='utf-8') == "ok":
            connection.sendall(information)

class Server:
    def __init__(self):
        self.minimumSupportedVersion = 0.2
        self.net = Network()

        self.musicTable = {}
        self.listenTogether = {}

        for index in os.listdir("./music"):
            with open(f"./music/{index}/info.json") as f:
                info = json.loads(f.read())
            
            self.musicTable[info["name"]] = {"index": index, "artist": info["artist"]}
        
        print(self.musicTable)

    def run(self):
        while True:
            c, addr = self.net.s.accept()
            print('Connecting with', addr, "...")

            try:
                request = json.loads(self.net.get(c))
                print(request)
            except: ...
            else:
                if request[0] == "MusicList":
                    try:
                        self.net.send(c, json.dumps(self.musicTable).encode(encoding='utf-8'))
                    except socket.error: ...
                elif request[0] == "get":
                    """
                    request:
                        0: get
                        1: #song name#
                    To be sent:
                        0: #song name#
                        1: #song author#
                        loop 1:
                        #song cover#
                        loop2:
                        3: #song content#
                    """
                    fileIndex = self.musicTable[request[1]]["index"]

                    with open(f"./music/{fileIndex}/cover.jpg", "rb") as f:
                        cover = f.read()
                    
                    with open(f"./music/{fileIndex}/music.mp3", "rb") as f:
                        content = f.read()

                    toBeSent = [
                        request[1],
                        self.musicTable[request[1]]["artist"],
                    ]

                    try:
                        self.net.send(c, json.dumps(toBeSent).encode(encoding='utf-8'))
                        if self.net.get(c) == "cover":
                            self.net.send(c, cover)
                        if self.net.get(c) == "music":
                            self.net.send(c, content)
                    except socket.error: ...
                elif request[0] == "listenTogether":
                    print(self.listenTogether)
                    if request[1] == "create":
                        for _ in range(1, 101):
                            rn = str(r.randint(1, 100))
                            if rn in self.listenTogether: 
                                if int(time.time())-self.listenTogether[rn]["time"] > 60: break
                                else: continue
                            else: break
                        else:
                            self.net.send(json.dumps({"result": False}).encode(encoding='utf-8'))
                            break
                        
                        self.listenTogether[rn] = {
                            "result": True, 
                            "song": None, 
                            "stat": "stop",
                            "time": 0,
                            "people": 1, 
                            "num": rn,
                            "usingTime": int(time.time())
                        }
                        self.net.send(c, json.dumps(self.listenTogether[rn]).encode(encoding='utf-8'))
                    elif request[1] == "join":
                        if str(request[2]) in rn:
                            if self.listenTogether[rn]["people"] <= 5:
                                self.listenTogether[rn]["people"] += 1
                                self.listenTogether[rn]["usingTime"] = int(time.time())
                                self.net.send(c, json.dumps(self.listenTogether[rn]).encode(encoding='utf-8'))
                            else:
                                self.net.send(c, json.dumps({"result": False}).encode(encoding='utf-8'))    
                        else:
                            self.net.send(c, json.dumps({"result": False}).encode(encoding='utf-8'))
                    elif request[1] == "info":
                        self.listenTogether[request[2]]["usingTime"] = int(time.time())
                        self.net.send(c, json.dumps(self.listenTogether[rn]).encode(encoding='utf-8'))
                    elif request[1] == "change":
                        _tmp = self.listenTogether[request[2]]
                        if "stat" in request[3]:
                            if _tmp["stat"] != request[3]["stat"]:
                                _tmp["stat"] = request[3]["stat"]
                        elif "song" in request[3]:
                            if _tmp["song"] != request[3]["song"]:
                                _tmp["song"] = request[3]["song"]
                        elif "time" in request[3]:
                            if abs(_tmp["time"]-request[3]["time"]) >= 3:
                                if _tmp["time"] < request[3]["time"]:
                                    _tmp["time"] = request[3]["time"]
                        
                        self.net.send(c, "okay".encode(encoding='utf-8'))
            c.close()


if __name__ == "__main__":
    serv = Server()
    serv.run()