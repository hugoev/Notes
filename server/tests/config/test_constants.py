"""
Tests for config constants.

This module contains tests for application constants and configuration values.
"""

import pytest
from config.constants import (ACCESS_TOKEN_LIFETIME_MINUTES, ALLOWED_HOSTS,
                              API_PREFIX, API_VERSION, AUTH_RATE_LIMIT,
                              CORS_ALLOWED_ORIGINS, DEFAULT_ORDERING,
                              DEFAULT_PAGE_SIZE, FILTER_FIELDS,
                              GENERAL_RATE_LIMIT, MAX_CATEGORY_NAME_LENGTH,
                              MAX_NOTE_CONTENT_LENGTH, MAX_NOTE_TITLE_LENGTH,
                              MAX_PAGE_SIZE, ORDERING_FIELDS,
                              REFRESH_TOKEN_LIFETIME_DAYS, SEARCH_FIELDS)


class TestConstants:
    """Tests for application constants."""

    def test_api_configuration(self):
        """Test API configuration constants."""
        assert API_VERSION == 'v1'
        assert API_PREFIX == 'api/v1'

    def test_pagination_constants(self):
        """Test pagination configuration constants."""
        assert DEFAULT_PAGE_SIZE == 20
        assert MAX_PAGE_SIZE == 100
        assert DEFAULT_PAGE_SIZE < MAX_PAGE_SIZE

    def test_rate_limiting_constants(self):
        """Test rate limiting configuration constants."""
        assert AUTH_RATE_LIMIT == '5/minute'
        assert GENERAL_RATE_LIMIT == '100/hour'

    def test_note_configuration_constants(self):
        """Test note configuration constants."""
        assert MAX_NOTE_TITLE_LENGTH == 200
        assert MAX_NOTE_CONTENT_LENGTH == 10000
        assert MAX_CATEGORY_NAME_LENGTH == 100
        assert MAX_NOTE_TITLE_LENGTH < MAX_NOTE_CONTENT_LENGTH

    def test_search_configuration_constants(self):
        """Test search configuration constants."""
        assert SEARCH_FIELDS == ['title', 'content']
        assert ORDERING_FIELDS == ['created_at', 'updated_at', 'title']
        assert DEFAULT_ORDERING == ['-updated_at']
        assert len(SEARCH_FIELDS) > 0
        assert len(ORDERING_FIELDS) > 0

    def test_filter_configuration_constants(self):
        """Test filter configuration constants."""
        assert FILTER_FIELDS == ['category', 'is_pinned']
        assert len(FILTER_FIELDS) > 0

    def test_jwt_configuration_constants(self):
        """Test JWT configuration constants."""
        assert ACCESS_TOKEN_LIFETIME_MINUTES == 60
        assert REFRESH_TOKEN_LIFETIME_DAYS == 7
        assert ACCESS_TOKEN_LIFETIME_MINUTES > 0
        assert REFRESH_TOKEN_LIFETIME_DAYS > 0

    def test_cors_configuration_constants(self):
        """Test CORS configuration constants."""
        assert CORS_ALLOWED_ORIGINS == [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        assert len(CORS_ALLOWED_ORIGINS) > 0
        assert all(origin.startswith('http://') for origin in CORS_ALLOWED_ORIGINS)

    def test_security_configuration_constants(self):
        """Test security configuration constants."""
        assert ALLOWED_HOSTS == ['localhost', '127.0.0.1', '0.0.0.0', 'backend']
        assert len(ALLOWED_HOSTS) > 0
        assert 'localhost' in ALLOWED_HOSTS
        assert '127.0.0.1' in ALLOWED_HOSTS

    def test_constants_are_strings_or_numbers(self):
        """Test that constants have appropriate types."""
        # String constants
        assert isinstance(API_VERSION, str)
        assert isinstance(API_PREFIX, str)
        assert isinstance(AUTH_RATE_LIMIT, str)
        assert isinstance(GENERAL_RATE_LIMIT, str)
        
        # Numeric constants
        assert isinstance(DEFAULT_PAGE_SIZE, int)
        assert isinstance(MAX_PAGE_SIZE, int)
        assert isinstance(MAX_NOTE_TITLE_LENGTH, int)
        assert isinstance(MAX_NOTE_CONTENT_LENGTH, int)
        assert isinstance(MAX_CATEGORY_NAME_LENGTH, int)
        assert isinstance(ACCESS_TOKEN_LIFETIME_MINUTES, int)
        assert isinstance(REFRESH_TOKEN_LIFETIME_DAYS, int)
        
        # List constants
        assert isinstance(SEARCH_FIELDS, list)
        assert isinstance(ORDERING_FIELDS, list)
        assert isinstance(DEFAULT_ORDERING, list)
        assert isinstance(FILTER_FIELDS, list)
        assert isinstance(CORS_ALLOWED_ORIGINS, list)
        assert isinstance(ALLOWED_HOSTS, list)

    def test_constants_have_positive_values(self):
        """Test that numeric constants have positive values."""
        assert DEFAULT_PAGE_SIZE > 0
        assert MAX_PAGE_SIZE > 0
        assert MAX_NOTE_TITLE_LENGTH > 0
        assert MAX_NOTE_CONTENT_LENGTH > 0
        assert MAX_CATEGORY_NAME_LENGTH > 0
        assert ACCESS_TOKEN_LIFETIME_MINUTES > 0
        assert REFRESH_TOKEN_LIFETIME_DAYS > 0

    def test_constants_are_consistent(self):
        """Test that related constants are consistent."""
        # Page size constraints
        assert DEFAULT_PAGE_SIZE <= MAX_PAGE_SIZE
        
        # Content length constraints
        assert MAX_NOTE_TITLE_LENGTH < MAX_NOTE_CONTENT_LENGTH
        
        # Token lifetime constraints
        assert ACCESS_TOKEN_LIFETIME_MINUTES < (REFRESH_TOKEN_LIFETIME_DAYS * 24 * 60)
