import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from narasumber.models import ExpertiseCategory

categories = [
    ('Technology', 'Software development, AI, cybersecurity, etc.'),
    ('Business', 'Marketing, finance, entrepreneurship, etc.'),
    ('Health', 'Medicine, fitness, nutrition, wellness, etc.'),
    ('Education', 'Teaching, training, academic research, etc.'),
    ('Arts & Design', 'Graphic design, photography, music, etc.'),
    ('Engineering', 'Civil, mechanical, electrical engineering, etc.'),
]

print("Creating expertise categories...")
for name, desc in categories:
    category, created = ExpertiseCategory.objects.get_or_create(
        name=name, 
        defaults={'description': desc}
    )
    if created:
        print(f'✓ Created: {name}')
    else:
        print(f'○ Already exists: {name}')

print(f"\nTotal categories: {ExpertiseCategory.objects.count()}")
