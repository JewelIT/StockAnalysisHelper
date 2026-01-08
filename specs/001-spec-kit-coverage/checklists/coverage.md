# Spec-Kit Coverage Checklist

**Purpose**: Validate Spec-Kit traceability (completed epics, in-progress items, and documentation artifacts) by grounding each coverage requirement against the current spec content and migration guardrails.  
**Created**: 2026-01-08  
**Feature**: [/specs/001-spec-kit-coverage/spec.md]

## Requirement Completeness

- [x] CHK001 Are the epics listed in `.specify/features/COMPLETE_PROJECT_STATE.md` and the stories tracked in `.specify/features/CURRENT_STATE_ANALYSIS.md` each linked to a dedicated `.specify/features/<epic>/SPEC.md` folder, ensuring no major Epic (auth, security, refactor, resilience, monitoring, deployment, Playwright, etc.) exists only in `docs/` or `.archive/`? [Completeness, Spec §Acceptance Criteria]  
	Evidence: the roadmap table enumerates Epics 1–10 with statuses and direct links to Spec-Kit folders while `CURRENT_STATE_ANALYSIS` describes the authentication foundation and upcoming payments/coupon/OAuth work that feed back into those epics; the README’s Documentation section explicitly points to the same `.specify/features/epic-*/SPEC.md` files so the catalog is discoverable.  

## Requirement Clarity

- [x] CHK002 Is the policy for `docs/` (“only `MODEL_CREDITS.md` plus `.archive/` remain; every other technical doc belongs under `.specify/features/` with a spec/plan pair”) clearly documented so owners know where to place new writing? [Clarity, Spec §Goals]  
	Evidence: the root README’s Documentation section states that all technical specs live in Spec-Kit and that `docs/` now only houses the model credits and archives, and the Documentation Migration Checklist records the same policy plus cleanup commands to keep legacy content out of `docs/`.  

## Scenario Coverage

- [x] CHK003 Does the spec explicitly call out all `CURRENT_STATE_ANALYSIS` progress items (auth foundation, payments, coupon, OAuth) and the blocking `CRITICAL_GAPS_ANALYSIS` entries so the checklist knows which scenarios still require Spec-Kit artifacts? [Scenario Coverage, Spec §Acceptance Criteria]  
	Evidence: `CURRENT_STATE_ANALYSIS` details the authentication foundation branch plus the planned payments/billing, coupon, OAuth phases, while `CRITICAL_GAPS_ANALYSIS` enumerates blocking gaps (Auth/Epic 1, Security/Epic 2, Coverage/Epic 3, Monitoring/Epic 18, Deployment/Epic 20, Playwright/Epic 21, etc.), keeping each scenario tied to a Spec-Kit folder.  

## Edge Case Coverage

- [x] CHK004 Is there a requirement for handling legacy files under `docs/.archive/` (e.g., summarizing actionable nuggets into a Spec-Kit file or marking them in the migration checklist) to prevent forgotten information from lurking outside Spec-Kit? [Edge Case Coverage, Spec §Acceptance Criteria]  
	Evidence: the Documentation Migration Checklist names `docs/.archive/` as the read-only archive and calls out the verification steps that ensure only `MODEL_CREDITS.md` and `.archive/` remain, so every archived artifact is acknowledged even if not migrated.  

## Non-Functional Requirements

- [x] CHK005 Are the non-functional expectations for documentation governance (root `README.md` pointing to Spec-Kit, README not referencing deleted docs, migration checklist as the guardrail) spelled out so reviewers can measure compliance? [Non-Functional Requirements, Spec §Goals]  
	Evidence: the README’s documentation section points readers to the Spec-Kit inventory instead of legacy docs and the migration checklist captures the cleanup commands and verification steps that enforce the governance.  

## Dependencies & Assumptions

- [x] CHK006 Is the dependency on `.specify/DOCUMENTATION_MIGRATION_CHECKLIST.md` being the single source of truth for future doc relocations stated so no one adds scattershot copy-and-paste docs? [Dependency, Spec §References]  
	Evidence: the migration checklist documents the completed migrations, deleted files, remaining reference docs, and verification steps as well as the policy statement that all new specs belong in `.specify/features/`, establishing it as the authoritative source.  

## Ambiguities & Conflicts

- [x] CHK007 Does the spec reconcile any apparent contradictions between the “completed” column in `COMPLETE_PROJECT_STATE` and the “blocking” gaps in `CRITICAL_GAPS_ANALYSIS` so reviewers can trust the published statuses? [Ambiguity, Spec §Goals]  
	Evidence: `COMPLETE_PROJECT_STATE` lists Epics 1–3 as in-progress/planned while the critical gaps analysis immediately clarifies exactly what pieces (auth routes, security hardening, coverage metrics, monitoring, etc.) remain, so there is no conflicting story once both artifacts are read together.  
