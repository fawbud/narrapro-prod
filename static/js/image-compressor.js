/**
 * Universal Image Compressor Module
 * Client-side image compression utility for Django applications
 * 
 * Features:
 * - Configurable compression quality and max file size
 * - Support for multiple image formats (JPEG, PNG, WebP)
 * - Progress tracking and callbacks
 * - Drag & drop support
 * - Preview functionality
 * - Error handling and validation
 * 
 * @version 1.0.0
 * @author NarraPro Development Team
 */

class ImageCompressor {
    constructor(options = {}) {
        // Default configuration
        this.config = {
            maxSizeKB: options.maxSizeKB || 1024, // 1MB default
            quality: options.quality || 0.8, // 80% quality
            maxWidth: options.maxWidth || 1920,
            maxHeight: options.maxHeight || 1080,
            outputFormat: options.outputFormat || 'auto', // 'jpeg', 'png', 'webp', 'auto'
            autoCompress: options.autoCompress !== false, // true by default
            enablePreview: options.enablePreview !== false, // true by default
            allowedTypes: options.allowedTypes || ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            onProgress: options.onProgress || null,
            onSuccess: options.onSuccess || null,
            onError: options.onError || null,
            onPreview: options.onPreview || null
        };

        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.currentFile = null;
        this.compressedFile = null;
        this.isProcessing = false;
    }

    /**
     * Initialize the compressor with a file input element
     * @param {HTMLInputElement|string} inputElement - File input element or selector
     * @param {Object} options - Additional options
     */
    init(inputElement, options = {}) {
        const input = typeof inputElement === 'string' 
            ? document.querySelector(inputElement) 
            : inputElement;

        if (!input || input.type !== 'file') {
            throw new Error('Invalid file input element provided');
        }

        // Merge options
        Object.assign(this.config, options);

        // Set up event listeners
        this.setupFileInput(input);
        
        // Set up drag and drop if container is provided
        if (options.dropContainer) {
            this.setupDragDrop(options.dropContainer);
        }

        return this;
    }

