# Vishnu-2 AI architecture

Vishnu-2 AI is a local idea ledger with a council in front of it.

```text
Web console
    |
FastAPI
    |
Idea store (SQLite) ---- Council
                          |-- Preserver  what must not break
                          |-- Builder    how it could exist
                          |-- Critic     strongest objection
                          |-- Operator   smallest reversible experiment
```

An idea moves `seed -> debated -> decided` or `parked`. A decision stores the claim, the dissent that survived, and one experiment that can falsify the claim. Nothing in this path launches apps, reads the screen, or calls device tools.

Model use is optional and replaceable. The heuristic council is the default so the product still works with no provider configured.
