import twitter
import re
import requests
import os
from urllib.parse import urlparse


def all_eligible_tweets():
    twitter_client = twitter.Api(
        consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
        consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
        access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
        tweet_mode='extended')

    search = twitter_client.GetSearch(
        "#transcrowdfund -filter:nativeretweets",
        result_type="recent",
        count=50,
        include_entities=True)

    eligible = []
    for t in search:
        url = next((u for u in t.urls if _is_valid_url(u)), None)
        if url:
            eligible.append({
                "text": _strip_text(t.full_text),
                "url": url,
            })
    return eligible


def format_url(url, user):
    if _is_paypal_url(url):
        parsed = urlparse(url.expanded_url)
        username = parsed.path[1:]
        url = "https://www.paypal.com/myaccount/transfer/send/external/ppme?profile={}&currencyCode=USD&amount={}&locale.x=en_US&country.x=US&flowType=send&note=%23transcrowdfund".format(
            username, user.amount)
        r = requests.post(
            "https://api-ssl.bitly.com/v4/shorten",
            headers={
                "Authorization": "Bearer " +
                os.environ["BITLY_AUTH_TOKEN"]},
            json={
                "long_url": url})
        return r.json()['link']
    elif _is_cash_app_url(url):
        return "{}/{}".format(url.expanded_url, user.amount)
    else:
        return url.expanded_url


def _strip_text(text):
    stripped_text = re.sub(r'https://t.co/\w+', '', text).replace("\n", " ")
    stripped_text = re.sub(r'\s+', ' ', stripped_text)
    return stripped_text


def _get_url_domain(url):
    parsed = urlparse(url.expanded_url)
    return parsed.netloc.lower().replace("www.", "")


def _is_cash_app_url(url):
    return _get_url_domain(url) in ['cash.app', 'cash.me']


def _is_paypal_url(url):
    return _get_url_domain(url) == 'paypal.me'


def _is_valid_url(url):
    return _get_url_domain(url) in ['cash.app', 'cash.me', 'paypal.me']
