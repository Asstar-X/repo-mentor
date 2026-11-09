# /trace — 上下文使用场景与调用脉络追踪

> **支撑技能**: [`skills/repo-trace/SKILL.md`](../skills/repo-trace/SKILL.md)  
> **核心职责**: **Follow a living data sample, never read dead symbols in isolation.** (拽着真实数据样本走全流程，绝不孤立看死符号。)

专注于**看目标在外部场景怎么用**：像真人同事梳理业务流一样，用通俗大白话讲透它用在哪里、真实场景下谁调它、下游交给了谁、拿个具体例子怎么跑、异常时怎么处理。

---

## 执行工作流

### 1. 提取目标对象的上下游调用关系
```bash
# 提取目标符号的调用层级
repo-mentor ast <target_path> --symbol <TargetSymbol> --calls
```

### 2. 生成调用脉络说明（保存至 `studies/<repo_name>/traces/<target>_trace.md`）

按自然段落与直观拓扑组织，包含以下要点（**严禁生硬套用格式八股模板**）：

1. **真实使用场景**：
   - 最上游是什么外界事件触发的，在全流程里它负责第几棒。
2. **上下游协同关系**：
   - 附带直观简洁的 Mermaid 流向图：
     ```mermaid
     flowchart LR
         Trigger["触发源头"] --> Caller["上游调用方"]
         Caller --> Target["当前目标"]
         Target --> Downstream["下游承接方"]
     ```
   - 标清上游直接调用方位于哪个文件哪一行 `[文件路径#L行号]`，下游把产物交给了谁。
3. **具体例子走读（拿个样本跑一遍）**：
   - 挑一个具体参数、结构体或样本数据：进去前长啥样、出来后变啥样、最后送到了哪。
4. **出错了怎么办**：
   - 执行失败、校验不通过或条件未满足时，错误如何向外反馈、重试或降级。

### ⚠️ 风格红线
- 严禁戏精演戏，严禁使用中二浮夸修辞；
- 严禁打 `[已验证事实]`、`[工程推导]` 等公章标签；
- 严禁原样输出提示词大纲，严禁在正文中输出任何内部验收打勾清单；
- 严禁在文末拼接“全局研读进度”、“在数学上被严格锁定”等官僚尾巴。

---

## 3. 自动化质量验证
```bash
repo-mentor verify <target_path> studies/<repo_name>/traces/<target>_trace.md --fix
```
确保场景说明通俗自然，上下游拓扑清晰，代码锚点真实有效。
