/**
 * Compressed Image Widget JavaScript
 * Handles the integration between Django forms and the ImageCompressor module
 * 
 * @version 1.0.0
 * @author NarraPro Development Team
 */

(function() {
    'use strict';

    class CompressedImageWidget {
        constructor(element, options = {}) {
            this.element = element;
            this.options = options;
            this.compressor = null;
            this.originalInput = null;
            this.compressedInput = null;
            this.previewContainer = null;
            this.progressContainer = null;
            this.infoContainer = null;
            this.dropZone = null;
            
            this.init();
        }

        init() {
            this.setupElements();
            this.setupCompressor();
            this.attachEventListeners();
        }

        setupElements() {
            // Find the original file input
            this.originalInput = this.element.querySelector('.compressed-image-input');
            if (!this.originalInput) {
                console.error('Original file input not found');
                return;
            }

            // Create UI elements
            this.createDropZone();
            this.createPreviewContainer();
            this.createProgressContainer();
            this.createInfoContainer();
            this.createHiddenInput();
        }

        createDropZone() {
            this.dropZone = document.createElement('div');
            this.dropZone.className = 'image-drop-zone';
            this.dropZone.innerHTML = `
                <div class="drop-zone-content">
                    <div class="drop-zone-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <circle cx="8.5" cy="8.5" r="1.5"/>
                            <polyline points="21,15 16,10 5,21"/>
                        </svg>
                    </div>
                    <div class="drop-zone-text">
                        <p><strong>Drop image here</strong> or click to browse</p>
                        <p class="drop-zone-subtext">Images will be automatically compressed</p>
                    </div>
                </div>
            `;

            // Insert drop zone before original input
            this.originalInput.parentNode.insertBefore(this.dropZone, this.originalInput);
            
            // Hide original input
            this.originalInput.style.display = 'none';
        }

        createPreviewContainer() {
            this.previewContainer = document.createElement('div');
            this.previewContainer.className = 'image-preview-container';
            this.previewContainer.style.display = 'none';
            this.element.appendChild(this.previewContainer);
        }

        createProgressContainer() {
            this.progressContainer = document.createElement('div');
            this.progressContainer.className = 'compression-progress';
            this.progressContainer.innerHTML = `
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <div class="progress-text">Ready to compress...</div>
            `;
            this.progressContainer.style.display = 'none';
            this.element.appendChild(this.progressContainer);
        }

        createInfoContainer() {
            this.infoContainer = document.createElement('div');
            this.infoContainer.className = 'compression-info';
            this.infoContainer.style.display = 'none';
            this.element.appendChild(this.infoContainer);
        }

        createHiddenInput() {
            // Create hidden input to store compressed file data
            this.compressedInput = document.createElement('input');
            this.compressedInput.type = 'hidden';
            this.compressedInput.name = this.originalInput.name + '_compressed_data';
            this.element.appendChild(this.compressedInput);
        }

        setupCompressor() {
            this.compressor = new ImageCompressor({
                ...this.options,
                onProgress: (percentage, message) => this.updateProgress(percentage, message),
                onSuccess: (file, stats) => this.handleSuccess(file, stats),
                onError: (error) => this.handleError(error),
                onPreview: (dataUrl, file) => this.showPreview(dataUrl, file)
            });

            // Initialize compressor with drop zone
            this.compressor.setupDragDrop(this.dropZone);
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

            // Form submission handler
            const form = this.element.closest('form');
            if (form) {
                form.addEventListener('submit', (e) => this.handleFormSubmit(e));
            }
        }

        async processFile(file) {
            try {
                this.showProgress();
                this.hideError();
                
                await this.compressor.processFile(file);
            } catch (error) {
                this.handleError(error);
            }
        }

        updateProgress(percentage, message) {
            const progressFill = this.progressContainer.querySelector('.progress-fill');
            const progressText = this.progressContainer.querySelector('.progress-text');
            
            progressFill.style.width = `${percentage}%`;
            progressText.textContent = message;
        }

        showProgress() {
            this.progressContainer.style.display = 'block';
            this.infoContainer.style.display = 'none';
        }

        hideProgress() {
            this.progressContainer.style.display = 'none';
        }

        showPreview(dataUrl, file) {
            this.previewContainer.innerHTML = `
                <div class="preview-header">
                    <h4>Image Preview</h4>
                    <button type="button" class="remove-image" title="Remove image">×</button>
                </div>
                <div class="preview-image">
                    <img src="${dataUrl}" alt="Preview" />
                </div>
                <div class="preview-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                </div>
            `;
            
            this.previewContainer.style.display = 'block';

            // Add remove button handler
            const removeButton = this.previewContainer.querySelector('.remove-image');
            removeButton.addEventListener('click', () => this.removeImage());
        }

        handleSuccess(file, stats) {
            this.hideProgress();
            
            // Update file input with compressed file
            this.updateFileInput(file);
            
            // Show compression info
            this.showCompressionInfo(stats);
            
            // Update preview with compressed file info
            this.updatePreviewInfo(file, stats);
        }

        handleError(error) {
            this.hideProgress();
            this.showError(error.message);
            console.error('Image compression error:', error);
        }

        updateFileInput(compressedFile) {
            // Create a new FileList with the compressed file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(compressedFile);
            this.originalInput.files = dataTransfer.files;

            // Store compressed file data for additional processing if needed
            this.storeCompressedData(compressedFile);
        }

        async storeCompressedData(file) {
            // Convert file to base64 for storage in hidden input
            const reader = new FileReader();
            reader.onload = (e) => {
                const data = {
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    data: e.target.result
                };
                this.compressedInput.value = JSON.stringify(data);
            };
            reader.readAsDataURL(file);
        }

        showCompressionInfo(stats) {
            const compressionRatio = (stats.compressionRatio * 100).toFixed(1);
            const originalSizeMB = (stats.originalSize / (1024 * 1024)).toFixed(2);
            const compressedSizeMB = (stats.compressedSize / (1024 * 1024)).toFixed(2);
            
            this.infoContainer.innerHTML = `
                <div class="compression-stats">
                    <h5>Compression Results</h5>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">Original Size:</span>
                            <span class="stat-value">${originalSizeMB} MB</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Compressed Size:</span>
                            <span class="stat-value">${compressedSizeMB} MB</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Size Reduction:</span>
                            <span class="stat-value">${compressionRatio}%</span>
                        </div>
                    </div>
                </div>
            `;
            
            this.infoContainer.style.display = 'block';
        }

        updatePreviewInfo(file, stats) {
            const previewInfo = this.previewContainer.querySelector('.preview-info');
            if (previewInfo) {
                const compressionRatio = (stats.compressionRatio * 100).toFixed(1);
                previewInfo.innerHTML = `
                    <div class="file-details">
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">${this.formatFileSize(file.size)}</span>
                        <span class="compression-ratio">Reduced by ${compressionRatio}%</span>
                    </div>
                `;
            }
        }

        showError(message) {
            let errorContainer = this.element.querySelector('.compression-error');
            if (!errorContainer) {
                errorContainer = document.createElement('div');
                errorContainer.className = 'compression-error';
                this.element.appendChild(errorContainer);
            }

            errorContainer.innerHTML = `
                <div class="error-message">
                    <span class="error-icon">⚠️</span>
                    <span class="error-text">${message}</span>
                    <button type="button" class="error-close" title="Close">×</button>
                </div>
            `;

            errorContainer.style.display = 'block';

            // Add close button handler
            const closeButton = errorContainer.querySelector('.error-close');
            closeButton.addEventListener('click', () => this.hideError());
        }

        hideError() {
            const errorContainer = this.element.querySelector('.compression-error');
            if (errorContainer) {
                errorContainer.style.display = 'none';
            }
        }

        removeImage() {
            // Clear file inputs
            this.originalInput.value = '';
            this.compressedInput.value = '';
            
            // Hide preview and info
            this.previewContainer.style.display = 'none';
            this.infoContainer.style.display = 'none';
            
            // Reset compressor
            this.compressor.reset();
            
            // Show drop zone again
            this.dropZone.style.display = 'block';
        }

        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        handleFormSubmit(e) {
            // Additional validation before form submission
            if (this.compressor.isProcessing) {
                e.preventDefault();
                alert('Please wait for image compression to complete.');
                return false;
            }

            return true;
        }

        // Public API methods
        getCompressor() {
            return this.compressor;
        }

        getCompressionInfo() {
            return this.compressor.getCompressionInfo();
        }

        updateOptions(newOptions) {
            this.options = { ...this.options, ...newOptions };
            this.compressor.updateConfig(newOptions);
        }
    }

    // Initialize widgets when DOM is ready
    function initializeWidgets() {
        const widgets = document.querySelectorAll('.compressed-image-widget');
        
        widgets.forEach(widget => {
            const optionsScript = widget.querySelector('.compression-options');
            let options = {};
            
            if (optionsScript) {
                try {
                    options = JSON.parse(optionsScript.textContent);
                } catch (e) {
                    console.warn('Failed to parse compression options:', e);
                }
            }
            
            new CompressedImageWidget(widget, options);
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeWidgets);
    } else {
        initializeWidgets();
    }

    // Re-initialize on dynamic content changes (for AJAX forms)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const widgets = node.querySelectorAll('.compressed-image-widget');
                        widgets.forEach(widget => {
                            if (!widget.dataset.initialized) {
                                const optionsScript = widget.querySelector('.compression-options');
                                let options = {};
                                
                                if (optionsScript) {
                                    try {
                                        options = JSON.parse(optionsScript.textContent);
                                    } catch (e) {
                                        console.warn('Failed to parse compression options:', e);
                                    }
                                }
                                
                                new CompressedImageWidget(widget, options);
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
    window.CompressedImageWidget = CompressedImageWidget;
})();
