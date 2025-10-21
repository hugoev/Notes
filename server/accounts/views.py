"""
Views for the Accounts application.

This module contains API views for user registration, authentication,
and profile management.
"""

import logging

from config.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (UserProfileSerializer, UserRegistrationSerializer,
                          UserSerializer)
from .throttling import AuthenticationThrottle

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration.
    
    Allows new users to create accounts with proper validation.
    """
    
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    throttle_classes = [AuthenticationThrottle]
    
    def create(self, request, *args, **kwargs):
        """Create a new user account."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = serializer.save()
            
            # Generate JWT tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"New user registered: {user.username}")
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            raise


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get or update user profile.
    
    GET: Retrieve current user's profile
    PUT/PATCH: Update current user's profile
    """
    try:
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = UserProfileSerializer(
                request.user, 
                data=request.data, 
                partial=partial
            )
            
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info(f"User profile updated: {request.user.username}")
                return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in user profile view: {str(e)}")
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.
    
    Requires current password and new password.
    """
    try:
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            raise ValidationError("All password fields are required.")
        
        if new_password != confirm_password:
            raise ValidationError("New passwords do not match.")
        
        if not request.user.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        
        request.user.set_password(new_password)
        request.user.save()
        
        logger.info(f"Password changed for user: {request.user.username}")
        
        return Response({
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error changing password for user {request.user.username}: {str(e)}")
        raise


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """
    Get user statistics.
    
    Returns various statistics about the user's account and activity.
    """
    try:
        user = request.user
        
        stats = {
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error retrieving user stats for {request.user.username}: {str(e)}")
        raise