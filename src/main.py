import logging
import sys

from .config import load_config
from .errors import ScrapeError
from .notifier import send_digest, send_failure_notice
from .parser import normalize
from .publish import write_public_listings
from .scraper import fetch_all_listings
from .search_url import extract_query_params
from .store import diff_new, load_seen_ids, save_seen_ids

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run() -> int:
    cfg = load_config()

    try:
        params = extract_query_params(cfg.search_url)
        raw = fetch_all_listings(params)
        listings = normalize(raw)
    except ScrapeError as e:
        logger.error("Scrape failed: %s", e)
        send_failure_notice(cfg, e)
        return 1

    logger.info("Fetched %d listings", len(listings))
    write_public_listings(listings)

    seen = load_seen_ids()
    new = diff_new(listings, seen)

    if new:
        logger.info("Found %d new listing(s), notifying", len(new))
        send_digest(cfg, new)
        save_seen_ids(seen | {listing.id for listing in listings})
    else:
        logger.info("No new listings.")

    return 0


if __name__ == "__main__":
    sys.exit(run())
