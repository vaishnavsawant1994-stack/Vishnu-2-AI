# Vishnu 2 AI

**Separate experimental autonomy project.** This repository is not the canonical [Vishnu personal AI](https://github.com/vaishnavsawant1994-stack/vishnu) repository and is not the independently managed Vishnu V1.0 Windows/Web release track.

## Purpose and source boundary

The [Vishnu 2 master architecture](docs/VISHNU-2-MASTER-ARCHITECTURE.md), adopted 8 October 2026, specifies a persistent, owner-governed intelligence that can plan, execute, verify, reconcile, learn and improve bounded capabilities without modifying its constitutional security controls. The codebase includes historical personal-assistant components and an experimental `evo/` tree; source presence is not evidence of operational autonomy or a released product.

Some older files were carried forward from Vishnu/Personal AI and refer to historical Railway branches, old GitHub accounts or past deployment decisions. **These references are historical evidence, not the current source of truth for this repository.** No production deployment, third-party API, security gate or physical-device test was requalified during the 14 November 2026 documentation audit.

## Current engineering gate

- **Phase 0 remains incomplete** according to the adopted architecture: the persisted-goal conflict/replan path must pass through the same canonical governed executor and reach a verified PLAN state.
- The architecture records replan machinery on `main`, with a full executor integration not yet established end to end.
- Stop, owner authority, permission checks, durable audit, verification, isolation and rollback are non-negotiable gates; later skill-learning/self-improvement phases cannot be declared complete in advance.
- A design or checkpoint document describes intended behavior and dated observations, not automatically the state of the latest commit.

See [Master Architecture](docs/VISHNU-2-MASTER-ARCHITECTURE.md), [Product Name (historical)](docs/PRODUCT_NAME.md), [Current Product Baseline (historical)](docs/CURRENT_PRODUCT_BASELINE.md) and [Tests Matrix](docs/TEST_MATRIX.md).

## Repository contents

- `evo/`: experimental planners, skill/tool modules, governed execution and replan-related components.
- `core/`, `agent/`, `models/`, `memory/`, `knowledge/`, `security/`, `server/`, `app/`, `desktop/` and `ui/`: historical and current assistant/runtime source, subject to verification.
- `docs/`: architecture, checkpoints, qualification plans and known blockers.
- `tests/`: validation assets; their presence does not prove a current passing release.

## Local developer bootstrap (not a release qualification)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Set only disposable local test values in an untracked .env, where needed.
python -m app.main
```

Run tests and inspect provider/storage configuration before executing actions. Avoid using live credentials or production personal data in development. A working local shell must not be described as a verified autonomy release.

## Security and provenance

This is a public source repository. Never commit keys, personal data, signing material, device identities or owner vault data. Historical import and qualification references are preserved for provenance, but current deployments and GitHub ownership must be verified independently before use.

## Detailed project guide

The [**Project Handbook**](docs/PROJECT_HANDBOOK.md) describes the repository's specific goals, users, source architecture, functional areas, current qualification limits, development setup, security requirements and next milestones. It differentiates implemented source from unverified or planned functionality.
