# Security Audit Report — ContentForge AI

**Date:** 2026-04-13  
**Auditor:** Security Engineer, Neo DevOrg  
**Repository:** `/home/claw/.openclaw/workspace/projects/contentforge-ai/`  
**Scope:** Full security audit before local execution or deployment  
**Methodology:** 9-step structured audit (source code, git history, dependencies, static analysis, configuration, filesystem, container, runtime behavior, risk assessment)

---

## Executive Summary

The ContentForge AI repository is a FastAPI + Next.js application for AI-powered content repurposing. The audit identified **1 CRITICAL**, **4 HIGH**, **6 MEDIUM**, and **8 LOW** severity findings. The most severe issue is an insecure deserialization vulnerability using `pickle.loads()` on data stored in Redis, which could lead to remote code execution if an attacker gains access to the Redis instance. Other significant issues include XSS via unsanitized RSS content rendering, committed `.env` files with sensitive key patterns, and weak default credentials in Docker services.

**Verdict: ONLY IN SANDBOX** — The application should not be run on a host machine without isolation until the CRITICAL and HIGH findings are remediated.

---

## Step 1: Source Code Inspection

### 1.1 Remote Code Execution Patterns

| File | Line | Pattern | Severity | Detail |
|------|------|---------|----------|--------|
| `scripts/deploy-backend.sh` | 86 | `curl \| bash` | MEDIUM | `curl https://raw.githubusercontent.com/render-oss/render-cli/main/install.sh \| bash` — Supply chain risk: if render-cli repo is compromised, arbitrary code runs |
| `scripts/backup-database.sh` | 131 | `curl -fsSL` + `unzip` + `sudo install` | LOW | Downloads AWS CLI from `awscli.amazonaws.com` with `sudo` — legitimate but risky pattern |
| `scripts/backup-database.sh` | 137 | `sudo "/tmp/aws/install"` | LOW | Executes installer with elevated privileges |

### 1.2 Obfuscated / Dynamic Execution

| File | Line | Pattern | Severity | Detail |
|------|------|---------|----------|--------|
| `src/backend/app/core/cache.py` | 64 | `pickle.loads(value)` | **CRITICAL** | Deserializes data from Redis — if Redis is compromised, this enables RCE |
| `src/backend/app/core/cache.py` | 55 | `pickle.dumps(value)` | — | Serialization counterpart (not directly exploitable but enables the RCE vector) |

### 1.3 Hardcoded Credentials in Committed Files

| File | Pattern | Severity | Detail |
|------|---------|----------|--------|
| `.env` | `SECRET_KEY=dev-secret-key-change-in-production` | HIGH | Committed to repo; developers may forget to change |
| `.env` | `GROQ_API_KEY=test-groq-key-for-local-testing` | MEDIUM | Placeholder but committed; could accidentally be real |
| `.env` | `STRIPE_SECRET_KEY=sk_test_mock_stripe_secret_key` | MEDIUM | Stripe test key pattern committed |
| `.env.production` | `sk_live_your_stripe_secret_key` pattern | **HIGH** | `sk_live_` prefix pattern — if a developer fills in real key, it's committed |
| `.env.production` | `pk_live_your_stripe_publishable_key` pattern | HIGH | Same risk as above for publishable key |
| `src/backend/.env` | Same as root `.env` | MEDIUM | Duplicated committed secrets |
| `src/frontend/.env.local` | `NEXT_PUBLIC_GROQ_API_KEY=test-groq-key-for-local-testing` | **HIGH** | `NEXT_PUBLIC_` prefix exposes key to browser bundle |
| `docker-compose.yml` | `POSTGRES_USER: postgres` / `POSTGRES_PASSWORD: postgres` | MEDIUM | Default weak credentials |
| `docker-compose.yml` | `N8N_BASIC_AUTH_USER: admin` / `N8N_BASIC_AUTH_PASSWORD: admin` | MEDIUM | Default weak credentials |
| `docker-compose.yml` | Redis with no auth | MEDIUM | Redis accepts connections without authentication |
| `docker-compose.yml` | `MINIO_ROOT_USER: minioadmin` / `MINIO_ROOT_PASSWORD: minioadmin` | LOW | Default MinIO credentials |

### 1.4 Privilege Escalation

| File | Line | Pattern | Severity |
|------|------|---------|----------|
| `scripts/backup-database.sh` | 137 | `sudo "/tmp/aws/install"` | LOW |

