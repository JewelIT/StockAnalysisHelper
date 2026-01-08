# Epic 4: Payment Integration & Subscription Management

**Epic ID**: Epic 4  
**Status**: PLANNED  
**Priority**: P1 (Critical - Blocks monetization)  
**Dependencies**: Epic 1 (Authentication) must be complete  
**Estimated Effort**: 3-4 weeks  
**Business Value**: Enable recurring revenue, convert free users to paid tiers

---

## 📋 Overview

### Problem Statement
The application currently has tier-based feature gating but no payment infrastructure to monetize premium features. Users cannot upgrade tiers, and there's no subscription management system.

**Current State:**
- Tier system exists (free, basic, premium, enterprise)
- No payment processing
- Manual tier upgrades via admin panel
- No billing history or invoices
- No subscription lifecycle management

**Desired State:**
- Stripe integration for payment processing
- Self-service subscription upgrades/downgrades
- Automated billing and invoice generation
- Webhook handlers for subscription events
- Subscription analytics dashboard

### Business Impact
- **Revenue Generation**: Enable $29/mo Basic, $99/mo Premium, custom Enterprise pricing
- **Self-Service**: Reduce manual tier changes by 100%
- **User Retention**: Automated subscription management reduces churn
- **Compliance**: PCI-compliant payment handling via Stripe

---

## 🎯 User Stories

### **US4.1: As a user, I want to subscribe to a paid tier** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 5 days  
**Business Value**: Enables primary revenue stream

**Acceptance Criteria:**
1. User can view pricing page with all tier options
2. User can select a tier (Basic, Premium, Enterprise)
3. User is redirected to Stripe Checkout for payment
4. Upon successful payment, user's tier is automatically upgraded
5. User receives confirmation email with receipt
6. Subscription start date is recorded in database

**Technical Notes:**
- Use Stripe Checkout (hosted payment page) for PCI compliance
- Implement Stripe Customer Portal for self-service management
- Store Stripe customer_id and subscription_id in users table

---

### **US4.2: As a subscribed user, I want to manage my subscription** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 3 days  
**Business Value**: Reduces support burden, improves UX

**Acceptance Criteria:**
1. User can view current subscription status (tier, renewal date, price)
2. User can upgrade to higher tier (immediate, prorated billing)
3. User can downgrade to lower tier (at end of billing period)
4. User can cancel subscription (access remains until period end)
5. User can update payment method (via Stripe Customer Portal)
6. User can view billing history and download invoices

**Technical Notes:**
- Use Stripe Customer Portal for subscription management UI
- Implement proration logic for mid-cycle upgrades
- Schedule downgrades/cancellations for period end

---

### **US4.3: As the system, I want to handle subscription events automatically** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 4 days  
**Business Value**: Prevents unauthorized access, ensures billing integrity

**Acceptance Criteria:**
1. System listens for Stripe webhooks (subscription.created, updated, deleted)
2. On payment failure, user is notified and grace period begins (3 days)
3. After grace period, user is downgraded to free tier
4. On successful renewal, subscription expiry is extended
5. On cancellation, user retains access until period end, then downgraded
6. All webhook events are logged and idempotent

**Technical Notes:**
- Verify webhook signatures using Stripe webhook secret
- Implement idempotency keys to prevent duplicate processing
- Use background task queue (Celery) for webhook processing
- Handle all Stripe events: `customer.subscription.*`, `invoice.*`, `payment_intent.*`

---

### **US4.4: As an admin, I want to view subscription analytics** ⭐ P2
**Priority**: P2 (Nice-to-have)  
**Effort**: 2 days  
**Business Value**: Inform pricing strategy, identify churn patterns

**Acceptance Criteria:**
1. Admin dashboard shows MRR (Monthly Recurring Revenue)
2. Admin can view tier distribution (% free vs. paid)
3. Admin can view churn rate (cancellations per month)
4. Admin can view failed payment rate
5. Admin can export subscription data to CSV

**Technical Notes:**
- Query Stripe API for analytics (use cached data for performance)
- Store MRR snapshots daily for historical trends
- Use Stripe Billing reports as source of truth

---

### **US4.5: As a user, I want to apply promo codes for discounts** ⭐ P2
**Priority**: P2 (Nice-to-have)  
**Effort**: 2 days  
**Business Value**: Marketing campaigns, affiliate partnerships

**Acceptance Criteria:**
1. User can enter promo code at checkout
2. Valid codes apply discount (% off or fixed amount)
3. Invalid/expired codes show error message
4. Promo code usage is tracked and limited (max redemptions)
5. Admin can create/edit/expire promo codes

