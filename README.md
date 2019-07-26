# coffeebot

Welcome to CoffeeBot, an automated coffee order retrieval application using the Slack API!

**STILL IN DEVELOPMENT**

## What it does
Run coffeebot locally to automatically collect coffee orders from your team via your Slack worksapce. A message will be sent to the channel named "coffee" in your workspace (must already exist). 
Users then have 15 minutes to invoke the slash command  **_/coffee_** followed by their order. 
After  15 minutes, a file named *orders.txt* will appear in the *coffeebot/* directory with the list of orders, ready to be sent to the coffeeshop!


## Installign CoffeeBot Into Your Workspace

## Using ngrok to run CoffeeBot locally

## Runnign CoffeeBot


*NOTE:* Workspace/Bot OAuth access tokens cannot appear in public GitHub repos
application's token will be pulled from a file 
located outside of this repo. Make sure your workspace/bot token is in a file
on your filesystem and the file path is specified. Tokens are generated
from the Slack API page for your application, for example:
www.coffeebot.slack.com/api
