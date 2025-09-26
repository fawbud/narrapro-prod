# Image Compression Module - Integration Guide

## Overview

This comprehensive image compression module provides client-side image compression for Django applications. Images are compressed in the user's browser before upload, reducing server load and improving upload speeds.

### Features

- ✅ **Client-side compression** - Processing happens in the browser
- ✅ **Configurable size limits** - Set maximum file size in KB (default: 1MB)
- ✅ **Quality control** - Adjustable compression quality (0.1 - 1.0)
- ✅ **Multiple formats** - Support for JPEG, PNG, WebP, GIF
- ✅ **Drag & drop** - Modern file upload interface
- ✅ **Progress tracking** - Real-time compression progress
- ✅ **Preview functionality** - Image preview with compression stats
- ✅ **Error handling** - Comprehensive validation and error messages
- ✅ **Django integration** - Custom form fields and widgets
- ✅ **Template tags** - Easy template integration
- ✅ **Responsive design** - Mobile-friendly interface
- ✅ **Dark mode support** - Automatic dark mode detection

## Quick Start

### 1. Basic Integration

Add the compression module to your Django template:

```html
<!-- In your template head -->
{% load static %}
{% load image_compression %}

{% compression_styles %}
{% compression_scripts %}

<!-- In your form -->
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    
    <!-- Method 1: Using template tag -->
    {% image_compression_widget 'profile_picture' max_size_kb=500 quality=0.85 %}
    
    <!-- Method 2: Using form field (if using CompressedImageField) -->
    {{ form.profile_picture }}
    
    <button type="submit">Upload</button>
</form>
```

### 2. Using Custom Form Fields

Update your Django forms to use the compressed image field:

```python
# forms.py
from django import forms
from narrapro.image_compression import CompressedImageField, ImageCompressionMixin

class ProfileForm(ImageCompressionMixin, forms.ModelForm):
    # Automatic compression for all image fields
    compression_config = {
        'maxSizeKB': 500,  # 500KB max
        'quality': 0.85,   # 85% quality
        'maxWidth': 1200,  # Max 1200px width
        'maxHeight': 800,  # Max 800px height
    }
    
    class Meta:
        model = Profile
        fields = ['name', 'profile_picture', 'cover_image']

# Or use individual field configuration
class EventForm(forms.ModelForm):
    cover_image = CompressedImageField(
        compression_options={
            'maxSizeKB': 1024,  # 1MB max
            'quality': 0.9,     # 90% quality
            'maxWidth': 1920,   # HD width
            'maxHeight': 1080,  # HD height
            'outputFormat': 'jpeg',  # Force JPEG output
        }
    )
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'cover_image']
```

### 3. JavaScript-Only Integration

For non-Django forms or custom implementations:

```html
<input type="file" id="imageInput" accept="image/*">
<div id="preview"></div>
<div id="progress"></div>

<script>
// Initialize compressor
const compressor = new ImageCompressor({
    maxSizeKB: 1024,        // 1MB max
    quality: 0.8,           // 80% quality
    maxWidth: 1920,         // Max width
    maxHeight: 1080,        // Max height
    enablePreview: true,    // Show preview
    onProgress: (percent, message) => {
        document.getElementById('progress').innerHTML = 
            `<div style="width: ${percent}%"></div><p>${message}</p>`;
    },
    onSuccess: (compressedFile, stats) => {
        console.log('Compression complete:', stats);
        // Handle compressed file
        handleUpload(compressedFile);
    },
    onError: (error) => {
        console.error('Compression failed:', error);
        alert('Compression failed: ' + error.message);
    }
});

// Initialize with file input
compressor.init('#imageInput');

function handleUpload(file) {
    const formData = new FormData();
    formData.append('image', file);
    
    fetch('/upload/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => console.log('Upload success:', data))
    .catch(error => console.error('Upload error:', error));
}
</script>
```

## Configuration Options

### Compression Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `maxSizeKB` | number | 1024 | Maximum file size in KB |
| `quality` | number | 0.8 | Compression quality (0.1-1.0) |
| `maxWidth` | number | 1920 | Maximum image width in pixels |
| `maxHeight` | number | 1080 | Maximum image height in pixels |
| `outputFormat` | string | 'auto' | Output format: 'auto', 'jpeg', 'png', 'webp' |
| `allowedTypes` | array | ['image/jpeg', 'image/png', 'image/gif', 'image/webp'] | Allowed MIME types |

