"""
Views for the Notes application.

This module contains API views for managing notes and categories,
including CRUD operations, filtering, searching, and custom actions.
"""

import logging
from typing import Optional

from config.constants import (DEFAULT_ORDERING, DEFAULT_PAGE_SIZE,
                                FILTER_FIELDS, MAX_PAGE_SIZE, ORDERING_FIELDS,
                                SEARCH_FIELDS)
from config.exceptions import (CategoryNotFoundError, NoteNotFoundError,
                                 UnauthorizedAccessError)
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Note
from .serializers import (CategoryListSerializer, CategorySerializer,
                          NoteCreateSerializer, NoteListSerializer,
                          NoteSerializer, NoteUpdateSerializer)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for consistent pagination across the API.
    """
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


class CategoryFilter(django_filters.FilterSet):
    """
    Custom filter for categories.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Category
        fields = ['name', 'created_after', 'created_before']


class NoteFilter(django_filters.FilterSet):
    """
    Custom filter for notes.
    """
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    class Meta:
        model = Note
        fields = ['title', 'content', 'category', 'is_pinned', 'category_name',
                 'created_after', 'created_before', 'updated_after', 'updated_before']


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories.
    
    Provides CRUD operations for categories with user isolation.
    """
    
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_queryset(self) -> QuerySet:
        """Return categories for the authenticated user."""
        return Category.objects.filter(user=self.request.user).select_related('user')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def perform_create(self, serializer) -> None:
        """Create a new category for the authenticated user."""
        try:
            serializer.save(user=self.request.user)
            logger.info(f"Category created for user {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error creating category for user {self.request.user.username}: {str(e)}")
            raise
    
    def perform_update(self, serializer) -> None:
        """Update an existing category."""
        try:
            serializer.save()
            logger.info(f"Category {serializer.instance.id} updated by user {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error updating category {serializer.instance.id}: {str(e)}")
            raise
    
    def perform_destroy(self, instance) -> None:
        """Delete a category."""
        try:
            category_id = instance.id
            instance.delete()
            logger.info(f"Category {category_id} deleted by user {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error deleting category {instance.id}: {str(e)}")
            raise
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None) -> Response:
        """Get all notes in a specific category."""
        try:
            category = self.get_object()
            notes = Note.objects.filter(user=request.user, category=category)
            
            # Apply filtering and pagination
            notes = self.filter_queryset(notes)
            page = self.paginate_queryset(notes)
            
            if page is not None:
                serializer = NoteListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = NoteListSerializer(notes, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            raise CategoryNotFoundError()
        except Exception as e:
            logger.error(f"Error retrieving notes for category {pk}: {str(e)}")
            raise


class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notes.
    
    Provides CRUD operations for notes with filtering, searching, and custom actions.
    """
    
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NoteFilter
    search_fields = SEARCH_FIELDS
    ordering_fields = ORDERING_FIELDS
    ordering = DEFAULT_ORDERING
    
    def get_queryset(self) -> QuerySet:
        """Return notes for the authenticated user."""
        return Note.objects.filter(user=self.request.user).select_related('category', 'user')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return NoteListSerializer
        elif self.action == 'create':
            return NoteCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NoteUpdateSerializer
        return NoteSerializer
    
    def perform_create(self, serializer) -> None:
        """Create a new note for the authenticated user."""
        try:
            serializer.save(user=self.request.user)
            logger.info(f"Note created for user {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error creating note for user {self.request.user.username}: {str(e)}")
            raise
    
    def perform_update(self, serializer) -> None:
        """Update an existing note."""
        try:
            serializer.save()
            logger.info(f"Note {serializer.instance.id} updated by user {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error updating note {serializer.instance.id}: {str(e)}")
            raise
    
    def perform_destroy(self, instance) -> None:
        """Delete a note."""
        try:
            note_id = instance.id
            instance.delete()
            logger.info(f"Note {note_id} deleted by user {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error deleting note {instance.id}: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def pinned(self, request) -> Response:
        """Get all pinned notes for the authenticated user."""
        try:
            pinned_notes = self.get_queryset().filter(is_pinned=True)
            pinned_notes = self.filter_queryset(pinned_notes)
            
            page = self.paginate_queryset(pinned_notes)
            if page is not None:
                serializer = NoteListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = NoteListSerializer(pinned_notes, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving pinned notes for user {request.user.username}: {str(e)}")
            raise
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None) -> Response:
        """Pin a note."""
        try:
            note = self.get_object()
            note.pin()
            serializer = self.get_serializer(note)
            return Response(serializer.data)
        except Note.DoesNotExist:
            raise NoteNotFoundError()
        except Exception as e:
            logger.error(f"Error pinning note {pk}: {str(e)}")
            raise
    
    @action(detail=True, methods=['post'])
    def unpin(self, request, pk=None) -> Response:
        """Unpin a note."""
        try:
            note = self.get_object()
            note.unpin()
            serializer = self.get_serializer(note)
            return Response(serializer.data)
        except Note.DoesNotExist:
            raise NoteNotFoundError()
        except Exception as e:
            logger.error(f"Error unpinning note {pk}: {str(e)}")
            raise
    
    @action(detail=True, methods=['post'])
    def move_to_category(self, request, pk=None) -> Response:
        """Move a note to a different category."""
        try:
            note = self.get_object()
            category_id = request.data.get('category_id')
            
            if category_id is None:
                # Remove from category
                note.move_to_category(None)
            else:
                try:
                    category = Category.objects.get(id=category_id, user=request.user)
                    note.move_to_category(category)
                except Category.DoesNotExist:
                    raise CategoryNotFoundError()
            
            serializer = self.get_serializer(note)
            return Response(serializer.data)
        except Note.DoesNotExist:
            raise NoteNotFoundError()
        except Exception as e:
            logger.error(f"Error moving note {pk} to category: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def recent(self, request) -> Response:
        """Get recently created notes (within last 7 days)."""
        try:
            recent_notes = self.get_queryset().filter(is_recent=True)
            recent_notes = self.filter_queryset(recent_notes)
            
            page = self.paginate_queryset(recent_notes)
            if page is not None:
                serializer = NoteListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = NoteListSerializer(recent_notes, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving recent notes for user {request.user.username}: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def stats(self, request) -> Response:
        """Get statistics for the user's notes."""
        try:
            queryset = self.get_queryset()
            
            stats = {
                'total_notes': queryset.count(),
                'pinned_notes': queryset.filter(is_pinned=True).count(),
                'categorized_notes': queryset.filter(category__isnull=False).count(),
                'recent_notes': queryset.filter(is_recent=True).count(),
                'total_categories': Category.objects.filter(user=request.user).count(),
            }
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error retrieving stats for user {request.user.username}: {str(e)}")
            raise