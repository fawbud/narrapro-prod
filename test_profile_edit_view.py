#!/usr/bin/env python
"""
Debug script to test the actual profile edit functionality.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
from event.models import EventProfile
from narasumber.models import NarasumberProfile, ExpertiseCategory

User = get_user_model()
client = Client()

def create_test_image(name="test.jpg"):
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(name, img_io.getvalue(), content_type='image/jpeg')

def test_event_profile_edit():
    """Test editing event profile via the actual view."""
    print('=== Testing Event Profile Edit View ===')
    
    try:
        # Clean up
        EventProfile.objects.filter(user__username='view_test_event').delete()
        User.objects.filter(username='view_test_event').delete()
        
        # Create user
        user = User.objects.create_user(
            username='view_test_event',
            email='viewtest@example.com',
            password='testpass123',
            user_type='event'
        )
        
        # Create initial profile with image
        initial_image = create_test_image('initial.jpg')
        profile = EventProfile.objects.create(
            user=user,
            name='Initial Event',
            description='Initial description',
            event_type='online',
            location='zoom',
            email='initial@test.com',
            cover_image=initial_image
        )
        
        print(f'✅ Created profile with image: {profile.cover_image.name}')
        
        # Login user
        client.login(username='view_test_event', password='testpass123')
        
        # Test 1: Edit without new image (should preserve existing)
        response = client.post(f'/profiles/{user.username}/edit/', {
            'name': 'Updated Event Name',
            'description': 'Updated description',
            'event_type': 'offline',
            'location': 'dki_jakarta',
            'email': 'updated@test.com',
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'username': user.username,
        })
        
        print(f'Response status: {response.status_code}')
        
        if response.status_code == 302:  # Redirect on success
            print('✅ Form submitted successfully')
            profile.refresh_from_db()
            print(f'✅ Profile updated: {profile.name}')
            print(f'✅ Image preserved: {profile.cover_image.name}')
        else:
            print('❌ Form submission failed')
            print(f'Response content: {response.content.decode()[:500]}...')
        
        # Test 2: Edit with new image
        new_image = create_test_image('new.jpg')
        response = client.post(f'/profiles/{user.username}/edit/', {
            'name': 'Event with New Image',
            'description': 'New image description',
            'event_type': 'hybrid',
            'location': 'dki_jakarta',
            'email': 'newimage@test.com',
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'username': user.username,
            'cover_image': new_image
        })
        
        print(f'New image response status: {response.status_code}')
        
        if response.status_code == 302:
            print('✅ Form with new image submitted successfully')
            profile.refresh_from_db()
            print(f'✅ New image uploaded: {profile.cover_image.name}')
            print(f'✅ Image URL: {profile.cover_image.url}')
        else:
            print('❌ Form with new image submission failed')
        
        # Clean up
        if profile.cover_image:
            profile.cover_image.delete()
        profile.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f'❌ View test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('=== Profile Edit View Test ===')
    test_event_profile_edit()
