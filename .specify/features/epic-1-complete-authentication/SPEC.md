# Feature Specification: Complete Authentication System

**Feature Branch**: `feature/authentication-tier-system` (already exists)  
**Created**: 2026-01-08  
**Status**: In Progress (~40% complete)  
**Epic**: Epic 1 - Complete Authentication System  
**Priority**: HIGH  
**Estimated Effort**: 3-5 days

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration (Priority: P1)

New users can create an account with email and password, receiving a FREE tier account by default.

**Why this priority**: Core prerequisite for all other authentication features. Without registration, no users can access the system.

**Independent Test**: Can be fully tested by submitting a registration form with valid credentials and verifying a new user record is created with FREE tier access.

**Acceptance Scenarios**:

1. **Given** a new visitor on the homepage, **When** they click "Register" and submit valid email/password, **Then** account is created with FREE tier and they're redirected to dashboard
2. **Given** a registration form, **When** password is too weak (< 8 chars), **Then** system rejects with clear error message
3. **Given** a registration form, **When** email is already registered, **Then** system shows "Email already exists" error
4. **Given** successful registration, **When** user logs in immediately, **Then** session is created with correct tier badge

---

### User Story 2 - User Login (Priority: P1)

Registered users can log in with email and password, establishing an authenticated session.

**Why this priority**: Equally critical as registration. Users must be able to access their accounts.

**Independent Test**: Can be tested by creating a user via backend, then logging in via the UI and verifying session state.

**Acceptance Scenarios**:

1. **Given** a registered user at login page, **When** they submit correct credentials, **Then** session is created and they're redirected to dashboard
2. **Given** a registered user at login page, **When** they submit wrong password 3 times, **Then** account is locked for 15 minutes
3. **Given** a locked account, **When** user tries to login before timeout, **Then** system shows "Account locked" message with remaining time
4. **Given** an authenticated session, **When** user refreshes the page, **Then** session persists and user remains logged in

---

### User Story 3 - Session Management (Priority: P1)

Authenticated users have persistent sessions across page reloads with secure HTTPOnly cookies.

**Why this priority**: Without session management, users would need to re-login constantly, breaking UX.

**Independent Test**: Can be tested by logging in, closing browser, reopening, and verifying session is still valid.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they close and reopen the browser within 24 hours, **Then** session is still valid
2. **Given** an authenticated user, **When** they click "Logout", **Then** session is destroyed and they're redirected to login page
3. **Given** an expired session (> 24 hours), **When** user tries to access protected route, **Then** they're redirected to login with "Session expired" message
4. **Given** an active session, **When** inspecting cookies, **Then** session cookie has HTTPOnly and Secure flags set

---

### User Story 4 - Tier-Based Feature Access (Priority: P2)

Users can only access features permitted by their subscription tier (FREE, MIDDLE, TOP).

**Why this priority**: Core business logic for monetization, but can be implemented after basic auth works.

**Independent Test**: Can be tested by creating users with different tiers and attempting to access restricted features.

**Acceptance Scenarios**:

1. **Given** a FREE tier user, **When** they try to access "Advanced Analysis" route, **Then** system returns 403 Forbidden with upgrade prompt
2. **Given** a MIDDLE tier user, **When** they access "Advanced Analysis", **Then** feature loads successfully
3. **Given** a TOP tier user, **When** they access any feature, **Then** all features are accessible
4. **Given** a FREE tier user in the UI, **When** they view the dashboard, **Then** premium features are grayed out with "Upgrade to MIDDLE" badges

---

### User Story 5 - User Profile Management (Priority: P3)

Authenticated users can view and update their profile information including email and password.

**Why this priority**: Important for UX but not critical for MVP. Can be added after core auth flow works.

**Independent Test**: Can be tested by logging in and updating profile fields, then verifying changes persist.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they visit /auth/me, **Then** their profile data (email, tier, created_at) is displayed
2. **Given** a user on profile page, **When** they update their email, **Then** email is updated after password confirmation
3. **Given** a user on profile page, **When** they change password with correct old password, **Then** new password is hashed and stored
4. **Given** a user trying to change password, **When** old password is incorrect, **Then** system rejects with "Current password is incorrect" error

---

### Edge Cases

