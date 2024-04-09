import configparser
import json
import logging
from logging.handlers import RotatingFileHandler

from ETradeBot.utils.consts import consumer_key
from ETradeBot.utils.order import Order

# loading configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# logger settings
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    "python_client.log", maxBytes=5 * 1024 * 1024, backupCount=3
)
FORMAT = "%(asctime)-15s %(message)s"
fmt = logging.Formatter(FORMAT, datefmt="%m/%d/%Y %I:%M:%S %p")
handler.setFormatter(fmt)
logger.addHandler(handler)


class Accounts:
    def __init__(self, session, base_url):
        """
        Initialize Accounts object with session and account information

        :param session: authenticated session
        """
        self.session = session
        self.account = {}
        self.base_url = base_url

    def account_list(self, format=None):
        """
        Calls account list API to retrieve a list of the user's E*TRADE accounts
        :param self:Passes in parameter authenticated session
        """
        url = self.base_url + "/v1/accounts/list.json"

        # Make API call for GET request
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )

            data = response.json()
            return data

    def portfolio(self, format=None):
        """
        Call portfolio API to retrieve a list of positions held in the specified account
        :param self: Passes in parameter authenticated session and information on selected account
        """

        # URL for the API endpoint
        url = (
            self.base_url
            + "/v1/accounts/"
            + self.account["accountIdKey"]
            + "/portfolio.json"
        )

        # Make API call for GET request
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)

            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )
            data = response.json()
            return data

    def balance(self, format=None):
        """
        Calls account balance API to retrieve the current balance and related details for a specified account
        :param self: Pass in parameters authenticated session and information on selected account
        """
        url = (
            self.base_url
            + "/v1/accounts/"
            + self.account["accountIdKey"]
            + "/balance.json"
        )

        # Add parameters and header information
        params = {"instType": self.account["institutionType"], "realTimeNAV": "true"}
        headers = {"consumerkey": consumer_key}

        # Make API call for GET request
        response = self.session.get(
            url, header_auth=True, params=params, headers=headers
        )
        logger.debug("Request url: %s", url)
        logger.debug("Request Header: %s", response.request.headers)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )
            data = response.json()
            return data
