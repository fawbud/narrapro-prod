#!/usr/bin/env python
"""
Production-focused Supabase storage test
"""
import os
import sys
import django
import requests
import uuid
import json
from pathlib import Path

# Setup Django
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')

# Load environment variables from .env file
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

django.setup()

def test_production_upload():
    """Test production upload scenario"""
    supabase_url = os.getenv('SUPABASE_URL', 'https://ijabdhhlybsdvkebioce.supabase.co').rstrip('/')
    service_key = os.getenv('SUPABASE_SECRET_ACCESS_KEY')
    anon_key = os.getenv('SUPABASE_ACCESS_KEY_ID')
    bucket = os.getenv('SUPABASE_BUCKET_NAME', 'storage')

    print(f"=== Production Upload Test ===")
    print(f"Supabase URL: {supabase_url}")
    print(f"Bucket: {bucket}")
    print(f"Service key present: {'Yes' if service_key else 'No'}")
    print(f"Anon key present: {'Yes' if anon_key else 'No'}")

    # Test content with unique filename
    test_data = b"Production test upload"
    unique_filename = f"test-production/{uuid.uuid4()}.txt"

    # Headers for service role
    service_headers = {
        'Authorization': f'Bearer {service_key}',
        'apikey': service_key,
        'Content-Type': 'text/plain'
    }

    # Test different upload endpoints
    endpoints_to_test = [
        f"{supabase_url}/storage/v1/object/{bucket}/{unique_filename}",
        f"{supabase_url}/storage/v1/object/public/{bucket}/{unique_filename}",
    ]

    print(f"\n=== Testing Upload Endpoints ===")

    for endpoint in endpoints_to_test:
        print(f"\nTesting: {endpoint}")

        # Try POST
        try:
            response = requests.post(
                endpoint,
                data=test_data,
                headers=service_headers,
                timeout=30
            )
            print(f"POST: {response.status_code} - {response.text[:200]}")
            if response.status_code in [200, 201]:
                success_url = endpoint
                break
        except Exception as e:
            print(f"POST error: {e}")

        # Try PUT
        try:
            response = requests.put(
                endpoint,
                data=test_data,
                headers=service_headers,
                timeout=30
            )
            print(f"PUT: {response.status_code} - {response.text[:200]}")
            if response.status_code in [200, 201]:
                success_url = endpoint
                break
        except Exception as e:
            print(f"PUT error: {e}")

    # Test file listing with proper prefix
    print(f"\n=== Testing File List (with prefix) ===")
    list_url = f"{supabase_url}/storage/v1/object/list/{bucket}"
    list_payload = {
        "prefix": "test-production/",
        "limit": 100
    }

    try:
        response = requests.post(
            list_url,
            json=list_payload,
            headers=service_headers,
            timeout=30
        )
        print(f"List response: {response.status_code}")
        if response.status_code == 200:
            files = response.json()
            print(f"Files found: {len(files)}")
            for file in files[:3]:
                print(f"  - {file.get('name', file)}")
        else:
            print(f"List error: {response.text}")
    except Exception as e:
        print(f"List error: {e}")

    # Test bucket permissions and policies
    print(f"\n=== Testing Bucket Info ===")
    bucket_info_url = f"{supabase_url}/storage/v1/bucket/{bucket}"
    try:
        response = requests.get(bucket_info_url, headers=service_headers, timeout=30)
        print(f"Bucket info: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Bucket info error: {e}")

def test_django_storage_production():
    """Test Django storage in production mode"""
    print(f"\n=== Django Storage Production Test ===")

    # Set production mode temporarily
    os.environ['PRODUCTION'] = 'true'

    try:
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        print(f"Storage class: {default_storage.__class__.__name__}")
        print(f"Storage module: {default_storage.__class__.__module__}")

        # Test upload
        test_content = ContentFile(b"Django production test", name="django_test.txt")
        test_path = f"django-test/{uuid.uuid4()}.txt"

        try:
            saved_path = default_storage.save(test_path, test_content)
            print(f"✅ Django upload successful: {saved_path}")

            # Test URL generation
            file_url = default_storage.url(saved_path)
            print(f"✅ File URL: {file_url}")

            return True

        except Exception as e:
            print(f"❌ Django upload failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"❌ Django storage setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_production_upload()
    test_django_storage_production()