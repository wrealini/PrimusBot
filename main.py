import os
from flask import Flask
import threading
import discord
import json
import time

## Create talespire message global variable and cleanup loop function
talespire_message = dict()
def talespire_message_cleanup_loop():
    global talespire_message
    print("Starting talespire message cleanup loop...")
    while True:
        talespire_message = dict()
        time.sleep(5)

## Create Flask web app
app = Flask(__name__)

# http://192.168.4.34:9090/
@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"

# http://192.168.4.34:9090/talespire
@app.route("/talespire")
def talespire_output():
    global talespire_message
    return json.dumps(talespire_message)

## Create discord bot
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        msg = str(message.content).lower()
        if msg.startswith("roll "):
            msg = msg.replace("roll ","")
            global talespire_message
            talespire_message[str(message.author)] = dict(roll = msg)
            embedVar = discord.Embed(title="Roll", description=msg)
            await message.channel.send(embed=embedVar)
            await message.delete()

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

def run_discord_bot():
    print("Starting to run discord bot...")
    f = open('discordBotToken.txt')
    token = f.read()
    f.close()
    global client
    client.run(token)


if __name__ == "__main__":
    ## Create each thread
    threads = []
    threads.append(threading.Thread(target=run_discord_bot))
    threads.append(threading.Thread(target=talespire_message_cleanup_loop))
    # Start each thread
    for t in threads:
        t.start()
    # Start the Flask app
    app.run(debug=False, host="192.168.4.34", port=int(os.environ.get("PORT", 9090)))