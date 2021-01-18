import alpaca_trade_api

from unittest.mock import patch, Mock

from llama.trader import TradeExecutor, Trader, Broker


def test_init():
    tony = Trader()
    assert not tony.is_immutable()


def test_brokers():
    tony = Trader()
    assert set(tony._brokers.keys()) == {"alpaca_paper", "alpaca_live"}
    for b in tony._brokers.values():
        assert isinstance(b, Broker)


# def test_buy():
#     mocked_order = "this is a mocking order!!!!"

#     tony = Trader()
#     with patch.object(
#         alpaca_trade_api, "order", Mock(wraps=alpaca_trade_api.order)
#     ) as patched_order:
#         patched_order.return_value = mocked_order

#         orders = tony.buy("IBM", 100)

#         assert order == {
#             "alpaca_paper": mocked_order,
#         }