### UI Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enablePreview` | boolean | true | Show image preview |
| `autoCompress` | boolean | true | Auto-compress on file selection |
| `dropContainer` | string/element | null | Drag & drop container selector |

### Callback Functions

| Option | Type | Description |
|--------|------|-------------|
| `onProgress` | function | Called during compression: `(percentage, message)` |
| `onSuccess` | function | Called on success: `(compressedFile, stats)` |
| `onError` | function | Called on error: `(error)` |
| `onPreview` | function | Called when preview is ready: `(dataUrl, file)` |

## Advanced Usage

### 1. Custom Validation

```python
# models.py
from django.core.exceptions import ValidationError
from narrapro.image_compression import validate_compressed_image

def validate_profile_image(image):
    validate_compressed_image(image, max_size_kb=500)
    
    # Additional custom validation
    if image:
        from PIL import Image
        img = Image.open(image)
        if img.width < 200 or img.height < 200:
            raise ValidationError('Profile image must be at least 200x200 pixels')

class Profile(models.Model):
    profile_picture = models.ImageField(
        upload_to='profiles/',
        validators=[validate_profile_image]
    )
```

### 2. Multiple File Upload

```html
<input type="file" id="multipleImages" multiple accept="image/*">
<div id="previews"></div>

<script>
const compressor = new ImageCompressor({
    maxSizeKB: 800,
    quality: 0.85,
    onSuccess: (file, stats) => {
        addToUploadQueue(file, stats);
    }
});

document.getElementById('multipleImages').addEventListener('change', async (e) => {
    const files = Array.from(e.target.files);
    
    for (const file of files) {
        try {
            await compressor.processFile(file);
        } catch (error) {
            console.error(`Failed to compress ${file.name}:`, error);
        }
    }
});
</script>
```

### 3. Server-side Fallback

```python
# views.py
from narrapro.image_compression import ImageCompressionService

def upload_image(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        
        if image:
            # Check if client-side compression was successful
            if image.size > 1024 * 1024:  # 1MB
                # Apply server-side compression as fallback
                image = ImageCompressionService.server_side_compress(
                    image, 
                    max_size_kb=1024, 
                    quality=85
                )
            
            # Save the image
            instance = MyModel.objects.create(image=image)
            
            return JsonResponse({
                'success': True,
                'image_url': instance.image.url
            })
    
    return JsonResponse({'success': False})
```

### 4. Progressive Enhancement

```html
<!-- Fallback for users without JavaScript -->
<noscript>
    <div class="alert alert-info">
        <strong>Note:</strong> JavaScript is disabled. Images will not be compressed 
        before upload. Please ensure your images are under 1MB.
    </div>
</noscript>

<!-- Enhanced experience with JavaScript -->
<div class="js-only" style="display: none;">
    <div id="compressionWidget"></div>
</div>

<script>
// Show enhanced widget only when JavaScript is available
document.querySelector('.js-only').style.display = 'block';

// Initialize compression widget
const widget = new CompressedImageWidget(
    document.getElementById('compressionWidget'),
    { maxSizeKB: 500, quality: 0.8 }
);
</script>
```

## Integration Examples

### 1. User Profile Form

```python
# forms.py
from django import forms
from django.contrib.auth.models import User
from narrapro.image_compression import CompressedImageField

class UserProfileForm(forms.ModelForm):
    profile_picture = CompressedImageField(
        label='Profile Picture',
        help_text='Upload a profile picture (max 500KB)',
        compression_options={
            'maxSizeKB': 500,
            'quality': 0.85,
            'maxWidth': 800,
            'maxHeight': 800,
        }
    )
    
    cover_image = CompressedImageField(
        label='Cover Image',
        help_text='Upload a cover image (max 1MB)',
        required=False,
        compression_options={
            'maxSizeKB': 1024,
            'quality': 0.8,
            'maxWidth': 1200,
            'maxHeight': 400,
        }
    )
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_image', 'bio']
```

