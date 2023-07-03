# Desc: Main file for radr
import io
import argparse
import os
import logging

from edgetpumodel import EdgeTPUModel
from utils import get_image_tensor
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("RadR starting")
    # get current direcory path and move up one level to models directory
    default_model_dir = 'models'
    default_model = 'yolov5s-int8-224_edgetpu.tflite'

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='.tflite model path',
                        default=os.path.join(default_model_dir,default_model))
    parser.add_argument("--names", type=str, default=os.path.join(default_model_dir,'coco.yaml'), help="Names file")
    parser.add_argument("--conf_thresh", type=float, default=0.25, help="model confidence threshold")
    parser.add_argument("--iou_thresh", type=float, default=0.45, help="NMS IOU threshold")
    args = parser.parse_args()

    print('Loading {} with {} labels.'.format(args.model, args.names))


    model = EdgeTPUModel(args.model, args.names, conf_thresh=args.conf_thresh, iou_thresh=args.iou_thresh)
    input_size = model.get_image_size()

    logger.info("Opening stream on device: {}".format(0))
        
    cam = cv2.VideoCapture(0)
    
    while True:
        try:
            res, image = cam.read()
            
            if res is False:
                logger.error("Empty image received")
                break
            else:
                full_image, net_image, pad = get_image_tensor(image, input_size[0])
                pred = model.forward(net_image)
                
                model.process_predictions(pred[0], full_image, pad)
                
                tinference, tnms = model.get_last_inference_time()
                logger.info("Frame done in {}".format(tinference+tnms))
        except KeyboardInterrupt:
            break
        
    cam.release()


if __name__ == "__main__":
    main()

