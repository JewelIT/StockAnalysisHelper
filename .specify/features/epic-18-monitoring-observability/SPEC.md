# Epic 18: Monitoring & Observability

**Epic ID**: Epic 18  
**Status**: PLANNED  
**Priority**: P1 (High - Production readiness)  
**Dependencies**: Epic 20 (Production Deployment) architecture decisions  
**Estimated Effort**: 2-3 weeks  
**Business Value**: Proactive issue detection, reduce MTTR, improve reliability

---

## 📋 Overview

### Problem Statement
The application lacks comprehensive monitoring and observability infrastructure. Production issues are discovered by users rather than automated systems. No application performance monitoring (APM), error tracking, or centralized logging.

**Current State:**
- Basic file-based logging only
- No error tracking or aggregation
- No performance metrics
- No alerting for critical failures
- No user behavior analytics
- No infrastructure monitoring

**Desired State:**
- Real-time application performance monitoring (APM)
- Centralized error tracking with stack traces
- Structured logging with correlation IDs
- Custom business metrics (analyses run, tier upgrades)
- Automated alerting for critical issues
- User behavior analytics

### Business Impact
- **Downtime Reduction**: Detect issues before users report (target: 50% reduction in MTTR)
- **User Experience**: Identify performance bottlenecks
- **Revenue**: Monitor payment failures, conversion funnels
- **Support**: Reduce time to diagnose issues from hours to minutes

---

## 🎯 User Stories

### **US18.1: As a developer, I want to track application errors in real-time** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 3 days  
**Business Value**: Proactive error detection, faster debugging

**Acceptance Criteria:**
1. All Python exceptions are captured and sent to error tracking service
2. Errors include full stack trace, request context, and user info
3. Errors are grouped by type and frequency
4. Developers receive Slack notifications for new error types
5. Error dashboard shows error trends (last 24h, 7d, 30d)
6. Can mark errors as resolved and track reoccurrence

**Recommended Tool**: Sentry (SaaS) or self-hosted alternative

**Technical Notes:**
- Integrate Sentry Python SDK
- Capture Flask request context (URL, method, user_id)
- Tag errors by environment (production, staging, development)
- Set release version for error tracking across deployments
- Filter out expected errors (e.g., 404s)

**Example:**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://...@sentry.io/...",
    integrations=[FlaskIntegration()],
    environment="production",
    release="1.2.3",
    traces_sample_rate=0.1,  # 10% of requests for APM
    before_send=filter_expected_errors
)
```

---

### **US18.2: As a developer, I want to monitor application performance (APM)** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 4 days  
**Business Value**: Identify bottlenecks, optimize user experience

**Acceptance Criteria:**
1. Track response times for all API endpoints (P50, P95, P99)
2. Monitor database query performance (slow queries >1s flagged)
3. Track external API latency (yfinance, Finnhub, Alpha Vantage)
4. Monitor memory usage and CPU utilization
5. Identify N+1 query problems
6. Dashboard shows slowest endpoints and transactions

**Recommended Tools**:
- **APM**: Sentry Performance, New Relic, or Datadog APM
- **Database**: SQLAlchemy query logging + slow query analysis

**Technical Notes:**
- Use Sentry performance monitoring (already includes APM)
- Instrument critical code paths with custom spans
- Set performance budgets (e.g., analysis endpoint <2s P95)
- Alert on degradation (>20% increase in P95 latency)

**Example:**
```python
import sentry_sdk

@app.route('/api/analysis/analyze', methods=['POST'])
def analyze():
    with sentry_sdk.start_transaction(op="http", name="POST /api/analysis/analyze"):
        with sentry_sdk.start_span(op="db", description="Fetch stock data"):
            data = fetch_stock_data()
        with sentry_sdk.start_span(op="ai", description="Run sentiment analysis"):
            sentiment = analyze_sentiment(data)
        return jsonify(sentiment)
