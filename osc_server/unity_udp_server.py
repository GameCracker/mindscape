import socket
import sys

def send_only():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('localhost', 8052)
	print 'starting up on %s port %s' % server_address
	sock.bind(server_address)
	data_send = "to unity"
	while True:
		# print  '\nwaiting to receive message'
		# data, address = sock.recvfrom(4096)
		# print 'received %s bytes from %s' % (len(data), address)
		# print >>sys.stderr, data 
		print 'sending data to client...'
		send = sock.sendto(data_send, address)
		print 'sent %s bytes back to %s' % (send, address)

def recv_send():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('localhost', 8052)
	print 'starting up on %s port %s' % server_address
	sock.bind(server_address)
	data_send = "to unity"
	while True:
		print  '\nwaiting to receive message'
		data, address = sock.recvfrom(4096)
		print 'received %s bytes from %s' % (len(data), address)
		print >>sys.stderr, data
		send = sock.sendto(data_send, address)
		print 'sent %s bytes back to %s' % (send, address)

send_only()
