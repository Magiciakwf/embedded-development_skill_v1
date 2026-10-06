---
name: hardfault-analyzer
description: "Analyze observed Cortex-M HardFault, MemManage, BusFault and UsageFault evidence using raw status registers, trustworthy exception frames and the matching ELF/MAP. Select architecture-specific semantics; do not diagnose from the exception name alone."
---

# HardFault Analyzer

Decode captured evidence before guessing causes. Reply in the user's language. A fault classification identifies a mechanism, not necessarily its originating defect.

## Obtain trustworthy evidence

Inspect available crash dumps, target/build identity and matching ELF/MAP first. Establish exact core/architecture, handler-entry LR (`EXC_RETURN`), faulted MSP/PSP, raw frame and implemented status/address registers. Do not request unsupported CFSR/HFSR on M0/M0+. TrustZone/Armv8-M banked stacks and security frames require the exact architecture documentation.

Preserve register values before clear/reset. Registers can be sticky or stale. Read [references/cortex-m-fault-registers.md](references/cortex-m-fault-registers.md) for verified Armv7-M bits/frame rules and [references/capture-and-symbols.md](references/capture-and-symbols.md) when obtaining a frame or symbolizing a dump.

The bundled stdlib decoder handles the Armv7-M register model and checks input bounds, address validity, frame caveats and xPSR Thumb state:

```text
python scripts/decode_hardfault.py --cfsr 0x8200 --hfsr 0x40000000 --bfar 0x40000000 --exc-return 0xFFFFFFFD --pc 0x08001234 --xpsr 0x01000000 --json
```

Its output is decoded evidence and cautions, not automatic root-cause confirmation. Do not apply its frame offsets to Armv8-M security transitions.

## Analyze

1. Decode all asserted implemented bits, escalation and address-valid flags. Multiple sticky bits do not by themselves order faults. `FORCED` with no captured CFSR cause is unresolved, not proof of an instruction-fetch error.
2. Locate the interrupted context's stack from entry `EXC_RETURN`, not the current handler SP after a C prologue. Check basic/extended frame, alignment, accessible bounds and stacking/unstacking/lazy-state errors before trusting words.
3. Validate stacked xPSR.T (bit 24), address ranges and frame coherence. A stacked instruction PC is normally halfword-aligned/even; odd function pointers encode Thumb state separately. Never reject a frame solely because PC bit 0 is zero.
4. Resolve the original stacked PC against the exact ELF and inspect disassembly plus operands. For a precise data BusFault it points to the faulting instruction. Never automatically subtract 2/4 for a supposed pipeline adjustment. Imprecise faults need preceding operations; corrupt/failed frames do not establish an instruction at all.
5. Correlate valid fault address with the computed effective address, permissions, accessible memory and object bounds. Saved R0-R3/R12 alone may be insufficient; R4-R11 and modified live handler registers must not be invented.
6. Trace defect -> illegal state/access -> fault; test pointer lifetime, stack corruption, invalid exception return, disabled coprocessor, alignment or device access only as evidence supports them. A DMA controller error is not automatically a CPU CFSR BusFault.

## Close the task

Lead with classification/confidence, raw decoded facts and frame reliability, then instruction/causal candidates, minimal fix when requested and decisive validation. If uncertain, identify the next exact register/frame/ELF evidence to capture. Build-test an authorized correction where possible and distinguish target evidence from proposed watchpoint/MPU/reproduction tests. Do not install a generic fault handler or reset policy merely to explain a dump.
