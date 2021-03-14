from socket import *
import http.client
import email
from io import StringIO
import mimetypes
from datetime import datetime 
import pytz
import os, time

DEFAULT_CONNECTION_TYPE = 'keep-alive'

def getResponseHeader(filename, connection, length):
	filetype = mimetypes.guess_type(filename)[0]
	header = "Content-Type: " + filetype + ';' + 'charset=utf-8' + "\r\n"
	GMT = pytz.timezone('GMT')
	now = datetime.now(GMT)
	header += 'Date: ' + now.strftime('%Y:%m:%d %H:%M:%S %Z %z') + '\r\n'
	header += 'Server: LilChichServer\r\n'
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)
	header += 'Last-Modified: ' + time.ctime(mtime) + '\r\n'
	header += 'Connection: ' + connection + '\r\n'
	header += 'Content-Length: ' + str(length) + '\r\n'
	return header

def contTypeAllowed(AcceptStr):
	 return ('text/plain' in AcceptStr or 'text/html' in AcceptStr or 'image/jpeg' in AcceptStr
	 	or '*/*' in AcceptStr)

def createServer():
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	try :
		serverSocket.bind(('localhost', 8888))
		serverSocket.listen(5)

		while(True):
			# Wait for client connections
			(clientSocket, address) = serverSocket.accept()

			# if we're connected
			requestText = clientSocket.recv(1024).decode()
			requestCopy = requestText

			_, headers = requestText.split('\r\n', 1)
			msg = email.message_from_file(StringIO(headers))
			headers = dict(msg.items())
			if (contTypeAllowed(headers.get('Accept'))):
				# Parse HTTP headers
				headersArray = requestCopy.split('\n')
				filename = headersArray[0].split()[1]

				if (headers.get('Connection')):
					connection = headers.get('Connection')
				else:
					connection = DEFAULT_CONNECTION_TYPE

				# main page
				if filename == '/':
					filename = 'index.html'

				# try to open requested file
				try:
					fin = open(filename)
					content = fin.read()
					responseHeaders = getResponseHeader(filename, connection, len(content.encode(encoding="utf-8")))
					fin.close() 

					# if successful, return the page
					response = 'HTTP/1.1 200 OK\r\n' + responseHeaders + '\r\n' + content

					# return 404 if failed to find a file
				except FileNotFoundError:
					response = 'HTTP/1.1 404 NOT FOUND\r\n\r\nFile Not Found:('
			else:
				response = 'HTTP/1.1 405 METHOD NOT ALLOWED\r\n\r\n Method Not Allowed'

			clientSocket.send(response.encode(encoding="utf-8"))
			clientSocket.close()

	except KeyboardInterrupt:
		print("\nShutting down...\n")

	except Exception as exc:
		print("Error:\n");
		print(exc)

	serverSocket.close()

print("Access http://localhost:8000")
createServer()