```html
<!-- templates/profile_edit.html -->
{% extends 'base.html' %}
{% load static %}
{% load image_compression %}

{% block extra_css %}
    {% compression_styles %}
{% endblock %}

{% block extra_js %}
    {% compression_scripts %}
{% endblock %}

{% block content %}
<div class="container">
    <h2>Edit Profile</h2>
    
    <form method="post" enctype="multipart/form-data" class="profile-form">
        {% csrf_token %}
        
        <div class="form-group">
            <label>{{ form.profile_picture.label }}</label>
            {{ form.profile_picture }}
            {% if form.profile_picture.help_text %}
                <small class="form-text">{{ form.profile_picture.help_text }}</small>
            {% endif %}
            {{ form.profile_picture.errors }}
        </div>
        
        <div class="form-group">
            <label>{{ form.cover_image.label }}</label>
            {{ form.cover_image }}
            {% if form.cover_image.help_text %}
                <small class="form-text">{{ form.cover_image.help_text }}</small>
            {% endif %}
            {{ form.cover_image.errors }}
        </div>
        
        <div class="form-group">
            <label>{{ form.bio.label }}</label>
            {{ form.bio }}
        </div>
        
        <button type="submit" class="btn btn-primary">Save Profile</button>
    </form>
</div>
{% endblock %}
```

### 2. Event Creation Form

```python
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EventForm

def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    
    return render(request, 'events/create.html', {'form': form})
```

### 3. AJAX Upload with Progress

```html
<form id="uploadForm" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" id="imageInput" name="image" accept="image/*">
    <div id="progressContainer" style="display: none;">
        <div class="progress-bar">
            <div id="progressBar" class="progress-fill"></div>
        </div>
        <div id="progressText">Ready...</div>
    </div>
    <div id="result"></div>
</form>

<script>
const compressor = new ImageCompressor({
    maxSizeKB: 1024,
    quality: 0.8,
    onProgress: (percentage, message) => {
        document.getElementById('progressContainer').style.display = 'block';
        document.getElementById('progressBar').style.width = percentage + '%';
        document.getElementById('progressText').textContent = message;
    },
    onSuccess: async (compressedFile, stats) => {
        document.getElementById('progressText').textContent = 'Uploading...';
        
        const formData = new FormData();
        formData.append('image', compressedFile);
        formData.append('csrfmiddlewaretoken', getCSRFToken());
        
        try {
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                document.getElementById('result').innerHTML = 
                    `<div class="alert alert-success">Upload successful!</div>`;
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (error) {
            document.getElementById('result').innerHTML = 
                `<div class="alert alert-error">Upload failed: ${error.message}</div>`;
        } finally {
            document.getElementById('progressContainer').style.display = 'none';
        }
    },
    onError: (error) => {
        document.getElementById('result').innerHTML = 
            `<div class="alert alert-error">Compression failed: ${error.message}</div>`;
        document.getElementById('progressContainer').style.display = 'none';
    }
});

compressor.init('#imageInput');

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
</script>
```

## Troubleshooting

### Common Issues

1. **Images not compressing**
   - Check if JavaScript is enabled
   - Verify file types are supported
   - Check browser console for errors

2. **File size validation errors**
   - Ensure compression is working properly
   - Check if server-side validation matches client-side settings
   - Verify file size limits are reasonable

3. **Preview not showing**
   - Check if `enablePreview` is set to `true`
   - Verify image file is valid
   - Check for CSS conflicts

4. **Upload failures**
   - Verify CSRF token is included
   - Check file permissions
   - Ensure proper form encoding (`multipart/form-data`)

### Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+
- ⚠️ Internet Explorer: Not supported (requires polyfills)

### Performance Considerations

- **Large images**: Compression may take time for very large images
- **Memory usage**: Browser memory usage increases during compression
- **Multiple files**: Process files sequentially to avoid memory issues
- **Mobile devices**: Consider lower quality settings for mobile

## API Reference

### ImageCompressor Class

```javascript
const compressor = new ImageCompressor(options);
```

#### Methods

- `init(inputElement, options)` - Initialize with file input
- `processFile(file)` - Compress a single file
- `reset()` - Reset compressor state
- `updateConfig(newConfig)` - Update configuration
- `getCompressionInfo()` - Get compression statistics

#### Static Methods

- `ImageCompressor.compress(file, options)` - One-time compression

### Django Classes

- `CompressedImageField` - Django form field with compression
- `CompressedImageWidget` - Django widget for file input
- `ImageCompressionMixin` - Mixin for form classes
- `ImageCompressionService` - Utility service class

### Template Tags

- `{% compression_scripts %}` - Include JS files
- `{% compression_styles %}` - Include CSS files
- `{% compression_config %}` - Generate JS config
- `{% image_compression_widget %}` - Render widget

## Support and Updates

For support, bug reports, or feature requests, please contact the NarraPro development team.

### Version History

- **v1.0.0** - Initial release with full functionality
- Comprehensive client-side compression
- Django integration
- Template tags and widgets
- Mobile responsive design
- Dark mode support

---

**NarraPro Development Team**  
*Making image uploads fast and efficient*
