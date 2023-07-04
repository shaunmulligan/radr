# app.py
import threading
import logging
import cv2
import numpy as np
from fastapi import FastAPI
from starlette.responses import StreamingResponse
from detector import Detector
from norfair import Detection, Tracker, draw_tracked_objects


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class VideoCamera(object):
    def __init__(self):
        self.detector = Detector()
        self.tracker = Tracker(distance_function="euclidean", distance_threshold=100)

        # Get the initial frame from the detector
        self.current_frame, _ = self.detector.get_objects()

        # Start a background thread to keep updating the current frame
        threading.Thread(target=self.update_frame, daemon=True).start()

    def update_frame(self):
        while True:
            # get image and detected objects
            image, objs = self.detector.get_objects()

            # Convert detections to Norfair format
            norfair_detections = [Detection(np.array([[box[0], box[1]], [box[2], box[3]]])) for box in objs[0]]

            # Update the tracker with the new detections
            tracked_objects = self.tracker.update(detections=norfair_detections)

            # Perform tracking and draw tracked objects on the image
            draw_tracked_objects(image, tracked_objects)

            # Update current frame
            self.current_frame = image

    def get_frame(self):
        encoded_frame = cv2.imencode('.jpg', self.current_frame)[1].tobytes()
        return encoded_frame
    
    def close(self):
        self.detector.close()

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