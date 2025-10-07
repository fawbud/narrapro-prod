"""
Sample Implementation: Image Compression Module
This file demonstrates how to use the image compression module in your Django forms

@version 1.0.0
@author NarraPro Development Team
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from narrapro.image_compression import (
    CompressedImageField, 
    CompressedImageWidget, 
    ImageCompressionMixin,
    validate_compressed_image
)

# Example 1: Basic form with compressed image field
class ProfileForm(forms.ModelForm):
    """Basic profile form with image compression"""
    
    profile_picture = CompressedImageField(
        label='Profile Picture',
        help_text='Upload your profile picture (automatically compressed to 500KB)',
        required=False,
        compression_options={
            'maxSizeKB': 500,
            'quality': 0.85,
            'maxWidth': 800,
            'maxHeight': 800,
            'outputFormat': 'jpeg',
        }
    )
    
    class Meta:
        model = User  # Replace with your User/Profile model
        fields = ['first_name', 'last_name', 'email', 'profile_picture']


# Example 2: Form with multiple image fields using mixin
class EventForm(ImageCompressionMixin, forms.ModelForm):
    """Event form with automatic compression for all image fields"""
    
    # Global compression settings for all image fields
    compression_config = {
        'maxSizeKB': 1024,  # 1MB
        'quality': 0.8,
        'maxWidth': 1920,
        'maxHeight': 1080,
    }
    
    # These will automatically be converted to CompressedImageField
    cover_image = forms.ImageField(
        label='Event Cover Image',
        help_text='Upload a cover image for your event'
    )
    
    gallery_image_1 = forms.ImageField(
        label='Gallery Image 1',
        required=False
    )
    
    gallery_image_2 = forms.ImageField(
        label='Gallery Image 2', 
        required=False
    )
    
    class Meta:
        model = User  # Replace with your Event model
        fields = ['title', 'description', 'cover_image', 'gallery_image_1', 'gallery_image_2']


# Example 3: Custom validation with compression
class ProductForm(forms.ModelForm):
    """Product form with custom validation and compression"""
    
    main_image = CompressedImageField(
        label='Product Image',
        help_text='Main product image (max 800KB)',
        compression_options={
            'maxSizeKB': 800,
            'quality': 0.9,
            'maxWidth': 1200,
            'maxHeight': 1200,
        }
    )
    
    thumbnail = CompressedImageField(
        label='Thumbnail',
        help_text='Small thumbnail image (max 200KB)',
        compression_options={
            'maxSizeKB': 200,
            'quality': 0.7,
            'maxWidth': 400,
            'maxHeight': 400,
        }
    )
    
    def clean_main_image(self):
        """Custom validation for main image"""
        image = self.cleaned_data.get('main_image')
        
        if image:
            # Use the built-in validator
            validate_compressed_image(image, max_size_kb=800)
            
            # Additional custom validation
            from PIL import Image
            import io
            
            # Reset file pointer
            image.seek(0)
            img = Image.open(image)
            
            # Check minimum dimensions
            if img.width < 600 or img.height < 600:
                raise ValidationError(
                    'Product image must be at least 600x600 pixels'
                )
            
            # Check aspect ratio (square images preferred)
            aspect_ratio = img.width / img.height
            if aspect_ratio < 0.8 or aspect_ratio > 1.2:
                raise ValidationError(
                    'Product image should be approximately square (aspect ratio 0.8-1.2)'
                )
            
            # Reset file pointer for Django to process
            image.seek(0)
        
        return image
    
    class Meta:
        model = User  # Replace with your Product model
        fields = ['name', 'description', 'price', 'main_image', 'thumbnail']


# Example 4: Dynamic compression settings
class DynamicCompressionForm(forms.Form):
    """Form with dynamic compression settings based on user preferences"""
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adjust compression settings based on user's connection speed
        # This is just an example - you'd get this from user preferences/detection
        is_mobile = getattr(user, 'is_mobile', False) if user else False
        
        if is_mobile:
            # More aggressive compression for mobile users
            compression_options = {
                'maxSizeKB': 300,
                'quality': 0.7,
                'maxWidth': 800,
                'maxHeight': 600,
            }
        else:
            # Standard compression for desktop users
            compression_options = {
                'maxSizeKB': 1024,
                'quality': 0.85,
                'maxWidth': 1920,
                'maxHeight': 1080,
            }
        
        self.fields['image'] = CompressedImageField(
            label='Upload Image',
            compression_options=compression_options,
            help_text=f"Max size: {compression_options['maxSizeKB']}KB"
        )


# Example 5: Custom widget with additional features
class AdvancedImageWidget(CompressedImageWidget):
    """Custom widget with additional features"""
    
    def __init__(self, attrs=None, compression_options=None):
        # Custom compression options with more features
        default_compression = {
            'maxSizeKB': 1024,
            'quality': 0.8,
            'maxWidth': 1920,
            'maxHeight': 1080,
            'outputFormat': 'auto',
            'enablePreview': True,
            'autoCompress': True,
            'allowedTypes': ['image/jpeg', 'image/png', 'image/webp'],
        }
        
        if compression_options:
            default_compression.update(compression_options)
        
        # Add custom CSS classes
        default_attrs = {
            'class': 'advanced-image-input',
            'data-auto-upload': 'true',
        }
        
        if attrs:
            default_attrs.update(attrs)
        
        super().__init__(default_attrs, default_compression)


class AdvancedImageForm(forms.Form):
    """Form using the advanced image widget"""
    
    image = forms.ImageField(
        widget=AdvancedImageWidget(
            attrs={'placeholder': 'Choose an image...'},
            compression_options={
                'maxSizeKB': 512,
                'quality': 0.9,
                'outputFormat': 'jpeg',
            }
        )
    )


# Example 6: Batch upload form
class BatchUploadForm(forms.Form):
    """Form for uploading multiple images with compression"""
    
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
            'accept': 'image/*',
            'class': 'batch-upload-input'
        }),
        help_text='Select multiple images (each will be compressed to 800KB)',
        label='Upload Images'
    )
    
    def clean_images(self):
        """Validate multiple images"""
        images = self.files.getlist('images')
        
        if len(images) > 10:
            raise ValidationError('Maximum 10 images allowed')
        
        for image in images:
            # Validate each image
            validate_compressed_image(image, max_size_kb=800)
        
        return images


# Usage examples for views
"""
# views.py example

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import ProfileForm, EventForm, ProductForm

