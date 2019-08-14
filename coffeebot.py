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
import json


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
		
	
		response_msg = { "response_type" : "ephemeral",
			   			 "text" : "Your order has been received!",
	 					 "attachments" : [
						 		{ "type" : "mrkdown",
						 		  "text" : "_" + order + "_"
							    }
						 ]
		}
		
		resp_json = json.dumps(response_msg)
		
		resp_str = ''
		resp_status = ''
		resp_headers = ''

		ordstr = user + ' wants ' + order + '\n'
		self.out_file.write(ordstr)

		resp_status = 'HTTP/1.1 200 OK\r\n'
		resp_headers = 'Content-Length: ' + str(len(resp_json)) + '\r\n'
		resp_headers += 'Content-Type: application/json\r\n'
		resp_str = resp_status + resp_headers + '\r\n' + resp_json


		return resp_str


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
	user_order = user_order.replace('+', ' ')

	# add order, get response
	order.lock.acquire()
	resp_str = order.add(user, user_order)
	order.lock.release()

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
		
	# finds the channelID of general, stores it
	response = client.channels_list()
	channels = response.get("channels")

	channel_id = None	
	for x in channels:
		if x['name'] == 'general':
			channel_id = x['id']
			break

	# shouldn't happen unless general channel is removed
	if channel_id == None:
		print('ERROR: No channel named \"general\" found in this workspace')
		sys.exit(1)	
	

	# create order and post message
	global order
	order = coffeeOrder(channel_id)
	response = client.chat_postMessage(**(order.getordermsg()))


	# listen for 10 minutes
	timeout = time.time() + 60*10
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

		



