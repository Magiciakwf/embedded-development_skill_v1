# Evidence collection and experiments

## Unexplained reset

Capture reset cause early, before HAL/startup clears it; document flag history. Correlate watchdog, brownout, NRST, fault record and firmware boot ID. Sticky reset flags can coexist and do not order causes. A missing fault log can mean failed capture, retention failure or reset before commit.

Retained RAM needs linker placement, startup exclusion from zero/copy initialization, hardware retention for this reset/power mode, and cache persistence if relevant. `.noinit` alone does not guarantee survival. Include magic/version, build ID, sequence and integrity check; mark a record committed only after payload completion. Concurrent writers and a reset mid-write must not yield a deceptively valid mixed record. Avoid blindly reusing data across builds.

## Hang without an exception

Determine whether the CPU is looping, waiting, interrupt-storming, masked, fault-locking or stopped by the debugger. Capture current instruction/backtrace, task wait/owner relationships, masks and pending IRQs. If ticks stop, inspect masking and timebase before assuming a mutex deadlock. If tasks stop but IRQs continue, inspect scheduler suspension, Ready tasks and highest-priority loops.

Observe power/reset lines when software evidence does not account for a reset. Disabling the watchdog can help expose the stalled context, but changes the experiment and cannot establish a production fix.

## Timing-sensitive corruption

Record event sequence numbers, buffer/index ownership and preemption boundaries; select a watchpoint on the earliest corrupted object rather than the eventual crash location. Check watchpoint coverage/width and DMA observability: a CPU watchpoint need not catch DMA writes. DWT/trace is optional and device-dependent.

Use fixed-size event records, bounded ring writes, GPIO markers or existing trace before synchronous formatting. Establish overflow policy, timestamp wrap/frequency and writer synchronization. Breakpoints, semihosting, retained logs and instrumentation can alter timing. A race masked by logging remains unresolved.

## Experiment record

`Question | baseline/build | one change | prediction | observed signature | exposure | conclusion | next action`.

Compare relevant board/build/voltage/load conditions, not a combinatorial matrix. For rare failures use comparable hours, events or cycles, not just pass counts. `0 failures in N hours` bounds observations under that workload; it is not an assertion that the rate is zero. Preserve known counterexamples. A timing workaround warrants a different confidence label from direct evidence of ownership violation or memory overwrite.
