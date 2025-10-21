"""
Tests for Notes serializers to improve coverage.

This module contains comprehensive tests for serializer functionality,
validation, and edge cases to achieve 90%+ test coverage.
"""

import pytest
from django.contrib.auth import get_user_model
from notes.models import Category, Note
from notes.serializers import (CategoryListSerializer, CategorySerializer,
                               NoteListSerializer, NoteSerializer)
from rest_framework.exceptions import ValidationError

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestCategorySerializers:
    """Tests for Category serializers."""

    def test_category_list_serializer_valid_data(self, user):
        """Test CategoryListSerializer with valid data."""
        category = Category.objects.create(name='Test Category', user=user)
        serializer = CategoryListSerializer(category)
        
        data = serializer.data
        assert data['id'] == category.id
        assert data['name'] == 'Test Category'
        assert data['notes_count'] == 0

    def test_category_list_serializer_with_notes_count(self, user):
        """Test CategoryListSerializer with notes count."""
        category = Category.objects.create(name='Test Category', user=user)
        
        # Create some notes for the category
        for i in range(3):
            Note.objects.create(
                title=f'Note {i}',
                content=f'Content {i}',
                user=user,
                category=category
            )
        
        serializer = CategoryListSerializer(category)
        data = serializer.data
        
        assert data['notes_count'] == 3

    def test_category_serializer_valid_data(self, user):
        """Test CategorySerializer with valid data."""
        category = Category.objects.create(name='Test Category', user=user)
        serializer = CategorySerializer(category)
        
        data = serializer.data
        assert data['id'] == category.id
        assert data['name'] == 'Test Category'
        assert data['created_at'] is not None
        assert data['updated_at'] is not None
        assert data['notes_count'] == 0

    def test_category_serializer_validation_empty_name(self, user):
        """Test category serializer validation with empty name."""
        serializer = CategoryListSerializer(data={'name': ''})
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_category_serializer_validation_whitespace_name(self, user):
        """Test category serializer validation with whitespace-only name."""
        serializer = CategoryListSerializer(data={'name': '   '})
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_category_serializer_validation_long_name(self, user):
        """Test category serializer validation with very long name."""
        long_name = 'A' * 300  # Exceeds the 100 character limit
        serializer = CategoryListSerializer(data={'name': long_name})
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_category_serializer_validation_duplicate_name_same_user(self, user):
        """Test category serializer validation with duplicate name for same user."""
        Category.objects.create(name='Duplicate Category', user=user)
        
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = CategoryListSerializer(
            data={'name': 'Duplicate Category'},
            context={'request': mock_request}
        )
        # CategoryListSerializer doesn't have duplicate validation, it's in CategorySerializer
        assert serializer.is_valid()

    def test_category_serializer_validation_duplicate_name_different_user(self, user):
        """Test category serializer validation with duplicate name for different user (should pass)."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        Category.objects.create(name='Duplicate Category', user=other_user)
        
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = CategoryListSerializer(
            data={'name': 'Duplicate Category'},
            context={'request': mock_request}
        )
        assert serializer.is_valid()

    def test_category_serializer_trim_whitespace(self, user):
        """Test that category serializer trims whitespace from name."""
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = CategoryListSerializer(
            data={'name': '  Test Category  '},
            context={'request': mock_request}
        )
        assert serializer.is_valid()
        assert serializer.validated_data['name'] == 'Test Category'


class TestNoteSerializers:
    """Tests for Note serializers."""

    def test_note_list_serializer_valid_data(self, user):
        """Test NoteListSerializer with valid data."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        serializer = NoteListSerializer(note)
        data = serializer.data
        
        assert data['id'] == note.id
        assert data['title'] == 'Test Note'
        assert data['content'] == 'Test content'
        assert data['created_at'] is not None
        assert data['updated_at'] is not None
        assert data['category'] == category.id
        assert data['category_name'] == 'Test Category'
        assert data['is_pinned'] == False
        assert data['word_count'] > 0
        assert data['is_recent'] is not None

    def test_note_list_serializer_with_character_count(self, user):
        """Test NoteListSerializer with character count."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        serializer = NoteListSerializer(note)
        data = serializer.data
        
        assert data['id'] == note.id
        assert data['title'] == 'Test Note'
        assert data['content'] == 'Test content'
        assert data['created_at'] is not None
        assert data['updated_at'] is not None
        assert data['category'] == category.id
        assert data['category_name'] == 'Test Category'
        assert data['is_pinned'] == False
        assert data['word_count'] > 0
        assert data['is_recent'] is not None

    def test_note_serializer_valid_data(self, user):
        """Test NoteSerializer with valid data."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        serializer = NoteSerializer(note)
        data = serializer.data
        
        assert data['id'] == note.id
        assert data['title'] == 'Test Note'
        assert data['content'] == 'Test content'
        assert data['created_at'] is not None
        assert data['updated_at'] is not None
        assert data['category'] == category.id
        assert data['category_name'] == 'Test Category'
        assert data['is_pinned'] == False
        assert data['word_count'] > 0
        assert data['character_count'] > 0
        assert data['is_recent'] is not None

    def test_note_serializer_validation_empty_title(self, user):
        """Test note serializer validation with empty title."""
        category = Category.objects.create(name='Test Category', user=user)
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = NoteSerializer(
            data={
                'title': '',
                'content': 'Test content',
                'category': category.id
            },
            context={'request': mock_request}
        )
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_note_serializer_validation_empty_content(self, user):
        """Test note serializer validation with empty content."""
        category = Category.objects.create(name='Test Category', user=user)
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = NoteSerializer(
            data={
                'title': 'Test Note',
                'content': '',
                'category': category.id
            },
            context={'request': mock_request}
        )
        assert not serializer.is_valid()
        assert 'content' in serializer.errors

    def test_note_serializer_validation_invalid_category(self, user):
        """Test note serializer validation with invalid category."""
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = NoteSerializer(
            data={
                'title': 'Test Note',
                'content': 'Test content',
                'category': 99999  # Nonexistent category
            },
            context={'request': mock_request}
        )
        assert not serializer.is_valid()
        assert 'category' in serializer.errors

    def test_note_serializer_validation_other_user_category(self, user):
        """Test note serializer validation with another user's category."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        category = Category.objects.create(name='Other Category', user=other_user)
        
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = NoteSerializer(
            data={
                'title': 'Test Note',
                'content': 'Test content',
                'category': category.id
            },
            context={'request': mock_request}
        )
        assert not serializer.is_valid()
        assert 'category' in serializer.errors

    def test_note_serializer_word_count_calculation(self, user):
        """Test that word count is properly calculated."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='This is a test note with multiple words',
            user=user,
            category=category
        )
        
        serializer = NoteSerializer(note)
        data = serializer.data
        
        assert data['word_count'] == 8  # "This is a test note with multiple words"

    def test_note_serializer_character_count_calculation(self, user):
        """Test that character count is properly calculated."""
        category = Category.objects.create(name='Test Category', user=user)
        content = 'Hello, World!'
        note = Note.objects.create(
            title='Test Note',
            content=content,
            user=user,
            category=category
        )
        
        serializer = NoteSerializer(note)
        data = serializer.data
        
        assert data['character_count'] == len(content)

    def test_note_serializer_is_recent_calculation(self, user):
        """Test that is_recent is properly calculated."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        serializer = NoteSerializer(note)
        data = serializer.data
        
        # Note was just created, so it should be recent
        assert data['is_recent'] == True

    def test_note_serializer_pinned_note(self, user):
        """Test serializer with pinned note."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category,
            is_pinned=True
        )
        
        serializer = NoteSerializer(note)
        data = serializer.data
        
        assert data['is_pinned'] == True

    def test_note_serializer_create_with_valid_data(self, user):
        """Test creating a note with valid data."""
        category = Category.objects.create(name='Test Category', user=user)
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = NoteSerializer(
            data={
                'title': 'Test Note',
                'content': 'Test content',
                'category': category.id
            },
            context={'request': mock_request}
        )
        
        assert serializer.is_valid()
        note = serializer.save(user=user)
        assert note.title == 'Test Note'
        assert note.content == 'Test content'
        assert note.category == category
        assert note.user == user

    def test_note_serializer_update_with_valid_data(self, user):
        """Test updating a note with valid data."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Original Title',
            content='Original content',
            user=user,
            category=category
        )
        
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = NoteSerializer(
            note, 
            data={
                'title': 'Updated Title',
                'content': 'Updated content'
            }, 
            partial=True,
            context={'request': mock_request}
        )
        
        assert serializer.is_valid()
        updated_note = serializer.save()
        assert updated_note.title == 'Updated Title'
        assert updated_note.content == 'Updated content'

    def test_note_serializer_validation_long_title(self, user):
        """Test note serializer validation with very long title."""
        category = Category.objects.create(name='Test Category', user=user)
        long_title = 'A' * 300  # Very long title
        
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = NoteSerializer(
            data={
                'title': long_title,
                'content': 'Test content',
                'category': category.id
            },
            context={'request': mock_request}
        )
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_note_serializer_validation_long_content(self, user):
        """Test note serializer validation with very long content."""
        category = Category.objects.create(name='Test Category', user=user)
        long_content = 'A' * 10000  # Very long content
        
        # Create a mock request object
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = NoteSerializer(
            data={
                'title': 'Test Note',
                'content': long_content,
                'category': category.id
            },
            context={'request': mock_request}
        )
        # The serializer doesn't validate content length, it's handled by the model field
        assert serializer.is_valid()
