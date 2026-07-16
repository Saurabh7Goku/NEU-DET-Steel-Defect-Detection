"""FPN with Xception encoder for steel surface defect segmentation."""

import segmentation_models_pytorch as smp

from src.data.constants import NUM_CLASSES, LEARNING_RATE, EPOCHS, CHECKPOINTS_DIR
from src.training.trainer import Trainer


def build_fpn_xception(pretrained=True):
    """Build an FPN model with an Xception encoder."""
    weights = "imagenet" if pretrained else None
    return smp.FPN(
        encoder_name="xception",
        encoder_weights=weights,
        in_channels=3,
        classes=NUM_CLASSES,
        activation=None,
    )


def train(epochs=EPOCHS, lr=LEARNING_RATE, checkpoint_path=None):
    """Train FPN + Xception and return the Trainer instance."""
    if checkpoint_path is None:
        import os
        checkpoint_path = os.path.join(CHECKPOINTS_DIR, "model_fpn_xception.pth")
    model = build_fpn_xception(pretrained=True)
    trainer = Trainer(model, lr, epochs, checkpoint_path)
    trainer.start()
    return trainer
