#!/usr/bin/env python
"""
Database seeding script for Notes app.
Creates 10,000+ mock notes with realistic data.
"""

import os
import random
import sys
from datetime import datetime, timedelta

import django
from faker import Faker

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_docker')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from notes.models import Category, Note

fake = Faker()

def create_categories(user, num_categories=20):
    """Create realistic categories for the user."""
    categories = []
    
    # Common note categories
    category_names = [
        'Work', 'Personal', 'Ideas', 'Shopping', 'Travel', 'Health', 'Finance',
        'Learning', 'Projects', 'Meetings', 'Recipes', 'Books', 'Movies',
        'Goals', 'Journal', 'Reminders', 'Research', 'Code', 'Design', 'Random'
    ]
    
    for name in category_names[:num_categories]:
        category, created = Category.objects.get_or_create(
            name=name,
            user=user,
            defaults={'name': name}
        )
        categories.append(category)
    
    return categories

def generate_realistic_note():
    """Generate realistic note content."""
    note_types = [
        {
            'title_templates': [
                'Meeting Notes: {topic}',
                'Ideas for {project}',
                'Thoughts on {subject}',
                'Research: {topic}',
                'Todo: {task}',
                'Recipe: {dish}',
                'Book Notes: {book}',
                'Project Update: {project}',
                'Learning: {skill}',
                'Reminder: {task}'
            ],
            'content_templates': [
                'Key points from today\'s discussion:\n• {point1}\n• {point2}\n• {point3}\n\nNext steps: {action}',
                'Interesting idea: {idea}\n\nPros:\n• {pro1}\n• {pro2}\n\nCons:\n• {con1}\n• {con2}',
                'Research findings:\n\n{findings}\n\nSources:\n• {source1}\n• {source2}',
                'Today I learned:\n\n{learning}\n\nKey takeaways:\n• {takeaway1}\n• {takeaway2}',
                'Project status:\n\nCompleted:\n• {completed1}\n• {completed2}\n\nIn progress:\n• {inprogress}\n\nNext: {next}',
                'Recipe for {dish}:\n\nIngredients:\n• {ingredient1}\n• {ingredient2}\n• {ingredient3}\n\nInstructions:\n{instructions}',
                'Book summary: {book}\n\nMain themes:\n• {theme1}\n• {theme2}\n\nFavorite quotes:\n"{quote}"',
                'Meeting with {person}:\n\nAgenda:\n• {agenda1}\n• {agenda2}\n\nOutcomes:\n• {outcome1}\n• {outcome2}',
                'Learning {skill}:\n\nResources:\n• {resource1}\n• {resource2}\n\nProgress: {progress}',
                'Reminder: {task}\n\nDue: {due_date}\nPriority: {priority}\nNotes: {notes}'
            ]
        }
    ]
    
    note_type = random.choice(note_types)
    title_template = random.choice(note_type['title_templates'])
    content_template = random.choice(note_type['content_templates'])
    
    # Generate realistic data for placeholders
    topics = ['AI', 'Marketing', 'Product Development', 'Team Building', 'Budget Planning', 'Customer Research']
    projects = ['Website Redesign', 'Mobile App', 'Database Migration', 'Content Strategy', 'Analytics Dashboard']
    subjects = ['Machine Learning', 'User Experience', 'Data Science', 'Cloud Computing', 'Agile Methodology']
    tasks = ['Review Documents', 'Update Database', 'Schedule Meeting', 'Prepare Presentation', 'Analyze Data']
    dishes = ['Pasta Carbonara', 'Chicken Curry', 'Chocolate Cake', 'Caesar Salad', 'Beef Stir Fry']
    books = ['Atomic Habits', 'The Lean Startup', 'Thinking Fast and Slow', 'Sapiens', 'The Art of War']
    skills = ['Python Programming', 'React Development', 'Data Analysis', 'Project Management', 'Public Speaking']
    people = ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Lisa Davis', 'Alex Rodriguez']
    
    # Fill in the templates
    title = title_template.format(
        topic=random.choice(topics),
        project=random.choice(projects),
        subject=random.choice(subjects),
        task=random.choice(tasks),
        dish=random.choice(dishes),
        book=random.choice(books),
        skill=random.choice(skills)
    )
    
    # Create a safe format dictionary with all possible keys
    format_dict = {
        'point1': fake.sentence(),
        'point2': fake.sentence(),
        'point3': fake.sentence(),
        'action': fake.sentence(),
        'idea': fake.sentence(),
        'pro1': fake.sentence(),
        'pro2': fake.sentence(),
        'con1': fake.sentence(),
        'con2': fake.sentence(),
        'findings': fake.paragraph(),
        'source1': fake.url(),
        'source2': fake.url(),
        'learning': fake.paragraph(),
        'takeaway1': fake.sentence(),
        'takeaway2': fake.sentence(),
        'completed1': fake.sentence(),
        'completed2': fake.sentence(),
        'inprogress': fake.sentence(),
        'next': fake.sentence(),
        'ingredient1': fake.word(),
        'ingredient2': fake.word(),
        'ingredient3': fake.word(),
        'instructions': fake.paragraph(),
        'theme1': fake.word(),
        'theme2': fake.word(),
        'quote': fake.sentence(),
        'person': random.choice(people),
        'agenda1': fake.sentence(),
        'agenda2': fake.sentence(),
        'outcome1': fake.sentence(),
        'outcome2': fake.sentence(),
        'resource1': fake.url(),
        'resource2': fake.url(),
        'progress': fake.sentence(),
        'due_date': fake.date_between(start_date='-30d', end_date='+30d').strftime('%Y-%m-%d'),
        'priority': random.choice(['High', 'Medium', 'Low']),
        'notes': fake.sentence(),
        'book': random.choice(books),
        'topic': random.choice(topics),
        'project': random.choice(projects),
        'subject': random.choice(subjects),
        'task': random.choice(tasks),
        'dish': random.choice(dishes),
        'skill': random.choice(skills)
    }
    
    try:
        content = content_template.format(**format_dict)
    except KeyError as e:
        # If there's a missing key, use a simple fallback
        content = fake.paragraph()
    
    return title, content

