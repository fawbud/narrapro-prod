#!/usr/bin/env python
"""
Simple test to verify form fix.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from profiles.forms import EventProfileForm
from event.models import EventProfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User = get_user_model()

def create_test_image():
    img = Image.new('RGB', (100, 100), color='green')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile('test.jpg', img_io.getvalue(), content_type='image/jpeg')

print('=== Simple Form Test ===')

# Test with existing profile
try:
    # Clean up any existing test data
    EventProfile.objects.filter(user__username='simple_test').delete()
    User.objects.filter(username='simple_test').delete()
    
    # Create user and profile with image
    user = User.objects.create(username='simple_test', email='simple@test.com', user_type='event')
    
    # Create initial profile with cover image
    initial_image = create_test_image()
    profile = EventProfile.objects.create(
        user=user,
        name='Initial Event',
        description='Initial description',
        event_type='online',
        location='zoom',
        email='initial@test.com',
        cover_image=initial_image
    )
    
    print('✅ Profile created with initial image')
    print(f'Image path: {profile.cover_image.name}')
    
    # Test editing without new image
    form_data = {
        'name': 'Updated Event Name',
        'description': 'Updated description',
        'event_type': 'offline',
        'location': 'dki_jakarta',
        'email': 'updated@test.com'
    }
    
    form = EventProfileForm(data=form_data, instance=profile)
    
    print(f'Form valid without new image: {form.is_valid()}')
    if form.is_valid():
        updated_profile = form.save()
        print(f'✅ Form saved! Image preserved: {updated_profile.cover_image.name}')
    else:
        print(f'❌ Form errors: {form.errors}')
    
    # Clean up
    profile.cover_image.delete()
    profile.delete()
    user.delete()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
