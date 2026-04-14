"""
Rate limiting and usage tracking tests for ContentForge AI.

Tests rate limiting middleware and usage tracking functionality.
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from fastapi import status, HTTPException

from tests.utils import (
    create_mock_auth_user,
    create_auth_headers,
    create_mock_supabase_response,
)


class TestRateLimiter:
    """Tests for the RateLimiter class."""
    
    @pytest.mark.unit
    def test_rate_limiter_allows_requests_within_limit(self):
        """Test that requests within limit are allowed."""
        from app.core.rate_limit import RateLimiter
        
        limiter = RateLimiter(requests=5, window=60)
        
        # First 5 requests should be allowed
        for i in range(5):
            assert limiter.is_allowed("test-key") is True
    
    @pytest.mark.unit
    def test_rate_limiter_blocks_excess_requests(self):
        """Test that requests over limit are blocked."""
        from app.core.rate_limit import RateLimiter
        
        limiter = RateLimiter(requests=3, window=60)
        
        # First 3 requests should be allowed
        for i in range(3):
            assert limiter.is_allowed("test-key") is True
        
        # 4th request should be blocked
        assert limiter.is_allowed("test-key") is False
    
    @pytest.mark.unit
    def test_rate_limiter_window_expires(self):
        """Test that rate limit window expires correctly."""
        from app.core.rate_limit import RateLimiter
        
        limiter = RateLimiter(requests=2, window=1)  # 1 second window
        
        # Use up the limit
        assert limiter.is_allowed("test-key") is True
        assert limiter.is_allowed("test-key") is True
        assert limiter.is_allowed("test-key") is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.is_allowed("test-key") is True
    
    @pytest.mark.unit
    def test_rate_limiter_separate_keys(self):
        """Test that different keys have separate limits."""
        from app.core.rate_limit import RateLimiter
        
        limiter = RateLimiter(requests=2, window=60)
        
        # Key 1 uses its limit
        assert limiter.is_allowed("key-1") is True
        assert limiter.is_allowed("key-1") is True
        assert limiter.is_allowed("key-1") is False
        
        # Key 2 still has full limit
        assert limiter.is_allowed("key-2") is True
        assert limiter.is_allowed("key-2") is True
    
    @pytest.mark.unit
    def test_rate_limiter_remaining_count(self):
        """Test remaining requests calculation."""
        from app.core.rate_limit import RateLimiter
        
        limiter = RateLimiter(requests=5, window=60)
        
        assert limiter.get_remaining("test-key") == 5
        
        limiter.is_allowed("test-key")
        assert limiter.get_remaining("test-key") == 4
        
        limiter.is_allowed("test-key")
        limiter.is_allowed("test-key")
        assert limiter.get_remaining("test-key") == 2


class TestCheckAndIncrementUsage:
    """Tests for usage checking and incrementing."""
    
    @pytest.mark.unit
    def test_check_usage_under_limit(self):
        """Test usage check when under limit."""
        from app.core.rate_limit import check_and_increment_usage
        
        user_id = "test-user-id"
        profile_data = {
            "monthly_usage_count": 50,
            "monthly_usage_limit": 100,
        }
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=profile_data)
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = \
            create_mock_supabase_response(data=[{**profile_data, "monthly_usage_count": 51}])
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            stats = check_and_increment_usage(user_id)
            
            assert stats.monthly_usage_count == 51
            assert stats.monthly_usage_limit == 100
            assert stats.remaining == 49
    
    @pytest.mark.unit
    def test_check_usage_at_limit(self):
        """Test usage check when at limit."""
        from app.core.rate_limit import check_and_increment_usage
        
        user_id = "test-user-id"
        profile_data = {
            "monthly_usage_count": 100,
            "monthly_usage_limit": 100,
        }
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=profile_data)
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                check_and_increment_usage(user_id)
            
            assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            assert "limit" in str(exc_info.value.detail).lower() or "reached" in str(exc_info.value.detail).lower()
    
    @pytest.mark.unit
    def test_check_usage_over_limit(self):
        """Test usage check when over limit."""
        from app.core.rate_limit import check_and_increment_usage
        
        user_id = "test-user-id"
        profile_data = {
            "monthly_usage_count": 150,
            "monthly_usage_limit": 100,
        }
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=profile_data)
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                check_and_increment_usage(user_id)
            
            assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    @pytest.mark.unit
    def test_check_usage_profile_not_found(self):
        """Test usage check when user profile doesn't exist."""
        from app.core.rate_limit import check_and_increment_usage
        
        user_id = "nonexistent-user"
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                check_and_increment_usage(user_id)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestGetUserUsageStats:
    """Tests for getting user usage statistics."""
    
    @pytest.mark.unit
    def test_get_usage_stats_success(self):
        """Test getting usage stats."""
        from app.core.rate_limit import get_user_usage_stats
        
        user_id = "test-user-id"
        profile_data = {
            "monthly_usage_count": 75,
            "monthly_usage_limit": 100,
        }
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=profile_data)
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            stats = get_user_usage_stats(user_id)
            
            assert stats.monthly_usage_count == 75
            assert stats.monthly_usage_limit == 100
            assert stats.remaining == 25
    
    @pytest.mark.unit
    def test_get_usage_stats_no_limit(self):
        """Test getting usage stats when no limit is set."""
        from app.core.rate_limit import get_user_usage_stats
        
        user_id = "test-user-id"
        profile_data = {
            "monthly_usage_count": 10,
            "subscription_tier": "free",  # Free tier has 10 limit
            # monthly_usage_limit is missing, should default based on tier
        }
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=profile_data)
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            stats = get_user_usage_stats(user_id)
            
            assert stats.monthly_usage_count == 10
            assert stats.monthly_usage_limit == 10  # Free tier limit
            assert stats.remaining == 0


