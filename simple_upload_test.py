import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
sys.path.insert(0, os.getcwd())
django.setup()

import requests

# Test Supabase upload directly
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SECRET_ACCESS_KEY')
bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'storage')

print(f"URL: {supabase_url}")
print(f"Bucket: {bucket_name}")
print(f"Key length: {len(supabase_key) if supabase_key else 0}")

# Test content
test_content = b"Test upload content"
test_file = "test_uploads/simple_test.txt"

# Try POST method (current)
print("\nTesting POST method:")
url_post = f"{supabase_url}/storage/v1/object/{bucket_name}/{test_file}"
headers = {
    'Authorization': f'Bearer {supabase_key}',
    'apikey': supabase_key,
    'Content-Type': 'text/plain'
}

try:
    response = requests.post(url_post, data=test_content, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Try PUT method
print("\nTesting PUT method:")
try:
    response = requests.put(url_post, data=test_content, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
