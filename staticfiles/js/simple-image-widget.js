/**
 * Simple Image Widget with Cropping
 * A simplified version that works reliably with Django forms
 */

(function() {
    'use strict';

    class SimpleImageWidget {
        constructor(element, options = {}) {
            this.element = element;
            this.options = {
                aspectRatio: options.aspectRatio || 1,
                maxSizeKB: options.maxSizeKB || 1024,
                outputWidth: options.outputWidth || 800,
                ...options
            };

            this.originalInput = null;
            this.cropper = null;
            this.currentFile = null;

            this.init();
        }

        init() {
            this.findFileInput();
            if (!this.originalInput) {
                console.warn('No file input found in widget');
                return;
            }

            this.setupCropper();
            this.attachEventListeners();
            this.createUI();
        }

        findFileInput() {
            this.originalInput = this.element.querySelector('input[type="file"]');
        }

        setupCropper() {
            const modalId = `cropper_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

            this.cropper = new ImageCropper({
                aspectRatio: this.options.aspectRatio,
                maxSizeKB: this.options.maxSizeKB,
                outputWidth: this.options.outputWidth,
                modalId: modalId,
                onCrop: (croppedFile) => this.handleCroppedFile(croppedFile),
                onCancel: () => this.handleCropCancel(),
                onError: (error) => this.showError(error.message)
            });
        }

        createUI() {
            // Create a simple drop zone
            const dropZone = document.createElement('div');
            dropZone.className = 'simple-drop-zone';
            dropZone.innerHTML = `
                <div class="drop-content">
                    <i class="fas fa-cloud-upload-alt fa-2x mb-2"></i>
                    <p>Click to upload or drag image here</p>
                    <small class="text-muted">
                        ${this.getAspectRatioText()} • Max ${Math.round(this.options.maxSizeKB / 1024 * 10) / 10}MB
                    </small>
                </div>
            `;

            // Insert before the original input and hide it
            this.originalInput.parentNode.insertBefore(dropZone, this.originalInput);
            this.originalInput.style.display = 'none';

            // Set up click handler
            dropZone.addEventListener('click', () => {
                this.originalInput.click();
            });

            this.dropZone = dropZone;
        }

        attachEventListeners() {
            this.originalInput.addEventListener('change', (e) => {
                if (e.target.files && e.target.files[0]) {
                    this.processFile(e.target.files[0]);
                }
            });
        }

        processFile(file) {
            this.currentFile = file;

            // Validate file
            if (!this.validateFile(file)) {
                return;
            }

            // Open cropper
            this.cropper.open(file);
        }

        validateFile(file) {
            const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

            if (!allowedTypes.includes(file.type)) {
                this.showError('Please upload a valid image file (JPG, PNG, GIF, or WebP)');
                return false;
            }

            if (file.size > 50 * 1024 * 1024) { // 50MB limit
                this.showError('File size must be less than 50MB');
                return false;
            }

            return true;
        }

        handleCroppedFile(croppedFile) {
            try {
                // Update the original input with the cropped file
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(croppedFile);
                this.originalInput.files = dataTransfer.files;

                // Show success message
                this.showSuccess(croppedFile);

                console.log('Image processed successfully:', {
                    name: croppedFile.name,
                    size: croppedFile.size,
                    type: croppedFile.type
                });
            } catch (error) {
                console.error('Error updating file input:', error);
                this.showError('Failed to process the image');
            }
        }

        handleCropCancel() {
            // Reset the file input
            this.originalInput.value = '';
            this.hideMessages();
        }

        showSuccess(file) {
            this.hideMessages();

            const successDiv = document.createElement('div');
            successDiv.className = 'image-success mt-2';
            successDiv.innerHTML = `
                <div class="alert alert-success d-flex align-items-center">
                    <i class="fas fa-check-circle me-2"></i>
                    <div>
                        <strong>Image ready:</strong> ${file.name}
                        (${this.formatFileSize(file.size)})
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-success ms-auto remove-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            this.element.appendChild(successDiv);

            // Add remove button handler
            successDiv.querySelector('.remove-btn').addEventListener('click', () => {
                this.originalInput.value = '';
                this.hideMessages();
            });
        }

        showError(message) {
            this.hideMessages();

            const errorDiv = document.createElement('div');
            errorDiv.className = 'image-error mt-2';
            errorDiv.innerHTML = `
                <div class="alert alert-danger d-flex align-items-center">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <span>${message}</span>
                    <button type="button" class="btn btn-sm btn-outline-danger ms-auto close-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            this.element.appendChild(errorDiv);

            // Add close button handler
            errorDiv.querySelector('.close-btn').addEventListener('click', () => {
                this.hideMessages();
            });
        }

        hideMessages() {
            const messages = this.element.querySelectorAll('.image-success, .image-error');
            messages.forEach(msg => msg.remove());
        }

        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        getAspectRatioText() {
            if (this.options.aspectRatio === 1) return '1:1 Square';
            if (this.options.aspectRatio === 4) return '4:1 Banner';
            return `${this.options.aspectRatio}:1`;
        }

        destroy() {
            if (this.cropper) {
                this.cropper.destroy();
            }
            this.hideMessages();
            if (this.dropZone) {
                this.dropZone.remove();
            }
            if (this.originalInput) {
                this.originalInput.style.display = '';
            }
        }
    }

    // Initialize widgets
    function initializeSimpleWidgets() {
        // Profile picture widgets (1:1 ratio, 1MB)
        const profileWidgets = document.querySelectorAll('.enhanced-image-widget[data-type="profile"]');
        profileWidgets.forEach(widget => {
            new SimpleImageWidget(widget, {
                aspectRatio: 1,
                maxSizeKB: 1024,
                outputWidth: 800
            });
        });

        // Cover image widgets (4:1 ratio, 4MB)
        const coverWidgets = document.querySelectorAll('.enhanced-image-widget[data-type="cover"]');
        coverWidgets.forEach(widget => {
            new SimpleImageWidget(widget, {
                aspectRatio: 4,
                maxSizeKB: 4096,
                outputWidth: 1200
            });
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeSimpleWidgets);
    } else {
        initializeSimpleWidgets();
    }

    // Export for global access
    window.SimpleImageWidget = SimpleImageWidget;
})();