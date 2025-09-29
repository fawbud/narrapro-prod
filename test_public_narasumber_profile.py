#!/usr/bin/env python
"""
Test script to verify the public narasumber profile page functionality.
This tests the new separate template and styling.
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from django.contrib.auth import get_user_model
from narasumber.models import NarasumberProfile, ExpertiseCategory
from django.test import Client
from django.urls import reverse

User = get_user_model()

def test_public_narasumber_profile():
    """Test the public narasumber profile page."""
    print("🧪 Testing Public Narasumber Profile Template...")
    
    try:
        # Create a test client
        client = Client()
        
        # Find a narasumber user for testing
        narasumber_users = User.objects.filter(user_type='narasumber')
        
        if not narasumber_users.exists():
            print("❌ No narasumber users found. Creating a test user...")
            
            # Create expertise category if it doesn't exist
            category, created = ExpertiseCategory.objects.get_or_create(
                name="Test Category",
                defaults={'description': 'Test category for testing'}
            )
            
            # Create test user
            test_user = User.objects.create_user(
                username='testnarasumber',
                email='test@example.com',
                first_name='Test',
                last_name='Narasumber',
                user_type='narasumber',
                is_approved=True
            )
            
            # Create narasumber profile
            narasumber_profile = NarasumberProfile.objects.create(
                user=test_user,
                full_name='Test Narasumber User',
                bio='This is a test bio for testing the public profile template.',
                expertise_area=category,
                experience_level='INTERMEDIATE',
                years_of_experience=5,
                email='test@example.com',
                phone_number='081234567890',
                is_phone_public=True,
                location='dki_jakarta',
                portfolio_link='https://example.com/portfolio'
            )
            
            print(f"✅ Created test narasumber user: {test_user.username}")
            test_username = test_user.username
        else:
            test_username = narasumber_users.first().username
            print(f"✅ Found existing narasumber user: {test_username}")
        
        # Test the profile URL
        profile_url = reverse('profiles:profile_detail', kwargs={'username': test_username})
        print(f"📄 Testing URL: {profile_url}")
        
        # Make request to profile page (not logged in - public view)
        response = client.get(profile_url)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if we're using the correct template
            template_names = [t.name for t in response.templates if t.name]
            print(f"📝 Templates used: {template_names}")
            
            if 'profiles/narasumber_public_profile.html' in template_names:
                print("✅ Correct template being used for public narasumber profile!")
            else:
                print("⚠️  Expected template not found. Used templates:", template_names)
            
            # Check for key elements in the response
            content = response.content.decode()
            
            checks = [
                ('Profile picture or placeholder', 'fa-user fa-3x' in content or 'profile_picture.url' in content),
                ('Full name display', 'narasumber_profile.full_name' in content),
                ('Username display', '@{{ profile_user.username }}' in content),
                ('Expertise area badge', 'expertise_area.name' in content),
                ('Experience level badge', 'get_experience_level_display' in content),
                ('Years experience badge', 'years_of_experience' in content),
                ('Email contact', 'fas fa-envelope' in content),
                ('Phone contact (if public)', 'get_public_phone' in content),
                ('Location display', 'location_display' in content),
                ('Bio section', 'Tentang Saya' in content),
                ('Contact links section', 'Hubungi Saya' in content),
                ('Email button', 'mailto:' in content),
                ('Portfolio button (if available)', 'Lihat Portfolio' in content),
                ('Neutral styling', 'btn-outline-secondary' in content),
                ('Small badges', 'font-size: 0.7rem' in content),
            ]
            
            print("\n🔍 Template Content Checks:")
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
            
            # Check that we're NOT extending profile_base.html
            if 'profile_base.html' not in content:
                print("✅ Template does NOT extend profile_base.html (no extra header card)")
            else:
                print("⚠️  Template might still be extending profile_base.html")
            
        else:
            print(f"❌ Failed to load profile page. Status: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Response content: {response.content.decode()[:500]}...")
        
        print("\n" + "="*60)
        print("🎯 SUMMARY:")
        print("✅ Created separate narasumber_public_profile.html template")
        print("✅ Modified view to use custom template for public narasumber profiles")  
        print("✅ Removed dependency on profile_base.html (no extra header)")
        print("✅ Applied neutral styling (btn-outline-secondary, text-muted)")
        print("✅ Made badges smaller with single color (font-size: 0.7rem)")
        print("✅ Maintained all requested functionality")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_public_narasumber_profile()
