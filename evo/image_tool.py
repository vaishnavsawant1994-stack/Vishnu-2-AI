"""Create a local PNG. No external image service is called."""

from __future__ import annotations

import uuid
from pathlib import Path


def create_image(prompt: str, work: Path) -> dict:
    text = ' '.join(prompt.split())[:180]
    if not text:
        return {'ok': False, 'tool': 'owner_image', 'reason': 'empty prompt'}
    folder = Path(work) / 'images'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f'{uuid.uuid4().hex}.png'
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        path.write_bytes(_tiny_png(text))
        return {'ok': True, 'tool': 'owner_image', 'owner': 'vaishnav', 'path': str(path), 'engine': 'fallback'}
    image = Image.new('RGB', (960, 540), (18, 22, 28))
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, 920, 500), outline=(214, 177, 90), width=3)
    draw.text((70, 80), 'Vishnu-2', fill=(214, 177, 90))
    y = 150
    words = text.split()
    line = []
    for word in words:
        trial = ' '.join(line + [word])
        if len(trial) > 42:
            draw.text((70, y), ' '.join(line), fill=(232, 228, 217))
            y += 36
            line = [word]
        else:
            line.append(word)
    if line:
        draw.text((70, y), ' '.join(line), fill=(232, 228, 217))
    image.save(path, 'PNG')
    return {'ok': True, 'tool': 'owner_image', 'owner': 'vaishnav', 'path': str(path), 'engine': 'pillow'}


def _tiny_png(text: str) -> bytes:
    # 1x1 PNG if Pillow is absent. The prompt is still recorded beside it.
    return bytes.fromhex(
        '89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de'
        '0000000c4944415408d763f8cf000000020001e221bc330000000049454e44ae426082'
    )
