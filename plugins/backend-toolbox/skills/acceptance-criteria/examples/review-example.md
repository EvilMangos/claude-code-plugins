# Example: Acceptance Review for User Authentication Feature

## Original Request

> "Add user authentication to the app. Users should be able to sign up with email/password, log in, and log out. Show a welcome message with their name when logged in."

## Acceptance Review

### Acceptance Review Summary

**Request**: User authentication with signup, login, logout, and welcome message with name
**Verdict**: PARTIAL

### Instructions Mapping

| # | Instruction | Status | Implementation | Notes |
|---|-------------|--------|----------------|-------|
| 1 | Sign up with email/password | ✅ Done | `src/auth/signup.ts:15` | Email and password fields present |
| 2 | Log in | ✅ Done | `src/auth/login.ts:22` | Login form and auth flow working |
| 3 | Log out | ✅ Done | `src/auth/logout.ts:8` | Logout button clears session |
| 4 | Welcome message with **name** | ⚠️ Partial | `src/components/Header.tsx:45` | Shows email instead of name |

### Gaps

1. **Welcome message shows email instead of name**
   - **Type**: Incomplete
   - **Requested**: "Show a welcome message with their name"
   - **Implemented**: Shows "Welcome, user@email.com" instead of "Welcome, John"
   - **Impact**: Does not match the request - user asked for name, not email

### Assumptions Made

| Assumption | Basis | Risk if Wrong |
|------------|-------|---------------|
| Name field needed in signup | Request mentions "their name" | Would need to add name field to signup form |

### Open Questions

- [ ] Should the signup form collect the user's name, or should we use a different source?
- [ ] What format should the welcome message use? ("Welcome, John" vs "Hello John!")

### Recommendation

The core authentication flow (signup, login, logout) is complete. However, instruction #4 is only partially met - the welcome message shows email instead of name as requested. To fully satisfy the request:
1. Add a "name" field to the signup form
2. Update the welcome message to display the user's name

**Verdict: PARTIAL** - 3 of 4 instructions fully satisfied, 1 partially satisfied.
