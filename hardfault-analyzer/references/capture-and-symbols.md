# Capture and symbol resolution

## Debugger capture

Use an existing fault capture or stop at the first instruction of the actual fault vector before compiler prologue/BL changes LR or MSP. Confirm startup vector names and any wrapper. A breakpoint inside a C helper can expose an ordinary LR, not entry EXC_RETURN.

On an implemented Armv7-M SCB, illustrative GDB reads:

```gdb
info registers
p/x $lr
p/x $msp
p/x $psp
x/1wx 0xE000ED24
x/1wx 0xE000ED28
x/1wx 0xE000ED2C
x/1wx 0xE000ED34
x/1wx 0xE000ED38
```

Register names vary by debugger. Save raw values and capture location. Select the entry SP from valid EXC_RETURN, validate accessible stack bounds, then read the appropriate basic/extended frame. Do not use `x/8wx $sp` indiscriminately after handler execution. Do not write status registers to clear them before saving evidence.

## Target capture when requested

Adapt to the compiler/core/startup code; inspect generated assembly. An entry assembly stub must save entry LR and selected SP before a C prologue. `__builtin_return_address(0)` in a normal C handler is not a portable entry EXC_RETURN capture. Avoid allocations, printf, RTOS calls and FP instructions in the recorder. Capture supported status first; validate stack bounds and error flags before reading frame words, and mark unavailable frame data rather than dereferencing an arbitrary SP.

For retained storage define linker NOLOAD/noinit placement, startup exclusions, reset-domain retention, cache persistence, format/build ID, integrity and a commit marker. Prevent recursive capture from producing a valid-looking partial record. Use the project's halt/reset/watchdog policy; do not change it solely as a diagnostic convenience. Test basic/PSP and applicable extended frames plus capture after a bad SP using a controlled target setup.

## Matching artifacts

Verify firmware identity/debug symbols; account for bootloader relocation, vector remap or RAM execution where relevant. Detect tools and their architecture support:

```text
arm-none-eabi-addr2line -e firmware.elf -f -C -i 0x08001234
arm-none-eabi-objdump -d -S firmware.elf --start-address=0x08001220 --stop-address=0x08001250
arm-none-eabi-nm -n -S firmware.elf
```

Resolve the captured instruction address first, with no automatic subtraction. For a branch pointer/LR Thumb marker, a separately normalized address can aid symbol lookup; preserve the raw value and do not confuse caller return address with fault PC. Inline/LTO and optimization may give approximate lines; disassembly and operands decide the access. `??:0` is unresolved, not success. MAP ranges are coarser and may lack symbol sizes/source lines; avoid false precision.

For an imprecise fault inspect earlier CPU writes and implementation-specific auxiliary status; controller/DMA/bus errors need their own status and may not appear in CFSR. Do not universally disable write buffering or use unsupported debug-control bits.
