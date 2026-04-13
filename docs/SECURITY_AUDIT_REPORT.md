# ContentForge AI — Full Security Audit Report

**Date:** 2026-04-13  
**Auditor:** Security Engineer (Neo DevOrg)  
**Repository:** `/home/claw/.openclaw/workspace/projects/contentforge-ai/`  
**Branch:** main  

---

## Executive Summary

A comprehensive 9-step security audit was performed on the ContentForge AI codebase — a Next.js frontend + Python/FastAPI backend application with Stripe payments, Supabase authentication, Groq AI, Redis caching, Celery background tasks, and n8n workflow integration.

**Overall Verdict: ⚠️ SANDBOX ONLY** — The application is safe for local development and testing with mock credentials. It must **NOT** be deployed to production until the HIGH and CRITICAL issues below are resolved. No real API keys or credentials were found leaked in the repository.

| Risk Level | Count |
|-----------|-------|
| CRITICAL  | 2     |
| HIGH      | 4     |
| MEDIUM    | 5     |
| LOW       | 5     |
| INFO      | 4     |

---

## Step 1: Source Code Inspection

### 1.1 Remote Code Execution Patterns

**Scan:** `grep -rn "curl.*|.*sh|wget.*|.*bash|eval(|exec(|base64|subprocess" --include="*.py" --include="*.js" --include="*.ts" --include="*.sh" src/ infra/`

**Findings:**
- No `eval()` or `exec()` calls in backend application code
- No `subprocess` with `shell=True` in application code
- `base64` usage found only in `src/backend/app/services/integration_services.py` — used for HMAC signature generation and HTTP Basic Auth encoding. **Legitimate use.** (INFO)
- No shell injection vectors detected

### 1.2 Obfuscated Code

**Scan:** `grep -rn "base64|encode|decode|marshal|pickle" --include="*.py" src/`

**Findings:**
- `pickle.loads` found in `src/backend/app/core/cache.py:64` — **[HIGH] SEE FINDING C1**
- `base64` usage in `integration_services.py` — legitimate HMAC/Basic Auth (INFO)
- `.encode()` / `.decode()` calls in test files for HMAC signature verification (INFO)

### 1.3 Hardcoded Credentials

**Scan:** `grep -rn "password\s*=\s*['\"][^'\"]+['\"]|api_key\s*=\s*['\"][^'\"]+['\"]|secret\s*=\s*['\"][^'\"]+['\"]" --include="*.py" --include="*.ts" --include="*.js" --include="*.env" src/`

**Findings:**
- No real hardcoded credentials in application source code
- All credentials in `.env` files are test/mock placeholders (`test-secret-key-for-local-testing`, `sk_test_mock_*`, `test-groq-key-for-local-testing`)
- `docker-compose.yml` contains hardcoded credentials — **[MEDIUM] SEE FINDING M1**

### 1.4 Unexpected Outbound Network Calls

**Scan:** `grep -rn "requests\.\(get\|post\)|httpx\.|fetch(" src/`

**Findings:**
- Frontend: All `fetch()` calls target `API_URL` (backend API) — expected (INFO)
- Backend: `httpx` used in integration services for webhook calls — expected (INFO)
- Backend: `requests` library present in requirements.txt but no direct `requests.get/post` calls found in app code
- All external API calls (Supabase, Groq, Stripe, Resend) use official SDKs with keys from environment variables — **Good practice** (INFO)

### 1.5 Privilege Escalation

**Scan:** `grep -rn "sudo|chmod 777|chown root"`

**Findings:**
- `sudo` found only in `scripts/backup-database.sh:137` — used for AWS CLI installation script. **[LOW] SEE FINDING L1**

### 1.6 Critical File Inspection

| File | Status | Notes |
|------|--------|-------|
| `infra/docker/Dockerfile.backend` | ✅ Good | Non-root user, health check, slim base image |
| `.github/workflows/ci-cd.yml` | ⚠️ | Uses secrets properly, but `continue-on-error: true` on deploy steps |
| `.github/workflows/frontend-build.yml` | ✅ | Secrets with fallback placeholders |
| `.github/workflows/security-scan.yml` | ✅ | TruffleHog, Bandit, pip-audit, npm audit configured |
| `src/frontend/package.json` | ✅ | No postinstall/preinstall scripts |
| `src/backend/requirements.txt` | ⚠️ | See Step 3 dependency analysis |

---

## Step 2: Git History Secret Scan

### 2.1 Secret Pattern Scan

