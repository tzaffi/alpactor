from io import StringIO
import logging
import uuid

import pytest
import unittest.mock as mock

from llama.base import LlamaABC, LlamaMixin, LlamaBase


def test_abc():
    with pytest.raises(TypeError):
        LlamaABC()


class ImmutableNumber(LlamaMixin):
    def __init__(self, num):
        super(ImmutableNumber, self).__init__(num=num)


def test_is_immutable():
    llamy = LlamaMixin()

    assert llamy.is_immutable() is True

    with pytest.raises(AttributeError):
        llamy.blah = "blah"

    imnum = ImmutableNumber(42)
    assert imnum.num == 42

    with pytest.raises(AttributeError):
        llamy.num = 43


def test_id():
    mock_id = "I think, therefore I am"
    with mock.patch.object(uuid, "uuid4", mock.Mock(wraps=uuid.uuid4)) as patched:
        patched.return_value = mock_id
        llamy = LlamaMixin()
        assert llamy.table_id == mock_id


class NumberEvent(LlamaMixin):
    @classmethod
    def has_timestamp(cls):
        return True

    def __init__(self, num):
        super(NumberEvent, self).__init__(num=num)


def test_created_at():
    ne = NumberEvent(42)
    assert ne.num == 42
    assert ne.has_timestamp()
    assert hasattr(ne, "created_at")


class NumberAndString(LlamaMixin):
    @classmethod
    def is_immutable(cls):
        return False

    def __init__(self):
        self.num = 42
        self.string = "hiya"
        self._private = "private"
        super().__init__()

    def another_method(self):
        pass


def test_db_table_name():
    nas = NumberAndString()
    assert nas.db_table_name() == "numberandstring"


def test_as_dict():
    nas = NumberAndString()
    assert not nas.has_timestamp()
    d = nas.as_dict()
    assert "table_id" in d
    assert {k: v for k, v in d.items() if k != "table_id"} == {"num": 42, "string": "hiya"}


def test_as_event_json():
    mock_id = "I think, therefore I am"

    with mock.patch.object(uuid, "uuid4", mock.Mock(wraps=uuid.uuid4)) as patched_id:
        patched_id.return_value = mock_id

        nas = NumberAndString()
        assert nas.as_event_json() == f'{{"num": 42, "string": "hiya", "table_id": "{mock_id}"}}'


def test_from_event_json():
    mock_id = "I think, therefore I am"

    with mock.patch.object(uuid, "uuid4", mock.Mock(wraps=uuid.uuid4)) as patched_id:
        patched_id.return_value = mock_id
        nas = NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')
        assert nas.as_event_json() == f'{{"num": 42, "string": "hiya", "table_id": "{mock_id}"}}'


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

    mock_id = "I think, therefore I am"
    with mock.patch.object(uuid, "uuid4", mock.Mock(wraps=uuid.uuid4)) as patched_id:
        patched_id.return_value = mock_id

        NumberAndString.from_event_json('{"num": 42, "string": "hiya"}')

        handler.flush()
        print(stream.getvalue())
        assert (
            stream.getvalue().strip()
            == f'NumberAndString:[{{"num": 42, "string": "hiya", "table_id": "{mock_id}"}}]<msg:initialized>'
        )

        logger.removeHandler(handler)
        handler.close()
        logging.root.setLevel(original_logging_level)
