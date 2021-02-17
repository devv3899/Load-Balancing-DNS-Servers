import threading
from thread import *
import sys
import socket
import time

# Global variables to read command line parameters
lsPort = int(sys.argv[1])
ts1Details = (sys.argv[2], int(sys.argv[3]))
ts2Details = (sys.argv[4], int(sys.argv[5]))

print('[LS]: Running on port:', lsPort)
print('[LS]: TS1 Details:', ts1Details)
print('[LS]: TS2 Details:', ts2Details)

def printRightNow(s):
	print(s)
	sys.stdout.flush()
	
	
# Method to connect to a address and do a call using socket.
# It responds back with the server's response.
def socketCall(serverAddress, serverPort, message, timeOut):
	try:
		cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		printRightNow("[LS]: TS socket created")
	except socket.error as err:
		printRightNow('socket open error: {} \n'.format(err))
		exit()
	

	# connect to the server on local machine
	server_binding = (serverAddress, serverPort)
	cs.connect(server_binding)
	
	printRightNow('[LS]: Sending ' + message)
	cs.send(message.encode('utf-8'))
	cs.settimeout(timeOut)

	# The hostname can be of max size 200, hence taking a buffer of 300 chars
	# just to be on safe side to accomodate ip address and other status
	data_from_server=cs.recv(300)
	printRightNow("[LS]: Data received from server: {}".format(data_from_server.decode('utf-8')))

	# close the client socket
	cs.close()
	return data_from_server.decode('utf-8')
	
	
	
# My Thread Instance
# This keeps some instance fields to track the status along with
# TS connection details.
# It is responsible to serve a single client request.
class ClientHandlerThread(threading.Thread):
	
	def __init__(self, csockid, ts1, ts2):
		# Call the Thread class's init function
		threading.Thread.__init__(self)
		self._csockid = csockid
		self._done = False
		self._ts1 = ts1
		self._ts2 = ts2
	
 
	# Override the run() function of Thread class
	def run(self):
		
		# We will create 3 threads here, 
		# One will call TS1, Second will call TS2
		# and another one will wait to see if any one of TS1 or TS2
		# responds back.
		
		# socket
		c = self._csockid
		
		# data received from client 
		hostNameQuery = c.recv(300).decode('utf-8')
		
		if hostNameQuery:
			
			# Function to handle when TS was unable to respond back.
			def defaultHandler(obj):
				# first wait for 5 seconds and some extra, So that if needed
				# TS calls get timed out.
				time.sleep(5+3)
				
				# If till now, the query is not processed, then it goes into Error state.
				if not obj._done:
					obj._done = True
					c.send((hostNameQuery + ' - Error:HOST NOT FOUND').encode('utf-8'))
					c.close()
			
			# TS handler, We are passing tsDetails so that we do not have to write
			# the same code for TS1 and TS2 again.
			def tsHandler(obj, tsDetails):
				# We are doing a blocking call below, which times out in 5 seconds
				result = socketCall(tsDetails[0], tsDetails[1], hostNameQuery, 5)
				
				# If TS responds with something meaningFul, then write that on socket.
				if result and not obj._done:
					obj._done = True
					# send the response now to the client.
					c.send(result.encode('utf-8'))
					c.close()
			
			# Algo:
			# We share the same object of the current thread, to below 3 threads,
			# If anyone succeeds, then it sets the _done field of the object.
			# Using which the other one get to know that processing is done
			# And sync between threads is maintained.
			start_new_thread(tsHandler, (self, self._ts1))
			start_new_thread(tsHandler, (self, self._ts2))
			start_new_thread(defaultHandler, (self,))
	   
def main():
	global lsPort
	global ts1Details
	global ts2Details
	
	# create a socket
	try:
		ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		printRightNow("[LS]: LS Server socket created")
	except socket.error as err:
		printRightNow('[LS]: socket open error: {}\n'.format(err))
		exit()
	
	# bind it on current address and specific port.
	server_binding = ('', lsPort)
	ss.bind(server_binding)

	# Lets allow max 10 connections at a time.
	ss.listen(10)

	# an infinite loop to allow parallel client connections
	while True:
		csockid, addr = ss.accept()
		
		# Handle each client request in a new thread, so that clients do not wait.
		# Below function starts a new thread and calls the function which is provided
		# as the first argument.
		t = ClientHandlerThread(csockid, ts1Details, ts2Details)
		t.start()
	
	# Close the server socket
	ss.close()
	exit()

if __name__ == "__main__":
	main()
