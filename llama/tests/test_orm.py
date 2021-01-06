import contextlib
from sqlalchemy import text, Table, insert, Column, Integer, DateTime
from sqlalchemy.exc import OperationalError
import uuid

import pytest

from llama.base import LlamaBase
from llama.event_handler import EventHandler
import llama.orm as orm
from llama.orm import ORM


@contextlib.contextmanager
def inmem_db_context():
    eng = orm.engine()
    try:
        yield eng
    finally:
        eng.dispose()


def test_inmemb_db():
    eng = orm.engine()
    with eng.connect() as conn:
        result = conn.execute(text("select 'hello world'"))

    res = result.all()
    assert len(res) == 1
    assert len(res[0]) == 1
    assert res[0][0] == "hello world"


def test_inmem_db_context():
    with inmem_db_context() as eng:
        with eng.connect() as conn:
            result = conn.execute(text("select 'hello world'"))

        res = result.all()
        assert len(res) == 1
        assert len(res[0]) == 1
        assert res[0][0] == "hello world"

    with inmem_db_context() as eng:
        with eng.begin() as comconn:
            comconn.execute(text("CREATE TABLE IF NOT EXISTS some_table (x int, y int)"))
            comconn.execute(
                text("INSERT INTO some_table (x, y) VALUES (:x, :y)"), [{"x": 1, "y": 1}, {"x": 2, "y": 4}]
            )
            result = comconn.execute(text("SELECT * FROM some_table"))
            assert len(result.all()) == 2

        with eng.begin() as comconn:
            result = comconn.execute(text("SELECT * FROM some_table"))
            assert len(result.all()) == 2

    with inmem_db_context() as eng:
        with eng.begin() as comconn:
            with pytest.raises(OperationalError) as oe:
                result = comconn.execute(text("SELECT * FROM some_table"))

            assert "no such table: some_table" in str(oe.value)


def test_create_again_blows_up():
    with inmem_db_context() as eng:
        with eng.begin() as comconn:
            comconn.execute(text("CREATE TABLE some_table (x int, y int)"))
            comconn.execute(
                text("INSERT INTO some_table (x, y) VALUES (:x, :y)"), [{"x": 1, "y": 1}, {"x": 2, "y": 4}]
            )
            result = comconn.execute(text("SELECT * FROM some_table"))
            assert len(result.all()) == 2

        with eng.begin() as comconn:
            with pytest.raises(OperationalError) as oe:
                comconn.execute(text("CREATE TABLE some_table (x int, y int)"))

            assert "table some_table already exists" in str(oe.value)

    with inmem_db_context() as eng:
        with eng.begin() as comconn:
            comconn.execute(text("CREATE TABLE some_table (x int, y int)"))
            comconn.execute(
                text("INSERT INTO some_table (x, y) VALUES (:x, :y)"), [{"x": 1, "y": 1}, {"x": 2, "y": 4}]
            )
            result = comconn.execute(text("SELECT * FROM some_table"))
            assert len(result.all()) == 2


class ImmutableNumber(LlamaBase):
    @classmethod
    def db_table_name(cls):
        return "yomama"

    def __init__(self, num):
        super(ImmutableNumber, self).__init__(num=num)


def test_llama_name():
    assert ImmutableNumber.db_table_name() == "yomama"

    imnum = ImmutableNumber(42)
    assert imnum.db_table_name() == "yomama"


def test_init():
    ori = ORM()

    assert hasattr(ori, "engine")
    assert hasattr(ori, "metadata")
    assert ori.tables == {}


def test_add_table():
    ori = ORM()

    table = ori.add_table(ImmutableNumber)
    assert isinstance(table, Table)
    assert ori.tables[ImmutableNumber] is table


def test_bootstrap_db():
    with inmem_db_context() as eng:
        ori = ORM(eng=eng)

        table = ori.add_table(ImmutableNumber, Column("num", Integer))
        ori.bootstrap_db()

        some_numbers = [
            {"id": str(uuid.uuid4()), "event": {"hello": "Mother"}, "num": 42},
            {"id": str(uuid.uuid4()), "event": {"goodbye": "Father"}, "num": 53},
        ]

        with eng.begin() as comconn:
            comconn.execute(insert(table, values=some_numbers))

            result = comconn.execute(text("SELECT * FROM yomama"))
            assert len(result.all()) == 2

        ori.bootstrap_db()
        assert "got here - so bootstrapping multiple times doesn't blow up"

    with inmem_db_context() as eng:
        with eng.begin() as comconn:
            with pytest.raises(OperationalError) as oe:
                result = comconn.execute(text("SELECT * FROM yomama"))

            assert "no such table: yomama" in str(oe.value)


def test_insert_and_retrieve():
    with inmem_db_context() as eng:
        ori = ORM(eng=eng)

        ori.add_table(ImmutableNumber, Column("num", Integer))
        ori.add_table(EventHandler, Column("created_at", DateTime(timezone=True)))
        ori.bootstrap_db()

        some_numbers = [
            ImmutableNumber(42),
            ImmutableNumber(53),
        ]
        num_ids = map(lambda x: x.table_id, some_numbers)
        ori.insert(ImmutableNumber, *some_numbers)

        some_events = [
            EventHandler(event_json='{"yo": "mama"}'),
            EventHandler(event_json='{"yo": "dada"}'),
            EventHandler(event_json='{"yo": "papa"}'),
        ]
        event_ids = map(lambda x: x.table_id, some_events)
        ori.insert(EventHandler, *some_events)

        with eng.connect() as conn:
            result = conn.execute(text("SELECT * FROM yomama"))
            assert len(result.all()) == 2

            result = conn.execute(text("SELECT * FROM events"))
            assert len(result.all()) == 3

        numbers_roundtrip = ori.retrieve(ImmutableNumber, *num_ids)
        events_roundtrip = ori.retrieve(EventHandler, *event_ids)

        assert numbers_roundtrip == {obj.table_id: obj for obj in some_numbers}
        assert events_roundtrip == {obj.table_id: obj for obj in some_events}

    with inmem_db_context() as eng:
        with eng.begin() as comconn:
            with pytest.raises(OperationalError) as oe:
                result = comconn.execute(text("SELECT * FROM yomama"))

            assert "no such table: yomama" in str(oe.value)
