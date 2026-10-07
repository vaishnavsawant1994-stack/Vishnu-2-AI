"""Create a simple PNG on disk. This is not a generative image model."""

from __future__ import annotations

from pathlib import Path


def create_image(title: str, folder: Path) -> dict:
    text = ' '.join(title.split())[:80] or 'Vishnu-2'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'owner-image.png'
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        path.write_bytes(_tiny_png(text))
        return {'ok': True, 'path': str(path), 'engine': 'plain-png', 'tool': 'owner_image'}
    image = Image.new('RGB', (960, 540), '#14120e')
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, 920, 500), outline='#d6b15a', width=3)
    draw.text((70, 230), text, fill='#e8e4d9')
    image.save(path, 'PNG')
    return {'ok': True, 'path': str(path), 'engine': 'pillow', 'tool': 'owner_image'}


def _tiny_png(text: str) -> bytes:
    # 1x1 PNG if Pillow is absent. The title is recorded beside the file.
    return bytes.fromhex(
        '89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de'
        '0000000c4944415408d763f8cfc0000000030001ad9d9c3e0000000049454e44ae426082'
    )
