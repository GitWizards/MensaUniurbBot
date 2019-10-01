"""
MensaUniurb - Telegram Bot

Authors: Radeox (dawid.weglarz95@gmail.com)
         Fast0n (theplayergame97@gmail.com)
"""

import calendar
import json
import locale
import os
import re
import sys
from datetime import datetime, timedelta
from io import BytesIO
from random import randint
from time import sleep


import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import requests
import telepot
from telepot.namedtuple import (InlineKeyboardButton, InlineKeyboardMarkup,
                                ReplyKeyboardMarkup, ReplyKeyboardRemove)

from settings import ADMIN, TOKEN

matplotlib.use('Agg')


class MessageHandler:
    # Preserve user stages between messages
    USER_STATE = {}

    # Message handle funtion
    def handle(self, msg):
        """
        This function handle all incoming messages and passages through the various states
        """
        content_type, _, chat_id = telepot.glance(msg)

        # Check user state
        try:
            self.USER_STATE[chat_id]
        except KeyError:
            self.USER_STATE[chat_id] = 0

        # Check what type of content was sent
        if content_type == "text":
            input_msg = msg['text']

            #! ------------ Single state messages ------------
            if input_msg == "/start":
                self.handle_start_msg(chat_id, msg)

            # Send info about the bot
            elif input_msg == "/info":
                self.send_info(chat_id)

            # Send prices table
            elif input_msg == "/prezzi":
                self.send_price_table(chat_id)

            # Send opening hours
            elif input_msg == "/orari":
                self.send_opening_hours(chat_id)

            # Send statistics about monthly use
            elif input_msg == "/statistiche":
                self.send_stats(chat_id)

            # Send allergy table
            elif input_msg == "/allergeni":
                bot.sendPhoto(chat_id,
                              "http://menu.ersurb.it/menum/Allergeni_legenda.png")

            # Send location Duca
            elif input_msg == "/posizioneduca":
                bot.sendLocation(chat_id, "43.72640143124929", "12.63739407389494",
                                 reply_to_message_id=msg['message_id'])

            # Send location Tridente
            elif input_msg == "/posizionetridente":
                bot.sendLocation(chat_id, "43.720036", "12.623293",
                                 reply_to_message_id=msg['message_id'])

            # Send location Sogesta
            elif input_msg == "/posizionesogesta":
                bot.sendLocation(chat_id, "43.700293", "12.641057",
                                 reply_to_message_id=msg['message_id'])

            #! ------------ Messages with state transitions ------------

            #! ------------ Entry points ------------
            elif input_msg == "/duca":
                self.USER_STATE[chat_id] = 10

                self.send_dish_keyboard(chat_id)

            elif input_msg == "/tridente":
                self.USER_STATE[chat_id] = 20

                self.send_dish_keyboard(chat_id)

            # User can write a report to admins
            elif input_msg == "/segnala":
                self.USER_STATE[chat_id] = 100
                bot.sendMessage(chat_id, "⚙️*Descrivi il tuo problema*🔧\n\nSe non hai impostato un username fornisci "
                                "un altro modo per contattarti altrimenti contatta direttamente @radeox o @fast0n.",
                                parse_mode="Markdown")

            #! ------------ Intermediate stages ------------
            # Choose between 'lunch' and 'dinner'
            elif self.USER_STATE[chat_id] == 10 or self.USER_STATE[chat_id] == 20:
                if input_msg == "Pranzo":
                    # State 11 or 21
                    self.USER_STATE[chat_id] = self.USER_STATE[chat_id] + 1
                elif input_msg == "Cena":
                    # State 12 or 22
                    self.USER_STATE[chat_id] = self.USER_STATE[chat_id] + 2

                self.send_week_keyboard(chat_id)

            #! ------------ Final stage ------------
            # User should respond with a date in each of this stages
            elif self.USER_STATE[chat_id] in [11, 12, 21, 22]:
                self.handle_week_messages(chat_id, input_msg)

                # Return to initial state
                self.USER_STATE[chat_id] = 0

            elif self.USER_STATE[chat_id] == 90:
                # The message will be delivered to all registred admins
                self.send_report(msg)

                # Return to initial state
                self.USER_STATE[chat_id] = 0
            else:
                # State not found
                bot.sendMessage(chat_id,
                                "Non ho capito! Riprova da capo",
                                parse_mode='Markdown')

                # Return to initial state
                self.USER_STATE[chat_id] = 0

    #! ------------ End message handler ------------

    #! ------------ Telegram stuff ------------

    def handle_start_msg(self, chat_id, msg):
        """
        Answer to user's start message
        """
        # Answer to user
        bot.sendMessage(chat_id, "*Benvenuto su @MensaUniurbBot*\n"
                        "Qui troverai il menù offerto da Erdis per gli studenti di Uniurb per il ristorante /duca e /tridente.\n\n"
                        "_Il bot è stato creato in modo non ufficiale nè Erdis March nè Uniurb sono responsabili in alcun modo._",
                        parse_mode='Markdown')

    def send_price_table(self, chat_id):
        """
        Send the price table to the user
        """
        with open("assets/price_list.png", 'rb') as f:
            bot.sendPhoto(chat_id, f)

    def send_info(self, chat_id):
        """
        Send info about the bot and devs
        """
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🍺 " + "Offrici una birra" + " 🍺", url="https://paypal.me/Radeox/")],
        ])

        bot.sendMessage(chat_id, "Google Play:\nhttps://play.google.com/store/apps/details?id=com.radeox.mensa_uniurb\n\n" +
                        "Codice sorgente:\nhttps://github.com/FastRadeox/MensaUniurbBot\n\n" +
                        "Sviluppato da:\nhttps://github.com/Radeox\nhttps://github.com/Fast0n",
                        reply_markup=keyboard)

    def send_opening_hours(self, chat_id):
        """
        Send the opening hours for each kitchen
        """
        bot.sendMessage(chat_id, "🍝*Duca*\nAperta tutti i giorni della settimana, "
                        "esclusi sabato e domenica, dalle *12:00* alle *14:00* "
                        "e dalle *19:00* alle *21:00*.\n"
                        "*Posizione*: /posizioneduca\n\n"
                        "*🍖Tridente*\nAperta tutti i giorni della settimana dalle *12:00* alle *14:00* "
                        "e dalle *19:00* alle *21:00*.\n"
                        "*Posizione*: /posizionetridente\n\n",
                        parse_mode="Markdown")

    def send_stats(self, chat_id):
        """
        Send a graph with monthly usage
        """
        # Get current date and split it
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%-m")
        day = now.strftime("%-d")

        # Requests statistics from the API
        r = requests.get("http://127.0.0.1:9543/stats/")

        # Convert the data to Json
        data = json.loads(r.text)

        # Get caption
        caption = ("Richieste totali: {0}\nRichieste {1}/{2}: {3}\n"
                   "Richieste oggi: {4}".format(data['total'],
                                                month.zfill(2),
                                                year,
                                                data['requests'][year][month]['total'],
                                                data['requests'][year][month][day]))

        # Clear plot
        plt.clf()

        # Make the grid steps integers
        ax = plt.figure().gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Set grid
        plt.grid()
        month_requests = []

        month_requests.append(0)

        for day in data['requests'][year][month]:
            if day != "total":
                month_requests.append(data['requests'][year][month][day])

        # Add titles
        plt.xlabel("Giorno")
        plt.ylabel("Richieste")
        plt.xlim([1, 31])

        # Add plots
        plt.plot(month_requests, color='#DB4437', linewidth=2)
        plt.fill_between(range(len(data['requests'][year][month])),
                         month_requests, 0, color='#d8655b')

        # Store the image in memory
        output = BytesIO()
        plt.savefig(output, format='png')
        output.seek(0)

        # Send it to the user
        bot.sendPhoto(chat_id, output, caption)

    def send_report(self, msg):
        """
        Send given message to all users
        """
        # Get user message
        input_msg = msg['text']

        # Get user's username or name
        try:
            try:
                username = "@" + msg['chat']['username']
            except KeyError:
                username = msg['chat']['first_name']
                username += ' ' + msg['chat']['last_name']
        except KeyError:
            pass

        # Send input_msg to all admins
        for user in ADMIN:
            try:
                bot.sendMessage(user, "_{0}_\n\nInviato da: {1}".format(
                    input_msg, username), parse_mode="Markdown")
            except:
                continue
        return 1

    #! ------------ Keyboards ------------

    def send_dish_keyboard(self, chat_id):
        """
        Send the keyboard from which you can choose between lunch and dinner
        """
        entries = [["Pranzo"], ["Cena"]]
        markup = ReplyKeyboardMarkup(keyboard=entries)
        bot.sendMessage(chat_id, "Pranzo o Cena?", reply_markup=markup)

    def send_week_keyboard(self, chat_id):
        """
        Send the keyboard from which you can choose the day for your search
        """
        # Some working variables
        counter = 0
        entries = []
        row = []

        # Make sure the locale is set to italian
        locale.setlocale(locale.LC_TIME, "it_IT.UTF-8")

        # Get today date
        now = datetime.now()
        entries.append(["Oggi {0}".format(now.strftime("%d/%m"))])

        # Do some magic to generate the rest of keyboard keys
        for day in range(1, 8):
            date = now + timedelta(day)
            row.append(date.strftime("%A %d/%m"))
            counter += 1

            # Put 3 days every row
            if counter > 3:
                entries.append(row)
                row = []
                counter = 0

        # Append the remaning days
        entries.append(row)

        # Send week keyboard
        markup = ReplyKeyboardMarkup(keyboard=entries)
        bot.sendMessage(chat_id, "Quando?", reply_markup=markup)

    #! ------------ Data and control stuff ------------
    def handle_week_messages(self, chat_id, input_msg):
        # Convert actual user state to right place
        places = {
            11: "duca",
            12: "duca",
            21: "tridente",
            22: "tridente"
        }

        # Convert actual user state to right meal
        meals = {
            11: "lunch",
            12: "dinner",
            21: "lunch",
            22: "dinner"
        }

        # Regular expression to check if input message is in form DAY_NAME DAY/MONTH
        p = re.compile("([A-z])\w+ ([0-9])\w+\/([0-9])\w+")

        if p.match(input_msg):
            # Get current date to extract year
            now = datetime.now()

            # Exchange day and month to be in form MM-DD-YYYY as requested by API
            date = "{0}-{1}-{2}".format(input_msg.split()[1].split("/")[1],
                                        input_msg.split()[1].split("/")[0],
                                        now.strftime("%Y"))

            # Request message from API
            msg = self.get_menu_msg(places[self.USER_STATE[chat_id]],
                                    date,
                                    meals[self.USER_STATE[chat_id]])

            # Check if menu is not empty
            if msg:
                # Randomly add paypal link to donate or link to playstore app
                num = randint(1, 4)

                if num == 1:
                    msg += ("\n\n💙Aiutaci a sostenere le spese di @MensaUniurb\_Bot.\n[Dona 2 Euro]"
                            "(https://paypal.me/Radeox/2) oppure [dona 5 Euro](https://paypal.me/Radeox/5)."
                            "\nGrazie del sostegno🍻")
                if num == 2:
                    msg += (
                        "\n\n📱Siamo anche su [Google Play](https://play.google.com/store/apps/details?id=com.radeox.mensa_uniurb)!")

                # Send message
                bot.sendMessage(chat_id, msg, parse_mode="Markdown",
                                reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            else:
                # Nothing found, probably it's closed
                bot.sendMessage(chat_id, "Non ho trovato nulla🤷🏻‍♂️ Controlla gli /orari", parse_mode="Markdown",
                                reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                self.send_opening_hours(chat_id)

        else:
            # User enters something instead using the keyboard
            bot.sendMessage(chat_id, "Non ho capito. Se il problema persiste /segnala",
                            reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

    def get_menu_msg(self, place, date, meal):
        """
        Request the menu and prepare the message to be sent
        """
        r = requests.get("http://127.0.0.1:9543/{0}/{1}/{2}".format(place,
                                                                    date,
                                                                    meal))

        data = json.loads(r.text)
        msg = ""

        if data['not_empty']:
            msg += "🍝" + "Primo:" + "\n"
            for dish in data['menu']['first']:
                msg += " • {0}\n".format(dish)

            msg += "\n🍖" + "Secondo:" + "\n"
            for dish in data['menu']['second']:
                msg += " • {0}\n".format(dish)

            msg += "\n🍟" + "Contorno:" + "\n"
            for dish in data['menu']['side']:
                msg += " • {0}\n".format(dish)

            msg += "\n🍨" + "Frutta/Dolci:" + "\n"
            for dish in data['menu']['fruit']:
                msg += " • {0}\n".format(dish)

            msg += "\n⚠️ Il menù potrebbe subire delle variazioni ⚠️"

        return msg


# Main
print("Starting MensaUniurbBot...")


# PID file
PID = str(os.getpid())
PIDFILE = "/tmp/mensa_uniurb_bot.pid"

# Check if PID exist
if os.path.isfile(PIDFILE):
    print("%s already exists, exiting!" % PIDFILE)
    sys.exit()

# Create PID file
with open(PIDFILE, 'w') as f:
    f.write(PID)

# Start working
try:
    handler = MessageHandler()
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handler.handle)

    while 1:
        sleep(10)
finally:
    # Remove PID file on exit
    os.unlink(PIDFILE)
