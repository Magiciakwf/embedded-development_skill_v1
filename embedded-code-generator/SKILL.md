---
name: embedded-code-generator
description: "Implement or extend embedded C/C++ drivers, protocol logic, state machines, buffers and RTOS modules in an existing firmware project. Use for requested code changes; preserve target contracts and verify integration rather than returning an unintegrated example."
---

# Embedded Code Generator

Implement the requested behavior in the project and verify it as far as available tools allow. Reply in the user's language. Follow existing architecture and conventions.

## Establish the integration contract

Inspect repository instructions, build configuration, target/device headers, a neighboring module and the relevant callers/IRQ/startup paths. Identify exact target/toolchain, HAL/SDK/RTOS version, execution contexts, buffer ownership, timing/resource bounds and error conventions only where material.

Derive acceptance criteria from the request. Infer routine choices from project conventions; ask only when missing hardware/interface/concurrency facts would materially change correctness. Complete independent logic while a device fact is unresolved. Never invent registers, pins, AFs, DMA mappings or IRQ names. Consult exact documentation or `datasheet-reader` when necessary.

## Implement

- Define the public API and ownership contract: who owns input/output, whether pointers survive return, completion/cancellation, blocking bounds, overflow policy and error propagation. Use the established allocation and synchronization model.
- For asynchronous code, define start/completion/error/timeout/abort/restart state transitions. Ensure only the winning terminal path publishes completion and hardware stops using a buffer before release/reuse. Distinguish partial transfers from successful completion.
- For task/ISR/CPU/DMA sharing, trace producer -> publication -> consumer -> release. `volatile` does not provide atomicity, synchronization or cache coherence. A lock-free design needs proven ordering, supported atomic operations and interrupt-safe bounded behavior; otherwise use the project's appropriate primitive.
- Preserve MMIO access semantics, flag-clear sequence, clock/init order and reserved-bit rules. Do not use generic read-modify-write on side-effect registers.
- For protocols, validate lengths without overflowing intermediate arithmetic, preserve endian/alignment rules and recover from malformed/truncated frames with bounded work. For timers, establish tick width, units and wrap assumptions.
- Read [references/implementation-contracts.md](references/implementation-contracts.md) only for applicable DMA, parser/buffer, persistent-storage or timing contracts. Keep the patch focused; do not add tasks, layers, dependencies or a redesign merely for convenience.

## Integrate and verify

Wire source files into the actual build and connect init, IRQ/callback, configuration and teardown paths. Avoid edits outside generated-code preservation regions. New declarations must have definitions and real callers where needed. Do not leave example code or unresolved hardware placeholders advertised as complete.

Run the project's relevant build/checks when available. For nontrivial pure logic add focused behavioral tests for boundaries and recovery; do not mirror implementation details or build a new test framework for a trivial reversible edit. Prefer the real target build over a host syntax-only check; host tests cannot establish MMIO/DMA timing.

Review the final diff for ownership, races, timeout/error paths, arithmetic and material memory/latency costs. Report changed behavior/files, actual commands/results and remaining assumptions. Separate implemented, build verified, host tested and target verified. For target-only behavior provide stimulus, expected signals/state and pass/fail criteria. Do not claim hardware validation without hardware evidence.
