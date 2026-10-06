---
name: freertos-debug
description: "Diagnose localized FreeRTOS scheduling, synchronization, event-loss, timing, stack/heap and ISR-integration failures from task states, API semantics, configuration and traces. Use for known RTOS problems, not unexplained system-wide failures."
---

# FreeRTOS Debug

Reconstruct actual waits, ownership and scheduler state before changing priorities or delays. Reply in the user's language.

## Use the available context

Inspect the relevant tasks/ISRs, synchronization API definitions, FreeRTOSConfig, port and wrappers. Identify kernel version, core/port, task priorities, tick/timebase and allocation model only where relevant. CMSIS-RTOS wrappers may change units, object semantics and callback context.

Classify the immediate symptom: task blocked, Ready but not scheduled, lost/coalesced event, ownership/deadlock, ISR wake latency, tick/timeout issue or memory corruption. Build a compact table of affected tasks: priority, observed state, waiting on, owned resources, measured stack margin and period/deadline. Label source-derived assumptions separately from runtime observations.

## Find the violated contract

1. Trace producer/ISR -> API/return value -> stored count/bits/data -> waiter wake/block -> scheduler -> consumer/release. For deadlock, establish a simultaneous wait-for cycle; for starvation, identify the runnable higher-priority work.
2. Determine whether the primitive preserves state, event count, message data or ownership. A binary semaphore/event bit can coalesce occurrences; a queue of pointers does not preserve buffer contents. Inspect notification action/index and clear behavior, not just API names.
3. Verify actual ISR context, permitted API, priority encoding/grouping, wake flag and port yield path. For Cortex-M priorities and callback/timer restrictions read [references/kernel-semantics.md](references/kernel-semantics.md).
4. Check the tick source, masks/scheduler suspension and timeout units. A blocked task can be correct; a timeout cannot expire if its timebase cannot advance. A standard highest-priority task's `taskYIELD()` does not make lower-priority tasks runnable in preference to it.
5. Inspect return values, object lifetimes, creation failures and overwritten control blocks. Stack/heap corruption can make synchronization look broken; quantify stack evidence before resizing.

## Capture and fix

Prefer existing RTOS-aware debugger snapshots, queue counts, owner/waiter state, targeted sequence records and traces. `uxTaskGetSystemState()` and formatting/statistics facilities can disturb scheduling and need configured support/buffer space; do not invoke heavy task APIs from an ISR or fault handler. Trace coverage/timestamps have limits and cannot automatically remove all ambiguity.

For missing evidence, supply one observation/experiment with outcomes that separate the leading explanations. Complete supported source analysis before asking for a targeted capture. Use `configASSERT`, overflow/malloc hooks or a trace facility when it answers a concrete question.

When a fix is requested, restore the intended synchronization/ownership contract with a focused patch. Validate original trigger, bursts/full queues, timeout/recovery and the relevant timing bound. Separate actual build/host results from target tests still needed. Lead the report with cause/confidence, concrete path or interleaving, fix and validation; avoid a generic RTOS checklist.
