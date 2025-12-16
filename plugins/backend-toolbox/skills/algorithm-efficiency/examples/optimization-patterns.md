# Algorithm Optimization Patterns

Before and after code patterns demonstrating common algorithmic improvements.

## List Membership to Set

### Before: O(n) per lookup

```python
def find_common(list1, list2):
    common = []
    for item in list1:
        if item in list2:  # O(n) each time!
            common.append(item)
    return common
# Total: O(n × m)
```

### After: O(1) per lookup

```python
def find_common(list1, list2):
    set2 = set(list2)  # O(m) one-time cost
    common = []
    for item in list1:
        if item in set2:  # O(1) each time
            common.append(item)
    return common
# Total: O(n + m)
```

---

## Nested Loop Join to Hash Join

### Before: O(n × m)

```python
def match_orders_to_users(orders, users):
    results = []
    for order in orders:
        for user in users:
            if order.user_id == user.id:
                results.append((order, user))
                break
    return results
# O(n × m) - checks every user for every order
```

### After: O(n + m)

```python
def match_orders_to_users(orders, users):
    user_map = {user.id: user for user in users}  # O(m)
    results = []
    for order in orders:  # O(n)
        user = user_map.get(order.user_id)
        if user:
            results.append((order, user))
    return results
# O(n + m) - single pass each
```

---

## Repeated String Concatenation

### Before: O(n²)

```python
def build_string(parts):
    result = ""
    for part in parts:
        result += part  # Creates new string each time
    return result
# For n parts of avg length k: O(n² × k)
```

### After: O(n)

```python
def build_string(parts):
    return "".join(parts)  # Single allocation
# O(n × k) - linear in total characters
```

---

## Finding Min and Max

### Before: Two passes O(2n)

```python
def get_range(numbers):
    minimum = min(numbers)  # O(n)
    maximum = max(numbers)  # O(n)
    return minimum, maximum
# Two passes through data
```

### After: Single pass O(n)

```python
def get_range(numbers):
    if not numbers:
        return None, None
    minimum = maximum = numbers[0]
    for num in numbers[1:]:
        if num < minimum:
            minimum = num
        elif num > maximum:
            maximum = num
    return minimum, maximum
# Single pass through data
```

---

## Sorting for Top-K

### Before: O(n log n)

```python
def top_k(items, k):
    sorted_items = sorted(items, reverse=True)  # O(n log n)
    return sorted_items[:k]
```

### After: O(n log k)

```python
import heapq


def top_k(items, k):
    return heapq.nlargest(k, items)  # O(n log k)
# Uses min-heap of size k
```

---

## Fibonacci: Exponential to Linear

### Before: O(2ⁿ)

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
# Exponential - recomputes same values many times
# fib(40) takes several seconds
```

### After: O(n) with memoization

```python
def fib(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]
# Linear - each value computed once
# fib(40) is instant
```

### Alternative: O(n) iterative

```python
def fib(n):
    if n <= 1:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr
# O(n) time, O(1) space
```

---

## Two Sum Problem

### Before: O(n²)

```python
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return None
# Checks every pair
```

### After: O(n)

```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return None
# Single pass with hash map
```

---

## Removing Duplicates

### Before: O(n²)

```python
def remove_duplicates(items):
    result = []
    for item in items:
        if item not in result:  # O(n) check
            result.append(item)
    return result
# O(n²) - linear search in result list
```

### After: O(n)

```python
def remove_duplicates(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:  # O(1) check
            seen.add(item)
            result.append(item)
    return result
# O(n) - hash set lookup
```

### Alternative: O(n) if order doesn't matter

```python
def remove_duplicates(items):
    return list(set(items))
```

---

## Counting Occurrences

### Before: Multiple passes

```python
def count_all(items):
    unique = set(items)
    counts = {}
    for item in unique:
        counts[item] = items.count(item)  # O(n) each
    return counts
# O(n × unique) - counts each unique item separately
```

### After: Single pass

```python
from collections import Counter


def count_all(items):
    return Counter(items)  # Single pass


# Or manually:
def count_all(items):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts
# O(n) - single pass
```

---

## Binary Search vs Linear Search

### Before: O(n)

```python
def find_in_sorted(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
# Doesn't leverage sorted property
```

### After: O(log n)

```python
def find_in_sorted(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
# Leverages sorted property
```

---

## Sliding Window vs Nested Loop

### Before: O(n × k)

```python
def max_sum_subarray(arr, k):
    max_sum = float('-inf')
    for i in range(len(arr) - k + 1):
        current_sum = sum(arr[i:i + k])  # O(k) each
        max_sum = max(max_sum, current_sum)
    return max_sum
```

### After: O(n)

```python
def max_sum_subarray(arr, k):
    if len(arr) < k:
        return None

    # Initial window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide window
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]  # O(1) update
        max_sum = max(max_sum, window_sum)

    return max_sum
# Reuses previous sum
```

---

## Summary Table

| Pattern                  | Before      | After       | Improvement             |
|--------------------------|-------------|-------------|-------------------------|
| List to set membership   | O(n) lookup | O(1) lookup | n× faster lookups       |
| Nested to hash join      | O(n×m)      | O(n+m)      | Dramatic for large sets |
| String concatenation     | O(n²)       | O(n)        | n× faster               |
| Min + max separately     | O(2n)       | O(n)        | 2× fewer iterations     |
| Sort for top-k           | O(n log n)  | O(n log k)  | Faster when k << n      |
| Recursive fib            | O(2ⁿ)       | O(n)        | Exponentially faster    |
| Two sum nested           | O(n²)       | O(n)        | n× faster               |
| Duplicate removal        | O(n²)       | O(n)        | n× faster               |
| Linear vs binary search  | O(n)        | O(log n)    | Exponentially faster    |
| Nested vs sliding window | O(n×k)      | O(n)        | k× faster               |
