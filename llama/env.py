import os
from pathlib import Path

from dotenv import load_dotenv

from definitions import PROJECT_ROOT


def get_env_file() -> Path:
    prefix = os.environ.get("ENV", "").lower()
    if prefix:
        prefix = "." + prefix
    return PROJECT_ROOT / f"{prefix}.env"


def setup():
    print(get_env_file())
    load_dotenv(dotenv_path=get_env_file(), override=True)
