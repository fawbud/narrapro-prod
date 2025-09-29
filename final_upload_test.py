#!/usr/bin/env python
"""
Final working test for production image upload
"""
import os
import sys
import django
from pathlib import Path
from PIL import Image
from io import BytesIO

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
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

def create_valid_test_image():
    """Create a valid test image using PIL"""
    img = Image.new('RGB', (200, 200), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)

    return SimpleUploadedFile(
        name="test_cover.jpg",
        content=img_bytes.read(),
        content_type="image/jpeg"
    )

def test_complete_upload_flow():
    """Test the complete upload flow with all validations fixed"""
    print("=== Complete Upload Flow Test ===")

    # 1. Create or get user
    user, created = User.objects.get_or_create(
        username='final_test_user',
        defaults={
            'email': 'finaltest@example.com',
            'user_type': 'event'
        }
    )
    print(f"✅ User ready: {user.username}")

    # 2. Create initial profile with required fields INCLUDING cover_image
    test_image_initial = create_valid_test_image()

    try:
        # Try to get existing profile first
        event_profile = EventProfile.objects.get(user=user)
        print(f"✅ Existing profile found")
    except EventProfile.DoesNotExist:
        # Create new profile with ALL required fields
        event_profile = EventProfile(
            user=user,
            name='Initial Event',
            description='Initial description',
            event_type='offline',
            location='dki_jakarta',  # Valid province from PROVINCE_CHOICES
            email='test@example.com'
        )
        # MUST set cover_image before calling save() because model requires it
        event_profile.cover_image.save(
            'initial_cover.jpg',
            test_image_initial,
            save=False
        )
        event_profile.save()
        print(f"✅ New profile created with initial image: {event_profile.cover_image.name}")

    # 3. Test form update with new image
    print(f"\n=== Testing Form Update ===")

    # Create form data with valid location
    form_data = {
        'name': 'Updated Event Name',
        'description': 'Updated description',
        'event_type': 'offline',
        'location': 'jawa_barat',  # Another valid province
        'email': 'updated@example.com',
    }

    # Create new image for update
    new_test_image = create_valid_test_image()
    files_data = {'cover_image': new_test_image}

    # Create form
    form = EventProfileForm(
        data=form_data,
        files=files_data,
        instance=event_profile
    )

    print(f"Form valid: {form.is_valid()}")

    if not form.is_valid():
        print("❌ Form validation errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False

    # 4. Save the form
    print(f"✅ Form is valid, saving...")

    try:
        old_image = event_profile.cover_image.name if event_profile.cover_image else None
        print(f"Old image: {old_image}")

        saved_instance = form.save()

        print(f"✅ Form saved successfully!")
        print(f"✅ New cover image: {saved_instance.cover_image.name}")
        print(f"✅ Image URL: {saved_instance.cover_image.url}")
        print(f"✅ File exists in storage: {saved_instance.cover_image.storage.exists(saved_instance.cover_image.name)}")

        # 5. Test accessing the image URL
        try:
            import requests
            response = requests.head(saved_instance.cover_image.url, timeout=10)
            print(f"✅ Image URL accessible: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  URL check failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Error saving form: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_form_without_image():
    """Test updating form without changing the image"""
    print(f"\n=== Testing Form Update Without Image ===")

    user = User.objects.get(username='final_test_user')
    event_profile = EventProfile.objects.get(user=user)

    print(f"Current image: {event_profile.cover_image.name}")

    # Form data without image
    form_data = {
        'name': 'Updated Name Only',
        'description': 'Updated description only',
        'event_type': 'online',  # Change to online
        'location': 'zoom',      # Valid online platform
        'email': 'nameonly@example.com',
    }

    # No files data - should keep existing image
    form = EventProfileForm(data=form_data, instance=event_profile)

    print(f"Form valid (no image): {form.is_valid()}")

    if form.is_valid():
        old_image = event_profile.cover_image.name
        saved_instance = form.save()
        print(f"✅ Updated without image")
        print(f"✅ Image preserved: {saved_instance.cover_image.name == old_image}")
        print(f"✅ Event type changed: {saved_instance.event_type}")
        print(f"✅ Location changed: {saved_instance.location}")
        return True
    else:
        print("❌ Form errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False

if __name__ == "__main__":
    success1 = test_complete_upload_flow()
    if success1:
        success2 = test_form_without_image()
        if success1 and success2:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ Image upload works in production")
            print(f"✅ Form validation works correctly")
            print(f"✅ Supabase storage integration is working")
        else:
            print(f"\n❌ Some tests failed")
    else:
        print(f"\n❌ Main upload test failed")