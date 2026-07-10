import os
import sys
from dataclasses import dataclass


@dataclass
class Config:
    search_url: str
    telegram_bot_token: str
    telegram_chat_id: str


REQUIRED_VARS = ["SEARCH_URL", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]


def load_config() -> Config:
    missing = [name for name in REQUIRED_VARS if not os.environ.get(name)]
    if missing:
        print(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + "\nSee README.md for setup instructions.",
            file=sys.stderr,
        )
        sys.exit(1)

    return Config(
        search_url=os.environ["SEARCH_URL"],
        telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        telegram_chat_id=os.environ["TELEGRAM_CHAT_ID"],
    )
