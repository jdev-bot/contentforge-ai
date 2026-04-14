"""
Search functionality for ContentForge AI.
Provides full-text search across content, projects, and assets.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.cache import cache
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter()


class SearchFilters(BaseModel):
    """Search filter options."""

    content_type: Optional[str] = None
    project_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None


class SearchResult(BaseModel):
    """Individual search result."""

    id: str
    type: str  # 'content', 'project', 'asset'
    title: str
    description: Optional[str] = None
    matched_field: str  # Which field matched
    matched_text: str  # The matching text snippet
    score: float  # Relevance score
    created_at: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response."""

    query: str
    total: int
    results: List[SearchResult]
    filters_applied: Optional[dict] = None


def _highlight_match(text: str, query: str, max_length: int = 150) -> str:
    """Create a highlighted snippet of the match."""
    if not text or not query:
        return text[:max_length] if text else ""

    query_lower = query.lower()
    text_lower = text.lower()

    # Find the position of the match
    pos = text_lower.find(query_lower)
    if pos == -1:
        return text[:max_length]

    # Extract snippet around match
    start = max(0, pos - 50)
    end = min(len(text), pos + len(query) + 50)
    snippet = text[start:end]

    # Add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet


def _calculate_relevance_score(
    text: str, query: str, field_weight: float = 1.0
) -> float:
    """Calculate a simple relevance score."""
    if not text or not query:
        return 0.0

    query_lower = query.lower()
    text_lower = text.lower()

    # Exact match gets highest score
    if query_lower == text_lower:
        return 1.0 * field_weight

    # Title match gets higher score
    if query_lower in text_lower:
        occurrences = text_lower.count(query_lower)
        return min(0.5 + (occurrences * 0.1), 0.9) * field_weight

    return 0.0


