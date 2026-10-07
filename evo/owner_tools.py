"""Vaishnav's own math, coding, and search tools."""

from __future__ import annotations

from evo.search import search_web
from evo.skills import calculate, check_code


def owner_math(expression: str) -> dict:
    result = calculate(expression)
    result['tool'] = 'owner_math'
    result['owner'] = 'vaishnav'
    return result


def owner_code(source: str) -> dict:
    result = check_code(source)
    result['tool'] = 'owner_code'
    result['owner'] = 'vaishnav'
    return result


def owner_search(query: str) -> dict:
    result = search_web(query)
    result['tool'] = 'owner_search'
    result['owner'] = 'vaishnav'
    return result
