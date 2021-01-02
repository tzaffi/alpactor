import os

import pytest

import definitions
from llama import env


def test_env_without_fixture():
    assert "TEST_ENV" == os.environ.get("ENV")
    assert os.environ.get("ENV_SENTINEL") == "TEST_ENV_SENTINEL"


# @pytest.mark.usefixtures("live_env_fixture")
def test_live_env():
    os.environ["ENV"] = "LIVE"

    assert os.environ.get("ENV") == "LIVE"

    assert env.get_env_file() == definitions.PROJECT_ROOT / ".live.env"

    assert os.environ.get("ENV_SENTINEL") == "TEST_ENV_SENTINEL"

    env.setup()
    assert os.environ.get("ENV_SENTINEL") == "Go for the gold!!!"

    os.environ["ENV"] = "TEST"
    env.setup()
    test_env_without_fixture()


# @pytest.mark.usefixtures("backtest_env_fixture")
def test_backtest_env():
    os.environ["ENV"] = "BACKTEST"

    assert os.environ.get("ENV") == "BACKTEST"

    assert env.get_env_file() == definitions.PROJECT_ROOT / ".backtest.env"

    assert os.environ.get("ENV_SENTINEL") == "TEST_ENV_SENTINEL"

    env.setup()
    assert os.environ.get("ENV_SENTINEL") == "Go for the bitcoin!!!"

    os.environ["ENV"] = "TEST"
    env.setup()
    test_env_without_fixture()


# @pytest.mark.usefixtures("paper_env_fixture")
def test_paper_env():
    os.environ["ENV"] = "PAPER"

    assert os.environ.get("ENV") == "PAPER"

    assert env.get_env_file() == definitions.PROJECT_ROOT / ".paper.env"

    assert os.environ.get("ENV_SENTINEL") == "TEST_ENV_SENTINEL"

    env.setup()
    assert os.environ.get("ENV_SENTINEL") == "Go for the fiat!!!"

    os.environ["ENV"] = "TEST"
    env.setup()
    test_env_without_fixture()
