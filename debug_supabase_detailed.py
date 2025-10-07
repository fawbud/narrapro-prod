#!/usr/bin/env python
"""
Detailed debug script for Supabase storage issues.
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from django.conf import settings

def test_environment_vars():
    """Check all environment variables."""
    print('=== Environment Variables ===')
    env_vars = [
        'PRODUCTION',
        'SUPABASE_URL', 
        'SUPABASE_ACCESS_KEY_ID',
        'SUPABASE_SECRET_ACCESS_KEY',
        'SUPABASE_BUCKET_NAME'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'SECRET' in var:
                # Mask sensitive data
                masked = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
                print(f'✅ {var}: {masked}')
            else:
                print(f'✅ {var}: {value}')
        else:
            print(f'❌ {var}: Not set')

def test_django_settings():
    """Check Django settings."""
    print('\n=== Django Settings ===')
    settings_to_check = [
        'DEFAULT_FILE_STORAGE',
        'AWS_S3_ENDPOINT_URL', 
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'MEDIA_URL'
    ]
    
    for setting in settings_to_check:
        value = getattr(settings, setting, 'Not set')
        if 'KEY' in setting or 'SECRET' in setting:
            # Mask sensitive data
            if value != 'Not set' and len(str(value)) > 20:
                masked = f"{str(value)[:10]}...{str(value)[-10:]}"
                print(f'✅ {setting}: {masked}')
            else:
                print(f'✅ {setting}: ***')
        else:
            print(f'✅ {setting}: {value}')

def test_boto3_connection():
    """Test direct boto3 connection."""
    print('\n=== Boto3 Connection Test ===')
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        # Get credentials from environment
        access_key = os.getenv('SUPABASE_ACCESS_KEY_ID')
        secret_key = os.getenv('SUPABASE_SECRET_ACCESS_KEY')
        endpoint_url = os.getenv('SUPABASE_URL')
        bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'storage')
        
        if not all([access_key, secret_key, endpoint_url]):
            print('❌ Missing required credentials')
            return False
        
        # Create session
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-east-1'
        )
        
        # Create S3 client
        s3_client = session.client(
            's3',
            endpoint_url=endpoint_url,
            region_name='us-east-1'
        )
        
        print('✅ S3 client created successfully')
        
        # Test 1: List buckets
        try:
            response = s3_client.list_buckets()
            print(f'✅ Connection successful! Found {len(response["Buckets"])} buckets:')
            bucket_names = []
            for bucket in response['Buckets']:
                bucket_names.append(bucket['Name'])
                print(f'   - {bucket["Name"]}')
                
            # Test 2: Check specific bucket
            if bucket_name in bucket_names:
                print(f'✅ Bucket "{bucket_name}" found in bucket list')
            else:
                print(f'❌ Bucket "{bucket_name}" NOT found in bucket list')
                print(f'Available buckets: {bucket_names}')
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f'❌ Failed to list buckets: {error_code} - {e.response["Error"]["Message"]}')
            return False
        
        # Test 3: Access specific bucket
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f'✅ Bucket "{bucket_name}" is accessible')
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f'❌ Bucket "{bucket_name}" does not exist')
            elif error_code == '403':
                print(f'❌ Access denied to bucket "{bucket_name}"')
            else:
                print(f'❌ Error accessing bucket "{bucket_name}": {error_code} - {e.response["Error"]["Message"]}')
            return False
        
        # Test 4: Try to list objects in bucket
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            object_count = response.get('KeyCount', 0)
            print(f'✅ Can list objects in bucket "{bucket_name}" (found {object_count} objects)')
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f'❌ Cannot list objects in bucket "{bucket_name}": {error_code} - {e.response["Error"]["Message"]}')
        
        return True
        
    except ImportError:
        print('❌ boto3 not installed')
        return False
    except NoCredentialsError:
        print('❌ Invalid credentials')
        return False
    except Exception as e:
        print(f'❌ Connection failed: {str(e)}')
        return False

def test_django_storage():
    """Test Django's storage backend."""
    print('\n=== Django Storage Test ===')
    
    try:
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        print(f'Storage backend: {default_storage.__class__.__name__}')
        
        # Test file upload
        test_content = ContentFile(b"Test file for debugging", name="debug_test.txt")
        test_path = "debug/test_upload.txt"
        
        try:
            saved_path = default_storage.save(test_path, test_content)
            print(f'✅ File uploaded successfully: {saved_path}')
            
            # Test URL generation
            file_url = default_storage.url(saved_path)
            print(f'✅ File URL generated: {file_url}')
            
            # Test file existence
            if default_storage.exists(saved_path):
                print('✅ File exists in storage')
            else:
                print('❌ File not found in storage')
            
            # Clean up
            default_storage.delete(saved_path)
            print('✅ Test file cleaned up')
            
            return True
            
        except Exception as e:
            print(f'❌ File upload failed: {str(e)}')
            return False
            
    except Exception as e:
        print(f'❌ Django storage test failed: {str(e)}')
        return False

if __name__ == '__main__':
    print('=== Detailed Supabase Storage Debug ===\n')
    
    # Test environment variables
    test_environment_vars()
    
    # Test Django settings
    test_django_settings()
    
    # Test boto3 connection
    boto3_success = test_boto3_connection()
    
    # Test Django storage
    django_success = test_django_storage()
    
    print('\n=== Summary ===')
    if boto3_success and django_success:
        print('✅ All tests passed! Supabase storage should be working.')
    elif boto3_success:
        print('⚠️  Boto3 connection works, but Django storage has issues.')
    elif django_success:
        print('⚠️  Django storage works, but boto3 connection has issues.')
    else:
        print('❌ Both boto3 and Django storage tests failed.')
