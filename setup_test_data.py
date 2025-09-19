import os
import django
import sys

# Add the project directory to Python path
sys.path.append('/c/Coding_Projects/narrapro')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from narasumber.models import ExpertiseCategory

print("Creating expertise categories...")

# Create categories
categories = [
    ('Technology', 'Software development, AI, cybersecurity, web development'),
    ('Business', 'Marketing, finance, entrepreneurship, management'),
    ('Health', 'Medicine, fitness, nutrition, wellness'),
    ('Education', 'Teaching, training, academic research'),
    ('Arts & Design', 'Graphic design, photography, music, visual arts'),
    ('Engineering', 'Civil, mechanical, electrical engineering'),
]

for name, description in categories:
    category, created = ExpertiseCategory.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    if created:
        print(f'✓ Created: {name}')
    else:
        print(f'○ Already exists: {name}')

total = ExpertiseCategory.objects.count()
print(f'\nTotal expertise categories: {total}')

print("\nAvailable categories:")
for cat in ExpertiseCategory.objects.all():
    print(f"- {cat.name}: {cat.description}")
