# Feature Specification: Security Hardening

**Feature Branch**: `feature/security-hardening`  
**Created**: 2026-01-08  
**Status**: Not Started  
**Epic**: Epic 2 - Security Hardening  
**Priority**: HIGH  
**Estimated Effort**: 2-3 days  
**Dependencies**: Epic 1 (Complete Authentication System) must be complete

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Input Validation Protection (Priority: P1)

All user inputs are validated and sanitized to prevent injection attacks (SQL, XSS, command injection).

**Why this priority**: Critical security control. Prevents most common attack vectors (OWASP Top 10).

**Independent Test**: Can be tested by submitting malicious payloads (e.g., `<script>alert('xss')</script>`) to all input fields and verifying they're properly escaped or rejected.

**Acceptance Scenarios**:

1. **Given** a stock search form, **When** user inputs `<script>alert('xss')</script>` as ticker symbol, **Then** input is sanitized and displayed as plain text (no script execution)
2. **Given** a chat input, **When** user inputs SQL injection payload `' OR '1'='1`, **Then** input is parameterized and query executes safely
3. **Given** an API endpoint, **When** request contains invalid JSON, **Then** system returns 400 Bad Request with clear error message
4. **Given** a file upload endpoint, **When** user uploads executable file (.exe, .sh), **Then** system rejects with "Invalid file type" error

---

### User Story 2 - Rate Limiting (Priority: P1)

All API endpoints have rate limits to prevent abuse and DoS attacks.

**Why this priority**: Prevents resource exhaustion and brute-force attacks.

**Independent Test**: Can be tested by sending 100 requests/second to an endpoint and verifying requests are throttled after threshold.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user, **When** they make 20 requests to /auth/login in 1 minute, **Then** system returns 429 Too Many Requests
2. **Given** a FREE tier user, **When** they exceed 100 requests/hour, **Then** system throttles with "Rate limit exceeded" message
3. **Given** a TOP tier user, **When** they make 500 requests/hour, **Then** all requests succeed (higher limit for premium users)
4. **Given** a rate-limited user, **When** they wait for cooldown period, **Then** rate limit counter resets and requests succeed

---

### User Story 3 - Security Headers (Priority: P2)

All HTTP responses include security headers to protect against common web vulnerabilities.

**Why this priority**: Defense-in-depth measure. Important but not as critical as input validation and rate limiting.

**Independent Test**: Can be tested by inspecting response headers with curl or browser DevTools and verifying all required headers are present.

**Acceptance Scenarios**:

1. **Given** any HTTP response, **When** inspecting headers, **Then** `Content-Security-Policy` header is present with strict policy
2. **Given** any HTTP response, **When** inspecting headers, **Then** `X-Frame-Options: DENY` is set
3. **Given** any HTTP response, **When** inspecting headers, **Then** `X-Content-Type-Options: nosniff` is set
4. **Given** any HTTP response, **When** inspecting headers, **Then** `Strict-Transport-Security` is set (HSTS)
5. **Given** any HTTP response, **When** inspecting headers, **Then** `X-XSS-Protection: 1; mode=block` is set

---

### User Story 4 - Security Audit Automation (Priority: P2)

Automated security scans run on every commit to detect vulnerabilities in dependencies and code.

**Why this priority**: Proactive security posture. Catches issues before they reach production.

**Independent Test**: Can be tested by introducing a known vulnerability (e.g., outdated dependency) and verifying CI/CD pipeline fails.

**Acceptance Scenarios**:

1. **Given** a new commit, **When** CI/CD pipeline runs, **Then** dependency vulnerability scan (pip-audit or safety) executes
2. **Given** a vulnerable dependency, **When** pipeline runs, **Then** build fails with list of vulnerabilities
3. **Given** a new commit, **When** pipeline runs, **Then** static code analysis (bandit) executes
4. **Given** code with security anti-pattern (e.g., hardcoded secret), **When** bandit runs, **Then** build fails with violation details

---

