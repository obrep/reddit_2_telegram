# Reddit 2 Telegram - A bot serving content from Reddit straight to Telegram chat

The bot is currently deployed on Heroku. You can talk to him here: [t.me/pablos_good_bot](https://t.me/pablos_good_bot). In case of any problems/suggestions, please contact me: obrepalski@pm.me

## Functionality
The bot can serve content from any subreddit, along with the statistics of corresponding post. Submissions already shown to the user are saved to database in order to not provide them repeatedly (of course different users can still see them).

### Subreddit commands
It also can serve pre-formatted content from specific subreddits with commands:

1. /joke -> provides 'hottest' unseen joke from r/jokes.
2. /meme -> provides 'hottest' unseen meme from r/memes.

### Utility commands
1. /stats -> displays how many submissions have been shown to how many users.
2. /userstats -> displays how how many submissions have been shown to current user.