class TestRateLimitDependency:
    """Tests for rate limit dependency."""
    
    @pytest.mark.unit
    def test_rate_limit_dependency_allows_request(self, mock_request):
        """Test rate limit dependency allows request within limit."""
        from app.core.rate_limit import rate_limit_dependency, RateLimiter
        
        # Create fresh limiter
        fresh_limiter = RateLimiter(requests=100, window=3600)
        
        mock_request.client.host = "192.168.1.1"
        
        with patch('app.core.rate_limit.rate_limiter', fresh_limiter):
            result = rate_limit_dependency(mock_request)
            assert result is True
    
    @pytest.mark.unit
    def test_rate_limit_dependency_blocks_excess(self, mock_request):
        """Test rate limit dependency blocks excess requests."""
        from app.core.rate_limit import rate_limit_dependency, RateLimiter
        
        # Create limiter with very low limit
        strict_limiter = RateLimiter(requests=1, window=3600)
        
        # Set up the request properly
        mock_request.client.host = "192.168.1.1"
        mock_request.state.user_id = None
        
        # Get the key that will be used
        key = "192.168.1.1"
        strict_limiter.is_allowed(key)  # Use up the one allowed request
        
        with patch('app.core.rate_limit.rate_limiter', strict_limiter):
            with pytest.raises(HTTPException) as exc_info:
                rate_limit_dependency(mock_request)
            
            assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            assert "rate limit" in str(exc_info.value.detail).lower()


class TestUsageTrackingMiddleware:
    """Tests for usage tracking middleware."""
    
    @pytest.mark.unit
    def test_middleware_tracks_content_endpoints(self):
        """Test middleware tracks content creation endpoints."""
        from app.core.rate_limit import UsageTrackingMiddleware
        
        middleware = UsageTrackingMiddleware(None)
        
        # Should track content endpoints
        assert middleware._should_track("/api/v1/content") is True
        assert middleware._should_track("/api/v1/content/123/generate") is True
        
        # Should not track other endpoints
        assert middleware._should_track("/api/v1/projects") is False
        assert middleware._should_track("/api/v1/auth/me") is False
        assert middleware._should_track("/health") is False


