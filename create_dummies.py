import os
import django
import random
import uuid
from datetime import timedelta
from io import BytesIO
import base64

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrapro.settings')
django.setup()

from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from narasumber.models import ExpertiseCategory, NarasumberProfile
from event.models import EventProfile  # SESUAIKAN jika letak model berbeda
from lowongan.models import Lowongan 

User = get_user_model()

# =========================================================
# Util: tiny PNG (1x1) agar tidak perlu Pillow
# =========================================================
# 1x1 PNG putih transparan (base64)
TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQAB"
    "J4mGtwAAAABJRU5ErkJggg=="
)

def tiny_png_contentfile(filename_prefix: str) -> ContentFile:
    data = base64.b64decode(TINY_PNG_B64)
    return ContentFile(data, name=f"{filename_prefix}_{uuid.uuid4().hex}.png")

# =========================================================
# Step 1: Seed Expertise Categories
# =========================================================
categories_seed = [
    ('Technology', 'Software development, AI, cybersecurity, dll.'),
    ('Business', 'Marketing, finance, entrepreneurship, dll.'),
    ('Health', 'Medicine, fitness, nutrition, wellness, dll.'),
    ('Education', 'Teaching, training, academic research, dll.'),
    ('Arts & Design', 'Graphic design, photography, music, dll.'),
    ('Engineering', 'Civil, mechanical, electrical engineering, dll.'),
]

print("Creating expertise categories...")
for name, desc in categories_seed:
    category, created = ExpertiseCategory.objects.get_or_create(
        name=name,
        defaults={'description': desc}
    )
    print(("✓ Created: " if created else "○ Already exists: ") + name)
print(f"Total categories: {ExpertiseCategory.objects.count()}\n")

all_categories = list(ExpertiseCategory.objects.all())
if not all_categories:
    raise RuntimeError("Tidak ada ExpertiseCategory. Pastikan model & migrasi sudah dibuat.")

# =========================================================
# Data pools
# =========================================================
first_names = ["Andi", "Budi", "Citra", "Dewi", "Eka", "Fajar", "Gita", "Hadi", "Indah", "Joko",
               "Kayla", "Lutfi", "Mega", "Nanda", "Oki", "Putri", "Rizky", "Sari", "Tono", "Vina"]
last_names  = ["Pratama", "Wijaya", "Siregar", "Saputra", "Kurniawan", "Lestari", "Hartono", "Hidayat",
               "Anggraini", "Pamungkas", "Wibowo", "Syahputra", "Ananda", "Setiawan"]

event_names = [
    "Tech Talk", "Business Summit", "Health Expo", "Edu Workshop", "Design Fest",
    "AI Conference", "Startup Meetup", "Wellness Retreat", "Teacher Training", "Art Showcase",
    "Engineer Day", "Cybersecurity Bootcamp", "Marketing Mastery", "Finance Forum"
]

PROVINCES_EVENT = [choice[0] for choice in EventProfile.PROVINCE_CHOICES]
PROVINCES_NS    = [choice[0] for choice in NarasumberProfile.PROVINCE_CHOICES]
experience_levels = [choice[0] for choice in NarasumberProfile.EXPERIENCE_LEVEL_CHOICES]

# =========================================================
# Helper: create or get user
# =========================================================
def ensure_user(username_prefix: str, user_type: str, email_domain="example.com") -> User:
    """
    Buat user unik dengan user_type ('event' atau 'narasumber').
    """
    username = f"{username_prefix}_{uuid.uuid4().hex[:8]}"
    email = f"{username}@{email_domain}"

    user = User.objects.create_user(
        username=username,
        email=email,
        password="password123",
    )
    # Set atribut tambahan pada custom User (sesuai modelmu)
    if hasattr(user, "user_type"):
        user.user_type = user_type
    if hasattr(user, "is_approved"):
        user.is_approved = True
    if hasattr(user, "approval_date"):
        user.approval_date = timezone.now()
    user.save()
    return user

# =========================================================
# Step 2: Generate 10 Narasumber (Profile + User)
# =========================================================
print("Creating 10 Narasumber profiles...")
created_narasumber = 0
for i in range(10):
    user = ensure_user("narasumber", user_type="narasumber")

    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    expertise = random.choice(all_categories)
    level = random.choice(experience_levels)
    years = random.randint(1, 15)

    phone = random.choice([None, f"+62{random.randint(81200000000, 81999999999)}"])
    is_phone_public = random.choice([True, False])

    location = random.choice(PROVINCES_NS)

    portfolio_link = random.choice([
        "", "https://portfolio.example.com", "https://mywork.example.org", None
    ]) or None

    # social_media = {
    #     "linkedin": f"https://www.linkedin.com/in/{full_name.replace(' ', '').lower()}",
    #     "twitter": f"https://x.com/{full_name.split()[0].lower()}{random.randint(1,999)}",
    #     "github": f"https://github.com/{full_name.split()[0].lower()}"
    # }

    # Buat profile (boleh langsung create karena tidak ada field wajib file)
    profile = NarasumberProfile.objects.create(
        user=user,
        full_name=full_name,
        bio=f"Saya {full_name}, berpengalaman di bidang {expertise.name}.",
        expertise_area=expertise,
        experience_level=level,
        years_of_experience=years,
        email=user.email,
        phone_number=phone,
        is_phone_public=is_phone_public,
        location=location,
        portfolio_link=portfolio_link,
        # social_media_links=social_media,
    )

    # Tambahkan foto profil dummy (opsional)
    if random.random() < 0.9:
        # langsung assign file lalu save model
        profile.profile_picture = tiny_png_contentfile("ns")
        profile.save(update_fields=["profile_picture"])

    created_narasumber += 1
    print(f"✓ Narasumber created: {full_name} ({expertise.name})")

