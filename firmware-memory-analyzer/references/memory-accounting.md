# Memory accounting

## Region totals

Use half-open address ranges `[start, end)`. Determine actual output-section placement and load ranges; linker aliases or overlapping logical regions may map to the same physical bank. Report union occupancy for overlaps, gaps/padding and the highest occupied/reserved address separately when these change usable headroom. Capacity minus sum of symbols is not a complete contiguous-allocation budget.

`.data` or RAM code with a Flash load image contributes to both RAM VMA and Flash LMA. ELF section virtual addresses alone do not identify LMA; use the MAP, linker `AT/AT>` rules, copy tables and appropriate load/program headers. Do not assume every physical address in a program header is a universally reliable vendor LMA convention. `.bss`/SHT_NOBITS, `.noinit` and NOLOAD reservations occupy runtime address space but normally have no initialization payload. Check startup zero/copy rules, boot metadata, vector alignment, constructors, exception tables, orphan sections and retained storage.

Do not sum PT_LOAD spans plus sections, or output sections plus input members plus symbols. These are different attribution views of the same allocation. Overlays require separate maximum simultaneous runtime occupancy and stored load images. Discarded MAP sections are not occupied output. Aliased/zero-size symbols and folded functions can inflate naive symbol totals.

BIN may include filled gaps between address ranges; HEX is encoded and sparse; ELF includes debug and metadata. State image payload vs programmed address span vs device reservation.

## Stacks and heaps

Determine whether a heap/stack is a real output section, linker minimum reservation, dynamic interval, RTOS pool or separate static allocation. A task stack allocated from an already-counted `ucHeap` consumes runtime capacity inside that pool, not extra linked RAM. Count static task stacks separately when they live outside it. `heap_3` uses the C allocator; `heap_5` may use multiple configured regions. Confirm wrappers and actual allocator source.

Report pool capacity, observed usage/peak, minimum free and largest free block if available; total free alone does not establish that the next contiguous allocation can succeed. Do not equate unused reserved RAM with automatically usable heap space.

Native FreeRTOS stack depths/watermarks normally use `StackType_t` units; wrappers/ports may differ. Verify units. Account for MSP/ISR nesting separately from PSP task stack. Watermarks depend on test coverage and touched memory, not necessarily the deepest SP. Combine compiler `.su`/call paths, indirect calls/recursion/library limitations and worst-case runtime evidence before proposing a stack reduction.

## Attribution and optimization

Use linked object/archive members and load sections to explain contributors. A library name alone is not enough: identify the actual pulled-in member/symbol, such as floating printf or an arithmetic helper. Preserve ABI and required unwind/constructor behavior. Enabling LTO, section GC, nano libraries, removing RTTI/exceptions or moving buffers can affect semantics, diagnostics and timing.

Rebuild comparable settings; report signed per-region/section deltas and relevant behavior checks. A pre-change symbol size is at most a candidate upper bound, not guaranteed savings after link-time transformations. Compare the intended bottleneck region, not just total image bytes.
