# Peripheral paths and device-dependent traps

## RCC, GPIO and interrupt path

Use the actual part's RCC and AF tables. Dedicated kernel muxes, timer TIMPRE/multipliers, voltage/Flash wait-state constraints and ADC domains differ. F1 GPIO/AFIO remap is not a MODER/AFR configuration. No single APB x2 rule, fixed priority-bit count, maximum clock or register-name set applies across STM32.

Recompute timing from verified clock values and encoded modes, not only CubeMX's displayed intended clock. For RTOS ISR API use read `__NVIC_PRIO_BITS`, port threshold and logical vs encoded values. Shared IRQs need correct dispatch and per-source acknowledgment. `HAL_Delay`/blocking timeout inside a masking context may stop progressing when their tick cannot preempt it; inspect the actual timebase implementation.

## DMA/cache and memory

Determine actual engine: channel, stream/channel selector, DMAMUX, BDMA/MDMA/GPDMA/LPDMA or another device implementation. Routing lists by broad family can miss variants. Use the specific bus matrix/engine accessibility, memory attributes and descriptor rules; do not assume every CCM/DTCM region has the same DMA restriction.

Trace allocation -> address/region -> start -> hardware ownership -> HT/TC/error -> consumer -> reuse. `__HAL_LINKDMA` or equivalent links the correct handle/callback path; verify actual HAL source rather than assuming every transfer uses the same path. Circular DMA can already be writing the next region when a callback runs. Capture counters and software indices together with a known observation order.

Where D-cache is enabled on a non-coherent cacheable buffer, TX requires CPU dirty data made visible before start. RX must start with a safe cache state and publish fresh data after completion; an old dirty cache line can write back during DMA and overwrite received data. Follow platform clean/invalidate and barrier requirements. Align and isolate entire owned cache lines; invalidating rounded unowned lines can lose adjacent dirty data. Do not clean stale RX cache over a completed DMA transfer. Consider the established non-cacheable/dedicated-buffer design rather than globally disabling cache.

[ST AN4839](https://www.st.com/resource/en/application_note/DM00272913-.pdf) is an official starting point for F7/H7 cache-coherency requirements; confirm current applicable revision and exact CMSIS implementation. It is not evidence that every STM32 buffer is cacheable or DMA-accessible.

[ST's DMA/cache coherency guidance](https://community.st.com/stm32-mpus-61/how-to-maintain-dcache-coherency-for-dma-on-stm32-devices-167548) explains dirty-line writeback during inbound DMA and pre/post maintenance. Its MP2 HAL/MPU code is an example, not a drop-in implementation for other chips. [CMSIS Cortex-M7 cache API documentation](https://arm-software.github.io/CMSIS_6/latest/Core/group__Dcache__functions__m7.html) specifies address alignment and byte-sized ranges; verify the installed implementation and isolate the maintained cache lines.

## UART

Separate no RX, wrong baud, overrun, callback loss and consumer overrun. Check oversampling/BRR encoding, polarity/parity/word-length, actual RX flags and error paths. Legacy SR/DR acknowledgment and newer ISR/ICR semantics differ. Receive-to-idle callback sizes, HT/TC/IDLE events and restart behavior are HAL/version/mode dependent; account for duplicate/overlapping events and circular index wrap. DMA completion may precede the last transmitted bit; check peripheral TC before an RS-485 direction change or framing boundary.

## I2C

Determine address format from the actual API (7/10-bit and shifted vs unshifted), not from a universal `address << 1` rule. Use waveform ACK/NACK location to distinguish wrong address, unpowered/busy device, unsupported operation and protocol state. Timing depends on kernel clock, rise/fall times and filters. BERR/ARLO can reflect protocol/configuration or multi-master arbitration as well as electrical faults.

For a stuck bus, snapshot SDA/SCL and state first. Any GPIO recovery needs open-drain release, active-master/clock-stretch checks, the peripheral/device's permitted recovery/STOP procedure and bounded attempts. Nine clocks are not a guaranteed universal cure; do not drive high against another device or assume a legitimate multi-master bus is idle.

## SPI

Verify mode, word length, FIFO/packing, CS/NSS setup/hold and actual wire completion. Software CS, hardware NSS and NSS pulse behavior depend on part/configuration; HAL does not universally mean manual CS. DMA TC is not always end-of-wire. Check busy/EOT behavior, RX handling/overrun and external-device transaction requirements before releasing CS or buffers.

## ADC and timers

ADC accuracy depends on reference/supply, input impedance, sampling/conversion time, channel/rank, alignment and trigger rate. Calibration, regulator stabilization and enable/disable order are device-specific; do not universally prescribe calibration after enable.

Timer analysis needs input clock, counting mode, PSC/ARR encoding, repetition, trigger routing and update/preload transfer. An update event used to latch values can also alter counters/flags/trigger behavior. Validate the relevant output/interrupt/ADC-trigger waveform, not only register values.
