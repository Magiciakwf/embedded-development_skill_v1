---
name: embedded-bug-investigator
description: "Investigate embedded resets, hangs, corruption and intermittent or timing-sensitive failures while the causal subsystem is unknown. Use hypothesis-driven experiments; switch to focused fault, RTOS, peripheral or memory analysis once evidence localizes the problem."
---

# Embedded Bug Investigator

Find a supported causal mechanism, then fix it if the user requested a fix. Reply in the user's language. A disappearing symptom is evidence, not proof.

## First pass

Inspect the available repository, logs and artifacts. Extract build/board identity, measurable symptom, trigger, failure frequency, time to failure and recovery. Ask only for missing details that change the next diagnostic decision; do not require a full intake before using supplied evidence.

Preserve the failing build and failure state before changes. Separate observations, interpretations and hypotheses. A watchdog reset identifies the recovery mechanism, not why forward progress stopped. Verify reset flags were captured before clearing and do not confuse a stale crash record with this boot.

## Drive the investigation

1. Reconstruct the shortest useful timeline around the failure. Use reset/fault evidence, task state, DMA ownership, registers or measurements as applicable. Log order alone does not establish a scheduler order.
2. Rank only credible competing explanations. For each record supporting/contradicting evidence and the observation that would distinguish it. Prefer a few high-value hypotheses over a subsystem checklist.
3. Choose the cheapest discriminating experiment: one meaningful variable, controlled baseline, expected outcomes, exposure budget and instrumentation impact. Define what a negative result means; an unreproduced intermittent failure need not reject the hypothesis.
4. Run experiments/builds supported by available tools and the user's scope. If hardware is unavailable, complete static analysis and deliver the precise capture or test procedure. Never fabricate execution results.
5. Update the hypothesis ranking after new evidence. Keep a compact investigation note only for a sustained investigation; reuse prior experiments rather than restarting. For capture design, reset/hang triage and intermittent exposure read [references/evidence-and-experiments.md](references/evidence-and-experiments.md).

Do not combine unrelated stack, priority, optimization, delay and DMA changes into a purported causal test. If a diagnostic perturbation suppresses the failure, preserve it as a clue and distinguish it from a production fix.

## Localize and close

When evidence narrows the question, use a focused skill if available: `hardfault-analyzer` for exception context, `freertos-debug` for scheduler/synchronization, `stm32-driver-debug` for peripheral paths, `firmware-memory-analyzer` for placement/capacity, or `datasheet-reader` for device facts. This is a workflow transition in the same task, not permission to spawn agents or abandon the repair. Carry forward facts, timeline, experiments and uncertainties. A code-review skill serves review requests; a localized runtime defect can be fixed directly.

Report `trigger -> mechanism -> invalid state -> failure`, confidence and evidence. Apply the narrow correction when requested and justified; verify original stress, relevant error paths and collateral effects. For intermittent faults report before/after counts and comparable exposure. If evidence is insufficient, lead with the next decisive experiment and expected observations rather than inventing a root cause. Omit empty report sections.
