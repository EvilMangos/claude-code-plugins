---
name: web-api-security
description: This skill should be used when the user asks to "secure my API", "prevent XSS", "SQL injection prevention", "fix CORS issues", "CSRF protection", "secure authentication", "input validation security", "OWASP vulnerabilities", "web security best practices", "security review", "check for vulnerabilities", "harden my web app", "implement JWT", "set up token refresh", "add rate limiting", "implement OAuth", or needs guidance on preventing common web application security flaws.
version: 0.1.0
---

# Web & API Security

Concise checklists for preventing common web application vulnerabilities. Focus on the OWASP Top 10 and practical secure
coding patterns.

## Quick Security Review Checklist

Before deploying any web application or API, verify these critical items:

- [ ] All user input is validated and sanitized
- [ ] Parameterized queries used for all database operations
- [ ] Output encoding applied before rendering user data
- [ ] Authentication uses secure session management
- [ ] Authorization checks on every protected endpoint
- [ ] HTTPS enforced with secure headers configured
- [ ] Sensitive data encrypted at rest and in transit
- [ ] Error messages don't leak implementation details

## Injection Prevention

### SQL Injection

**Prevention checklist:**

- [ ] Use parameterized queries or prepared statements exclusively
- [ ] Never concatenate user input into SQL strings
- [ ] Apply least-privilege database permissions
- [ ] Validate input types (expect integer? reject strings)

**Vulnerable pattern:**

```
query = "SELECT * FROM users WHERE id = " + userId
```

**Secure pattern:**

```
query = "SELECT * FROM users WHERE id = ?"
execute(query, [userId])
```

### NoSQL Injection

**Prevention checklist:**

- [ ] Validate input types strictly (string vs object)
- [ ] Reject unexpected operators in query objects
- [ ] Sanitize keys, not just values
- [ ] Use typed query builders where available

### Command Injection

**Prevention checklist:**

- [ ] Avoid shell execution with user input entirely
- [ ] Use language-native APIs instead of shell commands
- [ ] If shell required: whitelist allowed values, never sanitize
- [ ] Never pass user input to `eval()`, `exec()`, or similar

### XSS (Cross-Site Scripting)

**Prevention checklist:**

- [ ] Encode all output based on context (HTML, JS, URL, CSS)
- [ ] Use framework's built-in escaping (don't disable it)
- [ ] Implement Content-Security-Policy header
- [ ] Sanitize HTML if rich text absolutely required
- [ ] Use `HttpOnly` and `Secure` flags on cookies

**Context-specific encoding:**
| Context | Encoding Required |
|---------|-------------------|
| HTML body | HTML entity encoding |
| HTML attribute | Attribute encoding + quotes |
| JavaScript | JavaScript encoding |
| URL parameter | URL encoding |
| CSS | CSS encoding |

## Authentication Security

### Password Handling

**Checklist:**

- [ ] Hash passwords with bcrypt, scrypt, or Argon2
- [ ] Never store plaintext or reversibly encrypted passwords
- [ ] Enforce minimum password complexity
- [ ] Implement account lockout after failed attempts
- [ ] Use constant-time comparison for password verification

### Session Management

**Checklist:**

- [ ] Generate cryptographically random session IDs (min 128 bits)
- [ ] Regenerate session ID after authentication
- [ ] Set appropriate session timeout
- [ ] Invalidate sessions on logout (server-side)
- [ ] Store sessions server-side, not in cookies

### Token Security (JWT/API Keys)

**Checklist:**

- [ ] Use strong signing algorithms (RS256 or ES256, not HS256 with weak secret)
- [ ] Set reasonable expiration times
- [ ] Validate all claims (issuer, audience, expiration)
- [ ] Store refresh tokens securely
- [ ] Implement token revocation mechanism

## Authorization

### Access Control Checklist

- [ ] Enforce authorization on every request (not just UI)
- [ ] Default deny: explicitly grant access, never implicitly
- [ ] Validate user owns/can access requested resource
- [ ] Check permissions server-side, never trust client
- [ ] Log authorization failures for monitoring

