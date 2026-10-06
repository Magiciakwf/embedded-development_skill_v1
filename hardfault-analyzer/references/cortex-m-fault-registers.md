# Armv7-M fault registers and exception frames

Scope: Cortex-M3/M4/M7 Armv7-M configurable fault model. FPU fields apply only where implemented. M0/M0+ do not supply this configurable fault register set. Armv8-M/M23/M33/M55 and security transitions require their architecture-specific additions and frame rules; this table is not a complete decoder for them.

## CFSR (SCB + 0x28)

Bits below are absolute CFSR bit positions, not subregister-relative positions.

| Bit | Name | Evidence |
|---|---|---|
| 0 | IACCVIOL | MPU instruction access violation |
| 1 | DACCVIOL | MPU data access violation |
| 3 | MUNSTKERR | MemManage fault while unstacking |
| 4 | MSTKERR | MemManage fault while stacking |
| 5 | MLSPERR | MemManage fault during FP lazy preservation |
| 7 | MMARVALID | MMFAR can be interpreted as a captured fault address |
| 8 | IBUSERR | Instruction bus error |
| 9 | PRECISERR | Precise data bus error; stacked PC identifies faulting instruction |
| 10 | IMPRECISERR | Imprecise data bus error; stacked PC does not identify the responsible access |
| 11 | UNSTKERR | BusFault while unstacking |
| 12 | STKERR | BusFault while stacking |
| 13 | LSPERR | BusFault during FP lazy preservation |
| 15 | BFARVALID | BFAR can be interpreted as a captured fault address |
| 16 | UNDEFINSTR | Undefined instruction |
| 17 | INVSTATE | Invalid execution state, including EPSR/Thumb state |
| 18 | INVPC | Invalid exception-return value/integrity check; also present in Armv7-M |
| 19 | NOCP | Unsupported or disabled coprocessor |
| 24 | UNALIGNED | Unaligned access fault; some instructions fault regardless of UNALIGN_TRP |
| 25 | DIVBYZERO | Integer divide-by-zero trap |

MMFSR = CFSR[7:0]; BFSR = CFSR[15:8]; UFSR = CFSR[31:16]. Unrecognized set bits must be reported, not silently ignored or labeled an application root cause.

## Other status

HFSR (SCB + 0x2C): bit 1 VECTTBL = vector-table read BusFault; bit 30 FORCED = escalation; bit 31 DEBUGEVT = debug-related HardFault. FORCED can reflect a disabled fault or an unserviceable configurable fault at current priority. VECTTBL does not prove vector-table contents were overwritten.

SHCSR (SCB + 0x24) enables: MEMFAULTENA bit 16, BUSFAULTENA bit 17, USGFAULTENA bit 18. Active/pending states, interrupt masks and current priority also matter. Do not infer all escalation behavior from enable bits alone.

MMFAR (SCB + 0x34) and BFAR (SCB + 0x38) need their corresponding captured VALID bits. Without CFSR, validity is unknown. A valid address is not automatically a valid pointer; zero can be the actual fault address.

## Armv7-M EXC_RETURN and layout

Use LR at exception entry. Conventional valid values:

| Value | Return | Stack | Frame |
|---|---|---|---|
| 0xFFFFFFF1 | Handler | MSP | Basic |
| 0xFFFFFFF9 | Thread | MSP | Basic |
| 0xFFFFFFFD | Thread | PSP | Basic |
| 0xFFFFFFE1 | Handler | MSP | Extended FP |
| 0xFFFFFFE9 | Thread | MSP | Extended FP |
| 0xFFFFFFED | Thread | PSP | Extended FP |

Extended values require the applicable FP implementation/state. A normal function LR is not EXC_RETURN. Bit 2 selects stack, bit 3 return mode, bit 4 frame type only after the encoding/architecture is established.

Basic frame from the selected entry SP: R0,R1,R2,R3,R12,LR,PC,xPSR at offsets 0x00,04,08,0C,10,14,18,1C. In an Armv7-M extended FP frame these core offsets remain unchanged; S0-S15 occupy 0x20..0x5C, FPSCR is at 0x60 and a reserved word at 0x64. Total size is 0x68 before any alignment pad. Lazy FP preservation can reserve space without filling FP words; check FPCCR and lazy-state errors. Never add 0x48 to find the core frame: that would mistake FP state for core registers.

Stacked xPSR bit 9 reports an exception-entry alignment pad beyond the frame; it affects reconstructing the pre-exception SP, not the core PC offset above. xPSR bit 24 is Thumb state. The stacked PC is an instruction address, normally even; a function pointer/branch operand may instead carry a Thumb marker in bit 0.

Frame/access bounds and stacking errors come before dereferencing. A bad frame can cause another fault inside the capture handler.

## Source and interpretation boundaries

[Arm DDI 0403E.e](https://documentation-service.arm.com/static/606dc36485368c4c2b1bf62f), B1.5.6 PushStack()/ReturnAddress() (printed B1-532..534) and B1.5.7 Figure B1-4 (B1-538), specifies the core/FP offsets and halfword-aligned stacked return PC. [ST PM0214 Rev 10](https://www.st.com/resource/en/programming_manual/DM00046982-.pdf), sections 2.1.3 (PC/EPSR), 2.3.7 (exception frames/return), 2.4 (escalation) and 4.4 (fault status), covers the Cortex-M4 implementation. Section 4.4 CFSR PRECISERR ties the stacked PC to the faulting instruction; pipeline-based subtraction is not a general rule. Use the exact core manual for other implementations.

Status bits establish fault classes, not whether the original defect was a null pointer, overflow, power loss or an unavailable peripheral. A fault in memcpy or an RTOS context switch often needs caller/object history to find the originating defect.
