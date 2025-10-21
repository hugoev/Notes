# Notes App - Docker Development Setup

This guide will help you set up and run the Notes application using Docker for development.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### 1. Initial Setup

```bash
# Run the setup script
./scripts/dev-setup.sh
```

### 2. Start Development Environment

```bash
# Start all services
./scripts/start-dev.sh

# Or manually:
docker-compose -f docker-compose.dev.yml up
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Database**: localhost:5432

## Available Services

### Backend (Django)

- **Port**: 8000
- **API Endpoints**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Database**: PostgreSQL

### Frontend (Next.js)

- **Port**: 3000
- **Development Server**: http://localhost:3000
- **Hot Reload**: Enabled

### Database (PostgreSQL)

- **Port**: 5432
- **Database**: notes_db
- **User**: notes_user
- **Password**: notes_password

## Development Commands

### Start Services

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Start in background
docker-compose -f docker-compose.dev.yml up -d

# Start specific service
docker-compose -f docker-compose.dev.yml up backend
```

### Stop Services

```bash
# Stop all services
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes
docker-compose -f docker-compose.dev.yml down -v
```

### View Logs

```bash
# View all logs
docker-compose -f docker-compose.dev.yml logs

# View specific service logs
docker-compose -f docker-compose.dev.yml logs backend

# Follow logs in real-time
docker-compose -f docker-compose.dev.yml logs -f
```

### Database Operations

```bash
# Run migrations
docker-compose -f docker-compose.dev.yml run --rm backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.dev.yml run --rm backend python manage.py createsuperuser

# Access database shell
docker-compose -f docker-compose.dev.yml exec db psql -U notes_user -d notes_db
```

### Backend Commands

```bash
# Run Django shell
docker-compose -f docker-compose.dev.yml run --rm backend python manage.py shell

# Run tests
docker-compose -f docker-compose.dev.yml run --rm backend python manage.py test

# Collect static files
docker-compose -f docker-compose.dev.yml run --rm backend python manage.py collectstatic
```

### Frontend Commands

```bash
# Install new packages
docker-compose -f docker-compose.dev.yml run --rm frontend npm install package-name

# Run tests
docker-compose -f docker-compose.dev.yml run --rm frontend npm test

# Build for production
docker-compose -f docker-compose.dev.yml run --rm frontend npm run build
```

## File Structure

```
Notes/
├── docker-compose.yml          # Production compose file
├── docker-compose.dev.yml      # Development compose file
├── scripts/
│   ├── dev-setup.sh           # Initial setup script
│   ├── start-dev.sh           # Start development environment
│   └── stop-dev.sh            # Stop development environment
├── server/                     # Django Backend (clean structure!)
│   ├── manage.py              # Django management script
│   ├── Dockerfile             # Backend production image
│   ├── requirements.txt       # Python dependencies
│   ├── seed_data.py           # Database seeding script
│   ├── config/                # Django settings
│   │   ├── settings.py        # Base settings
│   │   ├── settings_docker.py # Docker settings
│   │   ├── urls.py           # URL configuration
│   │   ├── constants.py      # Application constants
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── utils.py          # Utility functions
│   ├── notes/                # Notes app
│   │   ├── models.py         # Note and Category models
│   │   ├── serializers.py    # API serializers
│   │   ├── views.py          # API views
│   │   └── migrations/       # Database migrations
│   └── accounts/             # User management app
│       ├── models.py         # User models
│       ├── serializers.py    # User serializers
│       ├── views.py          # User views
│       └── migrations/       # Database migrations
└── client/                    # Next.js Frontend
    ├── Dockerfile            # Frontend production image
    ├── Dockerfile.dev        # Frontend development image
    └── .dockerignore         # Frontend ignore file
```

## Environment Variables

### Backend Environment Variables

- `DEBUG`: Set to 1 for development
- `DATABASE_URL`: PostgreSQL connection string
- `DJANGO_SETTINGS_MODULE`: Django settings module

### Frontend Environment Variables

- `NODE_ENV`: Set to development
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Troubleshooting

### Common Issues

1. **Port Already in Use**

   ```bash
   # Check what's using the port
   lsof -i :3000
   lsof -i :8000

   # Kill the process
   kill -9 <PID>
   ```

2. **Database Connection Issues**

   ```bash
   # Check if database is running
   docker-compose -f docker-compose.dev.yml ps db

   # Restart database
   docker-compose -f docker-compose.dev.yml restart db
   ```

3. **Permission Issues**

   ```bash
   # Fix script permissions
   chmod +x scripts/*.sh
   ```

4. **Clean Start**

   ```bash
   # Stop all services and remove volumes
   docker-compose -f docker-compose.dev.yml down -v

   # Remove all images
   docker-compose -f docker-compose.dev.yml down --rmi all

   # Rebuild everything
   docker-compose -f docker-compose.dev.yml build --no-cache
   ```

### Reset Everything

```bash
# Stop and remove everything
docker-compose -f docker-compose.dev.yml down -v --rmi all

# Remove all containers and images
docker system prune -a

# Run setup again
./scripts/dev-setup.sh
```

## Production Deployment

For production deployment, use the main `docker-compose.yml` file:

```bash
# Build production images
docker-compose build

# Start production services
docker-compose up -d
```

## Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload in development mode
2. **Database Persistence**: Data is persisted in Docker volumes
3. **Logs**: Use `docker-compose logs -f` to follow logs in real-time
4. **Debugging**: You can exec into containers for debugging:
   ```bash
   docker-compose -f docker-compose.dev.yml exec backend bash
   docker-compose -f docker-compose.dev.yml exec frontend sh
   ```
