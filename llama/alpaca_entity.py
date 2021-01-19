from alpaca_trade_api.entity import Entity
from alpaca_trade_api.rest import APIError


class AlpacaEntity:
    def __init__(self, entity: Entity):
        self.entity = entity

    def as_dict(self) -> dict:
        return {k: getattr(self.entity, k) for k in self.entity._raw}


class AlpacaError:
    def __init__(self, api_error: APIError):
        self.api_error = api_error

    def as_dict(self) -> dict:
        res = {
            prop: getattr(self.api_error, prop)
            for prop in ["code", "status_code", "request", "response"]
        }
        res["message"] = str(self.api_error)
        return res