```

---

### **US18.3: As a developer, I want structured logging with correlation IDs** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 3 days  
**Business Value**: Easier debugging, trace requests across services

**Acceptance Criteria:**
1. All logs are structured JSON (not plain text)
2. Each request has a unique `request_id` included in all logs
3. Logs include timestamp, log level, module, message, context
4. Logs are centralized (Elasticsearch, CloudWatch, or Loki)
5. Can search logs by request_id, user_id, ticker, error_type
6. Log retention: 30 days minimum

**Recommended Tools**:
- **Logging Library**: `python-json-logger` or `structlog`
- **Centralized Logging**: ELK Stack (Elasticsearch + Logstash + Kibana), AWS CloudWatch Logs, or Grafana Loki

**Technical Notes:**
- Generate request_id in Flask middleware
- Attach request_id to Sentry errors and APM traces
- Include user_id (if authenticated) in log context
- Log levels: DEBUG (dev only), INFO, WARNING, ERROR, CRITICAL

**Example:**
```python
import logging
import uuid
from pythonjsonlogger import jsonlogger

# Configure JSON logger
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Flask middleware to add request_id
@app.before_request
def add_request_id():
    g.request_id = str(uuid.uuid4())

# Log with context
logger.info("Stock analysis started", extra={
    "request_id": g.request_id,
    "user_id": session.get('user_id'),
    "ticker": ticker,
    "tier": user.tier
})
```

---

### **US18.4: As a product manager, I want to track business metrics** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 3 days  
**Business Value**: Data-driven decisions, conversion optimization

**Acceptance Criteria:**
1. Track custom events: user_registered, tier_upgraded, analysis_run, chat_started
2. Metrics stored in time-series database (Prometheus, InfluxDB)
3. Grafana dashboards show:
   - Daily active users (DAU)
   - Analyses per day
   - Tier distribution
   - Conversion funnel (free → basic → premium)
   - Payment failures
4. Metrics refreshed every 5 minutes
5. Can create custom alerts on metric thresholds

**Recommended Tools**:
- **Metrics Storage**: Prometheus (pull-based) or InfluxDB (push-based)
- **Dashboards**: Grafana
- **Python Library**: `prometheus_client` or `influxdb-client`

**Technical Notes:**
- Use Prometheus counters for events (analyses_total, registrations_total)
- Use Gauges for current state (active_users, mrr)
- Use Histograms for distributions (analysis_duration_seconds)
- Export metrics via `/metrics` endpoint for Prometheus scraping

**Example:**
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
analyses_total = Counter('analyses_total', 'Total analyses run', ['tier'])
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')
active_subscriptions = Gauge('active_subscriptions', 'Active paid subscriptions')

# Instrument code
@analysis_bp.route('/analyze', methods=['POST'])
@analysis_duration.time()
def analyze():
    # Run analysis
    analyses_total.labels(tier=user.tier).inc()
    return jsonify(result)

# Metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest()
```

---

### **US18.5: As an operations engineer, I want automated alerting** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 2 days  
**Business Value**: Reduce downtime, faster incident response

**Acceptance Criteria:**
1. Alerts sent to Slack channel or PagerDuty
2. Alert on critical errors (error rate >1% of requests)
3. Alert on performance degradation (P95 latency >5s)
4. Alert on infrastructure issues (CPU >80%, memory >90%)
5. Alert on payment failures (>5 failures in 1 hour)
6. Alert on API quota exhaustion (>90% of quota used)
7. Alerts include severity (P0/P1/P2), context, and runbook link

**Recommended Tools**:
- **Alerting**: Grafana Alerts, Prometheus Alertmanager, or PagerDuty
- **Notifications**: Slack, PagerDuty, Email

**Technical Notes:**
- Define alert rules in Prometheus/Grafana
- Use alert severity levels (critical, warning, info)
- Include runbook links in alerts
- Implement on-call rotation (PagerDuty)

**Example Alert Rules:**
```yaml
# Prometheus alerting rules
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "{{ $value }} errors/second in last 5 minutes"
          runbook: "https://docs.example.com/runbooks/high-error-rate"
      
      - alert: SlowAPIResponse
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "API response time degraded"
```

