import os


class Session:
    etrade = None


consumer_key = os.environ.get("PROD_CONSUMER_KEY")
consumer_secret = os.environ.get("PROD_CONSUMER_SECRET")
renew_session = "https://api.etrade.com/oauth/renew_access_token"
revoke_token_url = "https://api.etrade.com/oauth/revoke_access_token"
