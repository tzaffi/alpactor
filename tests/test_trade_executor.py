import uuid

import alpaca_trade_api

from unittest.mock import patch, Mock, MagicMock

from llama.trader import TradeExecutor, Broker


def mock_init():
    mocked_api = MagicMock()
    with patch.object(alpaca_trade_api, "REST", Mock(wraps=alpaca_trade_api.REST)) as patched_REST:
        patched_REST.return_value = mocked_api

        broker = Broker("a", "b", "c", "d", "e", False)
        teena = TradeExecutor(broker)
    return mocked_api, patched_REST, broker, teena


def test_init():
    mocked_api, patched_REST, broker, teena = mock_init()

    assert teena.broker == broker
    assert teena.api == mocked_api
    patched_REST.assert_called_once_with(
        key_id=broker.api_key,
        secret_key=broker.api_secret,
        base_url=broker.api_url,
    )


def test_order():
    mocked_api, patched_REST, broker, teena = mock_init()

    mock_id = "yo mamma bear!!!!!"
    with patch.object(uuid, "uuid4", Mock(wraps=uuid.uuid4)) as patched_id:
        patched_id.return_value = mock_id

        teena.order(
            "buy",
            "IBM",
            1337,
        )

    mocked_api.submit_order.assert_called_once_with(
        side="buy",
        symbol="IBM",
        qty=1337,
        type="market",
        time_in_force="gtc",
        limit_price=None,
        stop_price=None,
        client_order_id=mock_id,
        order_class=None,
        take_profit=None,
        stop_loss=None,
        trail_price=None,
        trail_percent=None,
    )

    # with patch.object(
    #     alpaca_trade_api, "order", Mock(wraps=alpaca_trade_api.submit_order)
    # ) as patched_order:
    #     patched_order.return_value = mocked_order

    #     order = teena.order("buy", "IBM", 100)
    #     assert order == patched_order
