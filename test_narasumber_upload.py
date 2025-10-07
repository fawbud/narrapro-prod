#!/usr/bin/env python
"""
Test Narasumber profile picture upload in production
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
from narasumber.models import NarasumberProfile, ExpertiseCategory
from profiles.forms import NarasumberProfileForm
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

def create_test_image():
    """Create a valid test image using PIL"""
    img = Image.new('RGB', (200, 200), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=90)
    img_bytes.seek(0)

    return SimpleUploadedFile(
        name="narasumber_profile.jpg",
        content=img_bytes.read(),
        content_type="image/jpeg"
    )

def test_narasumber_upload():
    """Test Narasumber profile picture upload"""
    print("=== Testing Narasumber Profile Picture Upload ===")

    # 1. Get or create user
    user, created = User.objects.get_or_create(
        username='narasumber_test_user',
        defaults={
            'email': 'narasumbertest@example.com',
            'user_type': 'narasumber'
        }
    )
    print(f"User: {user.username}")

    # 2. Get or create expertise category
    expertise, created = ExpertiseCategory.objects.get_or_create(
        name='Software Development',
        defaults={'description': 'Software development expertise'}
    )
    print(f"Expertise: {expertise.name}")

    # 3. Get or create narasumber profile
    try:
        narasumber_profile = NarasumberProfile.objects.get(user=user)
        print(f"Existing profile found: {narasumber_profile.full_name}")
    except NarasumberProfile.DoesNotExist:
        # Create profile with required fields
        narasumber_profile = NarasumberProfile(
            user=user,
            full_name='Test Narasumber',
            bio='Test biography',
            expertise_area=expertise,
            experience_level='INTERMEDIATE',
            years_of_experience=5,
            email='test@example.com',
            location='dki_jakarta'
        )
        narasumber_profile.save()
        print(f"Created new profile: {narasumber_profile.full_name}")

    # 4. Test form with profile picture
    print(f"\n=== Testing Form Submission ===")

    # Create valid form data
    form_data = {
        'full_name': 'Updated Test Narasumber',
        'bio': 'Updated test biography',
        'expertise_area': expertise.id,
        'experience_level': 'EXPERT',
        'years_of_experience': 7,
        'email': 'updated@example.com',
        'location': 'jawa_barat',  # Valid province
        'phone_number': '+621234567890',
        'is_phone_public': True,
        'portfolio_link': 'https://example.com/portfolio',
        'linkedin_url': 'https://linkedin.com/in/test'
    }

    # Create image file
    test_image = create_test_image()
    files_data = {'profile_picture': test_image}

    # Create form
    form = NarasumberProfileForm(
        data=form_data,
        files=files_data,
        instance=narasumber_profile
    )

    print(f"Form valid: {form.is_valid()}")

    if form.is_valid():
        print("Form passed validation, saving...")
        try:
            saved = form.save()
            print(f"SUCCESS: Narasumber profile saved!")
            print(f"Profile picture: {saved.profile_picture.name if saved.profile_picture else 'None'}")
            if saved.profile_picture:
                print(f"Image URL: {saved.profile_picture.url}")
                print(f"File exists: {saved.profile_picture.storage.exists(saved.profile_picture.name)}")
            return True
        except Exception as e:
            print(f"ERROR saving form: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("FORM VALIDATION FAILED:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False

def test_form_without_image():
    """Test updating form without changing image"""
    print(f"\n=== Testing Form Update Without Image ===")

    user = User.objects.get(username='narasumber_test_user')
    narasumber_profile = NarasumberProfile.objects.get(user=user)

    print(f"Current image: {narasumber_profile.profile_picture.name if narasumber_profile.profile_picture else 'None'}")

    # Form data without image
    expertise = ExpertiseCategory.objects.first()
    form_data = {
        'full_name': 'Name Only Update',
        'bio': 'Bio update only',
        'expertise_area': expertise.id,
        'experience_level': 'BEGINNER',
        'years_of_experience': 3,
        'email': 'nameonly@example.com',
        'location': 'bali'
    }

    # No files data - should keep existing image
    form = NarasumberProfileForm(data=form_data, instance=narasumber_profile)

    print(f"Form valid (no image): {form.is_valid()}")

    if form.is_valid():
        old_image = narasumber_profile.profile_picture.name if narasumber_profile.profile_picture else None
        saved = form.save()
        new_image = saved.profile_picture.name if saved.profile_picture else None
        print(f"SUCCESS: Updated without new image")
        print(f"Image preserved: {old_image == new_image}")
        print(f"Name changed: {saved.full_name}")
        return True
    else:
        print("Form errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False

if __name__ == "__main__":
    try:
        success1 = test_narasumber_upload()
        if success1:
            success2 = test_form_without_image()
            if success1 and success2:
                print(f"\nSUCCESS: All Narasumber tests passed!")
            else:
                print(f"\nSome Narasumber tests failed")
        else:
            print(f"\nNarasumber upload test failed")
    except Exception as e:
        print(f"\nERROR during testing: {e}")
        import traceback
        traceback.print_exc()