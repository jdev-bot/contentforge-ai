# ContentForge AI - Full Security Audit Report

**Date:** 2026-04-13  
**Auditor:** Security Engineer, Neo DevOrg  
**Repository:** `git@github.com:jdev-bot/contentforge-ai.git`  
**Branch:** `main`  
**Tag:** `v2.0.0`

---

## Executive Summary

ContentForge AI has a **MEDIUM** overall security risk. The codebase shows good security practices in most areas (non-root Docker, RLS policies, secret management via env vars) but contains several findings that require attention before production deployment.

**Verdict: SAFE TO RUN LOCALLY WITH CAUTION** — Fix HIGH findings before production.

---

## Step 1: Source Code Inspection

### Findings

| # | Severity | Finding | File | Details |
|---|----------|---------|------|---------|
| 1.1 | LOW | `base64` usage | `app/services/integration_services.py:286-287,406,448` | Used for webhook signature encoding and HTTP Basic Auth — legitimate use cases, not obfuscation |
| 1.2 | **HIGH** | `pickle.dumps/loads` | `app/core/cache.py:60,64` | **CRITICAL**: Pickle deserialization of data from Redis. If Redis is compromised, attacker can achieve RCE via crafted pickle payloads |
| 1.3 | LOW | `re.compile` in extraction | `app/services/extraction_service.py:36` | Normal BeautifulSoup regex usage |
| 1.4 | LOW | `sudo` in backup script | `scripts/backup-database.sh:137` | Runs AWS CLI installer with sudo — expected for system-level install, not in app runtime |
| 1.5 | INFO | HTTP outbound calls | Multiple files | All expected: Supabase, Groq, Stripe, Resend, RSS feeds, webhook endpoints |
| 1.6 | INFO | No `curl|sh` or `wget|bash` | — | No remote code execution patterns found in application code |

---

## Step 2: Git History Secret Scan

### Findings

| # | Severity | Finding | Details |
|---|----------|---------|---------|
| 2.1 | **MEDIUM** | `.env.production` committed | Contains `sk_live_your_stripe_secret_key` and `pk_live_your_stripe_publishable_key` — **placeholder values**, but the file itself should not be in the repo |
| 2.2 | **MEDIUM** | `.env` committed in backend | Contains `test-secret-key-for-local-testing-only` — test values, but `.env` should never be committed |
| 2.3 | **MEDIUM** | `.env.local.example` committed | Contains test Supabase JWT — appears to be a local dev key, not a real secret |
| 2.4 | LOW | Test tokens in test files | `attacker-known-token`, `invalid JWT` tokens — expected in test code |
| 2.5 | INFO | No real API keys found | All `gsk_`, `sk_live_`, `pk_live_` patterns are placeholders (`your_*`, `test-*`, `mock_*`) |

**⚠️ Action Required:** Remove `.env`, `.env.production`, `.env.local.example` from git history. Only `.env.example` and `.env.production.template` should be committed (with placeholder values clearly marked).

---

## Step 3: Dependency Security Analysis

### Backend (Python) — `requirements.txt`

| Dependency | Version | Risk | Notes |
|------------|---------|------|-------|
| fastapi | 0.115.0 | LOW | Well-maintained, widely used |
| uvicorn | 0.32.0 | LOW | Standard ASGI server |
| pydantic | 2.9.2 | LOW | Input validation framework |
| supabase | 2.9.0 | LOW | Official Supabase client |
| groq | 0.12.0 | LOW | Official Groq client |
| python-jose | 3.3.0 | **MEDIUM** | Uses `cryptography` backend — ensure it's not using naive RSA/ECDSA. Consider migrating to PyJWT |
| passlib | 1.7.4 | LOW | bcrypt hashing — secure |
| celery | 5.4.0 | LOW | Standard task queue |
| stripe | 11.3.0 | LOW | Official Stripe SDK |
| resend | 2.4.0 | LOW | Official Resend SDK |
| jinja2 | 3.1.3 | LOW | Template engine — ensure autoescaping enabled |
| feedparser | 6.0.11 | LOW | RSS parsing — some historical CVEs, current version clean |
| pydub | 0.25.1 | LOW | Audio processing |
| youtube-transcript-api | 0.6.2 | LOW | Third-party but widely used |
| requests | 2.32.3 | LOW | Well-maintained HTTP library |
| httpx | 0.27.2 | LOW | Modern async HTTP client |
| beautifulsoup4 | 4.12.3 | LOW | HTML parser |

**No typosquatting detected.** All packages are legitimate, well-known libraries.

### Frontend (Node.js) — `package.json`

| Dependency | Version | Risk | Notes |
|------------|---------|------|-------|
| next | 16.2.3 | LOW | Latest Next.js |
| react | 19.2.4 | LOW | React 19 |
| @supabase/supabase-js | ^2.103.0 | LOW | Official Supabase client |
| framer-motion | ^12.38.0 | LOW | Animation library |
| recharts | ^3.8.1 | LOW | Chart library |
| lucide-react | ^1.8.0 | LOW | Icon library |
| lottie-react | ^2.4.1 | LOW | Animation library |
| jszip | ^3.10.1 | LOW | ZIP library |

