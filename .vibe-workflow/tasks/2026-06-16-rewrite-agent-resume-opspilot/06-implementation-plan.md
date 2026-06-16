# Rewrite Agent Resume OpsPilot Implementation Plan

> **For agentic workers:** This is a document-only task. Follow the project AGENTS.md workflow and keep edits scoped to the requested resume file.

**Goal:** Rewrite the OpsPilot-related content in `.interview/欧阳锦峰-Agent工程师版.md` using the project material under `.interview/.project/OpsPilot-AI运维智能体`.

**Architecture:** Preserve the existing resume structure and rewrite only the sections where OpsPilot affects positioning, project experience, and skills. Use interview-facing language, but keep claims traceable to the source material and `ACTION_PLAN.md`.

**Tech Stack:** Markdown documentation.

---

## File Structure

- Modify: `.interview/欧阳锦峰-Agent工程师版.md`
  - Personal positioning and strengths.
  - Huawei work experience summary.
  - `AI SRE 运维智能体` project experience.
  - Skills list.
- Create: `.vibe-workflow/tasks/2026-06-16-rewrite-agent-resume-opspilot/10-knowledge-capture.md`
  - Record decisions, validation, risks, and reusable checklist.

## Tasks

### Task 1: Rewrite Resume Content

- [x] Read current resume structure.
- [x] Read OpsPilot source material:
  - `.interview/.project/OpsPilot-AI运维智能体/模块一-取证与质量门控/01-取证与质量门控模块-主逻辑.md`
  - `.interview/.project/OpsPilot-AI运维智能体/模块一-取证与质量门控/02-取证与质量门控模块-面试题.md`
  - `.interview/.project/OpsPilot-AI运维智能体/模块一-取证与质量门控/03-取证与质量门控模块-工程化细节面试题.md`
  - `.interview/.project/OpsPilot-AI运维智能体/模块一-取证与质量门控/04-取证与质量门控模块-用户旅程与Agent设计.md`
- [x] Rewrite target sections in `.interview/欧阳锦峰-Agent工程师版.md`.

### Task 2: Validate and Capture Knowledge

- [x] Check that Markdown headings remain valid.
- [x] Check that claims are consistent with the source material.
- [x] Create knowledge capture file with decisions, risks, and reusable checklist.

## Acceptance Criteria

- The resume keeps its original Markdown structure.
- OpsPilot content highlights evidence-driven diagnosis, quality gating, Tool Gateway, checkpointing, and offline evaluation.
- The text does not claim unsupported production rollout status.
- No source material or project code is modified.
