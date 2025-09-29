"""
Simplified Supabase storage backend based on official documentation
"""
import os
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
import uuid


@deconstructible
class SimpleSupabaseStorage(Storage):
    """
    Simplified Supabase storage backend using the standard REST API
    """
    
    def __init__(self):
        print(f"SIMPLE DEBUG: SimpleSupabaseStorage.__init__() called")

        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'storage')

        print(f"SIMPLE DEBUG: SUPABASE_URL: {self.supabase_url}")
        print(f"SIMPLE DEBUG: SUPABASE_BUCKET_NAME: {self.bucket_name}")
        print(f"SIMPLE DEBUG: Service key length: {len(self.service_key) if self.service_key else 0}")

        if not self.supabase_url:
            print(f"SIMPLE DEBUG: ERROR - SUPABASE_URL is missing!")
            raise ValueError("SUPABASE_URL environment variable is required")

        if not self.service_key:
            print(f"SIMPLE DEBUG: ERROR - SUPABASE_SECRET_ACCESS_KEY is missing!")
            raise ValueError("SUPABASE_SECRET_ACCESS_KEY environment variable is required")

        self.supabase_url = self.supabase_url.rstrip('/')

        # Base URLs
        self.api_base = f"{self.supabase_url}/storage/v1"

        # Standard headers
        self.headers = {
            'Authorization': f'Bearer {self.service_key}',
            'apikey': self.service_key
        }

        print(f"SIMPLE DEBUG: SimpleSupabaseStorage initialized successfully")
        print(f"SIMPLE DEBUG: API base URL: {self.api_base}")
    
    def _save(self, name, content):
        """Upload file to Supabase"""
        print(f"SIMPLE DEBUG: _save() called with name={name}")
        print(f"SIMPLE DEBUG: Content type: {type(content)}")
        print(f"SIMPLE DEBUG: Storage backend: {self.__class__.__name__}")
        print(f"SIMPLE DEBUG: Supabase URL: {self.supabase_url}")
        print(f"SIMPLE DEBUG: Bucket: {self.bucket_name}")
        print(f"SIMPLE DEBUG: Service key present: {'Yes' if self.service_key else 'No'}")

        try:
            print(f"SIMPLE DEBUG: Starting upload for {name}")

            # Clean filename
            clean_name = name.replace('\\', '/').lstrip('/')
            print(f"SIMPLE DEBUG: Clean name: {clean_name}")

            # Read content
            if hasattr(content, 'read'):
                content.seek(0)
                file_data = content.read()
                content.seek(0)  # Reset for potential re-reads
            else:
                file_data = content

            print(f"SIMPLE DEBUG: File size: {len(file_data)} bytes")

            # Upload URL - try the most basic endpoint first
            upload_url = f"{self.api_base}/object/{self.bucket_name}/{clean_name}"

            # Upload headers
            upload_headers = self.headers.copy()
            upload_headers['Content-Type'] = getattr(content, 'content_type', 'application/octet-stream')

            print(f"SIMPLE DEBUG: Uploading to {upload_url}")
            print(f"SIMPLE DEBUG: Headers: {list(upload_headers.keys())}")

            # Try POST first (most common for file uploads)
            print(f"SIMPLE DEBUG: Attempting POST request...")
            response = requests.post(
                upload_url,
                data=file_data,
                headers=upload_headers,
                timeout=60
            )

            print(f"SIMPLE DEBUG: POST Response {response.status_code}: {response.text}")

            if response.status_code in [200, 201]:
                print(f"SIMPLE DEBUG: Upload successful via POST")
                return clean_name
            else:
                # If POST fails, try PUT
                print("SIMPLE DEBUG: POST failed, trying PUT...")
                response = requests.put(
                    upload_url,
                    data=file_data,
                    headers=upload_headers,
                    timeout=60
                )
                print(f"SIMPLE DEBUG: PUT Response {response.status_code}: {response.text}")

                if response.status_code in [200, 201]:
                    print(f"SIMPLE DEBUG: Upload successful via PUT")
                    return clean_name
                else:
                    print(f"SIMPLE DEBUG: Both POST and PUT failed")
                    raise Exception(f"Upload failed: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"SIMPLE DEBUG: Upload error: {e}")
            print(f"SIMPLE DEBUG: Exception type: {type(e)}")
            import traceback
            print(f"SIMPLE DEBUG: Traceback: {traceback.format_exc()}")
            raise
    
    def url(self, name):
        """Get public URL for file"""
        clean_name = name.replace('\\', '/').lstrip('/')
        return f"{self.api_base}/object/public/{self.bucket_name}/{clean_name}"
    
    def exists(self, name):
        """Check if file exists"""
        try:
            url = self.url(name)
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def delete(self, name):
        """Delete file"""
        try:
            clean_name = name.replace('\\', '/').lstrip('/')
            delete_url = f"{self.api_base}/object/{self.bucket_name}/{clean_name}"
            response = requests.delete(delete_url, headers=self.headers, timeout=30)
            return response.status_code in [200, 204]
        except:
            return False
    
    def size(self, name):
        """Get file size"""
        try:
            url = self.url(name)
            response = requests.head(url, timeout=10)
            return int(response.headers.get('Content-Length', 0))
        except:
            return 0