- What happens when session cookie is manually tampered with? → System invalidates session and redirects to login
- How does system handle concurrent logins from different devices? → Allow multiple active sessions (track with different session IDs)
- What if user deletes account while having active session? → Invalidate all sessions for that user
- How are failed login attempts tracked across multiple IPs? → Per-user account lockout (not IP-based)
- What happens during session ID collision? → UUID4 makes this astronomically unlikely, but regenerate if detected
- How does system handle password reset tokens? → Not in scope for Epic 1 (add to Epic 6 or future)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide POST /auth/register endpoint accepting email and password
- **FR-002**: System MUST validate email format (RFC 5322 compliant)
- **FR-003**: System MUST enforce password strength (≥8 chars, 1 uppercase, 1 lowercase, 1 digit)
- **FR-004**: System MUST hash passwords using Argon2id before storage
- **FR-005**: System MUST assign FREE tier to new users by default
- **FR-006**: System MUST provide POST /auth/login endpoint accepting email and password
- **FR-007**: System MUST create session with UUID4 token on successful login
- **FR-008**: System MUST set HTTPOnly and Secure flags on session cookies
- **FR-009**: System MUST implement account lockout after 5 failed login attempts for 15 minutes
- **FR-010**: System MUST provide POST /auth/logout endpoint to destroy sessions
- **FR-011**: System MUST provide GET /auth/me endpoint returning user profile for authenticated users
- **FR-012**: System MUST validate session on every protected route access
- **FR-013**: System MUST enforce tier-based access control via @require_tier decorator
- **FR-014**: System MUST track failed login attempts per user (not per IP)
- **FR-015**: System MUST return 401 Unauthorized for invalid sessions
- **FR-016**: System MUST return 403 Forbidden for insufficient tier access
- **FR-017**: System MUST log all authentication events (login, logout, failed attempts, lockouts)

### Key Entities *(include if feature involves data)*

- **User**: Represents a registered account with email, hashed_password, tier (FREE|MIDDLE|TOP), created_at, failed_login_attempts, locked_until
- **Session**: Represents an active authenticated session with session_id (UUID4), user_id, created_at, expires_at (24h from creation)
- **Tier**: Enum representing subscription level (FREE, MIDDLE, TOP) with associated feature permissions

## Technical Architecture

### Components Already Implemented ✅

1. **Repository Layer** (app/repositories/)
   - `UserRepositoryInterface` - Abstract contract
   - `SqliteUserRepository` - SQLite implementation
   - `InMemoryUserRepository` - Testing implementation
   - `SessionRepositoryInterface` - Abstract contract
   - `SqliteSessionRepository` - SQLite implementation
   - `InMemorySessionRepository` - Testing implementation

2. **Domain Models** (app/models/)
   - `User` - Pure Python dataclass with methods for password verification, lockout checks
   - `Session` - Pure Python dataclass with expiration logic
   - `UserTier` - Enum (FREE, MIDDLE, TOP)

3. **Service Layer** (app/services/)
   - `AuthenticationService` - Business logic for register, login, logout, validate_session, check_tier_access
   - Dependency Injection ready (takes repositories in constructor)

4. **Tests** (tests/unit/)
   - 106 unit tests covering repositories, models, and service layer ✅ All passing

### Components Missing ❌

1. **Route Layer** (app/routes/auth_routes.py) - NEW FILE NEEDED
   - POST /auth/register
   - POST /auth/login
   - POST /auth/logout
   - GET /auth/me
   - Error handling and response formatting

2. **Flask Integration** (app/__init__.py or app/factory.py)
   - Initialize SqliteRepositoryFactory on app startup
   - Register auth blueprint
   - Configure session management with Flask-Login or custom middleware
   - Set up CSRF protection with Flask-WTF

3. **Middleware/Decorators** (app/decorators.py) - NEW FILE NEEDED
   - `@require_auth` - Decorator to protect routes requiring login
   - `@require_tier(UserTier.MIDDLE)` - Decorator to enforce tier access

4. **Frontend UI** (static/js/auth.js, templates/auth/) - NEW FILES NEEDED
   - Login form (templates/auth/login.html)
   - Registration form (templates/auth/register.html)
   - Session state management (static/js/auth.js)
   - Tier badge display component

5. **Integration Tests** (tests/integration/test_auth_flow.py) - NEW FILE NEEDED
   - Full registration → login → access protected route → logout flow
   - Tier enforcement tests
   - Session persistence tests
   - Account lockout tests

