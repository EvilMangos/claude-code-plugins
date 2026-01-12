---
name: backend-performance
description: This skill should be used when the user asks to "optimize my API", "improve database performance", "fix slow queries", "reduce response time", "add caching", "fix memory leak", "profile my backend", "N+1 query problem", "connection pooling", "optimize server performance", or needs guidance on backend performance optimization, database tuning, caching strategies, and server-side efficiency.
version: 0.1.0
---

# Backend Performance Optimization

Principles and checklists for identifying and resolving backend performance bottlenecks. Focus on database optimization,
caching, API efficiency, and resource management.

## Performance Investigation Checklist

Before optimizing, identify the actual bottleneck:

- [ ] Profile to identify slow operations (don't guess)
- [ ] Measure baseline performance metrics
- [ ] Check database query execution times
- [ ] Review API response times by endpoint
- [ ] Monitor memory usage patterns
- [ ] Examine CPU utilization under load
- [ ] Check network latency to external services

## Database Optimization

### Query Performance Checklist

- [ ] Add indexes for columns in WHERE, JOIN, ORDER BY clauses
- [ ] Avoid SELECT * - fetch only needed columns
- [ ] Use EXPLAIN/ANALYZE to understand query plans
- [ ] Eliminate N+1 queries with eager loading or JOINs
- [ ] Paginate large result sets
- [ ] Avoid functions on indexed columns in WHERE clauses
- [ ] Use prepared statements for repeated queries

### N+1 Query Problem

**Symptom:** Loop executes one query per item instead of batch query.

**Detection checklist:**

- [ ] Review ORM-generated queries in logs
- [ ] Look for loops that trigger database calls
- [ ] Check for lazy-loaded relationships accessed in loops
- [ ] Profile total query count vs expected

**Resolution:**

- Use eager loading (include/preload associations)
- Batch queries with IN clauses
- Use JOINs instead of separate queries
- Implement DataLoader pattern for GraphQL

### Indexing Strategy

| Index Type       | Use Case                            |
|------------------|-------------------------------------|
| B-tree (default) | Equality, range queries, sorting    |
| Hash             | Exact equality only                 |
| Composite        | Multi-column WHERE/ORDER BY         |
| Partial          | Queries filtering specific subset   |
| Covering         | Query satisfied entirely from index |

**Indexing checklist:**

- [ ] Index foreign keys used in JOINs
- [ ] Create composite indexes for common query patterns
- [ ] Order composite index columns by selectivity (highest first)
- [ ] Remove unused indexes (they slow writes)
- [ ] Consider partial indexes for filtered queries

### Connection Pooling

- [ ] Configure appropriate pool size (typically 10-20 per instance)
- [ ] Set connection timeout to prevent waiting indefinitely
- [ ] Implement connection health checks
- [ ] Monitor pool exhaustion metrics
- [ ] Release connections promptly after use

**Pool sizing guideline:**

```
connections = (core_count * 2) + effective_spindle_count
```

For most web apps: start with 10-20 connections, tune based on monitoring.

## Caching Strategies

### Cache Decision Checklist

Before caching, verify:

- [ ] Data is read more often than written
- [ ] Stale data is acceptable for some period
- [ ] Cache hit rate will be high enough to justify complexity
- [ ] Invalidation strategy is clear

### Cache Layers

| Layer               | Latency  | Use Case                              |
|---------------------|----------|---------------------------------------|
| In-memory (local)   | ~1ms     | Frequently accessed, small datasets   |
| Distributed (Redis) | ~5-10ms  | Shared state, sessions, rate limiting |
| CDN                 | ~20-50ms | Static assets, API responses          |
| Database cache      | ~10-50ms | Query results, computed values        |

### Caching Patterns

**Cache-aside (Lazy loading):**

1. Check cache for data
2. On miss: fetch from source, populate cache
3. Return data

**Write-through:**

1. Write to cache and database together
2. Ensures consistency, higher write latency

**Write-behind:**

1. Write to cache immediately
2. Async write to database
3. Better write performance, risk of data loss

### Cache Invalidation Checklist

- [ ] Define TTL appropriate for data freshness requirements
- [ ] Implement explicit invalidation on data mutations
- [ ] Use cache tags/keys that enable targeted invalidation
- [ ] Handle cache stampede (use locks or probabilistic early expiration)
- [ ] Monitor cache hit rates and adjust TTLs

## API Performance

### Response Time Optimization

- [ ] Return minimal response payload (no unused fields)
- [ ] Use pagination for list endpoints
- [ ] Implement cursor-based pagination for large datasets
- [ ] Compress responses (gzip/brotli)
- [ ] Use appropriate HTTP caching headers
- [ ] Consider async processing for long operations

### Payload Optimization

- [ ] Remove null/empty fields from responses
- [ ] Use efficient serialization (JSON is fine for most cases)
- [ ] Avoid deeply nested structures
- [ ] Implement field selection (sparse fieldsets)
- [ ] Use appropriate data types (don't send numbers as strings)

### Async Processing

Move these operations out of request/response cycle:

- Email/notification sending
- File processing
- Report generation
- Third-party API calls (when possible)
- Audit logging (non-critical)

**Implementation options:**

- Message queues (RabbitMQ, SQS, Redis)
- Background job processors
- Event-driven architectures

## Memory Management

### Memory Leak Detection Checklist

- [ ] Monitor memory usage over time (should stabilize)
- [ ] Profile heap allocations during load testing
- [ ] Check for growing collections (caches, event listeners)
- [ ] Review closure scopes capturing large objects
- [ ] Verify streams and connections are properly closed

### Memory Optimization

- [ ] Stream large files instead of loading into memory
- [ ] Use pagination for large database result sets
- [ ] Implement bounded caches with eviction policies
- [ ] Pool reusable objects (buffers, connections)
- [ ] Avoid unnecessary object creation in hot paths

## Concurrency & Throughput

### Async Patterns Checklist

- [ ] Use async I/O for database, file, network operations
- [ ] Parallelize independent operations
- [ ] Avoid blocking the event loop (Node.js) or main thread
- [ ] Configure appropriate worker/thread pool sizes
- [ ] Implement backpressure for stream processing

### Rate Limiting & Throttling

- [ ] Implement rate limiting to prevent overload
- [ ] Use circuit breakers for external service calls
- [ ] Configure request timeouts
- [ ] Implement retry with exponential backoff
- [ ] Add bulkhead pattern to isolate failures

## Monitoring & Profiling

### Key Metrics to Track

| Metric              | Target    | Action Trigger |
|---------------------|-----------|----------------|
| P95 response time   | <200ms    | >500ms         |
| P99 response time   | <500ms    | >1s            |
| Error rate          | <0.1%     | >1%            |
| Database query time | <50ms avg | >100ms         |
| Cache hit rate      | >80%      | <60%           |
| Memory usage        | Stable    | Growing trend  |

### Profiling Approach

1. **Start with high-level metrics** - Identify slow endpoints
2. **Drill into database** - Check query times, count
3. **Profile application code** - Find CPU-intensive operations
4. **Examine external calls** - Identify slow third-party APIs
5. **Review memory allocation** - Check for leaks, excessive GC

## Quick Wins Checklist

Common optimizations with high impact:

- [ ] Add database indexes for slow queries
- [ ] Fix N+1 queries with eager loading
- [ ] Enable response compression
- [ ] Add caching for expensive computations
- [ ] Configure connection pooling
- [ ] Move heavy operations to background jobs
- [ ] Implement pagination for list endpoints
- [ ] Set appropriate HTTP cache headers

## Additional Resources

### Reference Files

For detailed patterns and techniques, consult:

- **`references/database-optimization.md`** - When fixing slow queries: EXPLAIN analysis, indexing strategies, N+1 resolution, connection pooling, and database-specific tuning (PostgreSQL, MySQL)
- **`references/caching-patterns.md`** - When implementing caching: cache-aside, write-through, write-behind patterns, cache hierarchy design, invalidation strategies, and technology selection (Redis, Memcached, CDN)

### Examples

Working examples in `examples/`:

- **`examples/common-bottlenecks.md`** - Before/after patterns for common performance issues

### Related Skills

When addressing performance issues, also consider:

- **algorithm-efficiency** - Code-level and algorithmic optimizations
- **web-api-security** - Security considerations that may impact performance
