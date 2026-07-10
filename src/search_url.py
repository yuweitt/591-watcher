from urllib.parse import parse_qs, urlsplit


def extract_query_params(search_url: str) -> dict[str, str]:
    """Parse the user-provided 591 search URL into flat query params.

    591's search UI encodes every filter (region, price, kind, area, ...)
    directly in the query string, so we just reuse whatever the user pasted
    and let scraper.py own pagination (firstRow).
    """
    parsed = urlsplit(search_url)
    raw_params = parse_qs(parsed.query)
    params = {key: values[0] for key, values in raw_params.items() if values}
    params.pop("firstRow", None)
    return params
