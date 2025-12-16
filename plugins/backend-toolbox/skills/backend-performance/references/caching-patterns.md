# Caching Patterns Reference

Detailed guidance on caching strategies, architecture, and implementation patterns.

## Cache Architecture

### Cache Hierarchy

```
Request → L1 (In-Process) → L2 (Distributed) → L3 (Database/CDN) → Origin
```

| Layer | Type                | Latency  | Capacity     | Use Case                      |
|-------|---------------------|----------|--------------|-------------------------------|
| L1    | In-process memory   | <1ms     | Limited (MB) | Hot data, sessions            |
| L2    | Distributed (Redis) | 1-10ms   | Large (GB)   | Shared state, computed values |
| L3    | CDN/DB cache        | 10-100ms | Very large   | Static assets, query cache    |

### Cache Technology Selection

| Technology    | Best For                              | Considerations                     |
|---------------|---------------------------------------|------------------------------------|
| In-memory map | Single instance, hot data             | Lost on restart                    |
| Redis         | Shared cache, sessions, rate limiting | Network hop, serialization         |
| Memcached     | Simple key-value, high throughput     | No persistence, limited data types |
| CDN           | Static assets, API responses          | Invalidation latency               |
| Database      | Query result cache                    | Database-specific                  |

## Caching Patterns

### Cache-Aside (Lazy Loading)

Most common pattern for application caching.

**Flow:**

1. Application checks cache
2. On hit: return cached data
3. On miss: fetch from source, cache result, return

**Characteristics:**

- Only caches data that's actually used
- First request for data is always slow
- Cache may become stale if source changes

**Implementation checklist:**

- [ ] Handle cache misses gracefully
- [ ] Set appropriate TTL
- [ ] Implement cache stampede protection
- [ ] Log cache hit/miss rates

### Write-Through

Write to cache and database simultaneously.

**Flow:**

1. Application writes to cache
2. Cache synchronously writes to database
3. Return success

**Characteristics:**

- Cache always consistent with database
- Higher write latency
- Simple mental model

**When to use:**

- Data consistency is critical
- Write frequency is moderate
- Can tolerate higher write latency

### Write-Behind (Write-Back)

Write to cache immediately, async write to database.

**Flow:**

1. Application writes to cache
2. Return success immediately
3. Cache asynchronously flushes to database

**Characteristics:**

- Very fast writes
- Risk of data loss on cache failure
- Complex failure handling

**When to use:**

- Write performance is critical
- Some data loss is acceptable
- Have reliable cache infrastructure

### Read-Through

Cache handles fetching from source on miss.

**Flow:**

1. Application requests from cache
2. On miss: cache fetches from source and caches
3. Return data

**Characteristics:**

- Application only talks to cache
- Cache manages source interaction
- Simplifies application code

## Cache Invalidation

### TTL-Based Expiration

Set time-to-live on cached data.

**Choosing TTL:**
| Data Type | Typical TTL | Considerations |
|-----------|-------------|----------------|
| Static content | Hours-days | CDN edge caching |
| Configuration | Minutes-hours | Low change frequency |
| User data | Seconds-minutes | Personalization freshness |
| Real-time data | Seconds | High consistency need |

**Best practices:**

- Add jitter to TTLs (prevent synchronized expiration)
- Use shorter TTLs for uncertain data
- Monitor staleness impact on business

### Explicit Invalidation

Invalidate cache entries when source data changes.

**Strategies:**

- **Single key**: Delete specific entry on update
- **Pattern-based**: Delete all matching keys
- **Tag-based**: Associate entries with tags, invalidate by tag
- **Version-based**: Increment version in key on update

**Implementation:**

```
# Tag-based invalidation
cache.set("user:123", data, tags=["user:123", "users"])
cache.invalidate_tag("user:123")  # Invalidates user-specific
cache.invalidate_tag("users")     # Invalidates all users
```

### Cache Stampede Prevention

