#!/usr/bin/env python
"""
Test script to verify the public event profile template works correctly.
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

User = get_user_model()

def test_event_public_profile():
    """Test public event profile page"""
    
    client = Client()
    
    print("🧪 Testing Event Public Profile Template...")
    
    # Find an event user
    event_users = User.objects.filter(user_type='event', is_approved=True)
    
    if not event_users.exists():
        print("❌ No approved event users found in database")
        return
    
    event_user = event_users.first()
    print(f"✅ Found event user: {event_user.username}")
    
    # Check if event profile exists
    try:
        event_profile = event_user.event_profile
        print(f"✅ Event profile exists: {event_profile.name}")
    except:
        print("❌ Event profile not found")
        return
    
    # Test public profile access (anonymous user)
    url = f"/profiles/{event_user.username}/"
    print(f"🌐 Testing URL: {url}")
    
    response = client.get(url)
    print(f"📊 Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Public event profile accessible!")
        
        # Check template used
        template_names = [t.name for t in response.templates]
        print(f"📄 Templates used: {template_names}")
        
        if 'profiles/event_public_profile.html' in template_names:
            print("✅ Correct template used: event_public_profile.html")
        else:
            print("❌ Wrong template used")
            
        # Check context data
        context = response.context
        if context.get('event_profile'):
            event_profile = context['event_profile']
            print(f"✅ Event profile in context: {event_profile.name}")
            
            # Test key features
            if hasattr(event_profile, 'email'):
                print(f"✅ Email field exists: {event_profile.email}")
            else:
                print("❌ Email field missing")
                
            if hasattr(event_profile, 'get_public_phone'):
                phone = event_profile.get_public_phone()
                print(f"✅ Phone privacy method works: {phone}")
            else:
                print("❌ get_public_phone method missing")
        else:
            print("❌ Event profile not in context")
    else:
        print(f"❌ Profile page not accessible: {response.status_code}")
        if response.status_code == 302:
            print(f"🔄 Redirected to: {response.url}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_event_public_profile()
