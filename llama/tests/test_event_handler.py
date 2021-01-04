import datetime
import logging
from io import StringIO
import uuid

import unittest.mock as mock

from llama.base import LlamaBase
from llama.event_handler import EventHandler


def test_is_llamba_base():
    assert issubclass(EventHandler, LlamaBase)


def test_init():
    evan = EventHandler()

    assert evan.has_timestamp()
    assert hasattr(evan, "created_at")

    assert isinstance(evan.created_at, datetime.datetime)


def test_as_event_json():
    mocked_now = "yeah, now we're mocking good"
    mock_id = "I think, therefore I am"

    with mock.patch.object(datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched_dt:
        with mock.patch.object(uuid, "uuid4", mock.Mock(wraps=uuid.uuid4)) as patched_id:
            patched_dt.now.return_value = mocked_now
            patched_id.return_value = mock_id

            evan = EventHandler()
            assert evan.as_event_json() == f'{{"created_at": "{mocked_now}", "table_id": "{mock_id}"}}'


def test_from_event_json():
    mocked_now = "yeah, now we're mocking good"
    mock_id = "yo mamma bear!!!!!"
    with mock.patch.object(datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched_dt, mock.patch.object(
        uuid, "uuid4", mock.Mock(wraps=uuid.uuid4)
    ) as patched_id:
        patched_dt.now.return_value = mocked_now
        patched_id.return_value = mock_id
        evan = EventHandler.from_event_json('{"num": 42, "string": "hiya"}')
        assert evan.as_dict() == {"created_at": mocked_now, "num": 42, "string": "hiya", "table_id": mock_id}


def test_log():
    logger = logging.root
    original_logging_level = logger.level

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.setLevel(logging.INFO)
    logger.removeHandler(handler)
    logger.addHandler(handler)

    mocked_now = "Dec 31 1999"
    mock_id = "yo mamma bear!!!!!"
    with mock.patch.object(datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched_dt, mock.patch.object(
        uuid, "uuid4", mock.Mock(wraps=uuid.uuid4)
    ) as patched_id:
        patched_dt.now.return_value = mocked_now
        patched_id.return_value = mock_id
        EventHandler()

    handler.flush()
    print(stream.getvalue())
    assert (
        stream.getvalue().strip()
        == f'EventHandler:[{{"created_at": "{mocked_now}", "table_id": "{mock_id}"}}]<msg:initialized>'
    )

    logger.removeHandler(handler)
    handler.close()
    logging.root.setLevel(original_logging_level)
