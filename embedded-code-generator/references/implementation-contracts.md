# Implementation contracts

Use the relevant contract to guide implementation and verification, not as a mandatory report template.

## DMA and cache

Define CPU-owned -> prepared -> DMA-owned -> complete/error -> CPU-owned -> reused. Validate the actual DMA engine's reachability and transfer limits, buffer lifetime, width/alignment and circular/half/full-transfer semantics. A task critical section does not stop DMA. Completion callback does not transfer ownership if another transfer has already restarted into that buffer.

On cacheable non-coherent memory, establish cache-line size and actual CMSIS/platform API. TX needs dirty CPU data made visible before DMA. RX needs a safe destination before start and DMA data made visible after completion; merely invalidating after RX can leave a preexisting dirty cache line that overwrites received data while DMA runs. Clean/invalidate details and barriers must follow the platform documentation. Isolate and align owned cache-line ranges; rounding an arbitrary buffer can discard or overwrite adjacent data. Never clean stale RX data over a completed transfer. An MPU non-cacheable mapping or dedicated aligned buffer may be appropriate if consistent with the project.

Abort/recovery must quiesce DMA and callbacks before buffer reuse. Account for stale completion, concurrent timeout and active readers. Use generation IDs or the existing serialization mechanism where the actual race requires it.

## Parsers and ring buffers

Before `offset + length`, check `offset <= size` and `length <= size - offset` using compatible unsigned types. Do not cast unaligned wire bytes to structs; decode with explicit endian helpers or suitable copies. Handle fragmented/concatenated frames, maximum lengths, unknown types, bad checksum and bounded resynchronization. Test malicious/oversized lengths as well as normal traffic.

For a ring define capacity convention (one slot unused vs independent count), full/drop policy, producer/consumer count and ownership. SPSC assumptions cease to hold with a second ISR producer or multiple task consumers. Publish data before advancing the producer index and release a slot only after consumption. Verify atomic width/alignment and memory ordering for the actual target; standard atomics are not automatically lock-free or suitable in an ISR.

## Time and ISR work

Unsigned subtraction supports wrap-safe elapsed time only within the chosen counter interval and observation assumptions. Establish maximum elapsed time/timeout and how often it is checked; it cannot count unobserved multiple wraps. Check ms-to-tick rounding to zero and conversion overflow. A timeout is not bounded if its tick source cannot run in the caller's ISR/critical section.

Preserve incoming interrupt-mask state when a project primitive requires it; do not unconditionally enable IRQs on exit. Defer blocking work and formatting from ISRs. Restore synchronization ownership on every error path; barriers alone do not establish ownership.

## Persistent writes

For requested storage code derive program/erase granularity and execution restrictions from the exact device. Define commit ordering, version/CRC validation, partial-write and power-loss recovery, erase cycling and upgrade compatibility. Verify by interrupting relevant commit phases using the existing test mechanism; a normal write/read test cannot prove torn-write recovery.
