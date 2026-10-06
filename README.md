# 8 个嵌入式 Skill 优化说明

已优化工作区 `skills`、`skills1` 和当前安装目录 `C:\Users\k2005\.codex\skills` 中的 8 个嵌入式 skill。原始版本分别保存在 `embedded-skills-backup-20261006-181448`，附源文件 SHA-256 清单。其他 skill 未修改。

## 修改重点

原来的主要问题是重复清单过多、部分流程过于固定、容易停在建议阶段，以及若干技术规则错误或过度泛化。这次保留 skill 名称和自动发现方式，将入口缩短，并把条件性的细节放到各自的 `references` 中按需读取。

| Skill | 实战改进 |
|---|---|
| datasheet-reader | 先读已有资料；区分 PDF 索引与印刷页码；表格/位域提取失真时看原页；禁止对 W1C/W0C 等寄存器机械使用读改写；注明资料适用性和来源。 |
| embedded-bug-investigator | 用最有区分度的实验推进；保留失效证据；记录暴露时间和反例；定位后继续处理原任务；修正 `.noinit` 必然跨复位保留的误导。 |
| embedded-code-generator | 直接集成到真实工程；定义异步完成/超时/取消/重启和缓冲区归属；核查 DMA 缓存行共享；避免凭空生成硬件映射；区分构建、主机测试与板上验证。 |
| embedded-code-review | 以可达触发、具体交错和运行后果支撑发现；主动检查反证；将条件性疑问与确认缺陷分开；避免把可能 HardFault 一律评成最高严重度。 |
| firmware-memory-analyzer | 区分 VMA/LMA、初始化镜像和运行占用；避免区段/对象/符号及 RTOS 堆内任务栈重复计数；核查别名、间隙与连续可用空间；移除不适配本环境的工具白名单。 |
| freertos-debug | 区分阻塞与饥饿、事件状态与计数、指针队列与数据副本；核查实际端口及优先级编码；补充事件组 ISR 延迟路径、守护任务依赖、通知通道冲突和栈单位。 |
| hardfault-analyzer | 修正 PC/Thumb 判断、故障指令偏移和 FP 扩展帧布局；不信任普通 C 函数中的 LR/SP；解码器明确 Armv7-M 范围，验证输入、地址有效位并保留未知位。 |
| stm32-driver-debug | 从第一处中断的事件链定位；移除跨系列统一 RCC、DMA、优先级位数、ADC 校准顺序和 CS 管理规则；补充 DMA 完成与线上完成的区别。 |

## 关键技术纠正

- 堆栈里的指令 PC 是半字对齐地址，bit 0 为 0 正常；Thumb 状态应检查堆栈 xPSR.T。函数指针的 Thumb 标记不能套到堆栈 PC 上。
- 对精确数据 BusFault，堆栈 PC 指向故障指令；不能固定减 2/4。非精确错误需要追查之前的访问。
- Armv7-M 扩展浮点帧仍从 SP 开始保存 R0 等核心寄存器，PC 在 SP+0x18，浮点区从 SP+0x20 开始，FPSCR 在 SP+0x60。原版本把核心区与浮点区的相对位置写反了。
- W1C 等寄存器不适用通用读改写方案。缓存维护以缓存行为单位，必须同时建立缓冲区归属与相邻数据保护。

异常帧和 PC 规则核对依据：[Arm DDI 0403E.e 的 PushStack / ReturnAddress / 扩展帧定义](https://documentation-service.arm.com/static/606dc36485368c4c2b1bf62f)、[ST PM0214](https://www.st.com/resource/en/programming_manual/DM00046982-.pdf)。FreeRTOS 和缓存规则的官方来源链接也保存在相应 skill 的参考文件中。

## 验证范围

- 8 个 skill 在三个目录的 frontmatter、命名和脚手架检查通过，所有本地参考链接有效。
- HardFault 解码器 18 项回归测试通过，覆盖正常偶数 PC、精确/非精确错误、地址有效位、基本/扩展帧、普通 LR、堆栈错误、未知位、输入越界、JSON 和符号工具异常。
- 三个目录的交付文件 SHA-256 一致；独立压缩包完整性检查通过。
- 8 个入口文件合计从 99,506 字节减少到 27,869 字节，约减少 72%。按需参考和脚本另计。这是入口体积变化，不等同于效果提升百分比。

没有接入真实板卡，也没有执行独立模型的前后对比评测；真实项目定位速度、误报率和一次成功率需要后续工程案例验证。符号解析的工具异常路径使用 mock 测试，未对真实 ARM ELF 做端到端验证。

## 如何使用

继续自然描述问题即可按场景发现对应 skill，也可以显式指定。例如：

```text
$embedded-code-generator 帮我在这个工程中实现 UART DMA 接收，按现有架构集成并构建。
$embedded-code-review 审查这个 diff，重点检查 ISR 与任务的缓冲区归属，指出有证据的缺陷。
$hardfault-analyzer 分析这份寄存器和堆栈转储，先判断异常帧可靠性，再用对应 ELF 定位。
```

尽量附带当前工程或具体日志/构建产物。无需先填完整硬件问卷；优化后的流程会先利用已有证据，再索取影响结论的关键缺项。

如果当前聊天仍显示旧的 skill 描述，可在新聊天中使用优化后的文件；本次对磁盘文件的同步已完成。

解码脚本及测试均只使用 Python 标准库：

```text
python skills/hardfault-analyzer/scripts/decode_hardfault.py --cfsr 0x8200 --hfsr 0x40000000 --bfar 0x40000000 --lr 0xFFFFFFFD --pc 0x08001234 --xpsr 0x01000000 --json
python -m unittest discover -s skills/hardfault-analyzer/scripts -p "test_*.py" -v
```

需要回滚时，从备份中选择对应的 `installed`、`workspace` 或 `workspace1` 子目录恢复相应 skill；备份包含修改前的原始文档、参考文件和脚本。
