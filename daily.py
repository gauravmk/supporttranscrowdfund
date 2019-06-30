from tweets import all_eligible_tweets
from app import User, Frequency
from send import send_tweet
import datetime
import random


def send_tweets():
    all_tweets = all_eligible_tweets():
    weekday = datetime.datetime.today().weekday()
    if weekday == 0:
        all_users = User.query.all()
    elif weekday == 2 or weekday == 4:
        all_users = User.query.filter(User.frequency != Frequency.Weekly).all()
    else:
        all_users = User.query.filter(User.frequency == Frequency.Daily).all()
    random.shuffle(all_tweets)
    for i, user in enumerate(all_users):
        tweet = all_tweets[i % len(all_tweets)]
        send_tweet(user, tweet)


if __name__ == "__main__":
    send_tweets()
