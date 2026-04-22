"""
Team Calendar router — org-scoped calendar view for scheduled posts.

Provides endpoints for viewing, filtering, and managing scheduled posts
across an organization's team members. Builds on the existing scheduler
infrastructure but adds org-scoping, date-range queries, and team member
assignment.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from pydantic import BaseModel, Field

from app.core.rate_limit import rate_limit_dependency
from app.core.supabase import get_supabase_admin_client
from app.routers.auth import get_auth_user
from app.routers.organizations import check_org_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/team-calendar", tags=["team-calendar"])


# ============== Models ==============


class TeamMemberInfo(BaseModel):
    """Team member info for calendar display."""

    id: str
    name: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    color: Optional[str] = None


class CalendarScheduledPost(BaseModel):
    """Scheduled post with team assignment info for calendar display."""

    id: str
    user_id: str
    content_id: str
    platform: str
    scheduled_at: datetime
    status: str
    asset_type: str
    timezone: str
    content: Optional[str] = None
    settings: Dict[str, Any] = {}
    assigned_to: List[str] = []
    recurrence: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    published_url: Optional[str] = None
    # Joined data
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None


class CalendarDayPosts(BaseModel):
    """Posts grouped by date."""

    date: str
    posts: List[CalendarScheduledPost]


class TeamCalendarMonthResponse(BaseModel):
    """Response for a month view of the team calendar."""

    org_id: str
    year: int
    month: int
    members: List[TeamMemberInfo]
    days: List[CalendarDayPosts]
    stats: Dict[str, int]


class TeamCalendarWeekResponse(BaseModel):
    """Response for a week view of the team calendar."""

    org_id: str
    start_date: str
    end_date: str
    members: List[TeamMemberInfo]
    days: List[CalendarDayPosts]
    stats: Dict[str, int]


class UpdatePostAssignmentRequest(BaseModel):
    """Request to update assigned team members on a scheduled post."""

    assigned_to: List[str] = Field(
        ..., description="List of organization member user IDs assigned to this post"
    )


class ConflictDetail(BaseModel):
    """Detail of a scheduling conflict."""

    post_id: str
    title: Optional[str] = None
    platform: str
    scheduled_at: datetime
    assigned_to: List[str] = []


class ConflictCheckResponse(BaseModel):
    """Response for team conflict checking."""

    has_conflicts: bool
    conflict_count: int
    conflicts: List[ConflictDetail]


# ============== Helper Functions ==============


# Distinct colors for team member calendar markers
_MEMBER_COLORS = [
    "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6",
    "#EF4444", "#EC4899", "#06B6D4", "#84CC16",
    "#F97316", "#6366F1", "#14B8A6", "#E11D48",
]


def _get_member_color(index: int) -> str:
    return _MEMBER_COLORS[index % len(_MEMBER_COLORS)]


def _get_org_members(supabase, org_id: str) -> List[Dict]:
    """Fetch org members with profile data."""
    members_result = (
        supabase.table("organization_members")
        .select("user_id, role")
        .eq("org_id", org_id)
        .execute()
    )

    if not members_result.data:
        return []

    member_user_ids = [m["user_id"] for m in members_result.data]

    # Batch-fetch profiles
    profiles_result = (
        supabase.table("profiles")
        .select("id, full_name, avatar_url, email")
        .in_("id", member_user_ids)
        .execute()
    )
    profiles_by_id = {}
    for p in profiles_result.data or []:
        profiles_by_id[p["id"]] = p

    members = []
    for i, m in enumerate(members_result.data):
        profile = profiles_by_id.get(m["user_id"], {})
        members.append({
            "id": m["user_id"],
            "name": profile.get("full_name") or profile.get("email", "Unknown"),
            "email": profile.get("email", ""),
            "role": m["role"],
            "avatar_url": profile.get("avatar_url"),
            "color": _get_member_color(i),
        })

    return members


def _posts_for_org_in_range(
    supabase,
    org_id: str,
    start_date: datetime,
    end_date: datetime,
    member_filter: Optional[str] = None,
    platform_filter: Optional[str] = None,
) -> List[Dict]:
    """Fetch scheduled posts for all org members within a date range."""
    # Get org member user IDs
    members_result = (
        supabase.table("organization_members")
        .select("user_id")
        .eq("org_id", org_id)
        .execute()
    )

    if not members_result.data:
        return []

    user_ids = [m["user_id"] for m in members_result.data]

    # If filtering by specific member, only include that user
    if member_filter and member_filter in user_ids:
        user_ids = [member_filter]

    # Query scheduled posts for these users in the date range
    start_iso = start_date.isoformat()
    end_iso = end_date.isoformat()

    query = (
        supabase.table("scheduled_posts")
        .select("*")
        .in_("user_id", user_ids)
        .gte("scheduled_at", start_iso)
        .lte("scheduled_at", end_iso)
        .in_("status", ["pending", "scheduled", "processing", "published", "failed"])
        .order("scheduled_at", desc=False)
    )

    if platform_filter:
        query = query.eq("platform", platform_filter)

    result = query.execute()

    return result.data or []


def _group_posts_by_day(posts: List[Dict]) -> Dict[str, List[Dict]]:
    """Group posts by date string (YYYY-MM-DD)."""
    grouped = {}
    for post in posts:
        scheduled = post.get("scheduled_at", "")
        if isinstance(scheduled, str):
            day_key = scheduled[:10]  # YYYY-MM-DD
        else:
            day_key = scheduled.strftime("%Y-%m-%d")
        grouped.setdefault(day_key, []).append(post)
    return grouped


def _count_stats(posts: List[Dict]) -> Dict[str, int]:
    """Count posts by status."""
    stats = {"total": len(posts), "scheduled": 0, "published": 0, "failed": 0, "draft": 0}
    for post in posts:
        status = post.get("status", "")
        if status in ("pending", "scheduled", "processing"):
            stats["scheduled"] += 1
        elif status == "published":
            stats["published"] += 1
        elif status == "failed":
            stats["failed"] += 1
        else:
            stats["draft"] += 1
    return stats


# ============== Endpoints ==============


@router.get("/month", response_model=TeamCalendarMonthResponse)
async def get_team_calendar_month(
    org_id: str = Query(..., description="Organization ID"),
    year: int = Query(..., description="Year (e.g. 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    member: Optional[str] = Query(None, description="Filter by user ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency),
):
    """
    Get team calendar data for a specific month.

    Returns all scheduled posts for org members within the month,
    grouped by day, with team member info and stats.
    """
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    # Verify org access
    has_access, role = check_org_access(supabase, org_id, user_id)
    if not has_access:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization",
        )

    # Calculate date range for the month
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)

    # Fetch org members and posts in parallel-ish (sync supabase calls)
    members = _get_org_members(supabase, org_id)
    posts = _posts_for_org_in_range(supabase, org_id, start_date, end_date, member, platform)

    # Build author lookup from members
    author_by_id = {m["id"]: m for m in members}

    # Enrich posts with author info
    for post in posts:
        author = author_by_id.get(post.get("user_id", ""), {})
        post["author_name"] = author.get("name")
        post["author_avatar"] = author.get("avatar_url")
        post["assigned_to"] = post.get("settings", {}).get("assigned_to", [])
        post["recurrence"] = post.get("settings", {}).get("recurrence")

    # Group by day
    grouped = _group_posts_by_day(posts)

    # Build day entries (include empty days for calendar grid)
    days_in_month = (end_date - start_date).days + 1
    days = []
    for day_offset in range(days_in_month):
        day_date = start_date + timedelta(days=day_offset)
        day_key = day_date.strftime("%Y-%m-%d")
        day_posts = grouped.get(day_key, [])
        days.append(
            CalendarDayPosts(
                date=day_key,
                posts=[CalendarScheduledPost(**p) for p in day_posts],
            )
        )

    return TeamCalendarMonthResponse(
        org_id=org_id,
        year=year,
        month=month,
        members=[TeamMemberInfo(**m) for m in members],
        days=days,
        stats=_count_stats(posts),
    )


@router.get("/week", response_model=TeamCalendarWeekResponse)
async def get_team_calendar_week(
    org_id: str = Query(..., description="Organization ID"),
    start_date: str = Query(..., description="Week start date (YYYY-MM-DD)"),
    member: Optional[str] = Query(None, description="Filter by user ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency),
):
    """
    Get team calendar data for a specific week.

    Returns all scheduled posts for org members within the 7-day window
    starting at start_date, grouped by day.
    """
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    has_access, role = check_org_access(supabase, org_id, user_id)
    if not has_access:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization",
        )

    try:
        week_start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid start_date format. Use YYYY-MM-DD.",
        )

    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

    members = _get_org_members(supabase, org_id)
    posts = _posts_for_org_in_range(supabase, org_id, week_start, week_end, member, platform)

    author_by_id = {m["id"]: m for m in members}
    for post in posts:
        author = author_by_id.get(post.get("user_id", ""), {})
        post["author_name"] = author.get("name")
        post["author_avatar"] = author.get("avatar_url")
        post["assigned_to"] = post.get("settings", {}).get("assigned_to", [])
        post["recurrence"] = post.get("settings", {}).get("recurrence")

    grouped = _group_posts_by_day(posts)

    days = []
    for day_offset in range(7):
        day_date = week_start + timedelta(days=day_offset)
        day_key = day_date.strftime("%Y-%m-%d")
        day_posts = grouped.get(day_key, [])
        days.append(
            CalendarDayPosts(
                date=day_key,
                posts=[CalendarScheduledPost(**p) for p in day_posts],
            )
        )

    return TeamCalendarWeekResponse(
        org_id=org_id,
        start_date=week_start.strftime("%Y-%m-%d"),
        end_date=week_end.strftime("%Y-%m-%d"),
        members=[TeamMemberInfo(**m) for m in members],
        days=days,
        stats=_count_stats(posts),
    )


@router.get("/day")
async def get_team_calendar_day(
    org_id: str = Query(..., description="Organization ID"),
    date: str = Query(..., description="Date (YYYY-MM-DD)"),
    member: Optional[str] = Query(None, description="Filter by user ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency),
):
    """
    Get team calendar data for a specific day.

    Returns all scheduled posts for org members on the given date.
    """
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    has_access, role = check_org_access(supabase, org_id, user_id)
    if not has_access:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization",
        )

    try:
        day_start = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD.",
        )

    day_end = day_start + timedelta(hours=23, minutes=59, seconds=59)

    members = _get_org_members(supabase, org_id)
    posts = _posts_for_org_in_range(supabase, org_id, day_start, day_end, member, platform)

    author_by_id = {m["id"]: m for m in members}
    for post in posts:
        author = author_by_id.get(post.get("user_id", ""), {})
        post["author_name"] = author.get("name")
        post["author_avatar"] = author.get("avatar_url")
        post["assigned_to"] = post.get("settings", {}).get("assigned_to", [])
        post["recurrence"] = post.get("settings", {}).get("recurrence")

    return {
        "org_id": org_id,
        "date": date,
        "members": [TeamMemberInfo(**m) for m in members],
        "posts": [CalendarScheduledPost(**p) for p in posts],
        "stats": _count_stats(posts),
    }


@router.put("/schedule/{post_id}/assign")
async def update_post_assignment(
    post_id: str,
    request: UpdatePostAssignmentRequest,
    org_id: str = Query(..., description="Organization ID"),
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency),
):
    """
    Update team member assignments on a scheduled post.

    Stores assigned member IDs in the post's settings.assigned_to field.
    Only org admins or the post owner can update assignments.
    """
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    has_access, role = check_org_access(supabase, org_id, user_id)
    if not has_access:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization",
        )

    # Get the current post
    post_result = (
        supabase.table("scheduled_posts")
        .select("*")
        .eq("id", post_id)
        .single()
        .execute()
    )

    if not post_result.data:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found",
        )

    post = post_result.data

    # Only post owner or org admin can reassign
    if post["user_id"] != user_id and role not in ("owner", "admin"):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only the post owner or org admin can update assignments",
        )

    # Validate assigned_to members belong to the org
    if request.assigned_to:
        org_member_ids = [
            m["user_id"]
            for m in (supabase.table("organization_members")
                      .select("user_id")
                      .eq("org_id", org_id)
                      .execute().data or [])
        ]
        invalid = set(request.assigned_to) - set(org_member_ids)
        if invalid:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Users not in organization: {list(invalid)}",
            )

    # Update settings.assigned_to
    current_settings = post.get("settings", {}) or {}
    current_settings["assigned_to"] = request.assigned_to

    update_result = (
        supabase.table("scheduled_posts")
        .update({"settings": current_settings})
        .eq("id", post_id)
        .execute()
    )

    if not update_result.data:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post assignment",
        )

    return {
        "message": "Assignment updated",
        "post_id": post_id,
        "assigned_to": request.assigned_to,
    }


@router.get("/conflicts", response_model=ConflictCheckResponse)
async def check_team_conflicts(
    org_id: str = Query(..., description="Organization ID"),
    scheduled_at: str = Query(..., description="Proposed scheduled time (ISO 8601)"),
    platform: str = Query(..., description="Platform to publish to"),
    exclude_id: Optional[str] = Query(None, description="Post ID to exclude"),
    window_minutes: int = Query(30, ge=5, le=120, description="Conflict window in minutes"),
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency),
):
    """
    Check for scheduling conflicts across the team.

    Returns any scheduled posts by org members that overlap with
    the proposed time for the same platform (within the configurable window).
    """
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    has_access, role = check_org_access(supabase, org_id, user_id)
    if not has_access:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization",
        )

    try:
        proposed_time = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid scheduled_at format. Use ISO 8601.",
        )

    # Get org member IDs
    members_result = (
        supabase.table("organization_members")
        .select("user_id")
        .eq("org_id", org_id)
        .execute()
    )
    user_ids = [m["user_id"] for m in members_result.data or []]

    if not user_ids:
        return ConflictCheckResponse(
            has_conflicts=False, conflict_count=0, conflicts=[]
        )

    window_start = (proposed_time - timedelta(minutes=window_minutes)).isoformat()
    window_end = (proposed_time + timedelta(minutes=window_minutes)).isoformat()

    query = (
        supabase.table("scheduled_posts")
        .select("id, platform, scheduled_at, content, settings")
        .in_("user_id", user_ids)
        .eq("platform", platform)
        .in_("status", ["pending", "scheduled", "processing"])
        .gte("scheduled_at", window_start)
        .lte("scheduled_at", window_end)
    )

    if exclude_id:
        query = query.neq("id", exclude_id)

    result = query.execute()
    conflict_posts = result.data or []

    conflicts = []
    for cp in conflict_posts:
        conflicts.append(
            ConflictDetail(
                post_id=cp["id"],
                title=cp.get("content", "")[:100] if cp.get("content") else None,
                platform=cp["platform"],
                scheduled_at=cp["scheduled_at"],
                assigned_to=cp.get("settings", {}).get("assigned_to", []),
            )
        )

    return ConflictCheckResponse(
        has_conflicts=len(conflicts) > 0,
        conflict_count=len(conflicts),
        conflicts=conflicts,
    )


@router.get("/members", response_model=List[TeamMemberInfo])
async def get_team_members(
    org_id: str = Query(..., description="Organization ID"),
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency),
):
    """
    Get team members for the calendar's member filter/avatar display.
    """
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    has_access, role = check_org_access(supabase, org_id, user_id)
    if not has_access:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization",
        )

    members = _get_org_members(supabase, org_id)
    return [TeamMemberInfo(**m) for m in members]