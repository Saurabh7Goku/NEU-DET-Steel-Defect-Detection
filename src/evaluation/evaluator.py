"""Evaluate a trained segmentation checkpoint against the validation set."""

import os
from collections import OrderedDict

import numpy as np
import torch
from torch.utils.data import DataLoader

from src.data.dataset import ValidationDataset
from src.data.constants import VALIDATION_ANNOTATIONS_DIR, VALIDATION_IMAGES_DIR
from src.models import build_model


def load_checkpoint(model, ckpt_path):
    """Load a training checkpoint, stripping DataParallel 'module.' prefix."""
    checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    state_dict = checkpoint.get("state_dict", checkpoint)
    cleaned = OrderedDict()
    for k, v in state_dict.items():
        cleaned[k[7:]] = v if k.startswith("module.") else v
        cleaned[k] = v
    model.load_state_dict(cleaned)
    return model


def evaluate(model_name: str, ckpt_path: str, batch_size: int = 2):
    """Run evaluation on the held-out validation set.

    Returns:
        dict with keys 'mean_dice', 'mean_iou', 'per_class_dice'.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(model_name, pretrained=False)
    model = load_checkpoint(model, ckpt_path)
    model.eval()
    model.to(device)

    dataset = ValidationDataset(VALIDATION_ANNOTATIONS_DIR, VALIDATION_IMAGES_DIR)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    total_dice = 0.0
    total_iou = 0.0
    count = 0

    with torch.no_grad():
        for images, masks in loader:
            images = images.to(device)
            masks = masks.to(device)
            logits = model(images)
            probs = torch.sigmoid(logits)

            # Per-sample dice
            batch_size_actual = images.size(0)
            for i in range(batch_size_actual):
                p = (probs[i] > 0.5).float()
                t = masks[i]
                intersection = (p * t).sum()
                union = p.sum() + t.sum()
                dice = (2 * intersection / union).item() if union > 0 else 0.0
                total_dice += dice

                pred_np = p.cpu().numpy().astype(bool)
                gt_np = t.cpu().numpy().astype(bool)
                inter = np.logical_and(pred_np, gt_np).sum()
                u = np.logical_or(pred_np, gt_np).sum()
                iou = inter / u if u > 0 else 0.0
                total_iou += iou
                count += 1

    results = {
        "mean_dice": total_dice / max(count, 1),
        "mean_iou": total_iou / max(count, 1),
        "num_samples": count,
    }
    print(f"Validation — Dice: {results['mean_dice']:.4f} | IoU: {results['mean_iou']:.4f} | Samples: {count}")
    return results
