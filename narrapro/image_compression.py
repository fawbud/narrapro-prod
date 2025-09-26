"""
Django Image Compressor Utilities
Server-side utilities to work with the client-side image compression module.

This module provides:
- Form fields with built-in compression support
- Widgets for image upload with compression
- Validation helpers
- Template tags for easy integration

@version 1.0.0
@author NarraPro Development Team
"""

import os
import json
from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from PIL import Image
import io


class CompressedImageWidget(forms.ClearableFileInput):
    """
    Custom widget for image upload with client-side compression
    """
    
    template_name = 'widgets/compressed_image_widget.html'
    
    def __init__(self, attrs=None, compression_options=None):
        default_attrs = {
            'accept': 'image/*',
            'class': 'compressed-image-input'
        }
        if attrs:
            default_attrs.update(attrs)
        
        super().__init__(default_attrs)
        
        # Default compression options
        self.compression_options = {
            'maxSizeKB': 1024,  # 1MB
            'quality': 0.8,
            'maxWidth': 1920,
            'maxHeight': 1080,
            'outputFormat': 'auto',
            'enablePreview': True,
            'autoCompress': True,
        }
        
        if compression_options:
            self.compression_options.update(compression_options)
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget with compression JavaScript"""
        context = {
            'widget': {
                'name': name,
                'value': value,
                'attrs': attrs or {},
                'compression_options': json.dumps(self.compression_options),
                'is_initial': bool(value and getattr(value, 'url', None)),
            }
        }
        
        # Render the base input
        html = super().render(name, value, attrs, renderer)
        
        # Add compression JavaScript and UI
        compression_html = render_to_string(self.template_name, context)
        
        return mark_safe(html + compression_html)
    
    class Media:
        js = ('js/image-compressor.js', 'js/compressed-image-widget.js')
        css = {'all': ('css/compressed-image-widget.css',)}


class CompressedImageField(forms.ImageField):
    """
    Custom image field that works with client-side compression
    """
    
    widget = CompressedImageWidget
    
    def __init__(self, *args, **kwargs):
        # Extract compression options
        self.compression_options = kwargs.pop('compression_options', {})
        self.max_size_kb = kwargs.pop('max_size_kb', 1024)
        self.validate_compression = kwargs.pop('validate_compression', True)
        
        super().__init__(*args, **kwargs)
        
        # Update widget with compression options
        if hasattr(self.widget, 'compression_options'):
            self.widget.compression_options.update(self.compression_options)
        else:
            self.widget = CompressedImageWidget(compression_options=self.compression_options)
    
    def validate(self, value):
        """Validate the uploaded image"""
        super().validate(value)
        
        if value and hasattr(value, 'size'):
            # Check file size
            size_kb = value.size / 1024
            if size_kb > self.max_size_kb and self.validate_compression:
                raise ValidationError(
                    f'Image file size ({size_kb:.1f}KB) exceeds maximum allowed size ({self.max_size_kb}KB). '
                    'Please ensure client-side compression is enabled.'
                )
    
    def clean(self, data, initial=None):
        """Clean and validate the image data"""
        cleaned_data = super().clean(data, initial)
        
        if cleaned_data and self.validate_compression:
            # Additional server-side validation
            self._validate_image_properties(cleaned_data)
        
        return cleaned_data
    
    def _validate_image_properties(self, image_file):
        """Validate image properties on the server side"""
        try:
            # Reset file pointer
            image_file.seek(0)
            
            # Open image with PIL
            img = Image.open(image_file)
            
            # Check dimensions if specified
            max_width = self.compression_options.get('maxWidth', 1920)
            max_height = self.compression_options.get('maxHeight', 1080)
            
            if img.width > max_width * 1.1 or img.height > max_height * 1.1:
                # Allow 10% tolerance for compression variations
                raise ValidationError(
                    f'Image dimensions ({img.width}x{img.height}) exceed maximum allowed '
                    f'dimensions ({max_width}x{max_height}). Please ensure proper compression.'
                )
            
            # Reset file pointer for further processing
            image_file.seek(0)
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            # If we can't validate, just warn in development
            if settings.DEBUG:
                print(f'Warning: Could not validate image properties: {e}')


class ImageCompressionMixin:
    """
    Mixin for forms that need image compression functionality
    """
    
    compression_config = {
        'maxSizeKB': 1024,
        'quality': 0.8,
        'maxWidth': 1920,
        'maxHeight': 1080,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_compressed_fields()
    
    def _setup_compressed_fields(self):
        """Set up compression for image fields"""
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ImageField) and not isinstance(field, CompressedImageField):
                # Convert regular ImageField to CompressedImageField
                self.fields[field_name] = CompressedImageField(
                    required=field.required,
                    compression_options=self.compression_config,
                    max_size_kb=self.compression_config['maxSizeKB']
                )
    
    def get_compression_config(self):
        """Get compression configuration as JSON"""
        return json.dumps(self.compression_config)


def validate_compressed_image(image_file, max_size_kb=1024):
    """
    Standalone validator for compressed images
    
    Args:
        image_file: Uploaded image file
        max_size_kb: Maximum file size in KB
    
    Raises:
        ValidationError: If validation fails
    """
    if not image_file:
        return
    
    # Check file size
    size_kb = image_file.size / 1024
    if size_kb > max_size_kb:
        raise ValidationError(
            f'Image file size ({size_kb:.1f}KB) exceeds maximum allowed size ({max_size_kb}KB)'
        )
    
    # Validate image format
    try:
        image_file.seek(0)
        img = Image.open(image_file)
        img.verify()  # Verify it's a valid image
        image_file.seek(0)  # Reset for further processing
    except Exception:
        raise ValidationError('Invalid image file')


def get_image_info(image_file):
    """
    Get information about an uploaded image file
    
    Args:
        image_file: Uploaded image file
    
    Returns:
        dict: Image information
    """
    if not image_file:
        return None
    
    try:
        image_file.seek(0)
        img = Image.open(image_file)
        
        info = {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height,
            'file_size': image_file.size,
            'file_size_kb': image_file.size / 1024,
            'file_size_mb': image_file.size / (1024 * 1024),
        }
        
        image_file.seek(0)  # Reset for further processing
        return info
        
    except Exception as e:
        if settings.DEBUG:
            print(f'Error getting image info: {e}')
        return None


class ImageCompressionService:
    """
    Service class for handling image compression operations
    """
    
    @staticmethod
    def get_compression_stats(original_size, compressed_size):
        """
        Calculate compression statistics
        
        Args:
            original_size: Original file size in bytes
            compressed_size: Compressed file size in bytes
        
        Returns:
            dict: Compression statistics
        """
        if not original_size or not compressed_size:
            return None
        
        compression_ratio = 1 - (compressed_size / original_size)
        size_saved = original_size - compressed_size
        
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'compression_percentage': compression_ratio * 100,
            'size_saved': size_saved,
            'size_saved_kb': size_saved / 1024,
            'size_saved_mb': size_saved / (1024 * 1024),
        }
    
    @staticmethod
    def server_side_compress(image_file, max_size_kb=1024, quality=85):
        """
        Server-side image compression as fallback
        
        Args:
            image_file: Image file to compress
            max_size_kb: Target maximum size in KB
            quality: JPEG quality (1-100)
        
        Returns:
            InMemoryUploadedFile: Compressed image file
        """
        try:
            image_file.seek(0)
            img = Image.open(image_file)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Calculate target dimensions
            max_dimension = 1920
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Save to memory with compression
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            # Create new uploaded file
            compressed_file = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{os.path.splitext(image_file.name)[0]}.jpg",
                'image/jpeg',
                output.getbuffer().nbytes,
                None
            )
            
            return compressed_file
            
        except Exception as e:
            if settings.DEBUG:
                print(f'Server-side compression failed: {e}')
            return image_file  # Return original if compression fails


# Template tag helpers
def compression_widget_context(field, compression_options=None):
    """
    Helper function to create context for compression widget templates
    """
    options = {
        'maxSizeKB': 1024,
        'quality': 0.8,
        'maxWidth': 1920,
        'maxHeight': 1080,
        'enablePreview': True,
        'autoCompress': True,
    }
    
    if compression_options:
        options.update(compression_options)
    
    return {
        'field': field,
        'compression_options': json.dumps(options),
        'compression_options_obj': options,
    }
