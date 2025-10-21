"""
Tests for Notes models to improve coverage.

This module contains comprehensive tests for model functionality,
methods, properties, and edge cases to achieve 90%+ test coverage.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from notes.models import Category, Note

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestCategoryModel:
    """Tests for Category model."""

    def test_category_creation(self, user):
        """Test creating a category."""
        category = Category.objects.create(name='Test Category', user=user)
        
        assert category.name == 'Test Category'
        assert category.user == user
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_str_representation(self, user):
        """Test category string representation."""
        category = Category.objects.create(name='Test Category', user=user)
        expected = f'Test Category ({user.username})'
        assert str(category) == expected

    def test_category_meta_options(self, user):
        """Test category meta options."""
        category = Category.objects.create(name='Test Category', user=user)
        
        # Test ordering
        categories = Category.objects.all()
        assert categories.ordered

    def test_category_unique_constraint(self, user):
        """Test that category names are unique per user."""
        Category.objects.create(name='Test Category', user=user)
        
        # Try to create another category with the same name for the same user
        # This should raise a ValidationError due to the clean() method
        with pytest.raises(ValidationError):
            category = Category(name='Test Category', user=user)
            category.full_clean()

    def test_category_different_users_same_name(self, user):
        """Test that different users can have categories with the same name."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        category1 = Category.objects.create(name='Test Category', user=user)
        category2 = Category.objects.create(name='Test Category', user=other_user)
        
        assert category1.name == category2.name
        assert category1.user != category2.user

    def test_category_notes_relationship(self, user):
        """Test category-notes relationship."""
        category = Category.objects.create(name='Test Category', user=user)
        
        # Create some notes for the category
        note1 = Note.objects.create(
            title='Note 1',
            content='Content 1',
            user=user,
            category=category
        )
        note2 = Note.objects.create(
            title='Note 2',
            content='Content 2',
            user=user,
            category=category
        )
        
        # Test reverse relationship using the related_name 'notes'
        notes = category.notes.all()
        assert len(notes) == 2
        assert note1 in notes
        assert note2 in notes

    def test_category_cascade_delete(self, user):
        """Test that deleting a category sets notes' category to NULL."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        # Delete the category
        category.delete()
        
        # Note should still exist but with category set to NULL
        note.refresh_from_db()
        assert Note.objects.filter(id=note.id).exists()
        assert note.category is None

    def test_category_clean_method(self, user):
        """Test category clean method."""
        category = Category(name='  Test Category  ', user=user)
        category.clean()
        
        # The clean method doesn't trim, it just validates
        # The trimming happens in the serializer
        assert category.name == '  Test Category  '

    def test_category_clean_method_empty_name(self, user):
        """Test category clean method with empty name."""
        category = Category(name='', user=user)
        
        with pytest.raises(ValidationError):
            category.clean()

    def test_category_clean_method_whitespace_name(self, user):
        """Test category clean method with whitespace-only name."""
        category = Category(name='   ', user=user)
        
        with pytest.raises(ValidationError):
            category.clean()

    def test_category_clean_method_long_name(self, user):
        """Test category clean method with very long name."""
        long_name = 'A' * 300  # Exceeds the 100 character limit
        category = Category(name=long_name, user=user)
        
        # The clean method doesn't check length, that's handled by the field max_length
        # and serializer validation
        category.clean()  # This should not raise an error


class TestNoteModel:
    """Tests for Note model."""

    def test_note_creation(self, user):
        """Test creating a note."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        assert note.title == 'Test Note'
        assert note.content == 'Test content'
        assert note.user == user
        assert note.category == category
        assert note.is_pinned == False
        assert note.created_at is not None
        assert note.updated_at is not None

    def test_note_str_representation(self, user):
        """Test note string representation."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        expected = f'Test Note ({user.username})'
        assert str(note) == expected

    def test_note_meta_options(self, user):
        """Test note meta options."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        # Test ordering
        notes = Note.objects.all()
        assert notes.ordered

    def test_note_word_count_property(self, user):
        """Test note word count property."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='This is a test note with multiple words',
            user=user,
            category=category
        )
        
        assert note.word_count == 8  # "This is a test note with multiple words"

    def test_note_character_count_property(self, user):
        """Test note character count property."""
        category = Category.objects.create(name='Test Category', user=user)
        content = 'Hello, World!'
        note = Note.objects.create(
            title='Test Note',
            content=content,
            user=user,
            category=category
        )
        
        assert note.character_count == len(content)

    def test_note_is_recent_property(self, user):
        """Test note is_recent property."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        # Note was just created, so it should be recent
        assert note.is_recent == True

    def test_note_is_recent_property_old_note(self, user):
        """Test note is_recent property for old note."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        # Manually set created_at to 8 days ago
        note.created_at = timezone.now() - timedelta(days=8)
        note.save()
        
        # Note is older than 7 days, so it should not be recent
        assert note.is_recent == False

    def test_note_pinned_note(self, user):
        """Test creating a pinned note."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category,
            is_pinned=True
        )
        
        assert note.is_pinned == True

    def test_note_clean_method(self, user):
        """Test note clean method."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note(
            title='  Test Note  ',
            content='  Test content  ',
            user=user,
            category=category
        )
        note.clean()
        
        # The clean method doesn't trim, it just validates
        # The trimming happens in the serializer
        assert note.title == '  Test Note  '
        assert note.content == '  Test content  '

    def test_note_clean_method_empty_title(self, user):
        """Test note clean method with empty title."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note(
            title='',
            content='Test content',
            user=user,
            category=category
        )
        
        with pytest.raises(ValidationError):
            note.clean()

    def test_note_clean_method_empty_content(self, user):
        """Test note clean method with empty content."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note(
            title='Test Note',
            content='',
            user=user,
            category=category
        )
        
        with pytest.raises(ValidationError):
            note.clean()

    def test_note_clean_method_whitespace_title(self, user):
        """Test note clean method with whitespace-only title."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note(
            title='   ',
            content='Test content',
            user=user,
            category=category
        )
        
        with pytest.raises(ValidationError):
            note.clean()

    def test_note_clean_method_whitespace_content(self, user):
        """Test note clean method with whitespace-only content."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note(
            title='Test Note',
            content='   ',
            user=user,
            category=category
        )
        
        with pytest.raises(ValidationError):
            note.clean()

    def test_note_clean_method_long_title(self, user):
        """Test note clean method with very long title."""
        category = Category.objects.create(name='Test Category', user=user)
        long_title = 'A' * 300  # Very long title
        note = Note(
            title=long_title,
            content='Test content',
            user=user,
            category=category
        )
        
        # The clean method doesn't check length, that's handled by the field max_length
        # and serializer validation
        note.clean()  # This should not raise an error

    def test_note_clean_method_long_content(self, user):
        """Test note clean method with very long content."""
        category = Category.objects.create(name='Test Category', user=user)
        long_content = 'A' * 10000  # Very long content
        note = Note(
            title='Test Note',
            content=long_content,
            user=user,
            category=category
        )
        
        # The clean method doesn't check content length
        note.clean()  # This should not raise an error

    def test_note_save_method(self, user):
        """Test note save method."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note(
            title='  Test Note  ',
            content='  Test content  ',
            user=user,
            category=category
        )
        note.save()
        
        # The save method doesn't trim, it just validates
        # The trimming happens in the serializer
        note.refresh_from_db()
        assert note.title == '  Test Note  '
        assert note.content == '  Test content  '

    def test_note_foreign_key_constraints(self, user):
        """Test note foreign key constraints."""
        category = Category.objects.create(name='Test Category', user=user)
        
        # Create note with valid foreign keys
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        assert note.user == user
        assert note.category == category

    def test_note_cascade_delete_user(self, user):
        """Test that deleting a user cascades to notes."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        # Delete the user
        user.delete()
        
        # Note should be deleted too
        assert not Note.objects.filter(id=note.id).exists()

    def test_note_cascade_delete_category(self, user):
        """Test that deleting a category sets notes' category to NULL."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        # Delete the category
        category.delete()
        
        # Note should still exist but with category set to NULL
        note.refresh_from_db()
        assert Note.objects.filter(id=note.id).exists()
        assert note.category is None

    def test_note_ordering(self, user):
        """Test note ordering."""
        category = Category.objects.create(name='Test Category', user=user)
        
        # Create notes with different creation times
        note1 = Note.objects.create(
            title='Note 1',
            content='Content 1',
            user=user,
            category=category
        )
        note2 = Note.objects.create(
            title='Note 2',
            content='Content 2',
            user=user,
            category=category
        )
        
        # Notes should be ordered by creation time (newest first)
        notes = Note.objects.all()
        assert notes[0] == note2  # Newest first
        assert notes[1] == note1

    def test_note_pinned_ordering(self, user):
        """Test that pinned notes come first in ordering."""
        category = Category.objects.create(name='Test Category', user=user)
        
        # Create unpinned note first
        unpinned_note = Note.objects.create(
            title='Unpinned Note',
            content='Content',
            user=user,
            category=category,
            is_pinned=False
        )
        
        # Create pinned note second
        pinned_note = Note.objects.create(
            title='Pinned Note',
            content='Content',
            user=user,
            category=category,
            is_pinned=True
        )
        
        # Pinned note should come first
        notes = Note.objects.all()
        assert notes[0] == pinned_note
        assert notes[1] == unpinned_note
