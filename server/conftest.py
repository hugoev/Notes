"""
Pytest configuration and fixtures for the Notes application.
"""
import pytest
from django.contrib.auth import get_user_model
from notes.models import Category, Note
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def category(user):
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        user=user
    )


@pytest.fixture
def note(user, category):
    """Create a test note."""
    return Note.objects.create(
        title='Test Note',
        content='This is a test note content.',
        user=user,
        category=category
    )


@pytest.fixture
def multiple_notes(user, category):
    """Create multiple test notes."""
    notes = []
    for i in range(5):
        note = Note.objects.create(
            title=f'Test Note {i+1}',
            content=f'This is test note content {i+1}.',
            user=user,
            category=category
        )
        notes.append(note)
    return notes


@pytest.fixture
def multiple_categories(user):
    """Create multiple test categories."""
    categories = []
    for i in range(3):
        category = Category.objects.create(
            name=f'Test Category {i+1}',
            user=user
        )
        categories.append(category)
    return categories
