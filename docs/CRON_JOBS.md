# ContentForge AI - Cron Job Configuration

> Documentation for automated scheduled tasks and cron job setup.

---

## Overview

ContentForge AI uses scheduled tasks for:
- **Database backups** - Daily and weekly backups to R2
- **Usage reset** - Monthly usage counter reset
- **Health monitoring** - Periodic health checks
- **Log rotation** - Cleanup of old logs
- **Error summary** - Daily error reports

---

## Cron Job Reference

### Backup Jobs

```bash
# Daily backup at 2:00 AM UTC
0 2 * * * /home/claw/contentforge-ai/scripts/backup-database.sh --daily >> /home/claw/contentforge-ai/logs/cron-backup-daily.log 2>&1

# Weekly full backup at 3:00 AM UTC on Sundays
0 3 * * 0 /home/claw/contentforge-ai/scripts/backup-database.sh --weekly >> /home/claw/contentforge-ai/logs/cron-backup-weekly.log 2>&1

# Backup cleanup (weekly on Mondays)
0 4 * * 1 /home/claw/contentforge-ai/scripts/backup-database.sh --cleanup >> /home/claw/contentforge-ai/logs/cron-backup-cleanup.log 2>&1
```

### Health Monitoring

```bash
# Health check every 5 minutes (using Render uptime checks instead)
# Or via external monitoring service (Sentry, UptimeRobot)

# Daily system metrics collection
0 * * * * curl -s https://contentforge-ai-api.onrender.com/api/v1/health/metrics > /dev/null 2>&1
```

### Log Rotation

```bash
# Daily log rotation (keep 30 days)
0 0 * * * find /home/claw/contentforge-ai/logs -name "*.log" -mtime +30 -delete

# Compress logs older than 7 days
0 1 * * * find /home/claw/contentforge-ai/logs -name "*.log" -mtime +7 -exec gzip {} \;
```

### Usage Management

```bash
# Monthly usage reset (1st of each month at 4 AM UTC)
0 4 1 * * curl -s -X POST https://contentforge-ai-api.onrender.com/api/v1/admin/reset-usage \
  -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null 2>&1
```

---

## Setup Instructions

### Using System Crontab (Linux/macOS)

1. **Edit crontab:**
   ```bash
   crontab -e
   ```

2. **Add jobs (copy from above):**
   ```bash
   # Example for daily backup
   0 2 * * * /home/claw/contentforge-ai/scripts/backup-database.sh --daily
   ```

3. **Verify crontab:**
   ```bash
   crontab -l
   ```

### Using Render Cron Jobs

For Render-hosted services:

1. **Create a `render.yaml` cron job:**
   ```yaml
   services:
     - type: cron
       name: daily-backup
       schedule: "0 2 * * *"
       command: |
         cd /app && ./scripts/backup-database.sh --daily
       envVars:
         - key: SUPABASE_URL
           sync: false
         - key: R2_BUCKET_NAME
           sync: false
   ```

2. **Deploy to Render:**
   ```bash
   render deploy --service daily-backup
   ```

### Using GitHub Actions (Alternative)

Create `.github/workflows/scheduled-tasks.yml`:

```yaml
name: Scheduled Tasks

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run backup
        run: ./scripts/backup-database.sh --daily
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          R2_BUCKET_NAME: ${{ secrets.R2_BUCKET_NAME }}
          R2_ACCESS_KEY_ID: ${{ secrets.R2_ACCESS_KEY_ID }}
          R2_SECRET_ACCESS_KEY: ${{ secrets.R2_SECRET_ACCESS_KEY }}
          R2_ACCOUNT_ID: ${{ secrets.R2_ACCOUNT_ID }}
```

---

## Cron Expression Reference

| Expression | Description |
|------------|-------------|
| `0 2 * * *` | Every day at 2:00 AM |
| `0 3 * * 0` | Every Sunday at 3:00 AM |
| `*/5 * * * *` | Every 5 minutes |
| `0 */6 * * *` | Every 6 hours |
| `0 0 1 * *` | First day of every month |
| `0 0 * * 1` | Every Monday at midnight |

---

## Monitoring Cron Jobs

### Verify Jobs are Running

```bash
# Check cron logs
grep CRON /var/log/syslog | tail -20

# Check specific job output
tail -f /home/claw/contentforge-ai/logs/cron-backup-daily.log
```

### Health Check Integration

Add to your monitoring:

```python
# Check if backups are recent
def verify_recent_backup():
    from datetime import datetime, timedelta
    import os
    
    backup_dir = "/home/claw/contentforge-ai/backups"
    
    # Get most recent backup file
    files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir)]
    files = [f for f in files if os.path.isfile(f)]
    
    if not files:
        return False, "No backups found"
    
    latest = max(files, key=os.path.getmtime)
    age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(latest))
    
    if age > timedelta(hours=26):  # Allow 2 hours buffer
        return False, f"Latest backup is {age} old"
    
    return True, f"Latest backup: {latest}"
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
   - Cron jobs run with minimal environment
   - Source `.env` file or set variables explicitly

4. **Review logs:**
   ```bash
   # System mail for cron
   cat /var/spool/mail/$(whoami)
   
   # Syslog
   grep CRON /var/log/syslog
   ```

### Backup Failures

1. **Check AWS CLI installation:**
   ```bash
   which aws
   aws --version
   ```

2. **Verify R2 credentials:**
   ```bash
   aws s3 ls s3://$R2_BUCKET_NAME --endpoint-url https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```

4. **Review backup logs:**
   ```bash
   tail -100 /home/claw/contentforge-ai/logs/backup-*.log
   ```

---

## Security Considerations

### Environment Variables

- **Never** hardcode credentials in cron jobs
- Use `.env` files with restricted permissions (600)
- Consider using secret management tools

### Cron Permissions

```bash
# Restrict cron to specific users
# /etc/cron.allow
claw

# /etc/cron.deny (empty to allow all)
```

### Log Security

- Logs may contain sensitive data
- Set appropriate permissions: `chmod 640 logs/*.log`
- Rotate and archive securely

---

## Maintenance Tasks

### Quarterly Review

- [ ] Verify all jobs are running successfully
- [ ] Check backup integrity
- [ ] Review and adjust retention policies
- [ ] Update cron schedules if needed
- [ ] Test restore procedures

### Annual Tasks

- [ ] Audit all scheduled jobs
- [ ] Review and update access permissions
- [ ] Document any custom scripts
- [ ] Verify monitoring coverage

---

*Last updated: 2026-04-13*  
*Version: 1.0*