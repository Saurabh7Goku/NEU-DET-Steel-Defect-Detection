from src.models.fpn_resnet import build_fpn_resnet
from src.models.fpn_inceptionv4 import build_fpn_inceptionv4
from src.models.fpn_xception import build_fpn_xception
from src.models.unet_resnet import build_unet_resnet

MODEL_REGISTRY = {
    "fpn_resnet": build_fpn_resnet,
    "fpn_inceptionv4": build_fpn_inceptionv4,
    "fpn_xception": build_fpn_xception,
    "unet_resnet": build_unet_resnet,
}


def build_model(name: str, pretrained: bool = True):
    """Build a segmentation model by name.

    Args:
        name: One of 'fpn_resnet', 'fpn_inceptionv4', 'fpn_xception', 'unet_resnet'.
        pretrained: Use ImageNet-pretrained encoder weights.
    """
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model '{name}'. Choose from: {list(MODEL_REGISTRY)}")
    return MODEL_REGISTRY[name](pretrained=pretrained)
