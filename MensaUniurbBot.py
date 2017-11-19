"""
MensaUniurb - Telegram Bot

Author: Radeox (dawid.weglarz95@gmail.com)
        Fast0n (theplayergame97@gmail.com)
"""

#!/usr/bin/python3.6
import os
import sys
import gettext

from time import sleep
from datetime import datetime, timedelta
from random import randint

import locale
import calendar
import re
import sqlite3
import requests
import telepot

from bs4 import BeautifulSoup
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

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

    # Function to change language
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get notification , language
    query = (
        'SELECT notification, language FROM user WHERE chat_id == "%s"' % chat_id)
    cursor.execute(query)
    notification, language = cursor.fetchall()[0]

    if language == "it":
        LANG = ['it_IT.ISO8859-15']
    elif language == "en":
        LANG = ['en_US']

    TEMP[chat_id] = {}
    TEMP[chat_id]['lang'] = LANG
    t = gettext.translation('messages', 'locales', languages=LANG)
    _ = t.gettext

    # Close connection to DB
    conn.close()

    # Check user state
    try:
        USER_STATE[chat_id]
    except KeyError:
        USER_STATE[chat_id] = 0

    # Check what type of content was sent
    if content_type == 'text':
        command_input = msg['text']

        # Send start message
        if command_input == '/start':
            bot.sendMessage(chat_id, START_MSG, parse_mode='Markdown')

            # Try to save username, name and language
            username = ""
            full_name = ""
            language = ""

            try:
                username = msg['chat']['username']
                language = msg['from']['language_code']
                full_name += msg['chat']['first_name']
                full_name += ' ' + msg['chat']['last_name']

            except KeyError:
                pass
            register_user(chat_id, username, full_name, language)

        # Get menu
        elif command_input in ['/duca', '/tridente', '/sogesta', '/cibusduca', '/cibustridente']:
            register_request(chat_id, command_input)
            USER_STATE[chat_id] = 1

            # Open connection to DB
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Get notification
            query = (
                'SELECT username, name FROM user WHERE chat_id == "%s"' % chat_id)
            cursor.execute(query)
            username, name = cursor.fetchall()[0]

            if username == "" or name == "" or username == None or name == None:
                # Try to update username and name
                username = ""
                full_name = ""

                try:
                    username = msg['chat']['username']
                    full_name += msg['chat']['first_name']
                    full_name += ' ' + msg['chat']['last_name']

                except KeyError:
                    pass
                update_user(chat_id, username, full_name)

            # Close connection to DB
            conn.close()

            # Some work vars
            counter = 0
            entries = []
            p_entries = []

            ck = {
                '/duca': 'Duca',
                '/tridente': 'Tridente',
                '/sogesta': 'Sogesta',
                '/cibustridente': 'CibusTr',
                '/cibusduca': 'Cibus'
            }

            # Init a dict to save temporaries for this action
            TEMP[chat_id]['kitchen'] = ck[command_input]
            
            # Set locale to get day names
            LANG = TEMP[chat_id]['lang'][0].split(".")
            locale.setlocale(locale.LC_TIME, LANG[0])

            # Get current day
            now = datetime.now()
            entries.append([_('today')])

            for day in range(1, 8):
                date = now + timedelta(day)
                p_entries.append(date.strftime("%A %d/%m"))
                counter += 1

                if counter > 3:
                    entries.append(p_entries)
                    p_entries = []
                    counter = 0
            entries.append(p_entries)

            # Make week keyboard
            markup = ReplyKeyboardMarkup(keyboard=entries)
            bot.sendMessage(chat_id, _('date'), reply_markup=markup)

        elif USER_STATE[chat_id] == 1:
            USER_STATE[chat_id] = 2

            now = datetime.now()

            # If current day
            if command_input == _('today'):
                date = now.strftime('%m-%d-%Y')
            else:
                d, m = command_input.split()[1].split('/')
                y = now.strftime('%Y')
                date = ("{0}-{1}-{2}".format(m, d, y))

            TEMP[chat_id]['date'] = date

            # Cibus can't choose
            if TEMP[chat_id]['kitchen'] == 'Cibus' or TEMP[chat_id]['kitchen'] == 'CibusTr':
                USER_STATE[chat_id] = 0

                # Finally send menu
                msg = get_menu_message(
                    TEMP[chat_id]['kitchen'], TEMP[chat_id]['date'], 'Cena')
                bot.sendMessage(chat_id, msg, parse_mode="Markdown",
                                reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            else:
                # Users choose lunch or dinner
                markup = ReplyKeyboardMarkup(
                    keyboard=[[_('lunch')], [_('dinner')]])
                bot.sendMessage(chat_id, _('lunch') + _('or') +
                                _('dinner') + "?", reply_markup=markup)

        elif USER_STATE[chat_id] == 2:
            USER_STATE[chat_id] = 0

            # Finally send menu
            msg = get_menu_message(
                TEMP[chat_id]['kitchen'], TEMP[chat_id]['date'], command_input)
            bot.sendMessage(chat_id, msg, parse_mode="Markdown",
                            reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Send prices table
        elif command_input == '/prezzi':
            register_request(chat_id, command_input)

            with open('price_list.png', 'rb') as f:
                bot.sendPhoto(chat_id, f, reply_markup=ReplyKeyboardRemove(
                    remove_keyboard=True))
                f.close()

        # Send allergy table
        elif command_input == '/allergeni':
            register_request(chat_id, command_input)
            bot.sendPhoto(
                chat_id, 'http://menu.ersurb.it/menum/Allergeni_legenda.png', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Send credits
        elif command_input == '/info':
            register_request(chat_id, command_input)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Dona',
                                      url='https://www.gitcheese.com/donate/users/9751015/repos/90749559')],
            ])
            bot.sendMessage(chat_id, _('source_code') + "\n" +
                            "https://github.com/Radeox/MensaUniurbBot\n\n" +
                            _('developed_by') + "\n" +
                            "https://github.com/Radeox\n" +
                            "https://github.com/Fast0n\n\n" +
                            "🍺 " + _('beer') + " 🍺", reply_markup=keyboard)

        # Send opening hours
        elif command_input == '/orari':
            register_request(chat_id, command_input)
            bot.sendMessage(chat_id, "🍝*Duca*\n{0}\n\n*🍖Tridente*\n{1}\n\n"
                                     "🍟*Sogesta\n*{2}".format(
                                         DUCA_HOURS, TRIDENTE_HOURS, SOGESTA_HOURS),
                                     parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Send statistics about monthly use
        elif command_input == '/statistiche':
            now = datetime.now()
            year = int(now.strftime("%Y"))
            month = int(now.strftime("%m"))

            # Get graph
            fname = get_month_graph(chat_id, year, month)

            with open(fname, 'rb') as f:
                # Get caption
                caption = (_('total_user') + "{0}".format(get_total_users()) + "\n" + _(
                    'total_requests') + "{0}".format(get_total_requests()))

                bot.sendPhoto(chat_id, f, caption, reply_markup=ReplyKeyboardRemove(
                    remove_keyboard=True))
                f.close()

        # Send location Duca
        elif command_input == '/posizioneduca':
            bot.sendLocation(chat_id, "43.72640143124929",
                             "12.63739407389494", reply_to_message_id=msg['message_id'])

        # Send location Tridente
        elif command_input == '/posizionetridente':
            bot.sendLocation(chat_id, "43.720036", "12.623293",
                             reply_to_message_id=msg['message_id'])

        # Send location Sogesta
        elif command_input == '/posizionesogesta':
            bot.sendLocation(chat_id, "43.700293", "12.641057",
                             reply_to_message_id=msg['message_id'])

        # Settings menu
        elif command_input == '/impostazioni':
            entries = []
            p_entries = []

            # Open connection to DB
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Get notification , language
            query = (
                'SELECT notification, language FROM user WHERE chat_id == "%s"' % chat_id)
            cursor.execute(query)
            notification, language = cursor.fetchall()[0]

            if language == "it":
                LANG = ['it_IT']
            elif language == "en":
                LANG = ['en_US']
            

            t = gettext.translation('messages', 'locales', languages=LANG)
            _ = t.gettext

            # Close connection to DB
            conn.close()

            entries.append([_('notification') + notification.title()])
            if language == "en":
                entries.append([_('language') + "It" + " 🇮🇹"])
            elif language == "it":
                entries.append([_('language') + "En" + " 🇺🇸"])

            entries.append(p_entries)

            # Make week keyboard
            markup = ReplyKeyboardMarkup(keyboard=entries)
            bot.sendMessage(chat_id, "⚙️ " + _('settings') , reply_markup=markup)

        elif command_input == _('notification') + "Off":
            # Open connection to DB
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            query = ('UPDATE user '
                     'SET notification ="{0}" '
                     'WHERE chat_id="{1}"'.format("on", chat_id))

            cursor.execute(query)
            conn.commit()

            # Close connection to DB
            conn.close()
            msg['text'] = "/impostazioni"
            handle(msg)

        elif command_input == _('notification') + "On":
            # Open connection to DB
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            query = ('UPDATE user '
                     'SET notification ="{0}" '
                     'WHERE chat_id="{1}"'.format("off", chat_id))

            cursor.execute(query)
            conn.commit()

            # Close connection to DB
            conn.close()
            msg['text'] = "/impostazioni"
            handle(msg)

        elif command_input == _('language') + "It" + " 🇮🇹":
            # Open connection to DB
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            query = ('UPDATE user '
                     'SET language ="{0}" '
                     'WHERE chat_id="{1}"'.format("it", chat_id))
            cursor.execute(query)
            conn.commit()
            # Close connection to DB
            conn.close()
            msg['text'] = "/impostazioni"
            handle(msg)
        elif command_input == _('language') + "En" + " 🇺🇸":
            # Open connection to DB
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            query = ('UPDATE user '
                     'SET language ="{0}" '
                     'WHERE chat_id="{1}"'.format("en", chat_id))
            cursor.execute(query)
            conn.commit()
            # Close connection to DB
            conn.close()
            msg['text'] = "/impostazioni"
            handle(msg)

        # Send news to all registred users - Password required - 1
        elif command_input == '/sendnews':
            USER_STATE[chat_id] = 3
            bot.sendMessage(chat_id, "*Inserisci la password*",
                            parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Send news to all registred users - Password required - 2
        elif USER_STATE[chat_id] == 3:
            if command_input.lower() == PASSWORD:
                USER_STATE[chat_id] = 4
                bot.sendMessage(chat_id,
                                "*Invia un messaggio o una foto con caption\n(Markdown non supportato con foto)*",
                                parse_mode="Markdown")
            else:
                USER_STATE[chat_id] = 0
                bot.sendMessage(chat_id, "*Password Errata*",
                                parse_mode="Markdown")

        # Send news to all registred users - Password required - 3
        elif USER_STATE[chat_id] == 4:
            USER_STATE[chat_id] = 0

            # Send to all users
            send_msg_news(command_input)

        # Edit news to all registred users - Password required - 1
        elif command_input == '/editnews':
            USER_STATE[chat_id] = 13
            bot.sendMessage(chat_id, "*Inserisci la password*",
                            parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Edit news to all registred users - Password required - 2
        elif USER_STATE[chat_id] == 13:

            if command_input.lower() == PASSWORD:
                USER_STATE[chat_id] = 14
                bot.sendMessage(chat_id,
                                "*Edita il messaggio*",
                                parse_mode="Markdown", reply_to_message_id=TEMP[chat_id]['sent']['message_id'])
            else:
                USER_STATE[chat_id] = 0
                bot.sendMessage(chat_id, "*Password Errata*",
                                parse_mode="Markdown")

        # Edit news to all registred users - Password required - 3
        elif USER_STATE[chat_id] == 14:
            USER_STATE[chat_id] = 0
            # Send to all users
            edit_msg_news(command_input)

        # Delete news to all registred users - Password required - 1
        elif command_input == '/deletenews':
            USER_STATE[chat_id] = 15
            bot.sendMessage(chat_id, "*Inserisci la password*",
                            parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Delete news to all registred users - Password required - 2
        elif USER_STATE[chat_id] == 15:

            if command_input.lower() == PASSWORD:
                USER_STATE[chat_id] = 16
                delete_msg_news(command_input)
            else:
                USER_STATE[chat_id] = 0
                bot.sendMessage(chat_id, "*Password Errata*",
                                parse_mode="Markdown")

        # Send poll to all registred users - Password required - 1
        elif command_input == '/sendpoll':
            USER_STATE[chat_id] = 6
            bot.sendMessage(chat_id, "*Inserisci la password*",
                            parse_mode="Markdown")

        # Send poll to all registred users - Password required - 2
        elif USER_STATE[chat_id] == 6:
            if command_input.lower() == PASSWORD:
                USER_STATE[chat_id] = 7
                bot.sendMessage(chat_id, "*Fai una domanda*",
                                parse_mode="Markdown")
            else:
                USER_STATE[chat_id] = 0
                bot.sendMessage(chat_id, "*Password Errata*",
                                parse_mode="Markdown")

        # Send poll to all registred users - Password required - 3
        elif USER_STATE[chat_id] == 7:
            USER_STATE[chat_id] = 8
            TEMP[chat_id] = {}
            TEMP[chat_id]['question'] = command_input

            bot.sendMessage(chat_id, "*Prima risposta*", parse_mode="Markdown")

        # Send poll to all registred users - Password required - 4
        elif USER_STATE[chat_id] == 8:
            USER_STATE[chat_id] = 9
            TEMP[chat_id]['first_answer'] = command_input

            bot.sendMessage(chat_id, "Seconda risposta", parse_mode="Markdown")

        elif USER_STATE[chat_id] == 9:
            USER_STATE[chat_id] = 0

            question = TEMP[chat_id]['question'].capitalize()
            first_answer = TEMP[chat_id]['first_answer'].capitalize()
            second_answer = command_input.capitalize()

            # Register in DB
            register_poll(question, first_answer, second_answer)

            # Send to all users
            send_msg_poll(question, first_answer, second_answer)

        # Send report to admin
        elif command_input == '/segnala':
            USER_STATE[chat_id] = 5
            bot.sendMessage(chat_id, '*' + _('report') + '*',
                            parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        elif USER_STATE[chat_id] == 5:
            USER_STATE[chat_id] = 0

            # Sent to admins
            msg = _('from') + "{0}:\n_{1}_".format(
                chat_id, command_input)
            send_msg_report(msg)

            # Send to user
            msg = _('report_one') + '_"{0}"_'.format(
                command_input) + _('report_two')
            bot.sendMessage(chat_id, msg, parse_mode="Markdown")

    # Send news to all registred users - Password required - 3
    elif content_type == 'photo' and USER_STATE[chat_id] == 4:
        USER_STATE[chat_id] = 0

        # Check if caption exist
        try:
            caption = msg['caption']
        except KeyError:
            caption = None

        msg = msg['photo'][-1]['file_id']

        # Send to all users
        send_photo_all(msg, caption)


def get_menu_message(kitchen, date, meal):
    """
    Generate a ready-to-send message with menu of given kitchen
    """
    ch = {
        'Duca': DUCA_HOURS,
        'Cibus': DUCA_HOURS,
        'Tridente': TRIDENTE_HOURS,
        'CibusTr': TRIDENTE_HOURS,
        'Sogesta': SOGESTA_HOURS
    }

    cn = {
        'Cibus': 'Cibus Duca',
        'CibusTr': 'Cibus Tridente',
        'Duca': 'Duca',
        'Tridente': 'Tridente',
        'Sogesta': 'Sogesta'
    }

    cm = {'Pranzo': 0, 'Cena': 1, 'Lunch': 0, 'Dinner': 1}

    # Get menu
    payload = {'mensa': kitchen, 'da': date, 'a': date}
    core_msg = get_menu(payload)

    # If menu exist send it

    if core_msg[cm[meal]] != "":
        msg = "🗓️*Menu Mensa {0}*\n\n{1}".format(
            cn[kitchen], core_msg[cm[meal]])
        msg += "\n⚠️ Il menù potrebbe subire delle variazioni ⚠️"

        # Random spam
        if randint(1, 5) == 3:
            msg += ("\n\n💙 Aiutaci a sostenere le spese di @MensaUniurb\_Bot.\n"
                    "[Dona 2€](https://www.gitcheese.com/donate/users/9751015/repos/90749559) oppure "
                    "[dona 5€](https://www.gitcheese.com/donate/users/9751015/repos/90749559).")
    else:
        msg = CLOSED_MSG.format(cn[kitchen], ch[kitchen])

    return msg


def get_menu(payload):
    """
    Get the menu from the ERSU page
    """
    r = requests.post("http://menu.ersurb.it/menum/menu.asp", data=payload)

    last = False
    msg_lunch = ""
    msg_dinner = ""
    p = ['', '', '', '']

    soup = BeautifulSoup(r.text, 'html.parser')

    for link in soup.find_all('a')[1:]:
        app = link.get('onclick').replace('showModal', '')

        # Get ID
        idi = app.split()[1]
        idi = idi.replace('"', '').replace(',', '')

        # Get name
        name = app.split(', ')[2]
        name = name.replace('"', '').replace(');', '')

        # Remove useless chars
        name = name.replace('*', 'X')

        # Capitalized entries
        name = name.capitalize()

        # Check if lunch/dinner
        if idi == '40':
            last = True
        elif idi == '10' and last:
            if p[0]:
                msg_lunch += "🍝Primi:\n%s\n" % p[0]
            if p[1]:
                msg_lunch += "🍖Secondi:\n%s\n" % p[1]
            if p[2]:
                msg_lunch += "🍟Contorno:\n%s\n" % p[2]
            if p[3]:
                msg_lunch += "🍨Frutta/Dolce:\n%s" % p[3]

            # Reset accumulation vars
            p = ['', '', '', '']
            last = False

        # Check type
        if idi == '10':
            p[0] += ' • {0}\n'.format(name)
        elif idi == '20':
            p[1] += ' • {0}\n'.format(name)
        elif idi == '30':
            p[2] += ' • {0}\n'.format(name)
        elif idi == '40':
            p[3] += ' • {0}\n'.format(name)

    if p[0]:
        msg_dinner += "🍝Primi:\n%s\n" % p[0]
    if p[1]:
        msg_dinner += "🍖Secondi:\n%s\n" % p[1]
    if p[2]:
        msg_dinner += "🍟Contorno:\n%s\n" % p[2]
    if p[3]:
        msg_dinner += "🍨Frutta/Dolce:\n%s" % p[3]

    return [msg_lunch, msg_dinner]


def get_month_graph(msg, year, month):
    """
    Return the uses graph of given month
    """
    # Ensure storage directory exists
    try:
        os.mkdir('plots')
    except FileExistsError:
        pass

    # Function to change language
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get notification , language
    query = (
        'SELECT notification, language FROM user WHERE chat_id == "%s"' % msg)
    cursor.execute(query)
    notification, language = cursor.fetchall()[0]

    if language == "it":
        LANG = ['it_IT.ISO8859-15']
    elif language == "en":
        LANG = ['en_US']

    t = gettext.translation('messages', 'locales', languages=LANG)
    _ = t.gettext

    # Close connection to DB
    conn.close()


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
    plt.title( _('usage_statistics') + " {0}/{1}".format(month, year))
    plt.xlabel( _('days_of_the_month') )
    plt.xlim([1, days_month])
    plt.ylabel(_('use') )

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
def send_msg_news(msg):
    """
    Send given message to all users
    """
    for user in get_user_list():
        try:
            # Open connection to DB
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Get notification
            query = (
                'SELECT notification FROM user WHERE chat_id == "%s"' % user)
            cursor.execute(query)
            notification = cursor.fetchone()[0].title()

            # Close connection to DB
            conn.close()

            if notification == "On":
                sent = bot.sendMessage(user, msg, parse_mode="Markdown")
                TEMP[user] = {}
                TEMP[user]['sent'] = sent
        except:
            continue

    return 1


def edit_msg_news(msg):
    """
    Edit last message sent to all users
    """
    for user in get_user_list():
        try:
            edited = telepot.message_identifier(TEMP[user]['sent'])
            bot.editMessageText(edited, msg, parse_mode="Markdown")
        except:
            continue

    return 1


def delete_msg_news(msg):
    """
    Delete last message sent to all users
    """
    for user in get_user_list():
        try:
            edited = telepot.message_identifier(TEMP[user]['sent'])
            bot.deleteMessage(edited)
        except:
            continue

    return 1


def send_msg_poll(question, first_answer, second_answer):
    """
    Send given message to all users
    """
    for user in get_user_list():
        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=first_answer, callback_data="1_%s" % question),
                InlineKeyboardButton(text=second_answer,
                                     callback_data="2_%s" % question),
            ]])

            bot.sendMessage(user, question, parse_mode="Markdown",
                            reply_markup=keyboard)
        except:
            continue

    return 1


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


def send_photo_all(photo, caption):
    """
    Send given photo to all users
    """
    users = get_user_list()

    for user in users:
        try:
            sent = bot.sendPhoto(user, photo, caption=caption)
            TEMP[user] = {}
            TEMP[user]['sent'] = sent
        except:
            continue

    return 1

## Query funtions ##


def register_user(chat_id, username, name, language):
    """
    Register given user to receive news and statistics
    """

    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        query = ('INSERT INTO user(chat_id, name, username, notification, language) '
                 'VALUES({0}, "{1}", "{2}", "{3}", "{4}")'.format(chat_id, name, username, 'on', language))

        cursor.execute(query)
        conn.commit()
    except sqlite3.IntegrityError:
        return 0
    finally:
        # Close connection to DB
        conn.close()

    return 1


def update_user(chat_id, username, name):
    """
    Register given user to receive news and statistics
    """
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        query = ('UPDATE user '
                 'SET username ="{0}", name ="{1}" '
                 'WHERE chat_id="{2}"'.format(username, name, chat_id))

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


def register_poll(question, first_answer, second_answer):
    """
    Register poll in DB
    """
    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = ('INSERT INTO poll(ask, answer1, answer2, count_answer1, count_answer2) '
             'VALUES("{0}", "{1}", "{2}", 0, 0)'.format(question, first_answer, second_answer))

    cursor.execute(query)
    conn.commit()

    # Close connection to DB
    conn.close()
    return 1


def on_callback_query(msg):
    """
    Register answer to poll
    """
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')

    response = data.split('_')[0]
    question = data.split('_')[1]

    # Open connection to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if response != '0':
        query = ('UPDATE poll '
                 'SET count_answer{0} = count_answer{0} + 1 '
                 'WHERE ask="{1}"'.format(response, question))
        cursor.execute(query)
        conn.commit()

        bot.answerCallbackQuery(query_id, "Grazie per aver votato")

    query = ('SELECT answer1, answer2, count_answer1, count_answer2 '
             'FROM poll WHERE ask="{0}"'.format(question))
    cursor.execute(query)

    answer1, answer2, response1, response2 = cursor.fetchall()[0]

    # Calculate percentage
    tot = response1 + response2
    pa1 = int((response1 / tot) * 100)
    pa2 = int((response2 / tot) * 100)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=answer1 + "(" + str(pa1) + "%)", callback_data='0_%s' % question),
        InlineKeyboardButton(
            text=answer2 + "(" + str(pa2) + "%)", callback_data='0_%s' % question),
    ]])

    # Edit buttons
    edit = (msg['message']['chat']['id'], msg['message']['message_id'])
    try:
        bot.editMessageText(edit, question, reply_markup=keyboard)
    except telepot.exception.TelegramError:
        pass

    # Close connection to DB
    conn.close()

    bot.sendMessage(from_id, "Hai già votato!\n\n"
                             "Voti totali: {0}\n"
                             "({1}%) voti per {2}\n"
                             "({3}%) voti per {4}".format(tot, pa1, answer1, pa2, answer2))

    bot.answerCallbackQuery(query_id)


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
TEMP = {}

# Start working
try:
    bot = telepot.Bot(TOKEN)
    bot.message_loop({'chat': handle, 'callback_query': on_callback_query})

    while 1:
        sleep(10)
finally:
    # Remove PID file on exit
    os.unlink(PIDFILE)
