__all__ = ["MantisMaskRCNN"]

from mantisshrimp.imports import *
from mantisshrimp.core import *
from mantisshrimp.models.mantis_rcnn.rcnn_param_groups import *
from mantisshrimp.models.mantis_rcnn.mantis_rcnn import *
from mantisshrimp.models.mantis_rcnn.mantis_faster_rcnn import *


class MantisMaskRCNN(MantisRCNN):
    @delegates(MaskRCNN.__init__)
    def __init__(self, n_class, h=256, pretrained=True, metrics=None, **kwargs):
        super().__init__(metrics=metrics)
        self.n_class, self.h, self.pretrained = n_class, h, pretrained
        self.m = maskrcnn_resnet50_fpn(pretrained=self.pretrained, **kwargs)
        in_features = self.m.roi_heads.box_predictor.cls_score.in_features
        self.m.roi_heads.box_predictor = FastRCNNPredictor(in_features, self.n_class)
        in_features_mask = self.m.roi_heads.mask_predictor.conv5_mask.in_channels
        self.m.roi_heads.mask_predictor = MaskRCNNPredictor(
            in_features_mask, self.h, self.n_class
        )

    def forward(self, images, targets=None):
        return self.m(images, targets)

    def model_splits(self):
        return split_rcnn_model(self.m)

    @staticmethod
    def build_training_sample(
        imageid: int,
        img: np.ndarray,
        label: List[int],
        bbox: List[BBox],
        mask: MaskArray,
        **kwargs,
    ):
        x, y = MantisFasterRCNN.build_training_sample(
            imageid=imageid, img=img, label=label, bbox=bbox,
        )
        y["masks"] = tensor(mask.data, dtype=torch.uint8)
        return x, y