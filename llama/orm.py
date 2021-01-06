import os
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, DateTime
from sqlalchemy import insert as sqla_insert, select as sqla_select
from sqlalchemy.future import Engine
from sqlalchemy.sql import func
from typing import Sequence, Type, Dict
from uuid import UUID

import llama.env as env
from llama.abstract_base import LlamaABC


def engine(db_uri: str = None, echo: bool = True) -> Engine:
    if db_uri is None:
        db_uri = os.environ.get("DB_URI")

    return create_engine(db_uri, echo=echo, future=True)


class ORM:
    def __init__(self, eng: Engine = None, db_uri: str = None, variant="sqlite", echo: bool = True):
        assert variant == "sqlite", "Currently can only handle SQLite"

        assert not (engine and db_uri), "If you specify the engine, please don't give a DB URI"

        self.engine = engine(db_uri=db_uri, echo=echo) if eng is None else eng

        self.metadata = MetaData()

        self.tables = {}

    def add_table(self, model: Type, *columns: Sequence[Column]) -> Table:
        assert issubclass(model, LlamaABC), f"Don't know how to model a non-Llama type {model}"

        self.tables[model] = Table(
            model.db_table_name(),
            self.metadata,
            Column("id", String(36), primary_key=True),  # should use native uuid type for postgres
            Column("saved_at", DateTime(timezone=True), server_default=func.now()),
            Column("event", JSON, nullable=False),
            *columns,
        )
        return self.tables[model]

    def bootstrap_db(self):
        self.metadata.create_all(self.engine, checkfirst=True)

    exclude_columns = ["saved_at"]

    def transform(self, obj: LlamaABC) -> dict:
        d = obj.as_dict()
        d["event"] = obj.as_event_json()
        d["id"] = str(d["table_id"])

        return {
            name: d[name] for col in self.tables[type(obj)].columns if (name := col.name) not in ORM.exclude_columns
        }

    def insert(self, model: Type, *objs: Sequence[LlamaABC]):
        assert issubclass(model, LlamaABC), f"Don't know how to model a non-Llama type {model}"
        assert model in self.tables, f"Model {model} never got added as an ORM table (don't forget 'add_table()')"
        assert objs, "Gotta have at least one object to insert"
        for obj in objs:
            assert isinstance(obj, model), f"obj is of type {type(obj)} but should be of type {model}"

        with self.engine.begin() as transaction:
            transaction.execute(sqla_insert(self.tables[model], [self.transform(obj) for obj in objs]))

    def hydrate(self, model: Type, d: dict) -> LlamaABC:
        return model.from_event_json(d["event"])

    def retrieve(self, model: Type, *ids: Sequence[UUID]) -> Dict[UUID, LlamaABC]:
        assert issubclass(model, LlamaABC), f"Don't know how to model a non-Llama type {model}"
        assert model in self.tables, f"Model {model} never got added as an ORM table (don't forget 'add_table()')"
        assert ids, "Gotta have at least one id to select"
        for id in ids:
            assert isinstance(id, UUID), f"id is of type {type(id)} but should be of type {UUID}"

        with self.engine.begin() as transaction:
            table = self.tables[model]
            results = transaction.execute(sqla_select(table).where(table.c.id.in_([str(id) for id in ids])))
            return {(obj := self.hydrate(model, d)).table_id: obj for d in results.mappings()}


env.setup()
