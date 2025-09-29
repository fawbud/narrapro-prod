#!/usr/bin/env python
"""
Debug script to test Supabase storage uploads and identify specific issues.
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import traceback


def debug_supabase_storage():
    """
    Debug Supabase storage configuration and test upload functionality.
    """
    print("=== Supabase Storage Debug ===\n")
    
    # 1. Check configuration
    print("1. Configuration Check:")
    print(f"   Storage Backend: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'default')}")
    print(f"   Media URL: {settings.MEDIA_URL}")
    print(f"   AWS_ACCESS_KEY_ID present: {'Yes' if hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID else 'No'}")
    print(f"   AWS_SECRET_ACCESS_KEY present: {'Yes' if hasattr(settings, 'AWS_SECRET_ACCESS_KEY') and settings.AWS_SECRET_ACCESS_KEY else 'No'}")
    print(f"   AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"   AWS_S3_ENDPOINT_URL: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
    print()
    
    # 2. Test storage initialization
    print("2. Storage Initialization Test:")
    try:
        storage = default_storage
        print(f"   ✅ Storage object created: {type(storage).__name__}")
        
        # Check storage attributes
        if hasattr(storage, 'bucket_name'):
            print(f"   Bucket name: {storage.bucket_name}")
        if hasattr(storage, 'endpoint_url'):
            print(f"   Endpoint URL: {storage.endpoint_url}")
        if hasattr(storage, 'custom_domain'):
            print(f"   Custom domain: {getattr(storage, 'custom_domain', 'Not set')}")
            
    except Exception as e:
        print(f"   ❌ Storage initialization failed: {str(e)}")
        traceback.print_exc()
        return False
    print()
    
    # 3. Test file upload
    print("3. File Upload Test:")
    try:
        # Create test content
        test_content = ContentFile(b"Test file content for Supabase upload", name="test_upload.txt")
        test_file_path = "debug_test/upload_test.txt"
        
        print(f"   Attempting to upload: {test_file_path}")
        
        # Save test file
        saved_path = default_storage.save(test_file_path, test_content)
        print(f"   ✅ File uploaded successfully: {saved_path}")
        
        # Get file URL
        file_url = default_storage.url(saved_path)
        print(f"   ✅ File URL generated: {file_url}")
        
        # Check if file exists
        if default_storage.exists(saved_path):
            print(f"   ✅ File exists in storage")
        else:
            print(f"   ❌ File not found in storage")
            return False
        
        # Try to read the file back
        try:
            with default_storage.open(saved_path, 'rb') as f:
                content = f.read()
                print(f"   ✅ File content read back: {len(content)} bytes")
        except Exception as e:
            print(f"   ⚠️  Could not read file back: {str(e)}")
        
        # Clean up test file
        try:
            default_storage.delete(saved_path)
            print(f"   ✅ Test file cleaned up")
        except Exception as e:
            print(f"   ⚠️  Could not clean up test file: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ File upload failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        traceback.print_exc()
        return False
    print()


def test_specific_upload_paths():
    """
    Test the specific upload paths used by your models.
    """
    print("4. Model Upload Path Test:")
    
    # Test event cover upload path
    try:
        from event.models import event_cover_upload_path
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Create a mock user and instance for path testing
        class MockUser:
            id = 123
        
        class MockEventInstance:
            user = MockUser()
        
        mock_instance = MockEventInstance()
        test_filename = "test_event_cover.jpg"
        
        upload_path = event_cover_upload_path(mock_instance, test_filename)
        print(f"   Event cover upload path: {upload_path}")
        
        # Test actual upload with this path
        test_content = ContentFile(b"Mock event cover image content", name=test_filename)
        
        saved_path = default_storage.save(upload_path, test_content)
        print(f"   ✅ Event cover uploaded: {saved_path}")
        
        file_url = default_storage.url(saved_path)
        print(f"   ✅ Event cover URL: {file_url}")
        
        # Clean up
        default_storage.delete(saved_path)
        print(f"   ✅ Event cover cleaned up")
        
    except Exception as e:
        print(f"   ❌ Event cover upload test failed: {str(e)}")
        traceback.print_exc()
    
    # Test narasumber profile picture upload path
    try:
        from narasumber.models import narasumber_profile_picture_upload_path
        
        class MockNarasumberInstance:
            user = MockUser()
        
        mock_instance = MockNarasumberInstance()
        test_filename = "test_profile_picture.jpg"
        
        upload_path = narasumber_profile_picture_upload_path(mock_instance, test_filename)
        print(f"   Narasumber profile upload path: {upload_path}")
        
        # Test actual upload with this path
        test_content = ContentFile(b"Mock profile picture content", name=test_filename)
        
        saved_path = default_storage.save(upload_path, test_content)
        print(f"   ✅ Profile picture uploaded: {saved_path}")
        
        file_url = default_storage.url(saved_path)
        print(f"   ✅ Profile picture URL: {file_url}")
        
        # Clean up
        default_storage.delete(saved_path)
        print(f"   ✅ Profile picture cleaned up")
        
    except Exception as e:
        print(f"   ❌ Profile picture upload test failed: {str(e)}")
        traceback.print_exc()


def check_supabase_bucket_permissions():
    """
    Test if the bucket is accessible and has correct permissions.
    """
    print("5. Bucket Permissions Test:")
    
    try:
        from storages.backends.s3boto3 import S3Boto3Storage
        import boto3
        from botocore.exceptions import ClientError
        
        # Create S3 client with Supabase credentials
        s3_client = boto3.client(
            's3',
            endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY'),
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
        )
        
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        
        # Test bucket access
        try:
            response = s3_client.head_bucket(Bucket=bucket_name)
            print(f"   ✅ Bucket '{bucket_name}' is accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"   ❌ Bucket '{bucket_name}' does not exist")
            elif error_code == '403':
                print(f"   ❌ Access denied to bucket '{bucket_name}' - check credentials")
            else:
                print(f"   ❌ Bucket access error: {error_code}")
            return False
        
        # Test list objects (to verify permissions)
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            print(f"   ✅ Can list objects in bucket")
        except ClientError as e:
            print(f"   ⚠️  Cannot list objects: {e.response['Error']['Code']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Bucket permissions test failed: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = debug_supabase_storage()
    
    if success:
        test_specific_upload_paths()
        check_supabase_bucket_permissions()
        print("\n=== Debug Complete ===")
        print("✅ Basic Supabase storage functionality is working!")
    else:
        print("\n=== Debug Complete ===")
        print("❌ Supabase storage has issues that need to be resolved.")
        print("\nCommon solutions:")
        print("1. Verify Supabase credentials are correct")
        print("2. Check that the storage bucket exists and is public")
        print("3. Ensure service role key has storage permissions")
        print("4. Verify Supabase project URL is correct")
