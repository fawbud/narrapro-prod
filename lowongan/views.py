from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Lowongan, LowonganApplication
from .forms import (
    LowonganForm, LowonganStatusForm, LowonganApplicationForm,
    LowonganApplicationStatusForm, LowonganFilterForm
)


def lowongan_list(request):
    """
    Public view to list all open lowongan opportunities
    """
    lowongan_qs = Lowongan.objects.filter(status='OPEN').select_related(
        'created_by', 'expertise_category'
    )

    # Apply filters
    filter_form = LowonganFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        if search:
            lowongan_qs = lowongan_qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        job_type = filter_form.cleaned_data.get('job_type')
        if job_type:
            lowongan_qs = lowongan_qs.filter(job_type=job_type)

        expertise_category = filter_form.cleaned_data.get('expertise_category')
        if expertise_category:
            lowongan_qs = lowongan_qs.filter(expertise_category=expertise_category)

        experience_level = filter_form.cleaned_data.get('experience_level')
        if experience_level:
            lowongan_qs = lowongan_qs.filter(experience_level_required=experience_level)

        location = filter_form.cleaned_data.get('location')
        if location:
            lowongan_qs = lowongan_qs.filter(location=location)

        is_remote = filter_form.cleaned_data.get('is_remote')
        if is_remote:
            lowongan_qs = lowongan_qs.filter(is_remote=True)

    # Pagination
    paginator = Paginator(lowongan_qs, 12)
    page_number = request.GET.get('page')
    lowongan_page = paginator.get_page(page_number)

    context = {
        'lowongan_page': lowongan_page,
        'filter_form': filter_form,
        'total_count': lowongan_qs.count()
    }

    return render(request, 'lowongan/lowongan_list.html', context)


def lowongan_detail(request, lowongan_id):
    """
    Public view to show lowongan details
    """
    lowongan = get_object_or_404(
        Lowongan.objects.select_related('created_by', 'expertise_category'),
        id=lowongan_id
    )

    # Check if user can apply
    user_can_apply = False
    user_has_applied = False
    user_application = None

    if request.user.is_authenticated:
        user_can_apply = lowongan.can_user_apply(request.user)
        if request.user.user_type == 'narasumber':
            try:
                user_application = LowonganApplication.objects.get(
                    lowongan=lowongan,
                    applicant=request.user
                )
                user_has_applied = True
            except LowonganApplication.DoesNotExist:
                pass

    context = {
        'lowongan': lowongan,
        'user_can_apply': user_can_apply,
        'user_has_applied': user_has_applied,
        'user_application': user_application,
    }

    return render(request, 'lowongan/lowongan_detail.html', context)


