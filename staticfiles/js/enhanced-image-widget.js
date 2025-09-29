/**
 * Enhanced Image Widget with Cropping and Compression
 * Integrates ImageCropper and ImageCompressor for seamless user experience
 *
 * @version 1.0.0
 * @author NarraPro Development Team
 */

(function() {
    'use strict';

    class EnhancedImageWidget {
        constructor(element, options = {}) {
            this.element = element;
            this.options = {
                // Cropping options
                aspectRatio: options.aspectRatio || 1, // 1:1 for profile, 4:1 for cover
                outputWidth: options.outputWidth || 800,
                enableCropping: options.enableCropping !== false,

                // Compression options
                maxSizeKB: options.maxSizeKB || 1024, // 1MB for profile, 4MB for cover
                quality: options.quality || 0.8,

                // Widget options
                showPreview: options.showPreview !== false,
                allowedTypes: options.allowedTypes || ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],

                // Callbacks
                onCrop: options.onCrop || null,
                onCompress: options.onCompress || null,
                onError: options.onError || null,

                ...options
            };

            this.originalInput = null;
            this.cropper = null;
            this.compressor = null;
            this.currentFile = null;
            this.processedFile = null;
            this.previewContainer = null;
            this.dropZone = null;
            this.progressContainer = null;

            this.init();
        }

        init() {
            this.setupElements();
            this.setupCropper();
            this.setupCompressor();
            this.attachEventListeners();
        }

        setupElements() {
            // Find the original file input
            this.originalInput = this.element.querySelector('input[type="file"]');
            if (!this.originalInput) {
                console.error('File input not found in enhanced image widget');
                return;
            }

            // Add classes for identification
            this.element.classList.add('enhanced-image-widget');
            this.originalInput.classList.add('enhanced-image-input');

            // Create UI elements
            this.createDropZone();
            this.createPreviewContainer();
            this.createProgressContainer();
            this.createInfoContainer();

            // Hide original input
            this.originalInput.style.display = 'none';
        }

        createDropZone() {
            this.dropZone = document.createElement('div');
            this.dropZone.className = 'enhanced-drop-zone';
            this.dropZone.innerHTML = `
                <div class="drop-zone-content">
                    <div class="drop-zone-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="drop-zone-text">
                        <p><strong>Drop image here</strong> or click to browse</p>
                        <p class="drop-zone-subtext">
                            ${this.options.enableCropping ? 'Image will be cropped and compressed automatically' : 'Image will be compressed automatically'}
                        </p>
                        <div class="drop-zone-specs">
                            <small class="text-muted">
                                Max size: ${this.formatFileSize(this.options.maxSizeKB * 1024)} •
                                Ratio: ${this.getAspectRatioText()} •
                                Formats: JPG, PNG, GIF, WebP
                            </small>
                        </div>
                    </div>
                </div>
            `;

            // Insert drop zone before original input
            this.originalInput.parentNode.insertBefore(this.dropZone, this.originalInput);
        }

        createPreviewContainer() {
            this.previewContainer = document.createElement('div');
            this.previewContainer.className = 'enhanced-preview-container';
            this.previewContainer.style.display = 'none';
            this.element.appendChild(this.previewContainer);
        }

        createProgressContainer() {
            this.progressContainer = document.createElement('div');
            this.progressContainer.className = 'enhanced-progress-container';
            this.progressContainer.innerHTML = `
                <div class="progress-header">
                    <span class="progress-title">Processing Image...</span>
                    <span class="progress-percentage">0%</span>
                </div>
                <div class="progress-bar-wrapper">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
                <div class="progress-message">Ready to process...</div>
            `;
            this.progressContainer.style.display = 'none';
            this.element.appendChild(this.progressContainer);
        }

        createInfoContainer() {
            this.infoContainer = document.createElement('div');
            this.infoContainer.className = 'enhanced-info-container';
            this.infoContainer.style.display = 'none';
            this.element.appendChild(this.infoContainer);
        }

        setupCropper() {
            if (!this.options.enableCropping) return;

            this.cropper = new ImageCropper({
                aspectRatio: this.options.aspectRatio,
                maxSizeKB: this.options.maxSizeKB,
                quality: this.options.quality,
                outputWidth: this.options.outputWidth,
                modalId: `imageCropper_${Date.now()}`,
                onCrop: (croppedFile) => this.handleCroppedFile(croppedFile),
                onCancel: () => this.handleCropCancel(),
                onError: (error) => this.handleError(error)
            });
        }

        setupCompressor() {
            this.compressor = new ImageCompressor({
                maxSizeKB: this.options.maxSizeKB,
                quality: this.options.quality,
                allowedTypes: this.options.allowedTypes,
                onProgress: (percentage, message) => this.updateProgress(percentage, message),
                onSuccess: (file, stats) => this.handleCompressedFile(file, stats),
                onError: (error) => this.handleError(error)
            });
        }

        attachEventListeners() {
            // Drop zone click handler
            this.dropZone.addEventListener('click', () => {
                this.originalInput.click();
            });

            // File input change handler
            this.originalInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.processFile(e.target.files[0]);
                }
            });

            // Drag and drop
            this.setupDragDrop();

            // Form submission handler
            const form = this.element.closest('form');
            if (form) {
                form.addEventListener('submit', (e) => this.handleFormSubmit(e));
            }
        }

        setupDragDrop() {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                this.dropZone.addEventListener(eventName, this.preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                this.dropZone.addEventListener(eventName, () => {
                    this.dropZone.classList.add('drag-over');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                this.dropZone.addEventListener(eventName, () => {
                    this.dropZone.classList.remove('drag-over');
                }, false);
            });

            this.dropZone.addEventListener('drop', (e) => {
                const files = Array.from(e.dataTransfer.files);
                if (files.length > 0) {
                    this.processFile(files[0]);
                }
            }, false);
        }

        preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        async processFile(file) {
            try {
                this.currentFile = file;
                this.hideError();
                this.validateFile(file);

                if (this.options.enableCropping) {
                    // Show cropping modal
                    this.cropper.open(file);
                } else {
                    // Direct compression
                    this.showProgress();
                    await this.compressor.processFile(file);
                }
            } catch (error) {
                this.handleError(error);
            }
        }

        validateFile(file) {
            if (!this.options.allowedTypes.includes(file.type)) {
                throw new Error(`File type ${file.type} is not allowed. Please use: ${this.options.allowedTypes.join(', ')}`);
            }

            const maxFileSizeMB = 50; // 50MB max before processing
            if (file.size > maxFileSizeMB * 1024 * 1024) {
                throw new Error(`File size exceeds maximum allowed size of ${maxFileSizeMB}MB`);
            }
        }

        handleCroppedFile(croppedFile) {
            this.processedFile = croppedFile;
            this.updateFileInput(croppedFile);
            this.showPreview(croppedFile);
            this.showSuccess('Image cropped and compressed successfully!');

            if (this.options.onCrop) {
                this.options.onCrop(croppedFile);
            }
        }

        handleCropCancel() {
            this.resetWidget();
        }

        handleCompressedFile(compressedFile, stats) {
            this.hideProgress();
            this.processedFile = compressedFile;
            this.updateFileInput(compressedFile);
            this.showPreview(compressedFile);
            this.showCompressionInfo(stats);

            if (this.options.onCompress) {
                this.options.onCompress(compressedFile, stats);
            }
        }

        updateFileInput(file) {
            try {
                // Create a new FileList with the processed file
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                this.originalInput.files = dataTransfer.files;

                // Trigger change event for form validation
                const changeEvent = new Event('change', {
                    bubbles: true,
                    cancelable: true
                });
                this.originalInput.dispatchEvent(changeEvent);

                console.log('File input updated:', {
                    filename: file.name,
                    size: file.size,
                    type: file.type
                });
            } catch (error) {
                console.error('Error updating file input:', error);
                this.handleError(new Error('Failed to update file input: ' + error.message));
            }
        }

        showPreview(file) {
            if (!this.options.showPreview) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                this.previewContainer.innerHTML = `
                    <div class="preview-header">
                        <h6><i class="fas fa-image me-2"></i>Image Preview</h6>
                        <button type="button" class="btn btn-sm btn-outline-danger remove-image" title="Remove image">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <div class="preview-image-wrapper">
                        <img src="${e.target.result}" alt="Preview" class="preview-image"
                             style="aspect-ratio: ${this.options.aspectRatio}; object-fit: cover;" />
                    </div>
                    <div class="preview-info">
                        <div class="file-details">
                            <div class="file-name">${file.name}</div>
                            <div class="file-specs">
                                <span class="file-size">${this.formatFileSize(file.size)}</span>
                                <span class="file-type">${file.type.split('/')[1].toUpperCase()}</span>
                            </div>
                        </div>
                    </div>
                `;

                this.previewContainer.style.display = 'block';
                this.dropZone.style.display = 'none';

                // Add remove button handler
                const removeButton = this.previewContainer.querySelector('.remove-image');
                removeButton.addEventListener('click', () => this.removeImage());
            };
            reader.readAsDataURL(file);
        }

        showProgress() {
            this.progressContainer.style.display = 'block';
            this.dropZone.style.display = 'none';
            this.previewContainer.style.display = 'none';
        }

        hideProgress() {
            this.progressContainer.style.display = 'none';
        }

        updateProgress(percentage, message) {
            const progressFill = this.progressContainer.querySelector('.progress-fill');
            const progressPercentage = this.progressContainer.querySelector('.progress-percentage');
            const progressMessage = this.progressContainer.querySelector('.progress-message');

            progressFill.style.width = `${percentage}%`;
            progressPercentage.textContent = `${Math.round(percentage)}%`;
            progressMessage.textContent = message;
        }

        showCompressionInfo(stats) {
            const compressionRatio = (stats.compressionRatio * 100).toFixed(1);
            const originalSizeMB = (stats.originalSize / (1024 * 1024)).toFixed(2);
            const compressedSizeMB = (stats.compressedSize / (1024 * 1024)).toFixed(2);

            this.infoContainer.innerHTML = `
                <div class="compression-results">
                    <h6><i class="fas fa-chart-line me-2"></i>Compression Results</h6>
                    <div class="results-grid">
                        <div class="result-item">
                            <span class="result-label">Original Size:</span>
                            <span class="result-value">${this.formatFileSize(stats.originalSize)}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Final Size:</span>
                            <span class="result-value">${this.formatFileSize(stats.compressedSize)}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Size Reduction:</span>
                            <span class="result-value success">${compressionRatio}%</span>
                        </div>
                    </div>
                </div>
            `;

            this.infoContainer.style.display = 'block';
        }

        showSuccess(message) {
            this.infoContainer.innerHTML = `
                <div class="success-message">
                    <div class="alert alert-success d-flex align-items-center">
                        <i class="fas fa-check-circle me-2"></i>
                        <span>${message}</span>
                    </div>
                </div>
            `;
            this.infoContainer.style.display = 'block';
        }

        handleError(error) {
            this.hideProgress();
            this.showError(error.message || 'An error occurred while processing the image.');

            if (this.options.onError) {
                this.options.onError(error);
            }
        }

        showError(message) {
            let errorContainer = this.element.querySelector('.enhanced-error-container');
            if (!errorContainer) {
                errorContainer = document.createElement('div');
                errorContainer.className = 'enhanced-error-container';
                this.element.appendChild(errorContainer);
            }

            errorContainer.innerHTML = `
                <div class="alert alert-danger d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <span>${message}</span>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger error-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            errorContainer.style.display = 'block';
            this.dropZone.style.display = 'block';
            this.previewContainer.style.display = 'none';

            // Add close button handler
            const closeButton = errorContainer.querySelector('.error-close');
            closeButton.addEventListener('click', () => this.hideError());
        }

        hideError() {
            const errorContainer = this.element.querySelector('.enhanced-error-container');
            if (errorContainer) {
                errorContainer.style.display = 'none';
            }
        }

        removeImage() {
            this.resetWidget();
        }

        resetWidget() {
            // Clear file inputs
            this.originalInput.value = '';
            this.currentFile = null;
            this.processedFile = null;

            // Reset UI
            this.previewContainer.style.display = 'none';
            this.infoContainer.style.display = 'none';
            this.hideProgress();
            this.hideError();
            this.dropZone.style.display = 'block';

            // Reset compressor
            if (this.compressor) {
                this.compressor.reset();
            }
        }

        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';

            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));

            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        getAspectRatioText() {
            if (this.options.aspectRatio === 1) return '1:1 (Square)';
            if (this.options.aspectRatio === 4) return '4:1 (Banner)';
            if (this.options.aspectRatio === 1.33) return '4:3 (Standard)';
            if (this.options.aspectRatio === 1.78) return '16:9 (Widescreen)';
            return `${this.options.aspectRatio}:1`;
        }

        handleFormSubmit(e) {
            // Additional validation before form submission
            if (this.compressor && this.compressor.isProcessing) {
                e.preventDefault();
                alert('Please wait for image processing to complete.');
                return false;
            }

            return true;
        }

        // Public API methods
        getProcessedFile() {
            return this.processedFile;
        }

        getCurrentFile() {
            return this.currentFile;
        }

        updateOptions(newOptions) {
            this.options = { ...this.options, ...newOptions };

            if (this.cropper) {
                this.cropper.config = { ...this.cropper.config, ...newOptions };
            }

            if (this.compressor) {
                this.compressor.updateConfig(newOptions);
            }
        }

        destroy() {
            if (this.cropper) {
                this.cropper.destroy();
            }

            if (this.compressor) {
                this.compressor.reset();
            }

            // Remove event listeners and clean up
            this.element.classList.remove('enhanced-image-widget');

            // Show original input
            if (this.originalInput) {
                this.originalInput.style.display = '';
            }
        }
    }

    // Initialize widgets when DOM is ready
    function initializeEnhancedWidgets() {
        // Profile picture widgets (1:1 ratio, 1MB)
        const profileWidgets = document.querySelectorAll('.enhanced-image-widget[data-type="profile"]');
        profileWidgets.forEach(widget => {
            new EnhancedImageWidget(widget, {
                aspectRatio: 1,
                maxSizeKB: 1024,
                outputWidth: 800,
                enableCropping: true
            });
        });

        // Cover image widgets (4:1 ratio, 4MB)
        const coverWidgets = document.querySelectorAll('.enhanced-image-widget[data-type="cover"]');
        coverWidgets.forEach(widget => {
            new EnhancedImageWidget(widget, {
                aspectRatio: 4,
                maxSizeKB: 4096,
                outputWidth: 1200,
                enableCropping: true
            });
        });

        // Generic widgets with custom options
        const genericWidgets = document.querySelectorAll('.enhanced-image-widget:not([data-type])');
        genericWidgets.forEach(widget => {
            const optionsScript = widget.querySelector('.widget-options');
            let options = {};

            if (optionsScript) {
                try {
                    options = JSON.parse(optionsScript.textContent);
                } catch (e) {
                    console.warn('Failed to parse widget options:', e);
                }
            }

            new EnhancedImageWidget(widget, options);
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeEnhancedWidgets);
    } else {
        initializeEnhancedWidgets();
    }

    // Re-initialize on dynamic content changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const widgets = node.querySelectorAll('.enhanced-image-widget');
                        widgets.forEach(widget => {
                            if (!widget.dataset.initialized) {
                                // Determine widget type and initialize accordingly
                                const type = widget.dataset.type;
                                let options = {};

                                if (type === 'profile') {
                                    options = {
                                        aspectRatio: 1,
                                        maxSizeKB: 1024,
                                        outputWidth: 800,
                                        enableCropping: true
                                    };
                                } else if (type === 'cover') {
                                    options = {
                                        aspectRatio: 4,
                                        maxSizeKB: 4096,
                                        outputWidth: 1200,
                                        enableCropping: true
                                    };
                                } else {
                                    const optionsScript = widget.querySelector('.widget-options');
                                    if (optionsScript) {
                                        try {
                                            options = JSON.parse(optionsScript.textContent);
                                        } catch (e) {
                                            console.warn('Failed to parse widget options:', e);
                                        }
                                    }
                                }

                                new EnhancedImageWidget(widget, options);
                                widget.dataset.initialized = 'true';
                            }
                        });
                    }
                });
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Export for global access
    window.EnhancedImageWidget = EnhancedImageWidget;
})();