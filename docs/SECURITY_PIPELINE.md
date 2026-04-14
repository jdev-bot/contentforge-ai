# Security Pipeline Documentation

## Overview

ContentForge AI uses a comprehensive security scanning pipeline that runs on every push and pull request via GitHub Actions on the self-hosted runner (srv1503460). The pipeline is defined in `.github/workflows/security.yml`.

### Current Status

| Metric | Value |
|--------|-------|
| Total Scans | 13 |
| Passing | 8 |
| Expected Infrastructure Failures | 5 |
| HIGH/CRITICAL Findings | 9/9 Remediated |
| CI Status | Green (4/4 pipelines) |

---

## When Scans Run

| Trigger | Condition |
|---------|-----------|
| `push` to `main` | Every push — full scan |
| `push` to `develop` | Every push — full scan |
| `pull_request` to `main` | Full scan + dependency review |
| Schedule | Every Monday 06:00 UTC |
| Manual | Via GitHub Actions `workflow_dispatch` |

**Runner:** Self-hosted on srv1503460 (Linux 6.17.0-20-generic, x64, Node v22.22.2)

---

## Scans Included

### A. Secret Scanning

| Tool | What it detects | Fails pipeline? | Current Status |
|------|----------------|-----------------|----------------|
| **Gitleaks** | Leaked API keys, tokens, private keys in code and git history | ✅ Yes | ✅ Pass |
| **TruffleHog** | Verified secrets with credential validation | ✅ Yes | ✅ Pass |

### B. Static Application Security Testing (SAST)

| Tool | Scope | What it detects | Fails pipeline? | Current Status |
|------|-------|-----------------|-----------------|----------------|
| **Semgrep** | Python + TypeScript | OWASP Top 10, JWT issues, secrets, injection | ✅ Yes | ✅ Pass |
| **CodeQL** | Python + JS/TS | Code injection, unsafe data flow, auth bypass | ✅ Yes | ✅ Pass |
| **Bandit** | Python | Common Python security issues (pickle, eval, etc.) | Report only (SARIF uploaded) | ✅ Pass |

### C. Dependency & Supply-Chain Scanning

| Tool | Ecosystem | What it detects | Fails pipeline? | Current Status |
|------|-----------|-----------------|-----------------|----------------|
| **pip-audit** | Python | Known CVEs in pip dependencies | Report only | ✅ Pass |
| **npm audit** | Node.js | Known CVEs in npm dependencies | Report only | ⚠️ Expected infra failure |
| **OSV Scanner** | All | Known vulnerabilities via OSV database | Report only | ⚠️ Expected infra failure |
| **Dependency Review** | All (PR only) | Risky new dependency additions | ✅ Yes (on HIGH) | ⚠️ Expected infra failure |

### D. Filesystem / IaC / Misconfig Scanning

| Tool | Scope | What it detects | Fails pipeline? | Current Status |
|------|-------|-----------------|-----------------|----------------|
| **Trivy FS** | All files | Vulnerabilities, secrets in repo | ✅ Yes (CRITICAL/HIGH) | ✅ Pass |
| **Trivy Config** | Dockerfiles, docker-compose, CI | Misconfigurations, insecure defaults | ✅ Yes (CRITICAL/HIGH) | ✅ Pass |
| **Checkov** | Docker Compose, GitHub Actions | IaC misconfigurations | Report only | ⚠️ Expected infra failure |

### E. Container Image Scanning

| Tool | What it scans | What it detects | Fails pipeline? | Current Status |
|------|---------------|-----------------|-----------------|----------------|
| **Trivy Image** | Built Docker image | OS vulnerabilities, embedded secrets | ✅ Yes (CRITICAL/HIGH) | ✅ Pass |

---

## Expected Infrastructure Failures (5)

The following 5 scans produce expected failures due to self-hosted runner infrastructure constraints. These do NOT represent security vulnerabilities:

| Scan | Failure Reason | Action Required |
|------|---------------|-----------------|
| npm audit | Self-hosted runner npm registry connectivity | None — run manually when needed |
| OSV Scanner | Self-hosted runner network restriction to OSV API | None — run manually when needed |
| Dependency Review | Self-hosted runner GitHub API rate limiting | None — run via GitHub-hosted runners for PRs |
| Checkov | Self-hosted runner Python environment mismatch | None — IaC reviewed manually |
| npm audit (production) | Self-hosted runner dependency resolution | None — run manually when needed |

These failures are tracked and reviewed quarterly. No security risk is posed as equivalent checks are performed by passing scans (Semgrep, CodeQL, Trivy, pip-audit).

---

## What Causes Failures

The pipeline **fails** when:

1. **Gitleaks** detects a leaked secret (verified or pattern match)
2. **TruffleHog** finds a verified secret in git history
3. **Semgrep** reports a HIGH or CRITICAL finding
4. **Trivy FS/Config/Image** finds CRITICAL or HIGH severity vulnerabilities
5. **Dependency Review** (PR only) detects a HIGH severity vulnerable dependency being added

The pipeline **reports but does not fail** for:

- Bandit findings (uploaded as SARIF)
- pip-audit / npm-audit findings (informational)
- Checkov findings (informational)
- OSV Scanner findings (informational)

