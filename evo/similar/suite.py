"""One original run of the safe jobs. Not a port of any studied repo."""

from __future__ import annotations

from pathlib import Path

from evo.similar.design import review
from evo.similar.story import write_story
from evo.similar.work import assign, comment, create_task
from evo.board import retain


def run_suite(work: Path, title: str) -> dict:
    note = f'# {title}\nThe user clicks save. Show an error if empty. Max 200 characters.'
    checked = review(note)
    task = create_task(work, title)
    comment(work, task['id'], 'Suite opened the job')
    assign(work, 'builder', 'full-stack', task['id'])
    retain(work, f'{title} started')
    story = write_story(work, title, ['Open the job', 'Do the work', 'Show the result or the error'])
    return {
        'ok': checked['ok'] and story['ok'],
        'tool': 'similar_suite',
        'task_id': task['id'],
        'design_ok': checked['ok'],
        'story': story['html'],
        'video': False,
        'voice_clone': False,
        'download': False,
    }
