# Complexity Analysis Reference

Detailed guidance on analyzing time and space complexity of algorithms.

## Big O Notation

### Definition

Big O describes the upper bound of an algorithm's growth rate as input size approaches infinity. It captures the worst-case scenario, ignoring constants and lower-order terms.

### Rules for Analysis

1. **Drop constants:** O(2n) → O(n)
2. **Drop lower-order terms:** O(n² + n) → O(n²)
3. **Consider dominant operations:** Focus on the most expensive operations
4. **Multiply nested operations:** Nested loop = O(outer × inner)
5. **Add sequential operations:** Sequential blocks = O(first + second)

### Common Complexity Classes

| Class | Growth | Example |
|-------|--------|---------|
| O(1) | Constant | Doesn't grow with input |
| O(log n) | Logarithmic | Halves problem each step |
| O(n) | Linear | Proportional to input |
| O(n log n) | Linearithmic | Divide and conquer with linear work |
| O(n²) | Quadratic | Nested iteration over input |
| O(n³) | Cubic | Triple nested iteration |
| O(2ⁿ) | Exponential | Doubles each additional input |
| O(n!) | Factorial | All permutations |

### Practical Size Limits

| Complexity | Max n (1 second) |
|------------|------------------|
| O(n!) | ~10 |
| O(2ⁿ) | ~25 |
| O(n³) | ~500 |
| O(n²) | ~10,000 |
| O(n log n) | ~10,000,000 |
| O(n) | ~100,000,000 |
| O(log n) | Practically unlimited |
| O(1) | Unlimited |

## Analysis Techniques

### Loop Analysis

**Single loop:**
```
for i in range(n):     # O(n)
    operation()        # O(1)
# Total: O(n)
```

**Nested loops:**
```
for i in range(n):         # O(n)
    for j in range(m):     # O(m)
        operation()        # O(1)
# Total: O(n × m)
```

**Loop with varying iterations:**
```
for i in range(n):         # O(n)
    for j in range(i):     # O(i) varies
        operation()
# Total: 0+1+2+...+(n-1) = n(n-1)/2 = O(n²)
```

**Loop with logarithmic iterations:**
```
i = n
while i > 0:               # O(log n)
    operation()
    i = i // 2
# Total: O(log n)
```

### Recursive Analysis

**Linear recursion:**
```
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
# T(n) = T(n-1) + O(1)
# Total: O(n)
```

**Binary recursion:**
```
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
# T(n) = T(n-1) + T(n-2) + O(1)
# Total: O(2ⁿ) - exponential!
```

**Divide and conquer:**
```
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])    # T(n/2)
    right = merge_sort(arr[mid:])   # T(n/2)
    return merge(left, right)       # O(n)
# T(n) = 2T(n/2) + O(n)
# Total: O(n log n)
```

### Master Theorem

For recurrences of form T(n) = aT(n/b) + O(nᵈ):

| Condition | Complexity |
|-----------|------------|
| d > log_b(a) | O(nᵈ) |
| d = log_b(a) | O(nᵈ log n) |
| d < log_b(a) | O(n^(log_b(a))) |

**Examples:**
- Merge sort: T(n) = 2T(n/2) + O(n) → a=2, b=2, d=1 → log₂(2)=1=d → O(n log n)
- Binary search: T(n) = T(n/2) + O(1) → a=1, b=2, d=0 → log₂(1)=0=d → O(log n)

## Amortized Analysis

### Definition

Amortized analysis considers the average performance over a sequence of operations, even if individual operations may be expensive.

### Dynamic Array Example

**Single append:** O(1) typically, O(n) when resize needed

**Amortized analysis:**
- Array doubles when full
- n insertions: cost = 1 + 1 + ... + 1 + (resize costs)
- Resize costs: 1 + 2 + 4 + 8 + ... + n = 2n - 1
- Total for n insertions: n + 2n = 3n
- **Amortized per insertion: O(1)**

### Common Amortized O(1) Operations

| Data Structure | Operation | Worst Case | Amortized |
|----------------|-----------|------------|-----------|
| Dynamic array | Append | O(n) | O(1) |
| Hash table | Insert | O(n) | O(1) |
| Splay tree | Access | O(n) | O(log n) |

## Space Complexity

### Stack Space

Recursive calls use stack space:

```python
def recursive(n):
    if n == 0:
        return
    recursive(n-1)
# Space: O(n) stack frames
```

**Tail recursion (if optimized):**
```python
def tail_recursive(n, acc=0):
    if n == 0:
        return acc
    return tail_recursive(n-1, acc+n)
# Space: O(1) if tail-call optimized (not in Python)
```

### Auxiliary Space vs Total Space

- **Auxiliary space:** Extra space beyond input
- **Total space:** Input + auxiliary

**Example - Merge sort:**
- Input: O(n)
- Auxiliary: O(n) for temporary arrays
- Total: O(n)

**Example - In-place quicksort:**
- Input: O(n)
- Auxiliary: O(log n) for recursion stack
- Total: O(n)

## Hidden Complexity

### String Operations

| Operation | Complexity |
|-----------|------------|
| Concatenation | O(m + n) - creates new string |
| Substring check | O(n × m) naive, O(n + m) with KMP |
| Repeated concat in loop | O(n²) total for n concats |

### Collection Operations

| Operation | List | Dict/Set |
|-----------|------|----------|
| Index access | O(1) | N/A |
| Membership test | O(n) | O(1) avg |
| Insert at end | O(1) amort | O(1) avg |
| Insert at start | O(n) | N/A |
| Delete by value | O(n) | O(1) avg |

### Built-in Functions

| Function | Complexity |
|----------|------------|
| len() | O(1) |
| min(), max() | O(n) |
| sum() | O(n) |
| sorted() | O(n log n) |
| in (list) | O(n) |
| in (set/dict) | O(1) average |

## Analysis Checklist

When analyzing an algorithm:

1. **Identify input size:** What variable(s) represent input size?
2. **Find dominant operations:** What operations grow with input?
3. **Analyze loops:** How many iterations? Nested?
4. **Check recursion:** What's the recurrence relation?
5. **Consider hidden costs:** String ops, collection methods?
6. **Account for space:** Stack frames, auxiliary storage?
7. **Consider best/worst/average:** Are they different?
8. **Check amortized:** Any expensive operations that are rare?

## Common Patterns

### Two Pointers: O(n)
```
left, right = 0, len(arr) - 1
while left < right:
    # process
    left += 1  # or right -= 1
```

### Sliding Window: O(n)
```
for right in range(len(arr)):
    # expand window
    while window_invalid:
        # contract from left
        left += 1
```

### Binary Search: O(log n)
```
while left <= right:
    mid = (left + right) // 2
    if found:
        return mid
    elif go_left:
        right = mid - 1
    else:
        left = mid + 1
```

### Divide and Conquer: O(n log n)
```
def solve(problem):
    if base_case:
        return trivial_solution
    left = solve(left_half)
    right = solve(right_half)
    return combine(left, right)
```
