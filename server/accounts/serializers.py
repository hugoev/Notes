"""
Serializers for the Accounts application.

This module contains serializers for user registration and authentication,
including validation for user data and password handling.
"""

from typing import Any, Dict

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles user creation with proper validation and password handling.
    """
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Confirm your password"
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm')
        read_only_fields = ('id',)
    
    def validate_username(self, value: str) -> str:
        """Validate username."""
        if not value or not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        
        value = value.strip()
        
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long."
            )
        
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        
        return value
    
    def validate_email(self, value: str) -> str:
        """Validate email."""
        if value:
            value = value.strip().lower()
            
            if User.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )
        
        return value
    
    def validate_password(self, value: str) -> str:
        """Validate password."""
        validate_password(value)
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the entire user instance."""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create a new user."""
        validated_data.pop('password_confirm', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read-only).
    
    Used for returning user information without sensitive data.
    """
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile updates.
    
    Allows users to update their profile information.
    """
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def validate_username(self, value: str) -> str:
        """Validate username for updates."""
        if not value or not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        
        value = value.strip()
        
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long."
            )
        
        # Check if username is taken by another user
        if User.objects.filter(username__iexact=value).exclude(
            pk=self.instance.pk
        ).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        
        return value
    
    def validate_email(self, value: str) -> str:
        """Validate email for updates."""
        if value:
            value = value.strip().lower()
            
            # Check if email is taken by another user
            if User.objects.filter(email__iexact=value).exclude(
                pk=self.instance.pk
            ).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )
        
        return value