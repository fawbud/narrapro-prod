from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('myprofile/', views.myprofile_redirect, name='myprofile_redirect'),
    path('profiles/<str:username>/', views.profile_detail, name='profile_detail'),
    path('profiles/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('profiles/<str:username>/change-password/', views.change_password, name='change_password'),
    path('profiles/<str:username>/lamaran/', views.profile_lamaran, name='profile_lamaran'),
    path('profiles/<str:username>/lowongan/', views.profile_lowongan, name='profile_lowongan'),
    path('profiles/<str:username>/booking/', views.profile_booking, name='profile_booking'),
    path('profiles/<str:username>/booking/create', views.book_narasumber, name='book_narasumber'),
    path('profiles/<str:username>/booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('profiles/<str:username>/booking/create/<uuid:narasumber_id>', views.create_booking, name='create_booking'),
]