import time

def getTimeAgo(timestamp):
    timespan = time.time() - timestamp

    if timespan > 3600*24:
        return '%d days ago' % int(timespan/(3600*24))
    elif timespan > 3600:
        return '%dh ago' % int(timespan/3600)
    else:
        return '%d minutes ago' % int(timespan/60)

def makeSnippet(submission):
    url = submission.permalink.replace('www.reddit.', 'm.reddit.')
    formated_comments = formatScore(submission.num_comments)
    timestamp = getTimeAgo(submission.created_utc)
    formatted_score = formatScore(submission.score)
    return '<a href="old.reddit.com%s">Statistics and link to thread:\n%s score, %s comments, %s</a>' % (url, formatted_score, formated_comments, timestamp)

def makeMessage(submission):
    return "[%s](%s)" % (submission.title, submission.url)

def formatScore(score):
    if score < 1000:
        return str(score)
    else:
        return str("%.1fk" % (score/1000))

