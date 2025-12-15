# Secure CI/CD Pipeline Examples

Working examples of secure pipeline configurations for common CI/CD platforms.

## GitHub Actions

### Secure Build and Deploy Pipeline

```yaml
name: Secure CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Minimal default permissions
permissions:
  contents: read

jobs:
  # Security scanning job
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write  # For CodeQL
    steps:
      # Pin action to SHA for security
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: javascript

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3

  # Dependency audit
  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Audit dependencies
        run: npm audit --audit-level=high

  # Build job
  build:
    runs-on: ubuntu-latest
    needs: [security-scan, dependency-audit]
    permissions:
      contents: read
      packages: write  # Only if pushing to GHCR
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          # Use cache for faster builds
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Container scanning
  container-scan:
    runs-on: ubuntu-latest
    needs: build
    permissions:
      contents: read
      security-events: write
    steps:
      - name: Scan container image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  # Deployment with environment protection
  deploy:
    runs-on: ubuntu-latest
    needs: [build, container-scan]
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://myapp.example.com
    permissions:
      id-token: write  # For OIDC authentication
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-deploy
          aws-region: us-east-1

      - name: Deploy to ECS
        env:
          IMAGE: ghcr.io/${{ github.repository }}:${{ github.sha }}
        run: |
          aws ecs update-service \
            --cluster production \
            --service myapp \
            --force-new-deployment
```

### Key Security Features

1. **Pinned action versions** - Using SHA instead of tags
2. **Minimal permissions** - Only what's needed per job
3. **Security scanning** - CodeQL, dependency audit, container scan
4. **Environment protection** - Required approval for production
5. **OIDC authentication** - No long-lived credentials
6. **Secret handling** - Using platform secrets only

---

## GitLab CI

### Secure Pipeline Configuration

```yaml
# .gitlab-ci.yml

stages:
  - security
  - build
  - scan
  - deploy

variables:
  # Don't clone full history
  GIT_DEPTH: 1
  # Secure Docker builds
  DOCKER_TLS_CERTDIR: "/certs"

# Security defaults
default:
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY

# SAST scanning
sast:
  stage: security
  image: returntocorp/semgrep
  script:
    - semgrep ci --config auto
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# Dependency scanning
dependency_scan:
  stage: security
  image: node:20-alpine
  script:
    - npm ci
    - npm audit --audit-level=high
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# Secret detection
secret_detection:
  stage: security
  image: trufflesecurity/trufflehog
  script:
    - trufflehog git --only-verified file://. --fail
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

# Build container
build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# Container scanning
container_scan:
  stage: scan
  image:
    name: aquasec/trivy
    entrypoint: [""]
  script:
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# Production deployment
deploy_production:
  stage: deploy
  script:
    - ./deploy.sh $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  environment:
    name: production
    url: https://myapp.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual  # Require manual trigger
  resource_group: production  # Prevent concurrent deploys
```

---

## Jenkins

### Secure Jenkinsfile

```groovy
pipeline {
    agent {
        docker {
            image 'node:20-alpine'
            args '-u root:root'  // Only if necessary, prefer non-root
        }
    }

    options {
        // Security options
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        // Use credentials plugin for secrets
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
        // Don't echo commands with secrets
        CI = 'true'
    }

    stages {
        stage('Security Scan') {
            steps {
                // SAST
                sh 'npm audit --audit-level=high'

                // Secret scanning
                sh '''
                    if grep -rE "(password|secret|key)\\s*=\\s*['\"][^'\"]+['\"]" src/; then
                        echo "Potential secret found!"
                        exit 1
                    fi
                '''
            }
        }

        stage('Build') {
            steps {
                sh 'npm ci'
                sh 'npm run build'
            }
        }

        stage('Build Container') {
            steps {
                script {
                    // Login without exposing credentials
                    sh '''
                        echo "$DOCKER_CREDENTIALS_PSW" | docker login -u "$DOCKER_CREDENTIALS_USR" --password-stdin
                    '''

                    // Build with cache
                    sh '''
                        docker build \
                            --tag myapp:${BUILD_NUMBER} \
                            --tag myapp:latest \
                            .
                    '''
                }
            }
        }

        stage('Scan Container') {
            steps {
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:${BUILD_NUMBER}'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'deploy-credentials',
                    usernameVariable: 'DEPLOY_USER',
                    passwordVariable: 'DEPLOY_TOKEN'
                )]) {
                    sh './deploy.sh'
                }
            }
        }
    }

    post {
        always {
            // Clean up
            sh 'docker logout'
            cleanWs()
        }
        failure {
            // Notify on failure
            slackSend(channel: '#alerts', message: "Build failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}")
        }
    }
}
```

