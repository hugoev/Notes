"""
Tests for Categories API endpoints.
"""
import pytest
from django.urls import reverse
from notes.models import Category, Note
from rest_framework import status


@pytest.mark.django_db
class TestCategoriesAPI:
    """Test cases for Categories API endpoints."""

    def test_list_categories_authenticated(self, authenticated_client, multiple_categories):
        """Test listing categories for authenticated user."""
        url = reverse('category-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert len(response.data['results']) == 3
        assert response.data['count'] == 3

    def test_list_categories_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list categories."""
        url = reverse('category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_authenticated(self, authenticated_client):
        """Test creating a category for authenticated user."""
        url = reverse('category-list')
        data = {'name': 'New Test Category'}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert Category.objects.filter(name=data['name']).exists()

    def test_create_category_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot create categories."""
        url = reverse('category-list')
        data = {'name': 'New Test Category'}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_duplicate_name(self, authenticated_client, category):
        """Test that creating a category with duplicate name fails."""
        url = reverse('category-list')
        data = {'name': category.name}  # Same name as existing category
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_create_category_empty_name(self, authenticated_client):
        """Test that creating a category with empty name fails."""
        url = reverse('category-list')
        data = {'name': ''}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_long_name(self, authenticated_client):
        """Test that creating a category with too long name fails."""
        url = reverse('category-list')
        data = {'name': 'A' * 101}  # Assuming max length is 100
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_category_authenticated(self, authenticated_client, category):
        """Test retrieving a specific category for authenticated user."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name

    def test_retrieve_category_unauthenticated(self, api_client, category):
        """Test that unauthenticated users cannot retrieve categories."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_category_authenticated(self, authenticated_client, category):
        """Test updating a category for authenticated user."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {'name': 'Updated Category Name'}
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == data['name']
        
        category.refresh_from_db()
        assert category.name == data['name']

    def test_update_category_unauthenticated(self, api_client, category):
        """Test that unauthenticated users cannot update categories."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {'name': 'Updated Category Name'}
        response = api_client.put(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_category_authenticated(self, authenticated_client, category):
        """Test deleting a category for authenticated user."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()

    def test_delete_category_with_notes(self, authenticated_client, category, note):
        """Test that deleting a category with notes succeeds (cascade delete)."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_category_unauthenticated(self, api_client, category):
        """Test that unauthenticated users cannot delete categories."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_categories_pagination(self, authenticated_client, multiple_categories):
        """Test that categories API supports pagination."""
        url = reverse('category-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    def test_categories_search(self, authenticated_client, multiple_categories):
        """Test searching categories by name."""
        url = reverse('category-list')
        response = authenticated_client.get(url, {'search': 'Test Category 1'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'Test Category 1' in response.data['results'][0]['name']

    def test_categories_ordering(self, authenticated_client, multiple_categories):
        """Test ordering categories by different fields."""
        url = reverse('category-list')
        response = authenticated_client.get(url, {'ordering': 'name'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 3
        
        # Check that categories are ordered by name ascending
        for i in range(len(results) - 1):
            assert results[i]['name'] <= results[i + 1]['name']

    def test_user_cannot_access_other_user_categories(self, authenticated_client, user):
        """Test that users cannot access categories from other users."""
        # Create another user and their category
        other_user = user.__class__.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_category = Category.objects.create(
            name='Other User Category',
            user=other_user
        )
        
        # Try to access the other user's category
        url = reverse('category-detail', kwargs={'pk': other_category.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_category_serializer_fields(self, authenticated_client, category):
        """Test that category serializer includes all required fields."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        required_fields = ['id', 'name', 'created_at', 'updated_at', 'notes_count']
        
        for field in required_fields:
            assert field in response.data

    def test_category_notes_count(self, authenticated_client, category, multiple_notes):
        """Test that category serializer includes correct notes count."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['notes_count'] == 5

    def test_category_list_notes_count(self, authenticated_client, category, multiple_notes):
        """Test that category list includes notes count."""
        url = reverse('category-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        category_data = next(
            (cat for cat in response.data['results'] if cat['id'] == category.id),
            None
        )
        assert category_data is not None
        assert category_data['notes_count'] == 5
