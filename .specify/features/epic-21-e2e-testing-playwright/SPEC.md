# Epic 21: End-to-End Testing with Playwright

**Epic ID**: Epic 21  
**Status**: BACKLOG  
**Priority**: P2 (Medium - Quality improvement)  
**Dependencies**: Epic 1 (Authentication), Epic 5 (Portfolio Analysis), Epic 6 (Vestor AI Chat)  
**Estimated Effort**: 2-3 weeks  
**Business Value**: Prevent regressions, improve release confidence, reduce manual QA

---

## 📋 Overview

### Problem Statement
The application has good unit test coverage (231 tests) but lacks end-to-end UI testing. User workflows (registration → login → analysis → chat → export) are not tested in real browsers. Regressions in UI can slip into production undetected.

**Current State:**
- 231 unit/integration tests (backend only)
- Manual UI testing before releases
- No automated browser testing
- No cross-browser testing (Chrome, Firefox, Safari)
- No visual regression testing
- Frontend JavaScript not tested

**Desired State:**
- Playwright-based E2E test suite
- Automated user journey tests (full workflows)
- Cross-browser testing (Chrome, Firefox, Safari)
- Visual regression testing (screenshot comparisons)
- CI/CD integration (run on every PR)
- Test coverage for all critical user paths

### Business Impact
- **Quality**: Catch UI bugs before production
- **Confidence**: Ship new features faster with safety net
- **Cost**: Reduce manual QA time by 70%
- **User Experience**: Ensure consistent UX across browsers

---

## 🎯 User Stories

### **US21.1: As a developer, I want to test complete user journeys** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 5 days  
**Business Value**: Prevent critical workflow regressions

**Acceptance Criteria:**
1. Test user registration flow (form → email verification → login)
2. Test user login flow (credentials → dashboard)
3. Test stock analysis flow (search ticker → run analysis → view results)
4. Test Vestor AI chat flow (start chat → ask questions → get responses)
5. Test tier upgrade flow (pricing page → checkout → tier updated)
6. Test export flow (analysis → export JSON/CSV → download)
7. All tests run in Chrome, Firefox, and Safari (WebKit)

**User Journeys to Test:**

**Journey 1: New User Registration & First Analysis**
```
1. Visit homepage
2. Click "Sign Up"
3. Fill registration form (email, password, name)
4. Submit form
5. Verify success message
6. Login with credentials
7. Navigate to analysis page
8. Search for ticker "AAPL"
9. Click "Analyze"
10. Wait for results
11. Verify analysis data displayed
12. Logout
```

**Journey 2: Premium User - Full Feature Access**
```
1. Login as premium user
2. Run advanced analysis (multiple tickers)
3. Export results as PDF
4. Start Vestor AI chat
5. Ask 3 questions
6. Verify AI responses
7. View billing history
8. Logout
```

**Journey 3: Free Tier - Hit Usage Limit**
```
1. Login as free user
2. Run 3 analyses (free tier limit)
3. Try 4th analysis
4. Verify "upgrade" prompt shown
5. Click upgrade
6. Verify pricing page displayed
```

**Technical Notes:**
- Use Playwright's `test.describe()` to group journeys
- Use Page Object Model (POM) pattern for maintainability
- Run tests in parallel (3 workers)

---

### **US21.2: As a developer, I want to test cross-browser compatibility** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 2 days  
**Business Value**: Ensure consistent UX across browsers

**Acceptance Criteria:**
1. All E2E tests run in 3 browsers: Chromium, Firefox, WebKit (Safari)
2. Test results show pass/fail per browser
3. Known browser-specific issues documented (e.g., Safari date picker)
4. Screenshots captured on test failure (per browser)
5. Browser matrix displayed in CI/CD logs

**Browser Support:**
- **Chrome/Chromium**: Latest stable (primary)
- **Firefox**: Latest stable
- **Safari/WebKit**: Latest stable (macOS/iOS)
- **Edge**: (optional, uses Chromium engine)

**Technical Notes:**
- Playwright supports all 3 browsers out of the box
- Use `@playwright/test` projects feature for multi-browser config
- CI runs all browsers in parallel (GitHub Actions matrix)

---

### **US21.3: As a developer, I want visual regression testing** ⭐ P2
**Priority**: P2 (Nice-to-have)  
**Effort**: 3 days  
**Business Value**: Detect unintended UI changes

**Acceptance Criteria:**
1. Baseline screenshots captured for key pages (homepage, dashboard, analysis results)
2. Visual diff generated when UI changes
3. Tests fail if diff exceeds threshold (e.g., 0.1% pixel difference)
4. Developers can review diffs and approve changes
5. Baseline screenshots stored in git (or artifact storage)
6. Visual tests run in Chromium only (consistent rendering)

**Pages to Test:**
- Homepage
- Login/Registration forms
- Dashboard (authenticated)
- Stock analysis results page
- Vestor AI chat interface
- Pricing page
- User profile page

