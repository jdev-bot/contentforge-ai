# ContentForge AI - Cron Job Configuration

> Documentation for automated scheduled tasks, cron job setup, and GitHub Actions scheduled workflows.

---

## Overview

ContentForge AI uses scheduled tasks for:
- **Database backups** — Daily and weekly backups to R2
- **Usage reset** — Monthly usage counter reset
- **Security scanning** — Weekly security pipeline
- **Data retention enforcement** — Automated cleanup per policies
- **SLA monitoring** — Continuous compliance tracking
- **Health monitoring** — Periodic health checks
- **Log rotation** — Cleanup of old logs

### Runner

All GitHub Actions scheduled workflows run on the **self-hosted runner (srv1503460)**.

---

## Cron Job Reference

### System Cron Jobs

```bash
# Daily backup at 2:00 AM UTC
0 2 * * * /home/claw/contentforge-ai/scripts/backup-database.sh --daily >> /home/claw/contentforge-ai/logs/cron-backup-daily.log 2>&1

# Weekly full backup at 3:00 AM UTC on Sundays
0 3 * * 0 /home/claw/contentforge-ai/scripts/backup-database.sh --weekly >> /home/claw/contentforge-ai/logs/cron-backup-weekly.log 2>&1

# Backup cleanup (weekly on Mondays at 4:00 AM UTC)
0 4 * * 1 /home/claw/contentforge-ai/scripts/backup-database.sh --cleanup >> /home/claw/contentforge-ai/logs/cron-backup-cleanup.log 2>&1

# Daily system metrics collection (every hour)
0 * * * * curl -s https://contentforge-ai-api.onrender.com/api/v1/health/metrics > /dev/null 2>&1

# Daily log rotation (keep 30 days)
0 0 * * * find /home/claw/contentforge-ai/logs -name "*.log" -mtime +30 -delete

# Compress logs older than 7 days
0 1 * * * find /home/claw/contentforge-ai/logs -name "*.log" -mtime +7 -exec gzip {} \;

# Monthly usage reset (1st of each month at 4 AM UTC)
0 4 1 * * curl -s -X POST https://contentforge-ai-api.onrender.com/api/v1/admin/reset-usage \
  -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null 2>&1

# Data retention enforcement (daily at 3:00 AM UTC)
0 3 * * * curl -s -X POST https://contentforge-ai-api.onrender.com/api/v1/retention/apply \
  -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null 2>&1
```

---

## GitHub Actions Scheduled Workflows

### Security Pipeline (Weekly)

**Workflow:** `.github/workflows/security.yml`

```yaml
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 06:00 UTC
  workflow_dispatch:       # Manual trigger available
```

**Runs on:** Self-hosted runner (srv1503460)

**Jobs:**
- Gitleaks (secret scanning)
- TruffleHog (verified secret detection)
- Semgrep (SAST - Python + TypeScript)
- CodeQL (SAST - Python + JS/TS)
- Bandit (Python security)
- pip-audit (Python dependency scanning)
- npm audit (Node.js dependency scanning)
- OSV Scanner (multi-ecosystem vulnerability scanning)
- Trivy FS (filesystem scanning)
- Trivy Config (IaC/Docker misconfiguration)
- Trivy Image (container image scanning)
- Checkov (IaC scanning)
- Dependency Review (PR only)
- Security Gate (summary)

**Status:** 8/13 scans pass, 5 expected infra failures

### CI/CD Pipeline (On Push)

**Workflow:** `.github/workflows/ci-cd.yml`

```yaml
on:
  push:
    branches: [main, develop]
```

**Runs on:** Self-hosted runner (srv1503460)

**Jobs:**
- Backend build + test (530 tests)
- Frontend build + lint
- Deploy (on push to main)

### Backend Tests (On Push/PR)

**Workflow:** `.github/workflows/backend-tests.yml`

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
```

### Frontend Build (On Push/PR)

**Workflow:** `.github/workflows/frontend-build.yml`

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
```

---

## Self-Hosted Runner Job Processing

### How Jobs Are Assigned

GitHub Actions dispatches jobs to the self-hosted runner (srv1503460) based on the `runs-on` label configured in each workflow:

```yaml
jobs:
  build:
    runs-on: self-hosted  # Routes to srv1503460
```

### Runner Job Queue

When multiple workflows trigger simultaneously:
1. Jobs queue on the single runner
2. Jobs execute sequentially (one at a time)
3. Job execution order: first-in, first-out
4. Long-running security scans may delay other jobs

### Monitoring Runner Job Processing

```bash
# Check runner status
systemctl status actions.runner.*

# View recent job logs
journalctl -u actions.runner.* -n 100 --no-pager

# Check GitHub Actions queue
gh run list --limit 10
gh run list --status queued

# View running jobs
gh run list --status in_progress
```

### Job Failure Handling

When a job fails on the self-hosted runner:
1. GitHub marks the job as failed
2. Subsequent dependent jobs are skipped
3. Failed job logs are available via `gh run view <id> --log-failed`
4. Re-run failed jobs: `gh run rerun <id>`
5. For persistent failures, check runner health and logs

---

## Setup Instructions

### Using System Crontab (Linux)

1. **Edit crontab:**
   ```bash
   crontab -e
   ```

2. **Add jobs** (copy from reference above)

3. **Verify crontab:**
   ```bash
   crontab -l
   ```

### Using GitHub Actions (Recommended for Security Scans)

