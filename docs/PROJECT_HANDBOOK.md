# Vishnu 2 AI — Governed Autonomous Intelligence Experiment — Project Handbook

**GitHub repository:** [vaishnavsawant1994-stack/Vishnu-2-AI](https://github.com/vaishnavsawant1994-stack/Vishnu-2-AI)  
**Documentation baseline:** 15 November 2026 · **Assessment type:** code structure, readme, manifests and available evidence—not a fresh production/CI/visual audit.

## 1. Product identity and objective
Separate autonomy/replanning research codebase, not the canonical main Vishnu assistant or the independent Vishnu V1.0 release program.

**Who benefits:** AI autonomy researchers and the repository owner.

## 2. Feature areas and user journeys
1. Goal planning, action/verification and reconciliation concepts.
2. Experimental `evo/` skills, planner and runtime modules.
3. Protected Stop, permission and owner authority kernel design.
4. Staged skill-learning and self-improvement roadmap.

A feature name may denote a documented requirement or source area; actual implemented, wired, and accepted status must be proven separately.

## 3. System architecture and repository map
Python assistant source (`app/`, `core/`, `agent/`, `memory/`, `security/`, `server/`, `tests/`) plus experimental `evo/`; `docs/VISHNU-2-MASTER-ARCHITECTURE.md` documents the distinct Phase 0 gate. Historic imported source still carries `personal-ai` package identifiers and dated infrastructure references.

## 4. Current development and release status
The master design says Phase 0 is incomplete: canonical governed executor/replan-to-PLAN integration must pass exact test criteria. No claim of fully autonomous, self-upgrading, safely deployed intelligence is supported.

**Evidence hierarchy:** observed source and exact-head tests > dated reports > roadmap statements. Live deployment and third-party operations must be independently verified.

## 5. Developer setup and validation
Python >=3.11, virtualenv, `pip install -r requirements.txt`, optional `python -m app.main` local smoke in synthetic environment. Tests/CLI behavior must be checked before allowing any tool execution.

Read configuration carefully; use isolated data, staging credentials and approved migration plans. Presence of a command is not evidence it succeeded today.

## 6. Security, privacy, quality and risk
- Owner Stop must be authoritative in every execution path.
- AI should not define its own tests and promote itself.
- Keep skill admission/rollback and isolation as hard gates.
Every future release should assess access control, input validation, failure modes, monitoring, retention, backup/restore, accessibility and rollback as applicable.

## 7. Next recommended milestones
1. Qualify persisted goal conflict/replan/permission/Stop tests.
2. Complete one end-to-end governed executor.
3. Document evidence for each subsequent Phase 1–10 gate.
4. Verify legacy source provenance and remove stale production claims.

## 8. Authoritative files and records
- [`README.md`](../README.md)
- [`docs/VISHNU-2-MASTER-ARCHITECTURE.md`](../docs/VISHNU-2-MASTER-ARCHITECTURE.md)
- [`docs/TEST_MATRIX.md`](../docs/TEST_MATRIX.md)
- [`docs/CURRENT_PRODUCT_BASELINE.md`](../docs/CURRENT_PRODUCT_BASELINE.md)
- [`evo/`](../evo/)

**Update policy:** revise this handbook when verified source and deployment evidence changes, and retain historical test/qualification records with original dates.
