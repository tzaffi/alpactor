import alpaca_trade_api

import uuid


from unittest.mock import patch, Mock, MagicMock

from llama.trader import TradeExecutor, Broker
from llama.alpaca_entity import AlpacaError, AlpacaEntity


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

    mock_id = uuid.uuid4()
    with patch.object(uuid, "uuid4", Mock(wraps=uuid.uuid4)) as patched_id:
        patched_id.return_value = mock_id
        mocked_response = alpaca_trade_api.entity.Entity({"id": str(mock_id)})
        teena.api.submit_order.return_value = mocked_response

        order = teena.order(
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
        client_order_id=str(mock_id),
        order_class=None,
        take_profit=None,
        stop_loss=None,
        trail_price=None,
        trail_percent=None,
    )

    assert order == {
        "external_order_id": mock_id,
        "order": {
            "side": "buy",
            "symbol": "IBM",
            "qty": 1337,
            "type": "market",
            "time_in_force": "gtc",
            "limit_price": None,
            "stop_price": None,
            "client_order_id": str(mock_id),
            "order_class": None,
            "take_profit": None,
            "stop_loss": None,
            "trail_price": None,
            "trail_percent": None,
        },
        "response": {"id": str(mock_id)},
    }


def test_cancel():
    def happy():
        mocked_api, patched_REST, broker, teena = mock_init()

        mock_id = "yo mamma bear!!!!!"
        teena.api.cancel_order.return_value = None

        cancellation = teena.cancel(mock_id)
        assert cancellation == {
            "external_order_id": mock_id,
            "cancelled": True,
        }

    def api_error():
        mocked_api, patched_REST, broker, teena = mock_init()

        mock_id = "yo mamma bear!!!!!"
        mock_err = alpaca_trade_api.rest.APIError({"message": "some error", "code": "some code"})
        teena.api.cancel_order.side_effect = mock_err

        cancellation = teena.cancel(mock_id)
        assert cancellation == {
            "external_order_id": mock_id,
            "cancelled": False,
            "api_error": AlpacaError(mock_err).as_dict(),
        }

    happy()
    api_error()


def test_market_clock():
    mocked_api, patched_REST, broker, teena = mock_init()

    mocked_clock = alpaca_trade_api.entity.Entity({"time": "tick tock tick tock 5 O'clock"})
    teena.api.get_clock.return_value = mocked_clock

    clock = teena.market_clock()

    mocked_api.get_clock.assert_called_once_with()

    assert clock == AlpacaEntity(mocked_clock).as_dict()
