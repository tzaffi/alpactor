import os
from pathlib import Path

from dotenv import load_dotenv, dotenv_values

from llama.logger import log
from definitions import PROJECT_ROOT


_envs_loaded = False

env_keys = {
    "ENV_SENTINEL",
    "ALPACA_API_KEY",
    "ALPACA_API_SECRET",
    "DB_URI",
    "KAFKA_API_KEY",
    "KAFKA_API_SECRET",
    "KAFKA_HOST",
}


def is_bootstrapping_mode():
    return os.environ.get("BOOTSTRAPPING", "FALSE") == "TRUE"


def is_live():
    return _has_setup() and os.environ.get("ENV") == "LIVE"


def is_paper():
    return _has_setup() and os.environ.get("ENV") == "PAPER"


def is_backtest():
    return _has_setup() and os.environ.get("ENV") == "BACKTEST"


def _has_setup():
    global _envs_loaded
    return _envs_loaded is True


def get_env_file() -> Path:
    prefix = os.environ.get("ENV", "").lower()
    if prefix:
        prefix = "." + prefix
    return PROJECT_ROOT / f"{prefix}.env"


def setup(force_rerun=False):
    if not force_rerun and _has_setup():
        log(__import__(__name__), msg="setup() has already been run")
        return

    dotenv_file = get_env_file()
    log(__import__(__name__), msg=f"setup() dot_env from {dotenv_file}")

    dotenv_keys = set(dotenv_values(dotenv_file).keys())
    assert dotenv_keys == env_keys, dotenv_keys ^ env_keys

    load_dotenv(dotenv_path=get_env_file(), override=True)

    global _envs_loaded
    _envs_loaded = True
