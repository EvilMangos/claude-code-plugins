# Sample Code Review

Example of a well-structured code review following the checklist.

---

## PR: Add user profile update endpoint

**Files changed:** 4
**Lines:** +127, -12

### Summary

- Adds PUT /api/users/:id endpoint for profile updates
- Implements input validation for email and name fields
- Good test coverage for happy path
- Missing authorization check is a blocking issue
- Overall clean implementation with minor suggestions

### Blocking Issues

1. **Missing authorization check** (`src/controllers/userController.ts:45`)
   - **Why:** Any authenticated user can update any other user's profile by changing the ID parameter. This is an IDOR vulnerability.
   - **Fix:** Add check that `req.user.id === params.id` or user has admin role:
     ```typescript
     if (req.user.id !== params.id && !req.user.isAdmin) {
       return res.status(403).json({ error: 'Forbidden' });
     }
     ```

2. **SQL injection risk** (`src/repositories/userRepository.ts:23`)
   - **Why:** The `orderBy` parameter is interpolated directly into the query string.
   - **Fix:** Whitelist allowed column names:
     ```typescript
     const allowedColumns = ['name', 'email', 'createdAt'];
     if (!allowedColumns.includes(orderBy)) {
       throw new Error('Invalid sort column');
     }
     ```

### Non-blocking Suggestions

- **[suggestion]** `src/validators/userValidator.ts:12` - Consider using a validation library like `zod` for cleaner validation logic. Current implementation works but is verbose.

- **[nit]** `src/controllers/userController.ts:52` - The variable name `u` could be more descriptive. Maybe `updatedUser`?

- **[suggestion]** `src/types/user.ts:8` - The `User` interface and `UserUpdateDto` share many fields. Consider using `Pick<User, 'name' | 'email'>` to reduce duplication.

- **[question]** `src/controllers/userController.ts:60` - Is returning the full user object (including password hash) intentional? I'd expect a sanitized response here.

### Test Feedback

- Good coverage of validation edge cases
- Missing test for authorization (unauthorized user trying to update another user's profile)
- Consider adding test for concurrent update handling
- `test/userController.test.ts:45` - Test name "should work" could be more descriptive: "should update user name when valid input provided"

### Checklist Summary

| Area | Status | Notes |
|------|--------|-------|
| Architecture | Pass | Clean separation of concerns |
| Readability | Pass | Clear code structure |
| Tests | Partial | Missing auth tests |
| Security | **Fail** | IDOR and SQL injection risks |
| Performance | Pass | No concerns |

---

**Verdict:** Request changes (2 blocking issues)
