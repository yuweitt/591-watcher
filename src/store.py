import json
from datetime import datetime, timezone
from pathlib import Path

from .parser import Listing

SEEN_IDS_PATH = Path(__file__).resolve().parent.parent / "data" / "seen_ids.json"


def load_seen_ids(path: Path = SEEN_IDS_PATH) -> set[str]:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("ids", []))


def save_seen_ids(ids: set[str], path: Path = SEEN_IDS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ids": sorted(ids),
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def diff_new(listings: list[Listing], seen: set[str]) -> list[Listing]:
    return [listing for listing in listings if listing.id not in seen]