def create_notes(user, categories, num_notes=10000):
    """Create a large number of realistic notes."""
    print(f"Creating {num_notes} notes for user: {user.username}")
    
    # Create notes in batches to avoid memory issues
    batch_size = 1000
    notes_created = 0
    
    for batch_num in range(0, num_notes, batch_size):
        current_batch_size = min(batch_size, num_notes - batch_num)
        notes_to_create = []
        
        print(f"Creating batch {batch_num // batch_size + 1}/{(num_notes + batch_size - 1) // batch_size} ({current_batch_size} notes)")
        
        for i in range(current_batch_size):
            title, content = generate_realistic_note()
            
            # Random creation date within the last 2 years
            days_ago = random.randint(0, 730)
            created_at = timezone.now() - timedelta(days=days_ago)
            
            # Random update date (usually close to creation date, sometimes much later)
            if random.random() < 0.3:  # 30% chance of being updated
                update_days_ago = random.randint(0, days_ago)
                updated_at = timezone.now() - timedelta(days=update_days_ago)
            else:
                updated_at = created_at
            
            note = Note(
                title=title,
                content=content,
                user=user,
                category=random.choice(categories) if random.random() < 0.7 else None,  # 70% have category
                is_pinned=random.random() < 0.05,  # 5% are pinned
                created_at=created_at,
                updated_at=updated_at
            )
            notes_to_create.append(note)
        
        # Bulk create notes
        Note.objects.bulk_create(notes_to_create, batch_size=100)
        notes_created += len(notes_to_create)
        
        print(f"Created {notes_created}/{num_notes} notes so far...")
    
    return notes_created

def main():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    # Get or create the admin user
    try:
        user = User.objects.get(username='admin')
        print(f"Using existing user: {user.username}")
    except User.DoesNotExist:
        print("Creating admin user...")
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
    
    # Create categories
    print("Creating categories...")
    categories = create_categories(user)
    print(f"Created {len(categories)} categories")
    
    # Check if notes already exist
    existing_notes = Note.objects.filter(user=user).count()
    if existing_notes > 0:
        print(f"Found {existing_notes} existing notes. Do you want to add more? (y/n)")
        response = input().lower()
        if response != 'y':
            print("Seeding cancelled.")
            return
    
    # Create notes
    num_notes = 10000
    notes_created = create_notes(user, categories, num_notes)
    
    print(f"✅ Seeding complete!")
    print(f"📊 Statistics:")
    print(f"   - User: {user.username}")
    print(f"   - Categories: {len(categories)}")
    print(f"   - Notes created: {notes_created}")
    print(f"   - Total notes for user: {Note.objects.filter(user=user).count()}")
    print(f"   - Pinned notes: {Note.objects.filter(user=user, is_pinned=True).count()}")
    print(f"   - Notes with categories: {Note.objects.filter(user=user, category__isnull=False).count()}")

if __name__ == '__main__':
    main()
