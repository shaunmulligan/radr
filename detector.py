# detector.py

import cv2
import os
import logging
from edgetpumodel import EdgeTPUModel
from utils import get_image_tensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Detector:
    def __init__(self, model_path='models/yolov5s-int8-224_edgetpu.tflite', names_path='models/coco.yaml', conf_thresh=0.40, iou_thresh=0.45, cam_id=0):
        logger.info('Loading {} with {} labels and using camera: .'.format(model_path, names_path, cam_id))
        self.model = EdgeTPUModel(model_path, names_path, conf_thresh=conf_thresh, iou_thresh=iou_thresh)
        self.input_size = self.model.get_image_size()
        self.cam = cv2.VideoCapture(cam_id)

    def get_objects(self):
        res, image = self.cam.read()

        if res is False:
            raise Exception("Empty image received")

        full_image, net_image, pad = get_image_tensor(image, self.input_size[0])
        pred = self.model.forward(net_image)
        processed_pred = self.model.process_predictions(pred[0], full_image, pad)

        tinference, tnms = self.model.get_last_inference_time()
        logger.info('Frame done in {}'.format(tinference+ tnms))

        return image, processed_pred

    def close(self):
        self.cam.release()
        logger.info("Camera released")