**Scan:** `git log --all -p | grep -iE "(sk_live|sk_test|pk_live|gsk_|xai-|BEGIN PRIVATE KEY|...)"`

**Findings:**
- **No real API keys found.** All `sk_live_*`, `pk_live_*`, and `gsk_*` patterns in git history are placeholders (`your_stripe_secret_key`, `your_api_key`, `••••••••` masked values).
- `.env.production` was committed to the repository with placeholder template values (e.g., `sk_live_your_stripe_secret_key`) — **[MEDIUM] SEE FINDING M2**
- Test files contain mock tokens (`attacker-known-token`, `eyJ...invalid_signature`) — these are test fixtures (INFO)

### 2.2 `.env` Files in Git History

**Scan:** `git log --all --name-only | grep "\.env"`

**Findings:**
The following `.env` files have been tracked in git history:
- `.env.production` — **[MEDIUM]** Contains template placeholder keys, but should not be committed
- `.env.example` — Acceptable (template with no real values)
- `.env.local.example` — Acceptable (template with no real values)
- `.env.production.template` — Acceptable (template)

**Current `.gitignore`** properly excludes `.env`, `.env.local`, `.env.*.local`, `*.key`, `*.pem`, `*.cert`, `*.pfx`, `*.p12`. However, `.env.production` is already tracked.

---

## Step 3: Dependency Security Analysis

### 3.1 Backend Dependencies (`src/backend/requirements.txt`)

| Package | Version | Risk Assessment |
|---------|---------|----------------|
| `fastapi` | 0.115.0 | ✅ Trusted, well-maintained |
| `uvicorn` | 0.32.0 | ✅ Trusted |
| `pydantic` | 2.9.2 | ✅ Trusted |
| `pydantic-settings` | 2.6.1 | ✅ Trusted |
| `httpx` | 0.27.2 | ✅ Trusted |
| `python-multipart` | 0.0.17 | ✅ Trusted |
| `supabase` | 2.9.0 | ✅ Official SDK |
| `groq` | 0.12.0 | ✅ Official SDK |
| `python-jose[cryptography]` | 3.3.0 | ⚠️ **[MEDIUM]** Unmaintained since 2020; no PyPI release since 2021. Known edge cases with key validation. Recommend migration to `PyJWT` or `python-jose` replacement |
| `passlib[bcrypt]` | 1.7.4 | ⚠️ **[LOW]** Stale but functional; `bcrypt` backend is still maintained |
| `python-dotenv` | 1.0.1 | ✅ Trusted |
| `requests` | 2.32.3 | ✅ Trusted |
| `beautifulsoup4` | 4.12.3 | ✅ Trusted |
| `youtube-transcript-api` | 0.6.2 | ⚠️ **[LOW]** Third-party, single maintainer. Verify before updates |
| `pydub` | 0.25.1 | ⚠️ **[LOW]** Requires ffmpeg (pulled into Docker image). No major CVEs |
| `celery` | 5.4.0 | ✅ Trusted, well-maintained |
| `redis` | 5.2.0 | ✅ Official SDK |
| `stripe` | 11.3.0 | ✅ Official SDK |
| `resend` | 2.4.0 | ✅ Official SDK |
| `pytest` / `pytest-asyncio` | 8.0.0 / 0.23.5 | ✅ Dev only |
| `email-validator` | 2.1.0 | ✅ Trusted |
| `jinja2` | 3.1.3 | ✅ Trusted (ensure not used for untrusted templates) |
| `pytz` | 2024.1 | ✅ Trusted |
| `feedparser` | 6.0.11 | ✅ Trusted |

### 3.2 Frontend Dependencies (`src/frontend/package.json`)

| Package | Version | Risk Assessment |
|---------|---------|----------------|
| `next` | 16.2.3 | ✅ Trusted, latest |
| `react` / `react-dom` | 19.2.4 | ✅ Trusted |
| `@supabase/supabase-js` | ^2.103.0 | ✅ Official SDK |
| `@supabase/auth-ui-react` | ^0.4.7 | ✅ Official |
| `framer-motion` | ^12.38.0 | ✅ Trusted |
| `recharts` | ^3.8.1 | ✅ Trusted |
| `jszip` | ^3.10.1 | ✅ Trusted |
| `lottie-react` | ^2.4.1 | ✅ Low-risk |
| `lucide-react` | ^1.8.0 | ✅ Trusted (icon library) |
| `clsx` | ^2.1.1 | ✅ Trusted |
| `tailwind-merge` | ^3.5.0 | ✅ Trusted |
| `puppeteer-core` | ^24.40.0 (dev) | ⚠️ **[LOW]** Dev dependency, not bundled |
| `node-screenshots` | ^0.2.8 (dev) | ⚠️ **[LOW]** Dev dependency, native module |

