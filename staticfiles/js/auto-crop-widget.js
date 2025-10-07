/**
 * Auto Crop Widget
 * Automatically crops and compresses images without user interaction
 */

(function() {
    'use strict';

    class AutoCropWidget {
        constructor(element, options = {}) {
            this.element = element;
            this.options = {
                aspectRatio: options.aspectRatio || 1, // 1:1 for profile, 4:1 for cover
                maxSizeKB: options.maxSizeKB || 1024, // Max file size after compression
                outputWidth: options.outputWidth || 800,
                quality: options.quality || 0.8,
                ...options
            };

            this.originalInput = null;
            this.canvas = document.createElement('canvas');
            this.ctx = this.canvas.getContext('2d');
            this.isProcessing = false;
            this.lastProcessedFileName = null;

            this.init();
        }

        init() {
            this.findFileInput();
            if (!this.originalInput) {
                return;
            }

            this.createUI();
            this.attachEventListeners();
        }

        findFileInput() {
            this.originalInput = this.element.querySelector('input[type="file"]');
            if (!this.originalInput) {
                // Also try looking for inputs with accept="image/*"
                this.originalInput = this.element.querySelector('input[accept*="image"]');
            }
        }

        createUI() {
            // Create drop zone
            const dropZone = document.createElement('div');
            dropZone.className = 'auto-crop-zone';
            dropZone.innerHTML = `
                <div class="drop-content">
                    <i class="fas fa-images fa-2x mb-2"></i>
                    <p><strong>Click to upload image</strong></p>
                    <small class="text-muted">
                        Will be auto-cropped to ${this.getAspectRatioText()} and compressed to max ${Math.round(this.options.maxSizeKB / 1024 * 10) / 10}MB
                    </small>
                </div>
            `;

            // Insert before original input and hide it
            this.originalInput.parentNode.insertBefore(dropZone, this.originalInput);
            this.originalInput.style.display = 'none';

            // Set up click handler
            dropZone.addEventListener('click', () => {
                this.originalInput.click();
            });

            this.dropZone = dropZone;
        }

        attachEventListeners() {
            // Remove any existing listeners to prevent infinite loops
            this.originalInput.removeEventListener('change', this.handleFileChange);

            // Bind the handler to preserve context
            this.handleFileChange = (e) => {
                if (e.target.files && e.target.files[0]) {
                    this.processFile(e.target.files[0]);
                }
            };

            this.originalInput.addEventListener('change', this.handleFileChange);
        }

        async processFile(file) {
            try {
                // Prevent processing if already processing or if it's the same file
                if (this.isProcessing) {
                    return;
                }

                // Check if this is a file we just processed (prevent infinite loop)
                if (file.name === this.lastProcessedFileName) {
                    return;
                }

                this.isProcessing = true;
                this.showProcessing();

                // Validate file
                if (!this.validateFile(file)) {
                    this.isProcessing = false;
                    return;
                }

                // Auto crop and compress
                const processedFile = await this.autoCropAndCompress(file);

                // Remember the processed filename
                this.lastProcessedFileName = processedFile.name;

                // Update file input
                this.updateFileInput(processedFile);

                // Show success
                this.showSuccess(processedFile, file);

                this.isProcessing = false;

            } catch (error) {
                console.error('Auto crop error:', error);
                this.showError(error.message);
                this.isProcessing = false;
            }
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

        autoCropAndCompress(file) {
            return new Promise((resolve, reject) => {
                const img = new Image();

                img.onload = async () => {
                    try {
                        // Calculate crop dimensions for center crop with aspect ratio
                        const { cropX, cropY, cropWidth, cropHeight } = this.calculateCenterCrop(
                            img.width,
                            img.height,
                            this.options.aspectRatio
                        );

                        // Set canvas to output dimensions
                        const outputHeight = Math.round(this.options.outputWidth / this.options.aspectRatio);
                        this.canvas.width = this.options.outputWidth;
                        this.canvas.height = outputHeight;

                        // Draw cropped and scaled image
                        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                        this.ctx.drawImage(
                            img,
                            cropX, cropY, cropWidth, cropHeight, // Source crop area
                            0, 0, this.canvas.width, this.canvas.height // Destination
                        );

                        // Convert to blob and compress if needed
                        const processedFile = await this.compressToTarget();
                        resolve(processedFile);

                    } catch (error) {
                        reject(error);
                    }
                };

                img.onerror = () => {
                    reject(new Error('Failed to load image'));
                };

                // Load image
                const reader = new FileReader();
                reader.onload = (e) => {
                    img.src = e.target.result;
                };
                reader.onerror = () => {
                    reject(new Error('Failed to read file'));
                };
                reader.readAsDataURL(file);
            });
        }

        calculateCenterCrop(imgWidth, imgHeight, aspectRatio) {
            const imgAspectRatio = imgWidth / imgHeight;

            let cropWidth, cropHeight, cropX, cropY;

            if (imgAspectRatio > aspectRatio) {
                // Image is wider than target ratio - crop from sides
                cropHeight = imgHeight;
                cropWidth = imgHeight * aspectRatio;
                cropX = (imgWidth - cropWidth) / 2;
                cropY = 0;
            } else {
                // Image is taller than target ratio - crop from top/bottom
                cropWidth = imgWidth;
                cropHeight = imgWidth / aspectRatio;
                cropX = 0;
                cropY = (imgHeight - cropHeight) / 2;
            }

            return { cropX, cropY, cropWidth, cropHeight };
        }

        compressToTarget() {
            return new Promise((resolve) => {
                let quality = this.options.quality;
                let attempts = 0;
                const maxAttempts = 10;

                const tryCompress = () => {
                    this.canvas.toBlob((blob) => {
                        if (!blob) {
                            resolve(this.createFallbackFile());
                            return;
                        }

                        const fileSizeKB = blob.size / 1024;

                        // If file size is acceptable or we've tried enough times
                        if (fileSizeKB <= this.options.maxSizeKB || attempts >= maxAttempts) {
                            const file = new File([blob], this.generateFilename(), {
                                type: 'image/jpeg',
                                lastModified: Date.now()
                            });
                            resolve(file);
                            return;
                        }

                        // Reduce quality for next attempt
                        attempts++;
                        quality = Math.max(0.1, quality - 0.1);
                        setTimeout(tryCompress, 10);

                    }, 'image/jpeg', quality);
                };

                tryCompress();
            });
        }

        createFallbackFile() {
            // Create a minimal file if compression fails
            const timestamp = Date.now();
            return new File([''], `processed_image_${timestamp}.jpg`, {
                type: 'image/jpeg',
                lastModified: timestamp
            });
        }

        generateFilename() {
            // Use a more stable filename to avoid infinite loops
            const ratioStr = this.options.aspectRatio.toString().replace('.', '-');
            return `cropped_${ratioStr}_image.jpg`;
        }

        updateFileInput(processedFile) {
            try {
                // Temporarily remove the change listener to prevent infinite loop
                this.originalInput.removeEventListener('change', this.handleFileChange);

                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(processedFile);
                this.originalInput.files = dataTransfer.files;

                // Re-add the listener after a short delay
                setTimeout(() => {
                    this.originalInput.addEventListener('change', this.handleFileChange);
                }, 100);

            } catch (error) {
                console.error('Error updating file input:', error);
                // Re-add listener even if there's an error
                setTimeout(() => {
                    this.originalInput.addEventListener('change', this.handleFileChange);
                }, 100);
                throw new Error('Failed to update file input');
            }
        }

        showProcessing() {
            this.hideMessages();
            this.dropZone.innerHTML = `
                <div class="drop-content processing">
                    <div class="spinner-border text-primary mb-2" role="status">
                        <span class="visually-hidden">Processing...</span>
                    </div>
                    <p><strong>Processing image...</strong></p>
                    <small class="text-muted">Cropping and compressing automatically</small>
                </div>
            `;
        }

        showSuccess(processedFile, originalFile) {
            this.hideMessages();

            const compressionRatio = ((originalFile.size - processedFile.size) / originalFile.size * 100).toFixed(1);

            this.dropZone.innerHTML = `
                <div class="drop-content success">
                    <i class="fas fa-check-circle fa-2x mb-2 text-success"></i>
                    <p><strong>Image processed successfully!</strong></p>
                    <small class="text-muted">
                        ${this.formatFileSize(processedFile.size)} •
                        ${compressionRatio}% smaller •
                        ${this.getAspectRatioText()}
                    </small>
                </div>
            `;

            // Add success message below
            const successMsg = document.createElement('div');
            successMsg.className = 'mt-2';
            successMsg.innerHTML = `
                <div class="alert alert-success d-flex align-items-center">
                    <i class="fas fa-info-circle me-2"></i>
                    <div>
                        <strong>Ready to upload:</strong> ${processedFile.name}
                        <button type="button" class="btn btn-sm btn-outline-success ms-auto reset-btn" style="margin-left: auto;">
                            <i class="fas fa-redo"></i> Change
                        </button>
                    </div>
                </div>
            `;

            this.element.appendChild(successMsg);

            // Add reset handler
            successMsg.querySelector('.reset-btn').addEventListener('click', () => {
                this.reset();
            });
        }

        showError(message) {
            this.hideMessages();

            this.dropZone.innerHTML = `
                <div class="drop-content error">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2 text-danger"></i>
                    <p><strong>Error processing image</strong></p>
                    <small class="text-muted">${message}</small>
                </div>
            `;

            // Reset after 3 seconds
            setTimeout(() => {
                this.reset();
            }, 3000);
        }

        reset() {
            // Temporarily remove listener to prevent triggering during reset
            this.originalInput.removeEventListener('change', this.handleFileChange);

            this.originalInput.value = '';
            this.hideMessages();
            this.isProcessing = false;
            this.lastProcessedFileName = null;

            this.dropZone.innerHTML = `
                <div class="drop-content">
                    <i class="fas fa-images fa-2x mb-2"></i>
                    <p><strong>Click to upload image</strong></p>
                    <small class="text-muted">
                        Will be auto-cropped to ${this.getAspectRatioText()} and compressed to max ${Math.round(this.options.maxSizeKB / 1024 * 10) / 10}MB
                    </small>
                </div>
            `;

            // Re-add listener after reset
            setTimeout(() => {
                this.originalInput.addEventListener('change', this.handleFileChange);
            }, 100);
        }

        hideMessages() {
            const messages = this.element.querySelectorAll('.alert');
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
            if (this.options.aspectRatio === 1) return '1:1 (Square)';
            if (this.options.aspectRatio === 4) return '4:1 (Banner)';
            return `${this.options.aspectRatio}:1`;
        }

        destroy() {
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
    function initializeAutoCropWidgets() {
        // Profile picture widgets (1:1 ratio, 1MB)
        const profileWidgets = document.querySelectorAll('.enhanced-image-widget[data-type="profile"]');
        profileWidgets.forEach((widget) => {
            new AutoCropWidget(widget, {
                aspectRatio: 1,
                maxSizeKB: 1024,
                outputWidth: 800
            });
        });

        // Cover image widgets (4:1 ratio, 4MB)
        const coverWidgets = document.querySelectorAll('.enhanced-image-widget[data-type="cover"]');
        coverWidgets.forEach((widget) => {
            new AutoCropWidget(widget, {
                aspectRatio: 4,
                maxSizeKB: 4096,
                outputWidth: 1200
            });
        });

        // Also check for any widgets without specific type
        const genericWidgets = document.querySelectorAll('.enhanced-image-widget:not([data-type])');
        genericWidgets.forEach((widget) => {
            new AutoCropWidget(widget, {
                aspectRatio: 1,
                maxSizeKB: 1024,
                outputWidth: 800
            });
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeAutoCropWidgets);
    } else {
        initializeAutoCropWidgets();
    }

    // Export for global access
    window.AutoCropWidget = AutoCropWidget;
})();