from abc import ABCMeta, abstractmethod, abstractclassmethod

import datetime
import json
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

    json_excludes = ["env_keys", "json_excludes"]

    def __init__(self, debug: bool = False):
        self._debug = debug
        self.env_vars = {k: os.environ.get(k) for k in LlamaMixin.env_keys}

    def as_dict(self) -> dict:
        return {
            k: v
            for k in set(dir(self)) - set(LlamaMixin.json_excludes)
            if not (k.startswith("_") or callable(v := getattr(self, k)))
        }

    def _hydrate_from_event_json(self, j: str):
        for k, v in json.loads(j).items():
            setattr(self, k, v)

    @classmethod
    def from_event_json(cls, j: str, debug: bool = False):
        llama = cls(debug=debug)
        llama._hydrate_from_event_json(j)
        return llama

    def as_event_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, default=str)


class LlamaBase(LlamaMixin, LlamaABC):
    @classmethod
    def ctor(cls, self, debug: bool = False):
        """
        Use this constructor function in the first line of any
        subclass __init__().

        EG:

        class Llaminizer(LlamaBase):
            def __init__(self, debug: bool = False, happy: bool = True):
                LlamaBase.ctor(self, debug=debug)
                self._happy = happy
        """
        super(LlamaMixin, self).__init__()
        self._debug = debug

    def add_timestamp(self):
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
