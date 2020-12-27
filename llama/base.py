from abc import ABCMeta, abstractmethod, abstractclassmethod

import json
import os


class LlamaABC(metaclass=ABCMeta):
    @abstractmethod
    def as_event_json(self) -> str:
        pass

    @classmethod
    @abstractclassmethod
    def from_event_json(cls, j: str):
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

    def __init__(self):
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
    def from_event_json(cls, j: str):
        llama = cls()
        llama._hydrate_from_event_json(j)
        return llama

    def as_event_json(self) -> str:
        return json.dumps(self.as_dict())


class LlamaBase(LlamaMixin, LlamaABC):
    def __init__(self):
        super(self, LlamaMixin)
