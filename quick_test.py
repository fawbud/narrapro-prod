#!/usr/bin/env python
"""
Quick test to see what exactly is happening with form validation.
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

# Quick test
print('Testing form validation...')

# Create minimal test data
try:
    user = User.objects.create(username='quicktest', email='quick@test.com', user_type='event')
    
    # Test form without instance (new profile)
    form_data = {
        'name': 'Test Event',
        'description': 'Test',
        'event_type': 'online',
        'location': 'zoom',
        'email': 'test@test.com'
    }
    
    form = EventProfileForm(data=form_data)
    print(f'New profile form valid: {form.is_valid()}')
    print(f'Required cover_image: {form.fields["cover_image"].required}')
    if not form.is_valid():
        print(f'Errors: {form.errors}')
    
    user.delete()
    print('✅ Quick test completed')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
