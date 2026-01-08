# Epic 7: Resilience & Error Handling

**Epic ID**: Epic 7  
**Status**: PLANNED  
**Priority**: P1 (High - Production stability)  
**Dependencies**: Epic 4 (Market Sentiment) implemented  
**Estimated Effort**: 2-3 weeks  
**Business Value**: Prevent cascading failures, improve uptime, better user experience

---

## 📋 Overview

### Problem Statement
The application currently has brittle error handling with single points of failure. External API failures (Finnhub, Alpha Vantage, yfinance) can crash entire analysis workflows. There's no retry logic, circuit breakers, or graceful degradation.

**Current State:**
- API errors crash analysis requests
- No retry logic for transient failures
- No fallback data sources when primary fails
- Unhandled exceptions bubble to users as 500 errors
- No rate limit handling (429 errors)
- No timeout protection

**Desired State:**
- Automatic retry with exponential backoff
- Circuit breakers prevent cascade failures
- Graceful degradation (partial data > no data)
- User-friendly error messages
- Self-healing system that recovers from transient failures
- Comprehensive error tracking and alerting

### Business Impact
- **Uptime**: Target 99.9% uptime (reduce from current ~95%)
- **User Trust**: Graceful failures maintain confidence
- **API Costs**: Circuit breakers prevent wasteful retries against dead services
- **Support**: Reduce error-related support tickets by 70%

---

## 🎯 User Stories

### **US7.1: As the system, I want to retry failed API calls automatically** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 3 days  
**Business Value**: Prevent 80% of transient failures from reaching users

**Acceptance Criteria:**
1. All external API calls (yfinance, Finnhub, Alpha Vantage) retry up to 3 times
2. Exponential backoff: 1s, 2s, 4s delays between retries
3. Only transient errors retry (timeout, 429, 502, 503, 504)
4. Non-retryable errors (400, 401, 404) fail immediately
5. Retry attempts are logged for monitoring
6. Total timeout per API call: 15 seconds max

**Technical Notes:**
- Use `tenacity` library for retry logic
- Implement `@retry` decorator for all data fetcher methods
- Track retry metrics (success after N retries)

**Example:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((Timeout, HTTPError)),
    reraise=True
)
def fetch_stock_data(ticker: str):
    # API call with automatic retry
    pass
```

---

### **US7.2: As the system, I want to use circuit breakers to prevent cascade failures** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 4 days  
**Business Value**: Prevent system-wide outages when one API fails

**Acceptance Criteria:**
1. Circuit breaker monitors each external API independently
2. After 5 consecutive failures, circuit opens (stop calling API)
3. Circuit stays open for 60 seconds (recovery window)
4. After 60 seconds, circuit enters half-open state (try 1 request)
5. If half-open request succeeds, circuit closes (resume normal)
6. If half-open request fails, circuit reopens for another 60 seconds
7. When circuit is open, return cached data or degraded response

**Technical Notes:**
- Use `pybreaker` library
- One circuit breaker per external service (yfinance, Finnhub, Alpha Vantage, CoinGecko)
- Store circuit state in Redis for distributed systems
- Emit metrics on circuit state changes

**Example:**
```python
from pybreaker import CircuitBreaker

yfinance_breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60,
    expected_exception=Exception
)

@yfinance_breaker
def fetch_yfinance_data(ticker):
    # Protected by circuit breaker
    pass
