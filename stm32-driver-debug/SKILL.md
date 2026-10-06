---
name: stm32-driver-debug
description: "Diagnose localized STM32 peripheral or driver failures through actual clocks, pins, registers, HAL/LL state, IRQ/DMA paths and waveforms. Verify exact-part and silicon dependencies rather than applying family-wide recipes."
---

# STM32 Driver Debug

Find the first broken link between requested operation and hardware completion. Reply in the user's language. Treat HAL/LL as source that maps to registers, not as a final diagnosis.

## Start at the failing boundary

Inspect the exact part/package/revision, startup/device header, RCC/init code, HAL/LL source/version, relevant callback and board wiring already available. Capture expected/observed behavior, return/error state and failure point. Ask only for missing device/wiring/waveform facts that change the diagnosis.

Capture state before clearing flags, aborting, resetting or reinitializing. Check read side effects and debugger SFR refresh. Use exact reference manual/datasheet/errata or `datasheet-reader` for device-dependent claims; do not substitute a nearby family.

## Trace the relevant path

`caller -> state/config -> peripheral event -> IRQ/DMA -> driver callback -> consumer`.

Start where evidence shows progress stopped, rather than checking every peripheral in a fixed order:

- **No activity / wrong timing:** inspect power/reset, actual RCC source/mux/readiness, bus and kernel clocks, GPIO/AF or F1 remap, physical pin/package and measured signal. Verify divider encoding and operating mode against the exact manual.
- **Event flag set but no ISR:** inspect source enable, vector symbol, NVIC enable/pending/priority, PRIMASK/BASEPRI/FAULTMASK where applicable, shared vector dispatch and clear/retrigger rules.
- **ISR fires but no callback:** trace handler -> HAL/LL -> handle instance/state -> linked DMA/callback registration -> user implementation. HAL callbacks may also be called in task context; verify callers.
- **DMA incomplete/corrupt:** inspect exact engine/request route, count/width/direction, accessibility, transfer/error flags, completion vs peripheral wire completion, lifetime, CPU reuse and cache-line ownership.
- **HAL_BUSY/timeout or failed restart:** inspect ongoing operation, ownership, timebase progress, abort/error/completion transitions and stale callbacks before forcing reset.

Read [references/peripheral-paths.md](references/peripheral-paths.md) for the applicable DMA/cache, UART, I2C, SPI, ADC or timer branch. Keep hypotheses conditional until code/register/waveform evidence distinguishes them.

## Fix and verify

Choose a focused capture or one-variable experiment that separates leading causes. If a fix is requested and the mechanism is established, patch configuration/code in the correct generated-code preservation region and build. Do not universally deinitialize, disable cache, add delays or reset the peripheral to hide a fault.

Report the broken boundary, evidence, device dependencies, minimal fix and actual validation. For hardware tests specify stimulus, expected register/callback/signal progression and pass/fail criterion; include relevant abort/error/restart behavior. Distinguish a proposed test from a performed test. Use a focused RTOS/fault/memory workflow when evidence localizes that dependency and continue the same task.
