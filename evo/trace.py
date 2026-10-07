"""Step tracker for a turn."""

from __future__ import annotations

from time import perf_counter


class ExecutionTrace:
    def __init__(self):
        self.started = perf_counter()
        self.steps: list[dict] = []

    def add(self, name: str, detail: str, status: str = 'completed') -> None:
        self.steps.append({
            'name': name,
            'detail': detail[:240],
            'status': status,
            'ms': int((perf_counter() - self.started) * 1000),
        })

    def export(self) -> dict:
        return {'steps': self.steps, 'count': len(self.steps)}
