from dataclasses import dataclass


@dataclass
class Listing:
    id: str
    title: str
    price: str
    kind: str
    area: str
    floor: str
    region_text: str
    image_url: str
    link: str


def parse_listing(raw: dict) -> Listing:
    post_id = str(raw.get("id") or "")
    link = raw.get("url") or (f"https://rent.591.com.tw/{post_id}" if post_id else "")

    return Listing(
        id=post_id,
        title=raw.get("title", ""),
        price=raw.get("price", ""),
        kind=raw.get("layoutStr") or raw.get("kind_name", ""),
        area=raw.get("area_name", ""),
        floor=raw.get("floor_name", ""),
        region_text=raw.get("address") or raw.get("community_name", ""),
        image_url=raw.get("cover", ""),
        link=link,
    )


def normalize(raw_listings: list[dict]) -> list[Listing]:
    listings = []
    for raw in raw_listings:
        listing = parse_listing(raw)
        if listing.id:
            listings.append(listing)
    return listings
