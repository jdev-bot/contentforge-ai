"""
Tests for subscription tier enforcement and usage limits.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Mock the supabase client before importing app modules
mock_supabase = MagicMock()
mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock()

with patch.dict('sys.modules', {'supabase': MagicMock(), 'supabase.client': MagicMock()}):
    from app.core.rate_limit import (
        check_and_increment_usage,
        get_user_usage_stats,
        get_subscription_limit,
        check_monthly_reset,
        UsageStats,
        SUBSCRIPTION_LIMITS,
    )


class TestSubscriptionLimits:
    """Test subscription tier limits."""

    def test_free_tier_limit(self):
        """Test Free tier has 10 content/month limit."""
        assert get_subscription_limit("free") == 10
        assert SUBSCRIPTION_LIMITS["free"] == 10

    def test_pro_tier_limit(self):
        """Test Pro tier has 100 content/month limit."""
        assert get_subscription_limit("pro") == 100
        assert SUBSCRIPTION_LIMITS["pro"] == 100

    def test_agency_tier_unlimited(self):
        """Test Agency tier has unlimited (infinity) limit."""
        assert get_subscription_limit("agency") == float("inf")
        assert SUBSCRIPTION_LIMITS["agency"] == float("inf")

    def test_case_insensitive_tier_lookup(self):
        """Test tier lookup is case insensitive."""
        assert get_subscription_limit("FREE") == 10
        assert get_subscription_limit("Free") == 10
        assert get_subscription_limit("PRO") == 100
        assert get_subscription_limit("Agency") == float("inf")

    def test_unknown_tier_defaults_to_free(self):
        """Test unknown tier defaults to Free tier limit."""
        assert get_subscription_limit("unknown") == 10
        assert get_subscription_limit("") == 10


class TestMonthlyReset:
    """Test monthly usage reset functionality."""

    @patch('app.core.rate_limit.get_supabase_client')
    def test_reset_when_new_month(self, mock_get_client):
        """Test usage resets when entering a new month."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up mock to return a profile from last month
        last_month = (datetime.now() - timedelta(days=32)).isoformat()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "updated_at": last_month,
            "monthly_usage_count": 8
        }
        
        result = check_monthly_reset("user-123")
        
        # Should update the profile to reset usage
        mock_client.table.return_value.update.assert_called_once()
        call_args = mock_client.table.return_value.update.call_args
        assert call_args[0][0]["monthly_usage_count"] == 0
        assert result is True

    @patch('app.core.rate_limit.get_supabase_client')
    def test_no_reset_same_month(self, mock_get_client):
        """Test usage does not reset within the same month."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up mock to return a profile from this month
        this_month = datetime.now().isoformat()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "updated_at": this_month,
            "monthly_usage_count": 5
        }
        
        result = check_monthly_reset("user-123")
        
        # Should not update
        mock_client.table.return_value.update.assert_not_called()
        assert result is False


class TestUsageEnforcement:
    """Test usage enforcement logic."""

    @patch('app.core.rate_limit.get_supabase_client')
    @patch('app.core.rate_limit.check_monthly_reset')
    def test_free_user_under_limit_can_create(self, mock_reset, mock_get_client):
        """Test Free user under limit can create content."""
        mock_reset.return_value = False
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "subscription_tier": "free",
            "monthly_usage_count": 5,
            "monthly_usage_limit": 10
        }
        
        stats = check_and_increment_usage("user-123")
        
        assert stats.monthly_usage_count == 6
        assert stats.monthly_usage_limit == 10
        assert stats.remaining == 4
        assert stats.subscription_tier == "free"

    @patch('app.core.rate_limit.get_supabase_client')
    @patch('app.core.rate_limit.check_monthly_reset')
    @patch('app.core.rate_limit.log_usage_event')
    def test_free_user_at_limit_blocked(self, mock_log, mock_reset, mock_get_client):
        """Test Free user at limit cannot create content."""
        mock_reset.return_value = False
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "subscription_tier": "free",
            "monthly_usage_count": 10,
            "monthly_usage_limit": 10
        }
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            check_and_increment_usage("user-123")
        
        assert exc_info.value.status_code == 429
        assert "limit exceeded" in str(exc_info.value.detail).lower() or "limit reached" in str(exc_info.value.detail).lower()

    @patch('app.core.rate_limit.get_supabase_client')
    @patch('app.core.rate_limit.check_monthly_reset')
    @patch('app.core.rate_limit.log_usage_event')
    def test_pro_user_under_limit_can_create(self, mock_log, mock_reset, mock_get_client):
        """Test Pro user under limit can create content."""
        mock_reset.return_value = False
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "subscription_tier": "pro",
            "monthly_usage_count": 50,
            "monthly_usage_limit": 100
        }
        
        stats = check_and_increment_usage("user-123")
        
        assert stats.monthly_usage_count == 51
        assert stats.monthly_usage_limit == 100
        assert stats.remaining == 49

    @patch('app.core.rate_limit.get_supabase_client')
    @patch('app.core.rate_limit.check_monthly_reset')
    @patch('app.core.rate_limit.log_usage_event')
    def test_pro_user_at_limit_blocked(self, mock_log, mock_reset, mock_get_client):
        """Test Pro user at 100 limit cannot create content."""
        mock_reset.return_value = False
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "subscription_tier": "pro",
            "monthly_usage_count": 100,
            "monthly_usage_limit": 100
        }
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            check_and_increment_usage("user-123")
        
        assert exc_info.value.status_code == 429

    @patch('app.core.rate_limit.get_supabase_client')
    @patch('app.core.rate_limit.check_monthly_reset')
    @patch('app.core.rate_limit.log_usage_event')
    def test_agency_user_unlimited(self, mock_log, mock_reset, mock_get_client):
        """Test Agency user can create unlimited content."""
        mock_reset.return_value = False
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Agency tier uses float('inf') from SUBSCRIPTION_LIMITS
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "subscription_tier": "agency",
            "monthly_usage_count": 999,
            "monthly_usage_limit": float("inf")  # Unlimited from tier
        }
        
        stats = check_and_increment_usage("user-123")
        
        assert stats.monthly_usage_count == 1000
        assert stats.remaining == -1  # Unlimited flag


class TestUsageStats:
    """Test usage stats retrieval."""

    @patch('app.core.rate_limit.get_supabase_client')
    @patch('app.core.rate_limit.check_monthly_reset')
    def test_get_usage_stats_returns_correct_values(self, mock_reset, mock_get_client):
        """Test get_user_usage_stats returns correct values."""
        mock_reset.return_value = False
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "subscription_tier": "pro",
            "monthly_usage_count": 45,
            "monthly_usage_limit": 100
        }
        
        stats = get_user_usage_stats("user-123")
        
        assert stats.monthly_usage_count == 45
        assert stats.monthly_usage_limit == 100
        assert stats.remaining == 55
        assert stats.subscription_tier == "pro"

    @patch('app.core.rate_limit.get_supabase_client')
    @patch('app.core.rate_limit.check_monthly_reset')
    def test_get_usage_stats_handles_unlimited(self, mock_reset, mock_get_client):
        """Test get_user_usage_stats handles unlimited tier correctly."""
        mock_reset.return_value = False
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "subscription_tier": "agency",
            "monthly_usage_count": 500,
            "monthly_usage_limit": float("inf")  # Unlimited from tier
        }
        
        stats = get_user_usage_stats("user-123")
        
        assert stats.monthly_usage_count == 500
        assert stats.monthly_usage_limit == -1
        assert stats.remaining == -1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
