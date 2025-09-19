"""
Utility functions for testing and managing Supabase storage.
"""
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def test_supabase_connection():
    """
    Test if Supabase storage is properly configured and accessible.
    """
    try:
        # Check if we're using Supabase storage
        storage_backend = getattr(settings, 'DEFAULT_FILE_STORAGE', 'default')
        print(f"Storage backend: {storage_backend}")
        
        if 'SupabaseStorage' not in storage_backend:
            print("⚠️  Not using Supabase storage. Check PRODUCTION environment variable.")
            return False
        
        # Test file upload
        test_content = ContentFile(b"Test file content", name="test.txt")
        test_file_path = "test/connection_test.txt"
        
        # Save test file
        saved_path = default_storage.save(test_file_path, test_content)
        print(f"✅ Test file uploaded: {saved_path}")
        
        # Get URL
        file_url = default_storage.url(saved_path)
        print(f"✅ File URL generated: {file_url}")
        
        # Check if file exists
        if default_storage.exists(saved_path):
            print("✅ File exists in storage")
        else:
            print("❌ File not found in storage")
            return False
        
        # Clean up test file
        default_storage.delete(saved_path)
        print("✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase storage test failed: {str(e)}")
        return False


def check_environment_variables():
    """
    Check if all required Supabase environment variables are set.
    """
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
            print(f"✅ {var}: {'*' * (len(value) - 4)}{value[-4:]}")
    
    if missing_vars:
        print(f"\n❌ Missing or placeholder environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease update your .env file with actual Supabase credentials.")
        return False
    
    return True


def get_storage_info():
    """
    Display current storage configuration information.
    """
    print("=== Storage Configuration ===")
    print(f"PRODUCTION: {os.getenv('PRODUCTION', 'false')}")
    print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'default')}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    
    if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
        print(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
        print(f"AWS_S3_ENDPOINT_URL: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
    
    if hasattr(settings, 'MEDIA_ROOT'):
        print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")


def migrate_local_files_to_supabase():
    """
    Migrate existing local files to Supabase storage.
    Use this when switching from local to Supabase storage.
    """
    from event.models import EventProfile
    
    print("=== Migrating Event Cover Images to Supabase ===")
    
    migrated_count = 0
    error_count = 0
    
    for event in EventProfile.objects.all():
        if event.cover_image:
            try:
                # Re-save the file to trigger upload to Supabase
                old_path = event.cover_image.name
                
                # Read the file content
                file_content = event.cover_image.read()
                event.cover_image.seek(0)
                
                # Save the model to trigger new upload path
                event.save()
                
                print(f"✅ Migrated: {old_path} → {event.cover_image.name}")
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Failed to migrate {event.name}: {str(e)}")
                error_count += 1
    
    print(f"\n=== Migration Complete ===")
    print(f"Successfully migrated: {migrated_count} files")
    print(f"Errors: {error_count} files")


if __name__ == "__main__":
    print("=== Supabase Storage Configuration Test ===\n")
    
    # Check environment variables
    if check_environment_variables():
        print("\n✅ All environment variables are set")
    else:
        print("\n❌ Environment configuration incomplete")
        exit(1)
    
    # Display storage info
    print("\n")
    get_storage_info()
    
    # Test connection (only if using Supabase)
    if os.getenv('PRODUCTION') == 'true':
        print("\n=== Testing Supabase Connection ===")
        if test_supabase_connection():
            print("\n✅ Supabase storage is working correctly!")
        else:
            print("\n❌ Supabase storage test failed!")
    else:
        print("\n⚠️  PRODUCTION=false, using local storage for development")
