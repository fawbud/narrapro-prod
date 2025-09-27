#!/usr/bin/env python
"""
Test script for narasumber profile picture upload functionality
"""
import os
import django
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from profiles.models import User
from narasumber.models import NarasumberProfile, ExpertiseCategory
from main.forms import NarasumberRegistrationForm


def create_test_image():
    """Create a simple test image for upload testing"""
    # Create a simple 100x100 red image
    image = Image.new('RGB', (100, 100), color='red')
    temp_file = BytesIO()
    image.save(temp_file, format='JPEG')
    temp_file.seek(0)
    
    return SimpleUploadedFile(
        name='test_profile.jpg',
        content=temp_file.read(),
        content_type='image/jpeg'
    )


def test_profile_picture_field_in_form():
    """Test that profile_picture field is included in NarasumberRegistrationForm"""
    print("Testing profile picture field in form...")
    
    form = NarasumberRegistrationForm()
    
    # Check if profile_picture field is in the form
    if 'profile_picture' in form.fields:
        print("✅ profile_picture field is present in NarasumberRegistrationForm")
        print(f"   Field type: {type(form.fields['profile_picture'])}")
        print(f"   Widget type: {type(form.fields['profile_picture'].widget)}")
    else:
        print("❌ profile_picture field is missing from NarasumberRegistrationForm")
        print(f"   Available fields: {list(form.fields.keys())}")


def test_form_with_profile_picture():
    """Test form validation with profile picture upload"""
    print("\nTesting form validation with profile picture...")
    
    # Create a test image
    test_image = create_test_image()
    
    # Create an expertise category
    category, created = ExpertiseCategory.objects.get_or_create(
        name="Test Technology",
        defaults={"description": "Test category"}
    )
    
    # Test form data
    form_data = {
        'bio': 'Test bio for profile picture upload',
        'expertise_area': category.id,
        'experience_level': 'INTERMEDIATE',
        'years_of_experience': 3,
        'email': 'test@example.com',
        'phone_number': '+62123456789',
        'is_phone_public': True,
        'location': 'dki_jakarta',
        'portfolio_link': 'https://example.com'
    }
    
    # Test form with files
    form = NarasumberRegistrationForm(data=form_data, files={'profile_picture': test_image})
    
    if form.is_valid():
        print("✅ Form validation passed with profile picture")
        # Don't save to avoid file system changes during test
        print("   Form would save successfully with profile picture")
    else:
        print("❌ Form validation failed")
        print(f"   Errors: {form.errors}")


def test_model_profile_picture_field():
    """Test that NarasumberProfile model has profile_picture field"""
    print("\nTesting NarasumberProfile model...")
    
    # Check if the model has the profile_picture field
    if hasattr(NarasumberProfile, 'profile_picture'):
        print("✅ NarasumberProfile model has profile_picture field")
        
        # Get field information
        field = NarasumberProfile._meta.get_field('profile_picture')
        print(f"   Field type: {type(field)}")
        print(f"   Upload to function: {field.upload_to}")
        print(f"   Blank allowed: {field.blank}")
        print(f"   Null allowed: {field.null}")
    else:
        print("❌ NarasumberProfile model missing profile_picture field")


if __name__ == '__main__':
    print("🔍 Testing Narasumber Profile Picture Upload Feature")
    print("=" * 60)
    
    test_model_profile_picture_field()
    test_profile_picture_field_in_form()
    test_form_with_profile_picture()
    
    print("\n" + "=" * 60)
    print("🎉 Testing completed!")