---

## Secure Dockerfile for CI/CD

```dockerfile
# Build stage
FROM node:20-alpine AS builder

# Security: run as non-root during build
RUN addgroup -S buildgroup && adduser -S builduser -G buildgroup
USER builduser

WORKDIR /app

# Copy dependency files first for caching
COPY --chown=builduser:buildgroup package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source
COPY --chown=builduser:buildgroup src/ ./src/

# Build
RUN npm run build

# Production stage
FROM gcr.io/distroless/nodejs20-debian12:nonroot

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder --chown=nonroot:nonroot /app/node_modules ./node_modules
COPY --from=builder --chown=nonroot:nonroot /app/dist ./dist

# Run as non-root
USER nonroot

# Use exec form for signals
CMD ["dist/index.js"]
```

---

## Secure Secrets Handling in Pipelines

### GitHub Actions

```yaml
steps:
  - name: Deploy
    env:
      # Secrets masked in logs automatically
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
    run: |
      # Never echo secrets
      # export DATABASE_URL for child processes
      ./deploy.sh
```

### GitLab CI

```yaml
deploy:
  script:
    - ./deploy.sh
  variables:
    # Masked in logs
    DATABASE_URL: $DATABASE_URL
  # Protect variable in UI settings:
  # Settings > CI/CD > Variables > Protected + Masked
```

### Jenkins

```groovy
// Use withCredentials block
withCredentials([string(credentialsId: 'api-key', variable: 'API_KEY')]) {
    sh '''
        # API_KEY available but masked in logs
        curl -H "Authorization: Bearer $API_KEY" https://api.example.com
    '''
}

// Never do this
sh "curl -H 'Authorization: Bearer ${API_KEY}' https://api.example.com"  // Interpolated!
```

---

## Pipeline Injection Prevention

### Unsafe Patterns

```yaml
# UNSAFE - PR title can contain shell commands
- run: echo "Building PR: ${{ github.event.pull_request.title }}"

# UNSAFE - Branch name can be malicious
- run: git checkout ${{ github.head_ref }}

# UNSAFE - Commit message injection
- run: echo "${{ github.event.head_commit.message }}"
```

### Safe Patterns

```yaml
# SAFE - Use environment variable
- name: Echo PR title
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "Building PR: $PR_TITLE"

# SAFE - Validate branch name
- name: Checkout
  env:
    BRANCH: ${{ github.head_ref }}
  run: |
    if [[ "$BRANCH" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
      git checkout "$BRANCH"
    else
      echo "Invalid branch name"
      exit 1
    fi
```

---

## Deployment Security Checklist

### Before Deployment

- [ ] All security scans passed
- [ ] Container image scanned
- [ ] Dependencies audited
- [ ] Secrets not in code
- [ ] Image signed and verified
- [ ] Required approvals obtained

### During Deployment

- [ ] Use OIDC for cloud auth (no static keys)
- [ ] Deploy from immutable artifact (SHA, not tag)
- [ ] Audit logging enabled
- [ ] Rollback plan ready
- [ ] Health checks configured

### After Deployment

- [ ] Verify deployment succeeded
- [ ] Check application health
- [ ] Monitor for anomalies
- [ ] Update deployment records
