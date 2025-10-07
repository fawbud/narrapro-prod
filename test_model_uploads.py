#!/usr/bin/env python
"""
Test script to verify that Supabase storage works with your models.
"""
import os
import sys
import django
from pathlib import Path
from io import BytesIO
from PIL import Image

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from event.models import EventProfile
from narasumber.models import NarasumberProfile, ExpertiseCategory

User = get_user_model()

def create_test_image(filename="test.jpg", size=(200, 200)):
    """Create a test image file."""
    # Create a simple test image
    img = Image.new('RGB', size, color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return SimpleUploadedFile(
        filename,
        img_io.getvalue(),
        content_type='image/jpeg'
    )

def test_event_cover_upload():
    """Test event cover image upload."""
    print('\n=== Testing Event Cover Upload ===')
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_event_user',
            defaults={
                'email': 'test_event@example.com',
                'first_name': 'Test',
                'last_name': 'Event'
            }
        )
        
        # Delete existing event profile if any
        EventProfile.objects.filter(user=user).delete()
        
        # Create test image
        test_image = create_test_image('event_cover_test.jpg')
        
        # Create event profile with cover image
        event_profile = EventProfile.objects.create(
            user=user,
            name='Test Event',
            description='Test event description',
            event_type='online',
            location='zoom',
            email='test@example.com',
            cover_image=test_image
        )
        
        print(f'✅ Event profile created: {event_profile.name}')
        print(f'✅ Cover image path: {event_profile.cover_image.name}')
        print(f'✅ Cover image URL: {event_profile.cover_image.url}')
        
        # Verify file exists
        if event_profile.cover_image.storage.exists(event_profile.cover_image.name):
            print('✅ Cover image exists in storage')
        else:
            print('❌ Cover image not found in storage')
            return False
        
        # Clean up
        event_profile.cover_image.delete()
        event_profile.delete()
        if created:
            user.delete()
        
        print('✅ Test cleanup completed')
        return True
        
    except Exception as e:
        print(f'❌ Event cover upload test failed: {str(e)}')
        return False

def test_narasumber_profile_upload():
    """Test narasumber profile picture upload."""
    print('\n=== Testing Narasumber Profile Upload ===')
    
    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='test_narasumber_user',
            defaults={
                'email': 'test_narasumber@example.com',
                'first_name': 'Test',
                'last_name': 'Narasumber'
            }
        )
        
        # Delete existing narasumber profile if any
        NarasumberProfile.objects.filter(user=user).delete()
        
        # Get or create expertise category
        expertise, _ = ExpertiseCategory.objects.get_or_create(
            name='Test Expertise',
            defaults={'description': 'Test expertise category'}
        )
        
        # Create test image
        test_image = create_test_image('narasumber_profile_test.jpg')
        
        # Create narasumber profile with profile picture
        narasumber_profile = NarasumberProfile.objects.create(
            user=user,
            full_name='Test Narasumber',
            bio='Test bio',
            expertise_area=expertise,
            experience_level='INTERMEDIATE',
            years_of_experience=5,
            email='test@example.com',
            location='dki_jakarta',
            profile_picture=test_image
        )
        
        print(f'✅ Narasumber profile created: {narasumber_profile.full_name}')
        print(f'✅ Profile picture path: {narasumber_profile.profile_picture.name}')
        print(f'✅ Profile picture URL: {narasumber_profile.profile_picture.url}')
        
        # Verify file exists
        if narasumber_profile.profile_picture.storage.exists(narasumber_profile.profile_picture.name):
            print('✅ Profile picture exists in storage')
        else:
            print('❌ Profile picture not found in storage')
            return False
        
        # Clean up
        narasumber_profile.profile_picture.delete()
        narasumber_profile.delete()
        if created:
            user.delete()
        
        print('✅ Test cleanup completed')
        return True
        
    except Exception as e:
        print(f'❌ Narasumber profile upload test failed: {str(e)}')
        return False

if __name__ == '__main__':
    print('=== Supabase Storage Model Upload Test ===')
    
    # Test both upload types
    event_success = test_event_cover_upload()
    narasumber_success = test_narasumber_profile_upload()
    
    print('\n=== Final Results ===')
    if event_success and narasumber_success:
        print('🎉 All upload tests passed! Supabase storage is working correctly.')
        print('   ✅ Event cover uploads: Working')
        print('   ✅ Narasumber profile uploads: Working')
    else:
        print('❌ Some upload tests failed:')
        print(f'   Event covers: {"✅ Working" if event_success else "❌ Failed"}')
        print(f'   Narasumber profiles: {"✅ Working" if narasumber_success else "❌ Failed"}')
