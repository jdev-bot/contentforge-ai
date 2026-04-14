"""
Data Retention Service.

Provides configurable retention policies per content type:
- Auto-archive content after retention period
- Auto-delete content after extended retention
- Retention policy CRUD
- Retention audit trail
- Compliance reporting (GDPR Article 5)
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.supabase import get_supabase_client


class RetentionService:
    """Service for managing data retention policies and compliance."""

    _supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client initialization."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    # ── Policy CRUD ──────────────────────────────────────────────

    def create_policy(
        self,
        user_id: UUID,
        content_type: str,
        archive_after_days: int,
        delete_after_days: Optional[int] = None,
        description: Optional[str] = None,
        is_active: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a retention policy.

        Args:
            user_id: Owner of the policy.
            content_type: Content type this policy applies to.
            archive_after_days: Days before content is auto-archived.
            delete_after_days: Days before content is auto-deleted (must be >= archive_after_days).
            description: Optional human-readable description.
            is_active: Whether the policy is active.

        Returns:
            Created policy record.
        """
        if delete_after_days is not None and delete_after_days < archive_after_days:
            raise ValueError("delete_after_days must be >= archive_after_days")

        policy_data = {
            "user_id": str(user_id),
            "content_type": content_type,
            "archive_after_days": archive_after_days,
            "delete_after_days": delete_after_days,
            "description": description,
            "is_active": is_active,
        }

        result = self.supabase.table("retention_policies").insert(policy_data).execute()
        self._record_audit(
            user_id=user_id,
            action="policy_created",
            resource_type="retention_policy",
            resource_id=result.data[0]["id"],
            details=policy_data,
        )
        return result.data[0]

    def list_policies(
        self,
        user_id: UUID,
        content_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """List retention policies for a user with optional filters."""
        query = (
            self.supabase.table("retention_policies")
            .select("*")
            .eq("user_id", str(user_id))
        )

        if content_type is not None:
            query = query.eq("content_type", content_type)
        if is_active is not None:
            query = query.eq("is_active", is_active)

        # Count
        count_result = (
            self.supabase.table("retention_policies")
            .select("count", count="exact")
            .eq("user_id", str(user_id))
        )
        if content_type is not None:
            count_result = count_result.eq("content_type", content_type)
        if is_active is not None:
            count_result = count_result.eq("is_active", is_active)
        count_result = count_result.execute()
        total = count_result.count or 0

        offset = (page - 1) * page_size
        result = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()

        return {
            "items": result.data,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_policy(self, policy_id: str, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single retention policy by ID."""
        result = (
            self.supabase.table("retention_policies")
            .select("*")
            .eq("id", policy_id)
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
        return result.data

    def update_policy(
        self,
        policy_id: str,
        user_id: UUID,
        **updates: Any,
    ) -> Dict[str, Any]:
        """
        Update a retention policy.

        Accepts partial updates for any field.
        """
        # Verify ownership
        existing = self.get_policy(policy_id, user_id)
        if not existing:
            return None

        # Validate consistency
        archive_days = updates.get("archive_after_days", existing["archive_after_days"])
        delete_days = updates.get("delete_after_days", existing.get("delete_after_days"))
        if delete_days is not None and delete_days < archive_days:
            raise ValueError("delete_after_days must be >= archive_after_days")

        updates["updated_at"] = datetime.now().isoformat()
        result = (
            self.supabase.table("retention_policies")
            .update(updates)
            .eq("id", policy_id)
            .eq("user_id", str(user_id))
            .execute()
        )

        self._record_audit(
            user_id=user_id,
            action="policy_updated",
            resource_type="retention_policy",
            resource_id=policy_id,
            details=updates,
        )
        return result.data[0] if result.data else None

    def delete_policy(self, policy_id: str, user_id: UUID) -> bool:
        """Delete a retention policy."""
        existing = self.get_policy(policy_id, user_id)
        if not existing:
            return False

        self.supabase.table("retention_policies").delete().eq("id", policy_id).eq("user_id", str(user_id)).execute()

        self._record_audit(
            user_id=user_id,
            action="policy_deleted",
            resource_type="retention_policy",
            resource_id=policy_id,
            details={},
        )
        return True

    # ── Apply Retention ───────────────────────────────────────────

    def apply_retention(self, user_id: UUID, content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply retention policies: archive and/or delete expired content.

        Scans all active policies for the user, finds content that has
        exceeded archive or delete thresholds, and acts on it.

        Returns summary of actions taken.
        """
        # Get active policies
        policy_query = (
            self.supabase.table("retention_policies")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("is_active", True)
        )
        if content_type:
            policy_query = policy_query.eq("content_type", content_type)
        policies_result = policy_query.execute()

        if not policies_result.data:
            return {"archived": 0, "deleted": 0, "policies_applied": 0}

        archived_count = 0
        deleted_count = 0
        policies_applied = 0
        now = datetime.now()

        for policy in policies_result.data:
            ct = policy["content_type"]
            archive_days = policy["archive_after_days"]
            delete_days = policy.get("delete_after_days")

            # Find content of this type that belongs to the user
            content_result = (
                self.supabase.table("content")
                .select("id, created_at, status")
                .eq("user_id", str(user_id))
                .eq("content_type", ct)
                .execute()
            )

            for content in content_result.data:
                created_at_str = content.get("created_at")
                if not created_at_str:
                    continue
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                age_days = (now - created_at.replace(tzinfo=None)).days

                # Check delete threshold first
                if delete_days and age_days >= delete_days and content.get("status") != "deleted":
                    self.supabase.table("content").update({
                        "status": "deleted",
                        "updated_at": now.isoformat(),
                    }).eq("id", content["id"]).execute()

                    self._record_audit(
                        user_id=user_id,
                        action="content_deleted",
                        resource_type="content",
                        resource_id=content["id"],
                        details={
                            "policy_id": policy["id"],
                            "content_type": ct,
                            "age_days": age_days,
                            "delete_after_days": delete_days,
                        },
                    )
                    deleted_count += 1
                    continue

                # Check archive threshold
                if age_days >= archive_days and content.get("status") not in ("archived", "deleted"):
                    self.supabase.table("content").update({
                        "status": "archived",
                        "updated_at": now.isoformat(),
                    }).eq("id", content["id"]).execute()

                    self._record_audit(
                        user_id=user_id,
                        action="content_archived",
                        resource_type="content",
                        resource_id=content["id"],
                        details={
                            "policy_id": policy["id"],
                            "content_type": ct,
                            "age_days": age_days,
                            "archive_after_days": archive_days,
                        },
                    )
                    archived_count += 1

            policies_applied += 1

        return {
            "archived": archived_count,
            "deleted": deleted_count,
            "policies_applied": policies_applied,
        }

    # ── Compliance Reporting ──────────────────────────────────────

    def get_compliance_report(self, user_id: UUID) -> Dict[str, Any]:
        """
        Generate a GDPR Article 5 compliance report.

        Covers:
        - Storage limitation principle (Art. 5(1)(e))
        - Active retention policies
        - Content counts by status
        - Audit trail summary
        """
        now = datetime.now()

        # Active policies
        policies_result = (
            self.supabase.table("retention_policies")
            .select("*")
            .eq("user_id", str(user_id))
            .execute()
        )
        active_policies = [p for p in policies_result.data if p.get("is_active")]
        inactive_policies = [p for p in policies_result.data if not p.get("is_active")]

        # Content counts by status
        content_result = (
            self.supabase.table("content")
            .select("status, content_type, created_at")
            .eq("user_id", str(user_id))
            .execute()
        )

        status_counts: Dict[str, int] = {}
        type_counts: Dict[str, int] = {}
        content_without_policy: List[str] = []
        policy_content_types = {p["content_type"] for p in active_policies}

        for c in content_result.data:
            s = c.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
            ct = c.get("content_type", "unknown")
            type_counts[ct] = type_counts.get(ct, 0) + 1
            if ct not in policy_content_types:
                content_without_policy.append(ct)

        # Audit trail summary (last 30 days)
        thirty_days_ago = (now - timedelta(days=30)).isoformat()
        audit_result = (
            self.supabase.table("retention_audit_log")
            .select("action")
            .eq("user_id", str(user_id))
            .gte("created_at", thirty_days_ago)
            .execute()
        )
        audit_summary: Dict[str, int] = {}
        for entry in audit_result.data:
            action = entry["action"]
            audit_summary[action] = audit_summary.get(action, 0) + 1

        total_content = len(content_result.data)
        covered_content = sum(
            count for ct, count in type_counts.items() if ct in policy_content_types
        )

        compliance_score = 0
        if total_content > 0:
            coverage_ratio = covered_content / total_content
            has_archive = any(p["archive_after_days"] for p in active_policies)
            has_delete = any(p.get("delete_after_days") for p in active_policies)
            compliance_score = int(coverage_ratio * 60 + (20 if has_archive else 0) + (20 if has_delete else 0))

        return {
            "report_generated_at": now.isoformat(),
            "gdpr_article": "Article 5(1)(e) — Storage limitation",
            "compliance_score": min(compliance_score, 100),
            "total_content": total_content,
            "content_by_status": status_counts,
            "content_by_type": type_counts,
            "active_policies": len(active_policies),
            "inactive_policies": len(inactive_policies),
            "content_covered_by_policy": covered_content,
            "content_without_policy": list(set(content_without_policy)),
            "audit_trail_last_30_days": audit_summary,
            "recommendations": self._compliance_recommendations(
                active_policies, content_without_policy, total_content, covered_content
            ),
        }

    # ── Audit ─────────────────────────────────────────────────────

    def get_audit_trail(
        self,
        user_id: UUID,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Retrieve the retention audit trail for a user."""
        query = (
            self.supabase.table("retention_audit_log")
            .select("*")
            .eq("user_id", str(user_id))
        )
        if action:
            query = query.eq("action", action)

        # Count
        count_query = (
            self.supabase.table("retention_audit_log")
            .select("count", count="exact")
            .eq("user_id", str(user_id))
        )
        if action:
            count_query = count_query.eq("action", action)
        count_result = count_query.execute()
        total = count_result.count or 0

        offset = (page - 1) * page_size
        result = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()

        return {
            "items": result.data,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # ── Internal ──────────────────────────────────────────────────

    def _record_audit(
        self,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any],
    ) -> None:
        """Record a retention audit entry."""
        try:
            self.supabase.table("retention_audit_log").insert({
                "user_id": str(user_id),
                "action": action,
                "resource_type": resource_type,
                "resource_id": str(resource_id),
                "details": details,
            }).execute()
        except Exception:
            # Audit logging should never break the main operation
            pass

    @staticmethod
    def _compliance_recommendations(
        active_policies: List[Dict],
        content_without_policy: List[str],
        total_content: int,
        covered_content: int,
    ) -> List[str]:
        """Generate compliance recommendations."""
        recs = []

        if not active_policies:
            recs.append("No active retention policies found. Create policies to comply with GDPR Art. 5(1)(e).")

        if content_without_policy:
            types_str = ", ".join(sorted(set(content_without_policy)))
            recs.append(
                f"Content types without retention policy: {types_str}. "
                "Add policies to ensure all data has defined retention periods."
            )

        uncovered = total_content - covered_content
        if uncovered > 0 and total_content > 0:
            pct = round(uncovered / total_content * 100, 1)
            recs.append(
                f"{uncovered} content items ({pct}%) are not covered by any retention policy."
            )

        has_delete = any(p.get("delete_after_days") for p in active_policies)
        if not has_delete:
            recs.append(
                "No deletion policies configured. GDPR requires personal data to be "
                "kept no longer than necessary. Add delete_after_days to policies."
            )

        return recs


# Singleton instance
retention_service = RetentionService()