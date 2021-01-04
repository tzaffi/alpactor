import logging
import datetime
import json
import uuid
from typing import Callable

import llama.logger as logger
import llama.env as env


from llama.abstract_base import LlamaABC


class LlamaMixin:
    """
    To achieve "immutability" we are only allowing settattr
    through the parent class.
    CF: https://stackoverflow.com/questions/42452953/python-3-user-defined-immutable-class-objects
    """

    @classmethod
    def is_immutable(cls) -> bool:
        return True

    @classmethod
    def db_table_name(cls) -> str:
        return cls.__qualname__.lower()

    @classmethod
    def has_timestamp(cls) -> bool:
        return False

    @classmethod
    def table_id_maker(cls) -> Callable:
        return lambda: uuid.uuid4()

    def add_timestamp(self):
        ts = datetime.datetime.now(datetime.timezone.utc)
        super(LlamaMixin, self).__setattr__("created_at", ts)

    json_excludes = ["json_excludes"]

    def __setattr__(self, k, v):
        if self.is_immutable():
            raise AttributeError(f"{type(self)} cannot be modified")

        super(LlamaMixin, self).__setattr__(k, v)

    def __init__(self, event_json: str = None, env: str = None, **kwargs):
        if self.has_timestamp():
            self.add_timestamp()

        super(LlamaMixin, self).__setattr__("table_id", self.table_id_maker()())

        for k, v in kwargs.items():
            super(LlamaMixin, self).__setattr__(k, v)

        if event_json:
            self._hydrate_from_event_json(event_json)

        self.log(msg="initialized")

    def _hydrate_from_event_json(self, j: str):
        for k, v in json.loads(j).items():
            if k == "table_id":
                v = uuid.UUID(v)
            super(LlamaMixin, self).__setattr__(k, v)

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

    def __eq__(self, other: LlamaABC) -> bool:
        return str(self.table_id) == str(other.table_id)

    def log(self, level: int = logging.INFO, msg: str = None):
        logger.log(self, level=level, msg=msg)


class LlamaBase(LlamaMixin, LlamaABC):
    pass


env.setup()
