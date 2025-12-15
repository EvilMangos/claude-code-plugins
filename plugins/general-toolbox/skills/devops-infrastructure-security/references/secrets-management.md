# Secrets Management Patterns

Comprehensive guide to managing secrets securely across development, CI/CD, and production environments.

## Secrets Hierarchy

Understanding where secrets should live at each stage:

| Stage | Storage | Access Pattern |
|-------|---------|----------------|
| Development | Local vault, env files (gitignored) | Developer machine only |
| CI/CD | Platform secrets (GitHub, GitLab, etc.) | Pipeline jobs only |
| Production | Dedicated secrets manager | Runtime injection |

## Secret Types and Handling

### API Keys and Tokens

**Characteristics:**
- Usually long-lived
- Often have broad permissions
- Frequently rotated less than they should be

**Best practices:**
- Create separate keys per environment
- Use scoped keys with minimum permissions
- Set up expiration where supported
- Monitor usage for anomalies

### Database Credentials

**Characteristics:**
- Direct access to sensitive data
- Often shared across multiple services
- Critical blast radius if compromised

**Best practices:**
- Use connection poolers with credential rotation
- Implement per-service database users
- Prefer IAM authentication where available
- Never store connection strings with credentials

### Encryption Keys

**Characteristics:**
- Loss means data loss
- Exposure means data exposure
- Require special backup procedures

**Best practices:**
- Use managed key services (KMS)
- Implement key rotation policies
- Maintain key escrow for recovery
- Log all key access operations

## Environment-Specific Patterns

### Development Environment

**DO:**
```
# .env.example (committed, no real values)
DATABASE_URL=postgres://user:password@localhost:5432/dev
API_KEY=your_api_key_here

# .env (gitignored, real development values)
DATABASE_URL=postgres://dev:devpass@localhost:5432/myapp
API_KEY=sk_test_abc123
```

**DON'T:**
```
# Committed to repo
config.py:
    DATABASE_URL = "postgres://prod:realpassword@prod-db.example.com/production"
```

**Gitignore essentials:**
```gitignore
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

### CI/CD Environment

**GitHub Actions pattern:**
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Requires approval
    steps:
      - name: Deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: ./deploy.sh
        # Script reads from $DATABASE_URL env var
```

**Secret scoping:**
```
Organization secrets: Cross-repo utilities (rarely used)
Repository secrets: Default for most secrets
Environment secrets: Production/staging separation
```

### Production Environment

**Application pattern:**
```python
# Don't do this
DATABASE_URL = "postgres://user:hardcoded@db.example.com/prod"

# Do this instead
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ConfigurationError("DATABASE_URL not set")
```

**Kubernetes secrets pattern:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  # Base64 encoded (NOT encrypted)
  database-url: cG9zdGdyZXM6Ly91c2VyOnBhc3NAZGIvYXBw

---
# Better: Use external secrets operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: app-secrets
  data:
    - secretKey: database-url
      remoteRef:
        key: prod/database
        property: url
```

## Rotation Strategies

### Manual Rotation Checklist

1. Generate new credential in secrets manager
2. Update application configuration to use new credential
3. Deploy application with new credential
4. Verify application works with new credential
5. Revoke old credential
6. Update any documentation referencing old credential

### Automated Rotation Pattern

```
┌─────────────────┐
│ Secrets Manager │
│ (rotates key)   │
└────────┬────────┘
         │ trigger
         ▼
┌─────────────────┐
│ Rotation Lambda │
│ (updates target)│
└────────┬────────┘
         │ update
         ▼
┌─────────────────┐
│ Target Service  │
│ (database, API) │
└─────────────────┘
```

### Rotation Triggers

| Trigger | Response Time |
|---------|---------------|
| Scheduled rotation | Per policy (30-90 days) |
| Personnel change | Within 24 hours |
| Suspected compromise | Immediately |
| Security audit finding | Per severity |

## Secret Detection and Prevention

### Pre-commit Checks

**Patterns to detect:**
```
# API keys
sk_live_[a-zA-Z0-9]{24}
AKIA[0-9A-Z]{16}
ghp_[a-zA-Z0-9]{36}

