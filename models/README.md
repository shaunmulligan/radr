# Models:

Currently we only have the one model, which is `yolov5s-int8-224_edgetpu.tflite`, which was taken from the [edgetpu-yolo project](https://github.com/jveitchmichaelis/edgetpu-yolo/blob/main/yolov5s-int8-224_edgetpu.tflite).

This model is a YOLOv5s model that has been quantized to run on the Coral.ai TPU accelerator. It was trained on the [COCO dataset](https://cocodataset.org/#home) and is capable of detecting 80 different classes of objects. The plan is to fine-tune the yolov5s model on a custom dataset of images from our usecase, but for now we are using this model as a proof of concept.