print(f"Total Narasumber created in this run: {created_narasumber}")
print(f"Total Narasumber in DB: {NarasumberProfile.objects.count()}\n")

# =========================================================
# Step 3: Generate 10 Event (Profile + User) — FIXED
# =========================================================
print("Creating 10 Event profiles...")
created_events = 0
today = timezone.now().date()

def random_event_dates():
    """
    Randomkan:
    - 40%: ongoing (tanpa tanggal)
    - 30%: single-day
    - 30%: range start-end
    Campur status: past / upcoming / active.
    """
    kind = random.random()
    if kind < 0.4:
        return None, None

    status = random.choice(["past", "upcoming", "active"])

    if status == "past":
        start = today - timedelta(days=random.randint(20, 60))
        end = start + timedelta(days=random.randint(0, 3))
    elif status == "upcoming":
        start = today + timedelta(days=random.randint(3, 45))
        end = start + timedelta(days=random.randint(0, 3))
    else:  # active
        start = today - timedelta(days=random.randint(0, 3))
        end = today + timedelta(days=random.randint(0, 3))

    if random.random() < 0.3:
        return start, start
    return start, end

for i in range(10):
    user = ensure_user("event", user_type="event")

    name = f"{random.choice(event_names)} #{random.randint(100, 999)}"
    description = (
        f"{name} adalah acara untuk komunitas terkait. "
        "Akan ada sesi keynote, networking, dan workshop interaktif."
    )
    location = random.choice(PROVINCES_EVENT)
    email = user.email
    phone = random.choice([None, f"+62{random.randint(81100000000, 81999999999)}"])
    is_phone_public = random.choice([True, False])
    website = random.choice([None, "https://event.example.com", "https://landing.example.org"])

    start_date, end_date = random_event_dates()

    # ----- FIX: Jangan pakai .create() karena akan memicu save() -> full_clean()
    # cover_image wajib ada sebelum save pertama.
    event = EventProfile(
        user=user,
        name=name,
        description=description,
        location=location,
        email=email,
        phone_number=phone,
        is_phone_public=is_phone_public,
        website=website,
        start_date=start_date,
        end_date=end_date,
    )

    # Set cover_image lebih dulu sebelum save pertama
    event.cover_image = tiny_png_contentfile("cover")

    # (opsional) profile picture event organizer (bisa di-set sebelum save juga)
    if random.random() < 0.7:
        event.profile_picture = tiny_png_contentfile("evtpfp")

    # Sekarang save pertama kali (lolos full_clean karena cover_image sudah ada)
    event.save()

    created_events += 1
    status = event.event_status if hasattr(event, "event_status") else "-"
    print(f"✓ Event created: {name} | Status: {status}")

print(f"Total Events created in this run: {created_events}")
print(f"Total Events in DB: {EventProfile.objects.count()}\n")

print("Creating 10 Lowongan (Job Opportunities)...")
created_lowongan = 0

# ambil semua Event users (karena hanya mereka boleh buat lowongan)
event_users = User.objects.filter(user_type="event")
if not event_users.exists():
    raise RuntimeError("Tidak ada user dengan user_type=event. Jalankan seed Event dulu.")

# ambil expertise categories
categories = list(ExpertiseCategory.objects.all())
if not categories:
    raise RuntimeError("Tidak ada ExpertiseCategory. Jalankan seed kategori dulu.")

today = timezone.now().date()

for i in range(10):
    creator = random.choice(event_users)
    category = random.choice(categories)

    title = f"Lowongan {random.choice(['Speaker', 'Moderator', 'Trainer', 'Consultant'])} #{random.randint(100,999)}"
    description = (
        f"{title} untuk acara {random.choice(event_names)}. "
        "Kami mencari narasumber berpengalaman yang siap tampil profesional."
    )

    # event date in the future
    event_date = today + timedelta(days=random.randint(10, 90))
    application_deadline = event_date - timedelta(days=random.randint(3, 7))

    lowongan = Lowongan(
        title=title,
        description=description,
        created_by=creator,
        job_type=random.choice([c[0] for c in Lowongan.JOB_TYPE_CHOICES]),
        expertise_category=category,
        experience_level_required=random.choice([c[0] for c in Lowongan.EXPERIENCE_LEVEL_CHOICES]),
        location=random.choice([c[0] for c in Lowongan.PROVINCE_CHOICES]),
        is_remote=random.choice([True, False]),
        event_date=event_date,
        duration_hours=random.randint(1, 8),
        budget_amount=random.choice([None, random.randint(500000, 5000000)]),
        budget_negotiable=random.choice([True, False]),
        application_deadline=application_deadline,
        max_applicants=random.choice([None, random.randint(3, 20)]),
        requirements=random.choice([
            "",
            "Minimal pengalaman 2 tahun di bidang terkait.",
            "Mampu presentasi di depan publik.",
            "Punya portofolio relevan."
        ]),
        contact_email=creator.email,
        contact_phone=random.choice([None, f"+62{random.randint(81100000000, 81999999999)}"]),
        status=random.choice(["OPEN", "DRAFT", "CLOSED"]),
    )
    lowongan.save()

    created_lowongan += 1
    print(f"✓ Lowongan created: {title} | Status: {lowongan.status}")

print(f"Total Lowongan created in this run: {created_lowongan}")
print(f"Total Lowongan in DB: {Lowongan.objects.count()}\n")

print("Done.")
