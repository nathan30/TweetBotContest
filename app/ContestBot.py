import tweepy
import json
from urllib.request import urlopen
import logging
import logging.config
import re
import queueClass
import datetime
from time import sleep
from random import randint, choice

# Load our configuration from the JSON file.
with open('/opt/TweetBot/src/data.json') as file:
    data = json.load(file)
    consumer_key = data['consumer_key']
    consumer_secret = data['consumer_secret']
    access_token = data['access_token']
    access_token_secret = data['access_token_secret']
    search_keyword = data['search']
    lang = data['lang']
    banned_words = data['banned_words']
    follow_keyword = data['follow-keyword']
    log_file = data['log_file']
    nb_tweets = data['nb_tweets_search']
    banned_users = data['banned_users']

# Set logger
logging.config.fileConfig(log_file)
LOGGER = logging.getLogger('superAwesomeLogzioLogger')

def follow_user():
    if FollowQueue.empty() is not True:
        user = FollowQueue.get()[0]
        screen_name = user[0]
        text = user[1]
        api.create_friendship(screen_name)  # Follow tweet author
        LOGGER.info('Follow author :  @' + screen_name)
        if '@' in text:  # Find if we need to follow other user (in addition to the author)
            usersToFollow = re.findall('@\S+', text)
            for user in usersToFollow:
                try:
                    api.create_friendship(user)
                    LOGGER.info('Follow user : ' + user)
                except tweepy.error.TweepError as tweepError:
                    LOGGER.error(str(tweepError).encode('utf-8'))
                    break
    else:
        LOGGER.error('Follow queue empty')

def retweet():
    if RTQueue.empty() is not True:
        RT_id = RTQueue.get()
        try:
            api.retweet(RT_id)
            LOGGER.info('RT tweet ')
        except tweepy.error.TweepError as tweepError:  # Workaround
            LOGGER.error(str(tweepError).encode('utf-8'))  # Because the key Retweeted
            pass  # isn't work and always set as False, so we can never check if the tweet already retweeted
    else:
        LOGGER.error('RT queue empty')

def update_status():
    if TweetQueue.empty() is not True:
        updated_tweet = TweetQueue.get()
        try:
            api.update_status(updated_tweet)
            LOGGER.info('Tweet random stuff')
        except tweepy.error.TweepError as tweepError:
            LOGGER.error(str(tweepError).encode('utf-8'))
            pass
    else:
        LOGGER.error('Tweet queue empty')


def process_queue():
    queue_list = [retweet, follow_user, update_status]
    while RTQueue.empty() is not True or FollowQueue.empty() is not True or TweetQueue.empty() is not True:  # Empty the Queues randomly
        LOGGER.info("RT size : " + str(RTQueue.qsize()) + ' - Follow size : ' + str(FollowQueue.qsize()) + ' - Tweet size : ' + str(TweetQueue.qsize()))
        choice(queue_list)()
        time = randint(100,400)
        LOGGER.info("Let's go slepping for " + str(time/60) + " min")
        sleep(time)  # Wait in order to don't spam too much

if __name__ == '__main__':
    # OAuth to Twitter and get Api object
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

    RTQueue = queueClass.Queue()  # Queue used to RT things one by one after a given time
    TweetQueue = queueClass.Queue()  # Same for random tweets
    FollowQueue = queueClass.Queue()  # Same for follow people

    # Start contest spamming process
    while True:
        for keyword in search_keyword:
            try:
                LOGGER.info("Using keyword : " + keyword)
                tweetsList = tweepy.Cursor(
                    api.search,
                    q=keyword,  # search query is case insensitive
                    lang=lang,
                    tweet_mode="extended"
                ).items(int(nb_tweets))

                for tweet in tweetsList:
                    isRT = hasattr(tweet, 'retweeted_status')  # Check if it's a RT

                    if isRT:
                        user_screen_name = tweet.retweeted_status.user.screen_name
                    else:
                        user_screen_name = tweet.user.screen_name

                    if not tweet.is_quote_status and not tweet.in_reply_to_status_id and user_screen_name not in banned_users and not any(word for word in banned_words if word in tweet.full_text.lower()):  # Do net process quoted status and response of a tweet
                        if not tweet.retweeted:  # Check you didn't already RT this tweet (not working for now)
                            if isRT:
                                rt = tweet.retweeted_status.id
                            else:
                                rt = tweet.id
                            RTQueue.put(rt)

                            # Search follow keyword
                            follow = None
                            if isRT:
                                if any(keyword in tweet.retweeted_status.full_text for keyword in follow_keyword):
                                    follow = [tweet.retweeted_status.user.screen_name, tweet.retweeted_status.full_text]
                            else:
                                if any(keyword in tweet.full_text for keyword in follow_keyword):
                                    follow = [tweet.user.screen_name, tweet.full_text]
                            if follow is not None:
                                if FollowQueue.put([(follow[0], follow[1])]) is True: # check if the fill is okay (aka no  duplicates)
                                    # Tweet Random quotes if there is any follow, in order to don't have too much random tweet
                                    try:
                                        for citation in urlopen('https://talaikis.com/api/quotes/random/'):
                                            randomTweet = json.loads(citation.decode('utf-8'))['quote']
                                        TweetQueue.put(randomTweet)
                                    except urllib.error.URLError:
                                        LOGGER.info("Error getting random tweet from API")
                process_queue()
            except tweepy.error.TweepError as tweepError:
                LOGGER.error(str(tweepError).encode('utf-8'))
                pass

