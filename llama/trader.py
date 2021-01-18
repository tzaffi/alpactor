import alpaca_trade_api as tradeapi

from dataclasses import dataclass
import os
import uuid

from llama.base import LlamaBase
import llama.env as env


@dataclass
class Broker:
    name: str
    api_url: str
    data_url: str
    api_key: str
    api_secret: str
    is_live: bool
    broker_type: str = "alpaca"


class TradeExecutor:
    def __init__(self, broker: Broker):
        self.broker = broker
        assert self.broker.broker_type == "alpaca"
        self.api = tradeapi.REST(
            key_id=self.broker.api_key,
            secret_key=self.broker.api_secret,
            base_url=self.broker.api_url,
        )

    def order(self, side: str, symbol: str, qty: int):
        """
        Basing off of: https://alpaca.markets/docs/api-documentation/api-v2/orders/
        """
        assert self.broker.broker_type == "alpaca"
        order = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": "market",  # TODO: will need to add more choices, starting with this
            "time_in_force": "gtc",
            "limit_price": None,
            "stop_price": None,
            "client_order_id": uuid.uuid4(),
            "order_class": None,
            "take_profit": None,
            "stop_loss": None,
            "trail_price": None,
            "trail_percent": None,
        }
        resp_order = self.api.submit_order(**order)
        return {"order": order, "response": resp_order}


class Trader(LlamaBase):
    """
    Immutable, json-izable class with a timestamp
    """

    @classmethod
    def has_timestamp(cls) -> bool:
        return True

    @classmethod
    def db_table_name(cls) -> str:
        return "trader"

    @classmethod
    def is_immutable(cls) -> bool:
        return False

    _ALPACA_PAPER = Broker(
        name="Alpaca Trading Paper",
        api_url="https://paper-api.alpaca.markets",
        data_url="https://data.alpaca.markets/",
        api_key=os.environ.get(env.ALPACA_API_KEY_PAPER),
        api_secret=os.environ.get(env.ALPACA_API_SECRET_PAPER),
        is_live=False,
    )

    _ALPACA_LIVE = Broker(
        name="Alpaca Trading Live",
        api_url="https://paper-api.alpaca.markets",
        data_url="https://data.alpaca.markets/",
        api_key=os.environ.get(env.ALPACA_API_KEY_LIVE),
        api_secret=os.environ.get(env.ALPACA_API_SECRET_LIVE),
        is_live=True,
    )

    def __init__(self):
        """
        Two layers of protection against trading live in a testing context:
        1. Only .live.env has Alpaca's live credentials
        2. Set self.brokers["alpaca_live"] to the paper broker in non-live contexts
        """
        self._brokers = {
            "alpaca_paper": self._ALPACA_PAPER,
        }
        self._brokers["alpaca_live"] = self._ALPACA_LIVE if env.is_live() else self._ALPACA_PAPER