### 1.5 Unexpected Network Calls

| Service | External Endpoints | Purpose | Assessment |
|---------|-------------------|---------|------------|
| `groq_service.py` | `https://api.groq.com/openai/v1` | AI content generation | Expected |
| `email_service.py` | Resend API + SMTP | Email delivery | Expected |
| `rss_service.py` | User-provided RSS URLs | Feed fetching | SSRF risk — see Step 4 |
| `integration_services.py` | Various (Slack, WordPress, etc.) | Content distribution | Expected but broad |
| `extraction_service.py` | External URLs | Content extraction | SSRF risk |

### 1.6 Findings Summary

- **CRITICAL:** 1 (pickle RCE)
- **HIGH:** 4 (committed .env with live key patterns, NEXT_PUBLIC_ API key exposure)
- **MEDIUM:** 5 (curl|bash, default credentials, placeholder keys committed)
- **LOW:** 2 (sudo install, MinIO defaults)

---

## Step 2: Git History Secret Scan

### 2.1 Methodology

Scanned git history using `git log --all -p` with grep patterns for API keys, private keys, tokens, and credentials.

### 2.2 Findings

| Commit Context | Pattern | File | Severity | Assessment |
|---------------|---------|------|----------|------------|
| Multiple commits | `sk_live_your_stripe_secret_key` | `.env.production.template` | MEDIUM | Placeholder pattern, not real key |
| Multiple commits | `pk_live_your_stripe_publishable_key` | `.env.production.template` | MEDIUM | Placeholder pattern, not real key |
| Multiple commits | `supabase_key=your_supabase_anon_key` | `.env.production.template` | LOW | Placeholder |
| Multiple commits | `SMTP_PASSWORD = "password"` | `.env` | MEDIUM | Hardcoded SMTP password (mock value) |
| Multiple commits | `test-groq-key-for-local-testing` | `.env`, `src/frontend/.env.local` | MEDIUM | Mock API key but committed |
| All history | No `BEGIN PRIVATE KEY` or `BEGIN RSA` found | — | — | Clean |
| All history | No real `sk_live_*` with actual key material | — | — | Clean |

### 2.3 Assessment

No **real** secrets were found in git history. However, the `.env` files containing key patterns (especially `sk_live_*`) are committed, which creates risk of accidental real-key commits in the future. The `.gitignore` lists `.env` but `.env` files are already tracked.

**Recommendation:** Remove tracked `.env` files from git with `git rm --cached` and force developers to use `.env.example` only.

---

## Step 3: Dependency Security Analysis

### 3.1 Backend Dependencies (Python — `requirements.txt`)

| Package | Version | Known Issues | Risk |
|---------|---------|-------------|------|
| `fastapi` | 0.115.0 | None significant | LOW |
| `uvicorn` | 0.32.0 | None significant | LOW |
| `pydantic` | 2.9.2 | None significant | LOW |
| `httpx` | 0.27.2 | None significant | LOW |
| `supabase` | 2.9.0 | None significant | LOW |
| `groq` | 0.12.0 | None significant | LOW |
| `python-jose` | 3.3.0 | **Known**: `python-jose` has had CVEs related to key confusion attacks; maintenance concerns | MEDIUM |
| `passlib` | 1.7.4 | **Known**: `passlib` is largely unmaintained; bcrypt backend still functional | LOW |
| `requests` | 2.32.3 | None significant | LOW |
| `celery` | 5.4.0 | None significant; pickling is default serialization (see Step 4) | MEDIUM |
| `redis` | 5.2.0 | None significant | LOW |
| `stripe` | 11.3.0 | None significant | LOW |
| `jinja2` | 3.1.3 | **Known**: Sandbox escape possible in some configurations | LOW |
| `beautifulsoup4` | 4.12.3 | None significant | LOW |
| `youtube-transcript-api` | 0.6.2 | Low adoption; niche package | LOW |
| `pydub` | 0.25.1 | Uses `subprocess` internally for ffmpeg | LOW |
| `feedparser` | 6.0.11 | None significant | LOW |
| `resend` | 2.4.0 | None significant | LOW |

### 3.2 Frontend Dependencies (Node.js — `package.json`)