```

---

### **US7.3: As the system, I want to degrade gracefully when APIs fail** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 4 days  
**Business Value**: Provide partial data instead of complete failure

**Acceptance Criteria:**
1. When sentiment data fails, analysis continues with price data only
2. When all data sources fail, return cached data (if available)
3. User is notified which data sources failed (warning banner)
4. Partial results are clearly marked (e.g., "Price data only, sentiment unavailable")
5. System logs degradation events for monitoring
6. Admin dashboard shows services in degraded state

**Degradation Hierarchy:**
1. **Full Data**: All sources successful
2. **Partial Data**: Core price data + some sentiment sources
3. **Cached Data**: Recent cached response (up to 24 hours old)
4. **Minimal Data**: Only yfinance data (always available)
5. **Error State**: All sources failed, return friendly error message

**Technical Notes:**
- Implement fallback chains: Primary → Secondary → Cache → Error
- Use `Optional[DataType]` return types to signal partial data
- Add `data_quality` field to responses: "full", "partial", "cached", "degraded"

---

### **US7.4: As a user, I want clear error messages instead of crashes** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 2 days  
**Business Value**: Improve user experience, reduce support tickets

**Acceptance Criteria:**
1. No 500 errors shown to users (catch all exceptions)
2. Error messages are user-friendly and actionable
3. Technical details logged server-side, not exposed to users
4. Rate limit errors (429) suggest retry timing
5. Network errors suggest checking connection
6. Invalid ticker errors suggest search feature

**User-Facing Error Messages:**
- ❌ **Bad**: "HTTPError: 500 Internal Server Error at line 42"
- ✅ **Good**: "We're having trouble fetching data for AAPL. Please try again in a moment."

**Technical Notes:**
- Global error handler in Flask app
- Map exception types to user-friendly messages
- Include request_id in errors for support lookup

---

### **US7.5: As the system, I want to handle rate limits intelligently** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 3 days  
**Business Value**: Prevent API quota exhaustion, optimize costs

**Acceptance Criteria:**
1. Detect 429 (Too Many Requests) responses from APIs
2. Parse `Retry-After` header and wait before retrying
3. Implement token bucket rate limiting for outgoing requests
4. When approaching quota, switch to fallback data source
5. Admin can view API quota usage in dashboard
6. Alert when quota usage exceeds 80%

**API Quota Limits:**
- **yfinance**: No official limit, rate limit ~2000 req/hour
- **Finnhub**: 60 calls/minute (free tier)
- **Alpha Vantage**: 5 calls/minute (free tier)
- **CoinGecko**: 50 calls/minute (free tier)

**Technical Notes:**
- Use `ratelimit` library for token bucket
- Cache API responses aggressively (1 hour for quotes, 24 hours for company info)
- Implement quota tracking in Redis

---

## 🔧 Functional Requirements

### Retry Logic
1. **Exponential Backoff**: 1s, 2s, 4s, 8s (max 3 retries)
2. **Jitter**: Add random 0-500ms to prevent thundering herd
3. **Timeout**: Each API call times out after 10 seconds
4. **Total Timeout**: Entire multi-source fetch completes in 30 seconds max
5. **Retryable Errors**: Timeout, ConnectionError, 429, 502, 503, 504
6. **Non-Retryable Errors**: 400, 401, 403, 404

### Circuit Breakers
7. **Per-Service Breakers**: Separate circuits for yfinance, Finnhub, Alpha Vantage, CoinGecko
8. **Failure Threshold**: Open after 5 consecutive failures
9. **Recovery Time**: 60 seconds in open state before half-open
10. **Half-Open Behavior**: Single probe request to test recovery
11. **State Persistence**: Store circuit state in Redis (distributed systems)

### Graceful Degradation
12. **Fallback Chain**: Primary API → Secondary API → Cache → Default
13. **Partial Data**: Return what's available, mark missing fields as `null`
14. **Staleness Indicator**: Show data age when using cache ("Data from 2 hours ago")
15. **Quality Metadata**: Include `data_quality` field in all responses

### Error Handling
16. **Global Exception Handler**: Catch all unhandled exceptions
17. **User-Friendly Messages**: Map technical errors to user language
18. **Error Codes**: Assign codes to errors for support lookup
19. **Request Tracking**: Include `request_id` in all responses
20. **Logging**: Log all errors with full context (request, user, params)

### Rate Limiting
21. **Client-Side Rate Limiting**: Respect API provider limits proactively
22. **Token Bucket Algorithm**: Smooth request distribution
23. **Quota Tracking**: Monitor API usage against quotas
24. **Adaptive Fallback**: Switch to secondary source when approaching limit
25. **Admin Dashboard**: Real-time quota usage visibility

---

## 🏗️ Non-Functional Requirements

### Reliability
1. **Fault Tolerance**: System handles any single API failure
2. **Self-Healing**: Automatic recovery from transient failures
3. **Data Consistency**: Cache invalidation prevents stale data >24 hours
4. **Idempotency**: All API wrappers are idempotent (safe to retry)

### Performance
5. **Timeout Budget**: All API calls complete within 10s
6. **Circuit Breaker Overhead**: <1ms per protected call
7. **Retry Efficiency**: 90% of retried requests succeed
8. **Cache Hit Rate**: 60% of requests served from cache

### Observability
9. **Metrics**: Track retry attempts, circuit breaker states, API latencies
10. **Alerts**: Notify on circuit open, quota exhaustion, persistent errors
11. **Dashboards**: Real-time view of system health and degradation
12. **Logs**: Structured logging with correlation IDs

### Scalability
13. **Distributed Circuit Breakers**: State shared via Redis
14. **Rate Limit Coordination**: Distributed rate limiting across instances
15. **Graceful Overload**: Queue excess requests instead of failing

---

## 🧪 Testing Requirements

### Unit Tests
- Retry logic with mocked failures
- Circuit breaker state transitions
- Fallback chain execution
- Rate limit token bucket algorithm

### Integration Tests
- End-to-end retry scenarios (API returns 503, then 200)
- Circuit breaker with real API (using test endpoints)
- Graceful degradation (kill API mid-request)
- Rate limit handling (exhaust quota, verify fallback)

### Chaos Engineering
- **Kill API Test**: Shut down Finnhub, verify yfinance fallback works
- **Latency Test**: Add 10s delay to API, verify timeout protection
- **Rate Limit Test**: Exhaust Alpha Vantage quota, verify switch to yfinance
- **Cascade Failure Test**: Kill all APIs, verify cached data served

### Load Testing
- 100 concurrent users hitting API
- Verify circuit breakers prevent overload
- Confirm retry logic doesn't amplify load

---

## 📊 Success Metrics

### Reliability Metrics
- **Uptime**: 99.9% availability (current: ~95%)
- **Error Rate**: <0.5% of requests result in user-facing errors (current: ~5%)
- **Recovery Time**: 90% of transient failures recover in <5 seconds
- **Cascade Failures**: Zero system-wide outages from single API failure

### Performance Metrics
- **P95 Latency**: <2 seconds for analysis (including retries)
- **Timeout Rate**: <1% of requests timeout
- **Cache Hit Rate**: 60% of requests served from cache
- **Retry Success Rate**: 90% of retried requests succeed

### Cost Metrics
- **API Cost Reduction**: 30% reduction from better caching and rate limiting
- **Support Tickets**: 70% reduction in error-related tickets

---

## 🔗 Dependencies

### Libraries
- `tenacity`: Retry logic with exponential backoff
- `pybreaker`: Circuit breaker implementation
- `redis`: Circuit state and rate limit storage
- `ratelimit`: Token bucket rate limiting

### Infrastructure
- **Redis**: For distributed circuit breaker state
- **Monitoring**: Prometheus + Grafana for metrics
- **Alerting**: PagerDuty/Slack for circuit breaker alerts

---

## 🚀 Implementation Phases

### Phase 1: Retry Logic (Week 1)
- Add `tenacity` to all API calls
- Configure retry parameters (attempts, backoff)
- Add timeout protection (10s per call)
- Test with simulated failures

### Phase 2: Circuit Breakers (Week 1-2)
- Implement circuit breakers for each API
- Add Redis state persistence
- Test state transitions (closed → open → half-open → closed)
- Add monitoring for circuit state changes

### Phase 3: Graceful Degradation (Week 2)
- Build fallback chains for each data type
- Implement cache-based fallback
- Add data quality metadata to responses
- Update UI to show partial data warnings

### Phase 4: Error Handling & Rate Limiting (Week 2-3)
- Global error handler in Flask
- User-friendly error message mapping
- Implement rate limiting with token bucket
- Add quota tracking and alerting

---

## 🎯 Definition of Done

### Code Complete
- [ ] All API calls protected with retry + circuit breaker
- [ ] Fallback chains implemented for all data types
- [ ] Global error handler catches all exceptions
- [ ] Rate limiting enforced on outgoing requests

### Testing Complete
- [ ] Unit tests for retry, circuit breaker, fallback logic
- [ ] Chaos tests (kill APIs, verify recovery)
- [ ] Load tests (100 concurrent users)
- [ ] All error scenarios tested

### Monitoring Complete
- [ ] Metrics dashboards for retries, circuit states, errors
- [ ] Alerts configured for circuit open, quota exhaustion
- [ ] Logging includes request IDs and correlation

### Documentation Complete
- [ ] Error handling guide for developers
- [ ] Troubleshooting playbook for operations
- [ ] User-facing error message catalog

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Overly aggressive retry amplifies load | HIGH | Exponential backoff + jitter, circuit breakers |
| Circuit breakers too sensitive (false opens) | MEDIUM | Tune failure threshold (5 failures), monitor metrics |
| Cache serves stale data | MEDIUM | TTL enforcement (24 hours max), staleness indicators |
| Distributed circuit state consistency | LOW | Use Redis with replication, fallback to local state |
| Rate limiting too restrictive | LOW | Monitor quota usage, adjust limits based on data |

---

## 📚 Resources

### Libraries
- [Tenacity Docs](https://tenacity.readthedocs.io/)
- [PyBreaker Docs](https://pybreaker.readthedocs.io/)
- [Redis Circuit Breaker Pattern](https://redis.io/docs/manual/patterns/distributed-locks/)

### Patterns
- [Retry Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Graceful Degradation](https://en.wikipedia.org/wiki/Fault_tolerance)

---

**Epic Status**: PLANNED  
**Next Step**: Complete Epic 4 (Market Sentiment), then begin retry logic implementation  
**Owner**: TBD  
**Last Updated**: 2026-01-08