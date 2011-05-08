#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        prompt.py
# Purpose:     A command line prompt that allows for prompting input and 
#              displaying output seemingly simultaneously.
#
# Author:      Andre Wiggins
#
# Created:     14/02/2011
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

import time
import msvcrt
import thread
import traceback


class EndOfLine(Exception):
    """Exception to represent when the users has finished entering a line of test"""
    pass


class CmdInterface():
    newline = '\r\n'
    controlprefix = '\xe0'
    functionprefix = '\x00'
    specialprefixes = [controlprefix, functionprefix]

    def __init__(self, prompt='>>> '):
        self.prompt = prompt
        self.charbuffer = []
        self.screen_lock = thread.allocate_lock()
        self.curpos = 0 # means cursor is at the end of the string, so after the last char.

    def write(self, s):
        s = str(s)
        self.screen_lock.acquire()
        try:
            curinput = self.prompt + ''.join(self.charbuffer)
            spaces = 0 if len(s) > len(curinput) else len(curinput) - len(s)
            output = s + ' '*spaces

            self.__write_string('\r' + output + '\n')
            self.__write_string(curinput + '\b'*abs(self.curpos))
        finally:
            self.screen_lock.release()

    def writeprompt(self):
        self.screen_lock.acquire()
        try:
            self.__write_string(self.prompt)
        finally:
            self.screen_lock.release()

    def __write_string(self, s):
        #TODO currently overwrites, do we want insert instead?
        for char in s:
            msvcrt.putch(char)

    def backspace(self, pos):
        if pos == 0:
            self.__write_string('\b \b')
            self.charbuffer.pop()
        elif abs(pos - 1) <= len(self.charbuffer):
            self.__write_string('\b' + ''.join(self.charbuffer[pos:]) + ' ')
            self.__write_string('\b' * abs(pos - 1))
            try:
                self.charbuffer.pop(pos - 1)
            except:
                traceback.print_exc()
                print 'newpos: %s' % pos - 1
                print 'len(charbuffer): %s' % len(self.charbuffer)

        return pos

    def readkey(self):
        if msvcrt.kbhit():
            char = msvcrt.getch()
            if char in CmdInterface.specialprefixes:
                char += msvcrt.getch()
            return char
        else:
            return None

    def readline(self):
        self.charbuffer = []
        while 1:
            key = self.readkey()
            if key:
                self.screen_lock.acquire()
                try:
                    self.curpos = self.handle_key_press(key, self.curpos)
                except EndOfLine:
                    break
                finally:
                    self.screen_lock.release()

        s = ''.join(self.charbuffer)
        self.charbuffer = []
        return s

    def handle_key_press(self, key, pos):
        newpos = pos
        if key[0] in CmdInterface.specialprefixes:
            newpos = self.handle_control_key(key, pos)
        elif key == '\b':
            if (pos == 0 and len(self.charbuffer) > 0) or (pos < 0):
                newpos = self.backspace(pos)
        elif key == '\r':
            self.__write_string(CmdInterface.newline)
            raise EndOfLine()
        else:
            self.__write_string(key)
            if pos < 0:
                self.charbuffer[pos] = key
                newpos = pos + 1
            else:
                self.charbuffer.append(key)
        return newpos

    def handle_control_key(self, key, pos):
        '''
        H = Up #TODO
        P = Down #TODO
        K = Left
        M = Right

        G = Home
        O = End

        I = Page Up
        Q = Page Down

        S = Delete #TODO
        R = Insert #TODO
        '''

        newpos = pos
        if key[-1] == 'K': #left
            if abs(pos - 1) <= len(self.charbuffer):
                newpos = pos - 1
                self.__write_string('\b')
        elif key[-1] == 'M': #Right
            if pos != 0:
                self.__write_string(self.charbuffer[pos])
                newpos += 1
        elif key[-1] == 'G': #Home
            self.__write_string('\r' + self.prompt)
            newpos = -len(self.charbuffer)
        elif key[-1] == 'O': #End
            self.__write_string(self.charbuffer[pos:])
            newpos = 0
        return newpos


def threaded_output(screen):
    while 1:
        time.sleep(4)
        screen.write('other: ' + str(time.time()))


def main():
    screen = CmdInterface('me: ')

    thread.start_new_thread(threaded_output, (screen,))

    while 1:
        screen.writeprompt()
        screen.readline()


if __name__ == '__main__':
    main()
