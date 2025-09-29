/**
 * Image Cropper with Compression Integration
 * Advanced client-side image cropping modal with aspect ratio locking and compression
 *
 * Features:
 * - Modal-based cropping interface
 * - Aspect ratio locking (1:1 for profiles, 4:1 for covers)
 * - Integration with ImageCompressor
 * - Touch/mouse support for crop area adjustment
 * - Real-time preview
 * - Size and quality controls
 *
 * @version 1.0.0
 * @author NarraPro Development Team
 */

class ImageCropper {
    constructor(options = {}) {
        this.config = {
            aspectRatio: options.aspectRatio || 1, // 1:1 for profile, 4:1 for cover
            maxSizeKB: options.maxSizeKB || 1024, // Max file size after compression
            quality: options.quality || 0.8,
            outputWidth: options.outputWidth || 800,
            outputHeight: options.outputHeight || null, // Auto-calculated from aspect ratio
            modalId: options.modalId || 'imageCropperModal',
            onCrop: options.onCrop || null,
            onCancel: options.onCancel || null,
            onError: options.onError || null
        };

        // Calculate output height if not provided
        if (!this.config.outputHeight) {
            this.config.outputHeight = Math.round(this.config.outputWidth / this.config.aspectRatio);
        }

        this.modal = null;
        this.canvas = null;
        this.ctx = null;
        this.image = null;
        this.cropArea = {
            x: 0,
            y: 0,
            width: 0,
            height: 0
        };
        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };
        this.currentFile = null;
        this.compressor = null;

        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
        this.setupCompressor();
    }

    createModal() {
        // Remove existing modal if present
        const existingModal = document.getElementById(this.config.modalId);
        if (existingModal) {
            existingModal.remove();
        }

        const modalHTML = `
            <div class="modal fade" id="${this.config.modalId}" tabindex="-1" aria-labelledby="cropperModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="cropperModalLabel">
                                <i class="fas fa-crop-alt me-2"></i>Crop Image
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="crop-container">
                                        <canvas id="cropCanvas" class="crop-canvas"></canvas>
                                        <div class="crop-overlay">
                                            <div class="crop-area">
                                                <div class="crop-handle crop-handle-tl"></div>
                                                <div class="crop-handle crop-handle-tr"></div>
                                                <div class="crop-handle crop-handle-bl"></div>
                                                <div class="crop-handle crop-handle-br"></div>
                                                <div class="crop-handle crop-handle-t"></div>
                                                <div class="crop-handle crop-handle-b"></div>
                                                <div class="crop-handle crop-handle-l"></div>
                                                <div class="crop-handle crop-handle-r"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="crop-preview-section">
                                        <h6><i class="fas fa-eye me-2"></i>Preview</h6>
                                        <div class="crop-preview">
                                            <canvas id="previewCanvas" width="200" height="200"></canvas>
                                        </div>
                                        <div class="preview-info text-center mt-3">
                                            <small class="text-muted">
                                                <div>Aspect Ratio: ${this.getAspectRatioText()}</div>
                                                <div>Max Size: ${Math.round(this.config.maxSizeKB / 1024 * 10) / 10}MB</div>
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-1"></i>Cancel
                            </button>
                            <button type="button" class="btn btn-primary" id="cropConfirm">
                                <i class="fas fa-check me-1"></i>Crop & Compress
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = new bootstrap.Modal(document.getElementById(this.config.modalId));

        // Get canvas and context
        this.canvas = document.getElementById('cropCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.previewCanvas = document.getElementById('previewCanvas');
        this.previewCtx = this.previewCanvas.getContext('2d');
    }

    setupEventListeners() {
        const modal = document.getElementById(this.config.modalId);

        // Canvas interactions
        this.setupCanvasEvents();

        // Confirm button
        modal.querySelector('#cropConfirm').addEventListener('click', () => {
            this.cropAndCompress();
        });

        // Modal events
        modal.addEventListener('hidden.bs.modal', () => {
            if (this.config.onCancel) {
                this.config.onCancel();
            }
        });
    }

    setupCanvasEvents() {
        const canvas = this.canvas;

        this.isResizing = false;
        this.resizeHandle = null;
        this.startPoint = { x: 0, y: 0 };

        // Get overlay and crop area after modal is created
        setTimeout(() => {
            const overlay = document.querySelector(`#${this.config.modalId} .crop-overlay`);
            const cropArea = overlay.querySelector('.crop-area');

            // Mouse events for dragging crop area
            cropArea.addEventListener('mousedown', (e) => this.startDrag(e));
            document.addEventListener('mousemove', (e) => this.drag(e));
            document.addEventListener('mouseup', (e) => this.endDrag(e));

            // Touch events for dragging crop area
            cropArea.addEventListener('touchstart', (e) => this.startDrag(e));
            document.addEventListener('touchmove', (e) => this.drag(e));
            document.addEventListener('touchend', (e) => this.endDrag(e));

            // Handle resize handles
            overlay.querySelectorAll('.crop-handle').forEach(handle => {
                handle.addEventListener('mousedown', (e) => {
                    e.stopPropagation();
                    this.isResizing = true;
                    this.resizeHandle = handle.className.split(' ').find(c => c.startsWith('crop-handle-'));
                    this.startResize(e);
                });

                handle.addEventListener('touchstart', (e) => {
                    e.stopPropagation();
                    this.isResizing = true;
                    this.resizeHandle = handle.className.split(' ').find(c => c.startsWith('crop-handle-'));
                    this.startResize(e);
                });
            });
        }, 100);
    }

    setupCompressor() {
        this.compressor = new ImageCompressor({
            maxSizeKB: this.config.maxSizeKB,
            quality: this.config.quality,
            autoCompress: false,
            enablePreview: false
        });
    }

    open(file) {
        this.currentFile = file;
        this.loadImage(file);
        this.modal.show();
    }

    loadImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.image = new Image();
            this.image.onload = () => {
                this.setupCanvas();
                this.initializeCropArea();
                this.render();
                this.updatePreview();
            };
            this.image.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    setupCanvas() {
        const maxWidth = 600;
        const maxHeight = 400;

        let { width, height } = this.image;

        // Scale image to fit canvas
        if (width > maxWidth || height > maxHeight) {
            const scale = Math.min(maxWidth / width, maxHeight / height);
            width *= scale;
            height *= scale;
        }

        this.canvas.width = width;
        this.canvas.height = height;
        this.canvas.style.width = width + 'px';
        this.canvas.style.height = height + 'px';

        // Update overlay size
        const overlay = document.querySelector(`#${this.config.modalId} .crop-overlay`);
        overlay.style.width = width + 'px';
        overlay.style.height = height + 'px';
    }

    initializeCropArea() {
        const canvasWidth = this.canvas.width;
        const canvasHeight = this.canvas.height;

        let cropWidth, cropHeight;

        if (this.config.aspectRatio) {
            // Calculate crop area based on aspect ratio
            if (canvasWidth / canvasHeight > this.config.aspectRatio) {
                cropHeight = canvasHeight * 0.8;
                cropWidth = cropHeight * this.config.aspectRatio;
            } else {
                cropWidth = canvasWidth * 0.8;
                cropHeight = cropWidth / this.config.aspectRatio;
            }
        } else {
            // Free crop - use 80% of canvas
            cropWidth = canvasWidth * 0.8;
            cropHeight = canvasHeight * 0.8;
        }

        this.cropArea = {
            x: (canvasWidth - cropWidth) / 2,
            y: (canvasHeight - cropHeight) / 2,
            width: cropWidth,
            height: cropHeight
        };

        this.updateCropAreaElement();
    }

    updateCropArea() {
        if (this.config.aspectRatio) {
            // Maintain aspect ratio
            const currentRatio = this.cropArea.width / this.cropArea.height;
            if (Math.abs(currentRatio - this.config.aspectRatio) > 0.01) {
                // Adjust height to match aspect ratio
                this.cropArea.height = this.cropArea.width / this.config.aspectRatio;

                // Ensure crop area stays within bounds
                if (this.cropArea.y + this.cropArea.height > this.canvas.height) {
                    this.cropArea.height = this.canvas.height - this.cropArea.y;
                    this.cropArea.width = this.cropArea.height * this.config.aspectRatio;
                }
            }
        }

        this.updateCropAreaElement();
        this.render();
        this.updatePreview();
    }

    updateCropAreaElement() {
        const cropAreaElement = document.querySelector(`#${this.config.modalId} .crop-area`);
        cropAreaElement.style.left = this.cropArea.x + 'px';
        cropAreaElement.style.top = this.cropArea.y + 'px';
        cropAreaElement.style.width = this.cropArea.width + 'px';
        cropAreaElement.style.height = this.cropArea.height + 'px';
    }

    startDrag(e) {
        e.preventDefault();
        this.isDragging = true;
        const rect = this.canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        this.dragStart = {
            x: clientX - rect.left - this.cropArea.x,
            y: clientY - rect.top - this.cropArea.y
        };
    }

    drag(e) {
        if (!this.isDragging) return;

        e.preventDefault();
        const rect = this.canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        const newX = clientX - rect.left - this.dragStart.x;
        const newY = clientY - rect.top - this.dragStart.y;

        // Constrain to canvas bounds
        this.cropArea.x = Math.max(0, Math.min(newX, this.canvas.width - this.cropArea.width));
        this.cropArea.y = Math.max(0, Math.min(newY, this.canvas.height - this.cropArea.height));

        this.updateCropAreaElement();
        this.render();
        this.updatePreview();
    }

    endDrag() {
        this.isDragging = false;
        this.isResizing = false;
        this.resizeHandle = null;
    }

    startResize(e) {
        e.preventDefault();
        const rect = this.canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        this.startPoint = {
            x: clientX - rect.left,
            y: clientY - rect.top,
            cropX: this.cropArea.x,
            cropY: this.cropArea.y,
            cropWidth: this.cropArea.width,
            cropHeight: this.cropArea.height
        };

        // Add global mouse/touch move listeners for resizing
        const handleResize = (e) => this.handleResize(e);
        const handleResizeEnd = () => {
            this.isResizing = false;
            this.resizeHandle = null;
            document.removeEventListener('mousemove', handleResize);
            document.removeEventListener('mouseup', handleResizeEnd);
            document.removeEventListener('touchmove', handleResize);
            document.removeEventListener('touchend', handleResizeEnd);
        };

        document.addEventListener('mousemove', handleResize);
        document.addEventListener('mouseup', handleResizeEnd);
        document.addEventListener('touchmove', handleResize);
        document.addEventListener('touchend', handleResizeEnd);
    }

    handleResize(e) {
        if (!this.isResizing || !this.resizeHandle) return;

        e.preventDefault();
        const rect = this.canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        const currentX = clientX - rect.left;
        const currentY = clientY - rect.top;
        const deltaX = currentX - this.startPoint.x;
        const deltaY = currentY - this.startPoint.y;

        let newX = this.startPoint.cropX;
        let newY = this.startPoint.cropY;
        let newWidth = this.startPoint.cropWidth;
        let newHeight = this.startPoint.cropHeight;

        // Handle different resize directions
        switch (this.resizeHandle) {
            case 'crop-handle-tl': // Top-left
                newX = this.startPoint.cropX + deltaX;
                newY = this.startPoint.cropY + deltaY;
                newWidth = this.startPoint.cropWidth - deltaX;
                newHeight = this.startPoint.cropHeight - deltaY;
                break;
            case 'crop-handle-tr': // Top-right
                newY = this.startPoint.cropY + deltaY;
                newWidth = this.startPoint.cropWidth + deltaX;
                newHeight = this.startPoint.cropHeight - deltaY;
                break;
            case 'crop-handle-bl': // Bottom-left
                newX = this.startPoint.cropX + deltaX;
                newWidth = this.startPoint.cropWidth - deltaX;
                newHeight = this.startPoint.cropHeight + deltaY;
                break;
            case 'crop-handle-br': // Bottom-right
                newWidth = this.startPoint.cropWidth + deltaX;
                newHeight = this.startPoint.cropHeight + deltaY;
                break;
            case 'crop-handle-t': // Top
                newY = this.startPoint.cropY + deltaY;
                newHeight = this.startPoint.cropHeight - deltaY;
                break;
            case 'crop-handle-b': // Bottom
                newHeight = this.startPoint.cropHeight + deltaY;
                break;
            case 'crop-handle-l': // Left
                newX = this.startPoint.cropX + deltaX;
                newWidth = this.startPoint.cropWidth - deltaX;
                break;
            case 'crop-handle-r': // Right
                newWidth = this.startPoint.cropWidth + deltaX;
                break;
        }

        // Enforce aspect ratio if set
        if (this.config.aspectRatio) {
            const currentRatio = newWidth / newHeight;
            if (Math.abs(currentRatio - this.config.aspectRatio) > 0.01) {
                if (this.resizeHandle.includes('t') || this.resizeHandle.includes('b')) {
                    // Height changed, adjust width
                    newWidth = newHeight * this.config.aspectRatio;
                } else {
                    // Width changed, adjust height
                    newHeight = newWidth / this.config.aspectRatio;
                }
            }
        }

        // Enforce minimum size
        const minSize = 50;
        newWidth = Math.max(minSize, newWidth);
        newHeight = Math.max(minSize, newHeight);

        // Keep within canvas bounds
        newX = Math.max(0, Math.min(newX, this.canvas.width - newWidth));
        newY = Math.max(0, Math.min(newY, this.canvas.height - newHeight));
        newWidth = Math.min(newWidth, this.canvas.width - newX);
        newHeight = Math.min(newHeight, this.canvas.height - newY);

        // Update crop area
        this.cropArea = {
            x: newX,
            y: newY,
            width: newWidth,
            height: newHeight
        };

        this.updateCropAreaElement();
        this.render();
        this.updatePreview();
    }

    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw image
        this.ctx.drawImage(this.image, 0, 0, this.canvas.width, this.canvas.height);

        // Draw crop overlay
        this.ctx.save();
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Clear crop area
        this.ctx.globalCompositeOperation = 'destination-out';
        this.ctx.fillRect(this.cropArea.x, this.cropArea.y, this.cropArea.width, this.cropArea.height);
        this.ctx.restore();
    }

    updatePreview() {
        if (!this.image) return;

        const previewSize = 150;
        this.previewCanvas.width = previewSize;
        this.previewCanvas.height = previewSize;

        // Calculate scale factor
        const scaleX = this.image.width / this.canvas.width;
        const scaleY = this.image.height / this.canvas.height;

        // Calculate source coordinates
        const sourceX = this.cropArea.x * scaleX;
        const sourceY = this.cropArea.y * scaleY;
        const sourceWidth = this.cropArea.width * scaleX;
        const sourceHeight = this.cropArea.height * scaleY;

        // Draw cropped area to preview
        const aspectRatio = sourceWidth / sourceHeight;
        let drawWidth = previewSize;
        let drawHeight = previewSize;

        if (aspectRatio > 1) {
            drawHeight = previewSize / aspectRatio;
        } else {
            drawWidth = previewSize * aspectRatio;
        }

        const offsetX = (previewSize - drawWidth) / 2;
        const offsetY = (previewSize - drawHeight) / 2;

        this.previewCtx.clearRect(0, 0, previewSize, previewSize);
        this.previewCtx.drawImage(
            this.image,
            sourceX, sourceY, sourceWidth, sourceHeight,
            offsetX, offsetY, drawWidth, drawHeight
        );

        // Update preview info
        document.getElementById('previewSize').textContent =
            `${Math.round(sourceWidth)} × ${Math.round(sourceHeight)}`;
        document.getElementById('previewRatio').textContent =
            `${(sourceWidth / sourceHeight).toFixed(2)}:1`;
    }

    async cropAndCompress() {
        try {
            // Create cropped image
            const croppedCanvas = document.createElement('canvas');
            const croppedCtx = croppedCanvas.getContext('2d');

            croppedCanvas.width = this.config.outputWidth;
            croppedCanvas.height = this.config.outputHeight;

            // Calculate scale factors
            const scaleX = this.image.width / this.canvas.width;
            const scaleY = this.image.height / this.canvas.height;

            // Calculate source coordinates
            const sourceX = this.cropArea.x * scaleX;
            const sourceY = this.cropArea.y * scaleY;
            const sourceWidth = this.cropArea.width * scaleX;
            const sourceHeight = this.cropArea.height * scaleY;

            // Draw cropped and scaled image
            croppedCtx.drawImage(
                this.image,
                sourceX, sourceY, sourceWidth, sourceHeight,
                0, 0, this.config.outputWidth, this.config.outputHeight
            );

            // Convert to blob
            const blob = await new Promise(resolve => {
                croppedCanvas.toBlob(resolve, 'image/jpeg', this.config.quality);
            });

            // Create file from blob
            const croppedFile = new File([blob], this.generateFilename(), {
                type: 'image/jpeg',
                lastModified: Date.now()
            });

            // Compress if needed
            let finalFile = croppedFile;
            if (croppedFile.size > this.config.maxSizeKB * 1024) {
                finalFile = await this.compressor.processFile(croppedFile);
            }

            this.modal.hide();

            if (this.config.onCrop) {
                this.config.onCrop(finalFile);
            }

        } catch (error) {
            if (this.config.onError) {
                this.config.onError(error);
            }
        }
    }

    generateFilename() {
        const timestamp = Date.now();
        const aspectRatioStr = this.config.aspectRatio ? `_${this.config.aspectRatio.toString().replace('.', '-')}` : '';
        return `cropped_image${aspectRatioStr}_${timestamp}.jpg`;
    }

    getAspectRatioText() {
        if (this.config.aspectRatio === 1) return '1:1 (Square)';
        if (this.config.aspectRatio === 4) return '4:1 (Banner)';
        if (this.config.aspectRatio === 1.33) return '4:3 (Standard)';
        if (this.config.aspectRatio === 1.78) return '16:9 (Widescreen)';
        return this.config.aspectRatio ? `${this.config.aspectRatio}:1` : 'Free';
    }

    destroy() {
        if (this.modal) {
            this.modal.dispose();
        }
        const modalElement = document.getElementById(this.config.modalId);
        if (modalElement) {
            modalElement.remove();
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageCropper;
}

// Global variable for browser usage
if (typeof window !== 'undefined') {
    window.ImageCropper = ImageCropper;
}