**Technical Notes:**
- Use Stripe Coupons and Promotion Codes
- Track redemptions in database for analytics
- Support one-time and recurring discounts

---

## 🔧 Functional Requirements

### Payment Processing
1. **Stripe Integration**
   - Stripe Checkout for hosted payment pages
   - Stripe Customer Portal for subscription management
   - Support credit/debit cards, Apple Pay, Google Pay
   - PCI DSS compliant (Stripe handles card data)

2. **Subscription Lifecycle**
   - Create subscription on checkout success
   - Automatic recurring billing (monthly/annual)
   - Proration for mid-cycle upgrades
   - Scheduled downgrades/cancellations
   - Grace period for failed payments (3 days)

3. **Pricing Plans**
   - **Free Tier**: $0/month (existing features)
   - **Basic Tier**: $29/month
   - **Premium Tier**: $99/month
   - **Enterprise Tier**: Custom pricing (contact sales)
   - Annual discounts: 20% off (e.g., $279/year for Basic)

4. **Invoice Management**
   - Auto-generate invoices via Stripe
   - Email invoices to users
   - Store invoice PDFs in user account
   - Support for VAT/tax calculations (Stripe Tax)

### Webhook Handling
5. **Event Processing**
   - `customer.subscription.created` → Update user tier
   - `customer.subscription.updated` → Sync tier changes
   - `customer.subscription.deleted` → Downgrade to free
   - `invoice.payment_succeeded` → Extend subscription
   - `invoice.payment_failed` → Start grace period, send email
   - `charge.refunded` → Handle partial/full refunds

6. **Idempotency & Reliability**
   - Store webhook event IDs to prevent duplicate processing
   - Retry failed webhook processing (3 attempts with backoff)
   - Log all webhook events for auditing

### User Experience
7. **Pricing Page**
   - Clear tier comparison table
   - Feature highlights for each tier
   - CTA buttons for each tier
   - FAQ section addressing common questions

8. **Subscription Dashboard**
   - Current tier and renewal date
   - Payment method on file
   - Billing history (last 12 months)
   - Upgrade/downgrade/cancel buttons
   - Usage statistics (analyses used this month)

### Admin Tools
9. **Subscription Management**
   - View all active subscriptions
   - Manually adjust tiers (with reason logging)
   - Issue refunds
   - Void invoices for support cases

10. **Analytics Dashboard**
    - MRR chart (30-day rolling)
    - Tier distribution pie chart
    - Churn rate graph
    - Failed payment alerts

---

## 🏗️ Non-Functional Requirements

### Security
1. **PCI Compliance**: Never store credit card data (use Stripe tokenization)
2. **Webhook Security**: Verify all webhook signatures before processing
3. **API Key Protection**: Store Stripe keys in environment variables, never commit to repo
4. **Audit Logging**: Log all payment events, tier changes, refunds

### Performance
5. **Webhook Response Time**: Respond to webhooks < 1 second (acknowledge, then process async)
6. **Checkout Load Time**: Pricing page loads < 2 seconds
7. **Subscription Query**: User subscription status query < 100ms

### Reliability
8. **Webhook Retry Logic**: Handle transient failures with exponential backoff
9. **Idempotency**: All payment operations are idempotent (can retry safely)
10. **Stripe API Downtime**: Gracefully handle Stripe outages, queue operations for retry

### Scalability
11. **Concurrent Checkouts**: Support 100 simultaneous checkouts without degradation
12. **Webhook Processing**: Handle 1000+ webhook events/hour

### Compliance
13. **GDPR**: Support data export (billing history) and deletion (anonymize payment records)
14. **SCA (Strong Customer Authentication)**: Support 3D Secure for EU customers via Stripe
15. **Tax Compliance**: Use Stripe Tax for automatic tax calculations

---

## 🎨 User Interface Requirements

### Pricing Page
- **Layout**: 3-column comparison table (Basic, Premium, Enterprise)
- **Visual Hierarchy**: Highlight Premium tier as "Most Popular"
- **Responsive**: Mobile-optimized (stack columns on small screens)
- **Accessibility**: WCAG 2.1 AA compliant

### Checkout Flow
1. User clicks "Subscribe" on pricing page
2. Redirected to Stripe Checkout (hosted page)
3. Enter payment details + billing info
4. Submit payment
5. Redirected back to app with success message
6. Immediate tier upgrade (no manual intervention)

### Subscription Dashboard
- **Current Tier**: Badge with tier name and color
- **Renewal Date**: Countdown timer ("Renews in 23 days")
- **Usage Metrics**: Progress bars for tier limits
- **Quick Actions**: Upgrade, Change Payment, Cancel buttons
- **Billing History**: Table with date, amount, invoice download link

---

## 🧪 Testing Requirements

