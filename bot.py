from telegram.ext import Updater, CommandHandler, MessageHandler
import logging
import tokens
import sys
# import dataset

#Python Reddit API Wrapper
import praw

# Logger setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

logger = logging.getLogger(__name__)

# Create reddit wrapper object
reddit = praw.Reddit(client_id = tokens.client_id,
                    client_secret = tokens.client_secret,
                    username = tokens.username,
                    password = tokens.password,
                    user_agent = tokens.user_agent)

class RedditBot():
    """
    Creates and mantains connection with Telegram.
    Provides content from Reddit through Telegram chat.

    Handles multiple commands (e.g. \start).
    Subreddits can be chosen using commands.
    """

    def __init__(self):
        # Create useful objects
        updater = Updater(token=tokens.telegram_token, use_context=True)
        dispatcher = updater.dispatcher

        # Add Handlers
        dispatcher.add_handler(CommandHandler('start', self.welcome))
        dispatcher.add_handler(CommandHandler('stats', self.stats))
        # dispatcher.add_handler(MessageHandler(self.fetch))
        # dispatcher.add_error_handler(ErrorHandler(self.error_callback))


                # Initial values of parameters
        self.message = ''
        self.chat_id = None
        self.user_id = None
        self.subreddit = None
        self.submission = None

        # Start the bot
        updater.start_polling()
        logger.info("RedditBot started polling.")

    def welcome(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="Hello. I'm a bot, please talk to me!")

    def stats(self):
        pass

    def fetch(self):
        pass
    
    # def error(self):
    #     pass

    def error_callback(update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    # def hello(bot, update):
    # 	update.message.reply_text(
    # 		'Hello {}'.format(update.message.from_user.first_name))

    # start_handler = CommandHandler('start', start)
    # hello_handler = CommandHandler('hello', hello)

    # updater = Updater(token=tokens.telegram_token, use_context=True)
    # dispatcher = updater.dispatcher

    # dispatcher.add_handler(hello_handler)
    # dispatcher.add_handler(start_handler)


# updater.idle()


if __name__ == "__main__":
        RedditBot()