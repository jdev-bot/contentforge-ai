"""
Template Marketplace Service.

Handles:
- Template CRUD (list, search, get, publish, unpublish)
- Template categories and tags
- Template ratings and reviews
- Template usage tracking (installs count)
- Featured/trending templates
- Template versioning
- Author profile (template publisher)
- Lazy Supabase init pattern
"""

import json
import logging
import time
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.core.supabase import get_supabase_client, get_supabase_admin_client

logger = logging.getLogger(__name__)

# Default categories for the marketplace
DEFAULT_CATEGORIES = [
    {"id": "blog", "name": "Blog Posts", "icon": "📝", "description": "Templates for blog content"},
    {"id": "social", "name": "Social Media", "icon": "📱", "description": "Templates for social media posts"},
    {"id": "newsletter", "name": "Newsletters", "icon": "📧", "description": "Email newsletter templates"},
    {"id": "marketing", "name": "Marketing", "icon": "🎯", "description": "Marketing campaign templates"},
    {"id": "seo", "name": "SEO Content", "icon": "🔍", "description": "SEO-optimized content templates"},
    {"id": "ecommerce", "name": "E-Commerce", "icon": "🛒", "description": "Product and e-commerce templates"},
    {"id": "technical", "name": "Technical Writing", "icon": "⚙️", "description": "Documentation and technical writing"},
    {"id": "creative", "name": "Creative Writing", "icon": "🎨", "description": "Storytelling and creative content"},
]


