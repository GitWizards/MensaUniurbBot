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
from random import randint

import calendar
import re
import sqlite3
import requests
import telepot

from bs4 import BeautifulSoup
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from settings import TOKEN, PASSWORD, ADMIN
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
    except KeyError:
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

            # Try to save username and name
            username = ""
            full_name = ""

            try:
                username = msg['chat']['username']
                full_name += msg['chat']['first_name']
                full_name += ' ' + msg['chat']['last_name']
            except KeyError:
                pass

            register_user(chat_id, username, full_name)

        # Send menu for DUCA
        elif command_input == '/duca':
            register_request(chat_id, command_input)
            date1 = convert_date(date)

            # Get menu
            payload = {'mensa': 'DUCA', 'da': date1, 'a': date1}
            msg = get_menu(payload)

            # If menu exist send it
            if msg:
                bot.sendMessage(
                    chat_id, '🗓️Mensa Duca - {0}\n\n{1}'.format(date, msg[0]), parse_mode="Markdown")
                bot.sendMessage(chat_id, msg[1], parse_mode="Markdown")
                if randint(1, 5) == 3:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️\n\n" +
                        "💙 Aiutaci a sostenere le spese di @MensaUniurb\_Bot. " +
                        "[Dona 2€](https://www.gitcheese.com/donate/users/9751015/repos/90749559), oppure " +
                        "[dona 5€](https://www.gitcheese.com/donate/users/9751015/repos/90749559).", parse_mode='Markdown')
                else:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️")

            else:
                bot.sendMessage(chat_id, CLOSED_MSG.format(
                    'Duca', date, DUCA_HOURS), parse_mode="Markdown")

        # Send menu for CIBUS DUCA
        elif command_input == '/cibusduca':
            register_request(chat_id, command_input)
            date1 = convert_date(date)

            # Get menu
            payload = {'mensa': 'CIBUS', 'da': date1, 'a': date1}
            msg = get_menu(payload)

            # If menu exist send it
            if msg:
                bot.sendMessage(
                    chat_id, '🗓️Mensa Cibus Duca - {0}\n\n{1}'.format(date, msg[1].replace('🌙Cena:\n\n', '').replace('\n🍟Contorno:\n', '')), parse_mode="Markdown")
                if randint(1, 5) == 3:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️\n\n" +
                        "💙 Aiutaci a sostenere le spese di @MensaUniurb\_Bot. " +
                        "[Dona 2€](https://www.gitcheese.com/donate/users/9751015/repos/90749559), oppure " +
                        "[dona 5€](https://www.gitcheese.com/donate/users/9751015/repos/90749559).", parse_mode='Markdown')
                else:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️")

            else:
                bot.sendMessage(chat_id, CLOSED_MSG.format(
                    'Cibus Duca', date, DUCA_HOURS), parse_mode="Markdown")

        # Send menu for TRIDENTE
        elif command_input == '/tridente':
            register_request(chat_id, command_input)
            date1 = convert_date(date)

            # Get menu
            payload = {'mensa': 'TRIDENTE', 'da': date1, 'a': date1}
            msg = get_menu(payload)

            # If menu exist send it
            if msg:
                bot.sendMessage(
                    chat_id, '🗓️Mensa Tridente - {0}\n\n{1}'.format(date, msg[0]), parse_mode="Markdown")
                bot.sendMessage(chat_id, msg[1], parse_mode="Markdown")
                if randint(1, 5) == 3:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️\n\n" +
                        "💙 Aiutaci a sostenere le spese di @MensaUniurb\_Bot. " +
                        "[Dona 2€](https://www.gitcheese.com/donate/users/9751015/repos/90749559), oppure " +
                        "[dona 5€](https://www.gitcheese.com/donate/users/9751015/repos/90749559).", parse_mode='Markdown')
                else:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️")
            else:
                bot.sendMessage(chat_id, CLOSED_MSG.format(
                    'Tridente', date, TRIDENTE_HOURS), parse_mode="Markdown")

        # Send menu for CIBUS TRIDENTE
        elif command_input == '/cibustridente':
            register_request(chat_id, command_input)
            date1 = convert_date(date)

            # Get menu
            payload = {'mensa': 'CIBUSTR', 'da': date1, 'a': date1}
            msg = get_menu(payload)

            # If menu exist send it
            if msg:
                bot.sendMessage(
                    chat_id, '🗓️Mensa Cibus Tridente - {0}\n\n{1}'.format(date, msg[0].replace('\n🍟Contorno:\n', '')), parse_mode="Markdown")
                bot.sendMessage(chat_id, msg[1].replace(
                    '\n🍟Contorno:\n', ''), parse_mode="Markdown")
                if randint(1, 5) == 3:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️\n\n" +
                        "💙 Aiutaci a sostenere le spese di @MensaUniurb\_Bot. " +
                        "[Dona 2€](https://www.gitcheese.com/donate/users/9751015/repos/90749559), oppure " +
                        "[dona 5€](https://www.gitcheese.com/donate/users/9751015/repos/90749559).", parse_mode='Markdown')
                else:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️")

            else:
                bot.sendMessage(chat_id, CLOSED_MSG.format(
                    'Cibus Tridente', date, TRIDENTE_HOURS), parse_mode="Markdown")

        # Send menu for Sogesta
        elif command_input == '/sogesta':
            register_request(chat_id, command_input)
            date1 = convert_date(date)

            # Get menu
            payload = {'mensa': 'TRIDENTE', 'da': date1, 'a': date1}
            msg = get_menu(payload)

            # If menu exist send it
            if msg:
                bot.sendMessage(
                    chat_id, '🗓️Mensa Sogesta - {0}\n\n{1}'.format(date, msg[0]), parse_mode="Markdown")
                bot.sendMessage(chat_id, msg[1], parse_mode="Markdown")
                if randint(1, 5) == 3:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️\n\n" +
                        "💙 Aiutaci a sostenere le spese di @MensaUniurb\_Bot. " +
                        "[Dona 2€](https://www.gitcheese.com/donate/users/9751015/repos/90749559), oppure " +
                        "[dona 5€](https://www.gitcheese.com/donate/users/9751015/repos/90749559).", parse_mode='Markdown')
                else:
                    bot.sendMessage(
                        chat_id, "⚠️ Il menù potrebbe subire delle variazioni ⚠️")
            else:
                bot.sendMessage(chat_id, CLOSED_MSG.format(
                    'Sogesta', date, SOGESTA_HOURS), parse_mode="Markdown")

        # Send prices table
        elif command_input == '/prezzi':
            register_request(chat_id, command_input)

            with open('price_list.png', 'rb') as f:
                bot.sendPhoto(chat_id, f)
                f.close()

        # Send allergy table
        elif command_input == '/allergeni':
            register_request(chat_id, command_input)
            bot.sendPhoto(
                chat_id, 'http://menu.ersurb.it/menum/Allergeni_legenda.png')

        # Send credits
        elif command_input == '/info':
            register_request(chat_id, command_input)
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
            register_request(chat_id, command_input)
            bot.sendMessage(chat_id,
                            "🍝*Duca*\n{0}\n\n*🍖Tridente*\n{1}\n\n🍟*Sogesta\n*{2}".format(DUCA_HOURS,
                                                                                            TRIDENTE_HOURS,
                                                                                            SOGESTA_HOURS),
                            parse_mode="Markdown")

        # Send statistics about monthly use
        elif command_input == '/statistiche':
            now = datetime.now()
            year = int(now.strftime("%Y"))
            month = int(now.strftime("%m"))

            # Get graph
            fname = get_month_graph(year, month)

            with open(fname, 'rb') as f:
                # Get caption
                caption = ("Utenti totali: {0}\n"
                           "Richieste totali: {1}".format(get_total_users(), get_total_requests()))

                bot.sendPhoto(chat_id, f, caption)
                f.close()

        # Send news to all registred users - Password required - 1
        elif command_input == '/sendnews':
            USER_STATE[chat_id] = 2
            bot.sendMessage(chat_id, "*Inserisci la password*",
                            parse_mode="Markdown")

        # Send news to all registred users - Password required - 2
        elif USER_STATE[chat_id] == 2:
            if command_input.lower() == PASSWORD:
                USER_STATE[chat_id] = 3
                bot.sendMessage(chat_id,
                                "*Invia un messaggio o una foto con caption\n(Markdown non supportato con foto)*",
                                parse_mode="Markdown")
            else:
                USER_STATE[chat_id] = 0
                bot.sendMessage(chat_id, "*Password Errata*",
                                parse_mode="Markdown")

        # Send news to all registred users - Password required - 3
        elif USER_STATE[chat_id] == 3:
            USER_STATE[chat_id] = 0

            # Send to all users
            send_msg_all(command_input_original)

        # Send report to admin
        if command_input == '/report' and USER_STATE[chat_id] == 0:
            bot.sendMessage(chat_id, 'Scrivi il tuo problema e invia')
            USER_STATE[chat_id] = 1

        if command_input != '/report' and USER_STATE[chat_id] == 1:
            try:
                message = "Messaggio inviato da " + str(chat_id) + ":\n" + command_input_original
                bot.sendMessage(chat_id, 'Il messaggio "_' + command_input_original +
                                '"_ è stato inviato con successo', parse_mode="Markdown")
            except:
                message = "Messaggio inviato da " + str(chat_id) + ":\n" + command_input
                bot.sendMessage(chat_id, 'Il messaggio "_' + command_input +
                                '"_ è stato inviato con successo', parse_mode="Markdown")
            send_msg_report(message)
            USER_STATE[chat_id] = 0

    # Send news to all registred users - Password required - 3
    elif content_type == 'photo' and USER_STATE[chat_id] == 3:
        # Check if caption exist
        try:
            caption = msg['caption']
        except KeyError:
            caption = None

        msg = msg['photo'][-1]['file_id']

        USER_STATE[chat_id] = 0

        # Send to all users
        send_photo_all(msg, caption)


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
                "</']", '').replace('\\', '').replace('*', '_*_')

            # Replace HTML 'Strong' with Markdown 'bold text'
            if "<strong> " in name:
                name = name.replace('<strong> ', '*')
                bt = '*'
            else:
                bt = ''

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

            # Capitalized menus
            name = name[:1].title() + name[1:].lower()

            # Check plate type
            if idi == '10':
                rv0 += ' • ' + name + bt + '\n'
                empty = False
            elif idi == '20':
                rv1 += ' • ' + name + bt + '\n'
                empty = False
            elif idi == '30':
                rv2 += ' • ' + name + bt + '\n'
                empty = False
            elif idi == '40':
                rv3 += ' • ' + name + bt + '\n'
                empty = False
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)

    rvc += rv0 + rv1 + rv2 + rv3

    if not empty:
        return [rvp, rvc]
    else:
        return