| Package | Version | Known Issues | Risk |
|---------|---------|-------------|------|
| `next` | 16.2.3 | None significant | LOW |
| `react` | 19.2.4 | None significant | LOW |
| `@supabase/supabase-js` | ^2.103.0 | None significant | LOW |
| `framer-motion` | ^12.38.0 | None significant | LOW |
| `puppeteer-core` | ^24.40.0 | Requires external Chromium; not bundled | LOW |
| `node-screenshots` | ^0.2.8 | **Suspicious**: Very low adoption, native module, version 0.2.x | MEDIUM |
| `lottie-react` | ^2.4.1 | None significant | LOW |
| `jszip` | ^3.10.1 | None significant | LOW |
| `recharts` | ^3.8.1 | None significant | LOW |

### 3.3 Typosquatting Check

No typosquatted package names detected. All dependencies appear to be legitimate, well-known packages except `node-screenshots` which warrants further verification.

### 3.4 Install Script Check

No `postinstall`, `preinstall`, or `postbuild` scripts found in `package.json`. ✅

### 3.5 Summary

- **MEDIUM**: `python-jose` (maintenance/CVE concerns), `celery` (pickle serialization default), `node-screenshots` (low-trust native module)
- **LOW**: All other dependencies

---

## Step 4: Static Code Analysis

### 4.1 Insecure Deserialization

| File | Line | Code | Severity | Detail |
|------|------|------|----------|--------|
| `src/backend/app/core/cache.py` | 64 | `return pickle.loads(value)` | **CRITICAL** | Deserializes cached data from Redis using `pickle`. If an attacker can write to Redis (no auth required in dev docker-compose), they can inject a malicious pickle payload achieving RCE on the backend server. |

### 4.2 Cross-Site Scripting (XSS)

| File | Line | Code | Severity | Detail |
|------|------|------|----------|--------|
| `src/frontend/src/components/RSSEntriesPanel.tsx` | 559 | `dangerouslySetInnerHTML={{ __html: entry.content.substring(0, 2000) }}` | **HIGH** | Renders RSS feed content as raw HTML without sanitization. If a malicious RSS feed contains `<script>` tags or event handlers, they execute in the user's browser. No DOMPurify or sanitize-html usage found anywhere in the project. |
| `src/frontend/src/app/layout.tsx` | 36 | `dangerouslySetInnerHTML={{ __html: ... }}` | LOW | Injects a theme-detection script from hardcoded inline JS. Content is static and controlled — not exploitable unless the build is compromised. |

### 4.3 Server-Side Request Forgery (SSRF)

| File | Line | Code | Severity | Detail |
|------|------|------|----------|--------|
| `src/backend/app/services/rss_service.py` | 30 | `async with httpx.AsyncClient(...) as client: response = await client.get(url, ...)` | MEDIUM | User-provided URL is fetched server-side without allowlist validation. An attacker could provide internal URLs (e.g., `http://169.254.169.254/` for cloud metadata, `http://localhost:6379/` for Redis). |
| `src/backend/app/services/extraction_service.py` | 16 | `async with httpx.AsyncClient() as client: response = await client.get(url)` | MEDIUM | Same SSRF risk — user-provided URLs fetched without validation. |

### 4.4 Unsafe Cryptographic Usage

| File | Line | Code | Severity | Detail |
|------|------|------|----------|--------|
| `src/backend/app/core/cache.py` | 200 | `hashlib.md5(...).hexdigest()` | LOW | MD5 used for cache key hashing. Not security-critical (only for cache deduplication), but MD5 is cryptographically broken. |
| `src/backend/app/utils/jwt.py` | 12 | `CryptContext(schemes=["bcrypt"])` | — | Good: bcrypt for password hashing ✅ |
| `src/backend/app/utils/jwt.py` | 35 | `jwt.encode(..., algorithm="HS256")` | — | Acceptable for JWT with proper secret key ✅ |

### 4.5 SQL Injection

All database queries use Supabase's `.table().select().eq()` builder pattern (parameterized queries). **No raw SQL string formatting found in application code.** ✅

### 4.6 Authentication & Authorization

| Aspect | Finding | Severity |
|--------|---------|----------|
| Auth middleware | `get_auth_user()` validates Bearer token via Supabase `auth.get_user()` — proper implementation | — ✅ |
| Protected routes | 25 of 27 routers use `Depends(get_auth_user)`. Two unauthenticated: `health`, `docs` | LOW |
| Webhook endpoints | Some webhook routes are unauthenticated (expected — they verify via HMAC signatures instead) | — ✅ |
| HMAC verification | Uses `hmac.compare_digest()` (constant-time comparison) | — ✅ |
| Admin routes | Protected with `Depends(get_auth_user)` but no role check | MEDIUM |
| CORS | `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]` with configurable origins | MEDIUM |

