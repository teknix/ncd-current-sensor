import socket
import re

# Set NCD Current Monitor IP address 
TCP_IP = '192.168.1.102'
# Set Listening Port on Remote Current Monitor
TCP_PORT = 2101
# Set Buffer Size
BUFFER_SIZE = 1024

# Set Command to be sent to Current Monitor
# In this case query all 6 channels | https://ncd.io/communicating-to-current-monitoring-controllers/
MESSAGE = 'aa0ebc320a54926a010106000004551374'.decode('hex')
#MESSAGE = 'AA03FE7C0128'.decode('hex')

#Create Socket
s = socket.socket()
s.connect((TCP_IP, TCP_PORT))
# Send Message to Current Monitor
s.send(MESSAGE)
# Collect response data
data = s.recv(BUFFER_SIZE)
s.close()

# Convert response to hex
data = data.encode('hex')
#Split into Byte Pairs
pairs = re.findall('..?', data)

print "received data:", pairs

#
for k,v in enumerate(pairs):
    print 'key: ' + str(k) + ' val: ' + str(int(v, 16))