**No postinstall/preinstall scripts found.** No typosquatting detected.

---

## Step 4: Static Code Analysis

### Findings

| # | Severity | Finding | File | Details |
|---|----------|---------|------|---------|
| 4.1 | **HIGH** | `dangerouslySetInnerHTML` | `src/frontend/src/components/RSSEntriesPanel.tsx:559` | Renders RSS entry content directly as HTML — **XSS risk** if RSS feed contains malicious scripts |
| 4.2 | LOW | `dangerouslySetInnerHTML` | `src/frontend/src/app/layout.tsx:36` | Used for structured data/JSON-LD — low risk if static |
| 4.3 | **HIGH** | `pickle.loads()` for Redis cache | `src/backend/app/core/cache.py:64` | Deserialization of untrusted data — **RCE risk** if Redis compromised |
| 4.4 | **MEDIUM** | `hashlib.md5()` for cache keys | `src/backend/app/core/cache.py:200` | MD5 used for cache key generation — not for security purposes, but could lead to cache collisions |
| 4.5 | INFO | No SQL injection patterns | — | All database queries use Supabase client (parameterized), no raw SQL string formatting found |
| 4.6 | INFO | No `eval()` or `exec()` | — | No Python `eval()` or `exec()` calls in application code |
| 4.7 | INFO | No `subprocess` with `shell=True` | — | No dangerous subprocess calls found |
| 4.8 | INFO | No `os.system()` | — | No shell command execution found |

---

## Step 5: Configuration & Infrastructure Scan

### Dockerfile (`infra/docker/Dockerfile.backend`)

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| 5.1 | INFO | ✅ Non-root user | `useradd -m -u 1000 appuser` + `USER appuser` |
| 5.2 | INFO | ✅ Health check | `HEALTHCHECK` configured with 30s interval |
| 5.3 | LOW | Slim base image | `python:3.12-slim` — good, minimal attack surface |
| 5.4 | INFO | ✅ No secrets in Dockerfile | No hardcoded credentials |
| 5.5 | INFO | ✅ apt cleanup | `rm -rf /var/lib/apt/lists/*` after install |
| 5.6 | LOW | System packages installed | `gcc`, `libpq-dev`, `ffmpeg`, `libsndfile1` — increases attack surface slightly |

### CI/CD Workflows (`.github/workflows/`)

| # | Severity | Finding | Details |
|---|----------|---------|---------|
| 5.7 | INFO | ✅ Secrets properly referenced | `${{ secrets.VERCEL_TOKEN }}`, `${{ secrets.SUPABASE_URL }}` |
| 5.8 | LOW | `continue-on-error: true` on deploy | Deployment failures won't fail the CI pipeline — could mask issues |
| 5.9 | INFO | ✅ Security scan workflow exists | Bandit, pip-audit, npm audit, TruffleHog configured |
| 5.10 | INFO | ✅ TruffleHog secret detection | Configured with `--only-verified` and `.trufflehogignore` |
| 5.11 | INFO | ✅ Dependency review action | Configured for PR reviews |
| 5.12 | LOW | Security tools run with `|| true` | Bandit and pip-audit results ignored (non-blocking) |

---

## Step 6: Filesystem & Project Scan

### Findings

| # | Severity | Finding | File | Details |
|---|----------|---------|------|---------|
| 6.1 | **MEDIUM** | `.env` file committed | `src/backend/.env` | Contains test keys — should be in `.gitignore` and removed from history |
| 6.2 | **MEDIUM** | `.env.production` committed | `.env.production` | Contains placeholder API keys — file should not be in repo |
| 6.3 | **MEDIUM** | `.env.local.example` committed | `.env.local.example` | Contains test JWT — should be `.env.example` format only |
| 6.4 | INFO | ✅ `.gitignore` configured | `.gitignore` | Properly excludes `node_modules/`, `venv/`, `.env`, `.env.local` |
| 6.5 | INFO | ✅ No real secrets found | — | All detected keys are test/placeholder values |

**Note:** The `.gitignore` file correctly excludes `.env` and `.env.local`, but `.env` and `.env.production` were already committed before being added to `.gitignore`. Git continues tracking committed files.

---

## Step 7: Container Security

### Dockerfile Analysis

| Category | Finding | Risk |
|----------|---------|------|
| Base image | `python:3.12-slim` | ✅ GOOD — minimal Debian-based image |
| User | `appuser` (UID 1000) | ✅ GOOD — non-root |
| Health check | Configured (30s interval) | ✅ GOOD |
| Exposed ports | 8000 (API only) | ✅ GOOD |
| Secrets | None embedded | ✅ GOOD |
| Package cleanup | `rm -rf /var/lib/apt/lists/*` | ✅ GOOD |
| COPY directive | Copies `src/backend/` only | ✅ GOOD — no secret files copied |
| Entrypoint | `uvicorn` with 2 workers | ✅ GOOD |

