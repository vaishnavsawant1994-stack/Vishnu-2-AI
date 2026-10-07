"""Multi-scene storyboard and narration. No video file is rendered."""

from __future__ import annotations

from pathlib import Path


def write_story(work: Path, title: str, scenes: list[str]) -> dict:
    folder = Path(work) / 'stories'
    folder.mkdir(parents=True, exist_ok=True)
    safe = ''.join(ch.lower() if ch.isalnum() else '-' for ch in title).strip('-') or 'story'
    body = '\n'.join(f'<section><h2>Scene {i}</h2><p>{scene}</p></section>' for i, scene in enumerate(scenes, 1))
    html = f'<!doctype html><html><body><h1>{title}</h1>{body}</body></html>'
    path = folder / f'{safe}.html'
    path.write_text(html, encoding='utf-8')
    script = '\n'.join(f'Scene {i}: {scene}' for i, scene in enumerate(scenes, 1))
    (folder / f'{safe}.txt').write_text(script, encoding='utf-8')
    return {'ok': True, 'html': str(path), 'scenes': len(scenes), 'video': False}
