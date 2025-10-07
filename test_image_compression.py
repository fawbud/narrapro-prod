#!/usr/bin/env python
"""
Image Compression Module Test Script
Simple test to verify the image compression module is working correctly

Run this script to test the basic functionality:
python test_image_compression.py

@version 1.0.0
@author NarraPro Development Team
"""

import os
import sys
import django
from django.conf import settings
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-key-for-compression-module',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'narrapro',
        ],
        USE_TZ=True,
    )
    django.setup()

def create_test_image(width=800, height=600, format='JPEG'):
    """Create a test image for compression testing"""
    # Create a simple test image
    img = Image.new('RGB', (width, height), color='red')
    
    # Add some detail to make compression meaningful
    for i in range(0, width, 50):
        for j in range(0, height, 50):
            # Add alternating colored squares
            color = 'blue' if (i + j) % 100 == 0 else 'green'
            img.paste(color, (i, j, min(i+25, width), min(j+25, height)))
    
    # Save to BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format=format, quality=95)
    img_buffer.seek(0)
    
    return img_buffer.getvalue()

def test_basic_functionality():
    """Test basic functionality of the image compression module"""
    print("🧪 Testing Image Compression Module")
    print("=" * 50)
    
    try:
        from narrapro.image_compression import (
            CompressedImageField,
            CompressedImageWidget, 
            validate_compressed_image,
            get_image_info,
            ImageCompressionService
        )
        print("✅ Successfully imported image compression modules")
    except ImportError as e:
        print(f"❌ Failed to import modules: {e}")
        return False
    
    # Test 1: Create a test image
    print("\n📷 Creating test image...")
    test_image_data = create_test_image(1200, 800, 'JPEG')
    original_size = len(test_image_data)
    print(f"✅ Created test image: {original_size} bytes ({original_size/1024:.1f}KB)")
    
    # Test 2: Create uploaded file
    print("\n📤 Creating uploaded file...")
    uploaded_file = SimpleUploadedFile(
        "test_image.jpg",
        test_image_data,
        content_type="image/jpeg"
    )
    print(f"✅ Created uploaded file: {uploaded_file.name}")
    
    # Test 3: Test image info function
    print("\n📊 Testing image info extraction...")
    image_info = get_image_info(uploaded_file)
    if image_info:
        print(f"✅ Image info: {image_info['width']}x{image_info['height']}, "
              f"{image_info['format']}, {image_info['file_size_kb']:.1f}KB")
    else:
        print("❌ Failed to get image info")
        return False
    
    # Test 4: Test validation
    print("\n🔍 Testing image validation...")
    try:
        # This should pass for a reasonable size
        validate_compressed_image(uploaded_file, max_size_kb=2048)
        print("✅ Image validation passed (2MB limit)")
        
        # Reset file pointer
        uploaded_file.seek(0)
        
        # This should fail for a small limit
        try:
            validate_compressed_image(uploaded_file, max_size_kb=10)
            print("❌ Validation should have failed for 10KB limit")
        except Exception:
            print("✅ Image validation correctly failed for 10KB limit")
            
    except Exception as e:
        print(f"❌ Image validation error: {e}")
        return False
    
    # Test 5: Test server-side compression
    print("\n🗜️ Testing server-side compression...")
    uploaded_file.seek(0)
    try:
        compressed_file = ImageCompressionService.server_side_compress(
            uploaded_file, 
            max_size_kb=500, 
            quality=75
        )
        
        if compressed_file:
            compressed_size = compressed_file.size
            compression_ratio = (1 - compressed_size / original_size) * 100
            print(f"✅ Server-side compression successful:")
            print(f"   Original: {original_size/1024:.1f}KB")
            print(f"   Compressed: {compressed_size/1024:.1f}KB")
            print(f"   Compression: {compression_ratio:.1f}%")
        else:
            print("❌ Server-side compression failed")
            return False
            
    except Exception as e:
        print(f"❌ Server-side compression error: {e}")
        return False
    
    # Test 6: Test compression statistics
    print("\n📈 Testing compression statistics...")
    stats = ImageCompressionService.get_compression_stats(original_size, compressed_file.size)
    if stats:
        print(f"✅ Compression stats:")
        print(f"   Compression ratio: {stats['compression_percentage']:.1f}%")
        print(f"   Size saved: {stats['size_saved_kb']:.1f}KB")
    else:
        print("❌ Failed to get compression stats")
        return False
    
    # Test 7: Test form field creation
    print("\n📝 Testing form field creation...")
    try:
        field = CompressedImageField(
            compression_options={
                'maxSizeKB': 500,
                'quality': 0.8,
            }
        )
        print("✅ CompressedImageField created successfully")
        
        widget = CompressedImageWidget(
            compression_options={
                'maxSizeKB': 1024,
                'quality': 0.85,
            }
        )
        print("✅ CompressedImageWidget created successfully")
        
    except Exception as e:
        print(f"❌ Form field creation error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Image compression module is working correctly.")
    print("\n📚 Next steps:")
    print("1. Read the integration guide: IMAGE_COMPRESSION_INTEGRATION_GUIDE.md")
    print("2. Check sample implementations: sample_image_compression_forms.py")
    print("3. Add compression to your Django forms")
    print("4. Include the JavaScript and CSS files in your templates")
    
    return True

def test_javascript_files():
    """Test if JavaScript files are present and contain expected content"""
    print("\n🔧 Testing JavaScript files...")
    
    js_files = [
        'static/js/image-compressor.js',
        'static/js/compressed-image-widget.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'ImageCompressor' in content:
                    print(f"✅ {js_file} exists and contains ImageCompressor")
                else:
                    print(f"⚠️ {js_file} exists but may be incomplete")
        else:
            print(f"❌ {js_file} not found")
    
    # Test CSS file
    css_file = 'static/css/compressed-image-widget.css'
    if os.path.exists(css_file):
        print(f"✅ {css_file} exists")
    else:
        print(f"❌ {css_file} not found")

def print_usage_example():
    """Print a simple usage example"""
    print("\n" + "=" * 50)
    print("📖 QUICK USAGE EXAMPLE")
    print("=" * 50)
    
    example_code = '''
# 1. In your forms.py:
from narrapro.image_compression import CompressedImageField

class MyForm(forms.ModelForm):
    image = CompressedImageField(
        compression_options={
            'maxSizeKB': 500,    # 500KB max
            'quality': 0.8,      # 80% quality
        }
    )

# 2. In your template:
{% load static %}
{% load image_compression %}

{% block extra_css %}
    {% compression_styles %}
{% endblock %}

{% block extra_js %}
    {% compression_scripts %}
{% endblock %}

# 3. In your form:
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.image }}
    <button type="submit">Upload</button>
</form>
'''
    
    print(example_code)

if __name__ == '__main__':
    print("🚀 Starting Image Compression Module Tests...")
    
    success = test_basic_functionality()
    test_javascript_files()
    
    if success:
        print_usage_example()
        print("\n🎉 Image Compression Module is ready to use!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
