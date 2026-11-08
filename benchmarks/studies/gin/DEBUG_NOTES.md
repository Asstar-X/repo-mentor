# Gin Source Walkthrough & Debug Journal

## 1. Local Debugging & Smoke Run Commands

### Build & Test Commands
```bash
# Environment setup (Go 1.21+)
cd /tmp/benchmark-repos/gin
go version

# Run core smoke unit tests
go test -v -run TestEngineDeploy ./...

# Run fast router benchmarks
go test -v -bench=BenchmarkOneRoute -run=^$ .
```

### Golden Breakpoint Call Stack
1. `Engine.ServeHTTP` (`gin.go#L691`) — Ingress entrypoint from standard `net/http` server.
2. `Engine.handleHTTPRequest` (`gin.go#L719`) — Router dispatch loop.
3. `node.getValue` (`tree.go#L418`) — Prefix tree path traversal.
4. `Context.Next` (`context.go#L197`) — Middleware handler chain execution.

---

## 2. Core Structures & Critical Gotchas

### 1. Radix Tree Route Storage (`tree.go`)
- `type node struct`:
  * `path string`: Common URL prefix segment.
  * `indices string`: First bytes of distinct child paths.
  * `wildChild bool`: True if any child is a param or catch-all wildcard.
  * `handlers HandlersChain`: Pre-composed slice of middleware and endpoint handlers.

### 2. Invariants & Trade-offs
- **System Invariant 1**: At most one wildcard (`:param` or `*filepath`) is permitted per radix segment level. Conflicting definitions panic at engine startup in `addRoute`.
- **System Invariant 2**: Context pointers recycled into `sync.Pool` must never be referenced by long-running background goroutines without calling `c.Copy()`.
- **System Invariant 3**: Calling `c.Abort()` freezes execution index to `abortIndex = 63`, guaranteeing subsequent handlers cannot execute even if user handler panics.

### 3. Limit Scenarios & Recovery Drills
- **Scenario 1: Slowloris Attack Defense**: Mitigated by `defaultReadHeaderTimeout = 10 * time.Second`.
- **Scenario 2: Uncaught Handler Panic**: Intercepted by `CustomRecoveryWithWriter` in `recovery.go#L53`, preserving process uptime.
- **Scenario 3: High-Throughput Memory Pressure**: Completely bypassed by `sync.Pool` zero-heap allocations.
