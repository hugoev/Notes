"""
URL configuration for the Notes backend project.

This module defines the URL patterns for the Notes API,
including authentication, notes, categories, and user management endpoints.
"""

from accounts.throttling import AuthenticationThrottle
from accounts.views import (UserRegistrationView, change_password,
                            user_profile, user_stats)
from config.constants import API_PREFIX
from django.contrib import admin
from django.urls import include, path
from notes.views import CategoryViewSet, NoteViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """
    JWT token obtain view with rate limiting.
    
    Provides authentication tokens with throttling to prevent abuse.
    """
    throttle_classes = [AuthenticationThrottle]


class ThrottledTokenRefreshView(TokenRefreshView):
    """
    JWT token refresh view with rate limiting.
    
    Allows refreshing expired access tokens with throttling.
    """
    throttle_classes = [AuthenticationThrottle]


# API Router Configuration
router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'categories', CategoryViewSet, basename='category')

# URL Patterns
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Routes
    path(f'{API_PREFIX}/', include(router.urls)),
    
    # Authentication Endpoints
    path(f'{API_PREFIX}/auth/token/', ThrottledTokenObtainPairView.as_view(), 
         name='token_obtain_pair'),
    path(f'{API_PREFIX}/auth/token/refresh/', ThrottledTokenRefreshView.as_view(), 
         name='token_refresh'),
    path(f'{API_PREFIX}/auth/register/', UserRegistrationView.as_view(), 
         name='user_register'),
    
    # User Management Endpoints
    path(f'{API_PREFIX}/users/profile/', user_profile, name='user_profile'),
    path(f'{API_PREFIX}/users/change-password/', change_password, 
         name='change_password'),
    path(f'{API_PREFIX}/users/stats/', user_stats, name='user_stats'),
    
    # Django REST Framework browsable API
    path('api-auth/', include('rest_framework.urls')),
    
    # Health Check Endpoint
    path('health/', include('django.contrib.auth.urls')),  # Placeholder for health check
]

# API Documentation URLs (if using drf-spectacular or similar)
# Uncomment and configure if you want to add API documentation
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# urlpatterns += [
#     path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
#     path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
# ]