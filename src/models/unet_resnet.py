"""UNet with ResNet-34 encoder for steel surface defect segmentation."""

import segmentation_models_pytorch as smp

from src.data.constants import NUM_CLASSES, LEARNING_RATE, EPOCHS, CHECKPOINTS_DIR
from src.training.trainer import Trainer


def build_unet_resnet(pretrained=True):
    """Build a UNet model with a ResNet-34 encoder."""
    weights = "imagenet" if pretrained else None
    return smp.Unet(
        encoder_name="resnet34",
        encoder_weights=weights,
        in_channels=3,
        classes=NUM_CLASSES,
        activation=None,
    )


def train(epochs=EPOCHS, lr=LEARNING_RATE, checkpoint_path=None):
    """Train UNet + ResNet-34 and return the Trainer instance."""
    if checkpoint_path is None:
        import os
        checkpoint_path = os.path.join(CHECKPOINTS_DIR, "model_unet_resnet.pth")
    model = build_unet_resnet(pretrained=True)
    trainer = Trainer(model, lr, epochs, checkpoint_path)
    trainer.start()
    return trainer
