#!/usr/bin/env python
"""
Debug script to test file upload form processing.
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
from profiles.forms import NarasumberProfileForm, EventProfileForm
from narasumber.models import NarasumberProfile, ExpertiseCategory
from event.models import EventProfile

User = get_user_model()

def create_test_image(filename="test.jpg", size=(200, 200)):
    """Create a test image file."""
    img = Image.new('RGB', size, color='blue')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return SimpleUploadedFile(
        filename,
        img_io.getvalue(),
        content_type='image/jpeg'
    )

def test_narasumber_form_upload():
    """Test narasumber profile form with file upload."""
    print('=== Testing Narasumber Profile Form Upload ===')
    
    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='test_form_narasumber',
            defaults={
                'email': 'test_form_narasumber@example.com',
                'first_name': 'Test',
                'last_name': 'Form',
                'user_type': 'narasumber'
            }
        )
        
        # Get or create expertise category
        expertise, _ = ExpertiseCategory.objects.get_or_create(
            name='Test Form Expertise',
            defaults={'description': 'Test expertise for form testing'}
        )
        
        # Get or create narasumber profile
        narasumber_profile, profile_created = NarasumberProfile.objects.get_or_create(
            user=user,
            defaults={
                'full_name': 'Test Form Narasumber',
                'bio': 'Test bio',
                'expertise_area': expertise,
                'experience_level': 'INTERMEDIATE',
                'years_of_experience': 3,
                'email': 'test@example.com',
                'location': 'dki_jakarta'
            }
        )
        
        # Create test image
        test_image = create_test_image('form_test_narasumber.jpg')
        
        # Prepare form data
        form_data = {
            'full_name': 'Updated Test Narasumber',
            'bio': 'Updated bio with form test',
            'expertise_area': expertise.id,
            'experience_level': 'EXPERT',
            'years_of_experience': 5,
            'email': 'updated_test@example.com',
            'location': 'dki_jakarta'
        }
        
        file_data = {
            'profile_picture': test_image
        }
        
        # Test form validation
        form = NarasumberProfileForm(
            data=form_data,
            files=file_data,
            instance=narasumber_profile
        )
        
        if form.is_valid():
            print('✅ Form is valid')
            
            # Save the form
            saved_profile = form.save()
            print(f'✅ Form saved successfully')
            print(f'✅ Profile picture path: {saved_profile.profile_picture.name if saved_profile.profile_picture else "No file"}')
            
            if saved_profile.profile_picture:
                print(f'✅ Profile picture URL: {saved_profile.profile_picture.url}')
                print(f'✅ File exists in storage: {saved_profile.profile_picture.storage.exists(saved_profile.profile_picture.name)}')
                
                # Clean up the uploaded file
                saved_profile.profile_picture.delete()
                print('✅ Test file cleaned up')
            else:
                print('❌ No profile picture was saved')
                return False
        else:
            print('❌ Form is not valid')
            print(f'Form errors: {form.errors}')
            return False
        
        # Clean up test data
        if profile_created:
            narasumber_profile.delete()
        if created:
            user.delete()
        
        return True
        
    except Exception as e:
        print(f'❌ Narasumber form test failed: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

def test_event_form_upload():
    """Test event profile form with file upload."""
    print('\n=== Testing Event Profile Form Upload ===')
    
    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='test_form_event',
            defaults={
                'email': 'test_form_event@example.com',
                'first_name': 'Test',
                'last_name': 'Event',
                'user_type': 'event'
            }
        )
        
        # First, create an event profile WITH a cover image
        initial_image = create_test_image('initial_event.jpg')
        
        event_profile, profile_created = EventProfile.objects.get_or_create(
            user=user,
            defaults={
                'name': 'Test Form Event',
                'description': 'Test event description',
                'event_type': 'online',
                'location': 'zoom',
                'email': 'test@example.com',
                'cover_image': initial_image  # Provide initial image
            }
        )
        
        print(f'✅ Event profile created with cover image: {event_profile.cover_image.name if event_profile.cover_image else "None"}')
        
        # Now test updating the profile with a new image
        test_image = create_test_image('form_test_event.jpg')
        
        # Prepare form data
        form_data = {
            'name': 'Updated Test Event',
            'description': 'Updated event description with form test',
            'event_type': 'offline',
            'location': 'dki_jakarta',
            'email': 'updated_event@example.com'
        }
        
        file_data = {
            'cover_image': test_image
        }
        
        # Test form validation with existing instance
        form = EventProfileForm(
            data=form_data,
            files=file_data,
            instance=event_profile  # Use existing instance
        )
        
        if form.is_valid():
            print('✅ Form is valid')
            
            # Save the form
            saved_profile = form.save()
            print(f'✅ Form saved successfully')
            print(f'✅ Cover image path: {saved_profile.cover_image.name if saved_profile.cover_image else "No file"}')
            
            if saved_profile.cover_image:
                print(f'✅ Cover image URL: {saved_profile.cover_image.url}')
                print(f'✅ File exists in storage: {saved_profile.cover_image.storage.exists(saved_profile.cover_image.name)}')
                
                # Test form without new file (should keep existing)
                print('\n--- Testing form without new file (should keep existing) ---')
                form_data_no_file = {
                    'name': 'Updated Test Event No File',
                    'description': 'Updated without new file',
                    'event_type': 'online',
                    'location': 'zoom',
                    'email': 'updated_nofile@example.com'
                }
                
                form_no_file = EventProfileForm(
                    data=form_data_no_file,
                    instance=saved_profile
                )
                
                if form_no_file.is_valid():
                    print('✅ Form valid without new file')
                    saved_no_file = form_no_file.save()
                    print(f'✅ Cover image preserved: {saved_no_file.cover_image.name if saved_no_file.cover_image else "No file"}')
                else:
                    print('❌ Form invalid without new file')
                    print(f'Errors: {form_no_file.errors}')
                
                # Clean up the uploaded files
                saved_profile.cover_image.delete()
                print('✅ Test file cleaned up')
            else:
                print('❌ No cover image was saved')
                return False
        else:
            print('❌ Form is not valid')
            print(f'Form errors: {form.errors}')
            return False
        
        # Clean up test data
        if profile_created:
            event_profile.delete()
        if created:
            user.delete()
        
        return True
        
    except Exception as e:
        print(f'❌ Event form test failed: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

def test_form_validation_without_files():
    """Test what happens when forms are submitted without files."""
    print('\n=== Testing Form Behavior Without Files ===')
    
    try:
        # Test narasumber form without file
        expertise, _ = ExpertiseCategory.objects.get_or_create(
            name='Test No File Expertise',
            defaults={'description': 'Test expertise'}
        )
        
        form_data = {
            'full_name': 'Test No File',
            'bio': 'Test bio without file',
            'expertise_area': expertise.id,
            'experience_level': 'BEGINNER',
            'years_of_experience': 1,
            'email': 'nofile@example.com',
            'location': 'dki_jakarta'
        }
        
        # Test form without files
        form = NarasumberProfileForm(data=form_data)
        
        if form.is_valid():
            print('✅ Narasumber form valid without file')
        else:
            print('❌ Narasumber form invalid without file')
            print(f'Errors: {form.errors}')
        
        # Test event form without file
        event_form_data = {
            'name': 'Test Event No File',
            'description': 'Test event without file',
            'event_type': 'online',
            'location': 'zoom',
            'email': 'noeventfile@example.com'
        }
        
        event_form = EventProfileForm(data=event_form_data)
        
        if event_form.is_valid():
            print('✅ Event form valid without file')
        else:
            print('❌ Event form invalid without file')
            print(f'Errors: {event_form.errors}')
        
        return True
        
    except Exception as e:
        print(f'❌ Form validation test failed: {str(e)}')
        return False

if __name__ == '__main__':
    print('=== Form Upload Debug Test ===')
    
    # Test all scenarios
    narasumber_success = test_narasumber_form_upload()
    event_success = test_event_form_upload()
    validation_success = test_form_validation_without_files()
    
    print('\n=== Final Results ===')
    if narasumber_success and event_success and validation_success:
        print('🎉 All form tests passed!')
        print('   ✅ Narasumber profile form: Working')
        print('   ✅ Event profile form: Working')
        print('   ✅ Form validation: Working')
        print('\nForms are working correctly. The issue might be:')
        print('   1. Template form submission (missing enctype="multipart/form-data")')
        print('   2. JavaScript interfering with form submission')
        print('   3. View logic not processing files correctly')
        print('   4. User permissions or validation errors')
    else:
        print('❌ Some form tests failed:')
        print(f'   Narasumber forms: {"✅ Working" if narasumber_success else "❌ Failed"}')
        print(f'   Event forms: {"✅ Working" if event_success else "❌ Failed"}')
        print(f'   Form validation: {"✅ Working" if validation_success else "❌ Failed"}')
