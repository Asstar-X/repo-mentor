# /trace (别名: /flow) — 具象用例数据旅程与调用链追踪

> **支撑技能**: [`skills/repo-trace/SKILL.md`](../skills/repo-trace/SKILL.md)

执行认知变焦中的 **Level 3 (Example 具象案例)**：挑选一个真实鲜活的输入事件，追踪数据在组件边界间的形态变形与载荷差分 (Payload Diff)，标明同步/异步调用跳跃，并还原异常穿透与回滚分支。

---

## 执行工作流

### 1. 确定目标领域并提取调用层级
```bash
# 提取目标领域的符号签名与调用层级关系
repo-mentor ast <target_path> --symbols --calls
```

### 2. 生成数据旅程切片 (`studies/<repo_name>/traces/<domain>_trace.md`)

#### 第一部分：具象用例全流程 — 单一真实输入原则 (A Day in the Life)
- **具象输入载荷**：提供一份完全真实具体的输入数据（如一个具体的 JSON 请求体、一条带有明确参数的 CLI 命令、一段具体的语法树节点）。
- **中继站点数据旅程与形态差分 (Payload Diff)**：
  1. **中继站 1: Ingress (接入层)**：协议解码、基础校验、Trace ID 注入（载荷差分：Raw 字节流 ➔ Command 上下文）。
  2. **中继站 2: Buffer / Spool (缓冲排队层，若有)**：Channel 或 RingBuffer 入队（载荷差分：分配全局递增序号）。
  3. **中继站 3: Processing (业务处理层)**：核心决策、状态机跃迁或计算核执行。
  4. **中继站 4: Persistence / Egress (出站落盘层)**：写库、fsync 刷盘或向外部响应。

#### 第二部分：5 阶段黄金调用链时序图 (Mermaid)
- 绘制 `sequenceDiagram`，参与者名称必须用双引号包裹且附带路径别名；
- 明确区分同步调用 (`->>`) 与异步调用 (`-->>`)，标明队列等待与唤醒条件；
- 必须使用 `alt / else` 块展现主流异常分支（如超时、限流、冲突）的降级与回滚逻辑。

---

## 3. 自动化质量验证
校验切片文档中引用的代码路径与 Mermaid 语法：
```bash
repo-mentor verify <target_path> studies/<repo_name>/traces/<domain>_trace.md --fix
```

---

## 4. 更新进度看板
在 `studies/<repo_name>/README.md` 的核心领域看板中，将该领域的调用链追踪标记为完成。
