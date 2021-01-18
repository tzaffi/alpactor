import os
from dotenv import dotenv_values

import definitions
from llama import env


def test_env_without_fixture():
    os.environ["ENV"] = "TEST"
    env.setup(force_rerun=True)

    assert "TEST_ENV_SENTINEL" == os.environ.get("ENV_SENTINEL")


def test_live_env():
    os.environ["ENV"] = "LIVE"
    env.setup(force_rerun=True)

    assert os.environ.get("ENV") == "LIVE"

    assert env.get_env_file() == definitions.PROJECT_ROOT / ".live.env"

    assert os.environ.get("ENV_SENTINEL") == "Go for the gold!!!"

    assert os.environ.get("ALPACA_API_KEY_LIVE") != os.environ.get("ALPACA_API_KEY_PAPER")
    assert os.environ.get("ALPACA_API_SECRET_LIVE") != os.environ.get("ALPACA_API_SECRET_PAPER")


def test_backtest_env():
    os.environ["ENV"] = "BACKTEST"
    env.setup(force_rerun=True)

    assert os.environ.get("ENV") == "BACKTEST"

    assert env.get_env_file() == definitions.PROJECT_ROOT / ".backtest.env"

    assert os.environ.get("ENV_SENTINEL") == "Go for the bitcoin!!!"

    assert os.environ.get("ALPACA_API_KEY_LIVE") == "TEST_ALPACA_API_KEY_LIVE"
    assert os.environ.get("ALPACA_API_SECRET_LIVE") == "TEST_ALPACA_API_SECRET_LIVE"


def test_paper_env():
    """
    Note: as a side-effect, a process calling this will be in a paper environment
    """
    os.environ["ENV"] = "PAPER"
    env.setup(force_rerun=True)

    assert os.environ.get("ENV") == "PAPER"

    assert env.get_env_file() == definitions.PROJECT_ROOT / ".paper.env"

    assert os.environ.get("ENV_SENTINEL") == "Go for the fiat!!!"

    assert os.environ.get("ALPACA_API_KEY_LIVE") == os.environ.get("ALPACA_API_KEY_PAPER")
    assert os.environ.get("ALPACA_API_SECRET_LIVE") == os.environ.get("ALPACA_API_SECRET_PAPER")


def test_envs():
    if os.environ.get("ENV") is not None:
        del os.environ["ENV"]

    assert os.environ.get("ENV") is None
    assert env.is_live() is False
    assert env.is_backtest() is False
    assert env.is_paper() is False

    os.environ["ENV"] = "LIVE"
    env.setup(force_rerun=True)
    assert env.is_live() is True
    assert env.is_backtest() is False
    assert env.is_paper() is False

    os.environ["ENV"] = "BACKTEST"
    env.setup(force_rerun=True)
    assert env.is_live() is False
    assert env.is_backtest() is True
    assert env.is_paper() is False

    os.environ["ENV"] = "PAPER"
    env.setup(force_rerun=True)
    assert env.is_live() is False
    assert env.is_backtest() is False
    assert env.is_paper() is True


def test_envs_are_not_production():
    os.environ["ENV"] = "TEST"
    env.setup(force_rerun=True)

    expected_env_var_keys = {
        "ENV_SENTINEL",
        "ALPACA_API_KEY_LIVE",
        "ALPACA_API_SECRET_LIVE",
        "ALPACA_API_KEY_PAPER",
        "ALPACA_API_SECRET_PAPER",
        "DB_URI",
        "KAFKA_API_KEY",
        "KAFKA_API_SECRET",
        "KAFKA_HOST",
    }

    expected_dict = {k: f"TEST_{k}" for k in expected_env_var_keys}
    expected_dict.update(DB_URI="sqlite+pysqlite:///:memory:")

    assert dotenv_values(env.get_env_file()) == expected_dict
