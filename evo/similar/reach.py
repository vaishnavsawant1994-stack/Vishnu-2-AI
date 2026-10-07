"""Read one public page. This does not crawl a site."""

from __future__ import annotations

from evo.skills import read_page


def reach(url: str) -> dict:
    result = read_page(url, limit=1200)
    result['tool'] = 'page_reach'
    result['crawled'] = False
    return result
