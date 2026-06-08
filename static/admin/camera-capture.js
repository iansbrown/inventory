/**
 * Camera Capture Widget for Equipment Images
 * 
 * Provides cross-platform camera capture functionality for modern browsers.
 * Supports iOS (Safari), Android (Chrome, Firefox), and Desktop (all modern browsers).
 */

class CameraCapture {
    constructor(elementId, equipmentId, csrfToken) {
        this.container = document.getElementById(elementId);
        this.equipmentId = equipmentId;
        this.csrfToken = csrfToken;
        this.mediaStream = null;
        this.canvas = null;
        this.video = null;
        this.state = 'idle'; // idle, active, captured
        
        if (!this.container) {
            console.error(`Camera widget container not found: ${elementId}`);
            return;
        }
        
        this.init();
    }
    
    /**
     * Initialize camera widget and check for browser support.
     */
    async init() {
        // Check camera API availability
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showFallback('Your browser doesn\'t support camera access. Please use traditional file upload.');
            return;
        }
        
        this.createUI();
    }
    
    /**
     * Create camera widget HTML structure.
     */
    createUI() {
        const html = `
            <div class="camera-widget">
                <!-- CAMERA PREVIEW -->
                <div id="camera-preview-${this.equipmentId}" class="camera-preview" style="display:none;">
                    <div class="camera-video-container">
                        <video id="camera-video-${this.equipmentId}" playsinline autoplay muted></video>
                    </div>
                    <div class="camera-controls">
                        <button id="camera-capture-btn-${this.equipmentId}" class="camera-btn capture-btn" type="button">
                            📸 Take Photo
                        </button>
                        <button id="camera-stop-btn-${this.equipmentId}" class="camera-btn stop-btn" type="button">
                            ✕ Stop
                        </button>
                    </div>
                </div>
                
                <!-- CAPTURE RESULT -->
                <div id="capture-result-${this.equipmentId}" class="capture-result" style="display:none;">
                    <div class="canvas-container">
                        <canvas id="capture-canvas-${this.equipmentId}"></canvas>
                    </div>
                    <div class="result-controls">
                        <button id="camera-retake-btn-${this.equipmentId}" class="camera-btn retake-btn" type="button">
                            🔄 Retake
                        </button>
                        <button id="camera-save-btn-${this.equipmentId}" class="camera-btn save-btn" type="button">
                            ✅ Save Photo
                        </button>
                    </div>
                    <div id="upload-status-${this.equipmentId}" class="upload-status"></div>
                </div>
                
                <!-- MAIN CONTROLS -->
                <div class="camera-main-controls">
                    <button id="camera-start-btn-${this.equipmentId}" class="camera-btn start-btn" type="button">
                        📷 Take Photo
                    </button>
                </div>
            </div>
        `;
        
        this.container.innerHTML += html;
        this.attachEventListeners();
    }
    
    /**
     * Attach event listeners to all camera controls.
     */
    attachEventListeners() {
        const id = this.equipmentId;
        
        const startBtn = document.getElementById(`camera-start-btn-${id}`);
        const captureBtn = document.getElementById(`camera-capture-btn-${id}`);
        const stopBtn = document.getElementById(`camera-stop-btn-${id}`);
        const retakeBtn = document.getElementById(`camera-retake-btn-${id}`);
        const saveBtn = document.getElementById(`camera-save-btn-${id}`);
        
        if (startBtn) startBtn.addEventListener('click', () => this.startCamera());
        if (captureBtn) captureBtn.addEventListener('click', () => this.capturePhoto());
        if (stopBtn) stopBtn.addEventListener('click', () => this.stopCamera());
        if (retakeBtn) retakeBtn.addEventListener('click', () => this.retakePhoto());
        if (saveBtn) saveBtn.addEventListener('click', () => this.savePhoto());
    }
    
    /**
     * Start camera and display video preview.
     */
    async startCamera() {
        try {
            // Request camera access with environment (back) camera preference
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment',  // Back camera on mobile
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            });
            
            this.video = document.getElementById(`camera-video-${this.equipmentId}`);
            this.video.srcObject = this.mediaStream;
            
            // Wait for video metadata to load
            this.video.onloadedmetadata = () => {
                this.video.play().catch(err => {
                    console.error('Error playing video:', err);
                });
            };
            
            // Show camera preview, hide main button
            document.getElementById(`camera-preview-${this.equipmentId}`).style.display = 'block';
            document.getElementById(`camera-start-btn-${this.equipmentId}`).style.display = 'none';
            
            this.state = 'active';
        } catch (error) {
            console.error('Camera access error:', error);
            
            if (error.name === 'NotAllowedError') {
                alert('❌ Camera permission denied. Please enable camera access in your browser settings.');
            } else if (error.name === 'NotFoundError') {
                alert('❌ No camera found on this device.');
            } else {
                alert(`❌ Camera error: ${error.message}`);
            }
        }
    }
    
    /**
     * Capture photo from video stream to canvas.
     */
    capturePhoto() {
        try {
            this.canvas = document.getElementById(`capture-canvas-${this.equipmentId}`);
            
            if (!this.video || !this.canvas) {
                console.error('Video or canvas element not found');
                return;
            }
            
            // Set canvas dimensions to match video
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            // Draw video frame to canvas
            const ctx = this.canvas.getContext('2d');
            ctx.drawImage(this.video, 0, 0);
            
            // Hide preview, show result
            document.getElementById(`camera-preview-${this.equipmentId}`).style.display = 'none';
            document.getElementById(`capture-result-${this.equipmentId}`).style.display = 'block';
            
            this.state = 'captured';
        } catch (error) {
            console.error('Photo capture error:', error);
            alert(`❌ Failed to capture photo: ${error.message}`);
        }
    }
    
    /**
     * Stop camera stream and close preview.
     */
    stopCamera() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
        
        document.getElementById(`camera-preview-${this.equipmentId}`).style.display = 'none';
        document.getElementById(`camera-start-btn-${this.equipmentId}`).style.display = 'block';
        
        this.state = 'idle';
    }
    
    /**
     * Retake photo - stop camera and restart.
     */
    async retakePhoto() {
        this.stopCamera();
        document.getElementById(`capture-result-${this.equipmentId}`).style.display = 'none';
        await new Promise(resolve => setTimeout(resolve, 100));  // Brief delay
        await this.startCamera();
    }
    
    /**
     * Save photo - convert canvas to blob and upload.
     */
    async savePhoto() {
        if (!this.canvas) {
            console.error('Canvas not found');
            alert('❌ No photo to save');
            return;
        }
        
        try {
            // Show upload status
            const statusDiv = document.getElementById(`upload-status-${this.equipmentId}`);
            statusDiv.textContent = '⏳ Compressing image...';
            statusDiv.style.display = 'block';
            
            // Convert canvas to blob with compression
            this.canvas.toBlob(
                async (blob) => {
                    await this.uploadImage(blob);
                },
                'image/jpeg',
                0.8  // 80% quality compression
            );
        } catch (error) {
            console.error('Photo save error:', error);
            alert(`❌ Failed to save photo: ${error.message}`);
        }
    }
    
    /**
     * Upload image blob to server.
     */
    async uploadImage(blob) {
        const statusDiv = document.getElementById(`upload-status-${this.equipmentId}`);
        
        try {
            statusDiv.textContent = '📤 Uploading...';
            
            const formData = new FormData();
            formData.append('image', blob, 'camera_capture.jpg');
            
            // Get image type from select field if available
            const imageTypeSelect = document.querySelector('select[name="image_type"]');
            if (imageTypeSelect) {
                formData.append('image_type', imageTypeSelect.value);
            }
            
            // Get caption from field if available
            const captionField = document.querySelector('textarea[name="caption"]');
            if (captionField) {
                formData.append('caption', captionField.value);
            }
            
            // Make API request
            const response = await fetch(
                `/equipment/api/equipment/${this.equipmentId}/capture-image/`,
                {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': this.csrfToken
                    }
                }
            );
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            
            if (data.success) {
                statusDiv.textContent = '✅ Photo saved successfully!';
                statusDiv.style.color = '#28a745';
                
                // Reset UI after delay
                setTimeout(() => {
                    this.resetUI();
                }, 2000);
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            statusDiv.textContent = `❌ Error: ${error.message}`;
            statusDiv.style.color = '#dc3545';
            
            // Hide error after 5 seconds
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }
    }
    
    /**
     * Reset UI to initial state.
     */
    resetUI() {
        this.stopCamera();
        document.getElementById(`capture-result-${this.equipmentId}`).style.display = 'none';
        document.getElementById(`upload-status-${this.equipmentId}`).style.display = 'none';
        document.getElementById(`camera-start-btn-${this.equipmentId}`).style.display = 'block';
        this.state = 'idle';
    }
    
    /**
     * Show fallback message when camera not supported.
     */
    showFallback(message) {
        const html = `
            <div class="camera-fallback">
                <p>${message}</p>
            </div>
        `;
        this.container.innerHTML += html;
    }
}

/**
 * Initialize camera widget on page load.
 */
document.addEventListener('DOMContentLoaded', function() {
    const cameraContainer = document.getElementById('camera-capture-widget');
    if (cameraContainer) {
        const equipmentId = cameraContainer.dataset.equipmentId;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        
        if (!equipmentId) {
            console.error('Equipment ID not found in container');
            return;
        }
        
        new CameraCapture('camera-capture-widget', equipmentId, csrfToken);
    }
});
