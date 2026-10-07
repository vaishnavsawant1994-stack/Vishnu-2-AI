"""Describe an image with the configured vision model. No description is invented."""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path


def describe_image(path: str, question: str, models=None) -> dict:
    image_path = Path(path).expanduser()
    if not image_path.is_file():
        return {'ok': False, 'tool': 'owner_vision', 'reason': 'image not found'}
    if models is None or not hasattr(models, 'vision'):
        return {'ok': False, 'tool': 'owner_vision', 'reason': 'vision model is not configured'}
    try:
        from PIL import Image
        with Image.open(image_path) as image:
            buffer = BytesIO()
            image.convert('RGB').save(buffer, format='JPEG', quality=80)
    except Exception as exc:
        return {'ok': False, 'tool': 'owner_vision', 'reason': str(exc)}
    data_url = 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')
    prompt = question.strip() or 'Describe this image.'
    try:
        text = models.vision(prompt, data_url)
    except Exception as exc:
        return {'ok': False, 'tool': 'owner_vision', 'reason': str(exc)}
    return {'ok': True, 'tool': 'owner_vision', 'owner': 'vaishnav', 'path': str(image_path), 'description': str(text)[:2000]}
