import twitter
import re
import random
import requests
import os
from urllib.parse import urlparse, quote
from twilio.rest import Client

AMOUNT = 20

def get_url_domain(url):
  parsed = urlparse(url.expanded_url)
  return parsed.netloc.lower().replace("www.", "")

def is_cash_app_url(url):
  return get_url_domain(url) in ['cash.app', 'cash.me']

def is_paypal_url(url):
  return get_url_domain(url) == 'paypal.me'

def is_valid_url(url):
  return get_url_domain(url) in ['cash.app', 'cash.me', 'paypal.me']

def send_tweet():
  twitter_client = twitter.Api(
      consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
      consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
      access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
      access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
      tweet_mode='extended')

  twilio_client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

  search = twitter_client.GetSearch("#transcrowdfund -filter:nativeretweets", result_type="recent", count=50, include_entities=True)

  relevant_tweets = [t for t in search if any([is_valid_url(u) for u in t.urls])]

  eligible = []
  for t in relevant_tweets:
    stripped_text = re.sub('https://t.co/\w+', '', t.full_text).replace("\n", " ")
    stripped_text = re.sub('\s+', ' ', stripped_text)
    url = next(u for u in t.urls if is_valid_url(u))
    if is_paypal_url(url):
      parsed = urlparse(url.expanded_url)
      username = parsed.path[1:]
      url = "https://www.paypal.com/myaccount/transfer/send/external/ppme?profile={}&currencyCode=USD&amount={}&locale.x=en_US&country.x=US&flowType=send".format(username, AMOUNT)
      r = requests.post("https://api-ssl.bitly.com/v4/shorten", headers={"Authorization": "Bearer "+os.environ["BITLY_AUTH_TOKEN"]}, json={"long_url": url})
      url = r.json()['link']
    elif is_cash_app_url(url):
      url = "{}/{}".format(url.expanded_url, AMOUNT)
    else:
      url = url.expanded_url
    eligible.append("{} {}".format(stripped_text, url))

  twilio_client.messages.create(body=random.choice(eligible), from_=os.environ['TWILIO_PHONE_NUMBER'], to="+14157067865")

if __name__== "__main__":
  send_tweet()