@login_required
def lowongan_apply(request, lowongan_id):
    """
    View for narasumber users to apply for lowongan
    """
    lowongan = get_object_or_404(Lowongan, id=lowongan_id)

    if request.user.user_type != 'narasumber':
        messages.error(request, 'Hanya narasumber yang bisa melamar lowongan.')
        return redirect('lowongan:detail', lowongan_id=lowongan_id)

    if not lowongan.can_user_apply(request.user):
        messages.error(request, 'Anda tidak bisa melamar lowongan ini.')
        return redirect('lowongan:detail', lowongan_id=lowongan_id)

    if request.method == 'POST':
        form = LowonganApplicationForm(
            request.POST,
            user=request.user,
            lowongan=lowongan
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Lamaran Anda telah di-submit!')
            return redirect('lowongan:detail', lowongan_id=lowongan_id)
    else:
        form = LowonganApplicationForm(user=request.user, lowongan=lowongan)

    context = {
        'lowongan': lowongan,
        'form': form,
    }

    return render(request, 'lowongan/lowongan_apply.html', context)


@login_required
def my_lowongan(request):
    """
    View for Event users to manage their lowongan
    """
    if request.user.user_type != 'event':
        messages.error(request, 'Only Event users can access this page.')
        return redirect('main:home')

    lowongan_qs = Lowongan.objects.filter(created_by=request.user).select_related(
        'expertise_category'
    )

    # Apply filters
    filter_form = LowonganFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        if search:
            lowongan_qs = lowongan_qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        status = filter_form.cleaned_data.get('status')
        if status:
            lowongan_qs = lowongan_qs.filter(status=status)

    # Pagination
    paginator = Paginator(lowongan_qs, 10)
    page_number = request.GET.get('page')
    lowongan_page = paginator.get_page(page_number)

    context = {
        'lowongan_page': lowongan_page,
        'filter_form': filter_form,
        'total_count': lowongan_qs.count()
    }

    return render(request, 'lowongan/my_lowongan.html', context)


@login_required
def lowongan_create(request):
    """
    View for Event users to create new lowongan
    """
    if request.user.user_type != 'event':
        messages.error(request, 'Only Event users can create lowongan.')
        return redirect('main:home')

    if request.method == 'POST':
        form = LowonganForm(request.POST, user=request.user)
        if form.is_valid():
            lowongan = form.save()
            messages.success(request, f'Lowongan "{lowongan.title}" berhasil dibuat!')
            return redirect('lowongan:my_lowongan')
    else:
        form = LowonganForm(user=request.user)

    context = {
        'form': form,
        'title': 'Create New Lowongan'
    }

    return render(request, 'lowongan/lowongan_form.html', context)


@login_required
def lowongan_edit(request, lowongan_id):
    """
    View for Event users to edit their lowongan
    """
    lowongan = get_object_or_404(Lowongan, id=lowongan_id, created_by=request.user)

    if request.method == 'POST':
        form = LowonganForm(request.POST, instance=lowongan, user=request.user)
        if form.is_valid():
            lowongan = form.save()
            messages.success(request, f'Lowongan "{lowongan.title}" berhasil di-update!')
            return redirect('lowongan:my_lowongan')
    else:
        form = LowonganForm(instance=lowongan, user=request.user)

    context = {
        'form': form,
        'lowongan': lowongan,
        'title': f'Edit Lowongan: {lowongan.title}'
    }

    return render(request, 'lowongan/lowongan_form.html', context)


@login_required
def lowongan_delete(request, lowongan_id):
    """
    View for Event users to delete their lowongan
    """
    lowongan = get_object_or_404(Lowongan, id=lowongan_id, created_by=request.user)

    if request.method == 'POST':
        title = lowongan.title
        lowongan.delete()
        messages.success(request, f'Lowongan "{title}" berhasil dihapus!')
        return redirect('lowongan:my_lowongan')

    context = {
        'lowongan': lowongan,
    }

    return render(request, 'lowongan/lowongan_confirm_delete.html', context)


@login_required
@require_POST
def lowongan_update_status(request, lowongan_id):
    """
    AJAX view to update lowongan status
    """
    lowongan = get_object_or_404(Lowongan, id=lowongan_id, created_by=request.user)

    form = LowonganStatusForm(request.POST, instance=lowongan)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': f'Status updated to {lowongan.get_status_display()}',
            'new_status': lowongan.status,
            'new_status_display': lowongan.get_status_display()
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


@login_required
def lowongan_applications(request, lowongan_id):
    """
    View for Event users to see applications for their lowongan
    """
    lowongan = get_object_or_404(Lowongan, id=lowongan_id, created_by=request.user)

    applications_qs = LowonganApplication.objects.filter(
        lowongan=lowongan
    ).select_related('applicant').order_by('-applied_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications_qs = applications_qs.filter(status=status_filter)

    # Pagination
    paginator = Paginator(applications_qs, 10)
    page_number = request.GET.get('page')
    applications_page = paginator.get_page(page_number)

    context = {
        'lowongan': lowongan,
        'applications_page': applications_page,
        'status_filter': status_filter,
        'status_choices': LowonganApplication.STATUS_CHOICES,
    }

    return render(request, 'lowongan/lowongan_applications.html', context)


@login_required
def application_detail(request, application_id):
    """
    View for Event users to see application details
    """
    application = get_object_or_404(
        LowonganApplication.objects.select_related('applicant', 'lowongan'),
        id=application_id,
        lowongan__created_by=request.user
    )

    context = {
        'application': application,
    }

    return render(request, 'lowongan/application_detail.html', context)


@login_required
@require_POST
def application_update_status(request, application_id):
    """
    AJAX view for Event users to update application status
    """
    application = get_object_or_404(
        LowonganApplication,
        id=application_id,
        lowongan__created_by=request.user
    )

    form = LowonganApplicationStatusForm(request.POST, instance=application)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': f'Application status updated to {application.get_status_display()}',
            'new_status': application.status,
            'new_status_display': application.get_status_display()
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


# my_applications view moved to profiles app at profiles.views.profile_lamaran
