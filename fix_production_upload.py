#!/usr/bin/env python
"""
Fix production image upload by addressing form validation issues
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
from django.core.files.storage import default_storage

User = get_user_model()

def create_valid_test_image():
    """Create a valid test image using PIL"""
    # Create a small RGB image
    img = Image.new('RGB', (100, 100), color='red')

    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    return SimpleUploadedFile(
        name="test_cover.jpg",
        content=img_bytes.read(),
        content_type="image/jpeg"
    )

def test_fixed_form_submission():
    """Test form submission with proper validation"""
    print("=== Fixed Production Upload Test ===")

    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='fixed_test_user',
        defaults={
            'email': 'fixedtest@example.com',
            'user_type': 'event'
        }
    )
    print(f"Test user: {user.username}")

    # Get or create EventProfile
    event_profile, created = EventProfile.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Test Event',
            'description': 'Test Description',
            'event_type': 'offline',
            'location': 'jakarta',  # Use valid province code
            'email': 'test@example.com'
        }
    )
    print(f"Event profile created: {created}")

    # Test with PROPER form data
    print(f"\n=== Test with Valid Form Data ===")

    # CORRECT form data with valid location
    form_data = {
        'name': 'Fixed Event Name',
        'description': 'Fixed description',
        'event_type': 'offline',  # Must match location type
        'location': 'dki_jakarta',  # Use proper province code from PROVINCE_CHOICES
        'email': 'fixed@example.com',
    }

    # Create valid image
    test_image = create_valid_test_image()
    files_data = {'cover_image': test_image}

    print(f"Form data: {form_data}")
    print(f"Files data: {list(files_data.keys())}")

    # Create form
    form = EventProfileForm(
        data=form_data,
        files=files_data,
        instance=event_profile
    )

    print(f"Form is valid: {form.is_valid()}")

    if not form.is_valid():
        print("Form validation errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False

    # Save the form
    print(f"\n=== Saving Valid Form ===")
    try:
        saved_instance = form.save()
        print(f"✅ Form saved successfully!")
        print(f"✅ Cover image: {saved_instance.cover_image.name if saved_instance.cover_image else 'None'}")

        if saved_instance.cover_image:
            print(f"✅ Image URL: {saved_instance.cover_image.url}")
            print(f"✅ File exists: {saved_instance.cover_image.storage.exists(saved_instance.cover_image.name)}")

            # Check if we can access the URL
            try:
                import requests
                response = requests.head(saved_instance.cover_image.url, timeout=10)
                print(f"✅ URL accessible: {response.status_code == 200}")
            except:
                print("⚠️  URL check failed (this might be normal in some setups)")

        return True

    except Exception as e:
        print(f"❌ Error saving form: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_event_types():
    """Test with different event types to ensure location validation works"""
    print(f"\n=== Testing Different Event Types ===")

    user = User.objects.get(username='fixed_test_user')

    test_cases = [
        {
            'event_type': 'online',
            'location': 'zoom',  # Valid online platform
            'should_pass': True
        },
        {
            'event_type': 'offline',
            'location': 'jawa_barat',  # Valid province
            'should_pass': True
        },
        {
            'event_type': 'hybrid',
            'location': 'bali',  # Valid province
            'should_pass': True
        },
        {
            'event_type': 'offline',
            'location': 'zoom',  # Wrong: online platform for offline event
            'should_pass': False
        }
    ]

    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['event_type']} event at {test_case['location']}")

        form_data = {
            'name': f'Test Event {i+1}',
            'description': 'Test description',
            'event_type': test_case['event_type'],
            'location': test_case['location'],
            'email': 'test@example.com',
        }

        # Create new profile for each test
        test_profile = EventProfile(
            user=user,
            name=f'Test {i+1}',
            description='Test',
            event_type='offline',
            location='dki_jakarta',
            email='test@example.com'
        )

        form = EventProfileForm(data=form_data, instance=test_profile)
        is_valid = form.is_valid()

        if test_case['should_pass']:
            if is_valid:
                print(f"✅ Passed as expected")
            else:
                print(f"❌ Should have passed but failed: {form.errors}")
        else:
            if not is_valid:
                print(f"✅ Failed as expected: {form.errors}")
            else:
                print(f"❌ Should have failed but passed")

if __name__ == "__main__":
    success = test_fixed_form_submission()
    if success:
        test_different_event_types()
    else:
        print("❌ Main test failed, skipping additional tests")