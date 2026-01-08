# Implementation Plan: Spec-Kit Coverage & Documentation Migration

**Branch**: `001-spec-kit-coverage` | **Date**: 2026-01-08 | **Spec**: [/specs/001-spec-kit-coverage/spec.md]
**Input**: Feature specification from `/specs/001-spec-kit-coverage/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Document the current Spec-Kit coverage (completed, in-progress, and planned work) and correlate every backlog/gap to an explicit Spec-Kit folder so that legacy docs and `.archive` references are either migrated or annotated in the migration checklist. This plan ensures the upcoming checklist run validates traceability between the `COMPLETE_PROJECT_STATE`, `CURRENT_STATE_ANALYSIS`, `CRITICAL_GAPS_ANALYSIS`, and the per-epic `SPEC.md` artifacts.

## Technical Context

**Language/Version**: Python 3.10+ (Flask backend, some support scripts invoking `run.py`, `build-executable.sh`)  
**Primary Dependencies**: Flask 2.x, Argon2-CFFI, pytest, Plotly, yfinance/Finnhub/AlphaVantage clients  
**Storage**: SQLite (prod/dev) + file caches (`cache/market_sentiment_cache.json`)  
**Testing**: pytest (231 tests exist), plans for Playwright E2E in `.specify/features/epic-21-e2e-testing-playwright`  
**Target Platform**: Linux servers and local dev environments (Docker + pyinstaller packaging)  
**Project Type**: Web application (Flask API + static SPA)  
**Performance Goals**: Maintain ≤2s sentiment responses; cache hit rate ≥70% (documented elsewhere)  
**Constraints**: No secrets in repo (per constitution), OWASP compliance, offline-ready doc migration process  
**Scale/Scope**: ~15k LOC, 12+ endpoints, multi-source data aggregation, 10+ active epics needing coverage

## Constitution Check

Gates: All new documentation references must conform to the constitution (no secrets, maintain security-first framing). This plan simply documents coverage; it inherits the existing compliance references from the spec artifacts listed in `CURRENT_STATE_ANALYSIS`, `CRITICAL_GAPS_ANALYSIS`, and the referenced epics.

## Project Structure

### Documentation (this feature)

```text
specs/001-spec-kit-coverage/
├── spec.md              # This specification (coverage/goals)  
├── plan.md              # This implementation plan (checklist prep)  
└── checklists/          # Auto-generated artifacts (created by /speckit.checklist)
```

### Source Code (repository root)

```text
src/                        # Flask services, analysis core, AI helpers  
app/routes/                  # Flask route definitions (market sentiment, analysis, chat)  
app/services/                # Market/data services, repositories  
tests/                       # pytest suites (unit + integration)  
static/                      # JS/CSS assets and UI interactions  
templates/                   # SPA templates (index, modals, partials)  
docs/                        # Model credits + .archive reference artifacts  
.specify/features/           # Complete Spec-Kit artifacts (epics, status docs, inventories)  
.specify/DOCUMENTATION_MIGRATION_CHECKLIST.md  # Migration guardrail  
```

**Structure Decision**: Maintain the Flask + static SPA layout; this feature only supplements the documentation/spec coverage rather than modifying the source structure.

## Complexity Tracking

Not applicable; this plan focuses on documenting existing work.
