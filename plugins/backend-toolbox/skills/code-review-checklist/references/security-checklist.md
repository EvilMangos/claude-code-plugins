# Security Review Checklist

Detailed security considerations for code review.

## OWASP Top 10 Reference

This checklist covers vulnerabilities from the [OWASP Top 10 (2021)](https://owasp.org/Top10/):

| OWASP ID | Category | Section in This Checklist |
|----------|----------|---------------------------|
| A01:2021 | Broken Access Control | Authentication & Authorization |
| A02:2021 | Cryptographic Failures | Cryptography, Data Protection |
| A03:2021 | Injection | Injection Prevention |
| A04:2021 | Insecure Design | (See code-review-checklist SKILL.md) |
| A05:2021 | Security Misconfiguration | Error Handling, API Security |
| A06:2021 | Vulnerable Components | Dependencies |
| A07:2021 | Auth Failures | Authentication & Authorization |
| A08:2021 | Software/Data Integrity | Dependencies |
| A09:2021 | Logging Failures | Logging & Monitoring |
| A10:2021 | SSRF | Input Validation |

## Input Validation

### User Input

Check for:

- [ ] All user input is validated before use
- [ ] Validation happens server-side (client-side is for UX only)
- [ ] Input length limits are enforced
- [ ] Input type/format is verified (email, URL, etc.)
- [ ] Null/undefined inputs are handled

Common vulnerabilities:

- Buffer overflow from unbounded input
- Type confusion attacks
- Prototype pollution (JavaScript)

### File Uploads

Check for:

- [ ] File type validation (not just extension)
- [ ] File size limits enforced
- [ ] Filenames sanitized before storage
- [ ] Files stored outside web root
- [ ] Antivirus scanning for uploaded content

Common vulnerabilities:

- Executable uploads
- Path traversal via filename
- DoS via large files

## Injection Prevention

### SQL Injection

Check for:

- [ ] Parameterized queries used (not string concatenation)
- [ ] ORM methods used correctly
- [ ] Dynamic table/column names are whitelisted
- [ ] Stored procedures don't use dynamic SQL

Red flags:

```sql
-- BAD: String concatenation
"SELECT * FROM users WHERE id = " + userId

-- GOOD: Parameterized
"SELECT * FROM users WHERE id = ?"
```

### Command Injection

Check for:

- [ ] Shell commands avoid user input
- [ ] If unavoidable, input is strictly validated
- [ ] Use language APIs instead of shell commands
- [ ] Arguments are properly escaped

Red flags:

```python
# BAD: Direct input in command
os.system(f"convert {user_file} output.png")

# GOOD: Use library APIs
from PIL import Image

Image.open(validated_path).save("output.png")
```

### XSS (Cross-Site Scripting)

Check for:

- [ ] Output encoding for HTML context
- [ ] Content-Security-Policy headers set
- [ ] User content in URLs is encoded
- [ ] JavaScript frameworks' safe methods used

Red flags:

```javascript
// BAD: innerHTML with user content
element.innerHTML = userInput;

// GOOD: textContent or sanitization
element.textContent = userInput;
```

### Path Traversal

Check for:

- [ ] File paths are canonicalized before use
- [ ] Paths verified to be within allowed directories
- [ ] Symlinks resolved and checked
- [ ] No direct use of user input in paths

Red flags:

```python
# BAD: Direct path concatenation
open(f"/data/{user_filename}")

# GOOD: Validate within allowed directory
safe_path = Path("/data").joinpath(user_filename).resolve()
if not safe_path.is_relative_to("/data"):
    raise SecurityError("Invalid path")
```

## Authentication & Authorization

### Authentication

Check for:

- [ ] Passwords hashed with modern algorithm (bcrypt, argon2)
- [ ] Timing-safe comparison for secrets
- [ ] Rate limiting on login attempts
- [ ] Secure session management
- [ ] MFA implementation is robust

Red flags:

- MD5/SHA1 for passwords
- Plaintext password storage
- Credentials in logs
- Predictable session tokens

### Authorization

Check for:

- [ ] Authorization checks on every request
- [ ] Checks happen server-side
- [ ] Principle of least privilege applied
- [ ] Resource ownership verified
- [ ] Admin functions protected

Common issues:

- IDOR (Insecure Direct Object Reference)
- Missing function-level access control
- Privilege escalation paths

## Data Protection

### Sensitive Data Handling

Check for:

- [ ] PII encrypted at rest
- [ ] TLS for data in transit
- [ ] Sensitive data not in logs
- [ ] Secure deletion when needed
- [ ] Data minimization practiced

Sensitive data includes:

- Passwords, tokens, API keys
- Personal identifiable information
- Financial data
- Health information

### Secrets Management

Check for:

- [ ] No hardcoded secrets in code
- [ ] Secrets not in version control
- [ ] Environment variables or secret managers used
- [ ] Secrets rotated periodically
- [ ] Different secrets per environment

Red flags:

```python
# BAD: Hardcoded secret
API_KEY = "sk-1234567890abcdef"

# GOOD: Environment variable
API_KEY = os.environ["API_KEY"]
```

## Cryptography

### Common Issues

Check for:

- [ ] Modern algorithms (AES-256, RSA-2048+, SHA-256+)
- [ ] Proper random number generation (CSPRNG)
- [ ] Keys stored securely
- [ ] IV/nonce not reused
- [ ] Authenticated encryption used

Red flags:

- Custom crypto implementations
- Deprecated algorithms (DES, MD5, SHA1)
- Predictable random values
- ECB mode for block ciphers

## Error Handling

### Information Leakage

Check for:

- [ ] Generic error messages to users
- [ ] Detailed errors only in logs
- [ ] Stack traces not exposed
- [ ] System information hidden
- [ ] Debug mode disabled in production

Red flags:

```python
# BAD: Exposing internal details
return {"error": str(exception)}

# GOOD: Generic message
return {"error": "An error occurred", "reference": error_id}
```

## Dependencies

### Third-Party Code

Check for:

- [ ] Dependencies from trusted sources
- [ ] Known vulnerabilities checked (npm audit, etc.)
- [ ] Dependency versions pinned
- [ ] Minimal necessary dependencies
- [ ] License compliance

Tools:

- `npm audit` / `yarn audit`
- `pip-audit`
- Snyk, Dependabot, etc.

## API Security

### REST API

Check for:

- [ ] Authentication required
- [ ] Rate limiting implemented
- [ ] Input validation on all parameters
- [ ] Proper HTTP methods used
- [ ] CORS configured correctly

### GraphQL

Check for:

- [ ] Query depth limiting
- [ ] Query complexity analysis
- [ ] Introspection disabled in production
- [ ] Field-level authorization

## Logging & Monitoring

### Security Logging

Check for:

- [ ] Authentication events logged
- [ ] Authorization failures logged
- [ ] Input validation failures logged
- [ ] Sensitive data not logged
- [ ] Log injection prevented

Required log events:

- Login success/failure
- Password changes
- Permission changes
- Access to sensitive data
- Security configuration changes

## Quick Remediation Patterns

### SQL Injection Fix

```python
# Before (vulnerable)
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)

# After (safe)
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))
```

### XSS Fix

```javascript
// Before (vulnerable)
document.getElementById('output').innerHTML = userInput;

// After (safe) - Option 1: textContent
document.getElementById('output').textContent = userInput;

// After (safe) - Option 2: DOMPurify for HTML
import DOMPurify from 'dompurify';
document.getElementById('output').innerHTML = DOMPurify.sanitize(userInput);
```

### IDOR Fix

```python
# Before (vulnerable)
@app.get("/api/documents/{doc_id}")
def get_document(doc_id: int, user: User):
    return db.get_document(doc_id)

# After (safe)
@app.get("/api/documents/{doc_id}")
def get_document(doc_id: int, user: User):
    doc = db.get_document(doc_id)
    if doc.owner_id != user.id and not user.is_admin:
        raise HTTPException(403, "Forbidden")
    return doc
```

### Command Injection Fix

```python
# Before (vulnerable)
import os
os.system(f"ping {user_host}")

# After (safe) - Use subprocess with list args
import subprocess
import shlex
subprocess.run(["ping", "-c", "1", shlex.quote(validated_host)], check=True)
```

### Path Traversal Fix

```python
# Before (vulnerable)
from pathlib import Path
file_path = Path(f"/uploads/{user_filename}")
content = file_path.read_text()

# After (safe)
from pathlib import Path
base_dir = Path("/uploads").resolve()
file_path = (base_dir / user_filename).resolve()
if not file_path.is_relative_to(base_dir):
    raise ValueError("Invalid file path")
content = file_path.read_text()
```

### Insecure Password Storage Fix

```python
# Before (vulnerable)
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# After (safe)
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verification
if bcrypt.checkpw(password.encode(), stored_hash):
    # Password matches
```

## Additional Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Secure Coding Guidelines](https://www.nist.gov/publications)
