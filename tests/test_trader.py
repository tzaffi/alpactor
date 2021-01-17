import dataclasses
from llama.trader import Trader, Broker


def test_init():
    tony = Trader()
    assert not tony.is_immutable()


def test_brokers():
    tony = Trader()
    assert set(tony._brokers.keys()) == {"alpaca_paper", "alpaca_live"}
    for b in tony._brokers.values():
        assert isinstance(b, Broker)
