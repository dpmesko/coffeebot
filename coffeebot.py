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
import json
import datetime

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
	
		date = datetime.date.today()

		header = ('COFFEE ORDER FOR ' + date.isoformat() + '\n')
		self.out_file.write(header)


	def getordermsg(self):
		return {
			'channel' : self.channel,
			'blocks' : self.ORDERFORM
		}

	def addorder(self, user, order):

		ordstr = 'User ' + user + ' wants ' + order
		self.out_file.write(ordstr)


if __name__ == '__main__':
	
	# parse OAuth token command line arg
	if len(sys.argv) != 2:
		err_str = ('ERROR: Please include the filepath to your OAuth access token '
			+ 'as the sole comamand line argument.')
		print(err_str)
		sys.exit()

	token_file = open(sys.argv[1], 'r+')
	token = token_file.readline()
	token = token.rstrip('\n')

	client = slack.WebClient(token)

	order = coffeeOrder("CL9GHRNSH")
	
	response = client.chat_postMessage(**(order.getordermsg()))

	if 'not_authed' in response:
		print('Error: OAuth access token is invalid')



