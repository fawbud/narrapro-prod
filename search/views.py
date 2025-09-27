from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lowongan.models import Lowongan
from narasumber.models import *
from event.models import *
from django.db.models import Q
from django.core.paginator import Paginator
import json

def search_preview(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must log in to access this page.")
        return redirect('/login')
    """
    Return JSON search preview results for popup suggestions.
    """
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    lowered = query.lower()
    category = None

    # --- Prefix detection ---
    if lowered.startswith("lowongan:"):
        category = "lowongan"
        query = query[len("lowongan:"):].strip()
    elif lowered.startswith("event:"):
        category = "event"
        query = query[len("event:"):].strip()
    elif lowered.startswith("narasumber:"):
        category = "narasumber"
        query = query[len("narasumber:"):].strip()

    results = []

    # --- Handle specific category ---
    if category == "event":
        event_matches = EventProfile.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:5]
        for event in event_matches:
            results.append({
                "type": "event",
                "id": event.id,
                "title": event.name,
                "subtitle": event.location_display,
            })

    elif category == "narasumber":
        narsum_matches = NarasumberProfile.objects.filter(
            Q(full_name__icontains=query) | Q(bio__icontains=query)
        )[:5]
        for narsum in narsum_matches:
            results.append({
                "type": "narasumber",
                "id": narsum.id,
                "title": narsum.full_name,
                "subtitle": narsum.expertise_area.name,
            })

    elif category == "lowongan":
        lowongan_matches = Lowongan.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
        for low in lowongan_matches:
            results.append({
                "type": "lowongan",
                "id": low.id,
                "title": low.title,
                "subtitle": low.company_name if hasattr(low, "company_name") else "",
            })

    else:
        # --- Default: search all categories (preview) ---
        event_matches = EventProfile.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:3]
        for event in event_matches:
            results.append({
                "type": "event",
                "id": event.id,
                "title": event.name,
                "subtitle": event.location_display,
            })

        narsum_matches = NarasumberProfile.objects.filter(
            Q(full_name__icontains=query) | Q(bio__icontains=query)
        )[:3]
        for narsum in narsum_matches:
            results.append({
                "type": "narasumber",
                "id": narsum.id,
                "title": narsum.full_name,
                "subtitle": narsum.expertise_area.name,
            })

        lowongan_matches = Lowongan.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:3]
        for low in lowongan_matches:
            results.append({
                "type": "lowongan",
                "id": low.id,
                "title": low.title,
                "subtitle": low.company_name if hasattr(low, "company_name") else "",
            })

    return JsonResponse({"results": results})


def search_result_page(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must log in to access this page.")
        return redirect('/login')
    
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").lower()
    page_number = request.GET.get("page", 1)

    expertise_filters = request.GET.getlist("expertise")
    expertise_ids = [int(e) for e in expertise_filters if e.isdigit()]

    lowered = query.lower()
    if lowered.startswith("lowongan:"):
        category = "lowongan"
        query = query[len("lowongan:"):].strip()
    elif lowered.startswith("event:"):
        category = "event"
        query = query[len("event:"):].strip()
    elif lowered.startswith("narasumber:"):
        category = "narasumber"
        query = query[len("narasumber:"):].strip()

    events, narasumbers, lowongans = [], [], []
    has_more = {"event": False, "narasumber": False, "lowongan": False}
    pagination_obj = None  

    # counts default
    events_count = 0
    narasumbers_count = 0
    lowongans_count = 0

    # =============== NARASUMBER ===============
    if category == "narasumber":
        qs = NarasumberProfile.objects.all()
        if query:
            qs = qs.filter(Q(full_name__icontains=query) | Q(bio__icontains=query))
        if expertise_ids:
            qs = qs.filter(expertise_area__id__in=expertise_ids)

        qs = qs.order_by("-created_at")
        narasumbers_count = qs.count()
        paginator = Paginator(qs, 25)
        narasumbers = paginator.get_page(page_number)
        pagination_obj = narasumbers

    # =============== EVENT ===============
    elif category == "event":
        qs = EventProfile.objects.all()
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))

        qs = qs.order_by("-created_at")
        events_count = qs.count()
        paginator = Paginator(qs, 25)
        events = paginator.get_page(page_number)
        pagination_obj = events

    # =============== LOWONGAN ===============
    elif category == "lowongan":
        qs = Lowongan.objects.all()
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))

        qs = qs.order_by("-created_at")
        lowongans_count = qs.count()
        paginator = Paginator(qs, 25)
        lowongans = paginator.get_page(page_number)
        pagination_obj = lowongans

    # =============== ALL CATEGORIES (preview) ===============
    else:
        event_qs = EventProfile.objects.all()
        if query:
            event_qs = event_qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
        events_count = event_qs.count()
        events = event_qs.order_by("-created_at")[:9]

        narsum_qs = NarasumberProfile.objects.all()
        if query:
            narsum_qs = narsum_qs.filter(Q(full_name__icontains=query) | Q(bio__icontains=query))
        narasumbers_count = narsum_qs.count()
        narasumbers = narsum_qs.order_by("-created_at")[:9]

        lowongan_qs = Lowongan.objects.all()
        if query:
            lowongan_qs = lowongan_qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
        lowongans_count = lowongan_qs.count()
        lowongans = lowongan_qs.order_by("-created_at")[:9]

        has_more["event"] = event_qs.count() > 8
        has_more["narasumber"] = narsum_qs.count() > 8
        # has_more["lowongan"] = lowongan_qs.count() > 8

    context = {
        "query": query,
        "category": category,
        "events": events,
        "narasumbers": narasumbers,
        "lowongans": lowongans,
        "has_more": has_more,
        "pagination_obj": pagination_obj,
        "expertise_categories": ExpertiseCategory.objects.all(),
        "selected_expertise": expertise_ids,
        "events_count": events_count,
        "narasumbers_count": narasumbers_count,
        "lowongans_count": lowongans_count,
    }
    return render(request, "search-result.html", context)
