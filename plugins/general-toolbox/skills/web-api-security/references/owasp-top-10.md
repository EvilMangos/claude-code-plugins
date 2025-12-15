# OWASP Top 10 (2021) Detailed Reference

Comprehensive breakdown of each OWASP Top 10 vulnerability with detection patterns and prevention strategies.

## A01:2021 - Broken Access Control

Access control enforces policy such that users cannot act outside their intended permissions.

### Common Weaknesses

1. **Violation of least privilege**: Access granted to anyone rather than specific roles
2. **Bypassing access control**: Modifying URL, application state, or HTML page
3. **IDOR**: Accessing another user's data by changing identifier
4. **Missing function-level access control**: API endpoints without authorization
5. **Metadata manipulation**: Tampering with JWT, cookies, hidden fields

### Detection Checklist

- [ ] Can users access admin pages by changing URL?
- [ ] Can users view/edit other users' data by changing IDs?
- [ ] Are API endpoints accessible without authentication?
- [ ] Does the app rely on client-side access control?
- [ ] Can JWT/tokens be modified without detection?

### Prevention

```
# Every endpoint must verify:
1. Is user authenticated?
2. Does user have required role/permission?
3. Does user own/have access to this specific resource?
```

- Deny by default except for public resources
- Implement access control mechanisms once, reuse throughout
- Log access control failures and alert on anomalies
- Disable directory listing and remove metadata files

---

## A02:2021 - Cryptographic Failures

Failures related to cryptography that expose sensitive data.

### Common Weaknesses

1. **Data transmitted in cleartext**: HTTP, FTP, SMTP without TLS
2. **Weak cryptographic algorithms**: MD5, SHA1, DES, RC4
3. **Default or weak keys**: Hardcoded secrets, insufficient key length
4. **Improper certificate validation**: Disabled verification
5. **Weak password hashing**: Unsalted, fast algorithms (MD5, SHA1)

### Detection Checklist

- [ ] Is any data transmitted over HTTP?
- [ ] Are old/weak crypto algorithms used?
- [ ] Are default crypto keys in use?
- [ ] Is certificate chain validation enforced?
- [ ] Are passwords hashed with bcrypt/scrypt/Argon2?
- [ ] Is sensitive data encrypted at rest?

### Prevention

- Classify data by sensitivity, apply controls accordingly
- Don't store sensitive data unnecessarily
- Encrypt all sensitive data at rest
- Use TLS for all data in transit
- Use authenticated encryption (AES-GCM, ChaCha20-Poly1305)
- Use password-specific hashing (bcrypt, scrypt, Argon2)

---

## A03:2021 - Injection

User-supplied data sent to an interpreter as part of a command or query.

### Types of Injection

| Type | Vector | Example |
|------|--------|---------|
| SQL | Database queries | `' OR '1'='1` |
| NoSQL | Document queries | `{"$gt": ""}` |
| OS Command | Shell execution | `; rm -rf /` |
| LDAP | Directory queries | `*)(uid=*)` |
| XPath | XML queries | `' or '1'='1` |
| ORM | Object queries | Depends on ORM |
| Expression Language | Template engines | `${7*7}` |

### Detection Checklist

- [ ] Is user input concatenated into queries?
- [ ] Are stored procedures used without parameterization?
- [ ] Does dynamic query building use string concatenation?
- [ ] Is input type-checked before use in queries?
- [ ] Are shell commands built with user input?

### Prevention

- Use parameterized queries exclusively
- Use positive server-side input validation
- Escape special characters for specific interpreter
- Use LIMIT to prevent mass disclosure
- Code review all query construction

---

## A04:2021 - Insecure Design

Flaws in design that cannot be fixed by perfect implementation.

### Common Weaknesses

1. **Missing threat modeling**: No security in design phase
2. **Insufficient separation**: No trust boundaries defined
3. **Missing rate limiting**: Resource exhaustion possible
4. **Unvalidated business logic**: Assumptions not enforced

### Detection Checklist

- [ ] Was threat modeling performed?
- [ ] Are trust boundaries clearly defined?
- [ ] Are business rules enforced server-side?
- [ ] Is there rate limiting on critical flows?
- [ ] Are security requirements documented?

### Prevention

- Establish secure development lifecycle
- Use threat modeling for critical flows
- Write security requirements and test against them
- Integrate security at design phase, not as afterthought
- Limit resource consumption per user/request

---

## A05:2021 - Security Misconfiguration

Insecure default configurations, incomplete configurations, open cloud storage, misconfigured HTTP headers, verbose error messages.

### Common Weaknesses