### User Story 5 - Penetration Testing (Priority: P3)

Security team can run automated penetration tests to identify exploitable vulnerabilities.

**Why this priority**: Important for compliance but can be done after basic security controls are in place.

**Independent Test**: Can be tested by running OWASP ZAP or similar tool and reviewing the report.

**Acceptance Scenarios**:

1. **Given** a penetration testing tool (OWASP ZAP), **When** automated scan runs against staging environment, **Then** zero high-severity vulnerabilities are found
2. **Given** a manual penetration test, **When** attempting SQL injection on all endpoints, **Then** all attempts are blocked
3. **Given** a manual penetration test, **When** attempting XSS on all input fields, **Then** all attempts are sanitized
4. **Given** a penetration test report, **When** reviewing findings, **Then** all medium+ severity issues have remediation plans

---

### Edge Cases

- What happens when rate limiter storage (Redis) is down? → Fail-open or fail-closed? (Recommend fail-closed for auth routes, fail-open for read-only)
- How are distributed rate limits handled across multiple app instances? → Use centralized Redis or database-backed rate limiter
- What if CSP policy blocks legitimate third-party resources? → Whitelist specific domains in CSP policy
- How are false positives from security scanners handled? → Maintain suppression list with justifications
- What happens when user bypasses client-side validation? → Server-side validation is mandatory, client-side is UX only

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate all user inputs against whitelist or regex patterns
- **FR-002**: System MUST sanitize all outputs before rendering in HTML (prevent XSS)
- **FR-003**: System MUST use parameterized queries for all database operations (prevent SQL injection)
- **FR-004**: System MUST implement rate limiting on all public endpoints
- **FR-005**: System MUST apply tier-based rate limits (FREE: 100/hour, MIDDLE: 300/hour, TOP: 1000/hour)
- **FR-006**: System MUST set Content-Security-Policy header with strict policy
- **FR-007**: System MUST set X-Frame-Options: DENY header
- **FR-008**: System MUST set X-Content-Type-Options: nosniff header
- **FR-009**: System MUST set Strict-Transport-Security header for HTTPS enforcement
- **FR-010**: System MUST reject file uploads of dangerous file types (.exe, .sh, .bat, .cmd)
- **FR-011**: System MUST validate file upload size (max 10MB)
- **FR-012**: System MUST log all security events (failed auth, rate limit hits, validation failures)
- **FR-013**: System MUST run dependency vulnerability scan on every commit (CI/CD)
- **FR-014**: System MUST run static code analysis (bandit) on every commit (CI/CD)
- **FR-015**: System MUST fail CI/CD build if high-severity vulnerabilities are found
- **FR-016**: System MUST validate JWT/session tokens for tampering
- **FR-017**: System MUST implement CSRF protection on all state-changing operations

### Non-Functional Requirements

- **NFR-001**: Rate limiter MUST add < 10ms latency to request processing
- **NFR-002**: Security headers MUST be added via middleware (no per-route duplication)
- **NFR-003**: Input validation errors MUST return helpful messages (no stack traces to users)
- **NFR-004**: Security scan results MUST be archived for compliance audits
- **NFR-005**: Penetration test reports MUST be generated quarterly (minimum)

### Key Entities *(include if feature involves data)*

- **RateLimitRule**: Represents rate limit configuration with endpoint_pattern, limit (requests), window (seconds), tier_overrides
- **SecurityEvent**: Represents logged security event with event_type (failed_auth|rate_limit|validation_error), user_id, ip_address, timestamp, details
- **VulnerabilityReport**: Represents security scan result with scan_type (dependency|code|pentest), severity (low|medium|high|critical), description, remediation_status

## Technical Architecture

### Components to Implement

1. **Input Validation Layer** (app/validators.py) - NEW FILE
   - `validate_ticker_symbol(ticker: str) -> str` - Whitelist alphanumeric + basic symbols
   - `validate_email(email: str) -> str` - RFC 5322 regex
   - `validate_json_payload(schema: dict) -> decorator` - Marshmallow or Pydantic schemas
   - `sanitize_html(text: str) -> str` - Bleach library for HTML sanitization

