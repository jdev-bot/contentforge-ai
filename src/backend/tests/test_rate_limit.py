"""
Tests for rate limiting and usage tracking.
"""
import pytest
import time
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.core.rate_limit import (
    RateLimiter,
    check_and_increment_usage,
    get_user_usage_stats,
    log_usage_event,
    UsageStats,
)


class TestRateLimiter:
    """Test the RateLimiter class."""
    
    def test_rate_limiter_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed."""
        limiter = RateLimiter(requests=5, window=60)
        key = "test_key"
        
        # Should allow 5 requests
        for _ in range(5):
            assert limiter.is_allowed(key) is True
    
    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test that requests over the limit are blocked."""
        limiter = RateLimiter(requests=3, window=60)
        key = "test_key"
        
        # Allow 3 requests
        for _ in range(3):
            assert limiter.is_allowed(key) is True
        
        # 4th request should be blocked
        assert limiter.is_allowed(key) is False
    
    def test_rate_limiter_remaining_count(self):
        """Test remaining count calculation."""
        limiter = RateLimiter(requests=10, window=60)
        key = "test_key"
        
        assert limiter.get_remaining(key) == 10
        
        limiter.is_allowed(key)
        assert limiter.get_remaining(key) == 9
        
        for _ in range(5):
            limiter.is_allowed(key)
        assert limiter.get_remaining(key) == 4
    
    def test_rate_limiter_window_expiry(self):
        """Test that old requests are cleared after window expires."""
        limiter = RateLimiter(requests=2, window=1)  # 1 second window
        key = "test_key"
        
        # Use up the limit
        limiter.is_allowed(key)
        limiter.is_allowed(key)
        assert limiter.is_allowed(key) is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.is_allowed(key) is True
    
    def test_rate_limiter_different_keys(self):
        """Test that different keys have independent limits."""
        limiter = RateLimiter(requests=2, window=60)
        
        # Use up limit for key1
        limiter.is_allowed("key1")
        limiter.is_allowed("key1")
        assert limiter.is_allowed("key1") is False
        
        # key2 should still have its full limit
        assert limiter.is_allowed("key2") is True
        assert limiter.is_allowed("key2") is True
        assert limiter.is_allowed("key2") is False


class TestUsageTracking:
    """Test usage tracking functions."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        with patch("app.core.rate_limit.get_supabase_client") as mock:
            supabase_mock = MagicMock()
            mock.return_value = supabase_mock
            yield supabase_mock
    
    def test_get_user_usage_stats(self, mock_supabase):
        """Test getting user usage statistics."""
        user_id = str(uuid4())
        
        result_mock = MagicMock()
        result_mock.data = {
            "monthly_usage_count": 45,
            "monthly_usage_limit": 100,
        }
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = result_mock
        
        stats = get_user_usage_stats(user_id)
        
        assert stats.monthly_usage_count == 45
        assert stats.monthly_usage_limit == 100
        assert stats.remaining == 55
    
    def test_get_user_usage_stats_not_found(self, mock_supabase):
        """Test getting stats for non-existent user."""
        user_id = str(uuid4())
        
        result_mock = MagicMock()
        result_mock.data = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = result_mock
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            get_user_usage_stats(user_id)
        
        assert exc_info.value.status_code == 404
    
    def test_log_usage_event(self, mock_supabase):
        """Test logging a usage event."""
        user_id = str(uuid4())
        event_type = "content_generation"
        tokens_used = 150
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        
        log_usage_event(user_id, event_type, tokens_used)
        
        # Verify insert was called with correct data
        call_args = mock_supabase.table.return_value.insert.call_args[0][0]
        assert call_args["user_id"] == user_id
        assert call_args["event_type"] == event_type
        assert call_args["tokens_used"] == tokens_used
    
    def test_check_and_increment_usage_under_limit(self, mock_supabase):
        """Test incrementing usage when under limit."""
        user_id = str(uuid4())
        
        # Mock profile lookup - user under limit
        profile_result = MagicMock()
        profile_result.data = {
            "monthly_usage_count": 50,
            "monthly_usage_limit": 100,
        }
        
        # Mock update result
        update_result = MagicMock()
        update_result.data = [{
            "monthly_usage_count": 51,
            "monthly_usage_limit": 100,
        }]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_result
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = update_result
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        
        stats = check_and_increment_usage(user_id)
        
        assert stats.monthly_usage_count == 51
        assert stats.remaining == 49
    
    def test_check_and_increment_usage_over_limit(self, mock_supabase):
        """Test that usage is rejected when over limit."""
        user_id = str(uuid4())
        
        # Mock profile lookup - user at limit
        profile_result = MagicMock()
        profile_result.data = {
            "monthly_usage_count": 100,
            "monthly_usage_limit": 100,
        }
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_result
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            check_and_increment_usage(user_id)
        
        assert exc_info.value.status_code == 429
        assert "Monthly usage limit exceeded" in exc_info.value.detail


class TestUsageStatsModel:
    """Test UsageStats Pydantic model."""
    
    def test_usage_stats_creation(self):
        """Test creating UsageStats instance."""
        stats = UsageStats(
            monthly_usage_count=25,
            monthly_usage_limit=100,
            remaining=75,
            reset_at=datetime.utcnow()
        )
        
        assert stats.monthly_usage_count == 25
        assert stats.monthly_usage_limit == 100
        assert stats.remaining == 75
        assert stats.reset_at is not None
    
    def test_usage_stats_default_reset_at(self):
        """Test UsageStats with optional reset_at."""
        stats = UsageStats(
            monthly_usage_count=10,
            monthly_usage_limit=50,
            remaining=40,
        )
        
        assert stats.reset_at is None