**Technical Notes:**
- Use Playwright's `expect(page).toHaveScreenshot()` API
- Store baselines in `tests/e2e/__screenshots__/`
- Update baselines with `playwright test --update-snapshots`
- Use `threshold` option to ignore minor rendering differences

---

### **US21.4: As a developer, I want to test responsive design (mobile)** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 2 days  
**Business Value**: Ensure mobile users have good experience

**Acceptance Criteria:**
1. Tests run in desktop (1920x1080) and mobile (375x667) viewports
2. Mobile-specific UI elements tested (hamburger menu, touch interactions)
3. Mobile tests verify responsive layout (no horizontal scroll, readable text)
4. Test viewport rotation (portrait → landscape)
5. Test touch gestures (swipe, tap, long-press)

**Viewports to Test:**
- **Desktop**: 1920x1080 (full HD)
- **Tablet**: 768x1024 (iPad)
- **Mobile**: 375x667 (iPhone SE)
- **Mobile Large**: 414x896 (iPhone 11 Pro)

**Technical Notes:**
- Use `page.setViewportSize()` to change viewport
- Use Playwright's mobile emulation (user agent, touch events)
- Test responsive navigation (desktop navbar vs. mobile hamburger menu)

---

### **US21.5: As a developer, I want E2E tests in CI/CD pipeline** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 2 days  
**Business Value**: Prevent broken UI from merging

**Acceptance Criteria:**
1. Playwright tests run on every PR
2. Tests run in parallel (3 browsers x 3 workers = 9 parallel tests)
3. Test report published as PR comment
4. Failure screenshots attached to CI artifacts
5. PR cannot merge if E2E tests fail
6. Tests run against staging environment (not production)

**CI Integration:**
```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - name: Install Playwright
        run: |
          npm ci
          npx playwright install --with-deps ${{ matrix.browser }}
      - name: Run E2E tests
        run: npx playwright test --project=${{ matrix.browser }}
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report-${{ matrix.browser }}
          path: playwright-report/
```

---

## 🔧 Functional Requirements

### Test Coverage
1. **Authentication**: Registration, login, logout, password reset
2. **Stock Analysis**: Search, analyze, view results, export
3. **Vestor AI Chat**: Start chat, ask questions, view responses
4. **Tier Management**: View tier, upgrade, downgrade, cancel
5. **Profile Management**: Edit profile, change password, view history
6. **Error Handling**: Test 404 page, API errors, validation errors

### Cross-Browser Testing
7. **Browsers**: Chromium, Firefox, WebKit (Safari)
8. **Viewports**: Desktop, tablet, mobile
9. **Parallelization**: Run tests in parallel (3 browsers x 3 workers)

### Visual Regression
10. **Baseline Screenshots**: Homepage, dashboard, analysis, chat, pricing
11. **Diff Threshold**: Fail if >0.1% pixel difference
12. **Update Workflow**: `playwright test --update-snapshots`

### CI/CD Integration
13. **Automated Runs**: On every PR and commit to main
14. **Test Reports**: HTML report published as CI artifact
15. **Failure Artifacts**: Screenshots and videos on test failure
16. **PR Status Check**: E2E tests must pass before merge

---

## 🏗️ Non-Functional Requirements

### Performance
1. **Test Execution Time**: Full suite completes in <10 minutes
2. **Parallelization**: Run tests across 3 workers per browser
3. **Flakiness**: <1% test flakiness rate (retry 2x on failure)

### Maintainability
4. **Page Object Model**: Reusable page classes (HomePage, LoginPage, etc.)
5. **Test Data**: Use factories/fixtures for test data
6. **DRY Principle**: Shared utilities for common actions (login, logout)

### Reliability
7. **Retry Logic**: Auto-retry flaky tests (max 2 retries)
8. **Timeouts**: Explicit waits for elements (no hardcoded sleeps)
9. **Idempotency**: Tests can run in any order

### Observability
10. **Screenshots**: Captured on test failure
11. **Videos**: Recorded for failing tests
12. **Traces**: Playwright trace for debugging

---

## 🧪 Test Structure

### Directory Layout
```
tests/e2e/
├── fixtures/           # Shared fixtures (authenticated user, test data)
├── pages/              # Page Object Model classes
│   ├── HomePage.ts
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   ├── AnalysisPage.ts
│   └── ChatPage.ts
├── tests/              # Test files
│   ├── auth.spec.ts
│   ├── analysis.spec.ts
│   ├── chat.spec.ts
│   ├── tier-upgrade.spec.ts
│   └── responsive.spec.ts
├── utils/              # Helper functions
│   ├── testData.ts     # Test data factories
│   └── helpers.ts      # Common utilities
└── playwright.config.ts
```

