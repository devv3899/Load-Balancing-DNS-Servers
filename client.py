import sys
import socket

# Global variables to read command line parameters
lsHostname = sys.argv[1]
lsListenPort = int(sys.argv[2])

print('[C]: lsHostname:', lsHostname)
print('[C]: lsListenPort:', lsListenPort)

def printRightNow(s):
	print(s)
	sys.stdout.flush()

# Method to connect to a address and do a call using socket.
# It responds back with the server's response.
def socketCall(serverAddress, serverPort, message):
	try:
		cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as err:
		printRightNow('[C]: socket open error: {} \n'.format(err))
		exit()
	
	# connect to the server on local machine
	server_binding = (serverAddress, serverPort)
	cs.connect(server_binding)
	
	printRightNow('[C]: Sending ' + message)
	cs.send(message.encode('utf-8'))

	# The hostname can be of max size 200, hence taking a buffer of 300 chars
	# just to be on safe side to accomodate ip address and other status
	data_from_server=cs.recv(300)
	printRightNow("[C]: Data received from server: {}".format(data_from_server.decode('utf-8')))

	# close the client socket
	cs.close()
	return data_from_server.decode('utf-8')

def main():
	inputFileName = 'PROJ2-HNS.txt'
	outputFileName = 'RESOLVED.txt'
	
	# We will read all the queries one by one from the file
	# and try to resolve them by making calls to LS program.
	f = open(inputFileName)
	w = open(outputFileName, 'w')
	for hostname in f:
		hostname = hostname.strip()
		result = socketCall(lsHostname, lsListenPort, hostname)
		w.write(result + '\n')
	f.close()
	w.close()
		

if __name__ == "__main__":
	main()














