---
name: algorithm-efficiency
description: >
  This skill should be used when the user asks to "optimize this algorithm", "improve time complexity",
  "reduce space complexity", "this code is slow", "Big O analysis", "choose the right data structure",
  "optimize this loop", "memoization", "reduce memory usage", "why is this function slow", or needs
  guidance on algorithmic efficiency, complexity analysis, data structure selection, and code-level
  performance optimization.
---

# Algorithm & Code Efficiency

Principles and checklists for writing efficient code. Focus on time/space complexity, data structure selection, and common optimization patterns.

## Code Efficiency Review Checklist

Before optimizing, verify the actual bottleneck:

- [ ] Profile to identify slow functions (measure, don't guess)
- [ ] Check if optimization is needed (premature optimization is costly)
- [ ] Understand the input size and growth patterns
- [ ] Consider readability vs performance tradeoffs
- [ ] Document any non-obvious optimizations

## Time Complexity Quick Reference

| Complexity | Name | Example Operations |
|------------|------|-------------------|
| O(1) | Constant | Hash lookup, array index access |
| O(log n) | Logarithmic | Binary search, balanced tree operations |
| O(n) | Linear | Single loop, linear search |
| O(n log n) | Linearithmic | Efficient sorting (merge, quick, heap) |
| O(n²) | Quadratic | Nested loops, bubble sort |
| O(2ⁿ) | Exponential | Recursive fibonacci, subsets |
| O(n!) | Factorial | Permutations, brute force TSP |

### Complexity Analysis Checklist

- [ ] Identify the dominant term (ignore constants, lower-order terms)
- [ ] Consider worst-case, average-case, and best-case
- [ ] Account for hidden loops (string operations, array methods)
- [ ] Check for recursive call complexity
- [ ] Consider amortized complexity for dynamic structures

## Data Structure Selection

### Selection Checklist

- [ ] What operations are most frequent? (lookup, insert, delete, iterate)
- [ ] Is ordering required?
- [ ] Are duplicates allowed?
- [ ] What is the expected data size?
- [ ] Is memory a constraint?

### Data Structure Decision Guide

| Need | Best Choice | Time Complexity |
|------|-------------|-----------------|
| Fast lookup by key | Hash map/dict | O(1) average |
| Fast lookup by value | Hash set | O(1) average |
| Ordered iteration | Sorted array, tree | O(n), O(n) |
| Fast min/max | Heap/priority queue | O(log n) |
| FIFO order | Queue | O(1) |
| LIFO order | Stack | O(1) |
| Range queries | Balanced tree, segment tree | O(log n) |
| Membership testing | Set | O(1) average |
| Frequent insertions | Linked list, dynamic array | O(1) amortized |

### Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Array for frequent lookups | O(n) search | Use hash map O(1) |
| Linear search in loop | O(n²) total | Pre-build lookup map |
| Repeated string concat | O(n²) for n concats | Use string builder |
| Sorting for min/max | O(n log n) | Use single pass O(n) |
| Array shift operations | O(n) per shift | Use queue/deque |

## Loop Optimization

### Loop Efficiency Checklist

- [ ] Move invariant computations outside loops
- [ ] Avoid function calls in loop conditions
- [ ] Use early exit when result is found
- [ ] Prefer single loop over multiple passes
- [ ] Consider loop unrolling for tight loops (rare)

### Common Loop Anti-Patterns

**Unnecessary repeated computation:**
```
# Bad: len() called every iteration
for i in range(len(items)):
    process(items[i])

# Good: cache length or use iterator
for item in items:
    process(item)
```

**Nested loops creating O(n²):**
```
# Bad: O(n*m) lookup in nested loop
for order in orders:
    for user in users:
        if user.id == order.user_id:
            process(order, user)

# Good: O(n+m) with lookup map
user_map = {u.id: u for u in users}
for order in orders:
    user = user_map.get(order.user_id)
    if user:
        process(order, user)
```

**Multiple passes when one suffices:**
```
# Bad: three passes through data
total = sum(values)
count = len(values)
maximum = max(values)

# Good: single pass
total, count, maximum = 0, 0, float('-inf')
for v in values:
    total += v
    count += 1
    maximum = max(maximum, v)
```

## Memoization & Caching

### When to Memoize

- [ ] Function is pure (same input = same output)
- [ ] Function is called repeatedly with same arguments
- [ ] Computation is expensive relative to cache lookup
- [ ] Memory tradeoff is acceptable

### Memoization Patterns

**Simple memoization:**
```python
cache = {}
def expensive_function(n):
    if n in cache:
        return cache[n]
    result = compute(n)
    cache[n] = result
    return result
```

**Recursive with memoization (dynamic programming):**
```python
def fib(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]
```

### Caching Considerations

- [ ] Set appropriate cache size limits
- [ ] Consider cache key design (hashable, unique)
- [ ] Implement eviction policy for bounded memory
- [ ] Be aware of closure-captured cache in recursion

## Space Complexity

### Space Optimization Checklist

- [ ] Avoid storing what can be computed
- [ ] Use generators/iterators for large sequences
- [ ] Consider in-place algorithms when possible
- [ ] Release references to large objects when done
- [ ] Watch for hidden memory in closures

### Space-Time Tradeoffs

| Approach | Space | Time | Use When |
|----------|-------|------|----------|
| Store all | O(n) | O(1) lookup | Memory available, frequent access |
| Compute on demand | O(1) | O(n) compute | Memory constrained, rare access |
| Cache recent | O(k) | O(1) hit, O(n) miss | Hot subset pattern |

## String Operations

### String Efficiency Checklist

- [ ] Use string builder for repeated concatenation
- [ ] Avoid regex when simple string methods suffice
- [ ] Pre-compile frequently used regex patterns
- [ ] Be aware of string immutability costs

### String Anti-Patterns

**Repeated concatenation:**
```
# Bad: O(n²) - creates new string each iteration
result = ""
for s in strings:
    result += s

# Good: O(n) - single join operation
result = "".join(strings)
```

**Unnecessary regex:**
```
# Bad: regex overhead for simple check
if re.match(r'^prefix', text):

# Good: simple string method
if text.startswith('prefix'):
```

## Collection Operations

### Collection Efficiency Checklist

- [ ] Use set for membership testing (O(1) vs O(n))
- [ ] Pre-allocate arrays when size is known
- [ ] Avoid modifying collections while iterating
- [ ] Use appropriate collection for access pattern

### Common Collection Mistakes

**Membership test with list:**
```
# Bad: O(n) per check
if item in large_list:

# Good: O(1) per check
large_set = set(large_list)
if item in large_set:
```

**Growing array without pre-allocation:**
```
# Acceptable: dynamic growth
result = []
for i in range(n):
    result.append(compute(i))

# Better for known size: pre-allocate
result = [None] * n
for i in range(n):
    result[i] = compute(i)

# Best: use comprehension
result = [compute(i) for i in range(n)]
```

## Algorithm Selection

### Sorting

| Algorithm | Average | Worst | Space | Use When |
|-----------|---------|-------|-------|----------|
| Quick sort | O(n log n) | O(n²) | O(log n) | General purpose |
| Merge sort | O(n log n) | O(n log n) | O(n) | Stable sort needed |
| Heap sort | O(n log n) | O(n log n) | O(1) | Memory constrained |
| Counting sort | O(n+k) | O(n+k) | O(k) | Small integer range |
| Built-in sort | O(n log n) | O(n log n) | O(n) | Default choice |

**Sorting checklist:**
- [ ] Use built-in sort unless specific algorithm needed
- [ ] Consider partial sort if only need top-k elements
- [ ] Check if data has properties allowing faster sort
- [ ] Use stable sort when order of equals matters

### Searching

| Algorithm | Time | Requirement |
|-----------|------|-------------|
| Linear search | O(n) | None |
| Binary search | O(log n) | Sorted data |
| Hash lookup | O(1) average | Hash map |
| Tree search | O(log n) | Balanced tree |

## Quick Wins Checklist

High-impact optimizations to check first:

- [ ] Replace list membership with set membership
- [ ] Pre-build lookup maps for nested loop joins
- [ ] Use appropriate data structure for access pattern
- [ ] Eliminate redundant computations in loops
- [ ] Add early exits for search operations
- [ ] Use generators for large sequences
- [ ] Cache expensive pure function results
- [ ] Use string builder for concatenation

## Additional Resources

### Reference Files

For detailed patterns and techniques, consult:
- **`references/complexity-analysis.md`** - Deep dive on Big O analysis, amortized complexity, and analysis techniques
- **`references/data-structures.md`** - Comprehensive guide to data structure selection and implementation tradeoffs

### Examples

Working examples in `examples/`:
- **`examples/optimization-patterns.md`** - Before/after code patterns for common inefficiencies

### Related Skills

When addressing code efficiency, also consider:
- **backend-performance** - Server-side and database performance
- **refactoring-patterns** - Code quality improvements that may impact performance
