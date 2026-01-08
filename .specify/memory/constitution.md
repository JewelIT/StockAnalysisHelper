# FinBERT Portfolio Analyzer Constitution

## Core Principles

### 1. Security First (NON-NEGOTIABLE)
All code MUST follow OWASP best practices and security-first design. No secrets, credentials, API keys, or sensitive data may be committed to version control (including history, logs, or configuration). All inputs MUST be validated; all outputs sanitized. Authentication and authorization MUST use industry-standard patterns (Argon2 for passwords, secure session management, account lockout). Least privilege MUST be enforced. Security vulnerabilities MUST be addressed within 7 days for critical issues. Rationale: Protecting user data and system integrity is paramount; proactive security prevents breaches and maintains trust.

### 2. Code Quality & Patterns (NON-NEGOTIABLE)
Code MUST adhere to SOLID principles, DRY, separation of concerns, and established design patterns. Repository Pattern MUST abstract persistence layers enabling implementation swaps without business logic changes. Dependency Injection MUST be used for services. Domain models MUST be pure Python with no framework dependencies. Code MUST be readable, maintainable, and follow PEP 8 style guidelines. Each class/module MUST have a single responsibility. Rationale: Quality patterns reduce technical debt, improve testability, and enable sustainable growth.

### 3. Test-Driven Development (NON-NEGOTIABLE)
TDD cycle MUST be followed: Write test → Test fails → Implement → Test passes → Refactor. Unit tests MUST cover new business logic with meaningful assertions including edge cases and error conditions. Integration tests MUST verify cross-component behavior and real API interactions. All tests MUST pass before merge. Test coverage for critical paths (authentication, financial calculations, data aggregation) MUST be ≥90%. Rationale: Tests prevent regressions, document behavior, and enable confident refactoring.

### 4. Free & Open Source Priority
Always prefer FREE and open-source solutions. No paid APIs without explicit approval and working credentials. Local-first approach: prefer locally-running models (HuggingFace) over API calls. Build redundancy with multiple free data sources (yfinance, Finnhub free tier, Alpha Vantage free tier). Minimize external dependencies and respect rate limits. Rationale: Sustainability and accessibility; reducing costs enables broader usage.

### 5. Data Integrity & Validation (NON-NEGOTIABLE)
All financial recommendations MUST cross-validate against multiple sources. Flag suspicious scores and log reasoning for every decision. Implement data consensus algorithms with discrepancy detection. Cache data locally to minimize API calls. Every recommendation MUST show confidence level, reasoning, and data sources. Rationale: Financial advice requires accuracy; transparency builds user trust and enables informed decisions.

### 6. Privacy & Minimal Data Collection
Only collect minimal necessary data. User portfolios and preferences stored locally (SQLite). No user tracking or analytics without explicit opt-in. Data retention policies MUST be documented. Session data MUST expire appropriately. Rationale: Respecting privacy safeguards users and reduces regulatory risk.

### 7. Atomic Commits & Git Hygiene
Commits MUST be atomic: one logical unit of work per commit. Small commits preferred over large batch changes. Each commit MUST be independently reviewable and revertible. GitHub is source of truth—no backup files in repo. No tracking comments ("I removed this"). Commit messages MUST explain WHAT and WHY. Rationale: Clean history enables bisecting, cherry-picking, and understanding evolution.

### 8. Incremental Development
Update individual methods/classes; avoid rewriting entire files unless critical. One function at a time: structure → implement → test → integrate. Start simple (YAGNI); add complexity only when needed with justification. Prefer editing over recreating to preserve git history and minimize token usage. Rationale: Incremental changes reduce risk, improve code review quality, and lower costs.

## Non-Negotiables & Technology Stack

**Non-Negotiables**:
- No secrets in code or public artifacts (use environment variables: `os.getenv()`)
- OWASP principles guide all security decisions
- Repository Pattern for all persistence layers
- Dependency Injection for services
- Domain models pure Python (no ORM imports)
- All authentication tests MUST use environment variables for passwords
- Dependencies vetted and kept updated (automated security scans)
- 106+ tests maintained with 100% pass rate
- Argon2 password hashing (OWASP recommended, GPU-resistant)
- Account lockout after 5 failed attempts

