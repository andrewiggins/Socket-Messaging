#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        util.py
# Purpose:     This module provides some utility functions for the Server and
#              Client
#
# Author:      Andre Wiggins
#
# Created:     18/02/2011
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
import traceback

def getIP(interface='eth0'):
    '''If running Linux:
     Pass the name of the network interface
     that you would like to get your IP from
     in the form of getIP(interface='eth0')

     On Windows, pass in nothing
    '''

    if 'linux' in sys.platform:
        import socket
        import fcntl
        import struct

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            return socket.inet_ntoa(fcntl.ioctl( s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', interface[:15])
            )[20:24])
        except IOError as error:
            if '[Errno 99]' in str(error):
                print str(error).split('[')[1].split(']')[0]+': Need new interface to pull IP from.'
            else:
                print 'Unknowm Error:'
                traceback.print_exc()
            sys.exit(1)

    elif 'win32' in sys.platform:
        import subprocess

        process = subprocess.Popen('ipconfig', shell=True, stdout=subprocess.PIPE)
        IPLine=''
        for line in process.stdout:
            if 'IP Address' in line or 'IPv4 Address' in line:
                IPLine=line
                break

        IP=IPLine.strip().split(': ')[1]
        return IP


def main():
    print getIP()

if __name__ == '__main__':
    main()
