"""
Image Compression Template Tags
Django template tags for easy integration of image compression functionality

@version 1.0.0
@author NarraPro Development Team
"""

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
import json

register = template.Library()


@register.inclusion_tag('widgets/compressed_image_widget.html', takes_context=True)
def compressed_image_field(context, field, **kwargs):
    """
    Render a compressed image field with customizable options
    
    Usage:
        {% compressed_image_field form.image_field max_size_kb=512 quality=0.9 %}
    
    Args:
        field: Django form field
        **kwargs: Compression options (max_size_kb, quality, max_width, etc.)
    """
    # Default compression options
    compression_options = {
        'maxSizeKB': kwargs.get('max_size_kb', 1024),
        'quality': kwargs.get('quality', 0.8),
        'maxWidth': kwargs.get('max_width', 1920),
        'maxHeight': kwargs.get('max_height', 1080),
        'outputFormat': kwargs.get('output_format', 'auto'),
        'enablePreview': kwargs.get('enable_preview', True),
        'autoCompress': kwargs.get('auto_compress', True),
    }
    
    return {
        'field': field,
        'compression_options': json.dumps(compression_options),
        'widget_attrs': kwargs.get('attrs', {}),
        'request': context.get('request'),
    }


@register.simple_tag
def compression_scripts():
    """
    Include required JavaScript files for image compression
    
    Usage:
        {% compression_scripts %}
    """
    return mark_safe("""
        <script src="/static/js/image-compressor.js"></script>
        <script src="/static/js/compressed-image-widget.js"></script>
    """)


@register.simple_tag
def compression_styles():
    """
    Include required CSS files for image compression
    
    Usage:
        {% compression_styles %}
    """
    return mark_safe("""
        <link rel="stylesheet" href="/static/css/compressed-image-widget.css">
    """)


@register.simple_tag
def compression_config(max_size_kb=1024, quality=0.8, **kwargs):
    """
    Generate JavaScript configuration object for image compression
    
    Usage:
        <script>
            const config = {% compression_config max_size_kb=512 quality=0.9 %};
            const compressor = new ImageCompressor(config);
        </script>
    
    Args:
        max_size_kb: Maximum file size in KB (default: 1024)
        quality: Compression quality 0.1-1.0 (default: 0.8)
        **kwargs: Additional compression options
    """
    config = {
        'maxSizeKB': max_size_kb,
        'quality': quality,
        'maxWidth': kwargs.get('max_width', 1920),
        'maxHeight': kwargs.get('max_height', 1080),
        'outputFormat': kwargs.get('output_format', 'auto'),
        'enablePreview': kwargs.get('enable_preview', True),
        'autoCompress': kwargs.get('auto_compress', True),
        'allowedTypes': kwargs.get('allowed_types', [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp'
        ]),
    }
    
    return mark_safe(json.dumps(config))


@register.filter
def file_size_format(bytes_size):
    """
    Format file size in human-readable format
    
    Usage:
        {{ file.size|file_size_format }}
    """
    if not bytes_size:
        return '0 B'
    
    try:
        bytes_size = int(bytes_size)
    except (ValueError, TypeError):
        return '0 B'
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.1f} PB"


@register.filter
def compression_ratio(original_size, compressed_size):
    """
    Calculate compression ratio as percentage
    
    Usage:
        {{ original_size|compression_ratio:compressed_size }}
    """
    try:
        original = float(original_size or 0)
        compressed = float(compressed_size or 0)
        
        if original == 0:
            return '0%'
        
        ratio = (1 - compressed / original) * 100
        return f"{ratio:.1f}%"
    
    except (ValueError, TypeError, ZeroDivisionError):
        return '0%'


@register.simple_tag(takes_context=True)
def image_compression_widget(context, field_name, **options):
    """
    Render a complete image compression widget with form integration
    
    Usage:
        {% image_compression_widget 'profile_picture' max_size_kb=500 quality=0.85 %}
    
    Args:
        field_name: Name of the form field
        **options: Widget configuration options
    """
    form = context.get('form')
    if not form or field_name not in form.fields:
        return ''
    
    field = form[field_name]
    
    # Merge default options with provided options
    widget_options = {
        'maxSizeKB': options.get('max_size_kb', 1024),
        'quality': options.get('quality', 0.8),
        'maxWidth': options.get('max_width', 1920),
        'maxHeight': options.get('max_height', 1080),
        'outputFormat': options.get('output_format', 'auto'),
        'enablePreview': options.get('enable_preview', True),
        'autoCompress': options.get('auto_compress', True),
        'dropContainer': options.get('drop_container', True),
    }
    
    # Generate widget HTML
    widget_id = f"compressed-widget-{field_name}"
    
    html = format_html("""
        <div class="compressed-image-widget" id="{widget_id}">
            <script type="application/json" class="compression-options">{options}</script>
            {field_html}
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                if (window.CompressedImageWidget) {{
                    const widget = document.getElementById('{widget_id}');
                    const options = JSON.parse(widget.querySelector('.compression-options').textContent);
                    new CompressedImageWidget(widget, options);
                }}
            }});
        </script>
    """,
        widget_id=widget_id,
        options=json.dumps(widget_options),
        field_html=field.as_widget(attrs={'class': 'compressed-image-input'})
    )
    
    return mark_safe(html)


@register.inclusion_tag('widgets/compression_preview.html')
def compression_preview(image_field, show_stats=True):
    """
    Show preview and compression statistics for uploaded images
    
    Usage:
        {% compression_preview form.image_field show_stats=True %}
    """
    return {
        'field': image_field,
        'show_stats': show_stats,
        'has_value': bool(image_field.value),
    }


@register.simple_tag
def compression_validation_script(field_name, max_size_kb=1024):
    """
    Generate client-side validation script for image fields
    
    Usage:
        {% compression_validation_script 'profile_picture' max_size_kb=500 %}
    """
    script = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const field = document.querySelector('[name="{field_name}"]');
                if (field) {{
                    field.addEventListener('change', function(e) {{
                        const file = e.target.files[0];
                        if (file) {{
                            const sizeKB = file.size / 1024;
                            if (sizeKB > {max_size_kb}) {{
                                alert(`File size (${{sizeKB.toFixed(1)}}KB) exceeds maximum allowed size ({max_size_kb}KB). Please compress the image.`);
                                e.target.value = '';
                                return false;
                            }}
                        }}
                    }});
                }}
            }});
        </script>
    """
    
    return mark_safe(script)


@register.simple_tag
def compression_progress_indicator():
    """
    Generate a reusable compression progress indicator
    
    Usage:
        {% compression_progress_indicator %}
    """
    html = """
        <div class="compression-progress-indicator" style="display: none;">
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <div class="progress-text">Compressing...</div>
        </div>
    """
    
    return mark_safe(html)
