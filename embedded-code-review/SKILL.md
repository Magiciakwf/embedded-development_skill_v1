---
name: embedded-code-review
description: "Review existing embedded C/C++ firmware or diffs for reachable correctness, memory, protocol, ISR/RTOS, DMA, timing, and Flash/OTA defects. Use for read-only, evidence-backed bug review; not implementation or open-ended runtime troubleshooting."
---

# Embedded Code Review

Review the requested scope for defects that can occur on the actual target. Reply in the user's language. Do not modify the project or generate build artifacts. Zero supported findings is valid.

## Focused review workflow

1. **Establish context selectively.** Identify the MCU, active build configuration, RTOS/SDK, and task/ISR/boot context only where relevant. Distinguish committed configuration from the actual built image; a host GCC check is not an ARMCC/Keil build.
2. **Start narrow.** For a diff, inspect changed lines and necessary callers. For a named module, trace reachable inputs and outputs. For an open-ended review, prioritize user-owned entry points and high-risk data, interrupt, and recovery paths; avoid wholesale vendor-library reading.
3. **Fast first pass.** In relevant paths check bounds, length/offset arithmetic, pointer lifetime, integer conversions, `switch` fall-through, error handling, and protocol validation. Include synchronization, DMA ownership, Flash alignment/partition bounds, and OTA state transitions when applicable. Do not apply every check to every file.
4. **Trace and refute candidates.** Follow only the callers, consumers, configurations, and failure paths needed to confirm a suspected defect. Reuse evidence instead of rereading unchanged files. For a complex domain, read only the relevant sections of [references/review-evidence.md](references/review-evidence.md).
5. **Stop on purpose.** Cover all explicitly requested paths. For an open-ended review, once key paths and strong findings have been checked, report coverage and blind spots instead of expanding indefinitely. About 3–5 confirmed findings is a checkpoint, **not** a hard cap or an excuse to skip requested exhaustive coverage.

## Proof and output

For each finding show `reachable trigger -> execution path/interleaving -> violated contract -> realistic consequence`. Check counterevidence such as caller bounds, excluded builds, locks, and device semantics. Distinguish **confirmed defects**, **conditional risks**, and **unresolved questions**; do not turn missing evidence into high severity.

Lead with the conclusion, then report each actionable issue with **severity, file:line, trigger/path, consequence, and minimal safe fix**. Show an interleaving for races and a targeted validation when needed. Group issues with the same root cause. State what was reviewed, skipped, compiled, or tested; never claim unperformed verification. Exclude generic style, `volatile`, NULL, stack, or HardFault warnings without a reachable mechanism. Remain read-only unless separately authorized to fix code.
