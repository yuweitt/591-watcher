import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .parser import Listing

LISTINGS_JSON_PATH = Path(__file__).resolve().parent.parent / "docs" / "listings.json"
MAX_LISTINGS = 200


def write_public_listings(
    listings: list[Listing], path: Path = LISTINGS_JSON_PATH
) -> None:
    trimmed = listings[:MAX_LISTINGS]
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "listings": [asdict(listing) for listing in trimmed],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
