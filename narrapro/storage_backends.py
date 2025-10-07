"""
Custom storage backend for Supabase Storage.
"""
import os
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from urllib.parse import urljoin


@deconstructible
class SupabaseStorage(Storage):
    """
    Custom storage backend for Supabase Storage using REST API.
    """
    
    def __init__(self, *args, **kwargs):
        # Get Supabase configuration from environment
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SECRET_ACCESS_KEY')  # Use service role key
        self.bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'storage')
        
        if not all([self.supabase_url, self.supabase_key, self.bucket_name]):
            raise ValueError("Missing Supabase configuration. Please check SUPABASE_URL, SUPABASE_SECRET_ACCESS_KEY, and SUPABASE_BUCKET_NAME environment variables.")
        
        # Ensure URL doesn't end with slash
        self.supabase_url = self.supabase_url.rstrip('/')
        
        # Build API URLs
        self.storage_api_url = f"{self.supabase_url}/storage/v1/object"
        self.public_url_base = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}"
        
        # Headers for API requests
        self.headers = {
            'Authorization': f'Bearer {self.supabase_key}',
            'apikey': self.supabase_key
        }
    
    def _save(self, name, content):
        """
        Save file to Supabase Storage.
        """
        # Normalize the file name
        cleaned_name = self._clean_name(name)
        
        # Prepare the upload URL - use public endpoint for uploads
        upload_url = f"{self.storage_api_url}/public/{self.bucket_name}/{cleaned_name}"
        
        # Read file content
        if hasattr(content, 'read'):
            file_content = content.read()
        else:
            file_content = content
        
        # Determine content type
        content_type = getattr(content, 'content_type', 'application/octet-stream')
        
        # Prepare headers for upload
        upload_headers = self.headers.copy()
        upload_headers['Content-Type'] = content_type
        upload_headers['Cache-Control'] = 'max-age=86400'
        
        # Upload file using PUT request (Supabase Storage API uses PUT, not POST)
        try:
            print(f"DEBUG: Uploading to {upload_url}")
            print(f"DEBUG: File size: {len(file_content)} bytes")
            print(f"DEBUG: Content type: {content_type}")
            
            response = requests.put(
                upload_url,
                data=file_content,
                headers=upload_headers,
                timeout=30
            )
            
            print(f"DEBUG: Upload response: {response.status_code}")
            print(f"DEBUG: Upload response text: {response.text}")
            
            if response.status_code in [200, 201]:
                return cleaned_name
            else:
                raise Exception(f"Upload failed: {response.status_code} - {response.text}")
                
        except requests.RequestException as e:
            raise Exception(f"Network error during upload: {str(e)}")
    
    def _open(self, name, mode='rb'):
        """
        Open and read file from Supabase Storage.
        """
        try:
            file_url = self.url(name)
            response = requests.get(file_url, timeout=30)
            
            if response.status_code == 200:
                return ContentFile(response.content)
            else:
                raise Exception(f"File not found: {response.status_code}")
                
        except requests.RequestException as e:
            raise Exception(f"Network error during file read: {str(e)}")
    
    def delete(self, name):
        """
        Delete file from Supabase Storage.
        """
        cleaned_name = self._clean_name(name)
        delete_url = f"{self.storage_api_url}/{self.bucket_name}/{cleaned_name}"
        
        try:
            response = requests.delete(delete_url, headers=self.headers, timeout=30)
            return response.status_code in [200, 204]
        except requests.RequestException:
            return False
    
    def exists(self, name):
        """
        Check if file exists in Supabase Storage.
        """
        try:
            file_url = self.url(name)
            response = requests.head(file_url, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def size(self, name):
        """
        Get file size from Supabase Storage.
        """
        try:
            file_url = self.url(name)
            response = requests.head(file_url, timeout=10)
            if response.status_code == 200:
                return int(response.headers.get('Content-Length', 0))
        except (requests.RequestException, ValueError):
            pass
        return 0
    
    def url(self, name):
        """
        Return the public URL for the file.
        """
        cleaned_name = self._clean_name(name)
        return f"{self.public_url_base}/{cleaned_name}"
    
    def _clean_name(self, name):
        """
        Clean and normalize file name for Supabase.
        """
        # Remove leading slashes and normalize
        return name.lstrip('/').replace('\\', '/')
    
    def get_available_name(self, name, max_length=None):
        """
        Return a filename that's free on the target storage system.
        For Supabase, we'll use the original name since our models use UUID.
        """
        return name


@deconstructible
class SupabasePublicStorage(SupabaseStorage):
    """
    Supabase storage for public files (images, documents).
    """
    pass


@deconstructible 
class SupabasePrivateStorage(SupabaseStorage):
    """
    Supabase storage for private files.
    """
    def url(self, name):
        """
        For private files, return a signed URL (if needed in future).
        For now, returns the same public URL.
        """
        return super().url(name)
