import threading
from discordBot import *
from gmailBot import *

# Create each thread
threads = []
threads.append(threading.Thread(target=runDiscordBot))
threads.append(threading.Thread(target=runGmailBot))

# Start each thread
for t in threads:
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()