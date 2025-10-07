#!/usr/bin/env python
"""
Test script to debug Supabase storage upload directly.
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

import requests
from django.core.files.base import ContentFile
from narrapro.storage_backends import SupabaseStorage

def test_direct_upload():
    """Test direct upload to Supabase storage API."""
    # Get configuration
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'storage')
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Bucket: {bucket_name}")
    print(f"Key present: {'Yes' if supabase_key else 'No'}")
    
    # Create test content
    test_content = b"This is a test file content for debugging upload issues."
    test_filename = "test_uploads/debug_upload_test.txt"
    
    # Method 1: Try POST upload (current approach)
    print("\n=== Testing POST upload ===")
    upload_url_post = f"{supabase_url}/storage/v1/object/{bucket_name}/{test_filename}"
    headers_post = {
        'Authorization': f'Bearer {supabase_key}',
        'apikey': supabase_key,
        'Content-Type': 'text/plain',
        'Cache-Control': 'max-age=86400'
    }
    
    try:
        response_post = requests.post(upload_url_post, data=test_content, headers=headers_post, timeout=30)
        print(f"POST Response: {response_post.status_code}")
        print(f"POST Response text: {response_post.text}")
    except Exception as e:
        print(f"POST Error: {e}")
    
    # Method 2: Try PUT upload
    print("\n=== Testing PUT upload ===")
    upload_url_put = f"{supabase_url}/storage/v1/object/{bucket_name}/{test_filename}"
    headers_put = {
        'Authorization': f'Bearer {supabase_key}',
        'apikey': supabase_key,
        'Content-Type': 'text/plain'
    }
    
    try:
        response_put = requests.put(upload_url_put, data=test_content, headers=headers_put, timeout=30)
        print(f"PUT Response: {response_put.status_code}")
        print(f"PUT Response text: {response_put.text}")
    except Exception as e:
        print(f"PUT Error: {e}")
    
    # Method 3: Test with Django storage backend
    print("\n=== Testing Django storage backend ===")
    try:
        storage = SupabaseStorage()
        test_file = ContentFile(test_content)
        test_file.name = "debug_django_test.txt"
        saved_name = storage.save("test_uploads/debug_django_test.txt", test_file)
        print(f"Django storage saved: {saved_name}")
        print(f"File URL: {storage.url(saved_name)}")
    except Exception as e:
        print(f"Django storage error: {e}")

if __name__ == "__main__":
    test_direct_upload()
