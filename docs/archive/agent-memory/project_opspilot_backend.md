---
name: OpsPilot Backend Implementation
description: OpsPilot SRE agent backend - P1~P8 phased implementation plan to build complete incident handling pipeline
type: project
---

OpsPilot is an SRE incident management agent with LangGraph-based workflow. Backend at `backend/app/`.

**Architecture**: FastAPI + LangGraph + SQLAlchemy (SQLite) + Pydantic v2 + OpenAI/MiniMax LLM.

**Implementation plan**: `guide/技术规划/后端实现计划.md` (master spec), `guide/技术规划/执行跟踪计划.md` (tracking).

**8 phases (P1→P8, strict order)**:
- P1: Runtime + persistence foundation (checkpoint/events/serde/runtime service)
- P2: Intake + Triage (3 entry modes, normalizers, 3-stage triage)
- P3: Memory + Planner + Evidence (dynamic investigation plans, parallel evidence)
- P4: Diagnose + Critic loop (multi-candidate RCA, 4-way critic routing)
- P5: Remediation + Risk Gate + Approval (interrupt/resume, 4 decision types)
- P6: Executor + Verify (idempotent execution, retry/compensation)
- P7: RCA + Knowledge Writeback (human confirm before writeback)
- P8: Platform adapters + Observability + Eval (MySQL/K8s/SLB/OSS, replay eval)

**Why:** Goal is to upgrade from demo to production-grade incident handling pipeline with full auditability, recoverability, and real platform integration.

**How to apply:** Always follow the phased plan strictly. Each phase must deliver code + tests + migration + docs. No skipping phases.
