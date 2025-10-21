"""
Tests for accounts serializers.

This module contains tests for user registration, profile update, and password change serializers.
"""

import pytest

pytestmark = pytest.mark.django_db

from accounts.serializers import (UserProfileSerializer,
                                  UserRegistrationSerializer, UserSerializer)
from django.contrib.auth.models import User
from rest_framework import serializers


class TestUserRegistrationSerializer:
    """Tests for UserRegistrationSerializer."""

    def test_validate_username_empty(self):
        """Test username validation with empty username."""
        serializer = UserRegistrationSerializer()
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_username("")
        
        assert "Username cannot be empty" in str(exc_info.value)

    def test_validate_username_whitespace_only(self):
        """Test username validation with whitespace-only username."""
        serializer = UserRegistrationSerializer()
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_username("   ")
        
        assert "Username cannot be empty" in str(exc_info.value)

    def test_validate_username_too_short(self):
        """Test username validation with username too short."""
        serializer = UserRegistrationSerializer()
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_username("ab")
        
        assert "Username must be at least 3 characters long" in str(exc_info.value)

    def test_validate_username_duplicate(self, user):
        """Test username validation with duplicate username."""
        serializer = UserRegistrationSerializer()
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_username(user.username)
        
        assert "A user with this username already exists" in str(exc_info.value)

    def test_validate_username_success(self):
        """Test username validation with valid username."""
        serializer = UserRegistrationSerializer()
        result = serializer.validate_username("newuser")
        assert result == "newuser"

    def test_validate_username_strips_whitespace(self):
        """Test username validation strips whitespace."""
        serializer = UserRegistrationSerializer()
        result = serializer.validate_username("  newuser  ")
        assert result == "newuser"


class TestUserProfileSerializer:
    """Tests for UserProfileSerializer."""

    def test_validate_username_empty(self, user):
        """Test username validation with empty username."""
        serializer = UserProfileSerializer(instance=user)
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_username("")
        
        assert "Username cannot be empty" in str(exc_info.value)

    def test_validate_username_whitespace_only(self, user):
        """Test username validation with whitespace-only username."""
        serializer = UserProfileSerializer(instance=user)
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_username("   ")
        
        assert "Username cannot be empty" in str(exc_info.value)

    def test_validate_username_too_short(self, user):
        """Test username validation with username too short."""
        serializer = UserProfileSerializer(instance=user)
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_username("ab")
        
        assert "Username must be at least 3 characters long" in str(exc_info.value)

    def test_validate_username_duplicate(self, user):
        """Test username validation with duplicate username."""
        # Create another user
        User.objects.create_user(username="otheruser", email="other@example.com")
        
        serializer = UserProfileSerializer(instance=user)
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_username("otheruser")
        
        assert "A user with this username already exists" in str(exc_info.value)

    def test_validate_username_same_user(self, user):
        """Test username validation with same user's current username."""
        serializer = UserProfileSerializer(instance=user)
        result = serializer.validate_username(user.username)
        assert result == user.username

    def test_validate_username_success(self, user):
        """Test username validation with valid new username."""
        serializer = UserProfileSerializer(instance=user)
        result = serializer.validate_username("newusername")
        assert result == "newusername"

    def test_validate_username_strips_whitespace(self, user):
        """Test username validation strips whitespace."""
        serializer = UserProfileSerializer(instance=user)
        result = serializer.validate_username("  newusername  ")
        assert result == "newusername"

    def test_validate_email_duplicate(self, user):
        """Test email validation with duplicate email."""
        # Create another user
        User.objects.create_user(username="otheruser", email="other@example.com")
        
        serializer = UserProfileSerializer(instance=user)
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_email("other@example.com")
        
        assert "A user with this email already exists" in str(exc_info.value)

    def test_validate_email_same_user(self, user):
        """Test email validation with same user's current email."""
        serializer = UserProfileSerializer(instance=user)
        result = serializer.validate_email(user.email)
        assert result == user.email

    def test_validate_email_success(self, user):
        """Test email validation with valid new email."""
        serializer = UserProfileSerializer(instance=user)
        result = serializer.validate_email("newemail@example.com")
        assert result == "newemail@example.com"

    def test_validate_email_strips_and_lowercases(self, user):
        """Test email validation strips whitespace and lowercases."""
        serializer = UserProfileSerializer(instance=user)
        result = serializer.validate_email("  NEWEMAIL@EXAMPLE.COM  ")
        assert result == "newemail@example.com"

    def test_validate_email_empty(self, user):
        """Test email validation with empty email."""
        serializer = UserProfileSerializer(instance=user)
        result = serializer.validate_email("")
        assert result == ""

    def test_validate_email_none(self, user):
        """Test email validation with None email."""
        serializer = UserProfileSerializer(instance=user)
        result = serializer.validate_email(None)
        assert result is None


class TestUserSerializer:
    """Tests for UserSerializer."""

    def test_user_serializer_fields(self):
        """Test UserSerializer has correct fields."""
        serializer = UserSerializer()
        expected_fields = {'id', 'username', 'email', 'date_joined', 'last_login'}
        assert set(serializer.fields.keys()) == expected_fields

    def test_user_serializer_read_only_fields(self):
        """Test UserSerializer has correct read-only fields."""
        serializer = UserSerializer()
        assert 'id' in serializer.Meta.read_only_fields
        assert 'date_joined' in serializer.Meta.read_only_fields
        assert 'last_login' in serializer.Meta.read_only_fields

    def test_user_serializer_serialization(self, user):
        """Test UserSerializer serializes user correctly."""
        serializer = UserSerializer(user)
        data = serializer.data
        
        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['email'] == user.email
        assert data['date_joined'] is not None
        assert data['last_login'] is None  # New user hasn't logged in yet
