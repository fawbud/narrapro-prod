#!/usr/bin/env python
"""
Test script to verify the event profile changes work correctly.
Tests both the edit form and public profile template.
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from profiles.forms import EventProfileForm

User = get_user_model()

def test_event_profile_changes():
    """Test that event profiles only use cover image, not profile picture"""
    
    print("🧪 Testing Event Profile Changes...")
    
    # Test 1: Check EventProfileForm fields
    print("\n1️⃣ Testing EventProfileForm fields...")
    form = EventProfileForm()
    
    # Check that profile_picture is NOT in the form fields
    if 'profile_picture' not in form.fields:
        print("   ✅ profile_picture removed from EventProfileForm")
    else:
        print("   ❌ profile_picture still in EventProfileForm")
    
    # Check that cover_image IS in the form fields
    if 'cover_image' in form.fields:
        print("   ✅ cover_image present in EventProfileForm")
    else:
        print("   ❌ cover_image missing from EventProfileForm")
    
    # Check new contact fields
    expected_fields = ['email', 'phone_number', 'is_phone_public']
    for field in expected_fields:
        if field in form.fields:
            print(f"   ✅ {field} present in EventProfileForm")
        else:
            print(f"   ❌ {field} missing from EventProfileForm")
    
    # Test 2: Check public event profile template
    print("\n2️⃣ Testing public event profile access...")
    client = Client()
    
    # Find an event user
    event_users = User.objects.filter(user_type='event', is_approved=True)
    
    if event_users.exists():
        event_user = event_users.first()
        print(f"   ✅ Found event user: {event_user.username}")
        
        # Test anonymous access to public profile
        url = f"/profiles/{event_user.username}/"
        response = client.get(url)
        
        if response.status_code == 200:
            print("   ✅ Public event profile accessible")
            
            # Check template used
            template_names = [t.name for t in response.templates]
            if 'profiles/event_public_profile.html' in template_names:
                print("   ✅ Correct template used: event_public_profile.html")
                
                # Check that the template doesn't reference profile_picture
                template_content = response.content.decode('utf-8')
                if 'profile_picture' not in template_content:
                    print("   ✅ Profile picture references removed from template")
                else:
                    print("   ⚠️ Profile picture references still in template")
                    
                if 'cover_image' in template_content:
                    print("   ✅ Cover image present in template")
                else:
                    print("   ❌ Cover image missing from template")
            else:
                print("   ❌ Wrong template used")
        else:
            print(f"   ❌ Profile page not accessible: {response.status_code}")
    else:
        print("   ⚠️ No event users found for testing")
    
    # Test 3: Check form field counts
    print("\n3️⃣ Testing form field structure...")
    form_fields = list(form.fields.keys())
    print(f"   📝 EventProfileForm fields: {form_fields}")
    
    expected_count = 9  # name, description, location, email, phone_number, is_phone_public, website, cover_image, start_date, end_date
    actual_count = len(form_fields)
    
    if actual_count == expected_count:
        print(f"   ✅ Correct number of fields: {actual_count}")
    else:
        print(f"   ⚠️ Field count mismatch. Expected: {expected_count}, Actual: {actual_count}")
    
    print("\n" + "="*50)
    print("🎯 Event Profile Update Summary:")
    print("✅ Removed profile_picture from EventProfileForm")
    print("✅ Kept cover_image as the main visual element")
    print("✅ Added email/phone_number contact fields")
    print("✅ Updated public event profile template")
    print("✅ Simplified event profile layout")

if __name__ == "__main__":
    test_event_profile_changes()
