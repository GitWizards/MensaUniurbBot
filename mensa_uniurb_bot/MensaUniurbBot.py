"""
MensaUniurb - Telegram Bot

Authors: Radeox (dawid.weglarz95@gmail.com)
         Fast0n (theplayergame97@gmail.com)
"""

import calendar
import gettext
import json
import locale
import os
import re
import sys
from datetime import datetime, timedelta
from random import randint
from time import sleep

import matplotlib
import matplotlib.pyplot as plt
import requests
import telepot
from bs4 import BeautifulSoup
from telepot.namedtuple import (InlineKeyboardButton, InlineKeyboardMarkup,
                                ReplyKeyboardMarkup, ReplyKeyboardRemove)

from db_manager import DBManager
from settings import ADMIN, DB_NAME, PASSWORD, TOKEN

matplotlib.use('Agg')


class MessageHandler:
    # Preserve all different user stages between messages
    USER_STATE = {}

    # Connector manages all interactions with the database
    dc = DBManager(DB_NAME)

    # Store the info about last message sent to all users
    GLOBAL_MSG = {}

    # Message handle funtion
    def handle(self, msg):
        """
        This function handle all incoming messages and passages through the various states
        """
        content_type, chat_type, chat_id = telepot.glance(msg)

        # Check user state
        try:
            self.USER_STATE[chat_id]
        except KeyError:
            self.USER_STATE[chat_id] = 0

        # Check what type of content was sent
        if content_type == "text":
            input_msg = msg['text']

            #! ------------ Immediate responses ------------
            if input_msg == "/start":
                self.handle_start_msg(chat_id, msg)

            # Send info about bot
            elif input_msg == "/info":
                self.send_info(chat_id)
                self.dc.log_request(input_msg)

            # Send prices table
            elif input_msg == "/prezzi":
                self.send_price_table(chat_id)
                self.dc.log_request(input_msg)

            # Send opening hours
            elif input_msg == "/orari":
                self.send_opening_hours(chat_id)
                self.dc.log_request(input_msg)

            # Send statistics about monthly use
            elif input_msg == "/statistiche":
                self.send_stats(chat_id)

            # Send allergy table
            elif input_msg == "/allergeni":
                bot.sendPhoto(chat_id,
                              "http://menu.ersurb.it/menum/Allergeni_legenda.png")
                self.dc.log_request(input_msg)

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

            #! ------------ State transition handler ------------
            #! ------------ Entry points ------------
            elif input_msg == "/duca":
                #! Skipping this choice as it was removed on website
                # self.USER_STATE[chat_id] = 1
                self.USER_STATE[chat_id] = 11

                # Send classic/cibus keyboard
                # self.send_kitchen_keyboard(chat_id)

                #! Skip here
                self.send_dish_keyboard(chat_id)
                self.dc.log_request(input_msg)

            elif input_msg == "/tridente":
                #! Skipping this choice as it was removed on website
                # self.USER_STATE[chat_id] = 2
                self.USER_STATE[chat_id] = 21

                # Send classic/cibus keyboard
                # self.send_kitchen_keyboard(chat_id)

                #! Skip here
                self.send_dish_keyboard(chat_id)
                self.dc.log_request(input_msg)

            #! Disabled for now
            # elif input_msg == "/sogesta":
            #     self.USER_STATE[chat_id] = 3

            #     # Send moment (lunch/dinner) keyboard
            #     self.send_dish_keyboard(chat_id)
            #     self.dc.log_request(input_msg)

            # User can write a report to admins
            elif input_msg == "/segnala":
                self.USER_STATE[chat_id] = 90
                bot.sendMessage(chat_id, "⚙️*Descrivi il tuo problema*🔧\n\nSe non hai impostato un username fornisci "
                                "un altro modo per contattarti altrimenti contatta direttamente @radeox o @fast0n.",
                                parse_mode="Markdown")

            # ------------ Admin commands ------------
            elif input_msg == "/sendnews":
                bot.sendMessage(
                    chat_id, "🔐 *Inserisci la password* 🔐", parse_mode="markdown")
                self.USER_STATE[chat_id] = 1000

            elif input_msg == "/editnews":
                bot.sendMessage(
                    chat_id, "🔐 *Inserisci la password* 🔐", parse_mode="markdown")
                self.USER_STATE[chat_id] = 1100

            elif input_msg == "/deletenews":
                bot.sendMessage(
                    chat_id, "🔐 *Inserisci la password* 🔐", parse_mode="markdown")
                self.USER_STATE[chat_id] = 1200

            #! ------------ Intermediate stages ------------
            # Duca or Tridente (classic)
            elif input_msg == "Classico" and \
                    (self.USER_STATE[chat_id] == 1 or self.USER_STATE[chat_id] == 2):

                # State 11 or 21
                self.USER_STATE[chat_id] = (self.USER_STATE[chat_id] * 10) + 1

                # Send moment (lunch/dinner) keyboard
                self.send_dish_keyboard(chat_id)

            # Duca or Tridente (cibus)
            elif input_msg == "Cibus" and \
                    (self.USER_STATE[chat_id] == 1 or self.USER_STATE[chat_id] == 2):

                # State 12 or 22
                self.USER_STATE[chat_id] = (self.USER_STATE[chat_id] * 10) + 2

                # Send keyboard to choose day
                self.send_week_keyboard(chat_id)

            # Duca or Tridente (classic-lunch)
            elif input_msg == "Pranzo" and \
                    (self.USER_STATE[chat_id] == 11 or self.USER_STATE[chat_id] == 21):

                # State 111 or 211
                self.USER_STATE[chat_id] = (self.USER_STATE[chat_id] * 10) + 1

                # Send keyboard to choose day
                self.send_week_keyboard(chat_id)

            # Duca or Tridente (classic-dinner)
            elif input_msg == "Cena" and \
                    (self.USER_STATE[chat_id] == 11 or self.USER_STATE[chat_id] == 21):

                # State 112 or 212
                self.USER_STATE[chat_id] = (self.USER_STATE[chat_id] * 10) + 2

                # Send keyboard to choose day
                self.send_week_keyboard(chat_id)

            # Sogesta (Lunch)
            elif input_msg == "Pranzo" and self.USER_STATE[chat_id] == 3:
                self.USER_STATE[chat_id] = 31

                # Send keyboard to choose day
                self.send_week_keyboard(chat_id)

            # Sogesta (dinner)
            elif input_msg == "Cena" and self.USER_STATE[chat_id] == 3:
                self.USER_STATE[chat_id] = 32

                # Send keyboard to choose day
                self.send_week_keyboard(chat_id)

            # ------------ Admin commands ------------
            # New global message
            elif input_msg == PASSWORD and self.USER_STATE[chat_id] == 1000:
                bot.sendMessage(
                    chat_id, "📝 *Inserisci il messaggio/foto da mandare* 📝", parse_mode="Markdown")
                self.USER_STATE[chat_id] = 1001

            # Edit global message
            elif input_msg == PASSWORD and self.USER_STATE[chat_id] == 1100:
                bot.sendMessage(
                    chat_id, "📝 *Inserisci il nuovo messaggio* 📝", parse_mode="Markdown")
                self.USER_STATE[chat_id] = 1101

            #! ------------ Final stage ------------
            # User should responde with a date in each of this stages
            elif self.USER_STATE[chat_id] in [12, 22, 31, 32, 111, 112, 211, 212]:
                self.handle_week_messages(chat_id, input_msg)

                # Return to initial state
                self.USER_STATE[chat_id] = 0

            elif self.USER_STATE[chat_id] == 90:
                # The message will be delivered to all registred admins
                self.send_report(msg)
                # Return to initial state
                self.USER_STATE[chat_id] = 0

            # Send message to all users
            elif self.USER_STATE[chat_id] == 1001:
                sent_to = self.send_msg_news(input_msg)

                # Check if there was some error
                if sent_to == 0:
                    bot.sendMessage(
                        chat_id, "💬 *Messaggio inviato a 0 utenti! Riprovo senza markdown.* 💬", parse_mode="Markdown")
                    sent_to = self.send_msg_news(input_msg, markdown=False)

                bot.sendMessage(
                    chat_id, "💬 *Messaggio inviato a {0} utenti* 💬".format(sent_to), parse_mode="Markdown")
                self.USER_STATE[chat_id] = 0

            # Edit last message sent to users
            elif self.USER_STATE[chat_id] == 1101:
                self.edit_msg_news(input_msg)
                bot.sendMessage(
                    chat_id, "💬 *Messaggio modificato* 💬", parse_mode="Markdown")
                self.USER_STATE[chat_id] = 0

            # ------------ Admin commands ------------
            # Delete last message to users
            elif input_msg == PASSWORD and self.USER_STATE[chat_id] == 1200:
                self.delete_msg_news()
                bot.sendMessage(
                    chat_id, "⚠️ *Messaggio eliminato* ⚠️", parse_mode="Markdown")
                self.USER_STATE[chat_id] = 0

            # Wrong password!
            elif input_msg != PASSWORD and self.USER_STATE[chat_id] in [1000, 1100, 1200]:
                bot.sendMessage(
                    chat_id, "❌ *Password errata! Riprova!* ❌", parse_mode="Markdown")
                self.USER_STATE[chat_id] = 0

        # Someone is trying to send a photo to all users
        elif content_type == "photo" and self.USER_STATE[chat_id]:
            # Check if caption exist
            try:
                caption = msg['caption']
            except KeyError:
                caption = None

            # Get photo ID
            photo = msg['photo'][-1]['file_id']

            sent_to = self.send_photo_all(photo, caption)

            # Check if there was some error
            if sent_to == 0:
                bot.sendMessage(
                    chat_id, "💬 *Messaggio inviato a 0 utenti! Riprovo senza markdown.* 💬", parse_mode="Markdown")
                sent_to = self.send_photo_all(photo, caption, markdown=False)

            bot.sendMessage(
                chat_id, "💬 *Messaggio inviato a {0} utenti* 💬".format(sent_to), parse_mode="Markdown")
            self.USER_STATE[chat_id] = 0

    #! ------------ End message handler ------------

    #! ------------ Telegram stuff ------------
    def handle_start_msg(self, chat_id, msg):
        """
        Handle the first message recevied from user, saving him in the db and
        sending some infos
        """
        # Save username and/or name
        try:
            try:
                username = msg['chat']['username']
            except:
                username = ""

            full_name = msg['chat']['first_name']
            full_name += ' ' + msg['chat']['last_name']
        except KeyError:
            pass

        self.dc.register_user(chat_id, username, full_name)

        # Answer to user
        #! Changed
        # bot.sendMessage(chat_id, "*Benvenuto su @MensaUniurbBot*\n"
        #                 "Qui troverai il menù offerto dal ERSU per gli studenti di Uniurb per il ristorante /duca, /tridente e /sogesta.\n\n"
        #                 "_Il bot è stato creato in modo non ufficiale nè ERSU Urbino nè UNIURB sono responsabili in alcun modo._",
        #                 parse_mode='Markdown')
        bot.sendMessage(chat_id, "*Benvenuto su @MensaUniurbBot*\n"
                        "Qui troverai il menù offerto dal ERSU per gli studenti di Uniurb per il ristorante /duca e /tridente.\n\n"
                        "_Il bot è stato creato in modo non ufficiale nè ERSU Urbino nè UNIURB sono responsabili in alcun modo._",
                        parse_mode='Markdown')

    def send_price_table(self, chat_id):
        """
        Send an image with the prices of each dish
        """
        with open("price_list_it.png", 'rb') as f:
            bot.sendPhoto(chat_id, f)
            f.close()

    def send_info(self, chat_id):
        """
        Send info about the bot and devs
        """
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🍺 " + "Offrici una birra" + " 🍺", url="https://paypal.me/Radeox/")],
        ])

        bot.sendMessage(chat_id, "Codice sorgente:" + "\n" +
                        "https://github.com/FastRadeox/MensaUniurbBot\n\n" +
                        "Sviluppato da:" + "\n" +
                        "https://github.com/Radeox\n" +
                        "https://github.com/Fast0n\n\n",
                        reply_markup=keyboard)

    def send_opening_hours(self, chat_id):
        """
        Send the opening hours for each kitchen
        """
        #! Changed
        # bot.sendMessage(chat_id, "🍝*Duca*\nAperta tutti i giorni della settimana,"
        #                 "esclusi sabato e domenica, dalle *12:00* alle *14:00* "
        #                 "e dalle *19:00* alle *21:00*.\n*Cibus* dalle *12:00* alle *14:30* e dalle *19:00* alle *21:30*.\n"
        #                 "*Posizione*: /posizioneduca\n\n"
        #                 "*🍖Tridente*\nAperta tutti i giorni della settimana dalle *12:00* alle *14:00* "
        #                 "e dalle *19:00* alle *21:00*.\n"
        #                 "*Cibus* esclusi sabato e domenica, stessi orari.\n"
        #                 "*Posizione*: /posizionetridente\n\n"
        #                 "🍟*Sogesta*\nAperta da Ottobre a Giugno, tutti i giorni della settimana "
        #                 "esclusa la domenica, dalle *12:30* alle *14:00* e dalle *19:30* "
        #                 "alle *21:00*.\n*Posizione*: /posizionesogesta",
        #                 parse_mode="Markdown")
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
        now = datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))

        # Get caption
        caption = ("Utenti totali: {0}\nRichieste totali: {1}".format(
                   self.dc.get_total_users(), self.dc.get_total_requests()))

        # Regenerate use graph
        fname = self.generate_use_graph(year, month)

        # Send use graph
        f = open(fname, 'rb')
        bot.sendPhoto(chat_id, f, caption)
        f.close()

    # Telegram related functions

    def send_msg_news(self, msg, markdown=True):
        """
        Send given message to all users
        """
        # Counter
        sent_to = 0

        for user in self.dc.get_user_list():
            try:
                # Send the message to next user
                if markdown:
                    sent_msg = bot.sendMessage(
                        user, msg, parse_mode="Markdown")
                else:
                    sent_msg = bot.sendMessage(user, msg)

                # Log it for future operations
                self.GLOBAL_MSG[user] = {}
                self.GLOBAL_MSG[user]['sent'] = sent_msg

                # Increment users counter
                sent_to += 1

                # Wait 1 sec to don't hit the API limit
                sleep(1)
            except:
                continue
        return sent_to

    def send_photo_all(self, photo, caption, markdown=True):
        """
        Send given photo to all users
        """
        # Counter
        sent_to = 0

        for user in self.dc.get_user_list():
            try:
                # Send the message to next user
                if markdown:
                    sent_msg = bot.sendPhoto(
                        user, photo, caption=caption, parse_mode="Markdown")
                else:
                    sent_msg = bot.sendPhoto(
                        user, photo, caption=caption)

                # Log it for future operations
                self.GLOBAL_MSG[user] = {}
                self.GLOBAL_MSG[user]['sent'] = sent_msg

                # Increment users counter
                sent_to += 1

                # Wait 1 sec to don't hit the API limit
                sleep(1)
            except:
                continue
        return sent_to

    def edit_msg_news(self, new_msg):
        """
        Edit last message sent to all users
        """
        for user in self.dc.get_user_list():
            try:
                old_msg = telepot.message_identifier(
                    self.GLOBAL_MSG[user]['sent'])
                bot.editMessageText(old_msg, new_msg, parse_mode="Markdown")
            except:
                continue
        return 1

    def delete_msg_news(self):
        """
        Delete last message sent to all users
        """
        for user in self.dc.get_user_list():
            try:
                msg_to_delete = telepot.message_identifier(
                    self.GLOBAL_MSG[user]['sent'])
                bot.deleteMessage(msg_to_delete)
            except:
                continue
        return 1

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
    def send_kitchen_keyboard(self, chat_id):
        """
        Send the keyboard from which you can choose between Classic and Cibus
        """
        entries = [["Classico"], ["Cibus"]]
        markup = ReplyKeyboardMarkup(keyboard=entries)
        bot.sendMessage(chat_id, "Classico o Cibus?", reply_markup=markup)

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
            12: "cibusduca",
            22: "cibustr",
            31: "sogesta",
            32: "sogesta",
            111: "duca",
            112: "duca",
            211: "tridente",
            212: "tridente"
        }

        # Convert actual user state to right meal
        meals = {
            12: None,
            22: None,
            31: "lunch",
            32: "dinner",
            111: "lunch",
            112: "dinner",
            211: "lunch",
            212: "dinner"
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
                # Randomly add some paypal spam
                if randint(1, 5) == 3:
                    msg += ("\n\n💙Aiutaci a sostenere le spese di @MensaUniurb\_Bot.\n[Dona 2 Euro]"
                            "(https://paypal.me/Radeox/2) oppure [dona 5 Euro](https://paypal.me/Radeox/5)."
                            "\nGrazie del sostegno🍻")

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

    def get_menu_msg(self, place, date=datetime.now(), meal="lunch"):
        """
        Request the menu and prepare the message to be sent
        """
        r = requests.get(
            "http://127.0.0.1:9543/{0}/{1}/{2}".format(place, date, meal))

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

    def generate_use_graph(self, year, month):
        """
        Return the uses graph of given month
        """
        # Ensure storage directory exists
        try:
            os.mkdir("plots")
        except FileExistsError:
            pass

        # Get current month days
        date = "{0}-{1}-".format(year, str(month).zfill(2))
        days_month = 1 + calendar.monthrange(year, month)[1]

        # Create month array
        month_counters = [0] * days_month
        radius = [1] * days_month

        for day in enumerate(month_counters):
            month_counters[day[0]] = self.dc.get_requests_in_day(
                date + str(day[0]).zfill(2))

        # Clear plot
        plt.clf()

        # Add titles
        plt.title(
            "Statistiche d'uso {0}/{1}".format(str(month).zfill(2), year))
        plt.xlabel("Giorni del mese")
        plt.xlim([1, days_month])
        plt.ylabel("Richieste")

        # Set grid
        plt.grid()

        # Add plots
        plt.plot(month_counters, color='#169D58', linewidth=2.5)
        plt.plot(month_counters, 'o', color='#138D4F')
        plt.fill(radius, month_counters)
        plt.fill_between(range(days_month), month_counters, 0, color='#71BA95')

        # Save it!
        fname = "plots/{0}_{1}.png".format(year, month)
        plt.savefig(fname)

        return fname


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
    f.close()

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