2. **Rate Limiting** (app/middleware/rate_limiter.py) - NEW FILE
   - Use Flask-Limiter extension
   - Configure storage backend (in-memory for dev, Redis for production)
   - Define rate limit decorators: `@rate_limit("100/hour")` with tier overrides
   - Custom error handler for 429 responses

3. **Security Headers Middleware** (app/middleware/security_headers.py) - NEW FILE
   - After-request hook to add headers to all responses
   - Configurable CSP policy
   - HSTS configuration (max-age=31536000, includeSubDomains)

4. **Security Logging** (app/services/security_logger.py) - NEW FILE
   - Centralized logging for security events
   - Structured logging (JSON format)
   - Integration with app logger
   - Configurable log levels and destinations

5. **CI/CD Security Scans** (.github/workflows/security-scan.yml) - NEW FILE
   - pip-audit for dependency scanning
   - bandit for static code analysis
   - Fail thresholds configuration
   - GitHub Security Advisories integration

6. **File Upload Validation** (app/validators.py) - EXTEND
   - `validate_file_upload(file) -> bool` - Check extension, MIME type, size
   - Magic byte verification (not just extension check)

### Security Controls

- ✅ Parameterized queries (already using SQLite with parameterized statements)
- ❌ Input validation decorators (needs implementation)
- ❌ Output sanitization (needs Bleach or similar)
- ❌ Rate limiting (needs Flask-Limiter)
- ❌ Security headers (needs middleware)
- ❌ CSRF protection (needs Flask-WTF - partially from Epic 1)
- ❌ File upload validation (needs implementation)
- ❌ Security event logging (needs structured logger)
- ❌ Dependency scanning (needs CI/CD integration)
- ❌ Static code analysis (needs CI/CD integration)

### External Dependencies

- **Flask-Limiter**: Rate limiting (add to requirements.txt)
- **Bleach**: HTML sanitization (add to requirements.txt)
- **marshmallow** or **pydantic**: Schema validation (add to requirements.txt)
- **pip-audit**: Dependency vulnerability scanning (CI/CD only)
- **bandit**: Python security linter (CI/CD only)
- **OWASP ZAP**: Penetration testing (manual/scheduled)
- **Redis** (optional): Distributed rate limiting storage (production only)

### Configuration

```python
# app/config.py - EXTEND

class SecurityConfig:
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "memory://")
    RATELIMIT_STRATEGY = "moving-window"
    RATELIMIT_DEFAULT = "200 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Tier-based rate limits (requests per hour)
    TIER_RATE_LIMITS = {
        "FREE": 100,
        "MIDDLE": 300,
        "TOP": 1000
    }
    
    # Content Security Policy
    CSP_POLICY = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "https://cdn.plot.ly"],
        "style-src": ["'self'", "'unsafe-inline'"],  # TODO: Remove unsafe-inline
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'"],
        "font-src": ["'self'"],
        "frame-ancestors": ["'none'"]
    }
    
    # File Upload
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".json", ".csv", ".txt"}
    
    # Security Logging
    SECURITY_LOG_FILE = "logs/security.log"
    SECURITY_LOG_FORMAT = "json"
```

## Success Criteria

### Phase 1: Input Validation & Sanitization (Day 1)
- [ ] Input validation decorators implemented (≥5 validators)
- [ ] Output sanitization applied to all HTML rendering
- [ ] File upload validation enforced
- [ ] ≥15 negative test cases (malicious inputs) passing
- [ ] XSS attempts blocked (verified with manual testing)
- [ ] SQL injection attempts blocked (verified with SQLMap or manual)

