"""
Notes application models.

This module contains the core data models for the Notes application,
including Note and Category models with proper relationships and constraints.
"""

from typing import List, Optional

from config.constants import MAX_CATEGORY_NAME_LENGTH, MAX_NOTE_TITLE_LENGTH
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """
    Category model for organizing notes.
    
    Each category belongs to a specific user and can contain multiple notes.
    Categories help users organize their notes by topic or purpose.
    """
    
    name = models.CharField(
        max_length=MAX_CATEGORY_NAME_LENGTH,
        help_text="Name of the category"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        help_text="User who owns this category"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this category was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this category was last updated"
    )
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'user']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['user', 'name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        """Return string representation of the category."""
        return f"{self.name} ({self.user.username})"
    
    def clean(self) -> None:
        """Validate the category instance."""
        super().clean()
        if not self.name or not self.name.strip():
            raise ValidationError("Category name cannot be empty.")
        
        # Check for duplicate names within the same user
        if Category.objects.filter(
            name__iexact=self.name.strip(),
            user=self.user
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                f"A category with the name '{self.name}' already exists for this user."
            )
    
    def save(self, *args, **kwargs) -> None:
        """Save the category with validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def notes_count(self) -> int:
        """Return the number of notes in this category."""
        return self.notes.count()
    
    def get_notes(self) -> models.QuerySet:
        """Return all notes in this category."""
        return self.notes.all()


class Note(models.Model):
    """
    Note model for storing user notes.
    
    Each note belongs to a specific user and optionally to a category.
    Notes support pinning for quick access and have timestamps for tracking.
    """
    
    title = models.CharField(
        max_length=MAX_NOTE_TITLE_LENGTH,
        help_text="Title of the note"
    )
    content = models.TextField(
        help_text="Content of the note"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
        help_text="User who owns this note"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes',
        help_text="Category this note belongs to (optional)"
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Whether this note is pinned for quick access"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this note was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this note was last updated"
    )
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        indexes = [
            models.Index(fields=['user', 'is_pinned', 'updated_at']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self) -> str:
        """Return string representation of the note."""
        return f"{self.title} ({self.user.username})"
    
    def clean(self) -> None:
        """Validate the note instance."""
        super().clean()
        if not self.title or not self.title.strip():
            raise ValidationError("Note title cannot be empty.")
        
        if not self.content or not self.content.strip():
            raise ValidationError("Note content cannot be empty.")
        
        # Ensure category belongs to the same user
        if self.category and self.category.user != self.user:
            raise ValidationError(
                "Category must belong to the same user as the note."
            )
    
    def save(self, *args, **kwargs) -> None:
        """Save the note with validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def word_count(self) -> int:
        """Return the word count of the note content."""
        return len(self.content.split())
    
    @property
    def character_count(self) -> int:
        """Return the character count of the note content."""
        return len(self.content)
    
    @property
    def is_recent(self) -> bool:
        """Return True if the note was created within the last 7 days."""
        return (timezone.now() - self.created_at).days <= 7
    
    def pin(self) -> None:
        """Pin the note."""
        self.is_pinned = True
        self.save(update_fields=['is_pinned'])
    
    def unpin(self) -> None:
        """Unpin the note."""
        self.is_pinned = False
        self.save(update_fields=['is_pinned'])
    
    def move_to_category(self, category: Optional[Category]) -> None:
        """Move the note to a different category."""
        if category and category.user != self.user:
            raise ValidationError(
                "Cannot move note to a category owned by a different user."
            )
        self.category = category
        self.save(update_fields=['category'])
    
    @classmethod
    def get_user_notes(cls, user: User) -> models.QuerySet:
        """Return all notes for a specific user."""
        return cls.objects.filter(user=user)
    
    @classmethod
    def get_pinned_notes(cls, user: User) -> models.QuerySet:
        """Return all pinned notes for a specific user."""
        return cls.objects.filter(user=user, is_pinned=True)
    
    @classmethod
    def get_notes_by_category(cls, user: User, category: Category) -> models.QuerySet:
        """Return all notes for a specific user and category."""
        return cls.objects.filter(user=user, category=category)