---

## 🔧 Functional Requirements

### Error Tracking
1. **Automatic Capture**: All unhandled exceptions sent to Sentry
2. **Context Enrichment**: Include request URL, user_id, tier, environment
3. **Release Tracking**: Tag errors with deployment version
4. **Issue Grouping**: Group similar errors by stack trace
5. **Notifications**: Slack alerts for new error types

### Application Performance Monitoring (APM)
6. **Transaction Tracking**: Monitor response times for all endpoints
7. **Database Profiling**: Track query execution times
8. **External API Monitoring**: Measure latency to yfinance, Finnhub, etc.
9. **Custom Instrumentation**: Track AI model inference times
10. **Performance Budgets**: Alert when endpoints exceed thresholds

### Logging
11. **Structured Logs**: JSON format with consistent schema
12. **Correlation IDs**: request_id in all logs for tracing
13. **Contextual Data**: Include user_id, tier, ticker in logs
14. **Centralization**: All logs aggregated in single system
15. **Retention**: 30-day retention for production logs

### Business Metrics
16. **User Metrics**: DAU, MAU, registrations, logins
17. **Feature Usage**: Analyses per day, chat sessions, exports
18. **Revenue Metrics**: MRR, churn rate, conversion rate
19. **API Usage**: Requests per endpoint, tier distribution
20. **Payment Metrics**: Successful/failed payments, refunds

### Alerting
21. **Error Alerts**: High error rate, new error types
22. **Performance Alerts**: Slow endpoints, database timeouts
23. **Infrastructure Alerts**: High CPU/memory, disk space
24. **Business Alerts**: Payment failures, unusual drop in DAU
25. **API Alerts**: Quota exhaustion, circuit breaker open

---

## 🏗️ Non-Functional Requirements

### Reliability
1. **Monitoring Uptime**: Monitoring system itself has 99.9% uptime
2. **No Single Point of Failure**: Metrics collection continues if Grafana is down
3. **Backpressure Handling**: Metrics buffered if backend unavailable

### Performance
4. **Low Overhead**: Monitoring adds <5% CPU overhead
5. **Sampling**: APM samples 10% of requests (adjustable)
6. **Async Logging**: Logs written asynchronously to avoid blocking

### Scalability
7. **High Cardinality**: Support 1M+ unique metric combinations
8. **Log Volume**: Handle 10K+ log entries per minute
9. **Retention**: Metrics stored for 90 days, logs for 30 days

### Security
10. **Data Privacy**: Do not log sensitive data (passwords, API keys, credit cards)
11. **Access Control**: Dashboards require authentication
12. **Encryption**: Logs and metrics encrypted in transit (TLS)

---

## 🧪 Testing Requirements

### Unit Tests
- Test metric increment logic
- Verify structured log format
- Test alert condition logic

### Integration Tests
- End-to-end error capture to Sentry
- APM transaction creation and timing
- Log aggregation to centralized system
- Alert trigger and notification delivery

### Load Tests
- Verify monitoring overhead <5% under load
- Confirm metrics collection doesn't degrade performance
- Test log buffering under high volume

---

## 📊 Success Metrics

### Operational Metrics
- **MTTR (Mean Time To Repair)**: <30 minutes (current: hours)
- **MTTD (Mean Time To Detect)**: <5 minutes (current: reactive)
- **Alert Accuracy**: >90% of alerts are actionable (avoid alert fatigue)
- **Uptime**: 99.9% (improved from 95% via proactive monitoring)

### Technical Metrics
- **Monitoring Overhead**: <5% CPU and memory impact
- **Log Search Speed**: <2 seconds to find logs by request_id
- **Dashboard Load Time**: <1 second for Grafana dashboards
- **Alert Latency**: Alerts fired within 1 minute of issue

