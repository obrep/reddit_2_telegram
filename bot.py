import logging
import os
import sys
# Dataset for storing information about already sent submissions
import dataset
# Telegram communication
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
# Python Reddit API Wrapper
import praw
# Error handling
from prawcore.exceptions import Redirect, NotFound
# Formatting functions
from helpers import * 
from messages import *


# Logger setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

logger = logging.getLogger(__name__)

# Create reddit wrapper object
reddit = praw.Reddit(client_id = os.environ['REDDIT_ID'],
                    client_secret = os.environ['REDDIT_SECRET'],
                    user_agent = os.environ['REDDIT_AGENT'])

# Connect to database
db = dataset.connect('sqlite:///:memory:')

class RedditBot():
    """
    Creates and mantains connection with Telegram.
    Provides content from Reddit through Telegram chat.

    Handles multiple commands (e.g. \start, \start).
    Messages that are not commands are treated as subreddit names.
    """

    def __init__(self):
        # Create useful objects
        updater = Updater(token=os.environ['TELEGRAM_TOKEN'], use_context=True)
        dispatcher = updater.dispatcher

        # Add Handlers
        # Handlers check the update in the order they were added
        # (So the errors etc. should be last)
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('joke', self.serveJoke))
        dispatcher.add_handler(CommandHandler('meme', self.serveMeme))
        dispatcher.add_handler(CommandHandler('help', self.help))
        dispatcher.add_handler(CommandHandler('stats', self.stats))
        dispatcher.add_handler(CommandHandler('userstats', self.userstats))
        dispatcher.add_handler(MessageHandler(Filters.text, self.fetch))
        dispatcher.add_handler(MessageHandler(Filters.command, self.unknown))

        # Initial values of parameters
        self.message = ''
        self.chat_id = None
        self.user_id = None
        self.subreddit = None
        self.submission = None

        # Start the bot
        updater.start_polling()
        logger.info("RedditBot started polling.")
    
    # Set methods
    def set_message(self, update):
        self.message = update.message.text

    def set_chat_id(self, update):
        self.chat_id = update.message.chat_id

    def set_user_id(self, update):
        self.user_id = update.message.from_user.id

    # Commands actions
    def start(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text=start_msg)
    
    def serveJoke(self, update, context):
        logger.info("Received joke command")
        self.get_submission('jokes')
        context.bot.send_message(chat_id=update.message.chat_id, text=self.submission.title)
        context.bot.send_message(chat_id=update.message.chat_id, text=self.submission.selftext)
    
    def serveMeme(self, update, context):
        logger.info("Received meme command")
        self.get_submission('memes')
        context.bot.sendPhoto(chat_id=update.message.chat_id,
                        photo=self.submission.url)


    def help(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text=help_msg)

    def stats(self, update, context):
        shown_count = len(db['shown'])
        users_count = len(list(db['shown'].distinct('userid')))
        stats_msg = "So far, I\'ve shown %d submissions to %d users." % (shown_count, users_count)
        context.bot.sendMessage(chat_id=update.message.chat_id, text=stats_msg)
        logger.info("Presented stats globally %s" % stats_msg)
    
    def userstats(self, update, context):
        shown_count = db['shown'].count(userid=self.user_id)
        stats_msg = "So far, I\'ve shown you %d submissions." % shown_count
        context.bot.sendMessage(chat_id=update.message.chat_id, text=stats_msg)
        logger.info("Presented stats to user %s: %s" % (self.user_id, stats_msg))

    def unknown(self, update, context):
        logger.info("Received Unknown command: '%s'", update.message.text)
        context.bot.send_message(chat_id=update.message.chat_id, text=unknown_command_msg)

    def error_callback(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    # Methods used to serve content
    def fetch(self, update, context):
        logger.info("Received message: '%s'", update.message.text)

        self.set_message(update)
        self.set_chat_id(update)
        self.set_user_id(update)
        self.set_subreddit(update, context)

        if self.subreddit is not None:
            self.get_submission()
            self.show_submission(update, context)

    def set_subreddit(self, update, context):
        sub = update.message.text
        # Test if provided name is correctly formatted
        if not sub.isalpha():
            logger.warning("Invalid subname provided: %s" % sub)
            wrong_sub_name_msg = "Provided subreddit name is not correct, it must contain only characters, without spaces, /, etc. Please try again :)"
            context.bot.sendMessage(chat_id=self.chat_id,
                        text=wrong_sub_name_msg)
            self.subreddit = None
            return
        
        # Test if subreddit exists
        try:
            reddit.subreddit(sub).id
        
        # If the subreddit does not exist log it and inform user
        except (Redirect, NotFound):
            exception_msg= "/r/{} could not be reached. Please try another subreddit, or one of the predefined commands (/help for full list).".format(sub)
            context.bot.sendMessage(chat_id=self.chat_id,
                                    text=exception_msg)
            logger.warning("Error when setting subreddit. Invalid /r/%s" % sub)
            return
        
        # Finally, set the subreddit 
        self.subreddit = reddit.subreddit(sub)
        logger.info("Subreddit set to r/%s" % sub)

            
    def get_submission(self, sub=None):
        if sub is not None:
            self.subreddit = reddit.subreddit(sub)
        
        for submission in self.subreddit.hot():
            if db['shown'].find_one(userid=self.user_id, submission=submission.id) is None and not submission.stickied:
                self.submission = submission
                db['shown'].insert(dict(userid=self.user_id,
                              subreddit=str(self.subreddit.display_name),
                              submission=str(submission.id)))
                break
    
        logger.info("Fetched from /r/%s" % self.subreddit.display_name)

    def show_submission(self, update, context, type=None):

        # Prepare text and snippet earlier, so it is ready to use and messages come at the same time
        text_message = makeMessage(self.submission)
        snippet = makeSnippet(self.submission)

        # Send messages
        context.bot.sendMessage(chat_id=self.chat_id,
                        text=text_message,
                        parse_mode=ParseMode.MARKDOWN)

        # Send short link to reddit, no preview. also keyboard to continue
        context.bot.sendMessage(chat_id=self.chat_id,
                        text=snippet,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True)

        logger.info("Shown: https://redd.it/%s to user: %s" % (self.submission.id, self.user_id))


if __name__ == "__main__":
        RedditBot()