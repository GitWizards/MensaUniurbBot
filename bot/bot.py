"""
MensaUniurb - Telegram Bot

Authors: Radeox (dawid.weglarz95@gmail.com)
         Fast0n (theplayergame97@gmail.com)
"""

import os
import logging
import signal
from datetime import datetime
from random import randint

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Filters, CommandHandler, ConversationHandler,
                          CallbackContext, MessageHandler, Updater)
from telegram.error import Conflict
from utils import get_menu_msg, get_monthly_stats, prepare_week_keyboard

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Conversation states
MEAL_CHOICE, DATE_CHOICE = range(2)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("*Benvenuto su @MensaUniurbBot*\n"
                              "Qui troverai il menù offerto troverai da "
                              "Uniurb nei ristoranti /duca e /tridente.\n\n"
                              "_Il bot è stato creato in modo non ufficiale "
                              "nè ERDIS Marche nè Uniurb sono responsabili in alcun modo._",
                              parse_mode='Markdown')
    return


def meal_choice(update: Update, context: CallbackContext) -> int:
    response = update['message']['text']

    if response == '/duca':
        context.user_data['place'] = "duca"
    elif response == '/tridente':
        context.user_data['place'] = "tridente"
    elif response == '/cibus':
        context.user_data['place'] = "cibus"

    # Prepare keyboard
    keyboard = [["Pranzo"], ["Cena"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text("*Pranzo o Cena?* 🍔🍝", reply_markup=markup, parse_mode="Markdown")
    return MEAL_CHOICE


def date_choice(update: Update, context: CallbackContext) -> int:
    response = update['message']['text']

    if response == 'Pranzo':
        context.user_data['meal'] = "lunch"
    elif response == 'Cena':
        context.user_data['meal'] = "dinner"

    markup = ReplyKeyboardMarkup(prepare_week_keyboard(), one_time_keyboard=True)

    update.message.reply_text("*Quando?* 📅", reply_markup=markup, parse_mode="Markdown")
    return DATE_CHOICE


def send_menu(update: Update, context: CallbackContext) -> int:
    # Convert date from DD/MM to MM-DD-YYYY
    now = datetime.now()
    date = update['message']['text'].split(' ')[1].replace('[', '').replace(']', '')
    complete_date = f"{date.split('/')[1]}-{date.split('/')[0]}-{now.strftime('%Y')}"

    msg = get_menu_msg(context.user_data['place'], complete_date, context.user_data['meal'])

    if msg == "NO_DATA":
        update.message.reply_text("*Non ho trovato nulla 🤷🏻‍♂️ *\n\nControlla gli /orari",
                                  reply_markup=ReplyKeyboardRemove(),
                                  parse_mode="Markdown")
    elif msg == "ERROR":
        update.message.reply_text("🔧 Qualcosa è andato nella comunicazione con il sito ERDIS 🔧\n\n"
                                  "Riprova più tardi o direttamente sul loro [sito](http://menu.ersurb.it/menum/ricercamenu.asp)",
                                  reply_markup=ReplyKeyboardRemove(),
                                  parse_mode="Markdown")
    else:
        # Randomly add paypal link to donate or link to playstore app
        if randint(1, 3) == 1:
            msg += ("\n\n-----------------------------\n\n💙 Aiutaci a sostenere le spese di @MensaUniurb\_Bot.\n"
                    "[Clicca qui](https://paypal.me/Radeox/) e decidi una somma. Grazie!")

        # Send menu to user
        update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")

    return ConversationHandler.END


def conversation_fallback(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("*Non ho capito! Riprova da capo 😕*\n\nOpzioni:\n/duca\n/tridente",
                              reply_markup=ReplyKeyboardRemove(),
                              parse_mode="Markdown")
    return ConversationHandler.END


def unimplemented_fallback(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("*Questa funzione potrebbe essere ancora rotta, "
                              "ma ci stiamo lavorando 😕*", parse_mode="Markdown")


def send_stats(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_monthly_stats())


def send_timetable(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("🍝 *Duca*\nAperta tutti i giorni feriali "
                              "dalle *12:00* alle *17:00*.\n"
                              "*Posizione*: /posizione\_duca\n\n"
                              "🍖 *Tridente*\n"
                              "Aperta tutti i giorni dalle *12:00* alle *14:00* "
                              "e dalle *19:00* alle *21:00*.\n"
                              "*Posizione*: /posizione\_tridente\n\n",
                              parse_mode="Markdown")


def send_duca_location(update: Update, context: CallbackContext) -> None:
    update.message.reply_location("43.72640143124929", "12.63739407389494", quote=True)
    update.message.reply_text("📍 *Indirizzo*: Via Budassi n° 3", parse_mode="Markdown")


def send_tridente_location(update: Update, context: CallbackContext) -> None:
    update.message.reply_location("43.720036", "12.623293", quote=True)
    update.message.reply_text("📍 *Indirizzo*: Via Giancarlo De Carlo n° 7", parse_mode="Markdown")


def send_pricelist(update: Update, context: CallbackContext) -> None:
    with open("assets/price_list.png", 'rb') as f:
        update.message.reply_photo(f, quote=True)


def send_allergylist(update: Update, context: CallbackContext) -> None:
    update.message.reply_photo("http://menu.ersurb.it/menum/Allergeni_legenda.png")


def send_credits(update: Update, context: CallbackContext) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="☕ Offrici un caffè e/o una birra 🍺",
                url="https://paypal.me/Radeox/"
            )
        ],
    ])

    update.message.reply_text("*Link*:\n"
                              "[Google Play](https://play.google.com/store/apps/details?id=com.radeox.mensa_uniurb)\n"
                              "[Codice sorgente](https://github.com/FastRadeox/MensaUniurbBot)\n\n"
                              "*Developers*:\n"
                              "[Radeox - Github](https://github.com/Radeox)\n"
                              "[Fast0n - Github](https://github.com/Fast0n)",
                              reply_markup=keyboard,
                              parse_mode="Markdown")


def error_handler(update: object, context: CallbackContext) -> None:
    if isinstance(context.error, Conflict):
        print("[FATAL] Token conflict!")
        os.kill(os.getpid(), signal.SIGINT)
    else:
        print("[ERROR] " + str(context.error))


def main():
    # Load env variables
    load_dotenv()
    TOKEN = os.environ['TOKEN']

    # Setup bot
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    start_handler = CommandHandler('start', start)
    stats_handler = CommandHandler('statistiche', send_stats)
    timetable_handler = CommandHandler('orari', send_timetable)
    pricelist_handler = CommandHandler('prezzi', send_pricelist)
    allergylist_handler = CommandHandler('allergeni', send_allergylist)
    credits_handler = CommandHandler('crediti', send_credits)
    donate_handler = CommandHandler('dona', send_credits)
    location_duca_handler = CommandHandler("posizione_duca", send_duca_location)
    location_tridente_handler = CommandHandler("posizione_tridente", send_tridente_location)

    menu_handler = ConversationHandler(
        entry_points=[CommandHandler(['duca', 'tridente', 'cibus'], meal_choice)],
        states={
            MEAL_CHOICE: [
                MessageHandler(Filters.regex('Pranzo|Cena'), date_choice),
            ],
            DATE_CHOICE: [
                MessageHandler(Filters.regex('[a-zA-Zì]+ .[0-9]+[/]+[0-9]+.'), send_menu),
            ],
        },
        fallbacks=[MessageHandler(Filters.update, conversation_fallback)],
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(menu_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(timetable_handler)
    dispatcher.add_handler(location_duca_handler)
    dispatcher.add_handler(location_tridente_handler)
    dispatcher.add_handler(pricelist_handler)
    dispatcher.add_handler(allergylist_handler)
    dispatcher.add_handler(credits_handler)
    dispatcher.add_handler(donate_handler)
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
