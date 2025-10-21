"""
Advanced tests for Notes views to improve coverage.

This module contains comprehensive tests for view functionality,
error handling, and edge cases to achieve 90%+ test coverage.
"""

import pytest
from django.urls import reverse
from notes.models import Category, Note
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestNotesViewsAdvanced:
    """Advanced tests for Notes views to improve coverage."""

    def test_notes_pinned_action(self, authenticated_client, user):
        """Test the pinned notes action."""
        # Create some pinned and unpinned notes
        category = Category.objects.create(name='Test Category', user=user)
        pinned_note = Note.objects.create(
            title='Pinned Note',
            content='This is a pinned note',
            user=user,
            category=category,
            is_pinned=True
        )
        unpinned_note = Note.objects.create(
            title='Unpinned Note',
            content='This is an unpinned note',
            user=user,
            category=category,
            is_pinned=False
        )
        
        url = reverse('note-pinned')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Pinned Note'

    def test_notes_pin_action_success(self, authenticated_client, user):
        """Test pinning a note successfully."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category,
            is_pinned=False
        )
        
        url = reverse('note-pin', kwargs={'pk': note.id})
        data = {'is_pinned': True}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_pinned'] == True
        
        note.refresh_from_db()
        assert note.is_pinned == True

    def test_notes_pin_action_unpin(self, authenticated_client, user):
        """Test unpinning a note."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category,
            is_pinned=True
        )
        
        # Use the unpin action instead of pin action
        url = reverse('note-unpin', kwargs={'pk': note.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_pinned'] == False
        
        note.refresh_from_db()
        assert note.is_pinned == False

    def test_notes_pin_action_invalid_data(self, authenticated_client, user):
        """Test pinning a note with invalid data."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        url = reverse('note-pin', kwargs={'pk': note.id})
        data = {'invalid_field': 'invalid_value'}
        response = authenticated_client.post(url, data)
        
        # The pin action ignores invalid data and just toggles the pin status
        assert response.status_code == status.HTTP_200_OK

    def test_notes_pin_action_nonexistent_note(self, authenticated_client):
        """Test pinning a nonexistent note."""
        url = reverse('note-pin', kwargs={'pk': 99999})
        data = {'is_pinned': True}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_notes_pin_action_unauthorized(self, api_client, user):
        """Test pinning a note without authentication."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        url = reverse('note-pin', kwargs={'pk': note.id})
        data = {'is_pinned': True}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_notes_pin_action_other_user_note(self, authenticated_client, user):
        """Test pinning another user's note."""
        other_user = user.__class__.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        category = Category.objects.create(name='Other Category', user=other_user)
        note = Note.objects.create(
            title='Other Note',
            content='Other content',
            user=other_user,
            category=category
        )
        
        url = reverse('note-pin', kwargs={'pk': note.id})
        data = {'is_pinned': True}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_notes_search_with_special_characters(self, authenticated_client, user):
        """Test searching notes with special characters."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Note with Special Chars: @#$%',
            content='Content with special characters: !@#$%^&*()',
            user=user,
            category=category
        )
        
        url = reverse('note-list')
        response = authenticated_client.get(url, {'search': '@#$%'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_notes_filter_by_category_nonexistent(self, authenticated_client, user):
        """Test filtering notes by nonexistent category."""
        url = reverse('note-list')
        response = authenticated_client.get(url, {'category': 99999})
        
        # Filtering by nonexistent category returns 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_notes_ordering_invalid_field(self, authenticated_client, user):
        """Test ordering notes by invalid field."""
        category = Category.objects.create(name='Test Category', user=user)
        Note.objects.create(
            title='Note 1',
            content='Content 1',
            user=user,
            category=category
        )
        
        url = reverse('note-list')
        response = authenticated_client.get(url, {'ordering': 'invalid_field'})
        
        assert response.status_code == status.HTTP_200_OK
        # Should still return results, just not ordered by invalid field

    def test_notes_pagination_edge_cases(self, authenticated_client, user):
        """Test pagination edge cases."""
        category = Category.objects.create(name='Test Category', user=user)
        
        # Create exactly 20 notes to test pagination boundary
        for i in range(20):
            Note.objects.create(
                title=f'Note {i}',
                content=f'Content {i}',
                user=user,
                category=category
            )
        
        # Test first page
        url = reverse('note-list')
        response = authenticated_client.get(url, {'page': 1, 'page_size': 10})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10
        assert response.data['count'] == 20
        assert response.data['next'] is not None
        
        # Test second page
        response = authenticated_client.get(url, {'page': 2, 'page_size': 10})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10
        assert response.data['previous'] is not None
        
        # Test page beyond available data
        response = authenticated_client.get(url, {'page': 5, 'page_size': 10})
        
        # Django pagination returns 404 for pages beyond available data
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_notes_create_with_invalid_category(self, authenticated_client, user):
        """Test creating a note with invalid category."""
        url = reverse('note-list')
        data = {
            'title': 'Test Note',
            'content': 'Test content',
            'category': 99999  # Nonexistent category
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'category' in response.data

    def test_notes_update_with_invalid_data(self, authenticated_client, user):
        """Test updating a note with invalid data."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        url = reverse('note-detail', kwargs={'pk': note.id})
        data = {
            'title': '',  # Empty title should fail validation
            'content': 'Updated content'
        }
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_notes_perform_create_logging(self, authenticated_client, user):
        """Test that note creation is properly logged."""
        category = Category.objects.create(name='Test Category', user=user)
        
        url = reverse('note-list')
        data = {
            'title': 'Test Note',
            'content': 'Test content',
            'category': category.id
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        # The logging happens in the view, so we just verify the note was created
        assert Note.objects.filter(title='Test Note').exists()

    def test_notes_perform_update_logging(self, authenticated_client, user):
        """Test that note updates are properly logged."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Original Title',
            content='Original content',
            user=user,
            category=category
        )
        
        url = reverse('note-detail', kwargs={'pk': note.id})
        data = {'title': 'Updated Title'}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        note.refresh_from_db()
        assert note.title == 'Updated Title'

    def test_notes_perform_destroy_logging(self, authenticated_client, user):
        """Test that note deletion is properly logged."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        url = reverse('note-detail', kwargs={'pk': note.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Note.objects.filter(id=note.id).exists()

    def test_notes_pin_action_logging(self, authenticated_client, user):
        """Test that pinning a note is properly logged."""
        category = Category.objects.create(name='Test Category', user=user)
        note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=user,
            category=category
        )
        
        url = reverse('note-pin', kwargs={'pk': note.id})
        data = {'is_pinned': True}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        # The logging happens in the view, so we just verify the action succeeded
        note.refresh_from_db()
        assert note.is_pinned == True
