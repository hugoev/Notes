"""
Custom exceptions for the Notes application.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class NoteNotFoundError(APIException):
    """Raised when a note is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Note not found.'
    default_code = 'note_not_found'


class CategoryNotFoundError(APIException):
    """Raised when a category is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Category not found.'
    default_code = 'category_not_found'


class UnauthorizedAccessError(APIException):
    """Raised when user tries to access resource they don't own."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to access this resource.'
    default_code = 'unauthorized_access'


class ValidationError(APIException):
    """Raised when validation fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation failed.'
    default_code = 'validation_error'
