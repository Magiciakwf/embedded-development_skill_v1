---
name: embedded-code-review
description: "Review embedded C/C++ changes or existing firmware for reachable, evidence-backed correctness, concurrency, ISR, DMA, timing and storage defects. Use for review findings, not unsolicited rewrites or broad runtime triage."
---

# Embedded Code Review

Review the requested scope for defects that can manifest on the actual target. Reply in the user's language. Prioritize a few supported findings; zero findings is a valid outcome.

## Establish scope and runtime paths

For a diff/PR/commit, review changed code first and follow relevant callers, definitions and configuration. For a full review, prioritize user-named modules and reachable data/interrupt paths. Honor the provided scope; do not broaden into a repository rewrite.

Inspect the target, build configuration, RTOS/SDK version and execution context only as needed to assess a candidate finding. Model producer, consumer, object lifetime, ownership, priority/preemption and error/recovery transitions. Repository macro names alone do not establish register side effects; consult exact documentation when material.

## Prove each candidate

Use `reachable trigger -> execution path/interleaving -> violated contract -> runtime consequence`.

- Memory/arithmetic: show the input/state reaching the out-of-bounds access, truncation, overflow, invalid shift, alignment or lifetime violation. Check actual types and caller guarantees.
- Shared state: show the unsafe interleaving, masks/locks and actual asynchronous writers. `volatile` neither makes a transaction atomic nor transfers DMA ownership.
- ISR/RTOS: establish the calling context, API contract, configured priorities and blocked/wake behavior. A missing immediate ISR yield may be a latency issue; do not mechanically report it after every `FromISR` call.
- MMIO/DMA: check documented read/write side effects, accessibility, lifetime, reuse and cacheability on the actual device. A task lock does not stop DMA.
- Timing/storage: establish the deadline, blocking bound, tick assumptions, erase/program contract or torn-write mechanism rather than generic risk.

For deeper review of relevant domains read [references/review-evidence.md](references/review-evidence.md). Do not load or walk every domain by default.

Actively look for a refutation: bounds enforced by callers, excluded build paths, hardware atomicity, established ownership, correct cache mapping or a lock you initially missed. Group multiple symptoms of the same defect. Separate conditional questions from confirmed findings. Never raise severity to compensate for missing evidence.

## Deliver actionable findings

Lead with the overall conclusion; list actionable defects by realistic impact and likelihood. Each needs a precise file/line or symbol, trigger, violated invariant, consequence and minimal fix. Include an explicit interleaving for races and a focused validation when useful. Use the repository/request severity scheme; absent one, reserve Critical for credible severe system impact, High for realistic functional failure, Medium/Low for narrower or limited impact. A possible HardFault alone does not automatically make a finding Critical.

Place unknown device/configuration dependencies under unresolved questions with the exact evidence needed. Say when no credible defect was found and note material coverage limits. Do not emit repetitive counts, empty sections, style complaints or ungrounded NULL/stack/cache warnings. A review request does not by itself request applying patches.
