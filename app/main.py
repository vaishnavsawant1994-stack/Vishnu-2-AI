"""Local console for the Vishnu-2 AI idea council."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.council import debate
from app.store import add_idea, connect, decide, get_idea, list_ideas, save_council

DATA = Path(os.getenv("VISHNU2_DATA_DIR", "./data"))
DB = DATA / "ideas.sqlite3"

app = FastAPI(title="Vishnu-2 AI", version="0.1.0")


class IdeaIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    seed: str = Field(default="", max_length=4000)


class DecisionIn(BaseModel):
    status: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return PAGE


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "product": "Vishnu-2 AI"}


@app.get("/api/ideas")
def ideas() -> list[dict]:
    with connect(DB) as conn:
        return list_ideas(conn)


@app.post("/api/ideas")
def create_idea(body: IdeaIn) -> dict:
    with connect(DB) as conn:
        return add_idea(conn, body.title, body.seed)


@app.post("/api/ideas/{idea_id}/council")
def run_council(idea_id: int) -> dict:
    with connect(DB) as conn:
        try:
            idea = get_idea(conn, idea_id)
        except KeyError:
            raise HTTPException(404, "idea not found") from None
        result = debate(idea["title"], idea["seed"])
        saved = save_council(conn, idea_id, result)
        saved["voices"] = [voice.__dict__ for voice in result.voices]
        return saved


@app.post("/api/ideas/{idea_id}/decision")
def set_decision(idea_id: int, body: DecisionIn) -> dict:
    with connect(DB) as conn:
        try:
            return decide(conn, idea_id, body.status)
        except KeyError:
            raise HTTPException(404, "idea not found") from None
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from None


def main() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("VISHNU2_HOST", "127.0.0.1"),
        port=int(os.getenv("VISHNU2_PORT", "8787")),
        reload=False,
    )


if __name__ == "__main__":
    main()


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Vishnu-2 AI</title>
  <style>
    :root { color-scheme: dark; --ink:#e8e4d9; --muted:#9a917f; --line:#3a3428; --gold:#d6b15a; --bg:#14120e; }
    body { margin:0; font:16px/1.5 Georgia, serif; background:var(--bg); color:var(--ink); }
    main { max-width:820px; margin:0 auto; padding:40px 20px 80px; }
    h1 { font-weight:500; letter-spacing:.04em; margin-bottom:0; }
    p.lead { color:var(--muted); margin-top:8px; }
    form, article { border:1px solid var(--line); padding:16px; margin-top:18px; }
    label { display:block; color:var(--muted); font-size:13px; margin-top:10px; }
    input, textarea { width:100%; box-sizing:border-box; background:#1c1914; color:var(--ink); border:1px solid var(--line); padding:8px; font:inherit; }
    button { margin-top:12px; background:transparent; color:var(--gold); border:1px solid var(--gold); padding:8px 12px; font:inherit; cursor:pointer; }
    .status { color:var(--gold); font-size:13px; letter-spacing:.08em; text-transform:uppercase; }
  </style>
</head>
<body>
  <main>
    <h1>Vishnu-2 AI</h1>
    <p class="lead">An idea council. Four voices argue the claim before anything is built.</p>
    <form id="new">
      <label>Idea title</label>
      <input name="title" required maxlength="160" placeholder="A weekly decision room for unfinished ideas" />
      <label>Seed note</label>
      <textarea name="seed" rows="4" maxlength="4000" placeholder="Who it is for, and what is still uncertain."></textarea>
      <button type="submit">File the idea</button>
    </form>
    <section id="list"></section>
  </main>
  <script>
    const list = document.querySelector('#list');
    async function load() {
      const ideas = await fetch('/api/ideas').then(r => r.json());
      list.innerHTML = ideas.map(idea => `
        <article>
          <div class="status">${idea.status}</div>
          <h2>${escapeHtml(idea.title)}</h2>
          <p>${escapeHtml(idea.seed || '')}</p>
          ${idea.decision ? `<p><strong>Decision.</strong> ${escapeHtml(idea.decision)}</p>` : ''}
          ${idea.dissent ? `<p><strong>Dissent.</strong> ${escapeHtml(idea.dissent)}</p>` : ''}
          ${idea.experiment ? `<p><strong>Experiment.</strong> ${escapeHtml(idea.experiment)}</p>` : ''}
          <button data-council="${idea.id}">Run council</button>
          <button data-status="decided" data-id="${idea.id}">Accept</button>
          <button data-status="parked" data-id="${idea.id}">Park</button>
        </article>
      `).join('');
    }
    function escapeHtml(value) {
      return String(value).replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));
    }
    document.querySelector('#new').addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = new FormData(event.target);
      await fetch('/api/ideas', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({title:data.get('title'), seed:data.get('seed')})});
      event.target.reset();
      load();
    });
    list.addEventListener('click', async (event) => {
      const council = event.target.dataset.council;
      const status = event.target.dataset.status;
      if (council) await fetch(`/api/ideas/${council}/council`, {method:'POST'});
      if (status) await fetch(`/api/ideas/${event.target.dataset.id}/decision`, {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({status})});
      if (council || status) load();
    });
    load();
  </script>
</body>
</html>
"""