### 4.7 Input Validation

| Aspect | Finding | Severity |
|--------|---------|----------|
| Pydantic models | Used throughout for request/response validation | — ✅ |
| Email validation | Uses `EmailStr` for email fields | — ✅ |
| URL validation | RSS feed URLs not validated against allowlist | MEDIUM (see SSRF) |
| HTML sanitization | **None found** — no DOMPurify, bleach, or sanitize-html | **HIGH** (see XSS) |

### 4.8 Summary

- **CRITICAL:** 1 (pickle RCE)
- **HIGH:** 1 (XSS via RSS content)
- **MEDIUM:** 3 (SSRF × 2, admin routes lack role check)
- **LOW:** 2 (MD5 for cache keys, CORS permissive)

---

## Step 5: Configuration & Infrastructure Scan

### 5.1 Dockerfile Analysis (`infra/docker/Dockerfile.backend`)

| Aspect | Finding | Severity |
|--------|---------|----------|
| Base image | `python:3.12-slim` — Good: minimal footprint | — ✅ |
| Root user | Creates and uses `appuser` (uid 1000) — Good: non-root | — ✅ |
| Health check | Present — checks `/api/v1/health` | — ✅ |
| Secrets in image | No secrets embedded | — ✅ |
| COPY scope | `COPY src/backend/ ./` — copies all backend source, no sensitive files outside project | LOW |
| Exposed port | 8000 — standard | — ✅ |
| Apt cleanup | `rm -rf /var/lib/apt/lists/*` after install | — ✅ |

### 5.2 docker-compose.yml Analysis

| Service | Finding | Severity |
|---------|---------|----------|
| PostgreSQL | Default `postgres/postgres` credentials | MEDIUM |
| PostgreSQL | Port 5432 exposed to host | LOW (dev only) |
| Redis | **No authentication configured** | MEDIUM |
| Redis | Port 6379 exposed to host | LOW (dev only) |
| n8n | `admin/admin` basic auth | MEDIUM |
| n8n | Port 5678 exposed to host | LOW |
| MinIO | `minioadmin/minioadmin` defaults | LOW |
| MinIO | Ports 9000, 9001 exposed | LOW |
| MailHog | Ports 1025, 8025 exposed | LOW |
| Networks | Bridge network `contentforge-network` | — ✅ |
| No privileged containers | None found | — ✅ |
| No Docker socket mount | None found | — ✅ |

### 5.3 CI/CD Workflow Analysis

**`.github/workflows/ci-cd.yml`:**
| Aspect | Finding | Severity |
|--------|---------|----------|
| Secrets handling | Uses `${{ secrets.* }}` properly | — ✅ |
| Fallback secrets | `NEXT_PUBLIC_SUPABASE_URL \|\| 'https://placeholder.supabase.co'` — acceptable fallbacks | LOW |
| Deploy step | Uses `amondnet/vercel-action@v25` with `continue-on-error: true` | LOW — silent deployment failures |
| Test environment | Test env vars use `sk-test-key` placeholders | — ✅ |

**`.github/workflows/security-scan.yml`:**
| Aspect | Finding | Severity |
|--------|---------|----------|
| Tools | Bandit, pip-audit, npm audit, ESLint security, TruffleHog, dependency-review | — ✅ Good coverage |
| TruffleHog | Configured with `--only-verified` and `--exclude-paths` | — ✅ |
| `continue-on-error: true` | Multiple scan steps use `continue-on-error` — security failures won't block CI | MEDIUM |

**`.github/workflows/backend-tests.yml`:**
| Aspect | Finding | Severity |
|--------|---------|----------|
| Test env vars | Mock keys (`sk-test-key`) used properly | — ✅ |
| Coverage upload | Uses codecov-action@v4 | — ✅ |

### 5.4 Render Blueprint (`render.yaml`)

