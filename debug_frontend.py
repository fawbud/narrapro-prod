#!/usr/bin/env python
"""
Debug script to check what happens during actual form processing.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from profiles.views import edit_profile
from io import BytesIO
from PIL import Image
from event.models import EventProfile
import traceback

User = get_user_model()

def create_test_image():
    img = Image.new('RGB', (100, 100), color='yellow')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile('test_upload.jpg', img_io.getvalue(), content_type='image/jpeg')

def debug_form_processing():
    """Debug the actual form processing in the view."""
    print('=== Debugging Form Processing ===')
    
    try:
        # Clean up any existing test data
        EventProfile.objects.filter(user__username='debug_user').delete()
        User.objects.filter(username='debug_user').delete()
        
        # Create test user
        user = User.objects.create_user(
            username='debug_user',
            email='debug@test.com',
            password='testpass',
            user_type='event'
        )
        
        # Create initial profile with image
        initial_image = create_test_image()
        profile = EventProfile.objects.create(
            user=user,
            name='Debug Event',
            description='Debug description',
            event_type='online',
            location='zoom',
            email='debug@test.com',
            cover_image=initial_image
        )
        
        print(f'✅ Created test profile with image: {profile.cover_image.name}')
        
        # Simulate a form submission
        request = HttpRequest()
        request.method = 'POST'
        request.user = user
        
        # Simulate form data (without new image first)
        request.POST = {
            'name': 'Updated Debug Event',
            'description': 'Updated description', 
            'event_type': 'offline',
            'location': 'dki_jakarta',
            'email': 'updated@test.com',
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'username': user.username,
        }
        
        request.FILES = {}  # No files initially
        
        print('\\n--- Testing form without new file ---')
        
        # Import the forms to test validation
        from profiles.forms import UserProfileForm, EventProfileForm
        
        user_form = UserProfileForm(request.POST, instance=user)
        event_form = EventProfileForm(request.POST, request.FILES, instance=profile)
        
        print(f'User form valid: {user_form.is_valid()}')
        if not user_form.is_valid():
            print(f'User form errors: {user_form.errors}')
            
        print(f'Event form valid: {event_form.is_valid()}')
        if not event_form.is_valid():
            print(f'Event form errors: {event_form.errors}')
            
        if user_form.is_valid() and event_form.is_valid():
            print('✅ Forms are valid, saving...')
            user_form.save()
            event_form.save()
            profile.refresh_from_db()
            print(f'✅ Profile updated: {profile.name}')
            print(f'✅ Image preserved: {bool(profile.cover_image)}')
        
        print('\\n--- Testing form with new file ---')
        
        # Now test with a new file
        new_image = create_test_image()
        request.FILES = {'cover_image': new_image}
        
        event_form_with_file = EventProfileForm(request.POST, request.FILES, instance=profile)
        
        print(f'Event form with file valid: {event_form_with_file.is_valid()}')
        if not event_form_with_file.is_valid():
            print(f'Event form with file errors: {event_form_with_file.errors}')
        else:
            print('✅ Form with file is valid')
            saved_profile = event_form_with_file.save()
            print(f'✅ New image uploaded: {saved_profile.cover_image.name}')
            print(f'✅ New image URL: {saved_profile.cover_image.url}')
        
        # Clean up
        if profile.cover_image:
            profile.cover_image.delete()
        profile.delete()
        user.delete()
        
    except Exception as e:
        print(f'❌ Error during debug: {e}')
        traceback.print_exc()

if __name__ == '__main__':
    debug_form_processing()
