import os
import sys
import telepot
import requests
import re
import datetime
from time import sleep
from bs4 import BeautifulSoup
from settings import token, start_msg


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    chat_id = msg['chat']['id']
    command_input = msg['text']

    if command_input == '/start':
        bot.sendMessage(chat_id, start_msg)

    try:
        date = command_input.split()[1]
        command_input = command_input.split()[0]
    except:
        now = datetime.datetime.now()
        date = now.strftime("%m-%d-%Y")

    if command_input == '/duca':
        msg = '🗓️Mensa Duca - %s\n' % date
        payload = {'mensa': 'DUCA', 'da': date, 'a': date}
        msg += getMenu(payload)

        bot.sendMessage(chat_id, msg)

    if command_input == '/tridente':
        msg = '🗓️Mensa Tridente - %s\n' % date
        payload = {'mensa': 'TRIDENTE', 'da': date, 'a': date}
        msg += getMenu(payload)

        bot.sendMessage(chat_id, msg)

    if command_input == '/allergeni':
        bot.sendMessage(chat_id,
                        'http://menu.ersurb.it/menum/Allergeni_legenda.png')

    if command_input == '/credits':
        bot.sendMessage(chat_id, "https://github.com/Radeox"
                                 "https://github.com/Fast0n")

    if command_input == '/status':
        bot.sendMessage(chat_id, "Running :)")


def getMenu(payload):
    r = requests.post("http://menu.ersurb.it/menum/menu.asp", data=payload)

    status = False
    rvp = '\n☀️Pranzo:\n'
    rvc = '_______________________________\n\n🌙Cena:\n'
    rv0 = '\n🍝Primi:\n'
    rv1 = '\n🍖Secondi:\n'
    rv2 = '\n🍟Contorno:\n'
    rv3 = '\n🍨Frutta/Dolce:\n'

    soup = BeautifulSoup(r.text, 'html.parser')

    for link in soup.find_all('a'):
        try:
            app = link.get('onclick')
            m = re.findall('(".*?")', app)

            if m[1].replace('"', '') == '40' and not status:
                status = True
            elif m[1].replace('"', '') == '10' and status:
                status = False
                rvp += rv0 + rv1 + rv2 + rv3
                rv0 = '\n🍝Primi:\n'
                rv1 = '\n🍖Secondi:\n'
                rv2 = '\n🍟Contorno:\n'
                rv3 = '\n🍨Frutta/Dolce:\n'

            if m[1].replace('"', '') == '10':
                rv0 += m[2].replace('"', '') + '\n'
            elif m[1].replace('"', '') == '20':
                rv1 += m[2].replace('"', '') + '\n'
            elif m[1].replace('"', '') == '30':
                rv2 += m[2].replace('"', '') + '\n'
            elif m[1].replace('"', '') == '40':
                rv3 += m[2].replace('"', '') + '\n'

        except:
            pass

    rvc += rv0 + rv1 + rv2 + rv3
    msg = rvp + rvc

    return msg


# Main
print("Starting UnimensaBot...")

# PID file
pid = str(os.getpid())
pidfile = "/tmp/unimensabot.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print("%s already exists, exiting!" % pidfile)
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)

# Start working
try:
    bot = telepot.Bot(token)
    bot.message_loop(handle)

    while 1:
        sleep(10)
finally:
    os.unlink(pidfile)
