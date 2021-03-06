import numpy as np
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import yaml

class Detectron2:

    def __init__(self):

        self.cfg = get_cfg()
        self.cfg.merge_from_file("detectron2/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
        self.cfg.MODEL.WEIGHTS = "detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl"
        self.predictor = DefaultPredictor(self.cfg)
        self.config = yaml.load(open('config.yaml', 'r'))
        self.all_classes = self.config['CLASSES']['ALL']
        self.required_classes = self.config['CLASSES']['RIGID'] + self.config['CLASSES']['NON_RIGID']
    
    def bbox(self, img):

        rows = np.any(img, axis=1)
        cols = np.any(img, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        return cmin, rmin, cmax, rmax

    def detect(self, im):
        
        outputs = self.predictor(im)
        boxes   = outputs["instances"].pred_boxes.tensor.cpu().numpy()
        classes = outputs["instances"].pred_classes.cpu().numpy()
        scores  = outputs["instances"].scores.cpu().numpy()
        masks   = outputs['instances'].pred_masks.cpu().numpy()

        bbox_xywh, cls_score, cls_ids, detections = [], [], [], []
        
        for (box, _class, score) in zip(boxes, classes, scores):
            if(self.all_classes[_class] in self.required_classes):
                x0, y0, x1, y1 = box
                detections.append([x0, y0, x1, y1, score])
                bbox_xywh.append([(x1 + x0)/2, (y1 + y0)/2, (x1 - x0), (y1 - y0)])
                cls_score.append(score)
                cls_ids.append(_class)
        
        boxes   = np.array(bbox_xywh, dtype=np.float64)
        scores  = np.array(cls_score)
        cls_ids = np.array(cls_ids)
        dets    = np.array(detections, dtype=np.float64)

        output = (boxes, scores, cls_ids, dets, masks)
        
        return output