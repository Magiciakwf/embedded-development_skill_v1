# Specialized Review Evidence

Use only sections relevant to a concrete candidate. These checks do not require scanning every subsystem.

## C, buffers and protocols

Trace input size through framing, parsing, copy/queue, buffer capacity, and consumer. Check zero, maximum, truncated, malformed, and repeated packets; compare sender/receiver limits. A queued pointer does not copy its pointee. For segmented transfers track cumulative offsets, including odd-length chunks before aligned accesses. Check reachable `switch` fall-through, integer narrowing, invalid shifts, pointer lifetime, and unchecked error returns. Distinguish dormant code from an active failure path.

## RTOS, ISR and ownership

Identify readers/writers, execution contexts, publication, and resource ownership. Prove feasible interleavings, priority/critical-section behavior, lock ordering, and release on error. A wait-for cycle is deadlock only if its edges can coexist. Validate interrupt priorities against the actual FreeRTOS port and API contracts. `volatile` is not a lock; mutexes do not exclude DMA/ISRs. Notifications/events may coalesce; report loss only if every occurrence matters. A missing immediate `FromISR` yield can be latency rather than correctness. `taskYIELD()` does not guarantee a lower-priority ready task runs.

## DMA, MMIO, timing and memory

Follow DMA buffer placement, accessibility, start/completion, CPU access, and reuse. Cache issues require an enabled data cache and cacheable region; consider cache-line sharing and pre/post-transfer maintenance. Verify the exact register's W1C/W0C/read-to-clear and interrupt semantics; macro names alone are insufficient. For deadlines establish a real bound, priority, tick units, wraparound, and required latency. A blocking call or large local array does not by itself prove failure; stack claims need allocation/call-path or measured-watermark evidence.

## Flash, OTA and persistent recovery

Verify device-specific erase size, programming width/alignment, legal bit transitions, and partition limits across *successive* chunks. Trace Bootloader–APP candidate selection, testing, confirmation, reset, retry, fallback, and subsequent boot. A rollback must persist; confirmation must satisfy the intended health criterion. Watchdog-based recovery requires an enabled watchdog and feasible feeding/timeout behavior. For metadata, check power cuts between erase and each write, valid-marker order, CRC/version, redundant-copy selection, and fallback for partly valid records. Distinguish recoverable hangs from irreversible loss. CRC/MD5 corruption checks do not prove firmware authenticity.

## Targeted validation

Propose the smallest experiment resolving a specific uncertainty: malformed frame, first misaligned write, exact IRQ priority, DMA address, power cut during metadata commit, or the next boot after rollback. Distinguish observations, source deductions, and untested hypotheses; avoid generic logging or stress-test prescriptions.
