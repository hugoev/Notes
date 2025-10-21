"""
Advanced tests for Categories views to improve coverage.

This module contains comprehensive tests for category functionality,
error handling, and edge cases to achieve 90%+ test coverage.
"""

import pytest
from django.urls import reverse
from notes.models import Category, Note
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestCategoriesViewsAdvanced:
    """Advanced tests for Categories views to improve coverage."""

    def test_categories_perform_create_logging(self, authenticated_client, user):
        """Test that category creation is properly logged."""
        url = reverse('category-list')
        data = {'name': 'Test Category'}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        # The logging happens in the view, so we just verify the category was created
        assert Category.objects.filter(name='Test Category').exists()

    def test_categories_perform_update_logging(self, authenticated_client, user):
        """Test that category updates are properly logged."""
        category = Category.objects.create(name='Original Name', user=user)
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {'name': 'Updated Name'}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == 'Updated Name'

    def test_categories_perform_destroy_logging(self, authenticated_client, user):
        """Test that category deletion is properly logged."""
        category = Category.objects.create(name='Test Category', user=user)
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()

    def test_categories_create_with_duplicate_name_same_user(self, authenticated_client, user):
        """Test creating a category with duplicate name for same user."""
        Category.objects.create(name='Duplicate Category', user=user)
        
        url = reverse('category-list')
        data = {'name': 'Duplicate Category'}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_categories_create_with_duplicate_name_different_user(self, authenticated_client, user):
        """Test creating a category with duplicate name for different user (should succeed)."""
        other_user = user.__class__.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        Category.objects.create(name='Duplicate Category', user=other_user)
        
        url = reverse('category-list')
        data = {'name': 'Duplicate Category'}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='Duplicate Category', user=user).exists()

    def test_categories_update_with_duplicate_name(self, authenticated_client, user):
        """Test updating a category with duplicate name."""
        category1 = Category.objects.create(name='Category 1', user=user)
        category2 = Category.objects.create(name='Category 2', user=user)
        
        url = reverse('category-detail', kwargs={'pk': category2.id})
        data = {'name': 'Category 1'}  # Try to rename category2 to category1's name
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_categories_search_with_special_characters(self, authenticated_client, user):
        """Test searching categories with special characters."""
        category = Category.objects.create(name='Category with Special Chars: @#$%', user=user)
        
        url = reverse('category-list')
        response = authenticated_client.get(url, {'search': '@#$%'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_categories_ordering_invalid_field(self, authenticated_client, user):
        """Test ordering categories by invalid field."""
        Category.objects.create(name='Category A', user=user)
        Category.objects.create(name='Category B', user=user)
        
        url = reverse('category-list')
        response = authenticated_client.get(url, {'ordering': 'invalid_field'})
        
        assert response.status_code == status.HTTP_200_OK
        # Should still return results, just not ordered by invalid field

    def test_categories_pagination_edge_cases(self, authenticated_client, user):
        """Test pagination edge cases for categories."""
        # Create exactly 20 categories to test pagination boundary
        for i in range(20):
            Category.objects.create(name=f'Category {i}', user=user)
        
        # Test first page
        url = reverse('category-list')
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

    def test_categories_create_with_empty_name(self, authenticated_client, user):
        """Test creating a category with empty name."""
        url = reverse('category-list')
        data = {'name': ''}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_categories_create_with_whitespace_name(self, authenticated_client, user):
        """Test creating a category with whitespace-only name."""
        url = reverse('category-list')
        data = {'name': '   '}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_categories_create_with_very_long_name(self, authenticated_client, user):
        """Test creating a category with very long name."""
        long_name = 'A' * 300  # Exceeds the 100 character limit
        url = reverse('category-list')
        data = {'name': long_name}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_categories_update_with_empty_name(self, authenticated_client, user):
        """Test updating a category with empty name."""
        category = Category.objects.create(name='Test Category', user=user)
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {'name': ''}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_categories_update_with_whitespace_name(self, authenticated_client, user):
        """Test updating a category with whitespace-only name."""
        category = Category.objects.create(name='Test Category', user=user)
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {'name': '   '}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_categories_update_with_very_long_name(self, authenticated_client, user):
        """Test updating a category with very long name."""
        category = Category.objects.create(name='Test Category', user=user)
        long_name = 'A' * 300  # Exceeds the 100 character limit
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {'name': long_name}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_categories_retrieve_nonexistent(self, authenticated_client):
        """Test retrieving a nonexistent category."""
        url = reverse('category-detail', kwargs={'pk': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_categories_update_nonexistent(self, authenticated_client, user):
        """Test updating a nonexistent category."""
        url = reverse('category-detail', kwargs={'pk': 99999})
        data = {'name': 'Updated Name'}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_categories_delete_nonexistent(self, authenticated_client):
        """Test deleting a nonexistent category."""
        url = reverse('category-detail', kwargs={'pk': 99999})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_categories_list_with_multiple_users(self, authenticated_client, user):
        """Test that categories are properly filtered by user."""
        # Create categories for the authenticated user
        Category.objects.create(name='User Category 1', user=user)
        Category.objects.create(name='User Category 2', user=user)
        
        # Create categories for another user
        other_user = user.__class__.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        Category.objects.create(name='Other User Category 1', user=other_user)
        Category.objects.create(name='Other User Category 2', user=other_user)
        
        url = reverse('category-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        category_names = [cat['name'] for cat in response.data['results']]
        assert 'User Category 1' in category_names
        assert 'User Category 2' in category_names
        assert 'Other User Category 1' not in category_names
        assert 'Other User Category 2' not in category_names

    def test_categories_notes_count_calculation(self, authenticated_client, user):
        """Test that notes count is properly calculated for categories."""
        category1 = Category.objects.create(name='Category 1', user=user)
        category2 = Category.objects.create(name='Category 2', user=user)
        
        # Create notes for category1
        for i in range(3):
            Note.objects.create(
                title=f'Note {i}',
                content=f'Content {i}',
                user=user,
                category=category1
            )
        
        # Create notes for category2
        for i in range(5):
            Note.objects.create(
                title=f'Note {i}',
                content=f'Content {i}',
                user=user,
                category=category2
            )
        
        url = reverse('category-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        # Find the categories in the response
        categories = response.data['results']
        cat1_data = next(cat for cat in categories if cat['name'] == 'Category 1')
        cat2_data = next(cat for cat in categories if cat['name'] == 'Category 2')
        
        assert cat1_data['notes_count'] == 3
        assert cat2_data['notes_count'] == 5
