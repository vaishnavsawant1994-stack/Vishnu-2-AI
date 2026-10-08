# Vishnu 2 AI — Canonical Master Architecture

Status: master design specification. Adopted 2026-10-08.
Source: owner-approved A-to-Z blueprint.

## Definition

Vishnu 2 is a persistent autonomous digital intelligence that understands goals, plans, remembers, researches, learns missing capabilities, creates and tests skills, uses tools, writes and debugs code, verifies real results, and improves non-protected components. It remains subordinate to an owner-controlled constitutional kernel.

No repository can contain every future API. The objective is the ability to discover, learn, test, qualify, install, and use capabilities that do not exist yet.

## Constitutional kernel

Owner identity, root authentication, Stop, root credential vault, root permission kernel, qualification authority, rollback authority, and audit integrity stay outside self-modification.

Stop always wins. Vishnu cannot clear, redefine, route around, or exempt an agent or skill from Stop.

## Design laws

1. Goals outrank plans. Owner-approved completion criteria do not change because a strategy is hard.
2. Reality outranks claims: observed external state, then verifier evidence, then tool output, then planner assertion.
3. Unknown is not failure.
4. An interrupted mutation is reconciled before it is repeated.
5. One meaningful action, then observe.
6. A candidate cannot define the exam, grade it, and promote itself.
7. Required isolation cannot be silently weakened.
8. A critical security failure is a hard gate.
9. Every action source uses one governed execution boundary.
10. The mind cannot own Stop.

## Current gate — Phase 0

Do not start skill learning, new sandbox backends, self-upgrade, specialist agents, or more autonomy features until this is green on canonical main.

Required path:

CONFLICTED → canonical executor → advance(REPLAN) → real persisted goal → revision 2 or the existing revision 2 → one revised step → PLAN → same governed executor.

CI must prove:

1. Conflict becomes revision 2 and returns to PLAN.
2. The same conflict, including after restart, stays revision 2.
3. No active goal becomes BLOCKED, with no invented goal.
4. Permission denial does not execute the revised step.
5. Stop does not execute the revised step and remains authoritative.

The revised step must use the same Stop, permission, operation key, execution, verification, reconciliation, and failure-classification path as an ordinary step.

Current status: replan machinery is on main. The complete executor hook is local only. Canonical live loop is not end-to-end complete.

## Native operating system

Mind, goals, planner, verifier, reconciler, memory, knowledge, learning, capability registry, skill registry, sandbox manager, policy engine, Stop, audit, model router, tool router, agent runtime, recovery, qualification, and rollback.

## Skill layer

GitHub, Railway, Vercel, email, calendar, cloud providers, and future APIs stay skills. A skill has a manifest, schemas, permissions, isolation requirement, tests, verification, rollback, provenance, and health.

## Later phases, after Phase 0

1. Receipts, provider reconciliation, states, failure taxonomy, criterion verifiers, recovery.
2. Capability check: AVAILABLE, PARTIAL, MISSING, UNKNOWN.
3. First autonomous skill-learning loop, then resume the original goal.
4. Stronger isolation backends when they actually exist.
5. Skill self-repair.
6. Frozen benchmarks.
7. Controlled self-improvement of non-protected zones.
8. Specialist agents.
9. Staging, canary, and rollback.
10. Continuous improvement inside the owner envelope.

## Unknown is not the end

A missing qualified capability becomes research, a candidate skill, sandbox admission, tests, security qualification, frozen-baseline comparison, registration, and resumption of the original goal. If isolation is insufficient, the result is INSUFFICIENT_ISOLATION and the goal stays fixed.
