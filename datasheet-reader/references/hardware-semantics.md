# Hardware semantics and calculations

Read the applicable subsection for the requested register, sequence or calculation.

## Writes and observation

Classify each touched field: ordinary RW, RO, W1C, W0C, read-to-clear, write-only, hardware-updated, or mixed semantics. Read-modify-write is appropriate only when both the read and write preserve the intended state. `STATUS |= FLAG` on W1C can clear unrelated pending flags; `STATUS &= ~FLAG` is not a generic W0C solution. Determine the documented clear value, reserved-bit policy and concurrency before supplying code. SET/CLR aliases may help when the actual device provides them.

Repeated register reads are not always harmless. Data-register reads may pop FIFOs or participate in flag-clearing sequences; debugger SFR auto-refresh may do the same. Prefer safe status registers and record destructive reads explicitly. Capture failure evidence before a reset, clear or reinitialization removes it.

For initialization/state transitions, determine prerequisite power/clocks/reset, required disabled state, programming order, readiness/completion/error conditions, delays and errata. Replace blind delay with a documented readiness condition plus a bounded timeout when the implementation calls for it. Do not assume that every reconfiguration requires deinitialization.

## Clock and timing

Trace source -> clock mux -> bus/kernel domain -> peripheral prescaler -> effective timing. Bus frequency and kernel frequency can differ. Timer multipliers, TIMPRE, dedicated muxes and counting modes are device-dependent; do not universalize an APB x2 rule.

For an ordinary edge-aligned up-counting timer, when supported by the exact manual:

`f_update = f_timer / ((PSC + 1) * (ARR + 1))`.

For other modes verify center-aligned counting, repetition counter, clock division, preload/update transfer and event semantics. UART oversampling/BRR encoding, ADC cycles and I2C analog/digital filters similarly need their own formulas; a simple frequency ratio does not establish a legal register encoding.

Compute integer encoding, resulting frequency/baud, signed relative error and oscillator/tolerance budget where material. I2C calculations must include rise/fall times and filters. Do not claim precision beyond the inputs.

## Electrical values

Distinguish recommended operating conditions, guaranteed min/max under stated conditions, typical values, and absolute maximum ratings. Absolute maximum is a stress limit, not a design operating point. Check temperature, supply, load, source impedance, package and pin-specific exceptions. Show the footnote that changes the interpretation.

## Code mapping

Trace statement -> macro definition -> register field -> documented behavior -> resulting hardware state. HAL/SDK state and hardware state can diverge; source inspection establishes what the library does, while the reference manual establishes what the hardware does.
