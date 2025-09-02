class GymAssistant {
    constructor() {
        // DOM Elements
        this.video = document.getElementById('videoElement');
        this.processedImage = document.getElementById('processedImage');
        this.startBtn = document.getElementById('startExercise');
        this.stopBtn = document.getElementById('stopExercise');
        this.exerciseSelect = document.getElementById('exerciseSelect');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.repCountEl = document.getElementById('repCount');
        this.feedbackEl = document.getElementById('feedback');

        // State
        this.ws = null;
        this.isExercising = false;
        this.currentStream = null;
        this.captureInterval = null;
    }

    init() {
        console.log('Initializing AI Gym Trainer...');
        this.setupEventListeners();
        this.connectWebSocket();
    }

    setupEventListeners() {
        this.startBtn.addEventListener('click', () => this.startExercise());
        this.stopBtn.addEventListener('click', () => this.stopExercise());
        this.exerciseSelect.addEventListener('change', () => this.resetStats());
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        console.log(`Connecting to WebSocket: ${wsUrl}`);
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'processed_data') {
                this.handleProcessedData(data);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            this.stopExercise(); // Stop everything if connection is lost
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.connectionStatus.className = 'connection-status connected';
            this.connectionStatus.innerHTML = '🟢 Connected to server';
        } else {
            this.connectionStatus.className = 'connection-status disconnected';
            this.connectionStatus.innerHTML = '🔴 Disconnected. Please refresh the page.';
        }
    }

    async startExercise() {
        console.log('Starting exercise...');
        try {
            this.currentStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
            this.video.srcObject = this.currentStream;
            this.video.style.display = 'none'; // Keep the raw video feed hidden
            this.processedImage.style.display = 'block';

            this.isExercising = true;
            this.updateButtons();
            this.resetStats();

            // Start sending frames to the server every 100ms (~10 FPS)
            this.captureInterval = setInterval(() => {
                this.sendFrame();
            }, 100);

        } catch (error) {
            console.error('Error accessing webcam:', error);
            alert('Could not access the webcam. Please ensure it is enabled and permissions are granted.');
        }
    }

    stopExercise() {
        console.log('Stopping exercise...');
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
        }
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
        }

        this.isExercising = false;
        this.updateButtons();
        this.processedImage.src = 'https://placehold.co/640x480/1a2a6c/ffffff?text=Camera+is+off';
    }
    
    sendFrame() {
        if (!this.isExercising || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        const canvas = document.createElement('canvas');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(this.video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');
        
        const payload = {
            type: 'frame',
            image: imageData,
            exercise_type: this.exerciseSelect.value,
        };
        this.ws.send(JSON.stringify(payload));
    }

    handleProcessedData(data) {
        this.repCountEl.textContent = data.rep_count;
        this.feedbackEl.textContent = data.feedback;
        this.processedImage.src = data.image; // Update the image with the processed one from the server
    }
    
    updateButtons() {
        this.startBtn.disabled = this.isExercising;
        this.stopBtn.disabled = !this.isExercising;
        this.exerciseSelect.disabled = this.isExercising;
    }

    resetStats() {
        this.repCountEl.textContent = 0;
        this.feedbackEl.textContent = 'Waiting...';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const app = new GymAssistant();
    app.init();
});
