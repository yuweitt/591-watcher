import json
import re
import subprocess
import time
from pathlib import Path

import requests

from .errors import ScrapeError

LIST_URL = "https://rent.591.com.tw/list"
PAGE_SIZE = 30
REQUEST_DELAY_SEC = 1.5
MAX_PAGES = 5  # newest-first, 150 listings/run is plenty to catch what's new since the last poll

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

NUXT_SCRIPT_RE = re.compile(r"<script[^>]*>\s*(window\.__NUXT__=.*?)</script>", re.S)
DECODE_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "decode_nuxt.js"


def _decode_nuxt_state(html: str) -> dict:
    """591's search results are server-rendered (Nuxt) and embedded as a
    `window.__NUXT__=(function(...){...})(...)` inline script rather than a
    separate JSON API. We run that script through Node (with a stubbed
    `window`) to reconstruct the real object graph, since it's plain JS
    describing itself.
    """
    match = NUXT_SCRIPT_RE.search(html)
    if not match:
        raise ScrapeError("591 頁面結構可能改版：找不到內嵌的 __NUXT__ 資料")

    try:
        proc = subprocess.run(
            ["node", str(DECODE_SCRIPT)],
            input=match.group(1),
            capture_output=True,
            text=True,
            timeout=20,
        )
    except FileNotFoundError as e:
        raise ScrapeError("找不到 node 執行檔，請確認執行環境已安裝 Node.js") from e
    except subprocess.TimeoutExpired as e:
        raise ScrapeError("解析 591 內嵌資料逾時") from e

    if proc.returncode != 0:
        raise ScrapeError(f"解析 591 內嵌資料失敗：{proc.stderr[:300]}")

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise ScrapeError(
            f"591 內嵌資料不是預期的 JSON：{proc.stdout[:300]!r}"
        ) from e


def fetch_all_listings(base_params: dict) -> list[dict]:
    params = {"order": "posttime", "orderType": "desc", **base_params}

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    listings: list[dict] = []
    offset = 0

    for _ in range(MAX_PAGES):
        page_params = {**params, "firstRow": offset}
        resp = session.get(LIST_URL, params=page_params, timeout=15)
        if resp.status_code != 200:
            raise ScrapeError(f"591 搜尋頁回傳 HTTP {resp.status_code}")

        state = _decode_nuxt_state(resp.text)
        try:
            rent_list = state["pinia"]["rent-list"]
            page_data = rent_list["dataList"]
            total = int(rent_list["total"])
        except (KeyError, TypeError, ValueError) as e:
            raise ScrapeError(f"591 資料結構改版：{str(state)[:300]}") from e

        if not page_data:
            break

        listings.extend(page_data)
        offset += PAGE_SIZE

        if offset >= total:
            break

        time.sleep(REQUEST_DELAY_SEC)

    return listings