### Phase 2: Rate Limiting (Day 2)
- [ ] Flask-Limiter integrated and configured
- [ ] Rate limits applied to ≥10 endpoints
- [ ] Tier-based rate limit overrides working
- [ ] 429 responses properly formatted (JSON with retry-after)
- [ ] Rate limit headers present (X-RateLimit-Limit, X-RateLimit-Remaining)
- [ ] ≥10 rate limit tests passing (unit + integration)

### Phase 3: Security Headers & Logging (Day 3)
- [ ] Security headers middleware implemented
- [ ] All responses include CSP, X-Frame-Options, HSTS, etc.
- [ ] Security event logger implemented
- [ ] All failed auth, validation errors, rate limits logged
- [ ] Log format is structured JSON
- [ ] ≥5 security header tests passing

### Phase 4: CI/CD Security Scans (Day 4)
- [ ] pip-audit integrated in GitHub Actions
- [ ] bandit integrated in GitHub Actions
- [ ] Build fails on high-severity findings
- [ ] Security scan results archived as artifacts
- [ ] Badge added to README showing scan status

### Phase 5: Penetration Testing (Day 5 - Optional)
- [ ] OWASP ZAP automated scan executed
- [ ] Zero high-severity vulnerabilities found
- [ ] Penetration test report generated
- [ ] Remediation plan created for medium-severity findings

### Overall Completion
- [ ] All Epic 1 tests still passing (no regressions)
- [ ] ≥30 new security tests passing
- [ ] Security headers verified with securityheaders.com (A+ rating)
- [ ] Rate limiting verified with load testing (Apache Bench or Locust)
- [ ] Zero OWASP Top 10 vulnerabilities (verified with manual audit)
- [ ] Documentation updated (security controls documented)

## Out of Scope (Future Epics)

- WAF (Web Application Firewall) integration (Epic 8 or infrastructure)
- DDoS protection (infrastructure/Cloudflare)
- Intrusion Detection System (IDS) (infrastructure)
- Security Information and Event Management (SIEM) integration (enterprise)
- Bug bounty program setup (future)
- SOC 2 compliance audit (enterprise)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Rate limiter causes performance degradation | Medium | High | Use in-memory storage for dev, Redis for prod; benchmark before deployment |
| CSP breaks existing functionality | High | Medium | Test thoroughly in staging; whitelist specific domains as needed |
| False positives from security scanners | High | Low | Maintain suppression list with justifications; manual review |
| Penetration test reveals critical vulnerability | Low | Critical | Fix immediately before going live; consider bug bounty program |
| Security logging fills disk | Medium | Medium | Implement log rotation and retention policies |

## OWASP Top 10 Compliance Matrix

| OWASP Risk | Mitigation | Status |
|------------|------------|--------|
| A01: Broken Access Control | Tier-based access control (@require_tier) | ✅ Epic 1 |
| A02: Cryptographic Failures | Argon2id password hashing, HTTPS enforcement | ✅ Epic 1 + HSTS (this epic) |
| A03: Injection | Parameterized queries, input validation | ⚠️ This epic |
| A04: Insecure Design | Threat modeling, security-by-design | ⚠️ This epic |
| A05: Security Misconfiguration | Security headers, secure defaults | ⚠️ This epic |
| A06: Vulnerable Components | Dependency scanning (pip-audit) | ⚠️ This epic |
| A07: Auth Failures | Account lockout, strong password policy | ✅ Epic 1 |
| A08: Data Integrity Failures | CSRF protection, input validation | ⚠️ Epic 1 (CSRF) + This epic |
| A09: Logging Failures | Security event logging | ⚠️ This epic |
| A10: SSRF | Input validation on URLs, whitelist external APIs | ⚠️ This epic |

## Implementation Notes

- Start with input validation (immediate security win)
- Test rate limiting under load (Apache Bench: `ab -n 1000 -c 10 http://localhost:5000/api/endpoint`)
- Use CSP report-only mode initially to catch issues before enforcing
- Review dependency scan results weekly (automate with GitHub Dependabot)
- Document all security exceptions/suppressions with justifications

---

**Next Steps**: Generate PLAN.md with detailed implementation tasks
