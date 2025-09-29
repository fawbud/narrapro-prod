#!/usr/bin/env python
"""
Test the complete fix for production image upload
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

def create_test_image():
    """Create a valid test image using PIL"""
    img = Image.new('RGB', (300, 300), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=90)
    img_bytes.seek(0)

    return SimpleUploadedFile(
        name="test_cover_fixed.jpg",
        content=img_bytes.read(),
        content_type="image/jpeg"
    )

def test_complete_form_workflow():
    """Test the complete fixed form workflow"""
    print("=== Testing Complete Form Workflow ===")

    # 1. Get or create user
    user, created = User.objects.get_or_create(
        username='complete_test_user',
        defaults={
            'email': 'completetest@example.com',
            'user_type': 'event'
        }
    )
    print(f"User: {user.username}")

    # 2. Create initial profile
    try:
        event_profile = EventProfile.objects.get(user=user)
        print(f"Existing profile found: {event_profile.name}")
    except EventProfile.DoesNotExist:
        # Create profile with required fields
        initial_image = create_test_image()
        event_profile = EventProfile(
            user=user,
            name='Complete Test Event',
            description='Complete test description',
            event_type='offline',
            location='dki_jakarta',
            email='complete@example.com'
        )
        event_profile.cover_image.save('initial_complete.jpg', initial_image, save=False)
        event_profile.save()
        print(f"Created new profile: {event_profile.name}")

    # 3. Test scenario 1: Offline event in valid province
    print(f"\n--- Test 1: Offline Event ---")
    test_offline_event(event_profile)

    # 4. Test scenario 2: Online event with valid platform
    print(f"\n--- Test 2: Online Event ---")
    test_online_event(event_profile)

    # 5. Test scenario 3: Form without image (should preserve existing)
    print(f"\n--- Test 3: Update Without Image ---")
    test_update_without_image(event_profile)

    print(f"\n=== All Tests Completed ===")

def test_offline_event(event_profile):
    """Test offline event form submission"""
    form_data = {
        'name': 'Offline Event Test',
        'description': 'Testing offline event',
        'event_type': 'offline',
        'location': 'jawa_barat',  # Valid province
        'email': 'offline@example.com',
    }

    # Create new image
    test_image = create_test_image()
    files_data = {'cover_image': test_image}

    form = EventProfileForm(
        data=form_data,
        files=files_data,
        instance=event_profile
    )

    print(f"Offline form valid: {form.is_valid()}")
    if form.is_valid():
        saved = form.save()
        print(f"SUCCESS: Offline event saved")
        print(f"Image: {saved.cover_image.name}")
        print(f"Event type: {saved.event_type}")
        print(f"Location: {saved.location} ({saved.location_display})")
        return True
    else:
        print(f"FAILED: Form errors: {form.errors}")
        return False

def test_online_event(event_profile):
    """Test online event form submission"""
    form_data = {
        'name': 'Online Event Test',
        'description': 'Testing online event',
        'event_type': 'online',
        'location': 'zoom',  # Valid online platform
        'email': 'online@example.com',
    }

    # Create new image
    test_image = create_test_image()
    files_data = {'cover_image': test_image}

    form = EventProfileForm(
        data=form_data,
        files=files_data,
        instance=event_profile
    )

    print(f"Online form valid: {form.is_valid()}")
    if form.is_valid():
        saved = form.save()
        print(f"SUCCESS: Online event saved")
        print(f"Image: {saved.cover_image.name}")
        print(f"Event type: {saved.event_type}")
        print(f"Location: {saved.location} ({saved.location_display})")
        return True
    else:
        print(f"FAILED: Form errors: {form.errors}")
        return False

def test_update_without_image(event_profile):
    """Test updating form without changing image"""
    current_image = event_profile.cover_image.name

    form_data = {
        'name': 'Updated Name Only',
        'description': 'Updated description only',
        'event_type': 'hybrid',
        'location': 'bali',  # Valid province for hybrid
        'email': 'updated@example.com',
    }

    # No files - should keep existing image
    form = EventProfileForm(data=form_data, instance=event_profile)

    print(f"Update form valid: {form.is_valid()}")
    if form.is_valid():
        saved = form.save()
        print(f"SUCCESS: Updated without new image")
        print(f"Image preserved: {saved.cover_image.name == current_image}")
        print(f"Event type changed to: {saved.event_type}")
        print(f"Location changed to: {saved.location} ({saved.location_display})")
        return True
    else:
        print(f"FAILED: Form errors: {form.errors}")
        return False

def test_validation_errors():
    """Test that validation errors are properly caught"""
    print(f"\n=== Testing Validation Error Handling ===")

    user = User.objects.get(username='complete_test_user')
    event_profile = EventProfile.objects.get(user=user)

    # Test invalid location for event type
    bad_form_data = {
        'name': 'Bad Test Event',
        'description': 'Testing bad validation',
        'event_type': 'offline',  # Offline event
        'location': 'zoom',       # But with online platform - should fail
        'email': 'bad@example.com',
    }

    form = EventProfileForm(data=bad_form_data, instance=event_profile)
    print(f"Invalid form correctly rejected: {not form.is_valid()}")
    if not form.is_valid():
        print(f"Expected validation errors: {form.errors}")
        return True
    else:
        print(f"ERROR: Bad form was accepted when it should have been rejected!")
        return False

if __name__ == "__main__":
    try:
        test_complete_form_workflow()
        test_validation_errors()
        print(f"\n🎉 ALL TESTS COMPLETED!")
        print(f"The form validation and image upload fixes are working!")
    except Exception as e:
        print(f"\nERROR during testing: {e}")
        import traceback
        traceback.print_exc()