# Spec: Spec-Kit Coverage & Documentation Migration

**Date**: 2026-01-08
**Purpose**: Prove that every implemented feature, in-progress epic, and backlog item is traced inside Spec-Kit, and that the `docs/` hierarchy only houses the remaining reference artifacts.

## Problem
The legacy docs/ and .dev-notes/ folders once held architectures, security audits, testing guidance, and subscriptions strategy content that kept mutating outside Spec-Kit. We migrated the content, but need a formal guardrail so additional work, especially the items archived under `docs/.archive/`, does not slip outside the Spec-Kit artifacts and so we can assert the repository-wide coverage is up to date.

## Goals
1. Tie the `IMPLEMENTED_FEATURES_INVENTORY` and the `CURRENT_STATE`/`COMPLETE_PROJECT_STATE` narratives to specific spec folders for each Epic (authentication, security, code quality, resilience, production deployment, Playwright, etc.).
2. Validate the remaining `docs/` contents (Model credits + `.archive`) are either documented inside Spec-Kit or scheduled for migration via the migration checklist.
3. Capture any missing spec coverage as checklist items and document non-spec artifacts inside `.specify/DOCUMENTATION_MIGRATION_CHECKLIST.md` for future cleanup.

## Acceptance Criteria
- [ ] Every Epic described in the `COMPLETE_PROJECT_STATE` table has an associated folder under `.specify/features/` with an up-to-date `SPEC.md` (Epic 1, 2, 3, 18, 20, 21, 7, 4 market sentiment, etc.). [Spec §Roadmap]
- [ ] In-progress items listed in `CURRENT_STATE_ANALYSIS` (authentication foundation, payment/billing planning, coupon, OAuth) are linked to spec/plan files or documented as `TODO` tasks inside Spec-Kit. [Spec §CurrentState]
- [ ] The gaps enumerated in `CRITICAL_GAPS_ANALYSIS` map to existing spec artifacts (e.g., `epic-1-complete-authentication/SPEC.md`, `epic-2-security-hardening/SPEC.md`, `epic-3-code-quality-refactoring/SPEC.md`, `epic-7-resilience-error-handling`, `epic-18-monitoring-observability`, `epic-20-production-deployment`, `epic-21-e2e-testing-playwright`). [Spec §Gaps]
- [ ] The documentation migration checklist lists any `docs/.archive/` items that still require transclusion and provides next steps. [Spec §MigrationChecklist]
- [ ] The root `README.md` points to Spec-Kit, and no legacy docs (except `docs/MODEL_CREDITS.md` and `.archive/*`) remain in the top-level `docs/` directory. [Spec §DocsPlacement]

## Non-Goals
- Implementing any of the features described above beyond what already exists on `main` or the feature branches.
- Reproducing the `.archive/` content verbatim; instead, only document the actionable parts inside Spec-Kit.

## References
1. `.specify/features/IMPLEMENTED_FEATURES_INVENTORY.md`
2. `.specify/features/CURRENT_STATE_ANALYSIS.md`
3. `.specify/features/COMPLETE_PROJECT_STATE.md`
4. `.specify/features/CRITICAL_GAPS_ANALYSIS.md`
5. `.specify/DOCUMENTATION_MIGRATION_CHECKLIST.md`
6. `.specify/features/epic-1-complete-authentication/SPEC.md` (auth roadmaps)
7. `.specify/features/epic-2-security-hardening/SPEC.md`
8. `.specify/features/epic-3-code-quality-refactoring/SPEC.md`
9. `.specify/features/epic-7-resilience-error-handling/*`
10. `.specify/features/epic-18-monitoring-observability/*`
11. `.specify/features/epic-20-production-deployment/*`
12. `.specify/features/epic-21-e2e-testing-playwright/*`
