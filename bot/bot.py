"""
MensaUniurb - Telegram Bot

Authors: Radeox (dawid.weglarz95@gmail.com)
         Fast0n (theplayergame97@gmail.com)
"""

import logging
import os
import signal
from datetime import datetime
from random import randint

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.error import Conflict
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from utils import get_menu_msg, get_monthly_stats, prepare_week_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Conversation states
MEAL_CHOICE, DATE_CHOICE = range(2)


async def start(update: Update, _) -> None:
    await update.message.reply_text(
        "*Benvenuto su @MensaUniurbBot*\n"
        "Qui troverai il menù offerto troverai da "
        "Uniurb nei ristoranti /duca e /tridente.\n\n"
        "_Il bot è stato creato in modo non ufficiale "
        "nè ERDIS Marche nè Uniurb sono responsabili in alcun modo._",
        parse_mode="Markdown",
    )
    return


async def meal_choice(update: Update, context: CallbackContext) -> int:
    response = update["message"]["text"]

    if response == "/duca":
        context.user_data["place"] = "duca"
    elif response == "/tridente":
        context.user_data["place"] = "tridente"

    # Prepare keyboard
    keyboard = [["Pranzo"], ["Cena"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "*Pranzo o Cena?* 🍔🍝", reply_markup=markup, parse_mode="Markdown"
    )
    return MEAL_CHOICE


async def date_choice(update: Update, context: CallbackContext) -> int:
    response = update["message"]["text"]

    if response == "Pranzo":
        context.user_data["meal"] = "lunch"
    elif response == "Cena":
        context.user_data["meal"] = "dinner"

    markup = ReplyKeyboardMarkup(prepare_week_keyboard(), one_time_keyboard=True)

    await update.message.reply_text(
        "*Quando?* 📅", reply_markup=markup, parse_mode="Markdown"
    )
    return DATE_CHOICE


async def send_menu(update: Update, context: CallbackContext) -> int:
    # Convert date from DD/MM to MM-DD-YYYY
    now = datetime.now()
    date = update["message"]["text"].split(" ")[1].replace("[", "").replace("]", "")
    complete_date = f"{date.split('/')[1]}-{date.split('/')[0]}-{now.strftime('%Y')}"

    msg = get_menu_msg(
        context.user_data["place"], complete_date, context.user_data["meal"]
    )

    if msg == "NO_DATA":
        await update.message.reply_text(
            "*Non ho trovato nulla 🤷🏻‍♂️ *\n\nControlla gli /orari\n\nOppure il [link ufficiale](https://www.erdis.it/menu/template/OpenMenuWeek.html)\n",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown",
        )
    elif msg == "ERROR":
        await update.message.reply_text(
            "🔧 Qualcosa è andato nella comunicazione con il sito ERDIS 🔧\n\n"
            "Riprova più tardi o direttamente sul loro [sito](http://menu.ersurb.it/menum/ricercamenu.asp)",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown",
        )
    else:
        # Randomly add paypal link to donate or link to playstore app
        if randint(1, 3) == 1:
            msg += (
                "\n\n-----------------------------\n\n💙 Aiutaci a sostenere le spese di @MensaUniurb\\_Bot.\n"
                "[Clicca qui](https://paypal.me/Radeox/) e decidi una somma. Grazie!"
            )

        # Send menu to user
        await update.message.reply_text(
            msg, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown"
        )

    return ConversationHandler.END


async def conversation_fallback(update: Update, _) -> int:
    await update.message.reply_text(
        "*Non ho capito! Riprova da capo 😕*\n\nOpzioni:\n/duca\n/tridente",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def send_stats(update: Update, _) -> None:
    await update.message.reply_text(get_monthly_stats())


async def send_timetable(update: Update, _) -> None:
    await update.message.reply_text(
        "🍝 *Duca*\nAperta tutti i giorni feriali "
        "dalle *12:00* alle *14:30* "
        "e dalle *19:00* alle *21:00*.\n"
        "*Posizione*: /posizione\\_duca\n\n"
        "🍖 *Tridente*\n"
        "Aperta tutti i giorni dalle *12:00* alle *14:15* "
        "e dalle *19:00* alle *21:00*.\n"
        "*Posizione*: /posizione\\_tridente\n\n",
        parse_mode="Markdown",
    )


async def send_duca_location(update: Update, _) -> None:
    await update.message.reply_location(
        "43.72640143124929", "12.63739407389494", quote=True
    )
    await update.message.reply_text(
        "📍 *Indirizzo*: Via Budassi n° 3", parse_mode="Markdown"
    )


async def send_tridente_location(update: Update, _) -> None:
    await update.message.reply_location("43.720036", "12.623293", quote=True)
    await update.message.reply_text(
        "📍 *Indirizzo*: Via Giancarlo De Carlo n° 7", parse_mode="Markdown"
    )


async def send_credits(update: Update, _) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="☕ Offrici un caffè e/o una birra 🍺",
                    url="https://paypal.me/Radeox/",
                )
            ],
        ]
    )

    await update.message.reply_text(
        "*Link*:\n"
        "[Google Play](https://play.google.com/store/apps/details?id=com.radeox.mensa_uniurb)\n"
        "[Codice sorgente](https://github.com/GitWizards/MensaUniurbBot)\n\n"
        "*Developers*:\n"
        "[Radeox - Github](https://github.com/Radeox)\n"
        "[Fast0n - Github](https://github.com/Fast0n)",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


async def error_handler(_, context: CallbackContext) -> None:
    if isinstance(context.error, Conflict):
        print("[FATAL] Token conflict!")
        os.kill(os.getpid(), signal.SIGINT)
    else:
        print("[ERROR] " + str(context.error))


def main() -> None:
    # Load env variables
    TOKEN = os.environ["TOKEN"]

    # Setup bot
    application = Application.builder().token(TOKEN).build()

    menu_handler = ConversationHandler(
        entry_points=[CommandHandler(["duca", "tridente"], meal_choice)],
        states={
            MEAL_CHOICE: [
                MessageHandler(filters.Regex("Pranzo|Cena"), date_choice),
            ],
            DATE_CHOICE: [
                MessageHandler(
                    filters.Regex("[a-zA-Zì]+ .[0-9]+[/]+[0-9]+."), send_menu
                ),
            ],
        },
        fallbacks=[MessageHandler(filters.Update, conversation_fallback)],
    )

    # Add command handlers
    application.add_handler(CommandHandler("crediti", send_credits))
    application.add_handler(CommandHandler("dona", send_credits))
    application.add_handler(CommandHandler("orari", send_timetable))
    application.add_handler(CommandHandler("posizione_duca", send_duca_location))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("statistiche", send_stats))
    application.add_handler(
        CommandHandler("posizione_tridente", send_tridente_location)
    )
    application.add_handler(menu_handler)
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling()


if __name__ == "__main__":
    main()
