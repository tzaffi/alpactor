from dataclasses import dataclass
import os

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