### IDOR Prevention (Insecure Direct Object Reference)

- [ ] Use indirect references (UUIDs) instead of sequential IDs
- [ ] Verify user authorization for every resource access
- [ ] Don't expose internal IDs in URLs/responses unnecessarily

## CSRF Protection

**Checklist:**

- [ ] Use anti-CSRF tokens for state-changing operations
- [ ] Verify `Origin` and `Referer` headers
- [ ] Use `SameSite` cookie attribute (Strict or Lax)
- [ ] Require re-authentication for sensitive actions

**Implementation pattern:**

1. Generate unique token per session
2. Include token in forms/requests
3. Validate token server-side before processing
4. Reject requests with missing/invalid tokens

## Secure Headers

Configure these HTTP security headers:

| Header                      | Value                                 | Purpose                |
|-----------------------------|---------------------------------------|------------------------|
| `Content-Security-Policy`   | Restrict sources                      | Prevent XSS, injection |
| `X-Content-Type-Options`    | `nosniff`                             | Prevent MIME sniffing  |
| `X-Frame-Options`           | `DENY` or `SAMEORIGIN`                | Prevent clickjacking   |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Force HTTPS            |
| `X-XSS-Protection`          | `1; mode=block`                       | Legacy XSS filter      |
| `Referrer-Policy`           | `strict-origin-when-cross-origin`     | Control referrer info  |

## Input Validation

### Validation Principles

1. **Validate at the boundary**: Check input as soon as it enters the system
2. **Whitelist over blacklist**: Define what's allowed, reject everything else
3. **Validate type, length, format, range**: All four, not just some
4. **Server-side validation is mandatory**: Client-side is UX only

### Validation Checklist

- [ ] Validate all input (query params, body, headers, cookies)
- [ ] Check expected data types
- [ ] Enforce maximum lengths
- [ ] Validate against expected patterns (email, phone, etc.)
- [ ] Reject unexpected fields in structured data
- [ ] Decode input only once (prevent double-encoding attacks)

## Error Handling

### Secure Error Response Checklist

- [ ] Return generic error messages to users
- [ ] Log detailed errors server-side only
- [ ] Never expose stack traces in production
- [ ] Don't reveal database structure or queries
- [ ] Use consistent error format (don't leak info via timing)

## API-Specific Security

### Rate Limiting

- [ ] Implement rate limiting on all endpoints
- [ ] Stricter limits on authentication endpoints
- [ ] Return `429 Too Many Requests` with `Retry-After`
- [ ] Consider per-user and per-IP limits

### API Versioning & Deprecation

- [ ] Maintain security patches for all supported versions
- [ ] Communicate deprecation timeline clearly
- [ ] Force upgrade path for critical vulnerabilities

## Common Mistakes

Avoid these frequent security anti-patterns:

- **Relying on client-side validation alone** - Attackers bypass JavaScript; always validate server-side
- **Using blacklists instead of whitelists** - Blacklists miss novel attacks; define what's allowed, reject everything else
- **Storing secrets in code or environment variables without encryption** - Use secret managers (Vault, AWS Secrets Manager)
- **Disabling CORS or using `Access-Control-Allow-Origin: *`** - Opens your API to cross-origin attacks; whitelist specific origins
- **Rolling your own crypto or auth** - Use battle-tested libraries (bcrypt, passport, established JWT libraries)

## Additional Resources

For detailed patterns and examples, consult:

- **`references/owasp-top-10.md`** - Complete OWASP Top 10 breakdown with examples
- **`references/injection-patterns.md`** - Deep dive into injection attack vectors and prevention
- **`examples/secure-vs-vulnerable.md`** - Side-by-side vulnerable vs secure code patterns

### Related Skills

When reviewing code for security issues, also consider:

- **code-review-checklist** - General code review with security section
- **test-best-practices** - Testing security-critical code paths