**No postinstall/preinstall scripts** found in `package.json`. ✅

### 3.3 Typosquatting Assessment
No evidence of typosquatting. All packages are well-known, official SDKs, or widely-used community packages.

---

## Step 4: Static Code Analysis

### 4.1 Python Dangerous Patterns

**Scan:** `grep -rn "eval(|exec(|subprocess.*shell=True|os.system(|pickle.loads|yaml.load(" --include="*.py" src/backend/app/`

**Findings:**
- `pickle.loads` in `src/backend/app/core/cache.py:64` — **[CRITICAL] SEE FINDING C1**
- No `eval()`, `exec()`, `os.system()`, or `subprocess` with `shell=True` found

### 4.2 SQL Injection Patterns

**Scan:** `grep -rn "f\".*SELECT|f\".*INSERT|f\".*UPDATE|f\".*DELETE|.format.*SELECT|%s.*SELECT" --include="*.py" src/`

**Findings:**
- **No SQL injection patterns found.** The application uses Supabase client SDK with parameterized queries, not raw SQL. ✅

### 4.3 TypeScript Dangerous Patterns

**Scan:** `grep -rn "dangerouslySetInnerHTML|eval(|Function(|child_process" --include="*.ts" --include="*.tsx" src/frontend/src/`

**Findings:**
- `dangerouslySetInnerHTML` in `src/frontend/src/components/RSSEntriesPanel.tsx:559` — renders `entry.content` from RSS feeds **[HIGH] SEE FINDING H2**
- `dangerouslySetInnerHTML` in `src/frontend/src/app/layout.tsx:36` — used for theme initialization script (inline `<script>`) — **[LOW] SEE FINDING L2**
- No `eval()`, `Function()`, or `child_process` usage found

### 4.4 Unsafe Cryptography

**Scan:** `grep -rn "hashlib.md5|hashlib.sha1|DES|RC4|math.random" --include="*.py" --include="*.ts" src/`

**Findings:**
- `hashlib.md5` in `src/backend/app/core/cache.py:200` — used for generating cache keys from function arguments. **[MEDIUM] SEE FINDING M3** — MD5 is cryptographically broken; while cache key generation is low-risk, collision attacks could cause cache poisoning
- No `hashlib.sha1`, `DES`, `RC4`, or `math.random` used for security purposes

---

## Step 5: Configuration & Infrastructure Scan

### 5.1 Docker Compose (`docker-compose.yml`)

**Findings:**

| Finding | Risk | ID |
|---------|------|----|
| PostgreSQL credentials `postgres:postgres` hardcoded | MEDIUM | M1 |
| n8n basic auth `admin:admin` hardcoded | MEDIUM | M4 |
| Redis has **no authentication** — no `requirepass` configured | HIGH | H3 |
| n8n shares the same PostgreSQL database (`contentforge`) as the main app | MEDIUM | M5 |
| MinIO credentials `minioadmin:minioadmin` hardcoded | LOW | L3 |
| All services expose ports to host (`5432`, `6379`, `5678`, `9000`, `9001`, `1025`, `8025`) | LOW | L4 |

### 5.2 CI/CD Workflows

**`.github/workflows/ci-cd.yml`:**
- Uses `${{ secrets.* }}` for Vercel deployment — ✅ proper secret management
- `continue-on-error: true` on both deploy steps — **[LOW] SEE FINDING L5** — failed deployments silently pass
- No `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` secrets exposed (earlier concern was from a different workflow that has test fallbacks)

**`.github/workflows/security-scan.yml`:**
- TruffleHog secret scanning with `--only-verified` — ✅
- Bandit (Python linter) configured — ✅
- pip-audit configured — ✅
- npm audit configured — ✅
- `.trufflehogignore` excludes test directories and `.env.local` — reasonable (INFO)

**`.github/workflows/frontend-build.yml`:**
- Build uses secrets with fallback placeholders — ✅
- Build artifacts uploaded with 7-day retention — ✅

### 5.3 Kubernetes Manifests
No Kubernetes manifests found in repository.

---

## Step 6: Filesystem & Project Scan

**Scan:** `grep -rn "api_key|secret_key|password|token|credential|private_key" src/`

