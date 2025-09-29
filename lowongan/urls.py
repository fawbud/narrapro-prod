from django.urls import path
from . import views

app_name = 'lowongan'

urlpatterns = [
    # Public views
    path('', views.lowongan_list, name='list'),
    path('<uuid:lowongan_id>/', views.lowongan_detail, name='detail'),
    path('<uuid:lowongan_id>/apply/', views.lowongan_apply, name='apply'),

    # Event user views (lowongan management)
    path('my/', views.my_lowongan, name='my_lowongan'),
    path('create/', views.lowongan_create, name='create'),
    path('<uuid:lowongan_id>/edit/', views.lowongan_edit, name='edit'),
    path('<uuid:lowongan_id>/delete/', views.lowongan_delete, name='delete'),
    path('<uuid:lowongan_id>/update-status/', views.lowongan_update_status, name='update_status'),

    # Application management
    path('<uuid:lowongan_id>/applications/', views.lowongan_applications, name='applications'),
    path('applications/<uuid:application_id>/', views.application_detail, name='application_detail'),
    path('applications/<uuid:application_id>/update-status/', views.application_update_status, name='application_update_status'),

    # Narasumber user views - moved to profiles app
    # path('my-applications/', views.my_applications, name='my_applications'),
]