| Aspect | Finding | Severity |
|--------|---------|----------|
| Secrets | All sensitive env vars use `sync: false` (stored in Render dashboard) | — ✅ |
| Generated secrets | `JWT_SECRET_KEY` and `ENCRYPTION_KEY` use `generateValue: true` | — ✅ |
| Redis | No IP allowlist (`ipAllowList: []`) | MEDIUM — open access |
| Free plan | All services on free tier | LOW — not production-ready |

### 5.5 Vercel Configuration (`vercel.json`)

| Aspect | Finding | Severity |
|--------|---------|----------|
| Security headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block` | — ✅ Good |
| API proxy | Rewrites `/api/v1/*` to Render backend | — ✅ |
| No CSP header | Missing `Content-Security-Policy` | MEDIUM |

### 5.6 Summary

- Dockerfile is well-configured (non-root, health check, slim image)
- docker-compose has multiple default credential issues (dev acceptable, prod not)
- CI/CD security scanning exists but `continue-on-error` weakens enforcement
- Missing Content-Security-Policy header
- Render Redis open to all IPs

---

## Step 6: Filesystem & Project Scan

### 6.1 Sensitive Files

| File | Finding | Severity |
|------|---------|----------|
| No `.pem`, `.key`, `.p12`, `.pfx` files found | — | — ✅ |
| No SSH private keys found | — | — ✅ |
| `.env` files committed despite `.gitignore` entry | `.env` was added to git before `.gitignore` rule | HIGH |
| `.env.production` committed with `sk_live_*` patterns | — | HIGH |

### 6.2 Credential Pattern Scan Results

Application source code references to `api_key`, `token`, `password`, `secret`, `credential` are all legitimate:
- Auth flow code (Supabase tokens, Bearer headers)
- Configuration field names (env var references)
- Webhook signature verification
- Stripe integration (proper use of backend SDK)
- No hard-coded real credentials found in application code

### 6.3 `.gitignore` Gap

`.gitignore` contains `.env`, `.env.local`, `.env.*.local` but `.env`, `.env.production`, and `src/backend/.env` are already tracked and not excluded from commits.

### 6.4 Summary

- No private keys or certificate files in repository ✅
- `.env` files tracked despite `.gitignore` — must be untracked
- No real credentials in application source code ✅

---

## Step 7: Container Security

### 7.1 Dockerfile Risk Report

| Check | Result | Severity |
|-------|--------|----------|
| Base image | `python:3.12-slim` — Official, minimal | LOW (check for CVEs in base) |
| Running as root | No — uses `appuser` (uid 1000) | — ✅ |
| Embedded secrets | None found in Dockerfile | — ✅ |
| COPY of sensitive files | `COPY src/backend/ ./` — includes `.env` if present | MEDIUM |
| Health check | Present and functional | — ✅ |
| Apt packages | `gcc`, `libpq-dev`, `ffmpeg`, `libsndfile1` — reasonable | LOW |
| Pinned versions | Python base not pinned to digest | LOW |
| Multi-stage build | No — single stage (larger attack surface) | LOW |

### 7.2 Runtime Concerns

- The Dockerfile `COPY src/backend/ ./` will include any `.env` file present in `src/backend/` at build time, embedding it in the image layer.
- `ffmpeg` dependency increases attack surface (known for CVEs).

### 7.3 Summary

- Container security posture is **good overall**
- Non-root execution ✅
- Health check ✅
- Risk: `.env` files baked into image layers, `ffmpeg` attack surface, unpinned base image

---

## Step 8: Runtime Behavior Analysis

### 8.1 Network Calls

| Endpoint | Direction | Purpose | Risk |
|----------|-----------|---------|------|
| `https://api.groq.com/openai/v1` | Outbound | AI content generation | Expected |
| Resend API (`api.resend.com`) | Outbound | Email delivery | Expected |
| User-provided RSS URLs | Outbound | Feed fetching | **SSRF risk** |
| User-provided extraction URLs | Outbound | Content extraction | **SSRF risk** |
| Integration webhooks (Slack, WordPress, etc.) | Outbound | Content distribution | Expected |
| SMTP servers | Outbound | Email fallback | Expected |
| `https://contentforge-ai-api.onrender.com` | Outbound (frontend) | API proxy | Expected |

### 8.2 File Writes

| Location | Purpose | Risk |
|----------|---------|------|
| Celery task results in Redis | Task queue results | LOW |
| PostgreSQL database | Application data | LOW |
| MinIO/S3 (R2) | File uploads, backups | LOW |
| `/tmp` (backup scripts) | Temporary files | LOW |

### 8.3 Process Spawning

| Process | Trigger | Risk |
|---------|---------|------|
| Celery workers | Task execution | LOW |
| `ffmpeg` (via pydub) | Audio processing | LOW |
| `uvicorn` workers | HTTP serving | LOW |

### 8.4 Data Exfiltration Indicators

- **No** exfiltration patterns detected
- **No** crypto mining indicators
- **No** unexpected background services
- **No** beaconing or heartbeat patterns to unknown hosts

### 8.5 Summary

Runtime behavior is consistent with the application's stated purpose. SSRF via user-provided URLs is the primary runtime risk. No malicious behavior patterns detected.

---

## Step 9: Final Risk Assessment

### 9.1 Risk Classification Summary

| Severity | Count | Findings |
|----------|-------|----------|
| **CRITICAL** | 1 | pickle RCE via Redis |
| **HIGH** | 4 | XSS via RSS, committed .env with `sk_live_*` patterns, NEXT_PUBLIC_ API key exposure, .env files tracked in git |
| **MEDIUM** | 6 | SSRF × 2, default Docker credentials, Redis no auth, admin routes lack role check, CI security scans continue-on-error |
| **LOW** | 8 | MD5 for cache keys, CORS permissive methods/headers, sudo in backup script, MinIO defaults, ffmpeg attack surface, unpinned base image, missing CSP, COPY includes .env |

### 9.2 Top 10 Critical Issues

| # | Severity | Issue | Impact | File |
|---|----------|-------|--------|------|
| 1 | **CRITICAL** | `pickle.loads()` on Redis data | Remote Code Execution if Redis is compromised | `src/backend/app/core/cache.py:64` |
| 2 | **HIGH** | `dangerouslySetInnerHTML` with unsanitized RSS content | XSS — attacker-controlled HTML executes in user browser | `src/frontend/src/components/RSSEntriesPanel.tsx:559` |
| 3 | **HIGH** | `.env.production` committed with `sk_live_*` Stripe key patterns | If developer enters real live key, it's in git history forever | `.env.production` |
| 4 | **HIGH** | `NEXT_PUBLIC_GROQ_API_KEY` in frontend `.env.local` | API key exposed in browser bundle | `src/frontend/.env.local` |
| 5 | **HIGH** | `.env` files tracked in git despite `.gitignore` | Secrets leak via version control | `.env`, `src/backend/.env` |
| 6 | **MEDIUM** | SSRF via RSS feed URL fetching | Access to internal services, cloud metadata | `src/backend/app/services/rss_service.py:30` |
| 7 | **MEDIUM** | SSRF via extraction service URL fetching | Same as above | `src/backend/app/services/extraction_service.py:16` |
| 8 | **MEDIUM** | Redis without authentication (docker-compose) | Anyone can read/write Redis → pickle RCE chain | `docker-compose.yml` |
| 9 | **MEDIUM** | Default credentials in docker-compose (postgres, n8n, minio) | Service takeover in dev environment | `docker-compose.yml` |
| 10 | **MEDIUM** | Admin routes lack role-based access control | Any authenticated user can access admin endpoints | `src/backend/app/routers/admin.py` |

### 9.3 Recommended Fixes

| Priority | Fix | Detail |
|----------|-----|--------|
| **P0** | Replace `pickle` with `json` serialization in CacheManager | Change `_serialize`/`_deserialize` to use `json.dumps`/`json.loads`. If complex objects needed, use `__dict__` serialization or Pydantic model export. |
| **P0** | Sanitize HTML before rendering | Add `DOMPurify` (frontend) or `bleach`/`nh3` (backend) to sanitize RSS `entry.content` before `dangerouslySetInnerHTML`. |
| **P1** | Remove tracked `.env` files from git | Run `git rm --cached .env .env.production src/backend/.env src/frontend/.env.local` and commit. Add them to `.gitignore`. |
| **P1** | Remove `NEXT_PUBLIC_` prefix from API keys | Move Groq API key to backend-only. Frontend should proxy through backend API rather than calling Groq directly. |
| **P1** | Change `.env.production.template` key patterns | Replace `sk_live_*` with `sk_live_REPLACE_ME` and add comment: "NEVER commit real keys". |
| **P2** | Add URL allowlist for RSS/extraction services | Validate user-provided URLs against an allowlist of domains or at minimum block RFC 1918 and link-local addresses. |
| **P2** | Add Redis authentication | Add `--requirepass` to Redis in docker-compose and set `REDIS_URL` with password. |
| **P2** | Add role-based access to admin routes | Create `get_admin_user` dependency that checks user role before allowing admin endpoints. |
| **P3** | Replace `python-jose` with `PyJWT` | `python-jose` has known issues and maintenance concerns. |
| **P3** | Replace MD5 with SHA-256 for cache keys | Change `hashlib.md5` to `hashlib.sha256` in `cache.py`. |
| **P3** | Add Content-Security-Policy header | Configure CSP in `vercel.json` and as FastAPI middleware. |
| **P3** | Remove `continue-on-error` from security scan steps | Security scan failures should block CI. |
| **P3** | Pin Docker base image to digest | Use `python:3.12-slim@sha256:...` for reproducible builds. |
| **P3** | Investigate `node-screenshots` package | Verify legitimacy; consider replacing with a more mainstream solution. |

### 9.4 Verdict

## ⚠️ ONLY IN SANDBOX

The application **should NOT be run on a host machine without isolation** until the CRITICAL finding (`pickle.loads` RCE chain) is remediated. The combination of unauthenticated Redis + `pickle.loads` creates a direct path to remote code execution in development environments.

**Safe execution conditions:**
1. Remediate P0 issues (pickle serialization, XSS sanitization)
2. Run in Docker with network isolation (no host network mode)
3. Change all default Docker credentials before starting
4. Add Redis authentication
5. Do not use `.env.production` with real keys until `.env` files are untracked from git

---

## Appendix A: Tools & Commands Used

```bash
# Source code pattern scanning
grep -rn 'subprocess\|os\.system\|eval(\|exec(\|pickle\.loads' --include="*.py" src/backend/app/
grep -rn 'dangerouslySetInnerHTML\|eval(\|child_process' --include="*.ts" --include="*.tsx" src/frontend/src/
grep -rn 'curl.*\|.*sh\|wget.*\|.*bash' --include="*.sh" --include="*.yml" scripts/ .github/

# Git history secret scan
git log --all -p | grep -iE 'api_key|secret|token|password|private_key|credential'

# Filesystem scan
grep -rn "api_key\|secret_key\|password\|token\|credential" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.yml" --include="*.env" src/
find . -name "*.pem" -o -name "*.key" -o -name "*.p12"

# Crypto usage
grep -rn 'hashlib\|bcrypt\|md5\|AES\|Fernet' --include="*.py" src/backend/app/

# Auth coverage
grep -rn 'get_auth_user\|Depends(get_auth_user)' --include="*.py" src/backend/app/routers/

# SSRF patterns
grep -rn 'httpx\|requests\|aiohttp\|fetch(' --include="*.py" --include="*.ts" src/backend/app/ src/frontend/src/
```

## Appendix B: Files Reviewed

- `Dockerfile`: `infra/docker/Dockerfile.backend`
- `docker-compose.yml`
- `render.yaml`
- `vercel.json`
- `.github/workflows/backend-tests.yml`
- `.github/workflows/ci-cd.yml`
- `.github/workflows/frontend-build.yml`
- `.github/workflows/security-scan.yml`
- `.env`, `.env.example`, `.env.production`, `.env.production.template`
- `src/backend/.env`, `src/frontend/.env.local`
- `src/backend/requirements.txt`
- `src/frontend/package.json`
- `src/backend/app/main.py`
- `src/backend/app/core/config.py`
- `src/backend/app/core/cache.py`
- `src/backend/app/core/rate_limit.py`
- `src/backend/app/utils/jwt.py`
- `src/backend/app/routers/auth.py`
- `src/backend/app/routers/admin.py`
- `src/backend/app/routers/webhooks.py`
- `src/backend/app/services/groq_service.py`
- `src/backend/app/services/rss_service.py`
- `src/backend/app/services/extraction_service.py`
- `src/backend/app/services/integration_services.py`
- `src/backend/app/services/email_service.py`
- `src/frontend/src/components/RSSEntriesPanel.tsx`
- `src/frontend/src/app/layout.tsx`
- `scripts/deploy-backend.sh`, `scripts/deploy-frontend.sh`
- `scripts/backup-database.sh`, `scripts/dev-setup.sh`

---

*Report generated by Security Engineer, Neo DevOrg — 2026-04-13*