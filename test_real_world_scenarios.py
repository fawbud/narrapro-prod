#!/usr/bin/env python
"""
Test real-world scenarios that might cause image upload failures
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

# Load environment variables
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
from narasumber.models import NarasumberProfile, ExpertiseCategory
from profiles.forms import EventProfileForm, NarasumberProfileForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.cache import SessionStore

User = get_user_model()

def create_large_image():
    """Create a large image that might exceed limits"""
    img = Image.new('RGB', (2000, 2000), color='red')  # Large 4MP image
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)  # High quality = large file
    img_bytes.seek(0)

    print(f"Large image size: {len(img_bytes.getvalue())} bytes ({len(img_bytes.getvalue())/1024/1024:.1f}MB)")

    return SimpleUploadedFile(
        name="large_image.jpg",
        content=img_bytes.read(),
        content_type="image/jpeg"
    )

def create_small_image():
    """Create a small, optimized image"""
    img = Image.new('RGB', (300, 300), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=75)  # Moderate quality
    img_bytes.seek(0)

    print(f"Small image size: {len(img_bytes.getvalue())} bytes ({len(img_bytes.getvalue())/1024:.1f}KB)")

    return SimpleUploadedFile(
        name="small_image.jpg",
        content=img_bytes.read(),
        content_type="image/jpeg"
    )

def test_image_size_limits():
    """Test if large images cause upload failures"""
    print("=== Testing Image Size Limits ===")

    # Test with large image
    user, _ = User.objects.get_or_create(
        username='size_test_user',
        defaults={'email': 'sizetest@example.com', 'user_type': 'event'}
    )

    event_profile, _ = EventProfile.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Size Test Event',
            'description': 'Testing size limits',
            'event_type': 'offline',
            'location': 'dki_jakarta',
            'email': 'sizetest@example.com'
        }
    )

    # Test 1: Large image (should it fail?)
    print(f"\n--- Testing Large Image ---")
    large_image = create_large_image()

    form_data = {
        'name': 'Large Image Test',
        'description': 'Testing large image upload',
        'event_type': 'offline',
        'location': 'jawa_barat',
        'email': 'large@example.com',
    }

    form = EventProfileForm(
        data=form_data,
        files={'cover_image': large_image},
        instance=event_profile
    )

    print(f"Large image form valid: {form.is_valid()}")
    if form.is_valid():
        try:
            saved = form.save()
            print(f"SUCCESS: Large image uploaded - {saved.cover_image.name}")
        except Exception as e:
            print(f"ERROR saving large image: {e}")
    else:
        print(f"Large image form errors: {form.errors}")

    # Test 2: Small image (should work)
    print(f"\n--- Testing Small Image ---")
    small_image = create_small_image()

    form_small = EventProfileForm(
        data=form_data,
        files={'cover_image': small_image},
        instance=event_profile
    )

    print(f"Small image form valid: {form_small.is_valid()}")
    if form_small.is_valid():
        try:
            saved = form_small.save()
            print(f"SUCCESS: Small image uploaded - {saved.cover_image.name}")
        except Exception as e:
            print(f"ERROR saving small image: {e}")
    else:
        print(f"Small image form errors: {form_small.errors}")

def test_missing_required_fields():
    """Test what happens when required fields are missing"""
    print(f"\n=== Testing Missing Required Fields ===")

    user = User.objects.get(username='size_test_user')
    event_profile = EventProfile.objects.get(user=user)

    # Test with missing or empty fields that might be required
    incomplete_data = {
        'name': '',  # Empty name
        'description': 'Description here',
        'event_type': 'offline',
        'location': 'dki_jakarta',
        'email': '',  # Empty email
    }

    form = EventProfileForm(data=incomplete_data, instance=event_profile)
    print(f"Incomplete form valid: {form.is_valid()}")
    if not form.is_valid():
        print("Form errors for incomplete data:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")

def test_invalid_file_types():
    """Test uploading non-image files"""
    print(f"\n=== Testing Invalid File Types ===")

    user = User.objects.get(username='size_test_user')
    event_profile = EventProfile.objects.get(user=user)

    # Create a fake "image" that's actually text
    fake_image = SimpleUploadedFile(
        name="fake.jpg",
        content=b"This is not an image file, just text pretending to be an image",
        content_type="image/jpeg"  # Lie about content type
    )

    form_data = {
        'name': 'Fake Image Test',
        'description': 'Testing fake image',
        'event_type': 'offline',
        'location': 'dki_jakarta',
        'email': 'fake@example.com',
    }

    form = EventProfileForm(
        data=form_data,
        files={'cover_image': fake_image},
        instance=event_profile
    )

    print(f"Fake image form valid: {form.is_valid()}")
    if not form.is_valid():
        print("Expected errors for fake image:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")

def test_csrf_simulation():
    """Test if CSRF might be causing issues"""
    print(f"\n=== Testing CSRF Simulation ===")

    # Simulate a request without proper CSRF
    factory = RequestFactory()
    request = factory.post('/profiles/test/')

    # Add session and messages (normally done by middleware)
    request.session = SessionStore()
    messages = FallbackStorage(request)
    request._messages = messages

    print(f"CSRF simulation - this is just to check if forms work with request context")
    print(f"In real scenarios, missing CSRF tokens would cause form submission failures")

def test_narasumber_edge_cases():
    """Test narasumber upload edge cases"""
    print(f"\n=== Testing Narasumber Edge Cases ===")

    # Create narasumber user
    user, _ = User.objects.get_or_create(
        username='narasumber_edge_test',
        defaults={'email': 'narasumberedge@example.com', 'user_type': 'narasumber'}
    )

    expertise, _ = ExpertiseCategory.objects.get_or_create(
        name='Edge Test',
        defaults={'description': 'Edge testing'}
    )

    narasumber_profile, _ = NarasumberProfile.objects.get_or_create(
        user=user,
        defaults={
            'full_name': 'Edge Test Narasumber',
            'bio': 'Edge testing',
            'expertise_area': expertise,
            'experience_level': 'BEGINNER',
            'years_of_experience': 1,
            'email': 'edge@example.com',
            'location': 'dki_jakarta'
        }
    )

    # Test with missing required fields
    incomplete_narasumber_data = {
        'full_name': '',  # Empty name
        'bio': 'Some bio',
        'expertise_area': '',  # Missing expertise
        'experience_level': 'EXPERT',
        'email': 'incomplete@example.com',
        'location': 'jawa_barat'
    }

    form = NarasumberProfileForm(data=incomplete_narasumber_data, instance=narasumber_profile)
    print(f"Incomplete narasumber form valid: {form.is_valid()}")
    if not form.is_valid():
        print("Narasumber form errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")

if __name__ == "__main__":
    try:
        test_image_size_limits()
        test_missing_required_fields()
        test_invalid_file_types()
        test_csrf_simulation()
        test_narasumber_edge_cases()
        print(f"\n=== Edge Case Testing Complete ===")
    except Exception as e:
        print(f"\nERROR during edge case testing: {e}")
        import traceback
        traceback.print_exc()