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
- Multiple issues found that must be resolved
- Overall clean implementation

### Issues

1. **Missing authorization check** (`src/controllers/userController.ts:45`)
    - **Why:** Any authenticated user can update any other user's profile by changing the ID parameter. This is an IDOR
      vulnerability.
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

3. **Verbose validation** (`src/validators/userValidator.ts:12`)
    - **Why:** Current implementation is verbose and harder to maintain.
    - **Fix:** Use a validation library like `zod` for cleaner validation logic.

4. **Poor variable naming** (`src/controllers/userController.ts:52`)
    - **Why:** The variable name `u` is not descriptive.
    - **Fix:** Rename to `updatedUser`.

5. **Code duplication** (`src/types/user.ts:8`)
    - **Why:** The `User` interface and `UserUpdateDto` share many fields.
    - **Fix:** Use `Pick<User, 'name' | 'email'>` to reduce duplication.

6. **Potential data leak** (`src/controllers/userController.ts:60`)
    - **Why:** Returning the full user object may include password hash.
    - **Fix:** Return a sanitized response without sensitive fields.

### Test Feedback

- Good coverage of validation edge cases
- Missing test for authorization (unauthorized user trying to update another user's profile)
- Consider adding test for concurrent update handling
- `test/userController.test.ts:45` - Test name "should work" could be more descriptive: "should update user name when
  valid input provided"

### Checklist Summary

| Area         | Status   | Notes                        |
|--------------|----------|------------------------------|
| Architecture | Pass     | Clean separation of concerns |
| Readability  | **Fail** | Naming and duplication issues|
| Tests        | **Fail** | Missing auth tests           |
| Security     | **Fail** | IDOR and SQL injection risks |
| Performance  | Pass     | No concerns                  |

---

**Verdict:** Request changes (6 issues to resolve)
