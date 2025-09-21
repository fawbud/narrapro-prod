import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from event.models import EventProfile
from narasumber.models import NarasumberProfile, ExpertiseCategory
from profiles.models import User


# ==================================================
# Buat expertise categories kalau belum ada
# ==================================================
categories = [
    ("Technology", "Software development, AI, cybersecurity, etc."),
    ("Business", "Marketing, finance, entrepreneurship, etc."),
    ("Health", "Medicine, fitness, nutrition, wellness, etc."),
    ("Education", "Teaching, training, academic research, etc."),
    ("Arts & Design", "Graphic design, photography, music, etc."),
    ("Engineering", "Civil, mechanical, electrical engineering, etc."),
]

for name, desc in categories:
    ExpertiseCategory.objects.get_or_create(
        name=name, defaults={"description": desc}
    )

all_categories = list(ExpertiseCategory.objects.all())


# ==================================================
# Buat users & EventProfile
# ==================================================
print("Creating Event users & profiles...")
for i in range(1, 11):
    username = f"event_user{i}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@narrapro.com",
            "user_type": "event",
            "is_active": True,
            "is_approved": True,
        },
    )
    if created:
        user.set_password("password123")
        user.save()
        print(f"✓ Created Event User: {username}")
    else:
        print(f"○ Event User exists: {username}")

    # Buat EventProfile kalau belum ada
    if not hasattr(user, "event_profile"):
        name = f"Event Demo {i}"
        description = f"Deskripsi untuk {name}. Acara ini membahas berbagai topik menarik."
        location = random.choice([choice[0] for choice in EventProfile.PROVINCE_CHOICES])
        contact = f"event{i}@narrapro.com"

        start_date = date.today() + timedelta(days=i * 3)
        end_date = start_date + timedelta(days=random.randint(1, 3))

        EventProfile.objects.create(
            user=user,
            name=name,
            description=description,
            location=location,
            contact=contact,
            website=f"https://event{i}.narrapro.com",
            cover_image=f"event_covers/{user.id}/dummy{i}.jpg",
            start_date=start_date,
            end_date=end_date,
        )
        print(f"✓ Created EventProfile for {username}")
    else:
        print(f"○ EventProfile already exists for {username}")


# ==================================================
# Buat users & NarasumberProfile
# ==================================================
print("\nCreating Narasumber users & profiles...")
for i in range(1, 11):
    username = f"narasumber_user{i}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@narrapro.com",
            "user_type": "narasumber",
            "is_active": True,
            "is_approved": True,
        },
    )
    if created:
        user.set_password("password123")
        user.save()
        print(f"✓ Created Narasumber User: {username}")
    else:
        print(f"○ Narasumber User exists: {username}")

    # Buat NarasumberProfile kalau belum ada
    if not hasattr(user, "narasumber_profile"):
        full_name = f"Narasumber Demo {i}"
        bio = f"Bio singkat untuk {full_name}, dengan pengalaman di bidang tertentu."
        expertise_area = random.choice(all_categories)
        experience_level = random.choice([c[0] for c in NarasumberProfile.EXPERIENCE_LEVEL_CHOICES])
        years_of_experience = random.randint(1, 15)
        location = random.choice([choice[0] for choice in NarasumberProfile.PROVINCE_CHOICES])

        NarasumberProfile.objects.create(
            user=user,
            full_name=full_name,
            bio=bio,
            expertise_area=expertise_area,
            experience_level=experience_level,
            years_of_experience=years_of_experience,
            email=f"narasumber{i}@narrapro.com",
            phone_number=f"08123{i:04d}",
            is_phone_public=random.choice([True, False]),
            location=location,
        )
        print(f"✓ Created NarasumberProfile for {username}")
    else:
        print(f"○ NarasumberProfile already exists for {username}")


print("\nSeeding selesai 🚀")
