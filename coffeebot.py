# # # # # # # # # # # # # # # # # # # # # # # # #
#
# 	coffeebot.py
#		The main driver file for the coffeebot application
#		Supply the filepath to your OAuth access token as a
#		command line argument when running this program with
#       python3.
#
# # # # # # # # # # # # # # # # # # # # # # # # #


import sys
import slack 
import datetime
import time
import threading
import socket


class coffeeOrder:

	ORDERFORM = [
			{	
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "Hey team! It's *coffee time*! Submit your order using */coffee* in this channel."
				}
			}
		]


	def __init__(self, channel):
		self.channel = channel
		self.out_file = open("orders.txt", 'w')
		self.lock = threading.Lock()
		
		date = datetime.date.today()

		header = ('COFFEE ORDER FOR ' + date.isoformat() + '\n')
		self.out_file.write(header)


	def getordermsg(self):
		return {
			'channel' : self.channel,
			'blocks' : self.ORDERFORM
		}

	def add(self, user, order):

		ordstr = user + ' wants ' + order + '\n'
		self.out_file.write(ordstr)



def handle_client(clntsock):
	global order
		
	response = b''
	bit = b''

	while b'\r\n\r\n' not in response:
		bit = clntsock.recv(1024)
		response += bit



	# parse user order from encoded url
	response = str(response)
	usersub = response.split('user_name=')
	user = (usersub[1].split('&'))[0]
	user_ordersub = response.split('text=')
	user_order = (user_ordersub[1].split('&'))[0]

#	for x in response:
	order.lock.acquire()
	order.add(user, user_order)
	order.lock.release()

	# TODO: Add an ACK message to the response reading back the order 
	resp_str = 'HTTP/1.1 200 OK\r\n\r\n'
	clntsock.send(resp_str.encode())
	clntsock.close()
	sys.exit()


if __name__ == '__main__':
	
	# parse OAuth token, portnum command line args
	if len(sys.argv) != 3:
		err_str = ('ERROR: Incorrect usage\n' + 
				'Usage: python3 coffebot.py <OAuth_token_file> <port_number>')
		print(err_str)
		sys.exit(1)

	# TODO: Replace with environent variable 
	token_file = open(sys.argv[1], 'r+')
	token = token_file.readline()
	token = token.rstrip('\n')

	client = slack.WebClient(token)
	
	# finds the channelID of a channel named coffee, stores it
	response = client.channels_list()
	channels = response.get("channels")

	channel_id = None	
	for x in channels:
		if x['name'] == 'coffee':
			channel_id = x['id']
			break

	if channel_id == None:
		print('ERROR: No channel named \"coffee\" found in this workspace')
		sys.exit(1)	
	

	# create order and post message
	global order
	order = coffeeOrder(channel_id)
	response = client.chat_postMessage(**(order.getordermsg()))

	# listen to port 2112 for 15 minutes for slash command payload
	#   from slack

	timeout = time.time() + 60
	socket = socket.socket()
	socket.bind(('',int(sys.argv[2])))
	socket.listen(5)

	
	# TODO: timeout won't be checked until one final connection is accepted...
	# use select()...
	while timeout > time.time():
		clntsock, addr = socket.accept()
	
		print('Incoming connection from ' + str(addr) + '\nStarting handler thread...')
		thread = threading.Thread(target=handle_client, args=(clntsock,))
		thread.start()

		



