"""
Tests for Notes API endpoints.
"""
import pytest
from django.urls import reverse
from notes.models import Category, Note
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestNotesAPI:
    """Test cases for Notes API endpoints."""

    def test_list_notes_authenticated(self, authenticated_client, multiple_notes):
        """Test listing notes for authenticated user."""
        url = reverse('note-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert len(response.data['results']) == 5
        assert response.data['count'] == 5

    def test_list_notes_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list notes."""
        url = reverse('note-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_note_authenticated(self, authenticated_client, category):
        """Test creating a note for authenticated user."""
        url = reverse('note-list')
        data = {
            'title': 'New Test Note',
            'content': 'This is a new test note content.',
            'category': category.id
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == data['title']
        assert response.data['content'] == data['content']
        assert response.data['category'] == category.id
        assert Note.objects.filter(title=data['title']).exists()

    def test_create_note_unauthenticated(self, api_client, category):
        """Test that unauthenticated users cannot create notes."""
        url = reverse('note-list')
        data = {
            'title': 'New Test Note',
            'content': 'This is a new test note content.',
            'category': category.id
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_note_authenticated(self, authenticated_client, note):
        """Test retrieving a specific note for authenticated user."""
        url = reverse('note-detail', kwargs={'pk': note.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == note.title
        assert response.data['content'] == note.content

    def test_retrieve_note_unauthenticated(self, api_client, note):
        """Test that unauthenticated users cannot retrieve notes."""
        url = reverse('note-detail', kwargs={'pk': note.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_note_authenticated(self, authenticated_client, note):
        """Test updating a note for authenticated user."""
        url = reverse('note-detail', kwargs={'pk': note.id})
        data = {
            'title': 'Updated Test Note',
            'content': 'This is updated test note content.',
            'category': note.category.id
        }
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == data['title']
        assert response.data['content'] == data['content']
        
        note.refresh_from_db()
        assert note.title == data['title']
        assert note.content == data['content']

    def test_update_note_unauthenticated(self, api_client, note):
        """Test that unauthenticated users cannot update notes."""
        url = reverse('note-detail', kwargs={'pk': note.id})
        data = {
            'title': 'Updated Test Note',
            'content': 'This is updated test note content.',
            'category': note.category.id
        }
        response = api_client.put(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_note_authenticated(self, authenticated_client, note):
        """Test deleting a note for authenticated user."""
        url = reverse('note-detail', kwargs={'pk': note.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Note.objects.filter(id=note.id).exists()

    def test_delete_note_unauthenticated(self, api_client, note):
        """Test that unauthenticated users cannot delete notes."""
        url = reverse('note-detail', kwargs={'pk': note.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_toggle_pin_note(self, authenticated_client, note):
        """Test toggling pin status of a note."""
        url = reverse('note-pin', kwargs={'pk': note.id})
        data = {'is_pinned': True}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_pinned'] == True
        
        note.refresh_from_db()
        assert note.is_pinned == True

    def test_notes_pagination(self, authenticated_client, multiple_notes):
        """Test that notes API supports pagination."""
        url = reverse('note-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    def test_notes_search(self, authenticated_client, multiple_notes):
        """Test searching notes by title and content."""
        url = reverse('note-list')
        response = authenticated_client.get(url, {'search': 'Test Note 1'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'Test Note 1' in response.data['results'][0]['title']

    def test_notes_filter_by_category(self, authenticated_client, multiple_notes, category):
        """Test filtering notes by category."""
        url = reverse('note-list')
        response = authenticated_client.get(url, {'category': category.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        for note in response.data['results']:
            assert note['category'] == category.id

    def test_notes_ordering(self, authenticated_client, multiple_notes):
        """Test ordering notes by different fields."""
        url = reverse('note-list')
        response = authenticated_client.get(url, {'ordering': '-created_at'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 5
        
        # Check that notes are ordered by created_at descending
        for i in range(len(results) - 1):
            assert results[i]['created_at'] >= results[i + 1]['created_at']

    def test_user_cannot_access_other_user_notes(self, authenticated_client, user):
        """Test that users cannot access notes from other users."""
        # Create another user and their note
        other_user = user.__class__.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_category = Category.objects.create(
            name='Other Category',
            user=other_user
        )
        other_note = Note.objects.create(
            title='Other User Note',
            content='This note belongs to another user.',
            user=other_user,
            category=other_category
        )
        
        # Try to access the other user's note
        url = reverse('note-detail', kwargs={'pk': other_note.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_note_serializer_fields(self, authenticated_client, note):
        """Test that note serializer includes all required fields."""
        url = reverse('note-detail', kwargs={'pk': note.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        required_fields = [
            'id', 'title', 'content', 'created_at', 'updated_at',
            'category', 'category_name', 'is_pinned', 'word_count', 'is_recent'
        ]
        
        for field in required_fields:
            assert field in response.data
