# Socket Messaging

A client and server program that allows the sending of messages from the command
line.

# Usage

## Setup Server

1. Decide what computer will run the server, and a port number to use.
2. Find the server computer's IP Address
3. Run `python server.py` on the server computer. Enter in its IP Address and 
   the chosen port number.

## Setup Client

1. Run `python client.py`
2. Enter in the server computer's IP Address
3. Enter in the chosen port number
4. Enter in a nickname
5. Start chatting!

Each person who wants to chat should run a client, even the computer running the
server. The server does not chat, just received and broadcasts messages.

NOTE: There is a current bug where if a client sends a message while you are
typing, then their message will show up in the middle of your text. The
`prompt.py` is a start at a fix for this, but it only works on Windows, and has
it own problems as well.
