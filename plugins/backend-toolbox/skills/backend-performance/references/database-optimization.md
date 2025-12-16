# Database Optimization Reference

Detailed guidance on database query optimization, indexing strategies, and performance tuning.

## Query Optimization

### Understanding Query Plans

Use EXPLAIN (PostgreSQL) or EXPLAIN ANALYZE to understand query execution:

**Key indicators in query plans:**

- **Seq Scan** - Full table scan, often indicates missing index
- **Index Scan** - Using index, generally efficient
- **Index Only Scan** - Best case, all data from index
- **Nested Loop** - Can be slow for large datasets
- **Hash Join** - Efficient for equality joins
- **Sort** - May indicate missing index for ORDER BY

### Query Anti-Patterns

| Anti-Pattern               | Problem                  | Solution                |
|----------------------------|--------------------------|-------------------------|
| SELECT *                   | Fetches unnecessary data | Specify needed columns  |
| OR in WHERE                | May prevent index usage  | Use UNION or IN         |
| Leading wildcard LIKE      | Cannot use index         | Use full-text search    |
| Function on indexed column | Prevents index usage     | Create functional index |
| Implicit type conversion   | Index may not be used    | Match types explicitly  |
| NOT IN with NULLs          | Unexpected results       | Use NOT EXISTS          |

### Optimizing Common Patterns

**Pagination:**

```
-- Inefficient for large offsets
SELECT * FROM items ORDER BY id LIMIT 10 OFFSET 10000;

-- Better: Cursor-based
SELECT * FROM items WHERE id > :last_id ORDER BY id LIMIT 10;
```

**Counting large tables:**

```
-- Slow: exact count
SELECT COUNT(*) FROM large_table;

-- Fast: approximate count (PostgreSQL)
SELECT reltuples FROM pg_class WHERE relname = 'large_table';
```

**Existence checks:**

```
-- Inefficient
SELECT COUNT(*) FROM users WHERE email = 'x' > 0;

-- Efficient
SELECT EXISTS(SELECT 1 FROM users WHERE email = 'x');
```

## Indexing Deep Dive

### Index Selection Decision Tree

1. **Is the column in WHERE clauses?** → Consider B-tree index
2. **Is it used in JOINs?** → Index foreign keys
3. **Is it in ORDER BY?** → Index may eliminate sort
4. **Is it high cardinality?** → Index more beneficial
5. **Is the table frequently updated?** → Fewer indexes preferred
6. **Is it a partial query pattern?** → Consider partial index

### Composite Index Design

**Column order matters:**

- Place equality columns first
- Place range columns last
- Order by selectivity (most selective first)

**Example:**

```
-- Query pattern
WHERE status = 'active' AND created_at > '2024-01-01' AND user_id = 123

-- Optimal index (assuming user_id is most selective)
CREATE INDEX idx_orders ON orders(user_id, status, created_at);
```

### Partial Indexes

Create indexes for specific subsets of data:

```
-- Index only active users (smaller index, faster updates)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Index only recent orders
CREATE INDEX idx_recent_orders ON orders(created_at) WHERE created_at > '2024-01-01';
```

### Covering Indexes

Include all columns needed by query to avoid table lookup:

```
-- Query
SELECT id, email, name FROM users WHERE email = 'x';

-- Covering index (PostgreSQL)
CREATE INDEX idx_users_email ON users(email) INCLUDE (id, name);
```

## Connection Pool Tuning

### Pool Size Formula

For transactional workloads:

```
pool_size = (core_count * 2) + effective_spindle_count
```

For most web applications:

- Start with 10-20 connections per application instance
- Monitor wait times and adjust
- Total connections across all instances should not exceed database max

### Connection Configuration

| Setting            | Recommended | Purpose                      |
|--------------------|-------------|------------------------------|
| min_connections    | 2-5         | Maintain warm connections    |
| max_connections    | 10-20       | Prevent exhaustion           |
| connection_timeout | 5-10s       | Fail fast on pool exhaustion |
| idle_timeout       | 10-30min    | Release unused connections   |
| max_lifetime       | 30-60min    | Prevent stale connections    |

### Monitoring Pool Health

Track these metrics:

- **Active connections** - Currently in use
- **Idle connections** - Available in pool
- **Waiting requests** - Queue depth
- **Connection wait time** - How long requests wait
- **Connection errors** - Failed acquisitions

## Database-Specific Tuning

### PostgreSQL

**Key configuration parameters:**

- `shared_buffers` - Set to 25% of RAM
- `effective_cache_size` - Set to 50-75% of RAM
- `work_mem` - Memory for sorts/hashes (start with 64MB)
- `maintenance_work_mem` - Memory for VACUUM, CREATE INDEX
- `random_page_cost` - Reduce for SSD (1.1 vs default 4.0)

**Maintenance:**

- Run ANALYZE after bulk inserts
- Regular VACUUM (autovacuum should handle most)
- REINDEX for bloated indexes
- pg_stat_statements for query analysis

### MySQL/MariaDB

**Key configuration:**

- `innodb_buffer_pool_size` - Set to 70-80% of RAM
- `innodb_log_file_size` - Larger for write-heavy workloads
- `innodb_flush_log_at_trx_commit` - 2 for better performance (1 for durability)
- `query_cache_size` - Often best to disable (8.0+ removed it)

### MongoDB

**Key optimizations:**

- Create indexes for query patterns
- Use projection to limit returned fields
- Avoid large documents (16MB limit)
- Shard for horizontal scaling
- Use read preferences for read scaling

## Query Caching

### When to Cache Queries

**Good candidates:**

- Expensive aggregations
- Frequently accessed, rarely changed data
- Complex JOINs across multiple tables
- Read-heavy, write-light tables

**Poor candidates:**

- User-specific data with low reuse
- Rapidly changing data
- Simple indexed lookups (already fast)

### Cache Key Design

Include all query parameters in cache key:

```
cache_key = f"query:{table}:{hash(where_clause)}:{hash(params)}"
```

### Invalidation Strategies

| Strategy      | Pros                        | Cons                    |
|---------------|-----------------------------|-------------------------|
| TTL-based     | Simple, automatic           | May serve stale data    |
| Write-through | Always consistent           | Higher write latency    |
| Event-based   | Precise invalidation        | Complex implementation  |
| Version tags  | Efficient bulk invalidation | Requires schema support |

## Monitoring Queries

### Slow Query Identification

**PostgreSQL:**

```
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 100; -- 100ms

-- Use pg_stat_statements
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

**MySQL:**

```
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.1;
```

### Query Performance Metrics

Track for each slow query:

- Execution time (avg, p95, p99)
- Rows examined vs rows returned
- Index usage
- Lock wait time
- Call frequency
