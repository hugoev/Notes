"""
Tests for Authentication API endpoints.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationAPI:
    """Test cases for Authentication API endpoints."""

    def test_user_registration_success(self, api_client):
        """Test successful user registration."""
        url = reverse('user_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['username'] == data['username']
        assert response.data['user']['email'] == data['email']
        assert User.objects.filter(username=data['username']).exists()

    def test_user_registration_password_mismatch(self, api_client):
        """Test user registration with password mismatch."""
        url = reverse('user_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_user_registration_duplicate_username(self, api_client, user):
        """Test user registration with duplicate username."""
        url = reverse('user_register')
        data = {
            'username': user.username,
            'email': 'different@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_user_registration_duplicate_email(self, api_client, user):
        """Test user registration with duplicate email."""
        url = reverse('user_register')
        data = {
            'username': 'differentuser',
            'email': user.email,
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_user_registration_invalid_email(self, api_client):
        """Test user registration with invalid email format."""
        url = reverse('user_register')
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_user_registration_short_password(self, api_client):
        """Test user registration with short password."""
        url = reverse('user_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'password_confirm': '123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_user_login_success(self, api_client, user):
        """Test successful user login."""
        url = reverse('token_obtain_pair')
        data = {
            'username': user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_user_login_wrong_password(self, api_client, user):
        """Test user login with wrong password."""
        url = reverse('token_obtain_pair')
        data = {
            'username': user.username,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_login_nonexistent_user(self, api_client):
        """Test user login with nonexistent user."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'nonexistent',
            'password': 'somepassword'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh_success(self, api_client, user):
        """Test successful token refresh."""
        refresh = RefreshToken.for_user(user)
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_token_refresh_invalid_token(self, api_client):
        """Test token refresh with invalid token."""
        url = reverse('token_refresh')
        data = {'refresh': 'invalid_token'}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_profile_authenticated(self, authenticated_client, user):
        """Test retrieving user profile for authenticated user."""
        url = reverse('user_profile')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

    def test_user_profile_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot access profile."""
        url = reverse('user_profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_profile_authenticated(self, authenticated_client, user):
        """Test updating user profile for authenticated user."""
        url = reverse('user_profile')
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == data['username']
        assert response.data['email'] == data['email']
        
        user.refresh_from_db()
        assert user.username == data['username']
        assert user.email == data['email']

    def test_update_user_profile_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot update profile."""
        url = reverse('user_profile')
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        response = api_client.put(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_authenticated(self, authenticated_client, user):
        """Test changing password for authenticated user."""
        url = reverse('change_password')
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password('newpass123')

    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test changing password with wrong old password."""
        url = reverse('change_password')
        data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data

    def test_change_password_mismatch(self, authenticated_client, user):
        """Test changing password with password mismatch."""
        url = reverse('change_password')
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'differentpass'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data

    def test_change_password_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot change password."""
        url = reverse('change_password')
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_authenticated(self, authenticated_client):
        """Test logout for authenticated user."""
        url = reverse('user_stats')  # Using user_stats as logout endpoint
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'username' in response.data

    def test_logout_unauthenticated(self, api_client):
        """Test that unauthenticated users can still call logout."""
        url = reverse('user_stats')  # Using user_stats as logout endpoint
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_user_profile_serializer_error(self, authenticated_client, user):
        """Test user profile update with serializer validation error."""
        # Test with invalid data that triggers serializer validation
        data = {
            'username': '',  # Empty username should trigger validation error
            'email': 'invalid-email',  # Invalid email format
        }
        
        response = authenticated_client.put('/api/v1/users/profile/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data or 'email' in response.data

    def test_change_password_serializer_error(self, authenticated_client, user):
        """Test change password with serializer validation error."""
        # Test with mismatched passwords
        data = {
            'current_password': 'admin123',
            'new_password': 'newpass123',
            'confirm_password': 'differentpass123'
        }
        
        response = authenticated_client.post('/api/v1/users/change-password/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data

    def test_change_password_same_password_error(self, authenticated_client, user):
        """Test change password with same current and new password."""
        data = {
            'current_password': 'admin123',
            'new_password': 'admin123',
            'confirm_password': 'admin123'
        }
        
        response = authenticated_client.post('/api/v1/users/change-password/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
