# Adding Tests to Existing Code: User Authentication Example

Step-by-step guide for adding tests to existing functionality, focusing on what to test and how to mock appropriately.

## The Existing Code

An authentication service that exists without tests:

```typescript
// auth.ts
import { db } from './database';
import { hashPassword, comparePassword } from './crypto';
import { sendEmail } from './email';

interface User {
  id: string;
  email: string;
  passwordHash: string;
  isVerified: boolean;
  failedAttempts: number;
  lockedUntil: Date | null;
}

export class AuthService {
  private readonly MAX_ATTEMPTS = 5;
  private readonly LOCK_DURATION_MS = 15 * 60 * 1000; // 15 minutes

  async login(email: string, password: string): Promise<{ token: string }> {
    const user = await db.users.findByEmail(email);
    if (!user) {
      throw new Error('Invalid credentials');
    }

    if (user.lockedUntil && user.lockedUntil > new Date()) {
      throw new Error('Account locked. Try again later.');
    }

    const isValid = await comparePassword(password, user.passwordHash);
    if (!isValid) {
      await this.recordFailedAttempt(user);
      throw new Error('Invalid credentials');
    }

    if (!user.isVerified) {
      throw new Error('Please verify your email first');
    }

    await db.users.update(user.id, { failedAttempts: 0, lockedUntil: null });
    return { token: this.generateToken(user) };
  }

  private async recordFailedAttempt(user: User): Promise<void> {
    const attempts = user.failedAttempts + 1;
    const updates: Partial<User> = { failedAttempts: attempts };

    if (attempts >= this.MAX_ATTEMPTS) {
      updates.lockedUntil = new Date(Date.now() + this.LOCK_DURATION_MS);
      await sendEmail(user.email, 'Account locked due to too many failed attempts');
    }

    await db.users.update(user.id, updates);
  }

  private generateToken(user: User): string {
    return Buffer.from(JSON.stringify({ id: user.id, email: user.email })).toString('base64');
  }
}
```

## Step 1: Identify What to Test

Analyze the code for testable behaviors:

| Behavior                           | Test Priority | Reason                               |
|------------------------------------|---------------|--------------------------------------|
| User not found → error             | High          | Security - don't leak user existence |
| Wrong password → error             | High          | Core auth functionality              |
| Account locked → error             | High          | Security feature                     |
| Unverified user → error            | Medium        | Business rule                        |
| Successful login → token           | High          | Happy path                           |
| Failed attempts tracking           | High          | Security feature                     |
| Account locking after max attempts | High          | Security feature                     |
| Lock duration                      | Medium        | Verify timing                        |

**Skip testing:**

- `generateToken` internals (private, tested via login)
- Database query mechanics (external dependency)
- Email sending mechanics (external dependency)

## Step 2: Set Up Test Infrastructure

Create test file with mocks at system boundaries:

```typescript
// auth.test.ts
import { AuthService } from './auth';

// Mock external dependencies
jest.mock('./database', () => ({
  db: {
    users: {
      findByEmail: jest.fn(),
      update: jest.fn()
    }
  }
}));

jest.mock('./crypto', () => ({
  hashPassword: jest.fn(),
  comparePassword: jest.fn()
}));

jest.mock('./email', () => ({
  sendEmail: jest.fn()
}));

import { db } from './database';
import { comparePassword } from './crypto';
import { sendEmail } from './email';

const mockDb = db as jest.Mocked<typeof db>;
const mockComparePassword = comparePassword as jest.Mock;
const mockSendEmail = sendEmail as jest.Mock;
```

## Step 3: Create Test Fixtures

```typescript
// Test data factory
function createUser(overrides: Partial<User> = {}): User {
  return {
    id: 'user-123',
    email: 'test@example.com',
    passwordHash: 'hashed-password',
    isVerified: true,
    failedAttempts: 0,
    lockedUntil: null,
    ...overrides
  };
}
```

## Step 4: Write Tests by Behavior

### Test: User Not Found

```typescript
describe('AuthService.login', () => {
  let authService: AuthService;

  beforeEach(() => {
    authService = new AuthService();
    jest.clearAllMocks();
  });

  describe('when user does not exist', () => {
    it('throws generic credentials error', async () => {
      mockDb.users.findByEmail.mockResolvedValue(null);

      await expect(authService.login('unknown@test.com', 'password'))
        .rejects.toThrow('Invalid credentials');
    });

    it('does not reveal that user does not exist', async () => {
      // Same error as wrong password - security requirement
      mockDb.users.findByEmail.mockResolvedValue(null);

      await expect(authService.login('unknown@test.com', 'password'))
        .rejects.toThrow('Invalid credentials');
      // NOT "User not found" - that would leak information
    });
  });
```

### Test: Wrong Password

```typescript
  describe('when password is incorrect', () => {
    it('throws credentials error', async () => {
      mockDb.users.findByEmail.mockResolvedValue(createUser());
      mockComparePassword.mockResolvedValue(false);

      await expect(authService.login('test@example.com', 'wrong'))
        .rejects.toThrow('Invalid credentials');
    });

    it('increments failed attempts', async () => {
      const user = createUser({ failedAttempts: 2 });
      mockDb.users.findByEmail.mockResolvedValue(user);
      mockComparePassword.mockResolvedValue(false);

      try {
        await authService.login('test@example.com', 'wrong');
      } catch {}

      expect(mockDb.users.update).toHaveBeenCalledWith(
        user.id,
        expect.objectContaining({ failedAttempts: 3 })
      );
    });
  });
```