**Findings:**
- No real credentials, API keys, or secrets found in source code
- All authentication flows use environment variables via `settings` (Pydantic Settings)
- Stripe secret key read from `settings.STRIPE_SECRET_KEY` — ✅
- Groq API key read from `settings.GROQ_API_KEY` — ✅
- Supabase keys read from environment — ✅
- Frontend exposes `NEXT_PUBLIC_GROQ_API_KEY` as `NEXT_PUBLIC_` env var — **[HIGH] SEE FINDING H4**
- Frontend `SettingsTab.tsx` displays masked API key placeholders (`pk_live_••••`, `gsk_•••••`) — **[MEDIUM] SEE FINDING M6**

---

## Step 7: Container Security

### 7.1 Dockerfile Analysis (`infra/docker/Dockerfile.backend`)

| Check | Status | Notes |
|-------|--------|-------|
| Base image | ✅ Good | `python:3.12-slim` — minimal, trusted, current |
| Root user | ✅ Good | Creates and uses `appuser` (uid 1000) |
| COPY of sensitive files | ✅ | Only copies `requirements.txt` and `src/backend/` |
| Exposed ports | ✅ | Only port `8000` (FastAPI) |
| Health check | ✅ | HTTP health check every 30s |
| System deps | ✅ | `gcc`, `libpq-dev`, `ffmpeg`, `libsndfile1` — all needed |
| Apt cache cleanup | ✅ | `rm -rf /var/lib/apt/lists/*` |
| Multi-stage build | ❌ | Not used — **[LOW] SEE FINDING L6** — larger image size, gcc included in final image |

### 7.2 Docker Compose Services

| Service | Image | Auth | Network Exposure | Risk |
|---------|-------|------|-----------------|------|
| PostgreSQL | `postgres:16-alpine` | `postgres:postgres` | Port 5432 on host | MEDIUM |
| Redis | `redis:7-alpine` | **None** | Port 6379 on host | **HIGH** |
| n8n | `n8nio/n8n:latest` | `admin:admin` | Port 5678 on host | MEDIUM |
| MinIO | `minio/minio:latest` | `minioadmin:minioadmin` | Ports 9000, 9001 | LOW |
| MailHog | `mailhog/mailhog:latest` | None | Ports 1025, 8025 | LOW |

---

## Step 8: Runtime Behavior Analysis

### 8.1 External Network Calls

| Destination | Purpose | Auth Method | Risk |
|-------------|---------|-------------|------|
| Supabase (configurable URL) | Database, Auth | API key (service role key) | ✅ Expected |
| Groq API | AI/LLM inference | API key from env | ✅ Expected |
| Stripe API | Payment processing | Secret key from env | ✅ Expected |
| Resend API | Email delivery | API key from env | ✅ Expected |
| n8n Webhook | Workflow callbacks | HMAC-SHA256 signature | ✅ Expected |
| Cloudflare R2 | Object storage | Access key from env | ✅ Expected |

### 8.2 Process Spawning

- **Celery workers** (`celery_worker.py`) spawn background task processes with:
  - Task time limit: 300s (5 min)
  - Soft time limit: 240s
  - Max retries: 3
  - Rate limit: 10 tasks/minute
  - Task queues: email, analytics, webhooks, celery
  - ✅ Reasonable constraints

### 8.3 File System Writes

- Celery beat scheduler writes to `/tmp/celerybeat-schedule` — **[LOW]** acceptable for dev, should use persistent volume in production
- No arbitrary file system writes from API endpoints detected

### 8.4 Webhook Security

- HMAC-SHA256 signature verification with `hmac.compare_digest` (constant-time comparison) — ✅ **Good**
- Stripe webhook signature verification with timestamp-based replay protection (5-minute window) — ✅ **Good**
- Idempotency key checking to prevent duplicate processing — ✅ **Good**
- Webhook event logging to database — ✅ **Good**
- Webhook secret configurable via environment — ✅ **Good**

### 8.5 CORS Configuration

- Origins loaded from `settings.CORS_ORIGINS` (environment variable) — ✅
- `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]` — ⚠️ **[LOW]** Overly permissive headers/methods; should be narrowed in production

### 8.6 API Documentation

- Swagger docs (`/docs`) and ReDoc (`/redoc`) disabled when `DEBUG=false` — ✅ **Good**
- Enabled only in development mode

### 8.7 Authentication

