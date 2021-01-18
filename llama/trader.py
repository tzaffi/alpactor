import alpaca_trade_api as tradeapi
import alpaca_trade_api.rest as alpaca_rest

from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import uuid
from typing import Tuple

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

    def order(self, side: str, symbol: str, qty: int) -> dict:
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
            "client_order_id": str(uuid.uuid4()),
            "order_class": None,
            "take_profit": None,
            "stop_loss": None,
            "trail_price": None,
            "trail_percent": None,
        }
        resp_order = self.api.submit_order(**order)
        return {
            "external_order_id": uuid.UUID(resp_order.id),
            "order": order,
            "response": resp_order,
        }

    def cancel(self, external_order_id: uuid.UUID = None, order_bundle: dict = None) -> dict:
        assert (
            external_order_id or order_bundle
        ), "Can't cancel an order if you didn't tell me which one"
        if not external_order_id:
            external_order_id = order_bundle["external_order_id"]
        order_id = str(external_order_id)
        try:
            self.api.cancel_order(order_id)
            return {
                "external_order_id": external_order_id,
                "cancelled": True,
            }
        except alpaca_rest.APIError as e:
            return {
                "external_order_id": external_order_id,
                "cancelled": False,
                "api_error": e,
            }

    def market_clock(self) -> alpaca_rest.Clock:
        return self.api.get_clock()

    def market_open_and_toggle_delta(self) -> Tuple[bool, timedelta]:
        clock = self.market_clock()
        is_open = clock.is_open
        next_toggle = min(clock.next_close, clock.next_open)
        window = next_toggle - datetime.now(next_toggle.tz)
        return is_open, window


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

    def _set_brokers(self):
        self._ALPACA_PAPER = Broker(
            name="Alpaca Trading Paper",
            api_url="https://paper-api.alpaca.markets",
            data_url="https://data.alpaca.markets/",
            api_key=os.environ.get(env.ALPACA_API_KEY_PAPER),
            api_secret=os.environ.get(env.ALPACA_API_SECRET_PAPER),
            is_live=False,
        )

        self._ALPACA_LIVE = Broker(
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
        self._set_brokers()
        self._brokers = {
            "alpaca_paper": self._ALPACA_PAPER,
        }
        self._brokers["alpaca_live"] = self._ALPACA_LIVE if env.is_live() else self._ALPACA_PAPER
