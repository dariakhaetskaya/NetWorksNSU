from socket import *
from flask import Flask, request
import http.client
import email
import pprint
from io import StringIO
import mimetypes
from datetime import datetime 
import pytz
import os, time

def getResponseHeader(filename, length):
	filetype = mimetypes.guess_type(filename)[0]
	header = "Content-type: " + filetype + "\r\n"
	GMT = pytz.timezone('GMT')
	now = datetime.now(GMT)
	header += 'Date: ' + now.strftime('%Y:%m:%d %H:%M:%S %Z %z') + '\r\n'
	header += 'Server: LilChichServer\r\n'
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)
	header += 'Last-Modified: ' + time.ctime(mtime) + '\r\n'
	header += 'Content-Length: ' + str(length) + '\r\n'
	return header

def contTypeAllowed(AcceptStr):
	 return ('text/plain' in AcceptStr or 'text/html' in AcceptStr or 'image/jpeg')

def createServer():
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	try :
		serverSocket.bind(('localhost', 8000))
		serverSocket.listen(1)

		while(True):
			# Wait for client connections
			(clientSocket, address) = serverSocket.accept()

			# if we're connected
			requestText = clientSocket.recv(1024).decode()
			print(requestText)
			requestCopy = requestText

			_, headers = requestText.split('\r\n', 1)
			msg = email.message_from_file(StringIO(headers))
			headers = dict(msg.items())
			pprint.pprint(headers, width = 160)
			if (contTypeAllowed(headers.get('Accept'))):
				# Parse HTTP headers
				headers1 = requestCopy.split('\n')
				filename = headers1[0].split()[1]

				# main page
				if filename == '/':
					filename = 'index.html'

					print(filename)

				# try to open requested file
				try:
					fin = open(filename)
					content = fin.read()
					fin.close() 
					responseHeaders = getResponseHeader(filename, len(content))
					print(responseHeaders)

					# if successful, return the page
					response = 'HTTP/1.1 200 OK\r\n' + responseHeaders + content

					# return 404 if failed to find a file
				except FileNotFoundError:
					response = 'HTTP/1.1 404 NOT FOUND\r\nFile Not Found:('
			else:
				response = 'HTTP/1.1 405 METHOD NOT ALLOWED\r\n Method Not Allowed'

			print(response)
			clientSocket.sendall(response.encode())
			clientSocket.close()

	except KeyboardInterrupt:
		print("\nShutting down...\n")

	except Exception as exc:
		print("Error:\n");
		print(exc)

	serverSocket.close()

print("Access http://localhost:8000")
createServer()
