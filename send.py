import random
import os
import time
from twilio.rest import Client
from tweets import all_eligible_tweets, format_url

twilio_client = Client(
    os.environ['TWILIO_ACCOUNT_SID'],
    os.environ['TWILIO_AUTH_TOKEN'])

def send_welcome_text(user):
    body = "Thank you for joining Support #transcrowdfund. Reply STOP at any time to stop receiving notifications. You can update settings by refilling the form on http://supporttranscrowdfund.com. Here's an immediate tweet to get you started."
    _send_impl(body, user.phone_number)

    time.sleep(2)

    tweet = random.choice(all_eligible_tweets())
    send_tweet(user, tweet)

def send_update_text(user):
    _send_impl("Your account has been updated. Thank you for your support, it makes a real difference.", user.phone_number)

def send_tweet(user, tweet):
    body = "{} {}".format(tweet['text'], format_url(tweet['url']))
    _send_impl(body, user.phone_number)

def _send_impl(body, number):
    twilio_client.messages.create(
        body=body
        from_=os.environ['TWILIO_PHONE_NUMBER'],
        to=number)

