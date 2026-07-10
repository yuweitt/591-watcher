import html
import logging

import requests

from .config import Config
from .parser import Listing

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
MAX_MESSAGE_CHARS = 3500  # stay under Telegram's 4096 limit with margin
LISTINGS_PER_CHUNK = 15

logger = logging.getLogger(__name__)


def _listing_line(listing: Listing) -> str:
    title = html.escape(listing.title)
    kind = html.escape(listing.kind)
    region = html.escape(listing.region_text)
    return (
        f'<a href="{listing.link}">{title}</a>\n'
        f"💰 {listing.price} 元 · {kind} · {region} · {listing.floor}\n"
    )


def _chunk(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _post_message(token: str, chat_id: str, text: str) -> None:
    resp = requests.post(
        TELEGRAM_API.format(token=token),
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=15,
    )
    if resp.status_code != 200:
        logger.error("Telegram sendMessage failed: %s %s", resp.status_code, resp.text[:300])


def send_digest(cfg: Config, new_listings: list[Listing]) -> None:
    header = f"🏠 591 有 {len(new_listings)} 個新物件\n\n"
    for chunk in _chunk(new_listings, LISTINGS_PER_CHUNK):
        body = "\n".join(_listing_line(listing) for listing in chunk)
        text = header + body
        if len(text) > MAX_MESSAGE_CHARS:
            text = text[:MAX_MESSAGE_CHARS] + "\n…"
        _post_message(cfg.telegram_bot_token, cfg.telegram_chat_id, text)
        header = ""  # only prefix the first chunk


def send_failure_notice(cfg: Config, error: Exception) -> None:
    try:
        text = f"⚠️ 591 爬蟲執行失敗：\n{error}"
        _post_message(cfg.telegram_bot_token, cfg.telegram_chat_id, text)
    except Exception:
        logger.exception("Failed to send failure notice via Telegram")
