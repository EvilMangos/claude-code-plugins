---
name: devops-infrastructure-security
description: This skill should be used when user asks about "secure my pipeline", "secrets management", "container security", "CI/CD security", "dependency vulnerabilities", "supply chain security", "cloud security", "infrastructure security", "secure my deployment", "harden containers", "secure environment variables", "protect API keys", "scan for vulnerabilities", "security audit", "SAST", "DAST", "SBOM", "image scanning", "credential rotation", "least privilege", "security hardening", "zero trust", or need guidance on securing DevOps workflows, infrastructure, containers, or deployment pipelines.
version: 0.1.0
---

# DevOps & Infrastructure Security

Concise checklists for securing the software supply chain, infrastructure, and deployment pipelines.

## Quick Infrastructure Security Checklist

Before deploying infrastructure changes, verify these critical items:

- [ ] Ensure no secrets exist in code, configs, or environment files committed to repo
- [ ] Store secrets in a dedicated secrets manager
- [ ] Use container images from trusted base images and scan them for vulnerabilities
- [ ] Apply least privilege to CI/CD pipeline permissions
- [ ] Scan dependencies for known vulnerabilities
- [ ] Restrict network access to minimum required
- [ ] Enable logging and monitoring for security events
- [ ] Review Infrastructure as Code for misconfigurations

## Secrets Management

### What Qualifies as a Secret

- API keys and tokens
- Database credentials
- Encryption keys
- Certificates and private keys
- OAuth client secrets
- Service account credentials
- SSH keys
- Webhook secrets

### Storage Checklist

- [ ] Use dedicated secrets manager (Vault, AWS Secrets Manager, etc.)
- [ ] Never commit secrets to version control
- [ ] Never log secrets (even in debug mode)
- [ ] Never pass secrets via command-line arguments
- [ ] Rotate secrets regularly and on personnel changes
- [ ] Use different secrets per environment

### Environment Variables

**Safe pattern:**

```
# Secrets injected at runtime from secrets manager
# Application reads from environment
DATABASE_URL=${secrets.database_url}
```

**Dangerous patterns to avoid:**

```
# Hardcoded in code
DB_PASSWORD = "production_password_123"

# In .env files committed to repo
API_KEY=sk_live_abc123

# In docker-compose.yml
environment:
  - SECRET_KEY=hardcoded_value
```

### Detection Checklist

Before committing, scan for:

- [ ] `.env` files with real values
- [ ] Hardcoded strings matching secret patterns
- [ ] Credentials in configuration files
- [ ] Keys in documentation or comments
- [ ] Secrets in CI/CD configuration files

## Container Security

### Base Image Selection

- [ ] Use official images from trusted sources
- [ ] Prefer minimal images (alpine, distroless, scratch)
- [ ] Pin to specific versions (not `latest`)
- [ ] Verify image signatures when available
- [ ] Regularly update base images

### Image Hardening Checklist

- [ ] Run as non-root user
- [ ] Remove unnecessary packages and tools
- [ ] Ensure no secrets are baked into image layers
- [ ] Use read-only root filesystem where possible
- [ ] Drop all capabilities, add only required ones
- [ ] Set resource limits (memory, CPU)

### Dockerfile Security

**Secure patterns:**

```dockerfile
# Use specific version
FROM node:20.10-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Copy only necessary files
COPY --chown=appuser:appgroup package*.json ./
COPY --chown=appuser:appgroup src/ ./src/

# Don't install dev dependencies in production
RUN npm ci --only=production
```

**Dangerous patterns:**

```dockerfile
# Avoid
FROM node:latest        # Unpinned version
USER root               # Running as root
COPY . .                # Copying everything
RUN npm install         # Installing dev dependencies
```

### Runtime Security

- [ ] Use security context constraints
- [ ] Enable seccomp profiles
- [ ] Use network policies to restrict traffic
- [ ] Mount filesystems read-only
- [ ] Limit syscalls with AppArmor/SELinux

## CI/CD Pipeline Security

### Pipeline Hardening

- [ ] Pin action/plugin versions (SHA, not tags)
- [ ] Limit permissions to minimum required
- [ ] Use separate credentials per pipeline stage
- [ ] Review third-party actions before use
- [ ] Enable audit logging for pipeline changes

### Secrets in CI/CD

- [ ] Use CI/CD secrets management, not env files
- [ ] Mask secrets in logs
- [ ] Never echo secrets for debugging
- [ ] Scope secrets to specific jobs/environments
- [ ] Rotate secrets accessible to CI/CD regularly

### GitHub Actions Security

**Secure patterns:**

