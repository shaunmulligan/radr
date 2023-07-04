import glob
import threading
import logging
import cv2
import numpy as np
from fastapi import FastAPI
from starlette.responses import StreamingResponse
from detector import Detector
from norfair import Detection, Tracker, draw_points

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class VideoCamera(object):
    def __init__(self, input=0):
        self.detector = Detector(input_source=input)
        self.tracker = Tracker(distance_function="euclidean", distance_threshold=150)

        # Get the initial frame from the detector
        self.current_frame, _ = self.detector.get_objects()

        # Start a background thread to keep updating the current frame
        threading.Thread(target=self.update_frame, daemon=True).start()

    def update_frame(self):
        while True:
            # get image and detected objects
            image, objs = self.detector.get_objects()

            # Convert detections to Norfair format
            norfair_detections = [Detection(np.array([[box[0], box[1]], [box[2], box[3]]]), scores=np.array([box[4], box[4]])) for box in objs[0]]

            # Update the tracker with the new detections
            tracked_objects = self.tracker.update(detections=norfair_detections)
            logger.info("Tracked objects: {}".format(tracked_objects))
            # Draw the points of each tracked object
            draw_points(image, drawables=tracked_objects, radius=5, color='by_id', draw_ids=True, draw_labels=False)

            # Update current frame
            self.current_frame = image

    def get_frame(self):
        encoded_frame = cv2.imencode('.jpg', self.current_frame)[1].tobytes()
        return encoded_frame
    
    def close(self):
        self.detector.close()

# If a file with *.mp4 extension is found in the root folder, it will be used as input else use camera 0
video_files = glob.glob("*.mp4")

if video_files:
    logger.info("Found video file: {}".format(video_files[0]))
    camera = VideoCamera(input=video_files[0])
else:
    logger.info("No video file found, using camera 0")
    camera = VideoCamera(input=0)

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