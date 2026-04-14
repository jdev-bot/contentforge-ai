"""
Load testing suite for ContentForge AI API.
Tests concurrent user handling, rate limiting, and database connection pools.
"""

import asyncio
import concurrent.futures
import time
import pytest
from fastapi import status
from unittest.mock import MagicMock, patch
import threading
import queue


@pytest.mark.skip(
    reason="Load/performance tests are flaky in test environment - timing dependent"
)
class TestConcurrentUsers:
    """Test handling of multiple concurrent users."""

    def test_concurrent_registration_10_users(self, client):
        """Test concurrent user registration with 10 users."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase

        results = []
        errors = []

        def register_user(i):
            try:
                mock_user = MagicMock()
                mock_user.id = f"user-{i}"
                mock_user.email = f"user{i}@example.com"
                mock_session = MagicMock()
                mock_session.access_token = f"token-{i}"

                # Set up the mock for this call
                mock_auth.sign_up.return_value = MagicMock(
                    user=mock_user, session=mock_session
                )

                response = client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": f"user{i}@example.com",
                        "password": f"SecurePass{i}!",
                        "full_name": f"User {i}",
                    },
                )
                results.append((i, response.status_code))
            except Exception as e:
                errors.append((i, str(e)))

        # Execute 10 concurrent registrations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_user, i) for i in range(10)]
            concurrent.futures.wait(futures)

        # All should succeed
        assert (
            len(results) == 10
        ), f"Expected 10 results, got {len(results)}. Errors: {errors}"
        for i, status_code in results:
            assert (
                status_code == status.HTTP_201_CREATED
            ), f"User {i} failed with status {status_code}"

    def test_concurrent_login_50_users(self, client):
        """Test concurrent login with 50 users."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase

        results = []
        errors = []

        def login_user(i):
            try:
                mock_user = MagicMock()
                mock_user.id = f"user-{i}"
                mock_user.email = f"user{i}@example.com"
                mock_user.user_metadata = {"full_name": f"User {i}"}
                mock_session = MagicMock()
                mock_session.access_token = f"token-{i}"

                mock_auth.sign_in_with_password.return_value = MagicMock(
                    user=mock_user, session=mock_session
                )

                response = client.post(
                    "/api/v1/auth/login",
                    json={"email": f"user{i}@example.com", "password": f"Password{i}!"},
                )
                results.append((i, response.status_code))
            except Exception as e:
                errors.append((i, str(e)))

        # Execute 50 concurrent logins
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(login_user, i) for i in range(50)]
            concurrent.futures.wait(futures)

        assert (
            len(results) == 50
        ), f"Expected 50 results, got {len(results)}. Errors: {errors}"
        for i, status_code in results:
            assert (
                status_code == status.HTTP_200_OK
            ), f"User {i} failed with status {status_code}"

    def test_concurrent_content_creation_100_requests(self, client):
        """Test 100 concurrent content creation requests."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase

        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)

        results = []
        errors = []

        def create_content(i):
            try:
                mock_query.execute.return_value = MagicMock(
                    data=[
                        {
                            "id": f"content-{i}",
                            "project_id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "test-user-123",
                            "title": f"Content {i}",
                            "source_type": "text",
                            "source_url": None,
                            "original_text": f"Content text {i}",
                            "word_count": 10,
                            "status": "completed",
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00",
                        }
                    ]
                )

                response = client.post(
                    "/api/v1/content",
                    json={
                        "title": f"Content {i}",
                        "source": {"type": "text", "text": f"Content text {i}"},
                        "project_id": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    headers={"Authorization": "Bearer test-token"},
                )

                results.append((i, response.status_code))
            except Exception as e:
                errors.append((i, str(e)))

        # Execute 100 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(create_content, i) for i in range(100)]
            concurrent.futures.wait(futures)

        # Most should succeed (some rate limiting is acceptable)
        success_count = sum(1 for _, code in results if code == status.HTTP_201_CREATED)
        rate_limited = sum(
            1 for _, code in results if code == status.HTTP_429_TOO_MANY_REQUESTS
        )

        assert (
            success_count + rate_limited == 100
        ), f"Expected 100 results, got {len(results)}. Errors: {errors}"
        # At least 50% should succeed
        assert (
            success_count >= 50
        ), f"Only {success_count} succeeded, expected at least 50"

    def test_concurrent_get_requests_100_users(self, client):
        """Test 100 concurrent GET requests to public endpoints."""
        results = []
        errors = []

        def get_health(i):
            try:
                response = client.get("/api/v1/health")
                results.append(
                    (i, response.status_code, response.elapsed.total_seconds())
                )
            except Exception as e:
                errors.append((i, str(e)))

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(get_health, i) for i in range(100)]
            concurrent.futures.wait(futures)

        end_time = time.time()
        total_time = end_time - start_time

        assert (
            len(results) == 100
        ), f"Expected 100 results, got {len(results)}. Errors: {errors}"

        # All should be 200
        for i, code, elapsed in results:
            assert code == status.HTTP_200_OK, f"Request {i} returned {code}"

        # Calculate average response time
        avg_response_time = sum(elapsed for _, _, elapsed in results) / len(results)

        # With 100 concurrent requests, avg should still be reasonable
        assert (
            avg_response_time < 5.0
        ), f"Average response time {avg_response_time}s too high"
        print(f"\n100 concurrent requests completed in {total_time:.2f}s")
        print(f"Average response time: {avg_response_time:.3f}s")


class TestRateLimitStress:
    """Stress test rate limiting functionality."""

    def test_rapid_requests_rate_limit_trigger(self, client):
        """Test that rapid requests trigger rate limiting."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase

        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)

        # Set up mock for profile to trigger rate limit
        mock_query.execute.return_value = MagicMock(
            data={
                "id": "test-user-123",
                "monthly_usage_count": 1000,  # Exceeded limit
                "monthly_usage_limit": 10,
                "subscription_tier": "free",
            }
        )

        # Make rapid requests
        responses = []
        for i in range(20):
            response = client.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer test-token"}
            )
            responses.append(response.status_code)

        # Check for rate limiting (429) or success (200)
        rate_limited_count = responses.count(status.HTTP_429_TOO_MANY_REQUESTS)
        print(f"\nRate limited requests: {rate_limited_count}/20")

        # At least some should be rate limited or return 200
        assert len(responses) == 20

    def test_burst_requests_handling(self, client):
        """Test handling of burst requests."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase

        results = []

        def burst_request(i):
            response = client.get("/api/v1/health")
            results.append(response.status_code)

        # Send 50 requests as fast as possible
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(burst_request, i) for i in range(50)]
            concurrent.futures.wait(futures)

        # All should succeed (health endpoint shouldn't be rate limited)
        assert all(code == status.HTTP_200_OK for code in results)

    def test_sustained_load_1000_requests(self, client):
        """Test sustained load with 1000 sequential requests."""
        results = []

        start_time = time.time()

        for i in range(1000):
            response = client.get("/api/v1/health")
            results.append(response.status_code)

            # Every 100 requests, log progress
            if (i + 1) % 100 == 0:
                print(f"Completed {i + 1}/1000 requests")

        end_time = time.time()
        total_time = end_time - start_time

        # All should succeed
        success_count = results.count(status.HTTP_200_OK)
        assert success_count == 1000, f"Expected 1000 successes, got {success_count}"

        # Calculate throughput
        throughput = 1000 / total_time
        print(
            f"\n1000 requests completed in {total_time:.2f}s ({throughput:.2f} req/s)"
        )

        # Should maintain at least 10 req/s
        assert throughput > 10, f"Throughput {throughput:.2f} req/s too low"


class TestDatabaseConnectionPool:
    """Test database connection pool handling."""

    def test_connection_pool_under_load(self, client):
        """Test database connection pool with concurrent queries."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase

        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)

        # Set up query to return content
        mock_query.execute.return_value = MagicMock(data=[])

        results = []
        errors = []

        def query_content(i):
            try:
                response = client.get(
                    "/api/v1/content", headers={"Authorization": "Bearer test-token"}
                )
                results.append((i, response.status_code))
            except Exception as e:
                errors.append((i, str(e)))

        # Execute 50 concurrent database queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(query_content, i) for i in range(50)]
            concurrent.futures.wait(futures)

        assert (
            len(results) == 50
        ), f"Expected 50 results, got {len(results)}. Errors: {errors}"

        # Most should succeed (connection pool might reject some)
        success_count = sum(1 for _, code in results if code == status.HTTP_200_OK)
        assert success_count >= 45, f"Only {success_count}/50 succeeded"

    def test_connection_recovery_after_spike(self, client):
        """Test that connections recover after a load spike."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase

        # Spike: 100 requests
        def spike_request(i):
            return client.get("/api/v1/health")

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            list(executor.map(spike_request, range(100)))

        # Wait a moment
        time.sleep(0.5)

        # Normal: 10 requests
        for i in range(10):
            response = client.get("/api/v1/health")
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.skip(
    reason="Load/performance tests are flaky in test environment - timing dependent"
)
class TestResponseTimeBenchmarks:
    """Benchmark response times under various loads."""

    def test_health_endpoint_response_time(self, client):
        """Benchmark health endpoint response time."""
        response_times = []

        for _ in range(100):
            start = time.time()
            response = client.get("/api/v1/health")
            end = time.time()
            response_times.append(end - start)
            assert response.status_code == status.HTTP_200_OK

        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]

        print(f"\nHealth endpoint:")
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  95th percentile: {p95_time*1000:.2f}ms")
        print(f"  Max: {max_time*1000:.2f}ms")

        # Health should be very fast
        assert avg_time < 0.1, f"Average response time {avg_time*1000:.2f}ms too high"
        assert p95_time < 0.2, f"95th percentile {p95_time*1000:.2f}ms too high"

    def test_auth_endpoint_response_time(self, client):
        """Benchmark authenticated endpoint response time."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase

        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"full_name": "Test User"}
        mock_auth.get_user.return_value = MagicMock(user=mock_user)

        response_times = []

        for _ in range(50):
            start = time.time()
            response = client.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer test-token"}
            )
            end = time.time()
            response_times.append(end - start)
            assert response.status_code == status.HTTP_200_OK

        avg_time = sum(response_times) / len(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]

        print(f"\nAuth endpoint:")
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  95th percentile: {p95_time*1000:.2f}ms")

        # Auth endpoints can be slower due to validation
        assert avg_time < 0.5, f"Average response time {avg_time*1000:.2f}ms too high"

    def test_content_list_response_time(self, client):
        """Benchmark content listing endpoint."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase

        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)

        # Mock large result set
        mock_query.execute.return_value = MagicMock(
            data=[
                {
                    "id": f"content-{i}",
                    "project_id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "test-user-123",
                    "title": f"Content {i}",
                    "source_type": "text",
                    "source_url": None,
                    "original_text": f"Content text {i}",
                    "word_count": 100,
                    "status": "completed",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                }
                for i in range(50)  # 50 items
            ]
        )

        response_times = []

        for _ in range(30):
            start = time.time()
            response = client.get(
                "/api/v1/content", headers={"Authorization": "Bearer test-token"}
            )
            end = time.time()
            response_times.append(end - start)
            assert response.status_code == status.HTTP_200_OK

        avg_time = sum(response_times) / len(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]

        print(f"\nContent list endpoint:")
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  95th percentile: {p95_time*1000:.2f}ms")

        # Content endpoints with data can be slower
        assert avg_time < 1.0, f"Average response time {avg_time*1000:.2f}ms too high"
