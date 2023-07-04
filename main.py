# app.py
import threading
import cv2
import numpy as np
from fastapi import FastAPI
from starlette.responses import StreamingResponse
from detector import Detector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class VideoCamera(object):
    def __init__(self):
        self.video = Detector()
        self.current_frame = self.video.get_objects()[0]

        # Start a background thread to keep updating the current frame
        threading.Thread(target=self.update_frame, daemon=True).start()

    def get_frame(self):
        encoded_frame = cv2.imencode('.jpg', self.current_frame)[1].tobytes()
        return encoded_frame

    def update_frame(self):
        while True:
            self.current_frame = self.video.get_objects()[0]
    
    def close(self):
        self.video.close()

camera = VideoCamera()

@app.get('/')
def index():
    return "Video Streaming is running. Use endpoint /video to access the stream."

@app.get("/video")
async def video_feed():
    def gen():
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + camera.get_frame() + b'\r\n\r\n')

    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.on_event("shutdown")
def shutdown_event():
    # Clean up resources when the app is stopped
    logger.info("Shutting down...")
    camera.close()