import datetime
import logging
from io import StringIO
import unittest.mock as mock

from llama.base import LlamaBase
from llama.event_handler import EventHandler


def test_is_llamba_base():
    assert issubclass(EventHandler, LlamaBase)


def test_init():
    evan = EventHandler()

    assert isinstance(evan.created_at, datetime.datetime)
    assert isinstance(evan.env, str)
    assert evan.env == "TEST_ENV"


def test_as_event_json():
    mocked_now = "yeah, now we're mocking good"
    with mock.patch.object(datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
        patched.now.return_value = mocked_now
        evan = EventHandler()
        assert evan.as_event_json() == f'{{"created_at": "{mocked_now}", "env": "TEST_ENV"}}'


def test_log():
    logger = logging.root
    original_logging_level = logger.level

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.setLevel(logging.INFO)
    logger.removeHandler(handler)
    logger.addHandler(handler)

    mocked_now = "Dec 31 1999"
    with mock.patch.object(datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
        patched.now.return_value = mocked_now
        EventHandler()

    handler.flush()
    print(stream.getvalue())
    assert (
        stream.getvalue().strip()
        == f'EventHandler:[{{"created_at": "{mocked_now}", "env": "TEST_ENV"}}]<msg:initialized>'
    )

    logger.removeHandler(handler)
    handler.close()
    logging.root.setLevel(original_logging_level)


def test_envs():
    evan = EventHandler()
    assert evan.is_live() is False
    assert evan.env == "TEST_ENV"

    evan = EventHandler(env="LIVE")
    assert evan.is_live() is True

    evan = EventHandler(env="BACKTEST")
    assert evan.is_backtest() is True

    evan = EventHandler(env="PAPER")
    assert evan.is_paper() is True
