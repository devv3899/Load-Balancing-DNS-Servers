import threading
from thread import *
import sys
import socket

# Global Datastructures
port = int(sys.argv[1])
myDNSTable = dict()

print('[TS2]: Running on port:', port)

def printRightNow(s):
	print(s)
	sys.stdout.flush()
	
def loadDNSTable(fileName):
	global myDNSTable
	try:
		for line in open(fileName):
			line = line.strip()
			hostname = line.split(None, 3)[0]
			status = line.split(None, 3)[-1]
			
			if status == 'A':
				myDNSTable[hostname.lower()] = line
	except:
		printRightNow('[TS2]: Filesystem error in opening ' + fileName);
	
# thread function which handles client request
def clientHandler(c):
	global myDNSTable

	# data received from client 
	request = c.recv(300).decode('utf-8')
	printRightNow('[TS2]: Processing request: ' + request)
	
	if request:
		request = request.strip().lower()
		if request in myDNSTable:
			c.send(myDNSTable[request].encode('utf-8'))
	  
	# connection closed 
	c.close()
  

def main():
	# create a socket
	try:
		ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		printRightNow("[TS2]: TS Server socket created")
	except socket.error as err:
		printRightNow('[TS2]: socket open error: {}\n'.format(err))
		exit()
	
	# bind it on address and specific port.
	server_binding = ('', port)
	ss.bind(server_binding)

	# Lets allow max 5 connections at a time.
	ss.listen(5)

	# an infinite loop to allow parallel connections
	while True: 
		csockid, addr = ss.accept()
		
		# Handle each client request in a new thread, so that clients do not wait.
		# Below function starts a new thread and calls the function which is provided
		# as the first argument.
		start_new_thread(clientHandler, (csockid,)) 
		
	# Close the server socket
	ss.close()
	exit()


if __name__ == "__main__":
	loadDNSTable('PROJ2-DNSTS2.txt')
	main()
