import socket


TCP_IP = "127.0.0.1"
TCP_PORT = 3000
BUFFER_SIZE = 4096
MESSAGE = "Hi, server!"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
while 1:
	s.send(MESSAGE)
	print "send"
# data = s.recv(BUFFER_SIZE)
s.close()
