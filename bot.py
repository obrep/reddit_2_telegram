from telegram.ext import Updater, CommandHandler
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

start_handler = CommandHandler('start', start)
hello_handler = CommandHandler('hello', hello)

updater = Updater(token='701812755:AAF8egty5DwPkrmA4LOBPz4zoHdPtdoU3XU', use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(hello_handler)
dispatcher.add_handler(start_handler)

updater.start_polling()
# updater.idle()
