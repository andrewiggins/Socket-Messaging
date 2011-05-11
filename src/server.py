#! /usr/bin/python
#-------------------------------------------------------------------------------
# Name:        server.py
# Purpose:     The server that host the clients
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

#import sys
#import thread
#import subprocess
import util
import SocketServer


connections={}


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):
#     rbufsize = -1
#     wbufsize = 0
#
#     def setup(self):
#          self.connection = self.request
#          self.rfile = self.connection.makefile('rb', self.rbufsize)
#          self.wfile = self.connection.makefile('wb', self.wbufsize)
#
#     def setup(self):
#          self.nickname=""
#          while self.nickname in connections.keys() and self.nickname != "":
#               self.nickname = self.request.recv(1024).rstrip()
#          connections[self.nickname]=self
#          print self.client_address[0],":",self.nickname
#
#     def finish(self):
#          if not self.wfile.closed:
#               self.wfile.flush()
#          self.wfile.close()
#          self.rfile.close()

    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)

        self.nickname = self.connection.getpeername()[0]
        connections[self.nickname] = self
        print self.nickname, 'connected.'

    def handle(self):
        line = ''
        while line not in ('/exit','/quit', '/q'):
            peer = self.connection.getpeername()[0]
            line = self.rfile.readline().strip()
            if not line:
                continue
            print peer,'('+self.nickname+')', 'wrote:', line

            if line in ('/exit','/quit', '/q'):
                connections.pop(self.nickname)
                message = '%s exited.' %self.nickname
                print message
                self.sendall('**SERVER** '+message)
                break
            elif line[:2] == '/n' or line[:5] == '/nick':
                newnickname = line[2:].strip()
                oldnickname = self.nickname
                if connections.has_key(newnickname):
                    message = '**SERVER** "%s" is already taken.' %newnickname
                    print message
                    self.wfile.write(message+'\n')
                    continue
                else:
                    print oldnickname, 'changed nickname to',
                    connections.pop(self.nickname)
                    self.nickname = newnickname
                    connections[self.nickname] = self
                    print self.nickname
                    self.wfile.write('**SERVER** Nickname successfully changed to "%s"\n' %self.nickname)

                    message='**SERVER** "%s" is now known as "%s"' %(oldnickname, newnickname)
                    self.sendall(message)
                    continue
            elif line in ('/r', '/room'):
                room = self.Room()
                print 'Sending room to %s:\n\t%s' %(self.nickname, room)
                self.wfile.write('**SERVER** '+room+'\n')
                continue

            self.sendall(line)

    def sendall(self, data):
        for nickname in connections:
            if nickname == self.nickname:
                continue
            message = self.nickname+': '+data+'\n' if '**SERVER**' not in data else data+'\n'
            connections[nickname].wfile.write(message)

    def Room(self):
        room = 'Room: '
        for nickname in connections:
            room += nickname+', '
        return room

if __name__ == '__main__':
    # Port 0 means to select an arbitrary unused port
    host, port = raw_input('IP Address:'), input('Port:')
    if not host:
        host = util.getIP()

    server = SocketServer.ThreadingTCPServer((host, port), ThreadedTCPRequestHandler)

    print 'Waiting for clients on %s:%s...' % (host, port)
    server.serve_forever()