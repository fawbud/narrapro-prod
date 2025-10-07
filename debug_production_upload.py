#!/usr/bin/env python
"""
Debug production image upload flow
"""
import os
import sys
import django
from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django with production settings
os.environ['PRODUCTION'] = 'true'
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

from django.contrib.auth import get_user_model
from event.models import EventProfile
from profiles.forms import EventProfileForm
from django.test import RequestFactory
from django.core.files.storage import default_storage

User = get_user_model()

def create_test_image():
    """Create a small test image"""
    # Create a minimal PNG image (1x1 pixel)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'

    return SimpleUploadedFile(
        name="test_cover.png",
        content=png_data,
        content_type="image/png"
    )

def debug_form_submission():
    """Debug what happens during form submission"""
    print("=== Production Upload Debug ===")

    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_event_user',
        defaults={
            'email': 'test@example.com',
            'user_type': 'event'
        }
    )
    print(f"Test user: {user.username} (created: {created})")

    # Get or create EventProfile
    event_profile, created = EventProfile.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Test Event',
            'description': 'Test Description',
            'location': 'Test Location',
            'email': 'test@example.com'
        }
    )
    print(f"Event profile exists: {not created}")
    print(f"Profile has cover_image: {bool(event_profile.cover_image)}")
    if event_profile.cover_image:
        print(f"Current image: {event_profile.cover_image.name}")

    # Test 1: Form with no image (should be optional for existing)
    print(f"\n=== Test 1: Form without image ===")
    form_data = {
        'name': 'Updated Event Name',
        'description': 'Updated description',
        'location': 'Updated Location',
        'email': 'updated@example.com',
        'event_type': 'offline'
    }

    form = EventProfileForm(data=form_data, instance=event_profile)
    print(f"Form valid (no image): {form.is_valid()}")
    if not form.is_valid():
        print(f"Form errors: {form.errors}")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")

    # Test 2: Form with image
    print(f"\n=== Test 2: Form with image ===")
    test_image = create_test_image()
    files_data = {'cover_image': test_image}

    form_with_image = EventProfileForm(
        data=form_data,
        files=files_data,
        instance=event_profile
    )
    print(f"Form valid (with image): {form_with_image.is_valid()}")
    if not form_with_image.is_valid():
        print(f"Form errors: {form_with_image.errors}")
        for field, errors in form_with_image.errors.items():
            print(f"  {field}: {errors}")

    # Test 3: Try to save the form
    if form_with_image.is_valid():
        print(f"\n=== Test 3: Saving form ===")
        try:
            # Check storage before save
            print(f"Storage backend: {default_storage.__class__.__name__}")

            saved_instance = form_with_image.save(commit=False)
            print(f"Form save() complete, commit=False")
            print(f"Instance cover_image: {saved_instance.cover_image}")

            # Now save with commit=True
            saved_instance = form_with_image.save(commit=True)
            print(f"Form save() complete, commit=True")
            print(f"Saved cover_image: {saved_instance.cover_image.name if saved_instance.cover_image else 'None'}")

            if saved_instance.cover_image:
                print(f"Image URL: {saved_instance.cover_image.url}")
                print(f"File exists in storage: {saved_instance.cover_image.storage.exists(saved_instance.cover_image.name)}")

                # Check file size
                try:
                    size = saved_instance.cover_image.size
                    print(f"File size: {size} bytes")
                except Exception as e:
                    print(f"Error getting file size: {e}")

        except Exception as e:
            print(f"Error saving form: {e}")
            import traceback
            traceback.print_exc()

    # Test 4: Direct storage test
    print(f"\n=== Test 4: Direct storage test ===")
    try:
        test_image_2 = create_test_image()
        saved_path = default_storage.save('debug/direct_test.png', test_image_2)
        print(f"Direct storage save successful: {saved_path}")
        print(f"File URL: {default_storage.url(saved_path)}")

        # Clean up
        default_storage.delete(saved_path)
        print("Direct storage file cleaned up")

    except Exception as e:
        print(f"Direct storage test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_form_submission()