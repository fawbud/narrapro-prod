"""
Custom storage backend for Supabase Storage.
"""
import os
from storages.backends.s3boto3 import S3Boto3Storage
from urllib.parse import urljoin


class SupabaseStorage(S3Boto3Storage):
    """
    Custom storage backend for Supabase Storage that properly handles URLs.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set Supabase-specific configurations
        self.access_key = os.getenv('SUPABASE_ACCESS_KEY_ID')
        self.secret_key = os.getenv('SUPABASE_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'storage')
        self.endpoint_url = os.getenv('SUPABASE_URL')
        self.region_name = 'us-east-1'  # Supabase default
        
        # Configure for public access
        self.default_acl = 'public-read'
        self.querystring_auth = False
        self.file_overwrite = False
        
        # Set custom domain for direct Supabase access
        if self.endpoint_url and self.bucket_name:
            self.custom_domain = f"{self.endpoint_url}/storage/v1/object/public/{self.bucket_name}"
    
    def url(self, name):
        """
        Return the URL for accessing the file.
        Uses Supabase's public URL format.
        """
        if self.custom_domain:
            return urljoin(self.custom_domain + '/', name)
        return super().url(name)
    
    def _normalize_name(self, name):
        """
        Normalize the file name to be compatible with Supabase.
        """
        # Remove any leading slashes and normalize path
        normalized = name.lstrip('/')
        return super()._normalize_name(normalized)
    
    def _save(self, name, content):
        """
        Save the file with proper Supabase configuration.
        """
        # Ensure the file has proper metadata
        if hasattr(content, 'content_type') and content.content_type:
            self.object_parameters = {
                'ContentType': content.content_type,
                'CacheControl': 'max-age=86400',
            }
        
        return super()._save(name, content)


class SupabasePublicStorage(SupabaseStorage):
    """
    Supabase storage for public files (images, documents).
    """
    location = 'public'
    default_acl = 'public-read'


class SupabasePrivateStorage(SupabaseStorage):
    """
    Supabase storage for private files.
    """
    location = 'private'
    default_acl = 'private'
    querystring_auth = True