### Page Object Model Example
```typescript
// pages/LoginPage.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('#email');
    this.passwordInput = page.locator('#password');
    this.submitButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }
}
```

### Test Example
```typescript
// tests/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

test.describe('Authentication', () => {
  test('should allow user to login with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    
    await loginPage.login('test@example.com', 'Password123!');
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Verify user menu shows email
    const dashboardPage = new DashboardPage(page);
    await expect(dashboardPage.userMenu).toContainText('test@example.com');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    
    await loginPage.login('test@example.com', 'WrongPassword');
    
    const errorMessage = await loginPage.getErrorMessage();
    expect(errorMessage).toContain('Invalid credentials');
  });
});
```

---

## 📊 Success Metrics

### Quality Metrics
- **Test Coverage**: 100% of critical user journeys tested
- **Flakiness Rate**: <1% (tests fail inconsistently)
- **Defect Detection**: E2E tests catch 90% of UI regressions before production

### Performance Metrics
- **Test Execution Time**: <10 minutes for full suite (3 browsers)
- **CI/CD Integration**: Tests run on 100% of PRs
- **Failure Rate**: <5% of PRs fail E2E tests (indicates healthy quality)

### Business Metrics
- **Manual QA Reduction**: 70% reduction in manual testing time
- **Release Confidence**: Developers can ship with confidence (no manual QA gate)
- **Production Defects**: 50% reduction in UI-related bugs in production

---

## 🔗 Dependencies

### Tools
- **Playwright**: v1.40+ (browser automation)
- **Node.js**: 18+ (Playwright runtime)
- **TypeScript**: For type-safe tests
- **GitHub Actions**: CI/CD integration

### Infrastructure
- **Staging Environment**: Tests run against staging, not production
- **Test Database**: Separate database for E2E tests (reset between runs)
- **Test User Accounts**: Seeded test users (free tier, premium tier, admin)

---

## 🚀 Implementation Phases

### Phase 1: Setup & Infrastructure (Week 1)
- Install Playwright and configure project
- Set up Page Object Model structure
- Create base fixtures (authenticated user, test data)
- Configure CI/CD integration (GitHub Actions)

### Phase 2: Core User Journey Tests (Week 1-2)
- Test authentication flows (register, login, logout)
- Test stock analysis workflow
- Test Vestor AI chat workflow
- Test tier upgrade flow

### Phase 3: Cross-Browser & Responsive (Week 2)
- Configure multi-browser testing (Chromium, Firefox, WebKit)
- Add responsive design tests (desktop, tablet, mobile)
- Test mobile-specific UI (hamburger menu, touch gestures)

### Phase 4: Visual Regression & Advanced (Week 2-3)
- Implement visual regression tests
- Add error scenario tests (404, API failures)
- Add performance tests (page load time, Lighthouse scores)
- Optimize test execution speed (parallelization)

---

## 🎯 Definition of Done

### Test Coverage Complete
- [ ] All critical user journeys tested (auth, analysis, chat, tier upgrade)
- [ ] Cross-browser tests (Chromium, Firefox, WebKit)
- [ ] Responsive tests (desktop, tablet, mobile)
- [ ] Visual regression tests for key pages

### CI/CD Integration Complete
- [ ] Tests run on every PR
- [ ] Test reports published to CI artifacts
- [ ] PR cannot merge if tests fail
- [ ] Failure screenshots/videos captured

### Documentation Complete
- [ ] Test writing guide for developers
- [ ] Page Object Model patterns documented
- [ ] CI/CD integration guide
- [ ] Debugging guide (traces, screenshots)

### Quality Gates Met
- [ ] Test flakiness <1%
- [ ] Full suite runs in <10 minutes
- [ ] 100% of critical paths covered

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Test flakiness (intermittent failures) | HIGH | Use explicit waits, retry logic, stable selectors |
| Slow test execution (>15 mins) | MEDIUM | Parallelize tests, use headless browsers, optimize waits |
| Maintenance burden (tests break often) | HIGH | Use Page Object Model, semantic selectors, stable test data |
| Visual regression false positives | MEDIUM | Set diff threshold (0.1%), ignore dynamic content |
| CI resource limits (GitHub Actions) | LOW | Use self-hosted runners if needed, optimize test count |

---

## 📚 Resources

### Documentation
- [Playwright Docs](https://playwright.dev/docs/intro)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)
- [Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [CI/CD Integration](https://playwright.dev/docs/ci-intro)

### Examples
- [Playwright Test Examples](https://github.com/microsoft/playwright/tree/main/examples)
- [Page Object Model Template](https://github.com/microsoft/playwright/tree/main/examples/todomvc)

---

**Epic Status**: BACKLOG  
**Recommended Phase**: Phase 5 or 6 (after Epic 1-3 complete)  
**Next Step**: Complete Epic 1-2-3, then begin Playwright setup  
**Owner**: TBD  
**Last Updated**: 2026-01-08