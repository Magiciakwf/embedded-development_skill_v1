---
name: firmware-memory-analyzer
description: "Analyze embedded ELF, MAP, linker scripts and runtime measurements for Flash/RAM use, placement, overflow, stack/heap capacity and measured size optimization. Use build artifacts, not ELF file size or generic memory advice."
---

# Firmware Memory Analyzer

Explain where memory goes and whether placement/capacity is correct. Reply in the user's language. Tie every major number and finding to the exact build artifact.

## Collect and reconcile

Inspect available ELF/MAP/linker/build settings, target region capacities and configuration. Establish build identity before comparing builds; document compiler/flags/features/linker differences that affect deltas. Missing symbols limit attribution, not all capacity analysis.

Detect available architecture-compatible tools before using them. Useful GNU commands:

```text
arm-none-eabi-size -A firmware.elf
arm-none-eabi-readelf -lW firmware.elf
arm-none-eabi-objdump -h firmware.elf
arm-none-eabi-nm -S --size-sort -C firmware.elf
```

Use compatible LLVM/vendor equivalents after checking their options. If unavailable, parse the supplied MAP/linker output and state coverage. Do not apply GNU MAP assumptions to Keil/IAR layouts without adapting the parser.

Reconcile MEMORY regions -> load segments -> allocated output sections -> input objects/archive members -> symbols. Record VMA/runtime, LMA/storage, section size/type, alignment, actual region and reservations. Read [references/memory-accounting.md](references/memory-accounting.md) for dual Flash/RAM accounting, alias/overlap, RTOS pools, stack evidence or build comparison.

## Decide what matters

Prioritize correctness-threatening placement/overlap, overflow and evidenced exhaustion before size optimization. Verify DMA/core accessibility against the exact device bus map. Initialized `.data` can consume both storage and runtime memory; `.bss`/NOLOAD reserve runtime space without initialization payload. ELF/debug size, HEX text length and sparse BIN span do not equal Flash payload.

Produce separate region budgets and a small ranking of relevant contributors; do not double-count output sections, members and symbols as additional usage. Distinguish occupied bytes, address-span headroom, explicit reservations and runtime unknowns. Large symbols alone do not prove unsafe placement or exhaustion.

For each optimization cite its contributor and functional tradeoff. Mark savings measured, estimated, upper-bound or unknown. If optimization is requested, implement an appropriate focused change and rebuild/compare under controlled settings when available. Do not remove required alignment, diagnostics or runtime features solely for size.

## Deliver

Lead with the bottleneck/placement finding and evidence, then a region table (capacity, occupancy/reservations, remaining margin and accounting method), largest relevant contributors, and practical changes. Separate static budget from measured stack/heap state. Report actual tools/results, unresolved placement assumptions and the test needed to establish a margin. Never claim stack safety or exact savings from artifacts that cannot establish them.
