import pandas as pd

from unittest.mock import MagicMock

from alpaca_trade_api.entity import Entity
from alpaca_trade_api.rest import APIError

from llama.alpaca_entity import AlpacaEntity, AlpacaError


def test_entity_as_dict():
    raw = {"created_at": "2018-04-01T12:00:00.000Z", "symbol": "IBM", "qty": 400, "price": 128.7324}

    entity = Entity(raw)
    assert entity.symbol == "IBM"
    assert entity.qty == 400
    assert entity.price == 128.7324

    assert entity.created_at == pd.Timestamp("2018-04-01T12:00:00.000Z")

    as_dict = AlpacaEntity(entity).as_dict()
    assert as_dict["symbol"] == entity.symbol
    assert as_dict["qty"] == entity.qty
    assert as_dict["price"] == entity.price

    assert as_dict["created_at"] == entity.created_at


def test_api_error_as_dict():
    error = {"message": "some message", "code": "some code"}

    request = "some request"
    response = MagicMock(status_code="some status code")
    http_error = MagicMock(request=request, response=response)

    api_error = APIError(error, http_error=http_error)
    assert api_error.code == "some code"
    assert api_error.status_code == "some status code"
    assert api_error.request == "some request"
    assert api_error.response == response

    as_dict = AlpacaError(api_error).as_dict()
    assert api_error.code == as_dict["code"]
    assert api_error.status_code == as_dict["status_code"]
    assert api_error.request == as_dict["request"]
    assert api_error.response == as_dict["response"]
