# Security Pipeline Documentation

## Overview

ContentForge AI uses a comprehensive security scanning pipeline that runs on every push and pull request to `main` and `develop` branches. The pipeline is defined in `.github/workflows/security.yml`.

## When Scans Run

| Trigger | Condition |
|---------|-----------|
| `push` to `main` | Every push — full scan |
| `push` to `develop` | Every push — full scan |
| `pull_request` to `main` | Full scan + dependency review |
| Schedule | Every Monday 06:00 UTC |
| Manual | Via GitHub Actions `workflow_dispatch` |

## Scans Included

### A. Secret Scanning

| Tool | What it detects | Fails pipeline? |
|------|----------------|-----------------|
| **Gitleaks** | Leaked API keys, tokens, private keys in code and git history | ✅ Yes |
| **TruffleHog** | Verified secrets with credential validation | ✅ Yes |

### B. Static Application Security Testing (SAST)

| Tool | Scope | What it detects | Fails pipeline? |
|------|-------|-----------------|-----------------|
| **Semgrep** | Python + TypeScript | OWASP Top 10, JWT issues, secrets, injection | ✅ Yes |
| **CodeQL** | Python + JS/TS | Code injection, unsafe data flow, auth bypass | ✅ Yes |
| **Bandit** | Python | Common Python security issues (pickle, eval, etc.) | Report only (SARIF uploaded) |

### C. Dependency & Supply-Chain Scanning

| Tool | Ecosystem | What it detects | Fails pipeline? |
|------|-----------|-----------------|-----------------|
| **pip-audit** | Python | Known CVEs in pip dependencies | Report only |
| **npm audit** | Node.js | Known CVEs in npm dependencies | Report only |
| **OSV Scanner** | All | Known vulnerabilities via OSV database | Report only |
| **Dependency Review** | All (PR only) | Risky new dependency additions | ✅ Yes (on HIGH) |

### D. Filesystem / IaC / Misconfig Scanning

| Tool | Scope | What it detects | Fails pipeline? |
|------|-------|-----------------|-----------------|
| **Trivy FS** | All files | Vulnerabilities, secrets in repo | ✅ Yes (CRITICAL/HIGH) |
| **Trivy Config** | Dockerfiles, docker-compose, CI | Misconfigurations, insecure defaults | ✅ Yes (CRITICAL/HIGH) |
| **Checkov** | Docker Compose, GitHub Actions | IaC misconfigurations | Report only |

### E. Container Image Scanning

| Tool | What it scans | What it detects | Fails pipeline? |
|------|---------------|-----------------|-----------------|
| **Trivy Image** | Built Docker image | OS vulnerabilities, embedded secrets | ✅ Yes (CRITICAL/HIGH) |

## What Causes Failures

The pipeline **fails** when:

1. **Gitleaks** detects a leaked secret (verified or pattern match)
2. **TruffleHog** finds a verified secret in git history
3. **Semgrep** reports a HIGH or CRITICAL finding
4. **Trivy FS/Config/Image** finds CRITICAL or HIGH severity vulnerabilities
5. **Dependency Review** (PR only) detects a HIGH severity vulnerable dependency being added

The pipeline **reports but does not fail** for:

- Bandit findings (uploaded as SARIF to GitHub Security tab)
- pip-audit / npm-audit findings (informational)
- Checkov findings (informational)
- OSV Scanner findings (informational)

## Security Gate

All security jobs feed into a **Security Gate** summary job that:
- Reports pass/fail status for each scan
- Fails the overall workflow if any critical scan fails
- Generates a summary table visible in the GitHub Actions run

## Deployment Gating

Deploy jobs in `ci-cd.yml` only run on push events (not PRs) to `main` or `develop`. The security pipeline runs in parallel with CI/CD. For production deployments, ensure the security pipeline passes before merging PRs.

## SARIF Results

All SAST and vulnerability scan results are uploaded as SARIF to the GitHub **Security → Code scanning alerts** tab:

- Semgrep results
- CodeQL results
- Bandit results
- Trivy FS/Config/Image results

This provides a unified view of all security findings in the GitHub UI.

## Running Scans Locally

### Gitleaks
```bash
# Install: brew install gitleaks (macOS) or download from GitHub releases
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
# Install: brew install trivy (macOS) or download from GitHub releases

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
# Install: brew install trufflehog (macOS) or download from GitHub releases
trufflehog filesystem --only-verified .
```

## Configuration Files

| File | Purpose |
|------|---------|
| `.gitleaks.toml` | Gitleaks allowlist (test files, env templates) |
| `.github/codeql-config.yml` | CodeQL paths-ignore and query filters |
| `.osv-scanner.toml` | OSV Scanner ignored vulnerabilities |
| `.github/workflows/.trufflehogignore` | TruffleHog exclusion patterns |

## Severity Thresholds

The default failure threshold is set via the `SEVERITY_FAIL` environment variable in the workflow (default: `high`). To change it:

1. Edit `.github/workflows/security.yml`
2. Update `env.SEVERITY_FAIL` to `critical`, `high`, `medium`, or `low`
3. Trivy scans also have their own `severity` parameter

## Adding False Positive Suppressions

- **Gitleaks**: Add entries to `.gitleaks.toml` allowlist
- **TruffleHog**: Add regex patterns to `.github/workflows/.trufflehogignore`
- **Semgrep**: Add `# nosemgrep` inline comment or rules to config
- **CodeQL**: Add to `.github/codeql-config.yml` paths-ignore
- **OSV Scanner**: Add `[[IgnoredVulns]]` entries to `.osv-scanner.toml`
- **Bandit**: Add `# nosec` inline comment

---

*Last updated: 2026-04-13*