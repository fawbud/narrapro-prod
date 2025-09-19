# Supabase Storage Configuration Guide

## Overview
This guide explains how to configure Supabase Storage for handling image uploads in the NarraPro application.

## Prerequisites
- Supabase project created
- `django-storages` and `boto3` packages installed (already in requirements.txt)
- Supabase Storage API enabled

## Setup Steps

### 1. Create Supabase Storage Bucket

1. Go to your Supabase Dashboard
2. Navigate to **Storage** section
3. Create a new bucket named `storage` (or your preferred name)
4. Set the bucket to **Public** for image serving

### 2. Get Supabase Credentials

1. In Supabase Dashboard, go to **Settings** → **API**
2. Copy your **Project URL** (e.g., `https://your-project.supabase.co`)
3. Go to **Settings** → **Database** → **Connection String**
4. For S3-compatible access, you'll need:
   - **Access Key ID**: Your Supabase service role key (anon or service_role)
   - **Secret Access Key**: Your Supabase service role secret

### 3. Configure Environment Variables

Update your `.env` file with the following variables:

```bash
# Set to true when deploying to production
PRODUCTION=false

# Supabase Storage Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ACCESS_KEY_ID=your_supabase_access_key_id
SUPABASE_SECRET_ACCESS_KEY=your_supabase_secret_access_key
SUPABASE_BUCKET_NAME=storage
```

### 4. Supabase Storage Policy Setup

Create the following RLS (Row Level Security) policies in Supabase:

#### Allow Public Read Access
```sql
CREATE POLICY "Public can view event covers" ON storage.objects
FOR SELECT TO public
USING (bucket_id = 'storage' AND (storage.foldername(name))[1] = 'event_covers');
```

#### Allow Authenticated Users to Upload
```sql
CREATE POLICY "Authenticated users can upload event covers" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'storage' AND (storage.foldername(name))[1] = 'event_covers');
```

#### Allow Users to Update Their Own Files
```sql
CREATE POLICY "Users can update their own event covers" ON storage.objects
FOR UPDATE TO authenticated
USING (bucket_id = 'storage' AND (storage.foldername(name))[1] = 'event_covers')
WITH CHECK (bucket_id = 'storage' AND (storage.foldername(name))[1] = 'event_covers');
```

#### Allow Users to Delete Their Own Files
```sql
CREATE POLICY "Users can delete their own event covers" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'storage' AND (storage.foldername(name))[1] = 'event_covers');
```

## File Organization

The system automatically organizes uploaded files with the following structure:
```
storage/
└── event_covers/
    ├── user_1/
    │   ├── abc123def456.jpg
    │   └── xyz789uvw012.png
    ├── user_2/
    │   └── pqr345stu678.jpg
    └── ...
```

## Configuration Details

### Storage Backend Features
- **Unique File Names**: Uses UUID to prevent conflicts
- **User Organization**: Files organized by user ID
- **Public Access**: Images are publicly accessible via URL
- **Cache Control**: Files cached for 24 hours (86400 seconds)
- **No Overwrite**: Prevents accidental file overwrites

### Development vs Production
- **Development**: Files stored locally in `media/` folder
- **Production**: Files stored in Supabase Storage when `PRODUCTION=true`

### File Access URLs
In production, uploaded images will be accessible via:
```
https://your-project.supabase.co/storage/v1/object/public/storage/event_covers/user_id/filename.jpg
```

## Testing the Configuration

### 1. Check Settings
```python
# In Django shell
from django.conf import settings
print("Storage backend:", getattr(settings, 'DEFAULT_FILE_STORAGE', 'default'))
print("Media URL:", settings.MEDIA_URL)
```

### 2. Test Upload
```python
# Create an event profile with cover image through admin
# Check if file appears in Supabase Storage
```

### 3. Verify URL Generation
```python
# In Django shell
from event.models import EventProfile
event = EventProfile.objects.first()
if event and event.cover_image:
    print("Image URL:", event.cover_image.url)
```

## Troubleshooting

### Common Issues

1. **403 Forbidden Error**
   - Check Supabase RLS policies
   - Verify bucket permissions
   - Ensure correct API keys

2. **Connection Refused**
   - Verify SUPABASE_URL is correct
   - Check internet connectivity
   - Confirm Supabase project is active

3. **Invalid Credentials**
   - Double-check access key and secret
   - Ensure service role has storage permissions
   - Verify bucket name matches

4. **Files Not Showing**
   - Check bucket is set to public
   - Verify RLS policies allow SELECT
   - Confirm URL format is correct

### Debug Commands
```bash
# Test connection
python manage.py shell -c "from storages.backends.s3boto3 import S3Boto3Storage; storage = S3Boto3Storage(); print('Storage configured successfully')"

# Check environment variables
python manage.py shell -c "import os; print('Supabase URL:', os.getenv('SUPABASE_URL'))"
```

## Security Considerations

1. **Environment Variables**: Never commit real credentials to version control
2. **RLS Policies**: Properly configure Supabase Row Level Security
3. **Bucket Permissions**: Use public buckets only for non-sensitive images
4. **File Types**: Consider adding file type validation
5. **File Size**: Set appropriate file size limits

## Performance Optimization

1. **Image Compression**: Consider adding image compression before upload
2. **CDN**: Supabase Storage includes CDN capabilities
3. **Caching**: Files are cached with appropriate headers
4. **Thumbnails**: Consider generating thumbnails for better performance

## Migration from Local Storage

If you have existing local files, you can migrate them using:

```python
# Custom management command to migrate files
from django.core.management.base import BaseCommand
from event.models import EventProfile

class Command(BaseCommand):
    def handle(self, *args, **options):
        for event in EventProfile.objects.all():
            if event.cover_image:
                # Re-save to trigger upload to Supabase
                event.save()
```

## Support

For additional help:
- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [Django Storages Documentation](https://django-storages.readthedocs.io/)
- [django-storages S3 Backend](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
