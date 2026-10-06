# Evidence for specialized findings

## Concurrency and ownership

Identify readers/writers, context and publication/release points. Explain a concrete interleaving, including whether a higher-urgency interrupt bypasses the RTOS critical section. Check multi-producer assumptions, lock ordering and releases on cancellation/error. A wait-for cycle is deadlock evidence only if its edges coexist. Priority inheritance applies to the relevant mutex/port semantics, not to every signaling object.

Queues copy their configured item size; a queued pointer does not copy its pointee. Prove when the producer reuses/frees the object before consumption. Notification bits/events can coalesce; counting or mailbox APIs have different semantics. Report event loss only when every occurrence must be preserved.

## DMA and MMIO

Trace buffer address from allocation/linker output to DMA engine, start, completion, processing and reuse. Cache defects require actual enabled data cache and cacheable mapping. Assess RX pre-transfer dirty lines as well as post-transfer invalidation and cache-line sharing. Never universalize a family-wide DMA memory prohibition; consult the actual bus matrix/engine.

W1C/W0C/read-to-clear/write-only/mixed registers require exact semantics. Account for debugger observation effects and IRQ reassertion. A missing `volatile` finding requires an actual MMIO/asynchronous access problem; adding it does not fix synchronization.

## Time and resource bounds

For deadline findings cite priorities, a blocking/worst-case bound and required latency. A valid task wait is not a defect. A highest-priority task's `taskYIELD()` does not guarantee a lower-priority task runs in the standard fixed-priority scheduler.

For time arithmetic establish counter width, types, wrap horizon, units and observation frequency. Subtraction-based elapsed checks still require a bounded interval; deadline ordering can require stricter half-range assumptions. Check zero-tick rounding and conversion overflow.

A large local array is not proof of overflow. Establish configured stack, reachable call depth, compiler stack reports or measured margin and interrupt-stack contribution. High-water marks depend on executed paths and written bytes; untouched stack reservations can overstate margin.

## Persistence and recovery

Prove illegal erase/program alignment, execution restrictions or power-loss commit ordering from code and exact storage specifications. Distinguish immediate corruption, recoverability and endurance. Review bootloader/application boundaries, commit metadata, CRC/version, sequence wrap and recovery after interrupted writes where relevant.

## Validation questions

Every recommended check should resolve a named uncertainty: inspect one IRQ's priority and actual RTOS threshold; watch the first overwritten address; compare buffer VMA with the DMA bus map; drive maximum/truncated input through a parser; interrupt a specific commit phase. Avoid generic requests to add logging or stress everything.
