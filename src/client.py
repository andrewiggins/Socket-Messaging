#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        client.py
# Purpose:     The client that connects the server
#
# Author:      Andre Wiggins
#
# Created:     03/2008
# Copyright:   (c) Andre Wiggins 2011
# License:
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#-------------------------------------------------------------------------------

import sys
import util
import thread
import socket


class ClientSocket():
    
    
    rbufsize = -1
    wbufsize = 0


    def __init__(self, address, nickname=''):
        if type(address) == type(()) and type(address[0]) == type('') and type(address[1]) == type(1):
            pass
        else:
            print ('Address is of incorrect type. \n' +
                  'Must be (serverHost (str), serverPort (int)).')
            sys.exit(1)

        if nickname:
            self.changeNick(nickname)
        else:
            self.changeNick(raw_input('Nickname:'))

        self.prompt_on = False
        self.address = address
        
        
    def connect(self):
        self.connection=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect(self.address)
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)
        
        self.wfile.write('/nick ' + self.nickname + '\n')


    def serve_forever(self):
        self.connect()
        
        thread.start_new_thread(self.acceptinput,())

        line = ""
        while line not in ('/exit','/quit', '/q'):
            self.prompt_on=True
            line = raw_input(self.prompt)
            self.prompt_on=False
            if line[:2] == '/n' or line[:5] == '/nick':
                self.changeNick(line[2:].strip())
            self.wfile.write(line + '\n')

        self.close()
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()


    def changeNick(self, newNick):
        self.nickname = newNick
        self.prompt = self.nickname+': '
        self.backspace = '\b' * len(self.prompt)


    def acceptinput(self):
        while 1:
            data = self.rfile.readline().strip()
            if data:
                self.writedata(data)
                if 'Nickname successfully changed to' in data:
                    self.changeNick(data.split('"')[1])


    def writedata(self, data):
        if self.prompt_on:
            output = data if len(data) >= len(self.prompt) else data + ' ' * (len(self.prompt) - len(data))
            sys.stdout.write(self.backspace + output + '\n' + self.prompt)
            sys.stdout.flush()
        else:
            print data


    def close(self):
        if not self.wfile.closed:
            self.wfile.flush()
        self.wfile.close()
        self.rfile.close()


def main():
    serverHost = raw_input('Server Host:')
    if not serverHost:
        serverHost = util.getIP()
    serverPort = input('Server Port:')
    address = (serverHost, serverPort)

    client=ClientSocket(address)
    print 'Connecting to server on %s:%s' % (serverHost, serverPort)
    client.serve_forever()


if __name__ == '__main__':
    main()