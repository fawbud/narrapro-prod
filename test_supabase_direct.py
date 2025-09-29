#!/usr/bin/env python
"""
Test direct Supabase API calls to understand the correct endpoints
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
sys.path.insert(0, os.getcwd())
django.setup()

def test_supabase_storage_api():
    """Test various Supabase storage API endpoints"""
    supabase_url = os.getenv('SUPABASE_URL', 'https://ijabdhhlybsdvkebioce.supabase.co')
    service_key = os.getenv('SUPABASE_SECRET_ACCESS_KEY')
    anon_key = os.getenv('SUPABASE_ACCESS_KEY_ID')
    bucket = os.getenv('SUPABASE_BUCKET_NAME', 'storage')
    
    print(f"Testing with bucket: {bucket}")
    print(f"Supabase URL: {supabase_url}")
    
    # Test content
    test_data = b"Hello Supabase Storage Test!"
    filename = "test-uploads/api-test.txt"
    
    # Test 1: List buckets to verify connection
    print("\n=== Testing bucket list ===")
    buckets_url = f"{supabase_url}/storage/v1/bucket"
    headers = {
        'Authorization': f'Bearer {service_key}',
        'apikey': service_key
    }
    
    try:
        response = requests.get(buckets_url, headers=headers)
        print(f"Buckets response: {response.status_code}")
        if response.status_code == 200:
            buckets = response.json()
            print(f"Available buckets: {[b.get('name', b) for b in buckets]}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Bucket list error: {e}")
    
    # Test 2: Try standard upload endpoint
    print("\n=== Testing standard upload ===")
    upload_endpoints = [
        f"{supabase_url}/storage/v1/object/{bucket}/{filename}",
        f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}",
    ]
    
    for endpoint in upload_endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        
        # Try with service role key
        try:
            response = requests.post(
                endpoint,
                data=test_data,
                headers={
                    'Authorization': f'Bearer {service_key}',
                    'apikey': service_key,
                    'Content-Type': 'text/plain'
                },
                timeout=30
            )
            print(f"POST (service): {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"POST (service) error: {e}")
        
        # Try with anon key
        try:
            response = requests.post(
                endpoint,
                data=test_data,
                headers={
                    'Authorization': f'Bearer {anon_key}',
                    'apikey': anon_key,
                    'Content-Type': 'text/plain'
                },
                timeout=30
            )
            print(f"POST (anon): {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"POST (anon) error: {e}")
    
    # Test 3: Check if upload worked by listing files
    print("\n=== Testing file list ===")
    list_url = f"{supabase_url}/storage/v1/object/list/{bucket}"
    try:
        response = requests.post(
            list_url,
            json={"limit": 100, "offset": 0},
            headers=headers
        )
        print(f"File list response: {response.status_code}")
        if response.status_code == 200:
            files = response.json()
            print(f"Files found: {len(files)}")
            for file in files[:5]:  # Show first 5 files
                print(f"  - {file.get('name', file)}")
        else:
            print(f"List error: {response.text}")
    except Exception as e:
        print(f"File list error: {e}")

if __name__ == "__main__":
    # Load environment variables from .env file
    from pathlib import Path
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    test_supabase_storage_api()
