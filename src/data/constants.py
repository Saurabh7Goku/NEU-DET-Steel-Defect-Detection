"""Shared constants for the NEU-DET project."""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ImageNet normalization stats
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)

# Dataset paths (relative to project root)
IMAGES_DIR = os.path.join(PROJECT_ROOT, "data", "IMAGES")
ANNOTATIONS_DIR = os.path.join(PROJECT_ROOT, "data", "ANNOTATIONS")
VALIDATION_IMAGES_DIR = os.path.join(PROJECT_ROOT, "data", "validation_images")
VALIDATION_ANNOTATIONS_DIR = os.path.join(PROJECT_ROOT, "data", "validation_annotations")

# Checkpoints and ONNX output
CHECKPOINTS_DIR = os.path.join(PROJECT_ROOT, "checkpoints")
ONNX_DIR = os.path.join(PROJECT_ROOT, "onnx")

# Model hyperparameters
NUM_CLASSES = 6
IMAGE_SIZE = 256
BATCH_SIZE = 4
NUM_WORKERS = 0  # set to 6 if CUDA available
LEARNING_RATE = 5e-4
EPOCHS = 20
ACCUMULATION_STEPS = BATCH_SIZE  # 32 / batch_size

DEFECT_LABELS = [
    "crazing",
    "patches",
    "inclusion",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]
