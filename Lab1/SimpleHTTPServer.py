from socket import *
import http.client
import email
from io import StringIO
import mimetypes
from datetime import datetime 
import pytz
import os, time

DEFAULT_CONNECTION_TYPE = 'close'
BYTE_SIZE = 8
OK = 'HTTP/1.1 200 OK\r\n'
NOT_FOUND = 'HTTP/1.1 404 NOT FOUND\r\n\r\nFile Not Found:('
NOT_ALLOWED = 'HTTP/1.1 405 METHOD NOT ALLOWED\r\n\r\n Method Not Allowed'

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
	CONNECTION_ALIVE = False
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	try :
		serverSocket.bind(('localhost', 8888))
		serverSocket.listen(5)

		while(True):
			if (not CONNECTION_ALIVE):
				# Wait for client connections
				(clientSocket, address) = serverSocket.accept()

			# if we're connected
			requestText = clientSocket.recv(1024).decode()
			requestCopy = requestText
			print(requestText)

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
					filename = 'index1.html'
				else:
					filename = os.getcwd() + filename

				# try to open requested file
				try:
					if (filename.endswith(".jpg")):
						finImg = open(filename, 'rb')
						img = finImg.read()
						finImg.close()
						responseHeaders = getResponseHeader(filename, connection, len(img))
						response = OK + responseHeaders + '\r\n'
						clientSocket.send(response.encode(encoding="utf-8"))
						clientSocket.send(img)
						continue;

					else:
						fin = open(filename, encoding="utf-8")
						content = fin.read()
						fin.close() 
						responseHeaders = getResponseHeader(filename, connection, len(content))

						# if successful, return the page
						response = OK + responseHeaders + '\r\n' + content
						clientSocket.sendall(response.encode(encoding="utf-8"))


					# return 404 if failed to find a file
				except FileNotFoundError:
					clientSocket.sendall(NOT_FOUND.encode(encoding="utf-8"))
			else:
				clientSocket.sendall(NOT_ALLOWED.encode(encoding="utf-8"))

			if(connection == 'close'):
				clientSocket.close()
			else:
				CONNECTION_ALIVE = True

	except KeyboardInterrupt:
		print("\nShutting down...\n")

	except Exception as exc:
		print("Error:\n");
		print(exc)

	serverSocket.close()

print("Access http://localhost:8888")
createServer()
