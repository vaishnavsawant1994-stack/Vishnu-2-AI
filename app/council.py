"""Four disagreeing voices. Offline by default."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Voice:
    name: str
    stance: str
    text: str


@dataclass(frozen=True)
class CouncilResult:
    voices: list[Voice]
    decision: str
    dissent: str
    experiment: str
    source: str


def debate(title: str, seed: str) -> CouncilResult:
    """Return a structured council. Model rewrite is optional and must not be required."""
    base = _heuristic(title.strip(), seed.strip())
    if os.getenv("VISHNU2_MODEL_BASE_URL") and os.getenv("VISHNU2_MODEL_API_KEY"):
        rewritten = _try_model(title, seed, base)
        if rewritten is not None:
            return rewritten
    return base


def _heuristic(title: str, seed: str) -> CouncilResult:
    subject = title or "this idea"
    detail = seed or "No supporting note was given."
    voices = [
        Voice(
            "Preserver",
            "protect",
            f"Do not let {subject} erase a working promise. Keep the current user path intact until the new claim is proven.",
        ),
        Voice(
            "Builder",
            "make",
            f"{subject} can exist as one narrow loop: capture the claim, show the objection, and record the next step. Note: {detail}",
        ),
        Voice(
            "Critic",
            "oppose",
            f"The weakest point is evidence. {subject} is still a preference until someone can name who it is for and what would prove it wrong.",
        ),
        Voice(
            "Operator",
            "test",
            f"Run one 48-hour trial of {subject} with a single user and a written fail condition. Stop if the fail condition hits.",
        ),
    ]
    return CouncilResult(
        voices=voices,
        decision=f"Park build work on {subject} until the Operator trial has a named user and a fail condition.",
        dissent="Critic: there is not yet evidence that anyone wants this beyond the author.",
        experiment=f"Ask one real user to try {subject} for two days. Fail if they do not return to it unprompted.",
        source="heuristic",
    )


def _try_model(title: str, seed: str, fallback: CouncilResult) -> CouncilResult | None:
    """Best-effort rewrite. Any failure keeps the offline council."""
    try:
        import httpx
    except ImportError:
        return None
    base = os.environ["VISHNU2_MODEL_BASE_URL"].rstrip("/")
    key = os.environ["VISHNU2_MODEL_API_KEY"]
    model = os.getenv("VISHNU2_MODEL_NAME") or "gpt-4o-mini"
    prompt = (
        "Rewrite this idea council in four short voices: Preserver, Builder, Critic, Operator. "
        "Then give decision, dissent, and experiment. No tools. No computer control.\n"
        f"Title: {title}\nSeed: {seed}\nFallback: {fallback.decision}"
    )
    try:
        response = httpx.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.4},
            timeout=20.0,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None
    return CouncilResult(
        voices=fallback.voices,
        decision=text[:1200],
        dissent=fallback.dissent,
        experiment=fallback.experiment,
        source="model",
    )
