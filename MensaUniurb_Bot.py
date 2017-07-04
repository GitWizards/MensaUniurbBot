#!/usr/bin/python3.6
import os
import sys
import telepot
import requests
import re
import datetime
import calendar
from time import sleep
from bs4 import BeautifulSoup
from settings import token, start_msg, stats_password
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Message handle funtion
def handle(msg):
    # Init variables
    content_type = ''
    command_input = ''

    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':
        chat_id = msg['chat']['id']
        command_input = msg['text']
    elif content_type == 'photo':
        command_input = msg['caption']

    # Check which command was submitted
    if command_input == '/start':
        bot.sendMessage(chat_id, start_msg)

    try:
        news = command_input.split()[2:]
        date = command_input.split()[1]
        command_input = command_input.split()[0]
    except:
        now = datetime.datetime.now()
        date = now.strftime("%d-%m-%Y")

    if command_input == '/duca':
        printLog("{0} - {1}".format(chat_id, command_input), "log.txt")
        printLog("{0} {1} ({2})".format(msg['chat']['first_name'],
                 msg['chat']['last_name'],
                 msg['chat']['username']),
                 "user_list.txt")
        date1 = convertDate(date)

        payload = {'mensa': 'DUCA', 'da': date1, 'a': date1}
        msg = getMenu(payload)
        if msg:
            bot.sendMessage(chat_id, '🗓️Mensa Duca - {0}\n\n{1}'.format(date,
                            msg[0]))
            bot.sendMessage(chat_id, msg[1])
            bot.sendMessage(chat_id,
                            "⚠️ Il menù potrebbe subire delle variazioni ⚠️")
        else:
            bot.sendMessage(chat_id, '🗓️Menu Mensa Duca - %s\n\n'
                                     'Non disponibile.\n\n'
                                     '⚠️Attenzione⚠️\n'
                                     'Sabato e domenica il ristorante il /duca'
                                     ' non è aperto, quindi, non troverete '
                                     'nessun menù.' % date)

    if command_input == '/tridente':
        printLog("{0} - {1}".format(chat_id, command_input), "log.txt")
        printLog("{0} {1} ({2})".format(msg['chat']['first_name'],
                 msg['chat']['last_name'],
                 msg['chat']['username']),
                 "user_list.txt")
        date1 = convertDate(date)

        payload = {'mensa': 'TRIDENTE', 'da': date1, 'a': date1}
        msg = getMenu(payload)

        if msg:
            bot.sendMessage(chat_id, '🗓️Mensa Tridente - {0}\n\n{1}'.format(
                            date, msg[0]))
            bot.sendMessage(chat_id, msg[1])
            bot.sendMessage(chat_id,
                            "⚠️ Il menù potrebbe subire delle variazioni ⚠️")
        else:
            bot.sendMessage(chat_id, '🗓️Menu Mensa Tridente - %s\n\n'
                                     'Non disponibile.' % date)

    if command_input == '/prezzi':
        printLog("{0} - {1}".format(chat_id, command_input), "log.txt")
        printLog("{0} {1} ({2})".format(msg['chat']['first_name'],
                 msg['chat']['last_name'],
                 msg['chat']['username']),
                 "user_list.txt")
        f = open('price_list.png', 'rb')
        bot.sendPhoto(chat_id, f)
        f.close()

    if command_input == '/allergeni':
        printLog("{0} - {1}".format(chat_id, command_input), "log.txt")
        printLog("{0} {1} ({2})".format(msg['chat']['first_name'],
                 msg['chat']['last_name'],
                 msg['chat']['username']),
                 "user_list.txt")
        bot.sendMessage(chat_id,
                        'http://menu.ersurb.it/menum/Allergeni_legenda.png')

    if command_input == '/crediti':
        printLog("{0} - {1}".format(chat_id, command_input), "log.txt")
        printLog("{0} {1} ({2})".format(msg['chat']['first_name'],
                 msg['chat']['last_name'],
                 msg['chat']['username']),
                 "user_list.txt")
        bot.sendMessage(chat_id, "Sviluppato da:\n"
                                 "https://github.com/Radeox\n"
                                 "https://github.com/Fast0n")

    if command_input == '/dona':
        printLog("{0} - {1}".format(chat_id, command_input), "log.txt")
        printLog("{0} {1} ({2})".format(msg['chat']['first_name'],
                 msg['chat']['last_name'],
                 msg['chat']['username']),
                 "user_list.txt")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Dona',
                                  url='https://www.gitcheese.com/donate/'
                                      'users/9751015/repos/90749559')],
        ])
        bot.sendMessage(chat_id, "🍺 Se sei soddisfatto offri una birra agli"
                                 " sviluppatori 🍺\n", reply_markup=keyboard)

    if command_input == '/statistiche':
        try:
            f = open("log.txt", "r")

            # Get current month days
            now = datetime.datetime.now()
            days = calendar.monthrange(now.year, now.month)[1]
            days += 1

            # Create month array
            month_counters = []
            radius = []

            for i in range(days):
                month_counters.append(0)
                radius.append(1)

            # Read input file
            for line in f.readlines():
                date = line.split()[4]
                day, month, year = date.split('/')

                if int(year) == now.year and int(month) == now.month:
                    month_counters[int(day)] += 1

            # Clear plot
            plt.clf()

            # Add titles
            plt.title("Statistiche d'uso {0}/{1}".format(month, year))
            plt.xlabel('Giorni del mese')
            plt.xlim([1, days])
            plt.ylabel('Utilizzi')

            # Set grid
            plt.grid()

            # Add plots
            plt.plot(month_counters, color='#0099ff', linewidth=2.5)
            plt.plot(month_counters, 'o', color='#0099ff')
            plt.fill(radius, month_counters)
            x = range(days)
            plt.fill_between(x, month_counters, 0, color='#99d6ff')

            # Save
            plt.savefig('plot.png')
            f = open('plot.png', 'rb')

            # Send to user
            bot.sendPhoto(chat_id, f)

            f.close()
        except FileNotFoundError:
            pass

    if command_input == '/stats':
        # Check stats password
        if date == stats_password:
            try:
                msg = 'Ultime 100 richieste:\n'

                # Get number of lines
                num_lines = sum(1 for line in open("log.txt"))

                # Get user list
                f = open("log.txt", "r")

                for user in f.readlines():
                    registerClientID(user.split()[0])

                num_users = sum(1 for line in open("users.txt"))

                # Get last lines
                with open("log.txt", "r") as f:
                    lines = list(f)[-100:]

                for line in lines:
                    msg += line

                msg += '\nRichieste totali: {0}\n'.format(num_lines)
                msg += 'Utenti totali: {0}'.format(num_users)
                bot.sendMessage(chat_id, msg)

                f.close()
            except FileNotFoundError:
                print("Log file not found")
                pass

    if command_input == '/users':
        # Check stats password
        if date == stats_password:
            try:
                # Get last lines
                msg = 'Ultime 100 persone:\n'

                with open("user_list.txt", "r") as f:
                    lines = list(f)[-100:]

                for line in lines:
                    msg += line

                bot.sendMessage(chat_id, msg)

                f.close()
            except FileNotFoundError:
                print("Log file not found")
                pass

        else:
            bot.sendMessage(chat_id, "⚠️ Password errata! ⚠️")

    if command_input == '/sendnews':
        # Check stats password
        if date == stats_password:
            # Regenrate user list
            f = open("log.txt", "r")

            for user in f.readlines():
                registerClientID(user.split()[0])

            if content_type == 'text':
                msg = ''

                # Concat message
                for s in news:
                    s = str(s).replace('<br>', '\n')
                    msg += s + ' '

                # Send to all users
                sendMsgToAll(msg)

            elif content_type == 'photo':
                msg = msg['photo'][-1]['file_id']

                # Send to all users
                sendPhotoToAll(msg)

        else:
            bot.sendMessage(chat_id, "⚠️ Password errata! ⚠️")


