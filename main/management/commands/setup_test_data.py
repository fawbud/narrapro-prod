from django.core.management.base import BaseCommand
from narasumber.models import ExpertiseCategory


class Command(BaseCommand):
    help = 'Create sample expertise categories for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating expertise categories...')
        
        categories = [
            ('Technology', 'Software development, AI, cybersecurity, web development'),
            ('Business', 'Marketing, finance, entrepreneurship, management'),
            ('Health', 'Medicine, fitness, nutrition, wellness'),
            ('Education', 'Teaching, training, academic research'),
            ('Arts & Design', 'Graphic design, photography, music, visual arts'),
            ('Engineering', 'Civil, mechanical, electrical engineering'),
        ]

        created_count = 0
        for name, description in categories:
            category, created = ExpertiseCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {name}')
                )
                created_count += 1
            else:
                self.stdout.write(f'○ Already exists: {name}')

        total = ExpertiseCategory.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {created_count} new categories')
        )
        self.stdout.write(f'Total expertise categories: {total}')
        
        self.stdout.write('\nAvailable categories:')
        for cat in ExpertiseCategory.objects.all():
            self.stdout.write(f'- {cat.name}: {cat.description}')
