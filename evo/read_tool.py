"""Read a website, text file, PDF, or image. Secrets and the vault are refused."""

from __future__ import annotations

from pathlib import Path

from evo.skills import read_page

REFUSED = ('vault', 'secret', '.env', 'id_rsa', 'credentials')
TEXT_SUFFIXES = {'.txt', '.md', '.json', '.csv', '.py', '.html', '.htm', '.log'}
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}


def _refused(path: Path) -> bool:
    lowered = str(path).lower()
    return any(part in lowered for part in REFUSED)


def read_anything(target: str, work: Path, limit: int = 4000) -> dict:
    raw = target.strip()
    if raw.startswith('https://'):
        page = read_page(raw, limit=limit)
        page['tool'] = 'owner_read'
        page['kind'] = 'website'
        return page
    if raw.startswith('http://'):
        return {'ok': False, 'tool': 'owner_read', 'reason': 'only https websites'}
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = Path(work) / path
    path = path.resolve()
    if _refused(path):
        return {'ok': False, 'tool': 'owner_read', 'reason': 'secret files are refused'}
    if not path.exists() or not path.is_file():
        return {'ok': False, 'tool': 'owner_read', 'reason': 'file not found'}
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        return _pdf(path, limit)
    if suffix in IMAGE_SUFFIXES:
        return _image(path)
    if suffix in TEXT_SUFFIXES or suffix == '':
        text = path.read_text(encoding='utf-8', errors='replace')[:limit]
        return {'ok': True, 'tool': 'owner_read', 'kind': 'file', 'path': str(path), 'text': text}
    return {'ok': False, 'tool': 'owner_read', 'reason': f'unsupported file type {suffix}'}


def _pdf(path: Path, limit: int) -> dict:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages[:20]:
            parts.append(page.extract_text() or '')
        text = '\n'.join(parts)[:limit]
    except Exception as exc:
        return {'ok': False, 'tool': 'owner_read', 'kind': 'pdf', 'reason': str(exc)}
    return {'ok': bool(text.strip()), 'tool': 'owner_read', 'kind': 'pdf', 'path': str(path), 'text': text}


def _image(path: Path) -> dict:
    try:
        from PIL import Image
        with Image.open(path) as image:
            info = {'format': image.format, 'mode': image.mode, 'width': image.width, 'height': image.height}
    except Exception as exc:
        return {'ok': False, 'tool': 'owner_read', 'kind': 'image', 'reason': str(exc)}
    return {
        'ok': True,
        'tool': 'owner_read',
        'kind': 'image',
        'path': str(path),
        'info': info,
        'text': f"Image {info['format']} {info['width']}x{info['height']} {info['mode']}",
    }
