"""Download an HTTPS file into the data folder. No local or private addresses."""

from __future__ import annotations

import ipaddress
import re
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


MAX_BYTES = 2_000_000_000
CHUNK = 1024 * 1024


def _safe_name(url: str) -> str:
    name = Path(urlparse(url).path).name or 'download'
    name = re.sub(r'[^A-Za-z0-9._-]', '_', name)[:80]
    return name or 'download'


def _public_host(host: str) -> bool:
    if not host or host in {'localhost'}:
        return False
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return '.' in host
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)


def download_file(url: str, work: Path) -> dict:
    parsed = urlparse(url.strip())
    if parsed.scheme != 'https' or not _public_host(parsed.hostname or ''):
        return {'ok': False, 'tool': 'owner_download', 'reason': 'only public https URLs'}
    folder = Path(work) / 'downloads'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f'{uuid.uuid4().hex[:8]}-{_safe_name(url)}'
    request = Request(url, headers={'User-Agent': 'Vishnu2Download/0.1'})
    written = 0
    try:
        with urlopen(request, timeout=60) as response, path.open('wb') as handle:
            while written <= MAX_BYTES:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                written += len(chunk)
                if written > MAX_BYTES:
                    break
                handle.write(chunk)
    except Exception as exc:
        path.unlink(missing_ok=True)
        return {'ok': False, 'tool': 'owner_download', 'reason': str(exc)}
    if written > MAX_BYTES:
        path.unlink(missing_ok=True)
        return {'ok': False, 'tool': 'owner_download', 'reason': 'file is larger than 2 GB'}
    return {'ok': True, 'tool': 'owner_download', 'owner': 'vaishnav', 'path': str(path), 'bytes': written}