```yaml
permissions:
  contents: read  # Minimum required

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # Pin to SHA, not tag
      - uses: actions/checkout@a5ac7e51b41094c92402da3b24376905380afc29
      # Don't expose secrets in outputs
      - run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
```

**Dangerous patterns:**

```yaml
permissions: write-all  # Too broad

steps:
  - uses: some-action@main  # Unpinned
  - run: echo ${{ secrets.KEY }}  # Logged!
  - run: curl ${{ github.event.pull_request.body }}  # Injection
```

### Pipeline Injection Prevention

- [ ] Never use untrusted input in run commands directly
- [ ] Sanitize PR titles, branch names, commit messages
- [ ] Use environment variables instead of inline expansion
- [ ] Review workflow triggers for injection vectors

## Dependency Security

### Dependency Management Checklist

- [ ] Use lock files (package-lock.json, Gemfile.lock, etc.)
- [ ] Pin dependencies to specific versions
- [ ] Verify package integrity (checksums, signatures)
- [ ] Review dependency tree for vulnerabilities
- [ ] Monitor for new vulnerabilities continuously
- [ ] Have process for emergency dependency updates

### Supply Chain Security

- [ ] Verify package maintainer reputation
- [ ] Check for typosquatting (similar package names)
- [ ] Review source code of critical dependencies
- [ ] Use private registries for internal packages
- [ ] Enable dependency vulnerability alerts
- [ ] Sign and verify internal artifacts

### Dependency Update Strategy

1. **Regular updates**: Schedule weekly/monthly dependency updates
2. **Security patches**: Apply critical patches within 24-48 hours
3. **Major versions**: Review breaking changes, test thoroughly
4. **Abandoned packages**: Plan migration to maintained alternatives

## Cloud Configuration Security

### General Cloud Security

- [ ] Enable MFA for all accounts
- [ ] Use roles/service accounts, not user credentials
- [ ] Follow least privilege for IAM policies
- [ ] Enable audit logging (CloudTrail, etc.)
- [ ] Review and restrict public access
- [ ] Encrypt data at rest and in transit

### Storage Security

- [ ] Block public access by default
- [ ] Enable server-side encryption
- [ ] Use bucket/container policies for access control
- [ ] Enable versioning for critical data
- [ ] Set up access logging

### Network Security

- [ ] Use private subnets for databases and internal services
- [ ] Restrict security group rules to specific IPs/ports
- [ ] Enable VPC flow logs
- [ ] Use VPN or private endpoints for sensitive access
- [ ] Implement WAF for public endpoints

## Infrastructure as Code Security

### IaC Review Checklist

- [ ] Ensure no hardcoded secrets exist in templates
- [ ] Apply least privilege to all resources
- [ ] Configure restrictive network rules
- [ ] Enable encryption where available
- [ ] Configure logging and monitoring
- [ ] Store state files securely (encrypted, access-controlled)

### Common Misconfigurations

| Resource        | Misconfiguration  | Secure Setting        |
|-----------------|-------------------|-----------------------|
| S3/Storage      | Public access     | Block public access   |
| Security Groups | 0.0.0.0/0 ingress | Specific IP ranges    |
| IAM             | Admin policies    | Scoped permissions    |
| Databases       | Public subnet     | Private subnet        |
| Encryption      | Disabled          | Enabled (KMS managed) |

## Logging & Monitoring

### Security Logging Checklist

- [ ] Log authentication events (success and failure)
- [ ] Log authorization failures
- [ ] Log administrative actions
- [ ] Log security-relevant configuration changes
- [ ] Centralize logs in secure, immutable storage
- [ ] Set up alerts for anomalies

### What to Monitor

- Failed authentication attempts
- Permission denied errors
- Unusual API call patterns
- Configuration changes
- Network traffic anomalies
- Resource usage spikes

## Incident Response Preparation

### Before Incidents

- [ ] Document secrets rotation procedures
- [ ] Have runbooks for common scenarios
- [ ] Test backup and restore processes
- [ ] Define communication channels
- [ ] Know how to revoke compromised credentials

### Credential Compromise Response

1. **Identify**: Determine which credentials are affected
2. **Revoke**: Immediately invalidate compromised credentials
3. **Rotate**: Generate new credentials
4. **Audit**: Review logs for unauthorized access
5. **Remediate**: Fix the vulnerability that caused exposure

## Detailed References

For in-depth guidance on specific topics, consult these reference documents:

- **`references/secrets-management.md`** - In-depth secrets management patterns and tools
- **`references/container-hardening.md`** - Comprehensive container security guide

### Related Skills

When reviewing infrastructure for security issues, also consider:

- **web-api-security** - Application-level security patterns
- **code-review-checklist** - General review guidance
