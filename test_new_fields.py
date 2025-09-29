#!/usr/bin/env python
"""
Test script to verify new fields are available in forms
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from main.forms import EventRegistrationForm, NarasumberRegistrationForm
from profiles.forms import EventProfileForm, NarasumberProfileForm
from narasumber.models import Education, NarasumberProfile
from event.models import EventProfile

def test_event_forms():
    print("=== Testing Event Forms ===")
    
    # Test registration form
    reg_form = EventRegistrationForm()
    print(f"Event Registration Form Fields: {list(reg_form.fields.keys())}")
    
    # Test edit form
    edit_form = EventProfileForm()
    print(f"Event Profile Edit Form Fields: {list(edit_form.fields.keys())}")
    
    # Check if new fields are present
    new_fields = ['event_type', 'target_audience']
    for field in new_fields:
        if field in reg_form.fields:
            print(f"✅ {field} found in registration form")
        else:
            print(f"❌ {field} NOT found in registration form")
            
        if field in edit_form.fields:
            print(f"✅ {field} found in edit form")
        else:
            print(f"❌ {field} NOT found in edit form")
    
    # Test event type choices
    event_type_choices = EventProfile.EVENT_TYPE_CHOICES
    print(f"Event Type Choices: {event_type_choices}")
    
    # Test location choices
    online_choices = EventProfile.ONLINE_PLATFORM_CHOICES
    province_choices = EventProfile.PROVINCE_CHOICES
    print(f"Online Platform Choices: {len(online_choices)} choices")
    print(f"Province Choices: {len(province_choices)} choices")

def test_narasumber_forms():
    print("\n=== Testing Narasumber Forms ===")
    
    # Test registration form
    reg_form = NarasumberRegistrationForm()
    print(f"Narasumber Registration Form Fields: {list(reg_form.fields.keys())}")
    
    # Test edit form
    edit_form = NarasumberProfileForm()
    print(f"Narasumber Profile Edit Form Fields: {list(edit_form.fields.keys())}")
    
    # Test Education model
    education_fields = [field.name for field in Education._meta.fields if field.name != 'id']
    print(f"Education Model Fields: {education_fields}")
    
    # Test Education choices
    degree_choices = Education.DEGREE_CHOICES
    print(f"Degree Choices: {degree_choices}")

def test_model_methods():
    print("\n=== Testing Model Methods ===")
    
    # Test EventProfile methods
    print("EventProfile.get_location_choices_for_event_type('online'):")
    online_choices = EventProfile.get_location_choices_for_event_type('online')
    print(f"  - {len(online_choices)} choices for online events")
    
    print("EventProfile.get_location_choices_for_event_type('offline'):")
    offline_choices = EventProfile.get_location_choices_for_event_type('offline')
    print(f"  - {len(offline_choices)} choices for offline events")

if __name__ == "__main__":
    print("🧪 Testing New Fields Implementation\n")
    test_event_forms()
    test_narasumber_forms()
    test_model_methods()
    print("\n✅ Test completed!")
