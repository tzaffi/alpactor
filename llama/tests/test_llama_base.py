from io import StringIO
import logging

import pytest
import unittest.mock as mock

from llama.base import LlamaABC, LlamaMixin, LlamaBase


def test_abc():
    with pytest.raises(TypeError):
        LlamaABC()


def test_envs():
    expected_env_var_keys = {
        "ENV",
        "ALPACA_API_KEY",
        "ALPACA_API_SECRET",
        "KAFKA_API_KEY",
        "KAFKA_API_SECRET",
        "KAFKA_HOST",
    }

    llamy = LlamaMixin()
    assert set(llamy.env_vars.keys()) == expected_env_var_keys


def test_envs_are_not_production():
    expected_env_var_keys = {
        "ENV",
        "ALPACA_API_KEY",
        "ALPACA_API_SECRET",
        "KAFKA_API_KEY",
        "KAFKA_API_SECRET",
        "KAFKA_HOST",
    }

    llamy = LlamaMixin()
    assert llamy.env_vars == {k: f"TEST_{k}" for k in expected_env_var_keys}


def test_is_live():
    llamy = LlamaMixin()
    assert llamy.is_live() is False

    llamy = LlamaMixin(env="LIVE")
    assert llamy.is_live() is True


def test_is_paper():
    llamy = LlamaMixin()
    assert llamy.is_paper() is False

    llamy = LlamaMixin(env="PAPER")
    assert llamy.is_paper() is True


def test_is_backtest():
    llamy = LlamaMixin()
    assert llamy.is_backtest() is False

    llamy = LlamaMixin(env="BACKTEST")
    assert llamy.is_backtest() is True


class NumberAndString(LlamaMixin):
    def __init__(self):
        self.num = 42
        self.string = "hiya"
        self._private = "private"
        super().__init__()

    def another_method(self):
        pass


def test_as_dict():
    nas = NumberAndString()
    assert nas.as_dict() == {"env": "TEST_ENV", "num": 42, "string": "hiya"}


def test_as_event_json():
    nas = NumberAndString()
    assert nas.as_event_json() == '{"env": "TEST_ENV", "num": 42, "string": "hiya"}'


def test_from_event_json():
    nas = NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')
    assert nas.as_dict() == {"env": "TEST_ENV", "num": 42, "string": "hiya"}


def test_class_hierarchy():
    assert issubclass(LlamaBase, LlamaABC)
    assert issubclass(LlamaBase, LlamaMixin)


def test_logging():
    original_logging_level = logging.root.level

    # Under default logging level, as_dict() isn't called even though log() is
    assert logging.root.level == logging.WARN, logging.root.level

    with mock.patch.object(logging, "log") as log:
        nas = NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')
    assert isinstance(nas, NumberAndString), type(nas)
    log.assert_called_once_with(logging.INFO, "%s:[%s]<msg:%s>", "NumberAndString", nas, "initialized")

    with mock.patch.object(LlamaMixin, "as_dict") as as_dict:
        nas = NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')
    assert isinstance(nas, NumberAndString), type(nas)
    as_dict.assert_not_called()

    with mock.patch.object(logging, "log") as log:
        nas = NumberAndString()
    assert isinstance(nas, NumberAndString), type(nas)
    log.assert_called_once_with(logging.INFO, "%s:[%s]<msg:%s>", "NumberAndString", nas, "initialized")

    with mock.patch.object(LlamaMixin, "as_dict") as as_dict:
        nas = NumberAndString()
    assert isinstance(nas, NumberAndString), type(nas)
    as_dict.assert_not_called()

    # Under DEBUG logging level, as_dict() is ALSO called
    logging.root.setLevel(logging.DEBUG)
    assert logging.root.level == logging.DEBUG, logging.root.level

    with mock.patch.object(logging, "log") as log:
        nas = NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')
    assert isinstance(nas, NumberAndString), type(nas)
    log.assert_called_once_with(logging.INFO, "%s:[%s]<msg:%s>", "NumberAndString", nas, "initialized")

    with mock.patch.object(LlamaMixin, "as_dict") as as_dict:
        nas = NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')
    assert isinstance(nas, NumberAndString), type(nas)
    as_dict.assert_called()

    with mock.patch.object(logging, "log") as log:
        nas = NumberAndString()
    assert isinstance(nas, NumberAndString), type(nas)
    log.assert_called_once_with(logging.INFO, "%s:[%s]<msg:%s>", "NumberAndString", nas, "initialized")

    with mock.patch.object(LlamaMixin, "as_dict") as as_dict:
        nas = NumberAndString()
    assert isinstance(nas, NumberAndString), type(nas)
    as_dict.assert_called()

    # reset the logging level to where it was
    logging.root.setLevel(original_logging_level)


def test_log():
    logger = logging.root
    original_logging_level = logger.level

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.setLevel(logging.INFO)
    logger.removeHandler(handler)
    logger.addHandler(handler)

    NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')

    handler.flush()
    print(stream.getvalue())
    assert (
        stream.getvalue().strip()
        == 'NumberAndString:[{"env": "TEST_ENV", "num": 42, "string": "hiya"}]<msg:initialized>'
    )

    logger.removeHandler(handler)
    handler.close()
    logging.root.setLevel(original_logging_level)
