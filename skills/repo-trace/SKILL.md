---
name: repo-trace
description: End-to-end data journey and golden path call chain tracing. Use when tracing how a concrete input payload transforms across system components, identifying sync/async hops, documenting payload diffs, and mapping error recovery branches (Level 3).
license: MIT
---

# Repo Trace — Concrete Data Journey & Golden Path Tracing

`repo-trace` 是深入代码库微观世界前的数据显微镜。它的使命是帮助开发者**跳出静态文件的孤岛迷宫，跟随一份真实具体的数据样本，亲历其在系统各个模块间的变形与跨界流转**，完成认知变焦中的 **Level 3 (Example)**。

**Tradeoff:** 偏向单条端到端黄金链路的真实变形追踪，放弃对所有边角分支的穷举。
**Personality:** 数据法医与侦探——拒绝抽象概念漂移，只关心具体字节在何时、被哪个模块、改造成了什么形态。

---

## 1. A Day in the Life (单一真实输入原则)

**读者在看具体代码行前，必须看到一份活生生的真实输入在系统里流转变形。**

严禁使用泛指代词（如“某个请求到达系统”）。必须给出一份**真实可感知、具有完整字段的测试用例或数据样本**：
- **Web 后端**：一条具体的 HTTP POST 请求及 JSON Body（如带有特定 `user_id` 与时间戳的注册请求）；
- **前端/客户端**：一次具体的用户点击或表单提交事件，伴随明确的状态 Action 载荷；
- **编译器/构建**：一段具体的输入代码片段（如包含变量声明与箭头的 3 行 JS 源码）；
- **AI 算法/推理**：一个具体的文本 Prompt（如 `"Explain backpropagation in 10 words"`）及对应的 Token 数组；
- **CLI/系统工具**：一条带真实参数的命令（如 `rg --json "pattern" ./dir/`）。

---

## 2. Station-by-Station Payload Diff (站点数据变形差分)

**步步追踪数据形态的生老病死。每一个站点必须明确指出“进来了什么”与“变成了什么”。**

追踪过程中，必须划分出 4 大标准中继站，并输出形态变化差分 (Diff)：
1. **Station 1: Ingress (入口网关/接入层)**
   - 原始形态：Raw Buffer / HTTP Request / CLI Args
   - 加工动作：协议解码、基础校验、脱敏清洗、时间戳与 Trace ID 注入
   - 变形产物：Internal Command / Context Object
2. **Station 2: Buffer / Spool (缓冲与排队层，若有)**
   - 暂存形态：Channel / Memory RingBuffer / WAL (Write-Ahead Log)
   - 关键变化：追加序列号、内存对齐、持久化防丢标记
3. **Station 3: Processing (核心业务引擎/计算核)**
   - 核心处理：业务决策、AST 变换、状态机流转、张量计算
   - 变形产物：Execution Plan / Mutation Delta / Log Entry
4. **Station 4: Persistence / Egress (落盘与出站)**
   - 出站形态：DB Row / Fsync Payload / HTTP Response JSON
   - 最终交付：外界可见的不可逆状态变更

---

## 3. 5-Phase Golden Path Sequence (5 阶段序列时序图)

**用 Mermaid 时序图还原调用链路，必须显式区分同步与异步跨界。**

在绘制时序图 (`sequenceDiagram`) 时，必须遵守以下严格规范：
- **参与者明确标注物理路径**：`participant Gateway as Ingress (src/gateway.go)`
- **明确标出同步 vs 异步边界**：
  - 同步调用：实线箭头 `->>`
  - 异步派发（Queue / Channel / Goroutine / Event Loop）：虚线带箭头 `-->>`
  - 明确标注等待唤醒条件（如 `Wait for Ack` 或 `Future.get()`）
- **异常穿透与恢复分支**：
  - 必须使用 `alt / else` 块展示主流错误分支（如校验失败、连接超时、限流熔断）；
  - 必须指出发生错误时的回滚与降级机制。

---

## 4. Eliminate Happy-Path Bias (消除快乐路径偏见)

**只讲正常流程等于没讲。健壮架构的精髓 80% 藏在异常防御与重试回滚中。**

### 怎么做 vs 不要怎么做 (Contrast Table)

| 绝对不要（业余/快乐路径） | 必须做到（名师/深度追踪） |
| :--- | :--- |
| **流水账式列调用**：“A 调用了 B，B 又调用了 C，最后存入数据库。” | **数据变形与责任转移**：“A 收到 Raw JSON 后剥离 header 封装成 Command 塞入 RingBuffer，B 消费 Command 并做乐观锁校验，版本冲突时走重试指数退避。” |
| **假装永远不报错**：时序图中一条直线到底，没有任何错误处理分支。 | **异常与降级全景**：标出网络超时、序列化失败、锁冲突时的补偿动作与错误日志落地。 |
| **忽视异步与并发**：把异步队列调用画成简单的函数同步返回。 | **显式标明异步解耦点**：指出数据何时离开主调用栈、进入常驻 Worker 轮询、何时被消费 Ack。 |

---

## 5. Goal-Driven Execution (确定性工具链)

追踪调用链路时，先通过 AST 工具定位目标符号与真实调用关系：

```bash
# 1. 提取目标领域的符号定义与调用层级
repo-mentor ast <target_path> --symbols --calls

# 2. 定位关键函数所在行号范围
repo-mentor ast <target_path> --symbol <EntrypointSymbol>
```

---

## 6. 验收清单 (Verifiable Success Criteria)

产出 `studies/<repo_name>/traces/<domain>_trace.md` 后，必须满足：
- [ ] **样本具象鲜活**：具有一份完全真实的输入载荷（非抽象伪代码）；
- [ ] **中继站差分明确**：至少展现 Ingress ➔ Processing ➔ Persistence 的数据变形对比；
- [ ] **Mermaid 时序图合规**：包含参与者路径别名，实线/虚线区分同步/异步调用；
- [ ] **包含至少 1 条异常分支**：展现发生超时、校验失败或并发冲突时的系统应对；
- [ ] **代码事实锚定预备**：为下一步下钻准备好 2~3 个承重节点的文件路径。