### Test: Account Locking

```typescript
  describe('account locking', () => {
    it('locks account after 5 failed attempts', async () => {
      const user = createUser({ failedAttempts: 4 }); // One more triggers lock
      mockDb.users.findByEmail.mockResolvedValue(user);
      mockComparePassword.mockResolvedValue(false);

      try {
        await authService.login('test@example.com', 'wrong');
      } catch {}

      expect(mockDb.users.update).toHaveBeenCalledWith(
        user.id,
        expect.objectContaining({
          failedAttempts: 5,
          lockedUntil: expect.any(Date)
        })
      );
    });

    it('sends notification email when account is locked', async () => {
      const user = createUser({ failedAttempts: 4 });
      mockDb.users.findByEmail.mockResolvedValue(user);
      mockComparePassword.mockResolvedValue(false);

      try {
        await authService.login('test@example.com', 'wrong');
      } catch {}

      expect(mockSendEmail).toHaveBeenCalledWith(
        user.email,
        expect.stringContaining('locked')
      );
    });

    it('rejects login when account is locked', async () => {
      const lockedUser = createUser({
        lockedUntil: new Date(Date.now() + 60000) // Locked for 1 more minute
      });
      mockDb.users.findByEmail.mockResolvedValue(lockedUser);

      await expect(authService.login('test@example.com', 'password'))
        .rejects.toThrow('Account locked');

      // Password should NOT be checked when account is locked
      expect(mockComparePassword).not.toHaveBeenCalled();
    });

    it('allows login after lock expires', async () => {
      const expiredLockUser = createUser({
        lockedUntil: new Date(Date.now() - 1000), // Lock expired
        failedAttempts: 5
      });
      mockDb.users.findByEmail.mockResolvedValue(expiredLockUser);
      mockComparePassword.mockResolvedValue(true);

      const result = await authService.login('test@example.com', 'correct');

      expect(result.token).toBeDefined();
    });
  });
```

### Test: Unverified User

```typescript
  describe('when user is not verified', () => {
    it('rejects login with verification message', async () => {
      const unverifiedUser = createUser({ isVerified: false });
      mockDb.users.findByEmail.mockResolvedValue(unverifiedUser);
      mockComparePassword.mockResolvedValue(true);

      await expect(authService.login('test@example.com', 'correct'))
        .rejects.toThrow('verify your email');
    });
  });
```

### Test: Successful Login

```typescript
  describe('successful login', () => {
    it('returns token for valid credentials', async () => {
      mockDb.users.findByEmail.mockResolvedValue(createUser());
      mockComparePassword.mockResolvedValue(true);

      const result = await authService.login('test@example.com', 'correct');

      expect(result.token).toBeDefined();
      expect(typeof result.token).toBe('string');
    });

    it('resets failed attempts on successful login', async () => {
      const userWithAttempts = createUser({ failedAttempts: 3 });
      mockDb.users.findByEmail.mockResolvedValue(userWithAttempts);
      mockComparePassword.mockResolvedValue(true);

      await authService.login('test@example.com', 'correct');

      expect(mockDb.users.update).toHaveBeenCalledWith(
        userWithAttempts.id,
        expect.objectContaining({ failedAttempts: 0, lockedUntil: null })
      );
    });

    it('includes user id and email in token', async () => {
      const user = createUser();
      mockDb.users.findByEmail.mockResolvedValue(user);
      mockComparePassword.mockResolvedValue(true);

      const result = await authService.login('test@example.com', 'correct');
      const decoded = JSON.parse(Buffer.from(result.token, 'base64').toString());

      expect(decoded.id).toBe(user.id);
      expect(decoded.email).toBe(user.email);
    });
  });
});
```

## Step 5: Verify Test Quality

Final test file structure:

```
auth.test.ts
├── AuthService.login
│   ├── when user does not exist (2 tests)
│   ├── when password is incorrect (2 tests)
│   ├── account locking (4 tests)
│   ├── when user is not verified (1 test)
│   └── successful login (3 tests)
```

**Coverage achieved:**

- All error paths tested
- Security behaviors verified (no info leakage, locking)
- Happy path with token validation
- State changes (failed attempts, resets) verified

**What we mocked:**

- Database (external, stateful)
- Password comparison (external crypto)
- Email sending (external service)

**What we tested with real code:**

- Business logic (attempt counting, lock thresholds)
- Token generation
- Error messages
- State transitions

## Key Takeaways

1. **Mock at boundaries** - Database, HTTP, email, file system
2. **Test behavior, not implementation** - Focus on what happens, not how
3. **Group tests by scenario** - Makes it clear what's being tested
4. **Use descriptive test names** - Self-documenting tests
5. **Test error paths** - Often where bugs hide
6. **Verify security invariants** - Information leakage, timing attacks
7. **Reset mocks between tests** - Ensure test independence
