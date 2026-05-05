# NC-TEST-FR-200 — Alpha Testing Plan for NeoCortex MCP Tools

## Overview
Alpha testing of 17 core MCP tools to validate functionality, performance, and readiness for open-source release.

## Testing Timeline
**Duration**: 3 weeks (April 2026)
**Goal**: Validate all 17 MCP Super Tools against roadmap Q2 2026 milestones

## Tools to Test (16 Super Tools + 1 Core)

### Phase 1: Basic Functionality (Week 1)
1. **NC-SUPER-013-health.py** - Health monitoring
   - Test actions: server.health, server.tools_count, ssot.audit, metrics.live, watchdog.status
   - Success criteria: All actions return valid responses

2. **NC-SUPER-001-governance.py** - Governance rules
   - Test actions: policy.check, rule.list, compliance.report, violation.log
   - Success criteria: Governance rules enforced correctly

3. **NC-SUPER-002-orchestration.py** - Task orchestration
   - Test actions: task.execute, task.list, task.status, agent.spawn
   - Success criteria: Tasks execute and track correctly

4. **NC-SUPER-003-memory.py** - Memory management
   - Test actions: cortex.get, lobe.search, knowledge.store, memory.search
   - Success criteria: Memory operations work, search returns results

### Phase 2: Core Services (Week 2)
5. **NC-SUPER-004-state.py** - State persistence
   - Test actions: checkpoint.get, savepoint.create, session.status, ledger.read
   - Success criteria: State saved/restored correctly

6. **NC-SUPER-005-llm-router.py** - LLM routing
   - Test actions: gateway.health, route.call, ollama.ask, budget.status
   - Success criteria: LLM calls routed correctly, budget tracked

7. **NC-SUPER-006-system.py** - System operations
   - Test actions: config.get, pulse.status, health.agent, system.diagnostics
   - Success criteria: System info accessible, diagnostics work

8. **NC-SUPER-007-brain.py** - Brain/planning
   - Test actions: brain.think, brain.plan, brain.critique, intelligence.query
   - Success criteria: Planning functions return coherent plans

9. **NC-SUPER-008-context.py** - Context management
   - Test actions: context.compress, session.summarize, report.generate
   - Success criteria: Context compressed, summaries generated

### Phase 3: Security & Monitoring (Week 3)
10. **NC-SUPER-009-security.py** - Security
    - Test actions: access.validate, lock.check, hook.register, audit.log_event
    - Success criteria: Security checks pass, hooks fire

11. **NC-SUPER-010-benchmark.py** - Benchmarking
    - Test actions: run.drift, run.titanomachy, benchmark.status
    - Success criteria: Benchmarks run, results collected

12. **NC-SUPER-011-notification.py** - Notifications
    - Test actions: push.send, push.list, peers.discover, peers.sync
    - Success criteria: Notifications sent, peers discovered

13. **NC-SUPER-012-akl.py** - AKL/Knowledge
    - Test actions: akl.add, akl.search, kg.query, consolidate.session
    - Success criteria: Knowledge added/queried correctly

14. **NC-SUPER-014-ledger.py** - Ledger
    - Test actions: ledger.read, ledger.write, agent.register, agent.identity
    - Success criteria: Ledger entries created, agent identity tracked

15. **NC-SUPER-015-memory-auto.py** - Auto-memory
    - Test actions: turn.record, session.hot, session.stats, lobe.auto
    - Success criteria: Memory auto-recorded, stats generated

16. **NC-SUPER-016-picoclaw.py** - PicoClaw IPC
    - Test actions: picoclaw.start, picoclaw.publish, picoclaw.poll, picoclaw.llm_call
    - Success criteria: IPC works, messages passed

17. **Core Framework** - Fractal memory architecture
    - Test: mmap IPC, memory fractalization, zero-trust execution
    - Success criteria: All core architectural components functional

## Testing Metrics

### Primary Metrics (Roadmap Targets)
1. **Token Efficiency**: Minimum 48% savings vs standard agents
   - Measurement: Compare token usage for identical tasks
   - Tool: Benchmark against baseline Claude/GPT agents

2. **Context Re-entry Reduction**: Minimum 64% reduction
   - Measurement: Count manual context re-entries avoided
   - Tool: Session logging and manual task tracking

3. **Response Time**: MCP tool call latency
   - Target: <100ms for local tools, <500ms for LLM calls
   - Measurement: Time from tool call to response

### Secondary Metrics
4. **Memory Efficiency**: Fractal memory vs traditional
   - Measurement: Memory usage per session
   - Tool: System monitoring

5. **Error Rate**: Tool failure rate
   - Target: <1% failure rate
   - Measurement: Successful vs failed tool calls

6. **Stability**: Uptime and crash frequency
   - Target: 99.9% uptime during testing
   - Measurement: Continuous monitoring

## Test Environment
- **OS**: Windows (current environment)
- **Python**: 3.12+
- **MCP Server**: Running locally
- **LLM Backend**: Ollama (qwen2.5-coder:1.5b) + DeepSeek
- **Monitoring**: Custom metrics collection

## Test Cases per Tool

### Example: NC-SUPER-013-health.py
```
Test Case 1: server.health
- Action: Call server.health
- Expected: Returns service status with reachable/unreachable
- Pass: All core services reported

Test Case 2: ssot.audit  
- Action: Call ssot.audit
- Expected: Returns SSOT compliance percentage (target: >80%)
- Pass: Returns 85.7% compliance

Test Case 3: metrics.live
- Action: Call metrics.live
- Expected: Returns recent metrics data
- Pass: Metrics returned (empty OK if no data)
```

## Reporting
- Daily test logs in `DIR-DS-002-audit-logs/`
- Weekly summary reports
- Final alpha test report with go/no-go recommendation

## Success Criteria for Alpha Completion
1. All 17 tools pass basic functionality tests
2. Token efficiency ≥48% savings demonstrated
3. Context re-entry reduction ≥64% demonstrated  
4. Error rate <1% across all tool calls
5. Documentation of all issues found and fixes applied

## Next Steps After Alpha
1. Fix identified issues
2. Prepare for open-source release
3. Begin academic paper drafting
4. Start Rust migration prototype