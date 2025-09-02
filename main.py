import asyncio
import base64
import json
import os
from typing import Dict

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from vision_processor import VisionProcessor

# Initialize FastAPI app
app = FastAPI(title="AI Gym Trainer")

# --- FILE PATHS & DIRECTORY SETUP ---
# It's better practice to define paths relative to this script's location.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Create the frontend directory if it doesn't exist to avoid startup errors
os.makedirs(FRONTEND_DIR, exist_ok=True)

# Mount the 'frontend' directory to serve static files like index.html, app.js, etc.
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# --- CONNECTION MANAGER ---
# A simple class to manage active WebSocket connections.
class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.vision_processor = VisionProcessor()

    async def connect(self, websocket: WebSocket):
        """Accepts a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Disconnects a WebSocket."""
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """Sends a message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- API ROUTES ---

@app.get("/")
async def read_root():
    """Serves the main HTML page."""
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles the WebSocket communication for video processing."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "frame":
                # Decode the base64 image data from the client
                image_data = base64.b64decode(data["image"].split(",")[1])
                np_arr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                # Process the frame using the VisionProcessor
                exercise_type = data.get("exercise_type", "bicep_curl")
                processed_data = manager.vision_processor.process_frame(frame, exercise_type)

                # Encode the processed image back to base64 to display on the frontend
                _, buffer = cv2.imencode(".jpg", processed_data["frame"])
                processed_image_b64 = base64.b64encode(buffer).decode("utf-8")

                # Prepare the response payload
                response = {
                    "type": "processed_data",
                    "rep_count": processed_data["rep_count"],
                    "feedback": processed_data["feedback"],
                    "image": f"data:image/jpeg;base64,{processed_image_b64}"
                }
                await websocket.send_json(response)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred in the WebSocket: {e}")
        manager.disconnect(websocket)


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    import uvicorn
    print("Starting AI Gym Trainer server...")
    print("Access the application at http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
