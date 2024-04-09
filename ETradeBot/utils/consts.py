import os

PREPROD = os.environ.get("PREPROD")

if PREPROD:
    print("IN PRE PRODUCTION MODE")
    consumer_key = os.environ.get("SANDBOX_CONSUMER_KEY")
    consumer_secret = os.environ.get("SANDBOX_CONSUMER_SECRET")
    base_url = "https://apisb.etrade.com"
else:
    consumer_key = os.environ.get("PROD_CONSUMER_KEY")
    consumer_secret = os.environ.get("PROD_CONSUMER_SECRET")
    base_url = "https://api.etrade.com"

renew_session = base_url + "/oauth/renew_access_token"
revoke_token_url = base_url + "/oauth/revoke_access_token"
request_token_url = base_url + "/oauth/request_token"
access_token_url = base_url + "/oauth/access_token"
