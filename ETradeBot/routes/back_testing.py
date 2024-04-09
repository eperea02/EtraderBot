import base64
import io
import pdb
import urllib

import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
from flask import Blueprint, current_app, render_template, request

back_testing = Blueprint("back_testing", __name__)


@back_testing.route("/strategy", methods=["GET"])
def strategy():
    symbol = request.args.get("symbol", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    host_url = request.host_url.rstrip("/")

    return render_template(
        "strategies/strategy.html",
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        host_url=host_url,
    )


@back_testing.route("/strategies", methods=["POST"])
def strategies():
    symbol = request.form.get("symbol")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    stock = yf.download(symbol, start=start_date, end=end_date)
    stock.drop("Adj Close", axis=1, inplace=True)
    stock["9_day"] = stock.Open.rolling(9).mean()
    stock["21_day"] = stock.Open.rolling(21).mean()
    stock["Return"] = np.log(stock.Close).diff()
    stock.dropna(inplace=True)

    with plt.style.context("ggplot"):
        plt.figure(figsize=(8, 6))
        plt.plot(stock.Close[-120:], label="stock")
        plt.plot(stock["9_day"][-120:], label="9-day")
        plt.plot(stock["21_day"][-120:], label="21-day")
        plt.legend(loc=2)
        plt.title("Stock Price and Moving Averages")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    moving_averages = urllib.parse.quote(base64.b64encode(img.read()).decode())

    stock["regime"] = np.where(stock["9_day"] > stock["21_day"], 1, -1)
    stock["strat_return"] = stock.Return * stock.regime

    with plt.style.context("ggplot"):
        plt.figure(figsize=(8, 6))
        plt.plot(np.exp(stock.strat_return.cumsum()), label="System")
        plt.plot(np.exp(stock.Return.cumsum()), label="Buy/Hold")
        plt.legend(loc=2)
        plt.title("Cumulative Return vs Buy and Hold")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    total_return = urllib.parse.quote(base64.b64encode(img.read()).decode())

    plot_html = render_template(
        "strategies/plot.html",
        moving_averages=moving_averages,
        total_return=total_return,
    )

    turbo = current_app.turbo

    if turbo.can_stream():
        return turbo.stream(
            turbo.update(plot_html, target="plot"),
        )

    return plot_html
