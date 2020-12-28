from abc import ABCMeta, abstractmethod, abstractclassmethod

import datetime
import json
import logging
import os


class LlamaABC(metaclass=ABCMeta):
    @abstractmethod
    def as_event_json(self) -> str:
        pass

    @classmethod
    @abstractclassmethod
    def from_event_json(cls, j: str, debug: bool = False):
        pass


class LlamaMixin:
    env_keys = [
        "KAFKA_HOST",
        "KAFKA_API_KEY",
        "KAFKA_API_SECRET",
        "ALPACA_API_KEY",
        "ALPACA_API_SECRET",
    ]

    json_excludes = ["env_vars", "env_keys", "json_excludes"]

    def __init__(self, event_json: str = None, **kwargs):
        self.env_vars = {k: os.environ.get(k) for k in LlamaMixin.env_keys}

        for k, v in kwargs.items():
            setattr(self, k, v)

        if event_json:
            self._hydrate_from_event_json(event_json)

        self.log(msg="initialized")

    def _hydrate_from_event_json(self, j: str):
        for k, v in json.loads(j).items():
            setattr(self, k, v)

    def as_dict(self) -> dict:
        return {
            k: v
            for k in set(dir(self)) - set(LlamaMixin.json_excludes)
            if not (k.startswith("_") or callable(v := getattr(self, k)))
        }

    @classmethod
    def from_event_json(cls, j: str):
        llama = cls.__new__(cls)
        super(cls, llama).__init__(event_json=j)
        return llama

    def as_event_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, default=str)

    def __str__(self) -> str:
        return self.as_event_json()

    def log(self, level: int = logging.INFO, msg: str = None):
        logging.log(level, "%s:[%s]<msg:%s>", type(self).__qualname__, self, msg)


class LlamaBase(LlamaMixin, LlamaABC):
    def add_timestamp(self):
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