**Technology Stack**:
- **Backend**: Flask (Python 3.10+)
- **Authentication**: Argon2-cffi, secure sessions, JWT tokens
- **Data Sources**: yfinance (free), Finnhub (free tier), Alpha Vantage (free tier), CoinGecko (free)
- **AI/ML**: HuggingFace Transformers (DistilBERT for sentiment analysis, local execution)
- **Technical Analysis**: ta-lib
- **Persistence**: Repository Pattern with SQLite (production), in-memory (testing)
- **Testing**: pytest, pytest-cov
- **Security**: Flask-Limiter (rate limiting), Flask-WTF (CSRF), email-validator, zxcvbn
- **Frontend**: HTML/JavaScript with Bootstrap
- **CI/CD**: Automated pipelines with security checks (secrets scanning, dependency audits)

## Development Workflow & Quality Gates

**Definition of Done** (change complete ONLY when all apply):
1. Code meets SOLID principles, DRY, and PEP 8 standards
2. Security principles upheld (OWASP, no secrets, input validation, output sanitization)
3. Repository Pattern used for persistence; Dependency Injection for services
4. Domain models remain pure Python (no framework coupling)
5. TDD cycle followed (test → fail → implement → pass → refactor)
6. Unit tests cover new logic (≥90% for critical paths); integration tests cover user journeys
7. All 106+ tests pass; no regressions introduced
8. Documentation updated (docstrings, architectural notes when behavior changes)
9. Atomic commit with clear message (WHAT and WHY)
10. Peer review completed (self-review acceptable during solo development with documented rationale)

**Quality Gates**:
- **Security**:
  - Secret scanning MUST pass (no credentials in code/history)
  - Input validation MUST be explicit (email format, password strength via zxcvbn)
  - Account lockout MUST prevent brute force (5 attempts → 15min lock)
  - Sessions MUST use secure tokens (secrets.token_hex)
  - Password hashing MUST use Argon2 (memory-hard, GPU-resistant)
- **Code Quality**:
  - Linting (flake8/pylint) MUST pass with zero high-severity findings
  - Type hints encouraged (mypy compliance target: ≥80%)
  - Cyclomatic complexity ≤10 per function (exceptions require justification)
- **Testing**:
  - Unit tests MUST pass (pytest -v)
  - Critical paths (auth, financial calculations, data aggregation) MUST have ≥90% coverage
  - Integration tests MUST verify end-to-end flows (register→login→portfolio→logout)
  - Negative test cases REQUIRED for security-sensitive code
- **Performance**:
  - API response times monitored (target: ≤2s for sentiment analysis)
  - Cache hit rate tracked (target: ≥70% for repeated queries)
  - Rate limiting prevents abuse (Finnhub 60/min, Alpha Vantage 5/min)
- **Data Integrity**:
  - Multi-source consensus REQUIRED for financial data (≥2 sources)
  - Discrepancies >10% MUST be flagged
  - Confidence scores MUST accompany recommendations
  - Data source attribution MUST be transparent

## Governance

**Authority & Scope**: This constitution supersedes informal practices. All artifacts (plans, specs, tasks, code, docs) MUST conform.

**Amendments**:
- Proposal via "Constitution Amendment" issue including: problem, proposed change, principles affected, version bump (MAJOR/MINOR/PATCH), impact analysis, migration plan
- Approval: document rationale; security/privacy changes require explicit security review
- Recording: version bump commit + changelog entry
- Communication: summary in release notes; MAJOR changes get dedicated announcement

**Versioning Policy**:
- **MAJOR**: Removal/redefinition of principle or breaking change to workflow
- **MINOR**: New principle added or material expansion of guidance
- **PATCH**: Clarifications, wording improvements, typo fixes

**Compliance Review**:
- Weekly: automated dependency scan, secret detection
- Per-commit: All tests must pass, linting clean
- Quarterly: manual principle alignment review + retrospective
- Violations MUST be documented with remediation tasks and resolution date

**Documentation Integration**:
- Plan templates MUST include Constitution Check alignment
- Task templates MUST reflect security, privacy, and quality concerns
- Spec templates MUST produce testable acceptance criteria

**Fast-Track Criteria**: Critical security/privacy fixes with active exploitation risk; retrospective postmortem REQUIRED

**Metrics**:
- Security remediation (critical) ≤7 days median
- Test pass rate: 100% (106+ tests maintained)
- Secret exposure incidents: 0 per quarter (target)
- Code coverage (critical paths): ≥90%
- Dependency updates: monthly review cycle
- Test suite execution time: ≤5s (unit), ≤30s (integration)

**Version**: 1.0.0 | **Ratified**: 2026-01-08 | **Last Amended**: 2026-01-08
