import pdb
import uuid

from flask import Blueprint, current_app, g, render_template, request
from flask import session as flask_session

from ETradeBot.utils.accounts import Accounts
from ETradeBot.utils.consts import base_url
from ETradeBot.utils.order import Order

place_order = Blueprint("place_order", __name__)


@place_order.route("/placeorder", methods=["GET"])
def placeorder():
    accountId = flask_session.get("accountId")
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

    account_html = render_template(
        "orders/data_card.html", title="Account Info:", data=accdata, tag="account_data"
    )

    order_html = render_template(
        "orders/order_form.html",
        accountId=account.account["accountId"],
        client_order_id=str(uuid.uuid4()),
    )

    return render_template(
        "orders/place_order.html", account_html=account_html, order_html=order_html
    )


@place_order.route("/preview_order", methods=["POST"])
def preview_order():
    order_request = {
        "client_order_id": request.form.get("client_order_id"),
        "price_type": request.form.get("price_type"),
        "order_term": request.form.get("order_term"),
        "symbol": request.form.get("symbol"),
        "order_action": request.form.get("order_action"),
        "limit_price": request.form.get("limit_price"),
        "quantity": request.form.get("quantity"),
    }

    oauth_session = g.get("oauth_session")
    account = Accounts(oauth_session, base_url)
    accounts_json = account.account_list(format="json")
    accounts_data = accounts_json["AccountListResponse"]["Accounts"]["Account"]
    account.account = accounts_json["AccountListResponse"]["Accounts"]["Account"][0]

    for acc in accounts_data:
        if acc["accountId"] == request.form.get("accountId"):
            account.account = acc
            break

    order = Order(oauth_session, account.account, base_url)
    response = order.preview_order(order=order_request)

    data = response.json()

    order_result_html = render_template(
        "orders/data_json_card.html", title="Order Result:", data=data, tag="balance"
    )

    turbo = current_app.turbo

    if turbo.can_stream():
        return turbo.stream(
            turbo.update(order_result_html, target="order_result"),
        )

    return render_template("index.html")
