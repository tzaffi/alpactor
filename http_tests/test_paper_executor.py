from datetime import datetime, timedelta
import os
import time
import uuid

import ray

import pytest

import alpaca_trade_api.rest as alpaca_rest

from llama.trader import Trader, TradeExecutor, RemoteTradeExecutor

from tests.test_env import test_paper_env


@pytest.fixture(scope="module")
def ray_fixture():
    ray.init(num_cpus=1)
    yield None
    ray.shutdown()


# ######################### Direct Calls ######################### #


def get_paper_broker():
    return Trader()._ALPACA_PAPER


def test_is_paper():
    test_paper_env()

    assert os.environ.get("ENV") == "PAPER"

    assert os.environ.get("ALPACA_API_KEY_LIVE") == os.environ.get("ALPACA_API_KEY_PAPER")
    assert os.environ.get("ALPACA_API_SECRET_LIVE") == os.environ.get("ALPACA_API_SECRET_PAPER")

    broker = get_paper_broker()
    assert broker.is_live is False

    return broker


def test_init():
    paper_broker = test_is_paper()
    assert paper_broker.is_live is False
    teena = TradeExecutor(paper_broker)

    assert teena.broker == paper_broker
    return teena


def test_order_nonsensical_symbol():
    teena = test_init()

    with pytest.raises(alpaca_rest.APIError) as e:
        teena.order("buy", "NONSENSE12345678", 1)

    assert "NONSENSE12345678" in str(e.value)


def test_cancel_nonexisting_order():
    teena = test_init()
    non_existing_order_id = uuid.uuid4()
    cancellation = teena.cancel(external_order_id=non_existing_order_id)
    assert cancellation["cancelled"] is False
    assert non_existing_order_id == cancellation["external_order_id"]
    assert cancellation["api_error"]["message"] == f"order not found: {non_existing_order_id}"


def test_is_off_market_hours():
    teena = test_init()

    clock = teena.market_clock()
    next_open = clock["next_open"]
    assert clock["is_open"] is False

    window = next_open - datetime.now(next_open.tz)
    assert window > timedelta(minutes=15)

    is_open, delta = teena.market_open_and_toggle_delta()
    assert not is_open and delta > timedelta(minutes=15)


def test_order_then_cancel_off_market_hours():
    test_is_off_market_hours()

    teena = test_init()

    order = teena.order("buy", "EVOK", 1)
    time.sleep(0.5)
    cancellation = teena.cancel(order_bundle=order)
    assert cancellation["cancelled"] is True
    assert order["external_order_id"] == cancellation["external_order_id"]


# ######################### Ray-Remote Indirect Calls ######################### #


def test_remote_init(ray_fixture):
    paper_broker = test_is_paper()
    assert paper_broker.is_live is False
    teena = RemoteTradeExecutor.remote(paper_broker)

    assert ray.get(teena.__str__.remote()) == "TradeExecutor with Broker[Alpaca Trading Paper (QA)]"
    return teena


def test_remote_order_nonsensical_symbol(ray_fixture):
    teena = test_remote_init(ray_fixture)

    with pytest.raises(alpaca_rest.APIError) as e:
        ray.get(teena.order.remote("buy", "NONSENSE12345678", 1))

    assert "NONSENSE12345678" in str(e.value)


def test_remote_cancel_nonexisting_order(ray_fixture):
    teena = test_remote_init(ray_fixture)
    non_existing_order_id = uuid.uuid4()
    cancellation = ray.get(teena.cancel.remote(external_order_id=non_existing_order_id))
    assert cancellation["cancelled"] is False
    assert non_existing_order_id == cancellation["external_order_id"]
    assert (cancellation["api_error"])["message"] == f"order not found: {non_existing_order_id}"


def test_remote_is_off_market_hours(ray_fixture):
    teena = test_remote_init(ray_fixture)

    clock = ray.get(teena.market_clock.remote())
    next_open = clock["next_open"]
    assert clock["is_open"] is False

    window = next_open - datetime.now(next_open.tz)
    assert window > timedelta(minutes=15)

    is_open, delta = ray.get(teena.market_open_and_toggle_delta.remote())
    assert not is_open and delta > timedelta(minutes=15)


def test_remote_order_then_cancel_off_market_hours(ray_fixture):
    test_remote_is_off_market_hours(ray_fixture)

    teena = test_remote_init(ray_fixture)

    order = ray.get(teena.order.remote("buy", "EVOK", 1))
    time.sleep(0.5)
    cancellation = ray.get(teena.cancel.remote(order_bundle=order))
    assert cancellation["cancelled"] is True
    assert order["external_order_id"] == cancellation["external_order_id"]