# Get the menu from the ERSU page
def getMenu(payload):
    r = requests.post("http://menu.ersurb.it/menum/menu.asp", data=payload)

    empty = True
    status = False
    rvp = '☀️Pranzo:\n'
    rvc = '🌙Cena:\n'
    rv0 = '\n🍝Primi:\n'
    rv1 = '\n🍖Secondi:\n'
    rv2 = '\n🍟Contorno:\n'
    rv3 = '\n🍨Frutta/Dolce:\n'

    soup = BeautifulSoup(r.text, 'html.parser')

    for link in soup.find_all('a')[1:]:
        try:
            # Get ID
            app = link.get('onclick')
            idi = re.findall('(".*?")', app)[1].replace('"', '')

            # Get name
            name = str(re.findall('(">.*?<\/)', str(link)))

            # Remove useless chars
            name = name.replace('''['">''', '').replace(
                                "</']", '').replace('\\', '')

            # Check if launch/dinner
            if idi == '40' and not status:
                status = True
            elif idi == '10' and status:
                status = False
                rvp += rv0 + rv1 + rv2 + rv3
                rv0 = '\n🍝Primi:\n'
                rv1 = '\n🍖Secondi:\n'
                rv2 = '\n🍟Contorno:\n'
                rv3 = '\n🍨Frutta/Dolce:\n'

            # Check plate type
            if idi == '10':
                rv0 += ' • ' + name + '\n'
                empty = False
            elif idi == '20':
                rv1 += ' • ' + name + '\n'
                empty = False
            elif idi == '30':
                rv2 += ' • ' + name + '\n'
                empty = False
            elif idi == '40':
                rv3 += ' • ' + name + '\n'
                empty = False
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)
            pass

    rvc += rv0 + rv1 + rv2 + rv3

    if not empty:
        return [rvp, rvc]
    else:
        return


# Register the client
def registerClientID(chat_id):
    try:
        f = open("users.txt", "r+")
    except IOError:
        f = open("users.txt", "w")
        f.write(str(chat_id) + '\n')
        f.close()
        return True

    insert = 1

    for client in f:
        if client.replace('\n', '') == str(chat_id):
            insert = 0

    if insert:
        f.write(str(chat_id) + '\n')
        f.close()
        return True

    f.close()
    return False


# Send the msg to all registred clients
def sendMsgToAll(msg):
    try:
        f = open("users.txt", "r")
    except IOError:
        return

    for client in f.readlines():
        try:
            bot.sendMessage(client, msg)
        except:
            continue

    f.close()


# Send the msg to all registred clients
def sendPhotoToAll(photo):
    try:
        f = open("users.txt", "r")
    except IOError:
        return

    for client in f.readlines():
        try:
            bot.sendPhoto(client, photo)
        except:
            continue

    f.close()


# Save some statistics on usage
def printLog(msg, log_file):
    try:
        f = open(log_file, "a")

        now = datetime.datetime.now()
        date = now.strftime("%H:%M %d/%m/%Y")

        f.write("{0} {1}\n".format(msg, date))
        f.close()
    except:
        print("Error opening log file!")


# Simple function covert MM-DD-YYYY to DD-MM-YYYY
def convertDate(date):
    x, y, z = date.split('-')
    rv = y + '-' + x + '-' + z

    return rv


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
    # Remove PID file on exit
    os.unlink(pidfile)
