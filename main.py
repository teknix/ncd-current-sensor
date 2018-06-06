import socket


TCP_IP = '192.168.1.102'
TCP_PORT = 2101
BUFFER_SIZE = 1024
MESSAGE = 'aa0ebc320a54926a010106000004551374'.decode('hex')
#MESSAGE = 'AA03FE7C0128'.decode('hex')
#print MESSAGE
s = socket.socket()
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
s.close()

print "received data:", data.encode('hex')
