# Container Hardening Guide

Comprehensive security guide for building, deploying, and running secure containers.

## Base Image Selection

### Image Trust Hierarchy

| Source                        | Trust Level | Use Case                      |
|-------------------------------|-------------|-------------------------------|
| Official images (Docker Hub)  | High        | Standard runtime environments |
| Verified publisher images     | High        | Vendor-provided images        |
| Organization private registry | High        | Internal base images          |
| Community images              | Low         | Avoid for production          |
| Unknown sources               | None        | Never use                     |

### Minimal Base Images

**Comparison:**

| Base Image               | Size       | Attack Surface | Use Case                      |
|--------------------------|------------|----------------|-------------------------------|
| scratch                  | ~0MB       | Minimal        | Static binaries (Go, Rust)    |
| distroless               | ~2-20MB    | Very low       | Runtime-only containers       |
| alpine                   | ~5MB       | Low            | General purpose, shell needed |
| slim variants            | ~50-100MB  | Medium         | When dependencies required    |
| Full OS (ubuntu, debian) | ~100-500MB | High           | Avoid for production          |

### Version Pinning

**Correct:**

```dockerfile
# Pin to specific digest for reproducibility
FROM node:20.10.0-alpine3.18@sha256:abc123...

# Or at minimum, pin to minor version
FROM node:20.10-alpine3.18
```

**Incorrect:**

```dockerfile
FROM node:latest        # Never do this
FROM node:20           # Too broad
FROM node:lts          # Changes over time
```

## Dockerfile Security

### Non-Root User

```dockerfile
# Create dedicated user and group
RUN addgroup --gid 1001 --system appgroup && \
    adduser --uid 1001 --system --ingroup appgroup appuser

# Set ownership of application files
COPY --chown=appuser:appgroup . /app

# Switch to non-root user
USER appuser

# Run application
CMD ["./app"]
```

### Multi-Stage Builds

```dockerfile
# Build stage - has build tools
FROM golang:1.21-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app

# Runtime stage - minimal
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

**Benefits:**

- Build tools not in final image
- Smaller attack surface
- Reduced image size
- Secrets used in build not in final layer

### Avoid Secret Exposure

**WRONG - secrets in layer:**

```dockerfile
# This copies .env to image
COPY . .

# This bakes secret into layer
ARG API_KEY
ENV API_KEY=$API_KEY

# This leaves secret in layer history
RUN --mount=type=secret,id=key cat /run/secrets/key > /app/.env
```

**CORRECT:**

```dockerfile
# Use secret only during build, don't persist
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) \
    npm ci --only=production