Prevent multiple processes from simultaneously rebuilding cache.

**Locking approach:**

1. On cache miss, acquire lock
2. If lock acquired: fetch data, cache it, release lock
3. If lock not acquired: wait and retry cache read

**Probabilistic early expiration:**

- Recompute value before actual expiration
- Add random factor to prevent synchronized refresh
- Useful for high-traffic keys

**Stale-while-revalidate:**

- Return stale data immediately
- Trigger async refresh in background
- Best user experience for non-critical data

## Cache Key Design

### Key Structure

Design keys for:

- Uniqueness (no collisions)
- Readability (debugging)
- Efficient invalidation

**Pattern:**

```
{namespace}:{entity}:{identifier}:{version}

Examples:
api:user:123:v2
product:details:456
search:results:hash(query)
```

### Key Best Practices

- [ ] Include version for breaking changes
- [ ] Use consistent hashing for complex parameters
- [ ] Keep keys reasonably short (memory overhead)
- [ ] Use namespaces to group related data
- [ ] Document key naming conventions

## Distributed Caching

### Redis Configuration

**Memory management:**

- `maxmemory`: Set appropriate limit
- `maxmemory-policy`: Choose eviction policy
    - `allkeys-lru`: Evict least recently used (general purpose)
    - `volatile-lru`: Evict LRU with TTL set
    - `allkeys-lfu`: Evict least frequently used
    - `noeviction`: Return error when full

**Persistence options:**

- `RDB`: Point-in-time snapshots (faster recovery)
- `AOF`: Append-only file (better durability)
- Both: Maximum durability

### Cache Cluster Patterns

**Client-side sharding:**

- Application determines which node to use
- Simple but inflexible

**Proxy-based:**

- Proxy handles routing (e.g., Twemproxy)
- Transparent to application

**Redis Cluster:**

- Native clustering with automatic sharding
- Supports high availability

### High Availability

- [ ] Configure Redis Sentinel or Cluster
- [ ] Implement circuit breaker for cache failures
- [ ] Design application to function without cache
- [ ] Monitor replication lag
- [ ] Test failover procedures

## Caching HTTP Responses

### Cache-Control Headers

| Directive                | Purpose                      |
|--------------------------|------------------------------|
| `max-age=N`              | Cache for N seconds          |
| `s-maxage=N`             | CDN/proxy cache time         |
| `private`                | Only browser can cache       |
| `public`                 | Any cache can store          |
| `no-cache`               | Must revalidate before use   |
| `no-store`               | Don't cache at all           |
| `stale-while-revalidate` | Serve stale while refreshing |

**Example headers:**

```
# Static assets (long cache, versioned URLs)
Cache-Control: public, max-age=31536000, immutable

# API responses (short cache)
Cache-Control: private, max-age=60

# User-specific, sensitive
Cache-Control: private, no-cache
```

### ETags and Conditional Requests

Use ETags for efficient revalidation:

1. Server returns `ETag: "abc123"` with response
2. Client sends `If-None-Match: "abc123"` on next request
3. Server returns `304 Not Modified` if unchanged

## Monitoring and Metrics

### Key Metrics

| Metric          | Target        | Alert Threshold |
|-----------------|---------------|-----------------|
| Hit rate        | >80%          | <60%            |
| Miss rate       | <20%          | >40%            |
| Latency (p95)   | <10ms         | >50ms           |
| Memory usage    | <80% capacity | >90%            |
| Eviction rate   | Low           | Sudden spike    |
| Connection pool | <80% utilized | >95%            |

### Troubleshooting

**Low hit rate:**

- TTL too short
- High data cardinality
- Cache key not matching patterns
- Insufficient cache size

**High latency:**

- Network issues
- Large values (serialize/deserialize)
- Redis command blocking
- Connection pool exhaustion

**Frequent evictions:**

- Insufficient memory
- Wrong eviction policy
- Memory leak (keys not expiring)