# Generic secrets
password\s*=\s*['"][^'"]+['"]
secret\s*=\s*['"][^'"]+['"]
api_key\s*=\s*['"][^'"]+['"]

# Private keys
-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----
```

### Remediation After Exposure

**If secret committed to public repo:**

1. **Revoke immediately** - Don't wait to rotate, revoke now
2. **Generate new secret** - Create replacement credential
3. **Update applications** - Deploy with new secret
4. **Scan for abuse** - Check logs for unauthorized usage
5. **Clean git history** - Use git-filter-repo or BFG
6. **Force push** - Push cleaned history
7. **Document** - Record incident for post-mortem

**Git history cleaning:**
```bash
# Using BFG Repo-Cleaner
java -jar bfg.jar --replace-text secrets.txt repo.git

# Using git-filter-repo
git filter-repo --replace-text expressions.txt
```

**Note:** GitHub caches commits. Even after cleaning, consider the secret compromised.

## Secrets Manager Comparison

### When to Use Each

| Scenario | Recommended Tool |
|----------|-----------------|
| Cloud-native, single cloud | Cloud provider's native (AWS Secrets Manager, etc.) |
| Multi-cloud or hybrid | HashiCorp Vault |
| Kubernetes-native | External Secrets Operator + backend |
| Simple applications | Platform secrets (GitHub, Vercel, etc.) |
| Local development | dotenv with .env.local (gitignored) |

### Access Patterns

**Service-to-service:**
```
1. Application starts
2. Uses instance role/service account to authenticate
3. Requests secrets from secrets manager
4. Secrets manager validates identity
5. Returns secrets for authorized resources only
```

**Human access:**
```
1. Engineer authenticates (SSO, MFA)
2. Requests access to secret
3. Requires approval for production secrets
4. Access logged and time-limited
5. Secret displayed/copied
```

## Audit and Compliance

### Audit Logging Requirements

Log these events:
- Secret creation, modification, deletion
- Secret access (read operations)
- Failed access attempts
- Permission changes
- Rotation events

### Access Review Process

**Quarterly review checklist:**
- [ ] Remove access for departed personnel
- [ ] Verify service accounts still needed
- [ ] Check for overly broad permissions
- [ ] Review secrets that haven't been rotated
- [ ] Audit secrets access patterns

### Compliance Considerations

| Requirement | Implementation |
|-------------|----------------|
| Encryption at rest | Use secrets manager with KMS |
| Encryption in transit | TLS for all secret retrieval |
| Access control | IAM policies, RBAC |
| Audit trail | Enable access logging |
| Separation of duties | Require approval for production |

## Emergency Procedures

### Suspected Compromise Runbook

```
1. ASSESS (5 minutes)
   - What secrets may be exposed?
   - What systems are affected?
   - What's the blast radius?

2. CONTAIN (15 minutes)
   - Revoke suspected secrets
   - Block suspicious access
   - Preserve logs for forensics

3. RECOVER (varies)
   - Generate new secrets
   - Deploy updated configuration
   - Verify service restoration

4. ANALYZE (ongoing)
   - Review access logs
   - Identify root cause
   - Document timeline

5. IMPROVE (post-incident)
   - Update procedures
   - Implement additional controls
   - Conduct post-mortem
```

### Communication Template

```
SECURITY INCIDENT NOTIFICATION

Severity: [Critical/High/Medium/Low]
Time detected: [timestamp]
Affected systems: [list]
Status: [Investigating/Contained/Resolved]

Summary:
[Brief description of what happened]

Impact:
[What data/systems may be affected]

Actions taken:
[List of remediation steps]

Next update: [timestamp]
```
