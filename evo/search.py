"""Live web search through a public results page. No key is stored."""

from __future__ import annotations

import re
from html import unescape
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


def search_web(query: str, limit: int = 5) -> dict:
    cleaned = ' '.join(query.split())[:200]
    if not cleaned:
        return {'ok': False, 'results': [], 'reason': 'empty query'}
    url = f'https://html.duckduckgo.com/html/?q={quote_plus(cleaned)}'
    request = Request(url, headers={'User-Agent': 'Vishnu2Search/0.1'})
    try:
        with urlopen(request, timeout=12) as response:
            page = response.read().decode('utf-8', 'replace')
    except Exception as exc:
        return {'ok': False, 'results': [], 'reason': str(exc)}
    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', page, flags=re.I | re.S)
    links = re.findall(r'class="result__a" href="(.*?)"', page, flags=re.I)
    results = []
    for title, link in zip(titles, links):
        text = re.sub('<[^>]+>', '', unescape(title))
        text = ' '.join(text.split())
        if text:
            results.append({'title': text[:180], 'url': unescape(link)})
        if len(results) >= limit:
            break
    return {'ok': bool(results), 'query': cleaned, 'results': results}
