"""
Serializers for the Notes application.

This module contains serializers for converting model instances to JSON
and handling validation for API requests and responses.
"""

from typing import Any, Dict, Optional

from config.constants import MAX_CATEGORY_NAME_LENGTH, MAX_NOTE_TITLE_LENGTH
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Category, Note


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    
    Handles serialization and validation of category data,
    including user ownership validation.
    """
    
    notes_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at', 'notes_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value: str) -> str:
        """Validate category name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        
        # Trim whitespace
        value = value.strip()
        
        if len(value) > MAX_CATEGORY_NAME_LENGTH:
            raise serializers.ValidationError(
                f"Category name cannot exceed {MAX_CATEGORY_NAME_LENGTH} characters."
            )
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the entire category instance."""
        name = attrs.get('name')
        user = self.context['request'].user
        
        if name:
            # Check for duplicate names within the same user
            existing_category = Category.objects.filter(
                name__iexact=name,
                user=user
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_category.exists():
                raise serializers.ValidationError({
                    'name': f"A category with the name '{name}' already exists."
                })
        
        return attrs


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for category lists.
    
    Used when listing categories to reduce payload size.
    """
    
    notes_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'notes_count']


class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for Note model.
    
    Handles serialization and validation of note data,
    including category relationship validation.
    """
    
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
        help_text="Name of the associated category"
    )
    word_count = serializers.ReadOnlyField(
        source='word_count',
        help_text="Number of words in the note content"
    )
    character_count = serializers.ReadOnlyField(
        source='character_count',
        help_text="Number of characters in the note content"
    )
    is_recent = serializers.ReadOnlyField(
        source='is_recent',
        help_text="Whether the note was created within the last 7 days"
    )
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at',
            'category', 'category_name', 'is_pinned', 'word_count',
            'character_count', 'is_recent'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value: str) -> str:
        """Validate note title."""
        if not value or not value.strip():
            raise serializers.ValidationError("Note title cannot be empty.")
        
        # Trim whitespace
        value = value.strip()
        
        if len(value) > MAX_NOTE_TITLE_LENGTH:
            raise serializers.ValidationError(
                f"Note title cannot exceed {MAX_NOTE_TITLE_LENGTH} characters."
            )
        
        return value
    
    def validate_content(self, value: str) -> str:
        """Validate note content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Note content cannot be empty.")
        
        return value.strip()
    
    def validate_category(self, value: Optional[Category]) -> Optional[Category]:
        """Validate category relationship."""
        if value:
            user = self.context['request'].user
            if value.user != user:
                raise serializers.ValidationError(
                    "You can only assign notes to your own categories."
                )
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the entire note instance."""
        # Additional validation can be added here
        return attrs


class NoteListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for note lists.
    
    Used when listing notes to reduce payload size.
    """
    
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    word_count = serializers.ReadOnlyField()
    is_recent = serializers.ReadOnlyField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at',
            'category', 'category_name', 'is_pinned',
            'word_count', 'is_recent'
        ]


class NoteCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new notes.
    
    Simplified serializer focused on note creation with minimal fields.
    """
    
    class Meta:
        model = Note
        fields = ['title', 'content', 'category', 'is_pinned']
    
    def validate_title(self, value: str) -> str:
        """Validate note title for creation."""
        if not value or not value.strip():
            raise serializers.ValidationError("Note title cannot be empty.")
        
        return value.strip()
    
    def validate_content(self, value: str) -> str:
        """Validate note content for creation."""
        if not value or not value.strip():
            raise serializers.ValidationError("Note content cannot be empty.")
        
        return value.strip()


class NoteUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing notes.
    
    Allows partial updates and includes validation for updates.
    """
    
    class Meta:
        model = Note
        fields = ['title', 'content', 'category', 'is_pinned']
    
    def validate_title(self, value: str) -> str:
        """Validate note title for updates."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Note title cannot be empty.")
        
        return value.strip() if value else value
    
    def validate_content(self, value: str) -> str:
        """Validate note content for updates."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Note content cannot be empty.")
        
        return value.strip() if value else value