### Business Metrics
- **Support Efficiency**: 50% reduction in time to diagnose issues
- **User Satisfaction**: Fewer user-reported bugs (proactive detection)
- **Cost Optimization**: Identify and eliminate wasteful API calls

---

## 🔗 Dependencies

### Tools & Services
- **Error Tracking**: Sentry (recommended) or Rollbar
- **APM**: Sentry Performance or New Relic
- **Metrics**: Prometheus + Grafana (self-hosted) or Datadog (SaaS)
- **Logging**: ELK Stack, AWS CloudWatch, or Grafana Loki
- **Alerting**: Grafana Alerts, PagerDuty, or Slack

### Infrastructure
- **Metrics Storage**: Time-series database (Prometheus, InfluxDB)
- **Log Storage**: Elasticsearch or S3 (for long-term retention)
- **Dashboards**: Grafana or Kibana

### Libraries
- **Python**: `sentry-sdk`, `prometheus_client`, `python-json-logger`, `structlog`
- **Flask**: `Flask-Talisman` (for security headers), `Flask-Limiter` (rate limiting metrics)

---

## 🚀 Implementation Phases

### Phase 1: Error Tracking & APM (Week 1)
- Set up Sentry account and configure SDK
- Instrument Flask app with error capture
- Enable APM transaction tracking
- Configure Slack notifications for critical errors

### Phase 2: Structured Logging (Week 1-2)
- Implement JSON logging with request IDs
- Set up centralized log aggregation (ELK or CloudWatch)
- Add contextual data to logs (user_id, tier)
- Create log search dashboards

### Phase 3: Business Metrics (Week 2)
- Instrument code with Prometheus metrics
- Set up Prometheus server and Grafana
- Create Grafana dashboards for business metrics
- Define custom metrics (DAU, MRR, analyses)

### Phase 4: Alerting & Dashboards (Week 2-3)
- Define alert rules for errors, performance, infrastructure
- Configure Slack/PagerDuty integrations
- Create operational dashboards (system health, error rates)
- Write runbooks for common alerts

---

## 🎯 Definition of Done

### Infrastructure Complete
- [ ] Sentry configured for error tracking and APM
- [ ] Prometheus + Grafana deployed for metrics
- [ ] Centralized logging system operational
- [ ] Alerting configured with Slack/PagerDuty

### Instrumentation Complete
- [ ] All exceptions captured by Sentry
- [ ] All endpoints instrumented with APM
- [ ] Structured logging implemented
- [ ] Business metrics tracked (DAU, MRR, analyses)

### Dashboards & Alerts Complete
- [ ] Grafana dashboards for system health, business metrics
- [ ] Alerts configured for errors, performance, infrastructure
- [ ] Runbooks written for critical alerts
- [ ] On-call rotation defined

### Testing & Documentation Complete
- [ ] Monitoring overhead validated <5%
- [ ] Alert accuracy >90% (no false positives)
- [ ] Monitoring setup guide documented
- [ ] Dashboard usage guide created

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Monitoring overhead degrades performance | MEDIUM | Use sampling (10% APM), async logging, test under load |
| Alert fatigue from too many alerts | HIGH | Tune alert thresholds, prioritize critical alerts only |
| Sensitive data logged accidentally | HIGH | Implement log sanitization, code review checklist |
| Third-party service downtime (Sentry) | MEDIUM | Use self-hosted fallback, queue metrics locally |
| High cost of SaaS monitoring tools | MEDIUM | Start with self-hosted (Prometheus + Grafana), migrate to SaaS later |

---

## 📚 Resources

### Documentation
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [Structured Logging Best Practices](https://www.structlog.org/)

### Example Dashboards
- [Flask Monitoring Dashboard](https://github.com/flask-dashboard/Flask-MonitoringDashboard)
- [Prometheus Flask Exporter](https://github.com/rycus86/prometheus_flask_exporter)

---

**Epic Status**: PLANNED  
**Next Step**: Set up Sentry account, begin error tracking implementation  
**Owner**: TBD  
**Last Updated**: 2026-01-08