- JWT tokens using `python-jose` with HS256 algorithm
- Token expiry: configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 7 days = 10080 min)
- ⚠️ **[LOW]** 7-day default token expiry is generous; consider shorter expiry with refresh tokens

---

## Step 9: Final Risk Assessment

### All Findings Summary

| ID | Severity | Category | Finding |
|----|----------|----------|---------|
| C1 | 🔴 CRITICAL | Deserialization | `pickle.loads` in cache.py deserializes untrusted Redis data |
| C2 | 🔴 CRITICAL | XSS | `dangerouslySetInnerHTML` renders raw RSS feed content without sanitization |
| H1 | 🟠 HIGH | Deserialization | `pickle.loads` + `pickle.dumps` used for Redis cache serialization — remote code execution if Redis is compromised |
| H2 | 🟠 HIGH | XSS | RSS feed `entry.content` rendered as raw HTML in `RSSEntriesPanel.tsx` |
| H3 | 🟠 HIGH | Infrastructure | Redis has no authentication in docker-compose.yml |
| H4 | 🟠 HIGH | Secret Exposure | `NEXT_PUBLIC_GROQ_API_KEY` exposed as frontend environment variable |
| M1 | 🟡 MEDIUM | Infrastructure | Hardcoded credentials in docker-compose.yml (postgres, n8n, minio) |
| M2 | 🟡 MEDIUM | Secret Hygiene | `.env.production` committed to git repository (contains placeholder keys) |
| M3 | 🟡 MEDIUM | Crypto | `hashlib.md5` used for cache key generation — collision risk |
| M4 | 🟡 MEDIUM | Infrastructure | n8n basic auth `admin:admin` in docker-compose.yml |
| M5 | 🟡 MEDIUM | Infrastructure | n8n shares same PostgreSQL database as main application |
| M6 | 🟡 MEDIUM | UI | `SettingsTab.tsx` displays masked API key placeholders including `gsk_` pattern |
| L1 | 🟢 LOW | Privilege | `sudo` in `scripts/backup-database.sh` for AWS CLI install |
| L2 | 🟢 LOW | XSS | `dangerouslySetInnerHTML` in `layout.tsx` for theme script (controlled content) |
| L3 | 🟢 LOW | Infrastructure | MinIO default credentials `minioadmin:minioadmin` |
| L4 | 🟢 LOW | Infrastructure | All Docker services expose ports to host |
| L5 | 🟢 LOW | CI/CD | `continue-on-error: true` on production deploy steps |
| L6 | 🟢 LOW | Container | Dockerfile not multi-stage — gcc and build tools in final image |

### Top 10 Critical Issues

| # | Finding | Severity | Impact | Fix |
|---|---------|----------|--------|-----|
| 1 | `pickle.loads` deserialization in `cache.py` | CRITICAL | If Redis is compromised or cache data is tampered, attacker achieves RCE on backend | Replace `pickle` with `json` or `msgpack` serialization |
| 2 | `dangerouslySetInnerHTML` on RSS content | CRITICAL | Stored XSS — malicious RSS feeds can execute arbitrary JS in user browsers | Sanitize HTML with DOMPurify before rendering; use text content or sandboxed iframe |
| 3 | Redis without authentication | HIGH | Any network-adjacent process can read/write Redis, inject cache data, or exploit pickle deserialization | Add `requirepass` to Redis config; use `--requirepass` flag |
| 4 | `NEXT_PUBLIC_GROQ_API_KEY` exposed in frontend | HIGH | Groq API key visible in browser JS bundle; anyone can use the key | Remove from `NEXT_PUBLIC_` env; proxy Groq calls through backend API |
| 5 | `.env.production` committed to git | MEDIUM | Template with placeholder keys, but encourages copying real keys into tracked files | Remove from git tracking; add to `.gitignore`; use secret management platform |
| 6 | Hardcoded docker-compose credentials | MEDIUM | Default passwords for Postgres, n8n, MinIO in development config | Use `.env` file or Docker secrets; document credential rotation |
| 7 | `hashlib.md5` for cache keys | MEDIUM | MD5 collisions could cause cache key collisions, leading to wrong data served | Replace with `hashlib.sha256` |
| 8 | n8n shares Postgres DB with app | MEDIUM | n8n workflows could read/modify application data | Use separate database for n8n |
| 9 | `python-jose` unmaintained | MEDIUM | No security patches since 2021; potential undiscovered vulnerabilities | Migrate to `PyJWT` |
| 10 | Dockerfile not multi-stage | LOW | Build tools (gcc) in production image increase attack surface | Use multi-stage build; only copy compiled artifacts |

