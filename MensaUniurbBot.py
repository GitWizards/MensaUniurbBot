"""
MensaUniurb - Telegram Bot

Author: Radeox (dawid.weglarz95@gmail.com)
        Fast0n (theplayergame97@gmail.com)
"""

#!/usr/bin/python3.6
import os
import sys

from time import sleep
from datetime import datetime

import re
import requests
import calendar
import telepot

from bs4 import BeautifulSoup
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

# Dev settings
from settings import TOKEN, PASSWORD
from messages import *

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Message handle funtion
def handle(msg):
    """
    This function handle all incoming messages
    """

    content_type, chat_type, chat_id = telepot.glance(msg)

    # Check user state
    try:
        USER_STATE[chat_id]
    except:
        USER_STATE[chat_id] = 0

    # Check what type of content was sent
    if content_type == 'text':
        command_input = msg['text']

        # Split command
        try:
            date = command_input.split()[1]
            command_input_original = command_input
            command_input = command_input.split()[0]
        except:
            now = datetime.now()
            date = now.strftime("%d-%m-%Y")

        # Send start message
        if command_input == '/start':
            bot.sendMessage(chat_id, START_MSG, parse_mode='Markdown')

        # Send menu for DUCA
        elif command_input == '/duca':
            print_log("{0} - {1}".format(chat_id, command_input), "log.txt")
            date1 = convert_date(date)

            # Get menu
            payload = {'mensa': 'DUCA', 'da': date1, 'a': date1}
            msg = get_menu(payload)

            # If menu exist send it
            if msg:
                bot.sendMessage(
                    chat_id, '🗓️Mensa Duca - {0}\n\n{1}'.format(date, msg[0]))
                bot.sendMessage(chat_id, msg[1])
                bot.sendMessage(
                    chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️")
            else:
                bot.sendMessage(chat_id, CLOSED_MSG.format(
                    'Duca', date, DUCA_HOURS), parse_mode="Markdown")

        # Send menu for TRIDENTE
        elif command_input == '/tridente':
            print_log("{0} - {1}".format(chat_id, command_input), "log.txt")
            date1 = convert_date(date)

            # Get menu
            payload = {'mensa': 'TRIDENTE', 'da': date1, 'a': date1}
            msg = get_menu(payload)

            # If menu exist send it
            if msg:
                bot.sendMessage(
                    chat_id, '🗓️Mensa Tridente - {0}\n\n{1}'.format(date, msg[0]))
                bot.sendMessage(chat_id, msg[1])
                bot.sendMessage(
                    chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️")
            else:
                bot.sendMessage(chat_id, CLOSED_MSG.format(
                    'Tridente', date, TRIDENTE_HOURS), parse_mode="Markdown")

        # Send menu for Sogesta
        elif command_input == '/sogesta':
            print_log("{0} - {1}".format(chat_id, command_input), "log.txt")
            date1 = convert_date(date)

            # Get menu
            payload = {'mensa': 'TRIDENTE', 'da': date1, 'a': date1}
            msg = get_menu(payload)

            # If menu exist send it
            if msg:
                bot.sendMessage(
                    chat_id, '🗓️Mensa Sogesta - {0}\n\n{1}'.format(date, msg[0]))
                bot.sendMessage(chat_id, msg[1])
                bot.sendMessage(
                    chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️")
            else:
                bot.sendMessage(chat_id, CLOSED_MSG.format(
                    'Sogesta', date, SOGESTA_HOURS), parse_mode="Markdown")

        # Send prices table
        elif command_input == '/prezzi':
            print_log("{0} - {1}".format(chat_id, command_input), "log.txt")
            f = open('price_list.png', 'rb')
            bot.sendPhoto(chat_id, f)
            f.close()

        # Send allergy table
        elif command_input == '/allergeni':
            print_log("{0} - {1}".format(chat_id, command_input), "log.txt")
            bot.sendPhoto(
                chat_id, 'http://menu.ersurb.it/menum/Allergeni_legenda.png')

        # Send credits
        elif command_input == '/info':
            print_log("{0} - {1}".format(chat_id, command_input), "log.txt")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Dona',
                                      url='https://www.gitcheese.com/donate/users/9751015/repos/90749559')],
            ])
            bot.sendMessage(chat_id, "Codice sorgente:\n"
                            "https://github.com/Radeox/MensaUniurbBot\n\n"
                            "Sviluppato da:\n"
                            "https://github.com/Radeox\n"
                            "https://github.com/Fast0n\n\n"
                            "🍺 Se sei soddisfatto offri una birra agli sviluppatori 🍺", reply_markup=keyboard)

        # Send opening hours
        elif command_input == '/orari':
            print_log("{0} - {1}".format(chat_id, command_input), "log.txt")
            bot.sendMessage(chat_id, "🍝*Duca*\n{0}\n\n*🍖Tridente*\n{1}\n\n🍟*Campus\n*{2}".format(DUCA_HOURS,
                                                                                                    TRIDENTE_HOURS,
                                                                                                    SOGESTA_HOURS), parse_mode="Markdown")

        # Send statistics about daily use
        elif command_input == '/statistiche':
            try:
                f = open("log.txt", "r")

                # Get current month days
                now = datetime.now()
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

        # Send more detailed statistics - Password required - 1
        elif command_input == '/stats':
            USER_STATE[chat_id] = 1
            bot.sendMessage(chat_id, "*Inserisci la password*",
                            parse_mode="Markdown")

        # Send more detailed statistics - Password required - 2
        elif USER_STATE[chat_id] == 1:
            if command_input == PASSWORD:
                try:
                    msg = 'Ultime 100 richieste:\n'

                    # Get number of lines
                    num_lines = sum(1 for line in open("log.txt"))

                    # Get user list
                    f = open("log.txt", "r")

                    for user in f.readlines():
                        register_user(user.split()[0])

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

            else:
                bot.sendMessage(chat_id, "*Password Errata*",
                                parse_mode="Markdown")

            # Return to initial state
            USER_STATE[chat_id] = 0

        # Send news to all registred users - Password required - 1
        elif command_input == '/sendnews':
            USER_STATE[chat_id] = 2
            bot.sendMessage(chat_id, "*Inserisci la password*",
                            parse_mode="Markdown")

        # Send news to all registred users - Password required - 2
        elif USER_STATE[chat_id] == 2:
            if command_input == PASSWORD:
                USER_STATE[chat_id] = 3
                bot.sendMessage(
                    chat_id, "*Invia un messaggio o una foto con caption\n(Markdown non supportato con foto)*", parse_mode="Markdown")
            else:
                USER_STATE[chat_id] = 0
                bot.sendMessage(chat_id, "*Password Errata*",
                                parse_mode="Markdown")

        # Send news to all registred users - Password required - 3
        elif USER_STATE[chat_id] == 3:
            f = open("log.txt", "r")

            for user in f.readlines():
                register_user(user.split()[0])

            f.close()

            # Send to all users
            send_msg_all(command_input_original)

            USER_STATE[chat_id] = 0

    # Send news to all registred users - Password required - 3
    elif content_type == 'photo' and USER_STATE[chat_id] == 3:
        f = open("log.txt", "r")

        for user in f.readlines():
            register_user(user.split()[0])

        f.close()

        # Check if caption exist
        try:
            caption = msg['caption']
        except KeyError:
            caption = None

        msg = msg['photo'][-1]['file_id']

        # Send to all users
        send_photo_all(msg, caption)

        USER_STATE[chat_id] = 0


