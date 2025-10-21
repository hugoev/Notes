"""
Application constants and configuration values.
"""

# API Configuration
API_VERSION = 'v1'
API_PREFIX = f'api/{API_VERSION}'

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Rate Limiting
AUTH_RATE_LIMIT = '5/minute'
GENERAL_RATE_LIMIT = '100/hour'

# Note Configuration
MAX_NOTE_TITLE_LENGTH = 200
MAX_NOTE_CONTENT_LENGTH = 10000
MAX_CATEGORY_NAME_LENGTH = 100

# Search Configuration
SEARCH_FIELDS = ['title', 'content']
ORDERING_FIELDS = ['created_at', 'updated_at', 'title']
DEFAULT_ORDERING = ['-updated_at']

# Filter Configuration
FILTER_FIELDS = ['category', 'is_pinned']

# JWT Configuration
ACCESS_TOKEN_LIFETIME_MINUTES = 60
REFRESH_TOKEN_LIFETIME_DAYS = 7

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Security
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'backend']