### Unit Tests
- Stripe webhook signature verification
- Proration calculations
- Subscription state transitions
- Promo code validation

### Integration Tests
- End-to-end checkout flow (using Stripe test mode)
- Webhook event processing
- Subscription upgrade/downgrade scenarios
- Failed payment handling and grace period

### Manual Testing Checklist
- [ ] Complete checkout with test card (4242 4242 4242 4242)
- [ ] Simulate failed payment (4000 0000 0000 0002)
- [ ] Test 3D Secure card (4000 0027 6000 3184)
- [ ] Verify webhook signature validation rejects invalid signatures
- [ ] Confirm tier upgrade is immediate after payment
- [ ] Confirm downgrade is scheduled for period end
- [ ] Test promo code application and discount calculation

---

## 📊 Success Metrics

### Business Metrics
- **Conversion Rate**: % of free users upgrading to paid (target: 5%)
- **MRR Growth**: Month-over-month revenue increase (target: 10%)
- **Churn Rate**: % of users canceling per month (target: <3%)
- **LTV (Lifetime Value)**: Average revenue per customer (target: $500+)

### Technical Metrics
- **Checkout Success Rate**: % of checkouts completed (target: 98%)
- **Webhook Processing Time**: Avg time to process webhook (target: <2s)
- **Payment Failure Rate**: % of failed charges (target: <2%)
- **Support Tickets**: Payment-related tickets per week (target: <5)

---

## 🔗 Dependencies

### External Services
- **Stripe Account**: Production and test mode API keys
- **Email Service**: For receipts and payment failure notifications
- **Task Queue**: Celery + Redis for async webhook processing

### Internal Dependencies
- **Epic 1 Complete**: User authentication and tier system must exist
- **Database Schema**: Add `stripe_customer_id`, `stripe_subscription_id`, `subscription_expires_at` to users table
- **Email Templates**: Receipt, payment failure, subscription renewal emails

---

## 🚀 Implementation Phases

### Phase 1: Stripe Setup & Checkout (Week 1)
- Set up Stripe account and API keys
- Implement Stripe Checkout integration
- Create pricing page UI
- Handle successful payment redirect

### Phase 2: Webhook Processing (Week 1-2)
- Build webhook endpoint with signature verification
- Implement handlers for subscription events
- Add idempotency and retry logic
- Test all webhook scenarios

### Phase 3: Subscription Management (Week 2)
- Build subscription dashboard UI
- Integrate Stripe Customer Portal
- Implement upgrade/downgrade/cancel logic
- Add billing history view

### Phase 4: Admin & Analytics (Week 3)
- Build admin subscription management panel
- Add MRR and churn analytics
- Implement promo code system
- Performance testing and optimization

---

## 🎯 Definition of Done

### Code Complete
- [ ] All user stories implemented and tested
- [ ] Webhook idempotency verified
- [ ] Stripe test mode checkout works end-to-end
- [ ] All edge cases handled (failed payments, refunds, cancellations)

### Testing Complete
- [ ] Unit test coverage ≥ 90% for payment module
- [ ] Integration tests pass with Stripe test mode
- [ ] Manual test checklist completed
- [ ] Security audit for webhook validation

### Documentation Complete
- [ ] Stripe integration guide (setup instructions)
- [ ] Webhook event handling documentation
- [ ] Pricing strategy document
- [ ] Support playbook for payment issues

### Deployment Ready
- [ ] Stripe production keys configured in environment
- [ ] Webhook endpoint registered in Stripe dashboard
- [ ] Payment failure email templates tested
- [ ] Monitoring/alerting configured for failed payments

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Stripe API changes | MEDIUM | Pin Stripe API version, monitor changelog |
| Webhook delivery failures | HIGH | Implement retry logic, manual reconciliation process |
| Payment fraud | HIGH | Use Stripe Radar for fraud detection |
| Failed payment churn | HIGH | Implement grace period, retry logic, dunning emails |
| Tax compliance complexity | MEDIUM | Use Stripe Tax, consult tax professional |
| Refund abuse | MEDIUM | Implement refund policy, manual approval for large refunds |

---

## 📚 Resources

### Stripe Documentation
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Stripe Customer Portal](https://stripe.com/docs/billing/subscriptions/customer-portal)
- [Stripe Testing](https://stripe.com/docs/testing)

### Pricing Research
- Competitor analysis: similar SaaS pricing tiers
- Customer interviews: willingness to pay
- Cost analysis: hosting + API costs per user

---

**Epic Status**: PLANNED  
**Next Step**: Complete Epic 1 (Authentication), then begin Stripe setup  
**Owner**: TBD  
**Last Updated**: 2026-01-08