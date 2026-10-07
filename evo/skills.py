"""Original assistant skills. These are not Grok's private tools."""

from __future__ import annotations

import ast
import math
import operator
from datetime import datetime, timezone
from html import unescape
from urllib.request import Request, urlopen
import re

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'sqrt', 'sin', 'cos'}:
        fn = {'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos}[node.func.id]
        return fn(*[_eval(arg) for arg in node.args])
    raise ValueError('only arithmetic is allowed')


def calculate(expression: str) -> dict:
    tree = ast.parse(expression.strip(), mode='eval')
    return {'ok': True, 'result': _eval(tree.body)}


def now() -> dict:
    stamp = datetime.now(timezone.utc)
    return {'utc': stamp.isoformat(), 'date': stamp.date().isoformat()}


def read_page(url: str, limit: int = 800) -> dict:
    if not url.startswith('https://'):
        return {'ok': False, 'reason': 'only https pages'}
    request = Request(url, headers={'User-Agent': 'Vishnu2Read/0.1'})
    try:
        with urlopen(request, timeout=12) as response:
            raw = response.read(200_000).decode('utf-8', 'replace')
    except Exception as exc:
        return {'ok': False, 'reason': str(exc)}
    text = re.sub('<script[\s\S]*?</script>', ' ', raw, flags=re.I)
    text = re.sub('<style[\s\S]*?</style>', ' ', text, flags=re.I)
    text = re.sub('<[^>]+>', ' ', text)
    text = ' '.join(unescape(text).split())
    return {'ok': bool(text), 'url': url, 'text': text[:limit]}
