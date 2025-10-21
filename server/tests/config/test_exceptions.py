"""
Tests for config exceptions.

This module contains tests for custom exceptions used in the application.
"""

import pytest
from config.exceptions import (CategoryNotFoundError, NoteNotFoundError,
                               UnauthorizedAccessError, ValidationError)
from rest_framework import status
from rest_framework.exceptions import APIException


class TestCustomExceptions:
    """Tests for custom exceptions."""

    def test_note_not_found_error(self):
        """Test NoteNotFoundError exception."""
        error = NoteNotFoundError()
        
        assert isinstance(error, APIException)
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.default_detail == 'Note not found.'
        assert error.default_code == 'note_not_found'

    def test_note_not_found_error_with_custom_detail(self):
        """Test NoteNotFoundError with custom detail."""
        custom_detail = 'Note with ID 123 not found.'
        error = NoteNotFoundError(detail=custom_detail)
        
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.detail == custom_detail
        assert error.default_code == 'note_not_found'

    def test_category_not_found_error(self):
        """Test CategoryNotFoundError exception."""
        error = CategoryNotFoundError()
        
        assert isinstance(error, APIException)
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.default_detail == 'Category not found.'
        assert error.default_code == 'category_not_found'

    def test_category_not_found_error_with_custom_detail(self):
        """Test CategoryNotFoundError with custom detail."""
        custom_detail = 'Category with ID 456 not found.'
        error = CategoryNotFoundError(detail=custom_detail)
        
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.detail == custom_detail
        assert error.default_code == 'category_not_found'

    def test_unauthorized_access_error(self):
        """Test UnauthorizedAccessError exception."""
        error = UnauthorizedAccessError()
        
        assert isinstance(error, APIException)
        assert error.status_code == status.HTTP_403_FORBIDDEN
        assert error.default_detail == 'You do not have permission to access this resource.'
        assert error.default_code == 'unauthorized_access'

    def test_unauthorized_access_error_with_custom_detail(self):
        """Test UnauthorizedAccessError with custom detail."""
        custom_detail = 'You cannot access notes belonging to other users.'
        error = UnauthorizedAccessError(detail=custom_detail)
        
        assert error.status_code == status.HTTP_403_FORBIDDEN
        assert error.detail == custom_detail
        assert error.default_code == 'unauthorized_access'

    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError()
        
        assert isinstance(error, APIException)
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.default_detail == 'Validation failed.'
        assert error.default_code == 'validation_error'

    def test_validation_error_with_custom_detail(self):
        """Test ValidationError with custom detail."""
        custom_detail = 'Title cannot be empty.'
        error = ValidationError(detail=custom_detail)
        
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.detail == custom_detail
        assert error.default_code == 'validation_error'

    def test_exceptions_inherit_from_api_exception(self):
        """Test that all custom exceptions inherit from APIException."""
        exceptions = [
            NoteNotFoundError,
            CategoryNotFoundError,
            UnauthorizedAccessError,
            ValidationError
        ]
        
        for exception_class in exceptions:
            assert issubclass(exception_class, APIException)

    def test_exceptions_have_correct_status_codes(self):
        """Test that exceptions have correct HTTP status codes."""
        assert NoteNotFoundError().status_code == status.HTTP_404_NOT_FOUND
        assert CategoryNotFoundError().status_code == status.HTTP_404_NOT_FOUND
        assert UnauthorizedAccessError().status_code == status.HTTP_403_FORBIDDEN
        assert ValidationError().status_code == status.HTTP_400_BAD_REQUEST

    def test_exceptions_have_default_details(self):
        """Test that exceptions have appropriate default details."""
        assert NoteNotFoundError().default_detail == 'Note not found.'
        assert CategoryNotFoundError().default_detail == 'Category not found.'
        assert UnauthorizedAccessError().default_detail == 'You do not have permission to access this resource.'
        assert ValidationError().default_detail == 'Validation failed.'

    def test_exceptions_have_default_codes(self):
        """Test that exceptions have appropriate default codes."""
        assert NoteNotFoundError().default_code == 'note_not_found'
        assert CategoryNotFoundError().default_code == 'category_not_found'
        assert UnauthorizedAccessError().default_code == 'unauthorized_access'
        assert ValidationError().default_code == 'validation_error'

    def test_exceptions_can_be_raised(self):
        """Test that exceptions can be raised and caught."""
        with pytest.raises(NoteNotFoundError):
            raise NoteNotFoundError()
        
        with pytest.raises(CategoryNotFoundError):
            raise CategoryNotFoundError()
        
        with pytest.raises(UnauthorizedAccessError):
            raise UnauthorizedAccessError()
        
        with pytest.raises(ValidationError):
            raise ValidationError()

    def test_exceptions_with_custom_details_and_codes(self):
        """Test exceptions with custom details and codes."""
        # Test custom detail
        custom_detail = 'Custom error message'
        error = NoteNotFoundError(detail=custom_detail)
        assert error.detail == custom_detail
        assert error.default_code == 'note_not_found'
        
        # Test that default_code remains unchanged
        error = CategoryNotFoundError(detail='Custom category error')
        assert error.detail == 'Custom category error'
        assert error.default_code == 'category_not_found'
        
        error = UnauthorizedAccessError(detail='Custom unauthorized error')
        assert error.detail == 'Custom unauthorized error'
        assert error.default_code == 'unauthorized_access'
        
        error = ValidationError(detail='Custom validation error')
        assert error.detail == 'Custom validation error'
        assert error.default_code == 'validation_error'
