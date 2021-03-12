"""
MensaUniurb - Telegram Bot

Authors: Radeox (dawid.weglarz95@gmail.com)
         Fast0n (theplayergame97@gmail.com)
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import os
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("🔧 *Il bot è rotto al momento* 🔧.\n\n" +
                              "Intanto puoi usare la nostra [App](https://play.google.com/store/apps/details?id=com.radeox.mensa_uniurb)",
                              parse_mode="Markdown")

    return


def main():
    load_dotenv()

    # Setup bot
    updater = Updater(os.environ['TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    backup_handler = MessageHandler(Filters.update, start)
    
    # Add command handlers
    dispatcher.add_handler(backup_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