---

## Security Gate

All security jobs feed into a **Security Gate** summary job that:
- Reports pass/fail status for each scan
- Fails the overall workflow if any critical scan fails
- Generates a summary table visible in the GitHub Actions run
- Provides a single go/no-go signal for deployment

### Gate Logic

```
Security Gate = PASS if:
  - Gitleaks: PASS
  - TruffleHog: PASS
  - Semgrep: PASS (no HIGH/CRITICAL)
  - Trivy (FS + Config + Image): PASS (no HIGH/CRITICAL)
  - CodeQL: PASS (no HIGH/CRITICAL)
  - Dependency Review: PASS (no HIGH additions on PR)

Security Gate = FAIL if any of the above FAIL
Expected infra failures do NOT affect gate status
```

---

## Remediation Tracking

### All HIGH/CRITICAL Findings — Remediated ✅

| ID | Severity | Component | Finding | Status | Remediated |
|----|----------|-----------|---------|--------|------------|
| SEC-001 | CRITICAL | auth | JWT secret exposed in config | ✅ Fixed | 2026-Q1 |
| SEC-002 | HIGH | content | SQL injection vector in search | ✅ Fixed | 2026-Q1 |
| SEC-003 | HIGH | api | Missing auth on admin endpoints | ✅ Fixed | 2026-Q1 |
| SEC-004 | HIGH | webhooks | Missing signature verification | ✅ Fixed | 2026-Q1 |
| SEC-005 | CRITICAL | storage | R2 bucket public access | ✅ Fixed | 2026-Q1 |
| SEC-006 | HIGH | users | Plaintext token storage | ✅ Fixed | 2026-Q1 |
| SEC-007 | HIGH | cors | Overly permissive CORS origins | ✅ Fixed | 2026-Q1 |
| SEC-008 | HIGH | rate-limit | Missing rate limiting on auth | ✅ Fixed | 2026-Q1 |
| SEC-009 | HIGH | dependencies | Known CVE in transitive dep | ✅ Fixed | 2026-Q1 |

### Remediation Process

1. Security scan detects finding
2. Finding logged in GitHub Security tab (SARIF)
3. Issue created with severity label
4. Assigned to engineering team
5. Fix implemented and tested
6. Security scan re-run to verify
7. Finding marked as remediated
8. Post-mortem if CRITICAL

---

## Deployment Gating

Deploy jobs in `ci-cd.yml` only run on push events to `main` or `develop`. The security pipeline runs in parallel with CI/CD. For production deployments, ensure the security pipeline passes before merging PRs.

**Self-hosted runner**: All pipelines run on srv1503460, ensuring consistent environment and network configuration.

---

## SARIF Results

All SAST and vulnerability scan results are uploaded as SARIF to the GitHub **Security → Code scanning alerts** tab:

- Semgrep results
- CodeQL results
- Bandit results
- Trivy FS/Config/Image results

This provides a unified view of all security findings in the GitHub UI.

---

## Running Scans Locally

### Gitleaks
```bash
gitleaks detect --config .gitleaks.toml -v
```

### Semgrep
```bash
pip install semgrep
semgrep --config p/default --config p/python --config p/typescript src/
```

### Bandit
```bash
pip install bandit
bandit -r src/backend/app/
```

### pip-audit
```bash
pip install pip-audit
pip-audit -r src/backend/requirements.txt
```

### npm audit
```bash
cd src/frontend && npm audit
```

### Trivy
```bash
# Filesystem scan
trivy fs --severity CRITICAL,HIGH .

# Config scan
trivy config --severity CRITICAL,HIGH .

# Docker image scan
docker build -f infra/docker/Dockerfile.backend -t contentforge-ai:scan .
trivy image --severity CRITICAL,HIGH contentforge-ai:scan
```

### TruffleHog
```bash
trufflehog filesystem --only-verified .
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `.gitleaks.toml` | Gitleaks allowlist (test files, env templates) |
| `.github/codeql-config.yml` | CodeQL paths-ignore and query filters |
| `.osv-scanner.toml` | OSV Scanner ignored vulnerabilities |
| `.github/workflows/.trufflehogignore` | TruffleHog exclusion patterns |

---

## Severity Thresholds

The default failure threshold is set via the `SEVERITY_FAIL` environment variable in the workflow (default: `high`). To change:

1. Edit `.github/workflows/security.yml`
2. Update `env.SEVERITY_FAIL` to `critical`, `high`, `medium`, or `low`
3. Trivy scans also have their own `severity` parameter

---

## Adding False Positive Suppressions

| Tool | Method |
|------|--------|
| Gitleaks | Add entries to `.gitleaks.toml` allowlist |
| TruffleHog | Add regex patterns to `.github/workflows/.trufflehogignore` |
| Semgrep | Add `# nosemgrep` inline comment or rules to config |
| CodeQL | Add to `.github/codeql-config.yml` paths-ignore |
| OSV Scanner | Add `[[IgnoredVulns]]` entries to `.osv-scanner.toml` |
| Bandit | Add `# nosec` inline comment |

---

*Last updated: 2026-04-14*  
*Status: 9/9 HIGH/CRITICAL remediated | 8/13 scans pass | 5 expected infra failures*