class MarketplaceService:
    """Service for Template Marketplace operations."""

    _supabase = None
    _admin_supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @property
    def admin_supabase(self):
        if self._admin_supabase is None:
            self._admin_supabase = get_supabase_admin_client()
        return self._admin_supabase

    # ── Template CRUD ───────────────────────────────────────────────

    def list_templates(
        self,
        *,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        author_id: Optional[str] = None,
        is_featured: Optional[bool] = None,
        sort_by: str = "newest",
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """List marketplace templates with filtering and pagination."""
        query = self.supabase.table("marketplace_templates").select(
            "*, author:profiles!marketplace_templates_author_id_fkey(id, email, full_name)",
            count="exact",
        ).eq("is_published", True)

        if category:
            query = query.eq("category", category)
        if author_id:
            query = query.eq("author_id", author_id)
        if is_featured is not None:
            query = query.eq("is_featured", is_featured)
        if tags:
            # Filter by tags overlap
            query = query.overlaps("tags", tags)

        # Search
        if search:
            query = query.or_(
                f"name.ilike.%{search}%,description.ilike.%{search}%"
            )

        # Sort
        if sort_by == "newest":
            query = query.order("created_at", desc=True)
        elif sort_by == "popular":
            query = query.order("install_count", desc=True)
        elif sort_by == "rating":
            query = query.order("avg_rating", desc=True)
        elif sort_by == "featured":
            query = query.order("is_featured", desc=True).order("created_at", desc=True)
        else:
            query = query.order("created_at", desc=True)

        # Pagination
        query = query.range(offset, offset + limit - 1)

        result = query.execute()
        templates = result.data or []
        total = result.count if result.count is not None else len(templates)

        return {
            "templates": templates,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a single template by ID."""
        result = (
            self.supabase.table("marketplace_templates")
            .select(
                "*, author:profiles!marketplace_templates_author_id_fkey(id, email, full_name)"
            )
            .eq("id", template_id)
            .single()
            .execute()
        )
        return result.data

    def create_template(
        self,
        *,
        author_id: str,
        name: str,
        description: str,
        category: str,
        content: str,
        tags: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        preview_image_url: Optional[str] = None,
        version: str = "1.0.0",
        is_published: bool = False,
    ) -> Dict[str, Any]:
        """Create a new template."""
        data = {
            "id": str(uuid.uuid4()),
            "author_id": author_id,
            "name": name,
            "description": description,
            "category": category,
            "content": content,
            "tags": tags or [],
            "platforms": platforms or [],
            "preview_image_url": preview_image_url,
            "version": version,
            "is_published": is_published,
            "is_featured": False,
            "install_count": 0,
            "avg_rating": 0.0,
            "rating_count": 0,
            "review_count": 0,
            "latest_version": version,
        }

        result = self.supabase.table("marketplace_templates").insert(data).execute()
        template = result.data[0]

        # If publishing, record in version history
        if is_published:
            self._record_version(template["id"], version, "Initial publish", author_id)

        return template

    def update_template(
        self,
        template_id: str,
        author_id: str,
        **fields,
    ) -> Optional[Dict[str, Any]]:
        """Update a template (only by the author)."""
        # Verify ownership
        existing = self.get_template(template_id)
        if not existing:
            return None
        if existing["author_id"] != author_id:
            raise ValueError("Only the template author can update it")

        # If version changed, record it
        new_version = fields.get("version")
        if new_version and new_version != existing.get("version"):
            fields["latest_version"] = new_version
            self._record_version(
                template_id,
                new_version,
                fields.get("change_summary", f"Updated to v{new_version}"),
                author_id,
            )

        result = (
            self.supabase.table("marketplace_templates")
            .update(fields)
            .eq("id", template_id)
            .eq("author_id", author_id)
            .execute()
        )
        if not result.data:
            return None
        return result.data[0]

    def delete_template(self, template_id: str, author_id: str) -> bool:
        """Delete a template (only by the author, only if unpublished)."""
        existing = self.get_template(template_id)
        if not existing:
            return False
        if existing["author_id"] != author_id:
            raise ValueError("Only the template author can delete it")
        if existing.get("is_published"):
            raise ValueError("Cannot delete a published template; unpublish first")

        result = (
            self.supabase.table("marketplace_templates")
            .delete()
            .eq("id", template_id)
            .eq("author_id", author_id)
            .execute()
        )
        return len(result.data) > 0

    def publish_template(self, template_id: str, author_id: str) -> Optional[Dict[str, Any]]:
        """Publish a template to the marketplace."""
        existing = self.get_template(template_id)
        if not existing:
            return None
        if existing["author_id"] != author_id:
            raise ValueError("Only the template author can publish it")
        if existing.get("is_published"):
            return existing  # Already published

        result = (
            self.supabase.table("marketplace_templates")
            .update({"is_published": True, "published_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", template_id)
            .execute()
        )
        if not result.data:
            return None
        return result.data[0]

    def unpublish_template(self, template_id: str, author_id: str) -> Optional[Dict[str, Any]]:
        """Unpublish a template from the marketplace."""
        existing = self.get_template(template_id)
        if not existing:
            return None
        if existing["author_id"] != author_id:
            raise ValueError("Only the template author can unpublish it")

        result = (
            self.supabase.table("marketplace_templates")
            .update({"is_published": False})
            .eq("id", template_id)
            .execute()
        )
        if not result.data:
            return None
        return result.data[0]

    # ── Categories ──────────────────────────────────────────────────

    def list_categories(self) -> List[Dict[str, Any]]:
        """List all marketplace categories with template counts."""
        # Get counts from database
        result = (
            self.supabase.table("marketplace_templates")
            .select("category")
            .eq("is_published", True)
            .execute()
        )

        counts: Dict[str, int] = {}
        for row in (result.data or []):
            cat = row.get("category", "other")
            counts[cat] = counts.get(cat, 0) + 1

        categories = []
        for cat in DEFAULT_CATEGORIES:
            categories.append({
                **cat,
                "template_count": counts.get(cat["id"], 0),
            })

        # Add uncategorized
        if counts.get("other"):
            categories.append({
                "id": "other",
                "name": "Other",
                "icon": "📂",
                "description": "Other templates",
                "template_count": counts["other"],
            })

        return categories

    # ── Tags ────────────────────────────────────────────────────────

    def list_popular_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List popular tags with usage counts."""
        result = (
            self.supabase.table("marketplace_templates")
            .select("tags")
            .eq("is_published", True)
            .execute()
        )

        tag_counts: Dict[str, int] = {}
        for row in (result.data or []):
            for tag in (row.get("tags") or []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"name": t, "count": c} for t, c in sorted_tags]

    # ── Ratings & Reviews ──────────────────────────────────────────

    def rate_template(
        self,
        template_id: str,
        user_id: str,
        rating: int,
        review: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Rate a template (1-5 stars, optional review)."""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        # Upsert rating
        data = {
            "template_id": template_id,
            "user_id": user_id,
            "rating": rating,
            "review": review,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Check for existing rating
        existing = (
            self.supabase.table("marketplace_ratings")
            .select("id")
            .eq("template_id", template_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if existing.data:
            # Update existing
            result = (
                self.supabase.table("marketplace_ratings")
                .update({"rating": rating, "review": review})
                .eq("id", existing.data["id"])
                .execute()
            )
        else:
            # Create new
            result = self.supabase.table("marketplace_ratings").insert(data).execute()

        # Recalculate template averages
        self._recalculate_template_ratings(template_id)

        return result.data[0] if result.data else data

    def get_template_ratings(
        self,
        template_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get ratings and reviews for a template."""
        result = (
            self.supabase.table("marketplace_ratings")
            .select("*, user:profiles!marketplace_ratings_user_id_fkey(id, email, full_name)", count="exact")
            .eq("template_id", template_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return {
            "ratings": result.data or [],
            "total": result.count if result.count is not None else 0,
            "limit": limit,
            "offset": offset,
        }

    def delete_rating(self, rating_id: str, user_id: str) -> bool:
        """Delete a rating (only by the user who created it)."""
        result = (
            self.supabase.table("marketplace_ratings")
            .delete()
            .eq("id", rating_id)
            .eq("user_id", user_id)
            .execute()
        )
        deleted = len(result.data) > 0
        if deleted and result.data:
            template_id = result.data[0].get("template_id")
            if template_id:
                self._recalculate_template_ratings(template_id)
        return deleted

    def _recalculate_template_ratings(self, template_id: str):
        """Recalculate average rating and counts for a template."""
        result = (
            self.supabase.table("marketplace_ratings")
            .select("rating, review")
            .eq("template_id", template_id)
            .execute()
        )

        ratings = result.data or []
        if not ratings:
            self.supabase.table("marketplace_templates").update({
                "avg_rating": 0.0,
                "rating_count": 0,
                "review_count": 0,
            }).eq("id", template_id).execute()
            return

        rating_values = [r["rating"] for r in ratings]
        avg_rating = sum(rating_values) / len(rating_values)
        review_count = sum(1 for r in ratings if r.get("review"))

        self.supabase.table("marketplace_templates").update({
            "avg_rating": round(avg_rating, 2),
            "rating_count": len(ratings),
            "review_count": review_count,
        }).eq("id", template_id).execute()

    # ── Usage Tracking ──────────────────────────────────────────────

    def install_template(self, template_id: str, user_id: str) -> Dict[str, Any]:
        """Record a template installation and increment the install count."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")
        if not template.get("is_published"):
            raise ValueError("Template is not published")

        # Record installation
        install_data = {
            "template_id": template_id,
            "user_id": user_id,
        }

        # Check if already installed
        existing = (
            self.supabase.table("marketplace_installs")
            .select("id")
            .eq("template_id", template_id)
            .eq("user_id", user_id)
            .execute()
        )

        if existing.data:
            return {"message": "Template already installed", "template_id": template_id, "already_installed": True}

        self.supabase.table("marketplace_installs").insert(install_data).execute()

        # Increment install count
        new_count = (template.get("install_count") or 0) + 1
        self.supabase.table("marketplace_templates").update({
            "install_count": new_count,
        }).eq("id", template_id).execute()

        return {"message": "Template installed", "template_id": template_id, "already_installed": False}

    def get_user_installs(self, user_id: str) -> List[Dict[str, Any]]:
        """Get templates installed by a user."""
        result = (
            self.supabase.table("marketplace_installs")
            .select("template_id, installed_at, template:marketplace_templates(id, name, category, version, latest_version, author:profiles!marketplace_templates_author_id_fkey(full_name))")
            .eq("user_id", user_id)
            .order("installed_at", desc=True)
            .execute()
        )
        return result.data or []

    # ── Featured & Trending ─────────────────────────────────────────

    def get_featured_templates(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Get featured templates."""
        result = (
            self.supabase.table("marketplace_templates")
            .select("*, author:profiles!marketplace_templates_author_id_fkey(id, full_name)")
            .eq("is_published", True)
            .eq("is_featured", True)
            .order("install_count", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    def get_trending_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending templates (most installs recently)."""
        result = (
            self.supabase.table("marketplace_templates")
            .select("*, author:profiles!marketplace_templates_author_id_fkey(id, full_name)")
            .eq("is_published", True)
            .order("install_count", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    def set_featured(self, template_id: str, featured: bool) -> Optional[Dict[str, Any]]:
        """Set or unset a template as featured (admin only in practice)."""
        result = (
            self.supabase.table("marketplace_templates")
            .update({"is_featured": featured})
            .eq("id", template_id)
            .execute()
        )
        if not result.data:
            return None
        return result.data[0]

    # ── Versioning ──────────────────────────────────────────────────

    def get_template_versions(self, template_id: str) -> List[Dict[str, Any]]:
        """Get version history for a template."""
        result = (
            self.supabase.table("marketplace_template_versions")
            .select("*")
            .eq("template_id", template_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    def get_template_version(self, template_id: str, version: str) -> Optional[Dict[str, Any]]:
        """Get a specific version of a template."""
        result = (
            self.supabase.table("marketplace_template_versions")
            .select("*")
            .eq("template_id", template_id)
            .eq("version", version)
            .single()
            .execute()
        )
        return result.data

    def _record_version(
        self,
        template_id: str,
        version: str,
        change_summary: str,
        author_id: str,
    ) -> Dict[str, Any]:
        """Record a new version in the template version history."""
        data = {
            "template_id": template_id,
            "version": version,
            "change_summary": change_summary,
            "author_id": author_id,
        }
        result = self.supabase.table("marketplace_template_versions").insert(data).execute()
        return result.data[0]

    # ── Author Profile ──────────────────────────────────────────────

    def get_author_profile(self, author_id: str) -> Optional[Dict[str, Any]]:
        """Get an author's marketplace profile with stats."""
        # Get author info from profiles
        profile = self._get_user_by_id(author_id)
        if not profile:
            return None

        # Get template stats
        templates = (
            self.supabase.table("marketplace_templates")
            .select("id, is_published, install_count, avg_rating")
            .eq("author_id", author_id)
            .execute()
        )

        template_list = templates.data or []
        published_count = sum(1 for t in template_list if t.get("is_published"))
        total_installs = sum(t.get("install_count", 0) for t in template_list)
        avg_ratings = [t["avg_rating"] for t in template_list if t.get("avg_rating") and t["avg_rating"] > 0]
        avg_rating = sum(avg_ratings) / len(avg_ratings) if avg_ratings else 0.0

        return {
            "id": author_id,
            "full_name": profile.get("full_name", ""),
            "email": profile.get("email", ""),
            "avatar_url": profile.get("avatar_url"),
            "template_count": len(template_list),
            "published_count": published_count,
            "total_installs": total_installs,
            "avg_rating": round(avg_rating, 2),
            "joined_at": profile.get("created_at", ""),
        }

    def get_author_templates(self, author_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get templates by a specific author."""
        result = (
            self.supabase.table("marketplace_templates")
            .select("*", count="exact")
            .eq("author_id", author_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return {
            "templates": result.data or [],
            "total": result.count if result.count is not None else 0,
            "limit": limit,
            "offset": offset,
        }

    # ── User Lookup ─────────────────────────────────────────────────

    def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID from profiles table."""
        result = self.supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return result.data


# Singleton
marketplace_service = MarketplaceService()