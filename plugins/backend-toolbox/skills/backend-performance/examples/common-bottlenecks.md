# Common Performance Bottlenecks

Before and after patterns for frequent backend performance issues.

## N+1 Query Problem

### Before (Inefficient)

```python
# Fetches each author separately - N+1 queries
def get_posts_with_authors():
    posts = db.query("SELECT * FROM posts LIMIT 100")  # 1 query
    for post in posts:
        # 100 additional queries!
        post.author = db.query("SELECT * FROM users WHERE id = ?", post.author_id)
    return posts
```

**Result:** 101 database queries for 100 posts.

### After (Optimized)

```python
# Batch fetch authors - 2 queries total
def get_posts_with_authors():
    posts = db.query("SELECT * FROM posts LIMIT 100")  # 1 query
    author_ids = [p.author_id for p in posts]
    authors = db.query("SELECT * FROM users WHERE id IN (?)", author_ids)  # 1 query
    author_map = {a.id: a for a in authors}
    for post in posts:
        post.author = author_map.get(post.author_id)
    return posts
```

**Result:** 2 database queries regardless of post count.

---

## Missing Database Index

### Before (Full Table Scan)

```sql
-- Query without index - scans entire table
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- EXPLAIN shows: Seq Scan on orders, cost: 15000
-- Time: 450ms
```

### After (Indexed Query)

```sql
-- Add composite index
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Same query now uses index
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- EXPLAIN shows: Index Scan, cost: 8
-- Time: 2ms
```

---

## Synchronous External Calls

### Before (Blocking)

```python
# Blocks on each external call sequentially
def process_order(order):
    # Each call blocks - total time is sum of all calls
    payment = payment_service.charge(order)  # 200ms
    inventory.reserve(order.items)  # 150ms
    email_service.send_confirmation(order)  # 300ms
    analytics.track("order_placed", order)  # 100ms
    return {"status": "success"}  # Total: 750ms
```

### After (Async + Background Jobs)

```python
# Non-blocking critical path + background jobs
async def process_order(order):
    # Only critical operations in request path
    payment, inventory = await asyncio.gather(
        payment_service.charge(order),  # 200ms
        inventory.reserve(order.items)  # 150ms (parallel)
    )  # Total: 200ms (parallel)

    # Non-critical operations in background
    background_queue.enqueue("send_order_email", order.id)
    background_queue.enqueue("track_analytics", "order_placed", order.id)

    return {"status": "success"}  # Total: ~200ms
```

---

## Uncached Expensive Computation

### Before (Recomputes Every Request)

```python
def get_dashboard_stats(user_id):
    # Expensive aggregation on every request
    stats = db.query("""
        SELECT
            COUNT(*) as total_orders,
            SUM(amount) as total_spent,
            AVG(amount) as avg_order
        FROM orders
        WHERE user_id = ? AND created_at > NOW() - INTERVAL '30 days'
    """, user_id)  # 500ms query
    return stats
```

### After (Cached with Invalidation)

```python
def get_dashboard_stats(user_id):
    cache_key = f"dashboard:stats:{user_id}"

    # Check cache first
    cached = cache.get(cache_key)
    if cached:
        return cached  # <1ms

    # Compute and cache on miss
    stats = db.query("""...""", user_id)  # 500ms
    cache.set(cache_key, stats, ttl=300)  # Cache for 5 minutes
    return stats


# Invalidate on order changes
def on_order_created(order):
    cache.delete(f"dashboard:stats:{order.user_id}")
```

---

## Large Payload Response

### Before (Returning Everything)

```python
def get_products():
    # Returns all fields, no pagination
    products = db.query("SELECT * FROM products")  # 10,000 rows
    return jsonify(products)  # 15MB response, 3 seconds
```

### After (Paginated with Field Selection)

```python
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    fields = request.args.get('fields', 'id,name,price').split(',')

    # Pagination + field selection
    products = db.query(f"""
        SELECT {', '.join(fields)}
        FROM products
        LIMIT ? OFFSET ?
    """, per_page, (page - 1) * per_page)

    return jsonify({
        "data": products,
        "page": page,
        "per_page": per_page,
        "has_more": len(products) == per_page
    })  # 5KB response, 50ms
```

---

## Memory Leak from Unbounded Cache

### Before (Unbounded Growth)

```python
# Cache grows indefinitely - memory leak
_cache = {}


def get_user(user_id):
    if user_id not in _cache:
        _cache[user_id] = db.query("SELECT * FROM users WHERE id = ?", user_id)
    return _cache[user_id]

# After running for days: _cache has millions of entries, OOM crash
```

### After (Bounded LRU Cache)

```python
from functools import lru_cache
from cachetools import TTLCache


# Option 1: LRU with max size
@lru_cache(maxsize=1000)
def get_user(user_id):
    return db.query("SELECT * FROM users WHERE id = ?", user_id)


# Option 2: TTL + max size
_cache = TTLCache(maxsize=1000, ttl=300)


def get_user(user_id):
    if user_id not in _cache:
        _cache[user_id] = db.query("SELECT * FROM users WHERE id = ?", user_id)
    return _cache[user_id]
```

---

## Connection Pool Exhaustion

### Before (New Connection Per Request)

```python
def get_data():
    # Creates new connection every time
    conn = database.connect()  # 50-100ms connection overhead
    try:
        result = conn.query("SELECT * FROM data")
        return result
    finally:
        conn.close()
```

### After (Connection Pooling)

```python
# Initialize pool once at startup
pool = database.create_pool(
    min_size=5,
    max_size=20,
    timeout=10
)


def get_data():
    # Reuses connection from pool
    with pool.connection() as conn:  # <1ms acquisition
        result = conn.query("SELECT * FROM data")
        return result
```

---

## Inefficient Serialization

### Before (Serializing in Loop)

```python
def export_users():
    users = db.query("SELECT * FROM users")  # 50,000 users
    result = []
    for user in users:
        # JSON serialization per user
        result.append(json.dumps(user.to_dict()))
    return "[" + ",".join(result) + "]"  # 30 seconds
```

### After (Streaming Serialization)

```python
def export_users():
    def generate():
        yield "["
        first = True
        for user in db.query_iterator("SELECT * FROM users"):
            if not first:
                yield ","
            yield json.dumps(user.to_dict())
            first = False
        yield "]"

    return Response(generate(), mimetype='application/json')  # Streams immediately
```

---

## Summary

| Bottleneck           | Key Fix                      | Typical Improvement        |
|----------------------|------------------------------|----------------------------|
| N+1 queries          | Batch/eager load             | 10-100x fewer queries      |
| Missing index        | Add appropriate index        | 10-1000x faster queries    |
| Sync external calls  | Async + background jobs      | 2-5x faster response       |
| Uncached computation | Add caching layer            | 100-1000x faster (hits)    |
| Large payloads       | Pagination + field selection | 10-100x smaller response   |
| Memory leak          | Bounded cache with TTL       | Stable memory usage        |
| Connection overhead  | Connection pooling           | 50-100ms saved per request |
| Loop serialization   | Streaming response           | Faster time-to-first-byte  |