# Or inject at runtime
ENV API_KEY=""  # Set via orchestrator
```

### Minimize Layers and Tools

```dockerfile
# Combine commands to reduce layers
RUN apk add --no-cache \
    package1 \
    package2 && \
    rm -rf /var/cache/apk/*

# Remove unnecessary tools
RUN apk del --purge \
    curl \
    wget \
    && rm -rf /tmp/*

# Use .dockerignore
# In .dockerignore:
.git
.env
*.md
tests/
```

## Runtime Security

### Security Context (Kubernetes)

```yaml
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
    runAsGroup: 1001
    fsGroup: 1001
    seccompProfile:
      type: RuntimeDefault

  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
          add:
            - NET_BIND_SERVICE  # Only if needed

      resources:
        limits:
          memory: "256Mi"
          cpu: "500m"
        requests:
          memory: "128Mi"
          cpu: "100m"

      volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache

  volumes:
    - name: tmp
      emptyDir: { }
    - name: cache
      emptyDir: { }
```

### Docker Run Security

```bash
# Secure docker run example
docker run \
  --user 1001:1001 \
  --read-only \
  --tmpfs /tmp \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --security-opt seccomp=default \
  --memory 256m \
  --cpus 0.5 \
  --pids-limit 100 \
  --network custom-network \
  myapp:1.0.0
```

### Capability Management

**Common capabilities and their risks:**

| Capability           | Risk                  | When Needed                |
|----------------------|-----------------------|----------------------------|
| CAP_NET_RAW          | Network sniffing      | Ping, network diagnostics  |
| CAP_SYS_ADMIN        | Container escape      | Almost never (avoid)       |
| CAP_NET_BIND_SERVICE | Bind low ports        | Web servers on port 80/443 |
| CAP_CHOWN            | Change file ownership | File management            |
| CAP_SETUID/SETGID    | Privilege escalation  | Process user switching     |

**Default policy:**

```
Drop ALL capabilities
Add back only specifically needed
Document why each capability is required
```

## Network Security

### Container Network Isolation

```yaml
# Kubernetes NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: frontend
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              role: database
      ports:
        - protocol: TCP
          port: 5432
```

### Service Mesh Security

When using service mesh (Istio, Linkerd):

- Enable mTLS between services
- Implement authorization policies
- Use egress gateways for external access
- Enable access logging

## Image Scanning

### What Scanners Detect

| Category                 | Examples                         |
|--------------------------|----------------------------------|
| OS vulnerabilities       | CVEs in base image packages      |
| Application dependencies | Vulnerable libraries             |
| Misconfigurations        | Running as root, exposed secrets |
| Malware                  | Known malicious software         |
| Secrets                  | Hardcoded credentials            |

### Scanning Integration Points

```
┌─────────────┐
│   Build     │ ◄── Scan during CI (block on critical)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Registry  │ ◄── Continuous scanning (alert on new CVEs)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Runtime   │ ◄── Admission control (block unscanned)
└─────────────┘
```

### Vulnerability Response Matrix

| Severity | Response Time | Action                            |
|----------|---------------|-----------------------------------|
| Critical | < 24 hours    | Block deployment, emergency patch |
| High     | < 7 days      | Plan immediate patch              |
| Medium   | < 30 days     | Include in regular update cycle   |
| Low      | < 90 days     | Address in maintenance window     |

## Registry Security

### Access Control

```yaml
# Example registry policy
{
  "policies": [
    {
      "name": "production-images",
      "rules": [
        {
          "action": "ALLOW",
          "operation": "PUSH",
          "principals": [ "group:ci-systems" ]
        },
        {
          "action": "ALLOW",
          "operation": "PULL",
          "principals": [ "serviceAccount:k8s-nodes" ]
        },
        {
          "action": "DENY",
          "operation": "*",
          "principals": [ "allUsers" ]
        }
      ]
    }
  ]
}
```

### Image Signing

```bash
# Sign image with cosign
cosign sign --key cosign.key myregistry/myapp:1.0.0

# Verify signature before deployment
cosign verify --key cosign.pub myregistry/myapp:1.0.0
```

### Admission Control

```yaml
# Kubernetes policy to require signed images
apiVersion: policy/v1
kind: ClusterAdmissionPolicy
spec:
  rules:
    - apiGroups: [ "" ]
      apiVersions: [ "v1" ]
      resources: [ "pods" ]
      operations: [ "CREATE", "UPDATE" ]
  validatingConfig:
    rules:
      - name: require-signed-images
        match:
          resources:
            - pods
        validate:
          message: "Images must be signed"
          pattern:
            spec:
              containers:
                - image: "myregistry/*"
```

## Monitoring and Logging

### Container Audit Logging

Events to log:

- Container start/stop
- Exec into container
- File system changes (if writable)
- Network connections
- Process execution
- Capability usage

### Runtime Detection

Monitor for:

- Unexpected processes
- Unusual network connections
- File integrity changes
- Privilege escalation attempts
- Abnormal resource usage

## Hardening Checklist

### Build Time

- [ ] Use minimal, pinned base image
- [ ] Implement multi-stage builds
- [ ] Run as non-root user
- [ ] Remove unnecessary packages
- [ ] No secrets in image layers
- [ ] Scan for vulnerabilities before push
- [ ] Sign images
- [ ] Use .dockerignore

### Deploy Time

- [ ] Pull from trusted registry only
- [ ] Verify image signature
- [ ] Block unscanned images
- [ ] Apply resource limits
- [ ] Set security context

### Runtime

- [ ] Read-only filesystem
- [ ] Drop all capabilities
- [ ] No privilege escalation
- [ ] Network policies enforced
- [ ] Runtime monitoring enabled
- [ ] Regular re-scanning for new CVEs

## Common Misconfigurations

### Dockerfile Issues

| Issue          | Risk                      | Fix                       |
|----------------|---------------------------|---------------------------|
| `USER root`    | Full container compromise | Use non-root user         |
| `FROM :latest` | Unpredictable updates     | Pin to specific version   |
| `ADD` with URL | Unverified downloads      | Use `COPY` or verify hash |
| `COPY . .`     | Secrets in image          | Use .dockerignore         |

### Runtime Issues

| Issue                 | Risk               | Fix                   |
|-----------------------|--------------------|-----------------------|
| Privileged mode       | Host access        | Never use privileged  |
| Host network          | Network sniffing   | Use container network |
| Host PID namespace    | Process visibility | Use container PID     |
| Mounted docker socket | Container escape   | Never mount socket    |
| Writable root FS      | Persistent malware | Read-only filesystem  |
