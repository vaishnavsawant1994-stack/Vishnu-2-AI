# Vishnu-2 AI

Vishnu-2 AI is an independent idea council. It takes a raw idea and runs it through four disagreeing voices, then records a reversible decision and the smallest next experiment.

This is not a copy of [vishnu](https://github.com/vaishnavsawant1994-stack/vishnu). Vishnu is a single-owner personal assistant: desktop shell, memory graph, devices, tools, and automation. Vishnu-2 AI does not control the computer, pair devices, or ingest a personal memory graph. Its job is to argue an idea before anyone builds it.

## Different idea

| Vishnu | Vishnu-2 AI |
| --- | --- |
| One assistant with autonomy modes | Four-voice council: Preserver, Builder, Critic, Operator |
| Desktop and mobile control surface | Local web console |
| Memory, knowledge, devices, tools | Idea ledger: claim, dissent, decision, experiment |
| Acts on files, browser, system | Does not act on the machine |

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

Open http://127.0.0.1:8787

The council works offline with a structured heuristic. Set `VISHNU2_MODEL_BASE_URL` and `VISHNU2_MODEL_API_KEY` only if you want an OpenAI-compatible model to rewrite the four voices. Secrets stay in the environment, never in git.

## Layout

- `app/main.py` — local FastAPI console and API
- `app/council.py` — Preserver, Builder, Critic, Operator
- `app/store.py` — SQLite idea ledger
- `tests/` — council and store checks

## License

MIT. Original work for this repository. No Vishnu source is included.
