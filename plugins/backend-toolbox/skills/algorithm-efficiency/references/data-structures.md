# Data Structure Selection Reference

Comprehensive guide to choosing the right data structure for specific use cases.

## Core Data Structures

### Arrays/Lists

**Characteristics:**

- Contiguous memory (usually)
- O(1) random access by index
- O(n) search, insert, delete (except end)

**Use when:**

- Need index-based access
- Iterating through all elements
- Size is known or grows at end
- Memory locality matters

**Avoid when:**

- Frequent insertions/deletions in middle
- Need fast search by value
- Unknown or highly variable size

### Hash Maps/Dictionaries

**Characteristics:**

- O(1) average for insert, delete, lookup
- O(n) worst case (hash collisions)
- No ordering guarantee
- Extra memory for hash table

**Use when:**

- Need fast key-based lookup
- Counting occurrences
- Caching/memoization
- Removing duplicates

**Avoid when:**

- Need ordered iteration
- Memory is very constrained
- Keys are not hashable

### Sets

**Characteristics:**

- O(1) average membership test
- No duplicates
- No ordering (usually)

**Use when:**

- Testing membership frequently
- Removing duplicates
- Set operations (union, intersection)

**Avoid when:**

- Need to store duplicate values
- Need ordered elements
- Need key-value pairs

### Linked Lists

**Characteristics:**

- O(1) insert/delete at known position
- O(n) access by index
- Extra memory for pointers

**Use when:**

- Frequent insertions/deletions
- Don't need random access
- Implementing queues/stacks

**Avoid when:**

- Need random access
- Memory is constrained
- Need cache-friendly iteration

## Specialized Data Structures

### Stacks (LIFO)

| Operation | Complexity |
|-----------|------------|
| Push      | O(1)       |
| Pop       | O(1)       |
| Peek      | O(1)       |

**Use cases:**

- Function call tracking
- Undo operations
- Expression evaluation
- Depth-first traversal

### Queues (FIFO)

| Operation | Complexity |
|-----------|------------|
| Enqueue   | O(1)       |
| Dequeue   | O(1)       |
| Peek      | O(1)       |

**Use cases:**

- Breadth-first traversal
- Task scheduling
- Buffer management
- Message queues

### Deques (Double-ended)

| Operation        | Complexity |
|------------------|------------|
| Add/remove front | O(1)       |
| Add/remove back  | O(1)       |

**Use cases:**

- Sliding window algorithms
- Work-stealing queues
- Palindrome checking

### Heaps/Priority Queues

| Operation        | Complexity |
|------------------|------------|
| Insert           | O(log n)   |
| Get min/max      | O(1)       |
| Remove min/max   | O(log n)   |
| Build from array | O(n)       |

**Use cases:**

- Top-k elements
- Priority scheduling
- Dijkstra's algorithm
- Merge k sorted lists

### Trees

**Binary Search Tree:**
| Operation | Average | Worst |
|-----------|---------|-------|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |

**Balanced Tree (AVL, Red-Black):**
| Operation | Complexity |
|-----------|------------|
| Search | O(log n) |
| Insert | O(log n) |
| Delete | O(log n) |

**Use cases:**

- Ordered data with dynamic updates
- Range queries
- In-order traversal
- Implementing sorted maps/sets

### Tries

| Operation     | Complexity                |
|---------------|---------------------------|
| Insert        | O(k) where k = key length |
| Search        | O(k)                      |
| Prefix search | O(k + results)            |

**Use cases:**

- Autocomplete
- Spell checking
- IP routing tables
- Dictionary word lookup

### Graphs

**Adjacency List:**

- Space: O(V + E)
- Add edge: O(1)
- Check edge: O(degree)
- Good for sparse graphs

**Adjacency Matrix:**

- Space: O(V²)
- Add edge: O(1)
- Check edge: O(1)
- Good for dense graphs

## Decision Matrix

### By Primary Operation

| Need                 | Data Structure              | Time                      |
|----------------------|-----------------------------|---------------------------|
| Fast key lookup      | Hash map                    | O(1)                      |
| Fast membership test | Hash set                    | O(1)                      |
| Ordered iteration    | Sorted array, tree          | O(n)                      |
| Fast min/max         | Heap                        | O(1) get, O(log n) remove |
| FIFO processing      | Queue                       | O(1)                      |
| LIFO processing      | Stack                       | O(1)                      |
| Range queries        | Balanced tree, segment tree | O(log n)                  |
| Prefix matching      | Trie                        | O(k)                      |

### By Access Pattern

| Pattern                | Best Choice                 |
|------------------------|-----------------------------|
| Sequential access      | Array, linked list          |
| Random access by index | Array                       |
| Random access by key   | Hash map                    |
| Sorted access          | Balanced tree, sorted array |
| Priority access        | Heap                        |

### By Modification Pattern

| Pattern           | Best Choice   |
|-------------------|---------------|
| Append only       | Dynamic array |
| Insert anywhere   | Linked list   |
| Insert + search   | Balanced tree |
| Insert + priority | Heap          |
| Mostly static     | Sorted array  |

## Language-Specific Implementations

### Python

| Concept        | Implementation            |
|----------------|---------------------------|
| Dynamic array  | `list`                    |
| Hash map       | `dict`                    |
| Hash set       | `set`                     |
| Queue          | `collections.deque`       |
| Priority queue | `heapq` module            |
| Ordered dict   | `collections.OrderedDict` |
| Default dict   | `collections.defaultdict` |
| Counter        | `collections.Counter`     |

### JavaScript

| Concept       | Implementation                     |
|---------------|------------------------------------|
| Dynamic array | `Array`                            |
| Hash map      | `Map` or `Object`                  |
| Hash set      | `Set`                              |
| Queue         | `Array` (shift/push) - inefficient |

### Java

| Concept        | Implementation             |
|----------------|----------------------------|
| Dynamic array  | `ArrayList`                |
| Hash map       | `HashMap`                  |
| Hash set       | `HashSet`                  |
| Queue          | `LinkedList`, `ArrayDeque` |
| Priority queue | `PriorityQueue`            |
| Sorted map     | `TreeMap`                  |
| Sorted set     | `TreeSet`                  |

## Composite Patterns

### LRU Cache

Combine hash map + doubly linked list:

- O(1) get
- O(1) put
- O(1) eviction

### Indexed Set

Combine hash set + array:

- O(1) insert/delete
- O(1) random access

### Multi-Map

Map where keys can have multiple values:

- Use: `dict` with `list` values
- Or: `collections.defaultdict(list)`

### Bidirectional Map

Map supporting reverse lookup:

- Maintain two maps: key→value and value→key
- Extra memory, O(1) both directions

## Space Considerations

### Memory Overhead

| Structure   | Overhead per Element  |
|-------------|-----------------------|
| Array       | ~0 (just the element) |
| Linked list | Pointer(s) per node   |
| Hash map    | ~2-3x element size    |
| Tree        | 2-3 pointers per node |
| Trie        | High (many pointers)  |

### When Memory Matters

**Prefer:**

- Arrays over linked lists
- Primitive arrays over object arrays
- Specialized collections (IntArrayList)
- Bit arrays for boolean flags

**Avoid:**

- Deep object hierarchies
- Excessive hash map usage
- String keys when int keys work