class TestLogUsageEvent:
    """Tests for usage event logging."""
    
    @pytest.mark.unit
    def test_log_usage_event_success(self):
        """Test successful usage event logging."""
        from app.core.rate_limit import log_usage_event
        
        user_id = "test-user-id"
        event_type = "content_generation"
        tokens_used = 150
        
        mock_client = MagicMock()
        mock_client.table.return_value.insert.return_value.execute.return_value = \
            create_mock_supabase_response(data=[{"id": "log-1"}])
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            # Should not raise
            log_usage_event(user_id, event_type, tokens_used)
            
            # Verify insert was called
            mock_client.table.assert_called_with("usage_logs")
    
    @pytest.mark.unit
    def test_log_usage_event_no_tokens(self):
        """Test logging event without token count."""
        from app.core.rate_limit import log_usage_event
        
        user_id = "test-user-id"
        event_type = "api_request"
        
        mock_client = MagicMock()
        mock_client.table.return_value.insert.return_value.execute.return_value = \
            create_mock_supabase_response(data=[{"id": "log-1"}])
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            log_usage_event(user_id, event_type, None)
            
            # Should complete without error
            mock_client.table.assert_called_once()
    
    @pytest.mark.unit
    def test_log_usage_event_failure_silent(self):
        """Test that logging failures are silent."""
        from app.core.rate_limit import log_usage_event
        
        user_id = "test-user-id"
        event_type = "content_generation"
        
        mock_client = MagicMock()
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            # Should not raise exception
            log_usage_event(user_id, event_type, 100)


class TestGetUsageHistory:
    """Tests for getting usage history."""
    
    @pytest.mark.unit
    def test_get_usage_history_success(self):
        """Test getting usage history."""
        from app.core.rate_limit import get_usage_history
        
        user_id = "test-user-id"
        history_data = [
            {"id": "log-1", "event_type": "content_generation", "tokens_used": 150},
            {"id": "log-2", "event_type": "content_generation", "tokens_used": 200},
        ]
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = \
            create_mock_supabase_response(data=history_data)
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            history = get_usage_history(user_id, limit=10)
            
            assert len(history) == 2
            assert history[0]["event_type"] == "content_generation"
    
    @pytest.mark.unit
    def test_get_usage_history_empty(self):
        """Test getting empty usage history."""
        from app.core.rate_limit import get_usage_history
        
        user_id = "test-user-id"
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = \
            create_mock_supabase_response(data=[])
        
        with patch('app.core.rate_limit.get_supabase_client', return_value=mock_client):
            history = get_usage_history(user_id)
            
            assert history == []


class TestUsageStatsModel:
    """Tests for UsageStats model."""
    
    @pytest.mark.unit
    def test_usage_stats_model_creation(self):
        """Test UsageStats model creation."""
        from app.core.rate_limit import UsageStats
        from datetime import datetime, timezone
        
        stats = UsageStats(
            monthly_usage_count=50,
            monthly_usage_limit=100,
            remaining=50,
            reset_at=datetime.now(timezone.utc)
        )
        
        assert stats.monthly_usage_count == 50
        assert stats.monthly_usage_limit == 100
        assert stats.remaining == 50
        assert stats.reset_at is not None
    
    @pytest.mark.unit
    def test_usage_stats_optional_reset(self):
        """Test UsageStats with optional reset_at."""
        from app.core.rate_limit import UsageStats
        
        stats = UsageStats(
            monthly_usage_count=10,
            monthly_usage_limit=100,
            remaining=90,
        )
        
        assert stats.reset_at is None


class TestRateLimitConfig:
    """Tests for RateLimitConfig."""
    
    @pytest.mark.unit
    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig default values from settings."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Should have default values from settings
        assert settings.RATE_LIMIT_REQUESTS == 1000  # From test env
        assert settings.RATE_LIMIT_WINDOW == 3600  # From test env
