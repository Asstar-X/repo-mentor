# /deep-dive (别名: /core, /drill) — 核心状态机、承重算法与极限演练

> **支撑技能**: [`skills/repo-deepdive/SKILL.md`](../skills/repo-deepdive/SKILL.md)

执行认知变焦中的 **Level 4 (Deep Dive 硬核源码)** 与 **Level 5 (Takeaway 架构权衡)**：剖析常驻核心实体内存布局、构建生命周期状态机模型 (FSM)、提取 3~8 行带有真实代码锚点的核心算法、构造时序交错的破坏性 What-If 极限推演，并提炼架构权衡与可迁移模式。

---

## 执行工作流

### 1. 审视核心实体结构与符号
```bash
# 定位目标领域的核心结构体、类定义或状态枚举
repo-mentor ast <target_path> --symbol <KeystoneStruct>
```

### 2. 生成深度切片报告 (`studies/<repo_name>/traces/<domain>_core.md`)

#### 第一部分：核心实体与生命周期状态机 (FSM)
- **核心实体结构**：标注物理文件路径 `[path/to/struct.ext#Lstart-Lend]`，说明关键字段内存持有关系与并发锁保护。
- **状态迁移模型 (`stateDiagram-v2`)**：明确从初始状态到终态的所有跃迁，显式指出**非法跃迁防护守卫 (Forbidden Guard)**。

#### 第二部分：承重算法与真实代码锚点 (Triple-Anchor)
- **3~8 行核心算法**：只截取最精炼的核心算法逻辑（如双检锁、指针位移、CAS 争抢点）。
- **三锚点强规范**：每个代码块必须精确挂载到 `[path/to/file.ext#Lstart-Lend]`。

#### 第三部分：破坏性极限场景推演 (What-If Drills)
- 💥 **What-If 灾难假设**：“如果把某行关键锁或超时保护去掉，系统会怎么死？”
- **时序交错反例证明**：构造包含 T1、T2、T3 的多线程交错时间线，证明竞态死锁或内存泄漏。
- **实时源码防御验证**：指出作者在真实代码中部署了何种护城河（如 CAS 重试、Singleflight 合并、WAL 幂等重放）。

#### 第四部分：Level 5 架构权衡与可迁移模式
- **架构权衡 (Trade-offs)**：作者为了换取核心指标，刻意牺牲了什么？技术债在何处？
- **可迁移模式 (Borrowable Patterns)**：提炼 1~2 个读者下周在自己的业务中可以直接借鉴的设计模式。

---

## 3. 自动化质量验证与归档
```bash
# 静态校验代码锚点与状态图语法（开启自动修正）
repo-mentor verify <target_path> studies/<repo_name>/traces/<domain>_core.md --fix

# 运行反 AI 套话与 100 分制裁判评估
repo-mentor eval <target_path> studies/<repo_name>/traces/<domain>_core.md
```

---

## 4. 更新领域进度
在 `studies/<repo_name>/README.md` 中，将该领域的状态机与极限推演标记为已探索：
```markdown
- [x] **领域: [领域名称]** (`[path/to/module/]`) — 已探索 (数据旅程、核心状态机与极限防御)
```
