# TweetBot Contest

After seeing some article about making bot for contest, I decided to create mine. It's a first real project I made in Python. It's tested with python 3.5.3 and python 3.6. 


# Install
Python 3.5.3 or Python 3.6 (do not hesitate to test another version and tell me if it's works)

    $ cd /opt/
    $ git clone https://github.com/nathan30/TweetBotContest.git TweetBot
    $ sudo apt install python3-pip
    $ sudo pip install tweepy

# Functionality
Follow the people in the tweet (using regex on the @ char) if needed
Follow the tweet author
RT the tweet
Tweet random citations
Execute function randomly
You can parameter the bot using the src/data.json file (banned words, search keyword etc..)

## Explanations


I decided to use the Tweepy library. It's easy to use with an inbuilt rate limit. I implement a random choice to don't spam to much the follow, RT and tweet function. It tweet some random tweet using french citation from Kaamelot in order to don't have an account with only RT. 
The only "issue" is the retweeted filter. It doesn't work as expected so I made a little workaround using some tweet key. If you have some solution, don't hesitate to make a pull request. 