def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil di-update!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'profile_edit.html', {'form': form})

def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            
            # Get compression info if available
            compression_info = []
            for field_name in ['cover_image', 'gallery_image_1', 'gallery_image_2']:
                field = form.fields.get(field_name)
                if hasattr(field, 'widget') and hasattr(field.widget, 'compression_options'):
                    compression_info.append({
                        'field': field_name,
                        'settings': field.widget.compression_options
                    })
            
            messages.success(request, 'Event berhasil dibuat!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    
    return render(request, 'create_event.html', {'form': form})

def ajax_upload(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return JsonResponse({
                'success': True,
                'product_id': product.id,
                'image_url': product.main_image.url if product.main_image else None
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
"""

# Template usage examples
"""
<!-- profile_edit.html example -->
{% extends 'base.html' %}
{% load static %}
{% load image_compression %}

{% block extra_css %}
    {% compression_styles %}
    <style>
        .form-container {
            max-width: 600px;
            margin: 2rem auto;
            padding: 2rem;
        }
    </style>
{% endblock %}

{% block extra_js %}
    {% compression_scripts %}
{% endblock %}

{% block content %}
<div class="form-container">
    <h2>Edit Profile</h2>
    
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {{ field }}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="alert alert-danger">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class="btn btn-primary">Save Changes</button>
    </form>
</div>
{% endblock %}

<!-- Alternative using template tags -->
{% block content_alternative %}
<div class="form-container">
    <h2>Create Event</h2>
    
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        <div class="form-group">
            <label>Event Title</label>
            {{ form.title }}
        </div>
        
        <div class="form-group">
            <label>Description</label>
            {{ form.description }}
        </div>
        
        <!-- Using template tag for image compression -->
        <div class="form-group">
            <label>Cover Image</label>
            {% image_compression_widget 'cover_image' max_size_kb=1024 quality=0.85 %}
        </div>
        
        <button type="submit" class="btn btn-primary">Create Event</button>
    </form>
</div>
{% endblock %}
"""