1. **Missing security hardening**: Default configs in production
2. **Unnecessary features enabled**: Debug mode, unused endpoints
3. **Default credentials**: Admin/admin still works
4. **Verbose error handling**: Stack traces to users
5. **Missing security headers**: CSP, HSTS not configured

### Detection Checklist

- [ ] Are default credentials changed?
- [ ] Is debug mode disabled in production?
- [ ] Are unnecessary features/ports disabled?
- [ ] Are security headers configured?
- [ ] Is error handling secure?
- [ ] Are cloud storage permissions correct?

### Prevention

- Automated hardening process
- Minimal platform without unnecessary features
- Regular configuration reviews
- Segmented architecture with separation
- Send security directives via headers

---

## A06:2021 - Vulnerable and Outdated Components

Using components with known vulnerabilities.

### Common Weaknesses

1. **Unknown versions**: Don't know what's in production
2. **Outdated software**: Known CVEs unpatched
3. **Unscanned dependencies**: No vulnerability scanning
4. **Abandoned libraries**: No security maintenance

### Detection Checklist

- [ ] Is there a software inventory?
- [ ] Are dependencies regularly scanned?
- [ ] Is there a patching policy?
- [ ] Are EOL components identified?
- [ ] Are dependency updates automated?

### Prevention

- Maintain inventory of components and versions
- Remove unused dependencies and features
- Continuously monitor for vulnerabilities
- Only obtain components from official sources
- Prefer signed packages

---

## A07:2021 - Identification and Authentication Failures

Weaknesses in confirming user identity and session management.

### Common Weaknesses

1. **Credential stuffing**: No protection against automated attacks
2. **Weak passwords**: No complexity requirements
3. **Broken session management**: Predictable tokens, no timeout
4. **Missing MFA**: Single factor for sensitive operations

### Detection Checklist

- [ ] Is there brute-force protection?
- [ ] Are passwords checked against breach databases?
- [ ] Is session ID regenerated after login?
- [ ] Is MFA available for sensitive accounts?
- [ ] Are sessions properly invalidated on logout?

### Prevention

- Implement rate limiting and account lockout
- Use secure password policy and breach checking
- Require MFA for sensitive operations
- Generate new random session ID on login
- Implement proper session timeout and logout

---

## A08:2021 - Software and Data Integrity Failures

Code and infrastructure lacking integrity verification.

### Common Weaknesses

1. **Untrusted sources**: Using CDNs without integrity checks
2. **Insecure CI/CD**: No integrity verification in pipeline
3. **Auto-updates without verification**: Blind trust in updates
4. **Insecure deserialization**: Accepting untrusted serialized objects

### Detection Checklist

- [ ] Are external resources integrity-checked (SRI)?
- [ ] Is CI/CD pipeline secured?
- [ ] Are updates verified before applying?
- [ ] Is serialized data from untrusted sources rejected?
- [ ] Are code signing and verification in place?

### Prevention

- Use digital signatures to verify integrity
- Ensure CI/CD has proper access controls
- Review code and config changes
- Do not send unsigned/unencrypted serialized data to untrusted clients
- Use SRI for external resources

---

## A09:2021 - Security Logging and Monitoring Failures

Insufficient logging, detection, monitoring, and response.

### Common Weaknesses

1. **Missing audit logs**: No record of sensitive actions
2. **Unclear log messages**: Insufficient detail for forensics
3. **No monitoring**: Logs collected but not analyzed
4. **No alerting**: Attacks not detected in real time

### Detection Checklist

- [ ] Are login/access control failures logged?
- [ ] Are logs in a format suitable for analysis?
- [ ] Is there real-time monitoring and alerting?
- [ ] Is there an incident response plan?
- [ ] Are logs protected from tampering?

### Prevention

- Log all authentication, access control, and input validation failures
- Ensure logs have enough context for analysis
- Use centralized log management
- Establish alerting thresholds
- Create incident response procedures

---

## A10:2021 - Server-Side Request Forgery (SSRF)

Application fetches remote resources without validating user-supplied URLs.

### Common Weaknesses

1. **Unvalidated URL input**: Fetching arbitrary URLs
2. **Bypassed allowlists**: Using redirects or DNS rebinding
3. **Internal network access**: Reaching internal services via SSRF

### Attack Patterns

```
# Access internal services
http://localhost:8080/admin
http://169.254.169.254/metadata  # Cloud metadata

# Bypass allowlist via redirect
http://allowed.com -> redirect to -> http://internal

# DNS rebinding
DNS lookup 1: allowed IP
DNS lookup 2: internal IP
```

### Prevention

- Validate and sanitize all URLs
- Use allowlist of permitted hosts/protocols
- Disable HTTP redirects or validate redirect target
- Block access to internal networks from URL fetchers
- Use network segmentation