### Security Controls

- ✅ Argon2id password hashing (implemented)
- ✅ Account lockout after 5 failed attempts (implemented in service layer)
- ❌ CSRF protection (needs Flask-WTF integration)
- ❌ HTTPOnly + Secure cookie flags (needs Flask session config)
- ✅ No secrets in code (using environment variables)
- ❌ Rate limiting per route (needs Flask-Limiter)
- ❌ Input validation decorators (needs marshmallow or similar)
- ❌ XSS protection in templates (needs Jinja2 autoescaping verification)

### Database Schema (SQLite)

```sql
-- Already defined in app/repositories/sqlite_repositories.py

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'FREE',
    created_at TEXT NOT NULL,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Dependencies

- **Existing Code**: Feature branch `feature/authentication-tier-system` must be current
- **External Libraries**: 
  - Flask-WTF (CSRF protection) - needs to be added to requirements.txt
  - Flask-Limiter (rate limiting) - optional for Epic 2
- **Environment Variables**: 
  - SECRET_KEY (for session signing) - must be set
  - DATABASE_URL (SQLite path) - must be set

## Success Criteria

### Phase 1: Route Layer (Day 1)
- [ ] POST /auth/register endpoint created and tested (≥5 integration tests)
- [ ] POST /auth/login endpoint created and tested (≥5 integration tests)
- [ ] POST /auth/logout endpoint created and tested (≥2 integration tests)
- [ ] GET /auth/me endpoint created and tested (≥3 integration tests)
- [ ] Error responses properly formatted (JSON with error messages)
- [ ] All 20+ integration tests passing

### Phase 2: Flask Integration (Day 2)
- [ ] SqliteRepositoryFactory initialized in app factory
- [ ] Auth blueprint registered
- [ ] Session management configured (HTTPOnly, Secure flags)
- [ ] CSRF protection enabled with Flask-WTF
- [ ] App starts without errors
- [ ] Session persists across requests (integration test)

### Phase 3: Frontend UI (Days 3-4)
- [ ] Login form created (templates/auth/login.html)
- [ ] Registration form created (templates/auth/register.html)
- [ ] Session state tracked in frontend (localStorage or cookie check)
- [ ] Tier badge displayed on dashboard
- [ ] Form validation (client-side + server-side)
- [ ] Error messages displayed to user
- [ ] UI automation tests with Playwright (≥10 tests)

### Phase 4: Feature Gating (Day 5)
- [ ] @require_auth decorator applied to ≥3 existing routes
- [ ] @require_tier decorator applied to ≥2 premium features
- [ ] Frontend hides/shows features based on tier
- [ ] Usage tracking incremented on feature access
- [ ] Tier enforcement tests passing (≥5 tests)

### Overall Completion
- [ ] All 106 existing unit tests still passing
- [ ] ≥30 new integration tests passing
- [ ] ≥10 UI automation tests passing
- [ ] Zero security vulnerabilities (manual OWASP check)
- [ ] Zero secrets in code (git grep SECRET_KEY returns empty)
- [ ] Documentation updated (API endpoints documented)

## Out of Scope (Future Epics)

- Password reset via email (Epic 6 or future)
- OAuth integration (Epic 6)
- Admin user management panel (Epic 7 or future)
- Email verification on registration (Epic 6 or future)
- Two-factor authentication (Epic 8 or future)
- Payment integration (Epic 4)
- Coupon redemption (Epic 5)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Session cookie conflicts with existing Flask session | Medium | High | Test early, use custom cookie name if needed |
| CSRF breaks existing frontend AJAX calls | High | Medium | Add CSRF token to all forms, exempt API endpoints if needed |
| Account lockout logic has race condition | Low | Medium | Use database-level locking or atomic updates |
| Frontend state management gets out of sync | Medium | Medium | Single source of truth (backend session validation) |
| Test coverage drops below 90% | Medium | High | Enforce coverage checks in CI/CD |

## Implementation Notes

- Start with route layer (easiest to test in isolation)
- Integrate one component at a time (don't do big-bang integration)
- Test after each component (keep 106 existing tests passing)
- Use feature flags if deploying partially complete features
- Document API endpoints using OpenAPI/Swagger (future Epic)

---

**Next Steps**: Generate PLAN.md with detailed implementation tasks