    /**
     * Set up file input event listeners
     * @param {HTMLInputElement} input - File input element
     */
    setupFileInput(input) {
        input.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            if (files.length > 0) {
                this.processFile(files[0]);
            }
        });

        // Set accept attribute
        input.accept = this.config.allowedTypes.join(',');
    }

    /**
     * Set up drag and drop functionality
     * @param {HTMLElement|string} container - Drop container element or selector
     */
    setupDragDrop(container) {
        const dropZone = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;

        if (!dropZone) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                this.processFile(files[0]);
            }
        }, false);
    }

    /**
     * Prevent default drag behaviors
     * @param {Event} e - Event object
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Process and compress a file
     * @param {File} file - File to process
     * @returns {Promise<File>} - Compressed file
     */
    async processFile(file) {
        if (this.isProcessing) {
            throw new Error('Another file is currently being processed');
        }

        try {
            this.isProcessing = true;
            this.currentFile = file;

            // Validate file
            this.validateFile(file);

            // Report progress
            this.reportProgress('Validating file...', 10);

            // Check if compression is needed
            const fileSizeKB = file.size / 1024;
            if (fileSizeKB <= this.config.maxSizeKB && !this.config.autoCompress) {
                this.compressedFile = file;
                this.reportProgress('File is already optimized', 100);
                this.onSuccess(file);
                return file;
            }

            // Create preview if enabled
            if (this.config.enablePreview) {
                this.createPreview(file);
            }

            // Compress the image
            this.reportProgress('Compressing image...', 30);
            const compressedFile = await this.compressImage(file);

            this.compressedFile = compressedFile;
            this.reportProgress('Compression complete', 100);
            this.onSuccess(compressedFile);

            return compressedFile;

        } catch (error) {
            this.onError(error);
            throw error;
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Validate file type and size
     * @param {File} file - File to validate
     */
    validateFile(file) {
        if (!this.config.allowedTypes.includes(file.type)) {
            throw new Error(`File type ${file.type} is not allowed. Allowed types: ${this.config.allowedTypes.join(', ')}`);
        }

        // Check maximum file size (before compression)
        const maxFileSizeMB = 50; // 50MB max before compression
        if (file.size > maxFileSizeMB * 1024 * 1024) {
            throw new Error(`File size exceeds maximum allowed size of ${maxFileSizeMB}MB`);
        }
    }

    /**
     * Create image preview
     * @param {File} file - File to preview
     */
    createPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            if (this.config.onPreview) {
                this.config.onPreview(e.target.result, file);
            }
        };
        reader.readAsDataURL(file);
    }

    /**
     * Compress image file
     * @param {File} file - File to compress
     * @returns {Promise<File>} - Compressed file
     */
    compressImage(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const img = new Image();
                
                img.onload = () => {
                    try {
                        this.reportProgress('Processing image...', 50);
                        
                        // Calculate new dimensions
                        const { width, height } = this.calculateDimensions(
                            img.width, 
                            img.height
                        );

                        // Set canvas dimensions
                        this.canvas.width = width;
                        this.canvas.height = height;

                        // Clear canvas and draw image
                        this.ctx.clearRect(0, 0, width, height);
                        this.ctx.drawImage(img, 0, 0, width, height);

                        this.reportProgress('Generating compressed file...', 70);

                        // Determine output format
                        const outputFormat = this.getOutputFormat(file.type);
                        
                        // Convert canvas to blob with compression
                        this.compressToTargetSize(outputFormat, file.name)
                            .then(resolve)
                            .catch(reject);

                    } catch (error) {
                        reject(error);
                    }
                };

                img.onerror = () => {
                    reject(new Error('Failed to load image'));
                };

                img.src = e.target.result;
            };

            reader.onerror = () => {
                reject(new Error('Failed to read file'));
            };

            reader.readAsDataURL(file);
        });
    }

    /**
     * Calculate optimal dimensions while maintaining aspect ratio
     * @param {number} originalWidth - Original image width
     * @param {number} originalHeight - Original image height
     * @returns {Object} - New dimensions
     */
    calculateDimensions(originalWidth, originalHeight) {
        let { width, height } = { width: originalWidth, height: originalHeight };

        // Scale down if exceeds maximum dimensions
        if (width > this.config.maxWidth || height > this.config.maxHeight) {
            const aspectRatio = width / height;

            if (width > height) {
                width = this.config.maxWidth;
                height = width / aspectRatio;
            } else {
                height = this.config.maxHeight;
                width = height * aspectRatio;
            }
        }

        return { 
            width: Math.round(width), 
            height: Math.round(height) 
        };
    }

    /**
     * Get output format based on input and configuration
     * @param {string} inputType - Input MIME type
     * @returns {string} - Output MIME type
     */
    getOutputFormat(inputType) {
        if (this.config.outputFormat !== 'auto') {
            return `image/${this.config.outputFormat}`;
        }

        // Auto-detect best format
        if (inputType === 'image/png' && this.needsTransparency()) {
            return 'image/png';
        }

        // Default to JPEG for best compression
        return 'image/jpeg';
    }

    /**
     * Check if image needs transparency support
     * @returns {boolean} - True if transparency is needed
     */
    needsTransparency() {
        // Check if canvas has transparent pixels
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;

        for (let i = 3; i < data.length; i += 4) {
            if (data[i] < 255) {
                return true; // Found transparent pixel
            }
        }

        return false;
    }

    /**
     * Compress image to target file size
     * @param {string} outputFormat - Output MIME type
     * @param {string} filename - Original filename
     * @returns {Promise<File>} - Compressed file
     */
    compressToTargetSize(outputFormat, filename) {
        return new Promise((resolve, reject) => {
            let quality = this.config.quality;
            let attempts = 0;
            const maxAttempts = 10;

            const tryCompress = () => {
                this.canvas.toBlob((blob) => {
                    if (!blob) {
                        reject(new Error('Failed to create compressed image'));
                        return;
                    }

                    const fileSizeKB = blob.size / 1024;
                    
                    this.reportProgress(`Attempt ${attempts + 1}: ${fileSizeKB.toFixed(1)}KB`, 80 + (attempts * 2));

                    // If file size is acceptable or we've tried enough times
                    if (fileSizeKB <= this.config.maxSizeKB || attempts >= maxAttempts) {
                        const newFilename = this.generateFilename(filename, outputFormat);
                        const file = new File([blob], newFilename, { 
                            type: outputFormat,
                            lastModified: Date.now()
                        });

                        resolve(file);
                        return;
                    }

                    // Reduce quality for next attempt
                    attempts++;
                    quality = Math.max(0.1, quality - 0.1);
                    
                    setTimeout(tryCompress, 10); // Small delay to prevent blocking
                    
                }, outputFormat, quality);
            };

            tryCompress();
        });
    }

    /**
     * Generate filename for compressed image
     * @param {string} originalFilename - Original filename
     * @param {string} outputFormat - Output MIME type
     * @returns {string} - New filename
     */
    generateFilename(originalFilename, outputFormat) {
        const extension = outputFormat.split('/')[1];
        const nameWithoutExt = originalFilename.replace(/\.[^/.]+$/, '');
        return `${nameWithoutExt}.${extension}`;
    }

    /**
     * Report progress to callback
     * @param {string} message - Progress message
     * @param {number} percentage - Progress percentage (0-100)
     */
    reportProgress(message, percentage) {
        if (this.config.onProgress) {
            this.config.onProgress(percentage, message);
        }
    }

    /**
     * Handle successful compression
     * @param {File} file - Compressed file
     */
    onSuccess(file) {
        if (this.config.onSuccess) {
            this.config.onSuccess(file, {
                originalSize: this.currentFile ? this.currentFile.size : 0,
                compressedSize: file.size,
                compressionRatio: this.currentFile ? (1 - file.size / this.currentFile.size) : 0
            });
        }
    }

    /**
     * Handle compression error
     * @param {Error} error - Error object
     */
    onError(error) {
        if (this.config.onError) {
            this.config.onError(error);
        }
    }

    /**
     * Get compression information
     * @returns {Object} - Compression info
     */
    getCompressionInfo() {
        if (!this.currentFile || !this.compressedFile) {
            return null;
        }

        return {
            originalFile: this.currentFile,
            compressedFile: this.compressedFile,
            originalSize: this.currentFile.size,
            compressedSize: this.compressedFile.size,
            compressionRatio: 1 - (this.compressedFile.size / this.currentFile.size),
            sizeSavedKB: (this.currentFile.size - this.compressedFile.size) / 1024
        };
    }

    /**
     * Reset the compressor state
     */
    reset() {
        this.currentFile = null;
        this.compressedFile = null;
        this.isProcessing = false;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    /**
     * Update configuration
     * @param {Object} newConfig - New configuration options
     */
    updateConfig(newConfig) {
        Object.assign(this.config, newConfig);
    }

    /**
     * Static method to compress a file with default settings
     * @param {File} file - File to compress
     * @param {Object} options - Compression options
     * @returns {Promise<File>} - Compressed file
     */
    static async compress(file, options = {}) {
        const compressor = new ImageCompressor(options);
        return await compressor.processFile(file);
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageCompressor;
}

// Global variable for browser usage
if (typeof window !== 'undefined') {
    window.ImageCompressor = ImageCompressor;
}