@router.get("/search", response_model=SearchResponse)
async def search_content(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    type: Optional[str] = Query(
        None, description="Filter by type: content, project, asset"
    ),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[str] = Query(
        None, description="Filter by date from (ISO format)"
    ),
    date_to: Optional[str] = Query(None, description="Filter by date to (ISO format)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    user=Depends(get_auth_user),
):
    """
    Search across content, projects, and assets.

    Args:
        q: Search query string
        type: Optional filter by item type
        project_id: Optional filter by project
        status: Optional filter by status
        date_from: Optional date filter start
        date_to: Optional date filter end
        limit: Maximum results to return

    Returns ranked search results with relevance scores.
    """
    supabase = get_supabase_client()
    user_id = str(user.id)

    # Create cache key based on search params
    cache_key = f"search:{user_id}:{q}:{type}:{project_id}:{limit}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return SearchResponse(**cached_result)

    results: List[SearchResult] = []

    try:
        # Search content
        if not type or type == "content":
            # Build content query
            content_query = (
                supabase.table("content")
                .select("*, projects(name)")
                .eq("user_id", user_id)
                .is_("deleted_at", None)
            )

            if project_id:
                content_query = content_query.eq("project_id", project_id)
            if status:
                content_query = content_query.eq("status", status)
            if date_from:
                content_query = content_query.gte("created_at", date_from)
            if date_to:
                content_query = content_query.lte("created_at", date_to)

            content_result = content_query.execute()

            for item in content_result.data or []:
                # Check for matches in title
                title_score = _calculate_relevance_score(
                    item.get("title", ""), q, field_weight=2.0
                )

                # Check for matches in original_text
                text_score = _calculate_relevance_score(
                    item.get("original_text", ""), q, field_weight=1.0
                )

                # Check for matches in source_url
                url_score = _calculate_relevance_score(
                    item.get("source_url", ""), q, field_weight=0.5
                )

                best_score = max(title_score, text_score, url_score)

                if best_score > 0:
                    # Determine matched field and text
                    if title_score >= text_score and title_score >= url_score:
                        matched_field = "title"
                        matched_text = _highlight_match(item.get("title", ""), q)
                    elif text_score >= url_score:
                        matched_field = "content"
                        matched_text = _highlight_match(
                            item.get("original_text", ""), q
                        )
                    else:
                        matched_field = "source_url"
                        matched_text = _highlight_match(item.get("source_url", ""), q)

                    results.append(
                        SearchResult(
                            id=item["id"],
                            type="content",
                            title=item.get("title", "Untitled"),
                            description=f"{item.get('word_count', 0)} words • {item.get('source_type', 'unknown')}",
                            matched_field=matched_field,
                            matched_text=matched_text,
                            score=best_score,
                            created_at=item["created_at"],
                            project_id=item.get("project_id"),
                            project_name=(
                                item.get("projects", {}).get("name")
                                if item.get("projects")
                                else None
                            ),
                        )
                    )

        # Search projects
        if not type or type == "project":
            project_query = (
                supabase.table("projects")
                .select("*")
                .eq("user_id", user_id)
                .is_("deleted_at", None)
            )

            if date_from:
                project_query = project_query.gte("created_at", date_from)
            if date_to:
                project_query = project_query.lte("created_at", date_to)

            project_result = project_query.execute()

            for item in project_result.data or []:
                # Check name match
                name_score = _calculate_relevance_score(
                    item.get("name", ""), q, field_weight=2.0
                )

                # Check description match
                desc_score = _calculate_relevance_score(
                    item.get("description", ""), q, field_weight=1.0
                )

                best_score = max(name_score, desc_score)

                if best_score > 0:
                    if name_score >= desc_score:
                        matched_field = "name"
                        matched_text = _highlight_match(item.get("name", ""), q)
                    else:
                        matched_field = "description"
                        matched_text = _highlight_match(item.get("description", ""), q)

                    results.append(
                        SearchResult(
                            id=item["id"],
                            type="project",
                            title=item.get("name", "Untitled Project"),
                            description=item.get("description", ""),
                            matched_field=matched_field,
                            matched_text=matched_text,
                            score=best_score,
                            created_at=item["created_at"],
                            project_id=None,
                            project_name=None,
                        )
                    )

        # Sort by relevance score (descending)
        results.sort(key=lambda x: x.score, reverse=True)

        # Apply limit
        total = len(results)
        results = results[:limit]

        # Prepare response
        filters_applied = {}
        if type:
            filters_applied["type"] = type
        if project_id:
            filters_applied["project_id"] = project_id
        if status:
            filters_applied["status"] = status
        if date_from:
            filters_applied["date_from"] = date_from
        if date_to:
            filters_applied["date_to"] = date_to

        response = SearchResponse(
            query=q,
            total=total,
            results=results,
            filters_applied=filters_applied if filters_applied else None,
        )

        # Cache for 1 minute
        cache.set(cache_key, response.dict(), ttl=60)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100), user=Depends(get_auth_user)
):
    """
    Get search suggestions based on user's content.
    Returns title suggestions matching the query.
    """
    supabase = get_supabase_client()
    user_id = str(user.id)

    try:
        # Get recent content titles
        content_result = (
            supabase.table("content")
            .select("title")
            .eq("user_id", user_id)
            .is_("deleted_at", None)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )

        # Get project names
        project_result = (
            supabase.table("projects")
            .select("name")
            .eq("user_id", user_id)
            .is_("deleted_at", None)
            .execute()
        )

        suggestions = []
        query_lower = q.lower()

        # Match content titles
        for item in content_result.data or []:
            title = item.get("title", "")
            if query_lower in title.lower():
                suggestions.append({"text": title, "type": "content"})

        # Match project names
        for item in project_result.data or []:
            name = item.get("name", "")
            if query_lower in name.lower():
                suggestions.append({"text": name, "type": "project"})

        # Deduplicate and limit
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s["text"] not in seen:
                seen.add(s["text"])
                unique_suggestions.append(s)
                if len(unique_suggestions) >= 10:
                    break

        return {"query": q, "suggestions": unique_suggestions}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}",
        )
