import os
import pdb

import flask
from dotenv import load_dotenv
from flask import g, request
from flask import session as flask_session
from rauth import OAuth1Service, OAuth1Session
from turbo_flask import Turbo

from ETradeBot.routes.back_testing import \
    back_testing as back_testing_blueprint
from ETradeBot.routes.place_order import place_order as place_order_blueprint
from ETradeBot.utils.accounts import Accounts
from ETradeBot.utils.consts import (access_token_url, base_url, consumer_key,
                                    consumer_secret, request_token_url,
                                    revoke_token_url)
from ETradeBot.utils.market import Market
from ETradeBot.utils.oauth import create_oauth_session
from ETradeBot.utils.order import Order

load_dotenv()


def create_app():  # noqa C901

    etrade = OAuth1Service(
        name="etrade",
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        request_token_url=request_token_url,
        access_token_url=access_token_url,
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url=base_url,
    )
    app = flask.Flask(__name__)
    app.secret_key = os.environ.get("PROD_CONSUMER_KEY")
    turbo = Turbo(app)
    app.turbo = turbo
    app.register_blueprint(place_order_blueprint)
    app.register_blueprint(back_testing_blueprint)

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
        if flask.request.endpoint in ["index", "authorize", "session", "callback"]:
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
        oauth_session = g.get("oauth_session")
        oauth_session.get(revoke_token_url)
        flask_session.clear()
        return flask.redirect(flask.url_for("index"))

    @app.route("/market_data", methods=["POST"])
    def market_data():
        symbols = request.form.get("symbols")  # if data is sent as form data
        oauth_session = g.get("oauth_session")
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

    @app.route("/callback", methods=["GET"])
    def callback():
        text_code = request.args.get("oauth_verifier")
        oauth_session = etrade.get_auth_session(
            request_token,
            request_token_secret,
            params={"oauth_verifier": text_code},
        )
        flask_session["access_token"] = oauth_session.access_token
        flask_session["access_token_secret"] = oauth_session.access_token_secret
        html = flask.render_template("session/home_page_with_session.html")

        if turbo.can_stream():
            return turbo.stream(turbo.update(html, target="appbody"))

        return html

    @app.route("/authorize")
    def authorize():
        return flask.redirect(authorize_url)

    @app.route("/accounts")
    def accounts():
        oauth_session = g.get("oauth_session")
        account = Accounts(oauth_session, base_url)
        accounts_json = account.account_list(format="json")
        accounts_data = accounts_json["AccountListResponse"]["Accounts"]["Account"]
        return flask.render_template(
            "accounts/accounts.html", accounts_data=accounts_data
        )

    @app.route("/session_account_selected", methods=["POST"])
    def session_account_selected():
        accountId = request.form.get("accountId")
        flask_session["accountId"] = accountId
        oauth_session = g.get("oauth_session")
        account = Accounts(oauth_session, base_url)
        accounts_json = account.account_list(format="json")
        accounts_data = accounts_json["AccountListResponse"]["Accounts"]["Account"]

        for acc in accounts_data:
            if acc["accountId"] == accountId:
                account.account = acc
                break

        balance = account.balance(format="json")
        accdata = [
            f"Account ID: {account.account['accountId']}",
            f"Account Name: {account.account['accountName']}",
            f"Account Description: {account.account['accountDesc']}",
            f"Account Type: {account.account['accountType']}",
            f"Balance: { balance['BalanceResponse']['Cash']['moneyMktBalance'] }",
        ]

        account_html = flask.render_template(
            "orders/data_card.html",
            title="Account Info:",
            data=accdata,
            tag="session_account_selected",
        )

        if turbo.can_stream():
            return turbo.stream(
                turbo.update(account_html, target="session_account_selected")
            )

        return account_html

    @app.route("/accounts_data", methods=["POST"])
    def accounts_data():
        oauth_session = g.get("oauth_session")
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