def get_menu(payload):
    """
    Get the menu from the ERSU page
    """
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

    rvc += rv0 + rv1 + rv2 + rv3

    if not empty:
        return [rvp, rvc]
    else:
        return


def register_user(chat_id):
    """
    Register given user to receive news
    """
    insert = 1

    try:
        f = open("users.txt", "r+")

        for user in f.readlines():
            if user.replace('\n', '') == str(chat_id):
                insert = 0

    except IOError:
        f = open("users.txt", "w")

    if insert:
        f.write(str(chat_id) + '\n')

    f.close()

    return insert


# Send the msg to all registred clients
def send_msg_all(msg):
    """
    Send given message to all users
    """
    try:
        f = open("users.txt", "r")
    except IOError:
        return 0

    for user in f.readlines():
        try:
            bot.sendMessage(user, msg, parse_mode="Markdown")
        except:
            continue

    f.close()

    return 1


# Send the msg to all registred clients
def send_photo_all(photo, caption):
    """
    Send given photo to all users
    """
    try:
        f = open("users.txt", "r")
    except IOError:
        return 0

    for user in f.readlines():
        try:
            bot.sendPhoto(user, photo, caption=caption)
        except:
            continue

    f.close()

    return 1


def print_log(msg, log_file):
    """
    Write to 'log_file' adding current date
    """
    try:
        f = open(log_file, "a")

        now = datetime.now()
        date = now.strftime("%H:%M %d/%m/%Y")

        f.write("{0} {1}\n".format(msg, date))
        f.close()
    except:
        print("Error opening log file!")


def convert_date(date):
    """
    Covert MM-DD-YYYY to DD-MM-YYYY
    """

    y, x, z = date.split('-')

    return "{0}-{1}-{2}".format(x, y, z)


# Main
print("Starting MensaUniurbBot...")

# PID file
PID = str(os.getpid())
PIDFILE = "/tmp/mensauniurbbot.pid"

# Check if PID exist
if os.path.isfile(PIDFILE):
    print("%s already exists, exiting!" % PIDFILE)
    sys.exit()

# Create PID file
with open(PIDFILE, 'w') as f:
    f.write(PID)
    f.close()

# Variables
USER_STATE = {}

# Start working
try:
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handle)

    while 1:
        sleep(10)

finally:
    # Remove PID file on exit
    os.unlink(PIDFILE)