Scheduled workflows are already configured in `.github/workflows/`. To add a new scheduled workflow:

1. Create `.github/workflows/scheduled-tasks.yml`:
   ```yaml
   name: Scheduled Tasks

   on:
     schedule:
       - cron: '0 2 * * *'  # Daily at 2 AM UTC
     workflow_dispatch:

   jobs:
     backup:
       runs-on: self-hosted
       steps:
         - uses: actions/checkout@v3
         - name: Run task
           run: ./scripts/your-task.sh
           env:
             SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
   ```

2. Push to repository
3. GitHub Actions will execute on schedule

---

## Cron Expression Reference

| Expression | Description |
|------------|-------------|
| `0 2 * * *` | Every day at 2:00 AM UTC |
| `0 3 * * 0` | Every Sunday at 3:00 AM UTC |
| `0 4 * * 1` | Every Monday at 4:00 AM UTC |
| `0 6 * * 1` | Every Monday at 6:00 AM UTC |
| `*/5 * * * *` | Every 5 minutes |
| `0 */6 * * *` | Every 6 hours |
| `0 0 1 * *` | First day of every month |
| `0 3 * * *` | Every day at 3:00 AM UTC |

---

## Monitoring Cron Jobs

### System Cron Monitoring

```bash
# Check cron logs
grep CRON /var/log/syslog | tail -20

# Check specific job output
tail -f /home/claw/contentforge-ai/logs/cron-backup-daily.log

# Verify cron service
systemctl status cron
```

### GitHub Actions Monitoring

```bash
# List recent workflow runs
gh run list --limit 20

# Check scheduled workflow status
gh run list --workflow=security.yml --limit 5

# View specific run
gh run view <run-id>

# Check run timing
gh run view <run-id> --json timing
```

### Backup Verification

```bash
# Verify recent backups
aws s3 ls s3://$R2_BUCKET_NAME/backups/ \
  --endpoint-url https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com

# Test backup integrity
./scripts/backup-database.sh --verify
```

---

## Troubleshooting

### Cron Job Not Running

1. **Check crontab syntax:**
   ```bash
   crontab -l | crontab -
   ```

2. **Verify path and permissions:**
   ```bash
   ls -la /home/claw/contentforge-ai/scripts/backup-database.sh
   chmod +x /home/claw/contentforge-ai/scripts/backup-database.sh
   ```

3. **Check environment variables:**
   - Cron runs with minimal environment
   - Source `.env` file or set variables explicitly

4. **Review logs:**
   ```bash
   grep CRON /var/log/syslog
   cat /var/spool/mail/$(whoami)
   ```

### GitHub Actions Scheduled Workflow Not Triggering

1. **Verify workflow file** is on the default branch (scheduled workflows only run from default branch)
2. **Check cron syntax** — GitHub uses UTC
3. **Verify runner is online:**
   ```bash
   systemctl status actions.runner.*
   ```
4. **Check GitHub Actions tab** for run history and errors
5. **Test manually** via `workflow_dispatch`

### Backup Failures

1. **Check AWS CLI:**
   ```bash
   which aws && aws --version
   ```

2. **Verify R2 credentials:**
   ```bash
   aws s3 ls s3://$R2_BUCKET_NAME --endpoint-url https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```

4. **Review logs:**
   ```bash
   tail -100 /home/claw/contentforge-ai/logs/cron-backup-daily.log
   ```

### Self-Hosted Runner Job Processing Issues

1. **Runner offline:**
   ```bash
   systemctl restart actions.runner.*
   ```

2. **Job stuck in queue:**
   - Check runner capacity (single runner = sequential processing)
   - Consider adding a second runner for parallel processing

3. **Job timeout:**
   - Check default timeout (6 hours for GitHub Actions)
   - Increase timeout in workflow: `timeout-minutes: 30`

4. **Disk space on runner:**
   ```bash
   df -h
   docker system prune -f
   rm -rf ~/actions-runner/_work/_temp/*
   ```

---

## Security Considerations

### Environment Variables

- **Never** hardcode credentials in cron jobs
- Use `.env` files with restricted permissions (600)
- GitHub Actions secrets are encrypted at rest
- Self-hosted runner environment variables set via `.env` in runner config

### Cron Permissions

```bash
# Restrict cron to specific users
# /etc/cron.allow
claw
```

### Log Security

- Logs may contain sensitive data
- Set permissions: `chmod 640 logs/*.log`
- Rotate and archive securely
- Compress old logs to reduce exposure window

---

## Maintenance Tasks

### Weekly

- [ ] Verify all cron jobs ran successfully
- [ ] Check GitHub Actions scheduled workflow runs
- [ ] Review self-hosted runner health
- [ ] Verify backup integrity

### Monthly

- [ ] Review cron job schedules for needed adjustments
- [ ] Check data retention enforcement
- [ ] Review SLA monitoring alerts
- [ ] Update backup retention if needed

### Quarterly

- [ ] Audit all scheduled jobs (system + GitHub Actions)
- [ ] Test restore procedures
- [ ] Review and update access permissions
- [ ] Document any custom scripts
- [ ] Verify monitoring coverage
- [ ] Review expected infra failures in security pipeline

---

*Last updated: 2026-04-14*  
*Version: 2.0*  
*Runner: srv1503460 | Security scans: Weekly Mon 06:00 UTC | Backups: Daily 02:00 UTC*