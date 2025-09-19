"""
Django management command to test Supabase storage configuration.
Usage: python manage.py test_supabase_storage
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os


class Command(BaseCommand):
    help = 'Test Supabase storage configuration and connectivity'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--migrate',
            action='store_true',
            help='Migrate existing local files to Supabase',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Supabase Storage Configuration Test ===\n')
        )
        
        # Check environment variables
        if self.check_environment_variables():
            self.stdout.write(self.style.SUCCESS("✅ All environment variables are set\n"))
        else:
            self.stdout.write(self.style.ERROR("❌ Environment configuration incomplete\n"))
            return
        
        # Display storage info
        self.display_storage_info()
        
        # Test connection if using Supabase
        if os.getenv('PRODUCTION') == 'true':
            self.stdout.write("=== Testing Supabase Connection ===")
            if self.test_supabase_connection():
                self.stdout.write(self.style.SUCCESS("\n✅ Supabase storage is working correctly!"))
            else:
                self.stdout.write(self.style.ERROR("\n❌ Supabase storage test failed!"))
        else:
            self.stdout.write(
                self.style.WARNING("⚠️  PRODUCTION=false, using local storage for development")
            )
        
        # Migrate files if requested
        if options['migrate']:
            self.migrate_local_files()
    
    def check_environment_variables(self):
        """Check if all required Supabase environment variables are set."""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_ACCESS_KEY_ID', 
            'SUPABASE_SECRET_ACCESS_KEY',
            'SUPABASE_BUCKET_NAME'
        ]
        
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.startswith('your_'):
                missing_vars.append(var)
            else:
                self.stdout.write(f"✅ {var}: {'*' * (len(value) - 4)}{value[-4:]}")
        
        if missing_vars:
            self.stdout.write(self.style.ERROR("\n❌ Missing or placeholder environment variables:"))
            for var in missing_vars:
                self.stdout.write(f"   - {var}")
            self.stdout.write("Please update your .env file with actual Supabase credentials.")
            return False
        
        return True
    
    def display_storage_info(self):
        """Display current storage configuration."""
        self.stdout.write("=== Storage Configuration ===")
        self.stdout.write(f"PRODUCTION: {os.getenv('PRODUCTION', 'false')}")
        self.stdout.write(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'default')}")
        self.stdout.write(f"MEDIA_URL: {settings.MEDIA_URL}")
        
        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            self.stdout.write(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
            self.stdout.write(f"AWS_S3_ENDPOINT_URL: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
        
        if hasattr(settings, 'MEDIA_ROOT'):
            self.stdout.write(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
        
        self.stdout.write("")
    
    def test_supabase_connection(self):
        """Test Supabase storage connectivity."""
        try:
            # Check storage backend
            storage_backend = getattr(settings, 'DEFAULT_FILE_STORAGE', 'default')
            self.stdout.write(f"Storage backend: {storage_backend}")
            
            if 'Supabase' not in storage_backend:
                self.stdout.write(
                    self.style.WARNING("⚠️  Not using Supabase storage. Check PRODUCTION environment variable.")
                )
                return False
            
            # Test file upload
            test_content = ContentFile(b"Test file content for Supabase connectivity", name="test.txt")
            test_file_path = "test/connection_test.txt"
            
            # Save test file
            saved_path = default_storage.save(test_file_path, test_content)
            self.stdout.write(f"✅ Test file uploaded: {saved_path}")
            
            # Get URL
            file_url = default_storage.url(saved_path)
            self.stdout.write(f"✅ File URL generated: {file_url}")
            
            # Check if file exists
            if default_storage.exists(saved_path):
                self.stdout.write("✅ File exists in storage")
            else:
                self.stdout.write(self.style.ERROR("❌ File not found in storage"))
                return False
            
            # Clean up test file
            default_storage.delete(saved_path)
            self.stdout.write("✅ Test file cleaned up")
            
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Supabase storage test failed: {str(e)}"))
            return False
    
    def migrate_local_files(self):
        """Migrate existing local files to Supabase."""
        from event.models import EventProfile
        
        self.stdout.write("=== Migrating Event Cover Images to Supabase ===")
        
        migrated_count = 0
        error_count = 0
        
        for event in EventProfile.objects.all():
            if event.cover_image:
                try:
                    old_path = event.cover_image.name
                    
                    # Trigger re-upload by saving the model
                    event.save()
                    
                    self.stdout.write(f"✅ Migrated: {old_path} → {event.cover_image.name}")
                    migrated_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Failed to migrate {event.name}: {str(e)}")
                    )
                    error_count += 1
        
        self.stdout.write(f"\n=== Migration Complete ===")
        self.stdout.write(self.style.SUCCESS(f"Successfully migrated: {migrated_count} files"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count} files"))