def get_month_graph(year, month):
    """
    Return the uses graph of given month
    """
    # Ensure storage directory exists
    try:
        os.mkdir('plots')
    except FileExistsError:
        pass

    # Get current month days
    date = "{0}-{1}-".format(year, month)
    days_month = 1 + calendar.monthrange(year, month)[1]

    # Create month array
    month_counters = [0] * days_month
    radius = [1] * days_month

    for day in enumerate(month_counters[1:]):
        month_counters[day[0]] = get_use_in_day(date + str(day[0]).zfill(2))

    # Clear plot
    plt.clf()

    # Add titles
    plt.title("Statistiche d'uso {0}/{1}".format(month, year))
    plt.xlabel("Giorni del mese")
    plt.xlim([1, days_month])
    plt.ylabel("Utilizzi")

    # Set grid
    plt.grid()

    # Add plots
    plt.plot(month_counters, color='#0099ff', linewidth=2.5)
    plt.plot(month_counters, 'o', color='#5e97f6')
    plt.fill(radius, month_counters)
    plt.fill_between(range(days_month), month_counters, 0, color='#99d6ff')

    # Save it!
    fname = 'plots/{0}_{1}.png'.format(year, month)
    plt.savefig(fname)

    return fname


# Telegram related functions
def send_msg_report(msg):
    """
    Send given message to all users
    """
    for user in ADMIN:
        try:
            bot.sendMessage(user, msg, parse_mode="Markdown")
        except:
            continue

    return 1

