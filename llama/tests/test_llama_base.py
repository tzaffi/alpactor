import json
import pytest

from llama.base import LlamaABC, LlamaMixin, LlamaBase


def test_abc():
    with pytest.raises(TypeError):
        LlamaABC()


def test_envs():
    expected_env_var_keys = {
        "KAFKA_HOST",
        "KAFKA_API_KEY",
        "KAFKA_API_SECRET",
        "ALPACA_API_KEY",
        "ALPACA_API_SECRET",
    }

    llamy = LlamaMixin()
    assert set(llamy.env_vars.keys()) == expected_env_var_keys


class NumberAndString(LlamaMixin):
    def __init__(self):
        self.num = 42
        self.string = "hiya"
        self._private = "private"

    def another_method(self):
        pass


def test_as_dict():
    nas = NumberAndString()
    assert nas.as_dict() == {"num": 42, "string": "hiya"}


def test_as_event_json():
    nas = NumberAndString()
    assert json.loads(nas.as_event_json()) == {"num": 42, "string": "hiya"}


def test_from_event_json():
    nas = NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')
    assert nas.as_dict() == {"num": 42, "string": "hiya"}


def test_class_hierarchy():
    assert issubclass(LlamaBase, LlamaABC)
    assert issubclass(LlamaBase, LlamaMixin)
