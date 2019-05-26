import time

def getTimeAgo(timestamp):
    timespan = time.time() - timestamp

    if timespan > 3600*24:
        return '%d days ago' % int(timespan/(3600*24))
    elif timespan > 3600:
        return '%d hours ago' % int(timespan/3600)
    else:
        return '%d minutes ago' % int(timespan/60)