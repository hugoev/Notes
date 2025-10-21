"""
Utility functions and helpers for the Notes application.

This module contains common utility functions used across the application,
including data validation, formatting, and helper functions.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils import timezone

logger = logging.getLogger(__name__)


def validate_date_range(start_date: Optional[datetime], end_date: Optional[datetime]) -> None:
    """
    Validate that a date range is valid.
    
    Args:
        start_date: Start date of the range
        end_date: End date of the range
        
    Raises:
        ValidationError: If the date range is invalid
    """
    if start_date and end_date and start_date > end_date:
        raise ValidationError("Start date cannot be after end date.")
    
    # Check if dates are not too far in the past or future
    now = timezone.now()
    if start_date and start_date > now + timedelta(days=365):
        raise ValidationError("Start date cannot be more than 1 year in the future.")
    
    if end_date and end_date < now - timedelta(days=3650):  # 10 years ago
        raise ValidationError("End date cannot be more than 10 years in the past.")


def format_queryset_stats(queryset: QuerySet) -> Dict[str, Any]:
    """
    Format statistics for a queryset.
    
    Args:
        queryset: Django QuerySet to analyze
        
    Returns:
        Dictionary containing statistics about the queryset
    """
    try:
        total_count = queryset.count()
        
        # Get date range if the model has created_at field
        if hasattr(queryset.model, 'created_at'):
            dates = queryset.values_list('created_at', flat=True)
            if dates:
                earliest = min(dates)
                latest = max(dates)
            else:
                earliest = latest = None
        else:
            earliest = latest = None
        
        return {
            'total_count': total_count,
            'earliest_created': earliest,
            'latest_created': latest,
            'date_range_days': (latest - earliest).days if earliest and latest else 0
        }
    except Exception as e:
        logger.error(f"Error formatting queryset stats: {str(e)}")
        return {'total_count': 0, 'error': str(e)}


def sanitize_search_query(query: str) -> str:
    """
    Sanitize a search query to prevent injection attacks.
    
    Args:
        query: Raw search query string
        
    Returns:
        Sanitized search query
    """
    if not query:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
    sanitized = query
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length
    sanitized = sanitized[:100]
    
    return sanitized.strip()


def get_user_activity_summary(user: User) -> Dict[str, Any]:
    """
    Get a summary of user activity.
    
    Args:
        user: Django User instance
        
    Returns:
        Dictionary containing user activity summary
    """
    try:
        from notes.models import Category, Note

        # Get basic counts
        notes_count = Note.objects.filter(user=user).count()
        categories_count = Category.objects.filter(user=user).count()
        pinned_notes_count = Note.objects.filter(user=user, is_pinned=True).count()
        
        # Get recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_notes = Note.objects.filter(
            user=user, 
            created_at__gte=thirty_days_ago
        ).count()
        
        # Get most recent note
        try:
            latest_note = Note.objects.filter(user=user).latest('created_at')
            latest_note_date = latest_note.created_at
        except Note.DoesNotExist:
            latest_note_date = None
        
        return {
            'total_notes': notes_count,
            'total_categories': categories_count,
            'pinned_notes': pinned_notes_count,
            'recent_notes_30_days': recent_notes,
            'latest_note_date': latest_note_date,
            'account_age_days': (timezone.now() - user.date_joined).days
        }
    except Exception as e:
        logger.error(f"Error getting user activity summary for {user.username}: {str(e)}")
        return {'error': str(e)}


def paginate_queryset(queryset: QuerySet, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Paginate a queryset manually.
    
    Args:
        queryset: Django QuerySet to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Dictionary containing paginated results and metadata
    """
    try:
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        # Validate page number
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get the page of results
        items = list(queryset[offset:offset + page_size])
        
        return {
            'items': items,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'previous_page': page - 1 if page > 1 else None
            }
        }
    except Exception as e:
        logger.error(f"Error paginating queryset: {str(e)}")
        return {'items': [], 'pagination': {'error': str(e)}}


def format_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Format an error response for API responses.
    
    Args:
        error: Exception instance
        context: Additional context about where the error occurred
        
    Returns:
        Formatted error response dictionary
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    response = {
        'error': {
            'type': error_type,
            'message': error_message,
            'context': context,
            'timestamp': timezone.now().isoformat()
        }
    }
    
    # Log the error
    logger.error(f"Error in {context}: {error_type} - {error_message}")
    
    return response


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 100) -> tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number
        page_size: Items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Tuple of (validated_page, validated_page_size)
    """
    # Validate page
    if page < 1:
        page = 1
    
    # Validate page_size
    if page_size < 1:
        page_size = 20
    elif page_size > max_page_size:
        page_size = max_page_size
    
    return page, page_size


def create_search_filters(search_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create database filters from search parameters.
    
    Args:
        search_params: Dictionary of search parameters
        
    Returns:
        Dictionary of database filters
    """
    filters = {}
    
    # Text search filters
    if 'search' in search_params and search_params['search']:
        search_query = sanitize_search_query(search_params['search'])
        if search_query:
            filters['search'] = search_query
    
    # Date range filters
    if 'created_after' in search_params:
        try:
            filters['created_at__gte'] = datetime.fromisoformat(search_params['created_after'])
        except (ValueError, TypeError):
            pass
    
    if 'created_before' in search_params:
        try:
            filters['created_at__lte'] = datetime.fromisoformat(search_params['created_before'])
        except (ValueError, TypeError):
            pass
    
    # Boolean filters
    if 'is_pinned' in search_params:
        filters['is_pinned'] = search_params['is_pinned'].lower() in ['true', '1', 'yes']
    
    # Category filter
    if 'category' in search_params and search_params['category']:
        try:
            filters['category_id'] = int(search_params['category'])
        except (ValueError, TypeError):
            pass
    
    return filters


def get_model_field_names(model_class) -> List[str]:
    """
    Get all field names for a Django model.
    
    Args:
        model_class: Django model class
        
    Returns:
        List of field names
    """
    return [field.name for field in model_class._meta.fields]


def is_valid_field_name(model_class, field_name: str) -> bool:
    """
    Check if a field name is valid for a Django model.
    
    Args:
        model_class: Django model class
        field_name: Field name to check
        
    Returns:
        True if the field name is valid, False otherwise
    """
    try:
        model_class._meta.get_field(field_name)
        return True
    except:
        return False
