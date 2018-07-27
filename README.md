# TweetBot Contest

After seeing some article about making bot for contest, I decided to create mine. It's a first real project I made in Python. It's tested with python 3.5.3 and python 3.6. 

After some days of use I've reached a 2.5 score out of 5 (at the start it was near 4.8) in the Bot-O-Meter application (check if a twitter account could be a bot or not) : https://botometer.iuni.iu.edu/#!/


# Install
Python 3.5.3 or Python 3.6 (do not hesitate to test another version and tell me if it's works)

    $ cd /opt/
    $ git clone https://github.com/nathan30/TweetBotContest.git TweetBot
    $ sudo apt install python3-pip python3-setuptools
    $ sudo pip3 install wheel
    $ sudo pip3 install tweepy
    $ sudo pip3 install logzio-python-handler (not mandatory)

Don't forget to fill the data.json with all the API informations from the apps.twitter.com website

If you want to use https://logz.io/, just make an account and fill the logz.conf file with your token. If you want to use juste the log/contestBot.log file, just modify "log_file" into src/data.json 

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