**Container Security Rating: LOW RISK** ✅

---

## Step 8: Runtime Behavior Analysis

### Expected Network Calls

| Destination | Purpose | Risk |
|-------------|---------|------|
| Supabase (`*.supabase.co`) | Database + Auth | ✅ Expected |
| Groq (`api.groq.com`) | AI content generation | ✅ Expected |
| Stripe (`api.stripe.com`) | Payment processing | ✅ Expected |
| Resend (`api.resend.com`) | Email delivery | ✅ Expected |
| User-configured webhooks | Integration delivery | ⚠️ User-controlled — validate URLs |
| RSS feed URLs | Content import | ⚠️ User-controlled — SSRF risk |

### Findings

| # | Severity | Finding | Details |
|---|----------|---------|---------|
| 8.1 | **MEDIUM** | SSRF risk in RSS import | `rss_service.py` fetches arbitrary URLs — could access internal services if not validated |
| 8.2 | **MEDIUM** | SSRF risk in webhook delivery | `integration_services.py` posts to user-configured URLs |
| 8.3 | LOW | Webhook signature verification | ✅ HMAC-SHA256/SHA512 verification implemented |
| 8.4 | INFO | No crypto mining indicators | No unusual CPU-intensive background tasks |
| 8.5 | INFO | No data exfiltration patterns | All outbound calls are to expected services |

---

## Step 9: Final Risk Assessment

### Risk Summary

| Severity | Count | Findings |
|----------|-------|----------|
| **CRITICAL** | 0 | — |
| **HIGH** | 3 | Pickle deserialization (4.3), XSS via RSS (4.1), Pickle in cache (1.2) |
| **MEDIUM** | 5 | Committed env files (2.1-2.3, 6.1-6.3), SSRF risks (8.1-8.2), MD5 cache keys (4.4), python-jose (3.x) |
| **LOW** | 7 | Base64 usage, Docker packages, CI continue-on-error, cache collisions, etc. |
| **INFO** | 12 | Good practices, expected patterns |

### Top 10 Critical/High Issues

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | **HIGH** | Pickle deserialization in cache | Replace `pickle` with `json` serialization in `cache.py` |
| 2 | **HIGH** | XSS via `dangerouslySetInnerHTML` in RSS | Sanitize RSS HTML with DOMPurify before rendering |
| 3 | **HIGH** | Pickle RCE vector (same as #1) | Use `json.dumps/loads` or `msgpack` instead of `pickle` |
| 4 | **MEDIUM** | `.env` files committed to git | Remove from tracking: `git rm --cached .env .env.production .env.local.example` |
| 5 | **MEDIUM** | `.env.production` in repo | Same as #4 — use `git filter-branch` or BFG to clean history |
| 6 | **MEDIUM** | SSRF risk in RSS import | Validate URLs against allowlist, block private IP ranges |
| 7 | **MEDIUM** | SSRF risk in webhook delivery | Validate webhook URLs, block internal networks |
| 8 | **MEDIUM** | MD5 for cache keys | Replace with `hashlib.sha256` for collision resistance |
| 9 | **MEDIUM** | python-jose for JWT | Consider migrating to `PyJWT` which is more actively maintained |
| 10 | **LOW** | CI security tools non-blocking | Make Bandit/pip-audit fail the pipeline on HIGH findings |

### Recommended Fixes (Priority Order)

1. **Immediate** — Replace `pickle` with `json` in `app/core/cache.py`
2. **Immediate** — Add HTML sanitization (DOMPurify) for RSS content rendering
3. **Before Production** — Remove committed `.env` files from git history
4. **Before Production** — Add SSRF protection to RSS and webhook URL validation
5. **Before Production** — Replace MD5 with SHA-256 for cache key generation
6. **After Launch** — Migrate from `python-jose` to `PyJWT`
7. **After Launch** — Make CI security scans blocking

---

## Final Verdict

### 🟡 SAFE TO RUN LOCALLY WITH CAUTION

**For local development/testing:** ✅ Safe to run. All detected secrets are test/placeholder values. The HIGH findings (pickle, XSS) require specific attack conditions (Redis compromise, malicious RSS feed) that are unlikely in a local dev environment.

**For production deployment:** ❌ Fix HIGH findings first. Specifically:
1. Replace `pickle` with `json` serialization
2. Add HTML sanitization for RSS content
3. Remove `.env` files from git history
4. Add SSRF protections

**Overall Security Score: 7/10**

Good foundation with proper Docker security, RLS policies, secret management, and CI/CD scanning. The HIGH findings are fixable within 1-2 hours of development work.

---

*Report generated 2026-04-13 by Security Engineer, Neo DevOrg*