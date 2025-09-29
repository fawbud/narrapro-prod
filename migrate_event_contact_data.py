#!/usr/bin/env python
"""
Data migration script to convert existing event contact data to new email/phone format.
This should be run before the model migration.
"""
import os
import sys
import django
import re

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from event.models import EventProfile

def migrate_contact_data():
    """
    Migrate existing contact field data to email and phone fields
    """
    print("🔄 Migrating existing event contact data...")
    
    # Get all event profiles
    event_profiles = EventProfile.objects.all()
    
    if not event_profiles.exists():
        print("✅ No event profiles found, migration not needed")
        return
    
    migrated_count = 0
    
    for profile in event_profiles:
        print(f"\n📝 Processing: {profile.name}")
        
        # Skip if already has email
        if hasattr(profile, 'email') and profile.email:
            print(f"   ✅ Already has email: {profile.email}")
            continue
            
        # Skip if no contact data
        if not hasattr(profile, 'contact') or not profile.contact:
            print("   ⚠️ No contact data to migrate")
            continue
            
        contact_data = profile.contact
        print(f"   📞 Original contact: {contact_data}")
        
        # Try to extract email from contact field
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, contact_data)
        
        # Try to extract phone from contact field  
        phone_pattern = r'(\+?62|0)[0-9\s\-\(\)]{8,}'
        phones = re.findall(phone_pattern, contact_data)
        
        # Set email (use first email found or create default)
        if emails:
            email = emails[0]
            print(f"   ✅ Extracted email: {email}")
        else:
            # Create default email based on username
            email = f"{profile.user.username}@example.com"
            print(f"   🔧 Created default email: {email}")
        
        # Set phone (use first phone found)
        phone = None
        is_phone_public = False
        if phones:
            phone = phones[0].strip()
            is_phone_public = True  # Assume public since it was in contact field
            print(f"   ✅ Extracted phone: {phone}")
        else:
            print("   ⚠️ No phone number found")
        
        # Update the profile (we'll do this manually since the model hasn't been migrated yet)
        print(f"   💾 Would set email: {email}")
        if phone:
            print(f"   💾 Would set phone: {phone} (public: {is_phone_public})")
        
        migrated_count += 1
    
    print(f"\n✅ Migration preparation complete! Processed {migrated_count} profiles")
    print("\n⚠️ IMPORTANT: Run 'python manage.py makemigrations event' and 'python manage.py migrate' next")

if __name__ == "__main__":
    migrate_contact_data()
