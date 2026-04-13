"""
ContentForge AI Python SDK — Data Models

Typed data models for Content, Project, Asset, Distribution, and WebhookEndpoint.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Parse a datetime string into a datetime object."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


@dataclass
class Content:
    """Represents a content item in ContentForge."""
    id: str
    project_id: str
    user_id: str
    title: str
    source_type: str
    status: str = "pending"
    source_url: Optional[str] = None
    original_text: Optional[str] = None
    word_count: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Content":
        """Create a Content instance from API response data."""
        return cls(
            id=data.get("id", ""),
            project_id=data.get("project_id", ""),
            user_id=data.get("user_id", ""),
            title=data.get("title", ""),
            source_type=data.get("source_type", "text"),
            status=data.get("status", "pending"),
            source_url=data.get("source_url"),
            original_text=data.get("original_text"),
            word_count=data.get("word_count"),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )


@dataclass
class Project:
    """Represents a project in ContentForge."""
    id: str
    user_id: str
    name: str
    is_active: bool = True
    description: Optional[str] = None
    brand_voice: Dict[str, Any] = field(default_factory=dict)
    target_platforms: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Project":
        """Create a Project instance from API response data."""
        return cls(
            id=data.get("id", ""),
            user_id=data.get("user_id", ""),
            name=data.get("name", ""),
            is_active=data.get("is_active", True),
            description=data.get("description"),
            brand_voice=data.get("brand_voice", {}),
            target_platforms=data.get("target_platforms", []),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )


@dataclass
class Asset:
    """Represents a generated asset in ContentForge."""
    id: str
    content_id: str
    user_id: str
    type: str
    content: str
    platform: Optional[str] = None
    tokens_used: Optional[int] = None
    status: str = "pending"
    engagement_prediction: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Asset":
        """Create an Asset instance from API response data."""
        return cls(
            id=data.get("id", ""),
            content_id=data.get("content_id", ""),
            user_id=data.get("user_id", ""),
            type=data.get("type", ""),
            content=data.get("content", ""),
            platform=data.get("platform"),
            tokens_used=data.get("tokens_used"),
            status=data.get("status", "pending"),
            engagement_prediction=data.get("engagement_prediction", {}),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )


@dataclass
class Distribution:
    """Represents a content distribution in ContentForge."""
    id: str
    asset_id: str
    user_id: str
    platform: str
    status: str = "pending"
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    published_url: Optional[str] = None
    external_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Distribution":
        """Create a Distribution instance from API response data."""
        return cls(
            id=data.get("id", ""),
            asset_id=data.get("asset_id", ""),
            user_id=data.get("user_id", ""),
            platform=data.get("platform", ""),
            status=data.get("status", "pending"),
            scheduled_at=_parse_datetime(data.get("scheduled_at")),
            published_at=_parse_datetime(data.get("published_at")),
            published_url=data.get("published_url"),
            external_id=data.get("external_id"),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )


@dataclass
class WebhookEndpoint:
    """Represents a webhook endpoint in ContentForge."""
    id: str
    name: str
    endpoint_url: str
    user_id: str
    is_active: bool = True
    description: Optional[str] = None
    project_id: Optional[str] = None
    secret: Optional[str] = None
    allowed_ips: List[str] = field(default_factory=list)
    total_calls: int = 0
    last_called_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "WebhookEndpoint":
        """Create a WebhookEndpoint instance from API response data."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            endpoint_url=data.get("endpoint_url", ""),
            user_id=data.get("user_id", ""),
            is_active=data.get("is_active", True),
            description=data.get("description"),
            project_id=data.get("project_id"),
            secret=data.get("secret"),
            allowed_ips=data.get("allowed_ips", []),
            total_calls=data.get("total_calls", 0),
            last_called_at=_parse_datetime(data.get("last_called_at")),
            created_at=_parse_datetime(data.get("created_at")),
        )