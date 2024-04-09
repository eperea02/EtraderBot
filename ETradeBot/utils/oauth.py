import os

from flask import session as flask_session
from rauth import OAuth1Session

from ETradeBot.utils.consts import consumer_key, consumer_secret, renew_session


def create_oauth_session():
    session = True if flask_session.get("access_token") else False
    if session:
        access_token = flask_session.get("access_token")
        access_token_secret = flask_session.get("access_token_secret")
        oauth_session = OAuth1Session(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
        response = oauth_session.get(renew_session)
        if response.status_code == 200:
            return oauth_session
        else:
            flask_session.clear()
            return None

    return None
