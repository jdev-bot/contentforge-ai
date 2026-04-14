"""
Alerting system for monitoring and notifications.
Supports email alerts via Resend and webhook notifications.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import httpx
from enum import Enum

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertChannel(str, Enum):
    """Alert notification channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"


class AlertManager:
    """Manager for sending alerts and notifications."""
    
    def __init__(self):
        self.settings = get_settings()
        self.alert_email = getattr(self.settings, 'ALERT_EMAIL', None)
        self.resend_api_key = getattr(self.settings, 'RESEND_API_KEY', None)
        self.webhook_url = getattr(self.settings, 'ALERT_WEBHOOK_URL', None)
    
    async def send_alert(
        self,
        subject: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.HIGH,
        details: Optional[Dict[str, Any]] = None,
        channels: Optional[List[AlertChannel]] = None
    ) -> bool:
        """
        Send an alert through configured channels.
        
        Args:
            subject: Alert subject line
            message: Alert message body
            severity: Alert severity level
            details: Additional details dictionary
            channels: List of channels to use (default: all configured)
        
        Returns:
            True if alert sent successfully to at least one channel
        """
        if channels is None:
            channels = []
            if self.alert_email and self.resend_api_key:
                channels.append(AlertChannel.EMAIL)
            if self.webhook_url:
                channels.append(AlertChannel.WEBHOOK)
        
        success = False
        
        if AlertChannel.EMAIL in channels:
            if await self._send_email_alert(subject, message, severity, details):
                success = True
        
        if AlertChannel.WEBHOOK in channels:
            if await self._send_webhook_alert(subject, message, severity, details):
                success = True
        
        return success
    
    async def _send_email_alert(
        self,
        subject: str,
        message: str,
        severity: AlertSeverity,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send alert via Resend email."""
        if not self.alert_email or not self.resend_api_key:
            return False
        
        try:
            # Color code by severity
            severity_colors = {
                AlertSeverity.CRITICAL: "#dc2626",
                AlertSeverity.HIGH: "#ea580c",
                AlertSeverity.MEDIUM: "#ca8a04",
                AlertSeverity.LOW: "#2563eb",
                AlertSeverity.INFO: "#16a34a"
            }
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: {severity_colors.get(severity, '#2563eb')}; 
                                color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                        <h2 style="margin: 0;">🔔 {severity.value.upper()} Alert</h2>
                    </div>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 5px;">
                        <h3 style="margin-top: 0;">{subject}</h3>
                        <p>{message}</p>
                        
                        {
                            f'<h4>Details:</h4><pre>{json.dumps(details, indent=2)}</pre>' 
                            if details else ''
                        }
                        
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #d1d5db;">
                            <p style="color: #6b7280; font-size: 12px;">
                                Timestamp: {datetime.now(timezone.utc).isoformat()} UTC<br>
                                Severity: {severity.value}<br>
                                Source: ContentForge AI
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.resend_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": "alerts@contentforge.ai",
                        "to": [self.alert_email],
                        "subject": f"[{severity.value.upper()}] {subject}",
                        "html": html_body
                    }
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"[AlertManager] Failed to send email alert: {e}")
            return False
    
    async def _send_webhook_alert(
        self,
        subject: str,
        message: str,
        severity: AlertSeverity,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send alert via webhook."""
        if not self.webhook_url:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json={
                        "alert_type": "contentforge",
                        "severity": severity.value,
                        "subject": subject,
                        "message": message,
                        "details": details or {},
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "source": "contentforge-ai"
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                return response.status_code in [200, 201, 202, 204]
                
        except Exception as e:
            logger.error(f"[AlertManager] Failed to send webhook alert: {e}")
            return False


# Predefined alert functions for common scenarios

async def alert_deployment_failed(
    environment: str,
    error_message: str,
    commit_hash: Optional[str] = None
) -> bool:
    """Send alert for failed deployment."""
    manager = AlertManager()
    
    details = {
        "environment": environment,
        "commit": commit_hash,
        "error": error_message
    }
    
    return await manager.send_alert(
        subject=f"Deployment Failed - {environment}",
        message=f"Deployment to {environment} environment failed with error: {error_message}",
        severity=AlertSeverity.CRITICAL,
        details=details
    )


async def alert_high_error_rate(
    error_rate: float,
    threshold: float,
    period_minutes: int = 5
) -> bool:
    """Send alert for high error rate."""
    manager = AlertManager()
    
    details = {
        "error_rate": f"{error_rate:.2%}",
        "threshold": f"{threshold:.2%}",
        "period_minutes": period_minutes
    }
    
    return await manager.send_alert(
        subject="High Error Rate Detected",
        message=f"Error rate is {error_rate:.2%} (threshold: {threshold:.2%}) over the last {period_minutes} minutes.",
        severity=AlertSeverity.HIGH,
        details=details
    )


async def alert_database_connection_failed(
    error_message: str,
    retry_count: int = 0
) -> bool:
    """Send alert for database connection failures."""
    manager = AlertManager()
    
    details = {
        "error": error_message,
        "retry_count": retry_count
    }
    
    return await manager.send_alert(
        subject="Database Connection Failed",
        message=f"Unable to connect to database after {retry_count} retries. Error: {error_message}",
        severity=AlertSeverity.CRITICAL,
        details=details
    )


async def alert_low_disk_space(
    free_gb: float,
    total_gb: float,
    percent_used: float
) -> bool:
    """Send alert for low disk space."""
    manager = AlertManager()
    
    severity = AlertSeverity.CRITICAL if percent_used > 90 else AlertSeverity.HIGH
    
    details = {
        "free_gb": free_gb,
        "total_gb": total_gb,
        "percent_used": percent_used
    }
    
    return await manager.send_alert(
        subject="Low Disk Space Warning",
        message=f"Disk space is {percent_used:.1f}% used. Only {free_gb:.1f}GB remaining out of {total_gb:.1f}GB total.",
        severity=severity,
        details=details
    )


async def alert_webhook_failure(
    webhook_type: str,
    error_message: str,
    retry_count: int = 0
) -> bool:
    """Send alert for webhook processing failures."""
    manager = AlertManager()
    
    details = {
        "webhook_type": webhook_type,
        "error": error_message,
        "retry_count": retry_count
    }
    
    return await manager.send_alert(
        subject=f"Webhook Failure - {webhook_type}",
        message=f"Webhook '{webhook_type}' failed after {retry_count} retries. Error: {error_message}",
        severity=AlertSeverity.HIGH,
        details=details
    )


async def alert_backup_failed(
    backup_type: str,
    error_message: str
) -> bool:
    """Send alert for backup failures."""
    manager = AlertManager()
    
    details = {
        "backup_type": backup_type,
        "error": error_message
    }
    
    return await manager.send_alert(
        subject=f"Backup Failed - {backup_type}",
        message=f"{backup_type} backup failed with error: {error_message}",
        severity=AlertSeverity.HIGH,
        details=details
    )


async def alert_security_event(
    event_type: str,
    description: str,
    source_ip: Optional[str] = None,
    user_id: Optional[str] = None
) -> bool:
    """Send alert for security-related events."""
    manager = AlertManager()
    
    details = {
        "event_type": event_type,
        "source_ip": source_ip,
        "user_id": user_id
    }
    
    return await manager.send_alert(
        subject=f"Security Alert - {event_type}",
        message=f"Security event detected: {description}",
        severity=AlertSeverity.CRITICAL,
        details=details
    )


async def alert_daily_summary(
    metrics: Dict[str, Any]
) -> bool:
    """Send daily summary email."""
    manager = AlertManager()
    
    # Build summary message
    message_parts = ["<strong>Daily System Summary</strong><ul>"]
    
    for key, value in metrics.items():
        message_parts.append(f"<li><strong>{key}:</strong> {value}</li>")
    
    message_parts.append("</ul>")
    
    return await manager.send_alert(
        subject="Daily System Summary",
        message="".join(message_parts),
        severity=AlertSeverity.INFO,
        details=metrics
    )


# Usage example
if __name__ == "__main__":
    import asyncio
    
    async def test_alerts():
        # Test deployment failure alert
        await alert_deployment_failed(
            environment="production",
            error_message="Build failed: npm install error",
            commit_hash="abc123"
        )
        
        # Test high error rate alert
        await alert_high_error_rate(
            error_rate=0.08,
            threshold=0.05
        )
    
    asyncio.run(test_alerts())