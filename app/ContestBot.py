import tweepy
import json
from urllib.request import urlopen
import logging
import re
import queue
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
    banned_user = data['banned_user']
    banned_words = data['banned_words']
    follow_keyword = data['follow-keyword']
    log_file = data['log_file']
    nb_tweets = data['nb_tweets_search']

# Set logger | DEBUG takes all log type | WARNING takes all log type except .info
LOGGER = logging.getLogger('ContestBot')
logFile = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logFile.setFormatter(formatter)
LOGGER.addHandler(logFile)
LOGGER.setLevel(logging.DEBUG)


def follow_user():
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
            except tweepy.error.TweepError as tweepError:
                LOGGER.error(str(tweepError).encode('utf-8'))
                break
            LOGGER.info('Follow user : ' + user)


def retweet():
    RT_id = RTQueue.get()
    try:
        api.retweet(RT_id)
    except tweepy.error.TweepError as tweepError:  # Workaround
        LOGGER.error(str(tweepError).encode('utf-8'))  # Because the key Retweeted
        pass  # isn't work and always set as False, so we can never check if the tweet already retweeted


def update_status():
    updated_tweet = TweetQueue.get()
    try:
        api.update_status(updated_tweet)
        LOGGER.info('Tweet random stuff')
    except tweepy.error.TweepError as tweepError:
        LOGGER.error(str(tweepError).encode('utf-8'))
        pass


def process_queue():
    queue_list = [retweet, follow_user, update_status]
    while RTQueue.empty() is not True and FollowQueue.empty() is not True and TweetQueue.empty is not True:  # Empty the Queues randomly
        choice(queue_list)()
        LOGGER.info("Let's go slepping for a while")
        sleep(randint(100, 500))  # Wait in order to don't spam too much

if __name__ == '__main__':
    # OAuth to Twitter and get Api object
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

    RTQueue = queue.Queue()  # Queue used to RT things one by one after a given time
    TweetQueue = queue.Queue()  # Same for random tweets
    FollowQueue = queue.Queue()  # Same for follow people

    # Start contest spamming process
    while True:
        for keyword in search_keyword:
            tweetsList = tweepy.Cursor(
                api.search,
                q=keyword,  # search query is case insensitive
                lang=lang,
                tweet_mode="extended",
                result_type="recent",
            ).items(int(nb_tweets))

            for tweet in tweetsList:
                isRT = hasattr(tweet, 'retweeted_status')  # Check if it's a RT
                if not tweet.is_quote_status and not tweet.in_reply_to_status_id and not any(word for word in banned_words if word in tweet.full_text.lower()):  # Do net process quoted status and response of a tweet
                    if not tweet.retweeted:  # Check you didn't already RT this tweet (not working for now)
                        if isRT:
                            rt = tweet.retweeted_status.id
                        else:
                            rt = tweet.id
                        RTQueue.put(rt)

                        # Search follow keyword
                        if isRT:
                            if any(keyword in tweet.retweeted_status.full_text for keyword in follow_keyword):
                                follow = [tweet.retweeted_status.user.screen_name, tweet.retweeted_status.full_text]
                        else:
                            if any(keyword in tweet.full_text for keyword in follow_keyword):
                                follow = [tweet.user.screen_name, tweet.full_text]
                        if follow is not None:
                            FollowQueue.put([(follow[0], follow[1])])

                        # Tweet Random quotes
                        for citation in urlopen('https://kaamelott.chaudie.re/api/random'):
                            randomTweet = json.loads(citation.decode('utf-8'))['citation']['citation']
                        #randomTweet = json.load(urlopen('https://kaamelott.chaudie.re/api/random').decode('utf-8'))['citation']['citation']
                        TweetQueue.put(randomTweet)
            process_queue()
