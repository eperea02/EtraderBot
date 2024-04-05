import os
import pdb

import flask
from flask import request
from flask import session as flask_session
from rauth import OAuth1Service, OAuth1Session
from turbo_flask import Turbo

from ETradeBot.utils.accounts import Accounts
from ETradeBot.utils.consts import revoke_token_url
from ETradeBot.utils.market import Market
from ETradeBot.utils.oauth import create_oauth_session
from ETradeBot.utils.order import Order


def create_app():  # noqa C901

    etrade = OAuth1Service(
        name="etrade",
        consumer_key=os.environ.get("PROD_CONSUMER_KEY"),
        consumer_secret=os.environ.get("PROD_CONSUMER_SECRET"),
        request_token_url="https://api.etrade.com/oauth/request_token",
        access_token_url="https://api.etrade.com/oauth/access_token",
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url="https://api.etrade.com/v1/",
    )
    app = flask.Flask(__name__)
    app.secret_key = os.environ.get("PROD_CONSUMER_KEY")
    turbo = Turbo(app)

    request_token, request_token_secret = etrade.get_request_token(
        params={"oauth_callback": "oob", "format": "json"}
    )
    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)

    def render_authenticate():
        html = flask.render_template("authenticate.html")
        if turbo.can_stream():
            return turbo.stream(turbo.update(html, target="appbody"))

        return flask.render_template("index.html")

    @app.before_request
    def before_request():
        if flask.request.endpoint in ["index", "authorize", "session"]:
            return

        oauth_session = create_oauth_session()
        if not oauth_session:
            return flask.redirect(flask.url_for("index"))

        flask.g.oauth_session = oauth_session

    @app.route("/")
    def index():
        session = create_oauth_session()
        if session:
            return flask.render_template("session/home_page_with_session.html")
        return flask.render_template("index.html")

    @app.route("/logout")
    def logout():
        oauth_session = flask.g.get("oauth_session")
        oauth_session.get(revoke_token_url)
        flask_session.clear()
        return flask.redirect(flask.url_for("index"))

    @app.route("/market_data", methods=["POST"])
    def market_data():
        symbols = request.form.get("symbols")  # if data is sent as form data
        oauth_session = flask.g.get("oauth_session")

        base_url = os.environ.get("PROD_BASE_URL")
        market = Market(oauth_session, base_url)
        quote_data = market.quotes(symbols=symbols, format="json")

        html = flask.render_template(
            "quote_data.html", quote_data=quote_data, symbols=symbols
        )
        if turbo.can_stream():
            return turbo.stream(turbo.update(html, target="quote_data"))

        return html

    @app.route("/market")
    def market():
        return flask.render_template("market.html")

    @app.route("/session", methods=["POST"])
    def session():
        text_code = request.form.get("text_code")  # if data is sent as form data
        oauth_session = etrade.get_auth_session(
            request_token,
            request_token_secret,
            params={"oauth_verifier": text_code},
        )
        flask_session["access_token"] = oauth_session.access_token
        flask_session["access_token_secret"] = oauth_session.access_token_secret
        html = flask.render_template("session/success.html")

        if turbo.can_stream():
            return turbo.stream(turbo.update(html, target="appbody"))

        return html

    @app.route("/authorize")
    def authorize():
        return flask.redirect(authorize_url)

    @app.route("/accounts")
    def accounts():
        return flask.render_template("accounts/accounts.html")

    @app.route("/accounts_data", methods=["POST"])
    def accounts_data():
        oauth_session = flask.g.get("oauth_session")
        base_url = os.environ.get("PROD_BASE_URL")
        account = Accounts(oauth_session, base_url)
        accounts_data = account.account_list(format="json")

        account.account = accounts_data["AccountListResponse"]["Accounts"]["Account"][0]
        balance = account.balance(format="json")
        portfolio = account.portfolio(format="json")

        # order = Order(oauth_session, account.account, base_url)
        # order.view_orders()

        html = flask.render_template(
            "accounts/accounts_data.html",
            accounts_data=accounts_data,
            balance=balance,
            portfolio=portfolio,
        )
        if turbo.can_stream():
            return turbo.stream(turbo.update(html, target="accounts_data"))

        return html

    return app


app = create_app()
