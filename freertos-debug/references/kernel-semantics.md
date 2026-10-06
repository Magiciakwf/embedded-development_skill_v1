# FreeRTOS semantics that change diagnoses

## Cortex-M ISR priorities

First determine the actual port. BASEPRI-based Cortex-M ports and PRIMASK-only ports do not have identical masking rules. Read the device's `__NVIC_PRIO_BITS`, configuration and actual priority grouping; do not assume four priority bits.

For the usual BASEPRI Cortex-M port, lower NVIC numbers mean higher urgency. CMSIS logical priority and the encoded high bits written to IPR differ. Where the project uses the conventional definitions:

`configMAX_SYSCALL_INTERRUPT_PRIORITY = configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY << (8 - configPRIO_BITS)`.

Compare in the same encoding. Interrupts above the API threshold must not call kernel APIs, including `FromISR`, and are not excluded by ordinary RTOS critical sections. A zero threshold is invalid for the relevant BASEPRI ports. Check how grouping divides preemption/subpriority bits and the port's asserts rather than hard-coding a CubeMX number.

Initialize `xHigherPriorityTaskWoken = pdFALSE` for an ISR invocation, preserve it across applicable `FromISR` operations, and use the port's yield convention when required. Establish whether missing immediate switching violates a deadline or only delays until the next scheduling opportunity. Nested interrupts and masks can dominate observed latency.

## Primitive and callback distinctions

- Mutexes have ownership and relevant priority inheritance; binary/counting semaphores are signaling/counting objects. Verify recursive requirements and give-by-owner. Priority inheritance does not eliminate all nested-lock or inversion problems.
- Queue items are copied at configured item size. Pointer queues require explicit lifetime/reuse. `xQueueOverwrite` has a single-item queue contract; do not treat it as a generic overflow policy.
- Notification action/index determines count, bits, overwrite/mailbox behavior. `ulTaskNotifyTake` clear/decrement choices differ; `xTaskNotifyWait` entry/exit masks and pending state matter. Stream/message buffers may use a task notification channel internally; check collisions with application notifications and actual single-writer/reader requirements.
- Event bits represent state, not count. `xEventGroupSetBitsFromISR` defers work through the daemon/timer command path; check enqueue return, command queue capacity and daemon priority if a wake is late or lost. Inspect wait-any/all and clear-on-exit with the actual kernel semantics; do not assume one waiter simply steals a bit from all others.
- Software-timer callbacks share the daemon task. Blocking there can delay other callbacks/commands; a timer command waiting on its own full queue can cause a dependency failure. HAL callbacks are not all ISRs: trace their callers.

## Time and stack measurements

Check native API vs wrapper units. Native task stack depth/high-water marks normally count `StackType_t` units, while CMSIS wrappers can take bytes. Verify stack width, measured workload and untouched local reservations. Low watermark is not a proof of a worst-case bound or coverage of MSP nesting.

Verify tick width, `pdMS_TO_TICKS` implementation, rounding-to-zero, multiplication overflow and actual `portMAX_DELAY` semantics/configuration. Unsigned elapsed-time checks require observation and interval bounds; they cannot track multiple missed wraps. Absolute periodic scheduling and relative delay have different drift/overrun behavior. Tickless idle requires correct sleep/wakeup time accounting; do not assume printed timestamps alone prove tick accuracy.

Official starting sources (use the installed kernel/port source for version-dependent details):

- [FreeRTOS Cortex-M port priorities](https://www.freertos.org/Documentation/02-Kernel/03-Supported-devices/04-Demos/ARM-Cortex/RTOS-Cortex-M3-M4)
- [FreeRTOS official kernel book, interrupt management](https://github.com/FreeRTOS/FreeRTOS-Kernel-Book/blob/main/ch07.md)
- [Event-group ISR deferral and failure return](https://www.freertos.org/Documentation/02-Kernel/04-API-references/12-Event-groups-or-flags/06-xEventGroupSetBitsFromISR)