def send_msg_all(msg):
    """
    Send given message to all users
    """
    for user in get_user_list():
        try:
            bot.sendMessage(user, msg, parse_mode="Markdown")
        except:
            continue

    return 1

def send_photo_all(photo, caption):
    """
    Send given photo to all users
    """
    users = get_user_list()

    for user in users:
        try:
            bot.sendPhoto(user, photo, caption=caption)
        except:
            continue

    return 1

# Utility functions
def convert_date(date):
    """
    Covert MM-DD-YYYY to DD-MM-YYYY
    """

    y, x, z = date.split('-')

    return "{0}-{1}-{2}".format(x, y, z)


## Query funtions ##
def register_user(chat_id, username, name):
    """
    Register given user to receive news and statistics
    """
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        query = ('INSERT INTO user(chat_id, name, username) '
                 'VALUES({0}, "{1}", "{2}")'.format(chat_id, name, username))

        cursor.execute(query)
        conn.commit()
    except sqlite3.IntegrityError:
        return 0
    finally:
        # Close connection to DB
        conn.close()

    return 1


def register_request(chat_id, request):
    """
    Store in database request made by users
    """
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get current date
    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")

    # Get ID
    query = ('SELECT id FROM action WHERE name == "%s"' % request)
    cursor.execute(query)
    action_id = cursor.fetchone()[0]

    query = ('INSERT INTO request(date, user, action) '
             'VALUES("{0}", {1}, {2})'.format(date, chat_id, action_id))

    cursor.execute(query)
    conn.commit()

    # Close connection to DB
    conn.close()
    return 1

def get_user_list():
    """
    Return the list of registred users chat_id
    """
    users = []

    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for user in cursor.execute('SELECT chat_id FROM user'):
        users.append(user[0])

    # Close connection to DB
    conn.close()
    return users


def get_total_requests():
    """
    Get total number of requests made by users
    """
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = 'SELECT count(*) FROM request'
    cursor.execute(query)
    total_requests = cursor.fetchone()[0]

    # Close connection to DB
    conn.close()
    return total_requests


def get_total_users():
    """
    Get total number of registered users
    """
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = 'SELECT count(*) FROM user'
    cursor.execute(query)
    total_users = cursor.fetchone()[0]

    # Close connection to DB
    conn.close()
    return total_users


def get_use_in_day(date):
    """
    Return the number of request in given DATE (YYYY-MM-DD)
    """
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = 'SELECT count(*) FROM request WHERE date BETWEEN "{0} 00:00:00" AND "{0} 23:59:59"'.format(
        date)
    cursor.execute(query)
    day_uses = cursor.fetchone()[0]

    # Close connection to DB
    conn.close()
    return day_uses


# Main
print("Starting MensaUniurbBot...")

# Database name
DB_NAME = 'mensauniurb.db'

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