### Recommended Fixes (Priority Order)

1. **[CRITICAL]** Replace `pickle` serialization in `cache.py` with JSON:
   ```python
   # Instead of:
   return pickle.dumps(value)
   return pickle.loads(value)
   
   # Use:
   return json.dumps(value).encode('utf-8')
   return json.loads(value.decode('utf-8'))
   ```
   Note: This requires cache values to be JSON-serializable (dicts, lists, strings, numbers).

2. **[CRITICAL]** Sanitize RSS HTML before rendering:
   ```tsx
   import DOMPurify from 'dompurify';
   
   <div dangerouslySetInnerHTML={{ 
     __html: DOMPurify.sanitize(entry.content.substring(0, 2000)) 
   }} />
   ```
   Or better: render in a sandboxed iframe with `sandbox=""` attribute.

3. **[HIGH]** Add Redis authentication:
   ```yaml
   redis:
     command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-dev_redis_pass}
   ```
   Update `REDIS_URL` to include the password: `redis://:password@localhost:6379/0`

4. **[HIGH]** Move Groq API key to backend-only:
   - Remove `NEXT_PUBLIC_GROQ_API_KEY` from `.env.local`
   - Create a backend proxy endpoint for Groq API calls
   - Frontend calls backend, backend calls Groq

5. **[MEDIUM]** Remove `.env.production` from git tracking:
   ```bash
   git rm --cached .env.production
   echo ".env.production" >> .gitignore
   git commit -m "chore: remove .env.production from tracking"
   ```

6. **[MEDIUM]** Replace `python-jose` with `PyJWT`:
   ```bash
   pip install PyJWT
   ```
   Update `src/backend/app/utils/jwt.py` to use `jwt.encode`/`jwt.decode` from `PyJWT`.

7. **[MEDIUM]** Replace `hashlib.md5` with `hashlib.sha256` in `cache.py`:
   ```python
   cache_key = hashlib.sha256(":".join(key_parts).encode()).hexdigest()
   ```

8. **[MEDIUM]** Separate n8n database:
   ```yaml
   n8n:
     environment:
       DB_POSTGRESDB_DATABASE: "n8n"
   ```
   Create a separate `n8n` database in Postgres.

9. **[LOW]** Use multi-stage Docker build:
   ```dockerfile
   FROM python:3.12-slim AS builder
   # Install deps, compile
   FROM python:3.12-slim
   COPY --from=builder /app /app
   ```

10. **[LOW]** Narrow CORS policy for production:
    ```python
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    ```

---

## Security Controls Assessment

| Control | Status | Notes |
|---------|--------|-------|
| Input validation | ⚠️ | RSS content not sanitized; Pydantic models used for API input ✅ |
| Authentication | ✅ | Supabase Auth + JWT tokens |
| Authorization | ⚠️ | Admin check exists on webhook logs; verify all endpoints have auth decorators |
| Secret management | ⚠️ | Environment-based (good), but `.env.production` tracked in git (bad) |
| Encryption in transit | ✅ | HTTPS for external APIs; Redis local-only in dev |
| Encryption at rest | ❌ | Not assessed — depends on deployment platform |
| Logging & monitoring | ✅ | Webhook event logging; error tracking middleware |
| Rate limiting | ✅ | Configurable via `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW` |
| CORS | ⚠️ | Configurable but overly permissive (`*` for methods/headers) |
| Dependency scanning | ✅ | CI pipeline includes TruffleHog, Bandit, pip-audit, npm audit |
| Container security | ✅ | Non-root user, slim image, health check |
| Webhook security | ✅ | HMAC-SHA256 signatures, idempotency, replay protection |

---

## Final Verdict

### ⚠️ SANDBOX ONLY

The ContentForge AI application is **safe for local development and testing** with its current mock credential configuration. However, it must **NOT be deployed to production** until the following are addressed:

1. ✅ Replace `pickle` serialization in cache layer
2. ✅ Sanitize RSS HTML content before rendering
3. ✅ Add Redis authentication
4. ✅ Move Groq API key to backend-only
5. ✅ Remove `.env.production` from git tracking

**No real credentials or API keys were found** leaked in the repository or git history. The placeholder values in `.env.production` are templates, not actual secrets. The codebase demonstrates several good security practices including HMAC webhook verification, non-root containers, CI security scanning, and environment-based configuration.

---

*Report generated by Neo DevOrg Security Engineer — 2026-04-13*