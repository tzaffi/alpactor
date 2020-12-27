import datetime
from llama.base import LlamaBase
from llama.event_handler import EventHandler

import unittest.mock as mock


def test_is_llamba_base():
    assert issubclass(EventHandler, LlamaBase)


def test_init():
    evan = EventHandler(debug=True)

    assert evan._debug is True
    assert isinstance(evan.created_at, datetime.datetime)


def test_as_event_json():
    mocked_now = "yeah, now we're mocking good"
    with mock.patch.object(
        datetime, "datetime", mock.Mock(wraps=datetime.datetime)
    ) as patched:
        patched.now.return_value = mocked_now
        evan = EventHandler(debug=True)
        assert evan.as_event_json() == f'{{"created_at": "{mocked_now}"}}'
