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
	while True:
		bit = clntsock.recv(1024)
		if not bit:
			break
		response += bit

	order.lock.acquire()
	order.add('john', str(response))
	order.lock.release()
	sys.exit()

if __name__ == '__main__':
	
	# parse OAuth token command line arg
	if len(sys.argv) != 2:
		err_str = ('ERROR: Please include the filepath to your OAuth access token '
			+ 'as the sole comamand line argument.')
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

	timeout = time.time() + 60*15
	socket = socket.socket()
	socket.bind(('',2112))
	socket.listen(5)

	# TODO: timeout won't be checked until one final connection is accepted...
	# use select()...
	while timeout > time.time():
		clntsock, addr = socket.accept()
		thread = threading.Thread(target=handle_client, args=(clntsock,))
		thread.start()




