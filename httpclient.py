#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Code modified by Ga Young Kim
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        # modified the regex pattern given in
        # http://stackoverflow.com/questions/9530950/parsing-hostname-and-port-from-string-or-url
        regexPattern = '(?:(http.*||ftp)://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*)/?(?P<restinfo>.*)'
        
        matches = re.search(regexPattern, url)
        host = matches.group("host")
        restinfo = matches.group("restinfo")
        if matches.group("port") == "":
            port = 80
        else:
            port = int(matches.group("port"))
        return host, port, restinfo

    def connect(self, host, port):
        try:
            #create an AF_INET, STREAM socket (TCP)
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print ('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
            sys.exit();

        #Connect to server        
        soc.connect((host , port))

        return soc

    def get_code(self, data):
        firstLine = data.split("\n")[0]
        
        firstLineinfo = firstLine.split(" ")
        
        code = int(firstLineinfo[1])
        return code

    def get_headers(self,data):
        dataInfo = data.split("\r\n")
        headString = ""
        
        for info in dataInfo:
            if(info == ""):
                break
            else:
                headString += info + "\r\n"      
        
        return headString
            
    def get_body(self, data):
        dataInfo = data.split("\r\n")
        
        start = len(dataInfo)-1
        bodyString = ""
        
        for key, info in enumerate(dataInfo):
            if(info == "" and key != len(dataInfo)-1):
                start = key
            elif (start < key):
                bodyString += info + "\n"
        return bodyString

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        host, port, urlinfo = self.get_host_port(url)
        
        conSocket = self.connect(host, port)
        
        header = ("GET /"+urlinfo+" HTTP/1.1\r\n"+
            "User-Agent: curl/7.29.0\r\n"+
            "Host: "+host+"\r\n"+
            "Accept: */*\r\n"+"\r\n")
        
        conSocket.sendall(header)
        
        data = self.recvall(conSocket)
        
        recHeader = self.get_headers(data)
        recBody = self.get_body(data)
        
        code = self.get_code(data)
        body = recHeader + recBody
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        if (args != None):
            postData = urllib.urlencode(args)
        else:
            postData = ""
        
        host, port, urlinfo = self.get_host_port(url)
        
        conSocket = self.connect(host, port)
        
        header = ("POST /"+urlinfo+" HTTP/1.1\r\n"+
                  "Host: "+host+"\r\n"+
                  "Accept: */*\r\n"+
                  "Content-Length: "+str(len(postData))+"\r\n"+
                  "Content-Type: application/x-www-form-urlencoded\r\n\r\n" + postData)
        
        conSocket.sendall(header)
                  
        data = self.recvall(conSocket)
        
        recHeader = self.get_headers(data)
        recBody = self.get_body(data)
        
        code = self.get_code(data)
        
        body = recBody
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
