---
name: python
description: This skill should be used when working with Python code. Triggers - "Python", "py", ".py files", or when the codebase uses Python.
version: 0.1.0
---

# Python

## Protocol Inheritance for IDE Support

When implementing a class that conforms to a `Protocol`, **explicitly inherit from the Protocol class** even though Python's structural typing doesn't require it.

```python
from typing import Protocol

class UserRepository(Protocol):
    def get_by_id(self, user_id: str) -> User: ...
    def save(self, user: User) -> None: ...

# GOOD - explicit inheritance gives IDE support
class PostgresUserRepository(UserRepository):
    def get_by_id(self, user_id: str) -> User:
        # IDE autocompletes method signature, warns on missing methods
        ...

# BAD - works at runtime but no IDE assistance
class PostgresUserRepository:
    def get_by_id(self, user_id: str) -> User:
        ...
```

**Benefits of explicit Protocol inheritance:**

- IDE autocomplete for required methods
- Immediate error highlighting if a method is missing or has wrong signature
- Better refactoring support when Protocol changes
- Self-documenting code showing which interface is implemented
