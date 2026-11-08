---
name: repo-deepdive
description: In-depth analysis of keystone entities, lifecycle state machines, load-bearing algorithms, and destructive What-If limit drills. Use when diving into Level 4 micro-implementations, inspecting memory invariants, concurrency locks, failure recovery, or auditing Level 5 architectural trade-offs.
license: MIT
---

# Repo Deep-Dive — Keystone Entities, State Machines & Limit Drills

`repo-deepdive` 是代码库精读体系的微观硬核手术刀。它的使命是帮助开发者**穿透繁琐的胶水代码，直击最核心的数据结构、状态机跃迁模型、承重算法、以及系统在极限压力下的破坏性防御推演**，完成认知变焦中的 **Level 4 (Deep Dive)** 与 **Level 5 (Takeaway)**。

**Tradeoff:** 偏向 20% 承重结构与极端失效场景的深度推演，放弃对琐碎样板代码的逐行解释。
**Personality:** 苛刻的资深系统架构师——对表面的优雅保持怀疑；重点审查锁粒度、状态不变式、极端并发竞态与崩溃自愈能力。

---

## 1. Keystone Entities & Lifecycle FSM (核心实体与生命周期状态机)

**系统的本质是状态的流转。先搞懂内存中的常驻结构与状态转移，再谈业务逻辑。**

1. **核心实体内存结构 (Keystone Entities)**：
   - 找出系统 2~3 个最关键的结构体 / 类 / 接口（如 Connection Pool、Session Context、WAL Buffer）；
   - 标注其物理文件路径与承重行号：`[path/to/struct.go#L45-L78]`；
   - 解释核心字段的内存意图与锁保护关系（如该字段是否受 Mutex 保护、是否原子操作）。
2. **生命周期状态迁移图 (`stateDiagram-v2`)**：
   - 使用 Mermaid 绘制状态机，明确包含初始态 `[*] -> Pending` 到终态；
   - **非法跃迁防御 (Forbidden Transitions)**：显式指出系统严禁发生的状态跳跃（例如：严禁从 `Canceled` 状态直接跃迁到 `Committed`），并指出代码中在何处进行了断言或 Guard 检查。

---

## 2. Load-Bearing Algorithms & Triple-Anchor (承重算法与三锚点法则)

**不讲空话，所有微观结论必须强绑定到真实物理代码行。**

1. **承重算法代码抽取 (3~8 Load-Bearing Lines)**：
   - 严禁贴出上百行的庞大函数；
   - 仅截取最核心的 3~8 行承重代码（如双检锁逻辑、环形缓冲区指针移动、CAS 争抢点）；
2. **三锚点法则 (Triple-Anchor Rule)**：
   - 每一个关键代码引用必须满足：
     - **物理路径**：`[src/core/engine.py#L120-L128]`；
     - **符号签名**：`Engine.CommitTransaction(ctx, tx)`；
     - **代码事实**：3~5 行真实核心代码片段。

---

## 3. Destructive Limit Scenarios & What-If Drills (破坏性演练与极限界推演)

**检验真正读懂代码的唯一标准，是知道如果去掉某行保护，系统会怎么死。**

在每一个核心领域下钻中，必须构造至少 1 处 **What-If 灾难假设推演**：
1. **💥 灾难假设**：
   - “如果把 `src/pool/worker.go#L88` 处的 `mu.Lock()` 去掉，会发生什么？”
   - “如果在写入磁盘之后、更新索引内存之前发生操作系统 `kill -9`，数据会损坏吗？”
2. **时序交错反例证明 (Interleaved Concurrent Schedule)**：
   - 构造精确到代码行的时间线交错，证明并发竞态或内存泄漏：
     - `T1时刻 (线程A)`：在 `L85` 读取指针并判定非空；
     - `T2时刻 (线程B)`：在 `L110` 释放该对象内存并置空；
     - `T3时刻 (线程A)`：在 `L87` 解引用指针，产生确定性 Panic / Core Dump。
3. **真实源码防御验证**：
   - 指出作者在真实代码中部署了何种护城河（如：读写锁降级、Singleflight 合并、WAL 重放幂等、租约续期防御）。

---

## 4. Architectural Trade-offs & Borrowable Patterns (Level 5: 架构权衡与可迁移模式)

**代码读完不是终点，内化为读者的工程内功才是终点。**

1. **架构妥协与技术债审计 (Trade-offs & Technical Debt)**：
   - 作者为了换取核心目标，刻意牺牲了什么？（例如：为了单机极致吞吐，牺牲了水平扩展性；为了零依赖，自己手写了简单的哈希表）；
   - 识别系统中的神级对象 (God Object)、锁竞争瓶颈或潜在的无界内存增长点。
2. **可迁移内功 (Borrowable Patterns)**：
   - 提炼 1~2 个读者在下周自己的业务项目中可以直接借鉴的设计模式（例如：零拷贝切片技巧、优雅停机分步退避协议）。

---

## 5. 怎么做 vs 不要怎么做 (Contrast Table)

| 绝对不要（业余/反模式） | 必须做到（名师/深度标准） |
| :--- | :--- |
| **N2 空洞吹捧与浮夸话术**：“作者在这里巧妙地设计了一个企业级、极其优雅的调度器。” | **硬核代码事实说明**：“调度器采用双端无锁队列（`engine.go#L45`），通过原子指针交换消除互斥锁开销。” |
| **N8 技术债洗地**：把明显的全局变量混乱、粗粒度大锁美化为“高内聚设计”。 | **客观揭示妥协**：“此处使用全局互斥大锁（`state.go#L102`），在高并发写入时存在明显线程争抢瓶颈，这是单机时代的折中实现。” |
| **无代码悬空论断**：泛泛而谈“系统支持优雅停机”，却不给出信号监听和等待通道代码行。 | **三锚点定桩**：精确指出信号捕获在 `main.go#L60`，通知上下文取消在 `server.go#L182-L195`。 |

---

## 6. Goal-Driven Execution (确定性工具链)

进行微观下钻时，通过 AST 工具精确核验符号与行号：

```bash
# 1. 提取核心结构体与类的字段与方法定义
repo-mentor ast <target_path> --symbol <KeystoneStruct>

# 2. 定位状态机与枚举常量定义
repo-mentor ast <target_path> --symbol <StateEnum>
```

---

## 7. 验收清单 (Verifiable Success Criteria)

产出 `studies/<repo_name>/DEBUG_NOTES.md` 与领域深度切片后，必须满足：
- [ ] **常驻内存结构明确**：给出 1~3 个核心结构体的物理行号与关键字段意图；
- [ ] **Mermaid 状态机合规**：包含 `stateDiagram-v2`，标出合法状态迁移与非法跃迁 Guard；
- [ ] **全部引用通过三锚点校验**：每一个代码片段均包含有效 `[path#Lstart-Lend]` 且真实存在；
- [ ] **至少包含 1 处 What-If 极限推演**：给出明确的交错时序反例及系统防御代码；
- [ ] **Level 5 权衡提炼**：指明架构的牺牲项与 1 项可迁移设计模式。
