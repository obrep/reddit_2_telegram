import praw 
reddit = praw.Reddit(client_id='ID', client_secret="SECRET", user_agent='USERAGENT')       

for submission in reddit.subreddit('learnpython').hot(limit=10): 
    print(submission.title) 