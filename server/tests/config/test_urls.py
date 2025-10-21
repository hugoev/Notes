"""
Tests for config URLs.

This module contains tests for URL configuration and routing.
"""

import pytest
from django.conf import settings
from django.test import TestCase
from django.urls import resolve, reverse


class TestURLConfiguration:
    """Tests for URL configuration."""

    def test_api_prefix_constant(self):
        """Test that API_PREFIX constant is correctly defined."""
        from config.constants import API_PREFIX
        assert API_PREFIX == 'api/v1'

    def test_admin_url_resolves(self):
        """Test that admin URL resolves correctly."""
        url = reverse('admin:index')
        assert url == '/admin/'

    def test_api_auth_token_url_resolves(self):
        """Test that API auth token URL resolves correctly."""
        url = reverse('token_obtain_pair')
        assert url == '/api/v1/auth/token/'

    def test_api_auth_token_refresh_url_resolves(self):
        """Test that API auth token refresh URL resolves correctly."""
        url = reverse('token_refresh')
        assert url == '/api/v1/auth/token/refresh/'

    def test_api_auth_register_url_resolves(self):
        """Test that API auth register URL resolves correctly."""
        url = reverse('user_register')
        assert url == '/api/v1/auth/register/'

    def test_api_users_profile_url_resolves(self):
        """Test that API users profile URL resolves correctly."""
        url = reverse('user_profile')
        assert url == '/api/v1/users/profile/'

    def test_api_users_change_password_url_resolves(self):
        """Test that API users change password URL resolves correctly."""
        url = reverse('change_password')
        assert url == '/api/v1/users/change-password/'

    def test_api_users_stats_url_resolves(self):
        """Test that API users stats URL resolves correctly."""
        url = reverse('user_stats')
        assert url == '/api/v1/users/stats/'

    def test_api_notes_list_url_resolves(self):
        """Test that API notes list URL resolves correctly."""
        url = reverse('note-list')
        assert url == '/api/v1/notes/'

    def test_api_notes_detail_url_resolves(self):
        """Test that API notes detail URL resolves correctly."""
        url = reverse('note-detail', kwargs={'pk': 1})
        assert url == '/api/v1/notes/1/'

    def test_api_categories_list_url_resolves(self):
        """Test that API categories list URL resolves correctly."""
        url = reverse('category-list')
        assert url == '/api/v1/categories/'

    def test_api_categories_detail_url_resolves(self):
        """Test that API categories detail URL resolves correctly."""
        url = reverse('category-detail', kwargs={'pk': 1})
        assert url == '/api/v1/categories/1/'

    def test_api_notes_pinned_url_resolves(self):
        """Test that API notes pinned URL resolves correctly."""
        url = reverse('note-pinned')
        assert url == '/api/v1/notes/pinned/'

    def test_api_notes_pin_url_resolves(self):
        """Test that API notes pin URL resolves correctly."""
        url = reverse('note-pin', kwargs={'pk': 1})
        assert url == '/api/v1/notes/1/pin/'

    def test_api_notes_unpin_url_resolves(self):
        """Test that API notes unpin URL resolves correctly."""
        url = reverse('note-unpin', kwargs={'pk': 1})
        assert url == '/api/v1/notes/1/unpin/'

    def test_api_notes_move_to_category_url_resolves(self):
        """Test that API notes move to category URL resolves correctly."""
        url = reverse('note-move-to-category', kwargs={'pk': 1})
        assert url == '/api/v1/notes/1/move_to_category/'

    def test_api_notes_recent_url_resolves(self):
        """Test that API notes recent URL resolves correctly."""
        url = reverse('note-recent')
        assert url == '/api/v1/notes/recent/'

    def test_api_notes_stats_url_resolves(self):
        """Test that API notes stats URL resolves correctly."""
        url = reverse('note-stats')
        assert url == '/api/v1/notes/stats/'

    def test_api_categories_notes_url_resolves(self):
        """Test that API categories notes URL resolves correctly."""
        url = reverse('category-notes', kwargs={'pk': 1})
        assert url == '/api/v1/categories/1/notes/'

    def test_url_patterns_include_api_prefix(self):
        """Test that all API URLs include the correct prefix."""
        api_urls = [
            reverse('token_obtain_pair'),
            reverse('token_refresh'),
            reverse('user_register'),
            reverse('user_profile'),
            reverse('change_password'),
            reverse('user_stats'),
            reverse('note-list'),
            reverse('category-list'),
        ]
        
        for url in api_urls:
            assert url.startswith('/api/v1/')

    def test_url_patterns_are_consistent(self):
        """Test that URL patterns follow consistent naming."""
        # Authentication URLs
        assert reverse('token_obtain_pair').endswith('/token/')
        assert reverse('token_refresh').endswith('/token/refresh/')
        assert reverse('user_register').endswith('/register/')
        
        # User management URLs
        assert reverse('user_profile').endswith('/profile/')
        assert reverse('change_password').endswith('/change-password/')
        assert reverse('user_stats').endswith('/stats/')
        
        # Notes URLs
        assert reverse('note-list').endswith('/notes/')
        assert reverse('note-pinned').endswith('/pinned/')
        assert reverse('note-recent').endswith('/recent/')
        assert reverse('note-stats').endswith('/stats/')
        
        # Categories URLs
        assert reverse('category-list').endswith('/categories/')

    def test_url_resolution_works(self):
        """Test that URL resolution works for key endpoints."""
        # Test that URLs resolve to correct views
        from config.urls import urlpatterns

        # Check that we have the expected number of URL patterns
        assert len(urlpatterns) > 0
        
        # Test that admin URL is included
        admin_urls = [pattern for pattern in urlpatterns if 'admin' in str(pattern)]
        assert len(admin_urls) > 0

    def test_rest_framework_urls_included(self):
        """Test that Django REST Framework browsable API URLs are included."""
        from config.urls import urlpatterns

        # Check for API auth URLs (Django REST Framework browsable API)
        api_auth_urls = [pattern for pattern in urlpatterns if 'api-auth' in str(pattern)]
        assert len(api_auth_urls) > 0

    def test_health_check_url_included(self):
        """Test that health check URL is included."""
        from config.urls import urlpatterns

        # Check for health check URL
        health_urls = [pattern for pattern in urlpatterns if 'health' in str(pattern)]
        assert len(health_urls) > 0
