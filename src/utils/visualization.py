"""Plotting helpers for training metrics and predictions."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_training_curves(trainer, save_path="training_curves.png"):
    """Plot loss, dice, and IoU curves from a Trainer instance."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, (key, label) in zip(axes, [
        ("losses", "BCE Loss"),
        ("dice_scores", "Dice Score"),
        ("iou_scores", "IoU Score"),
    ]):
        scores = getattr(trainer, key)
        epochs = range(len(scores["train"]))
        ax.plot(epochs, scores["train"], label="train")
        ax.plot(epochs, scores["val"], label="val")
        ax.set_title(label)
        ax.set_xlabel("Epoch")
        ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Training curves saved to {save_path}")


def plot_predictions(images, masks, preds, num_samples=4, save_path="predictions.png"):
    """Visualize ground truth masks vs predicted masks."""
    num_samples = min(num_samples, len(images))
    fig, axes = plt.subplots(num_samples, 3, figsize=(12, 4 * num_samples))
    if num_samples == 1:
        axes = axes[np.newaxis, :]

    for i in range(num_samples):
        img = images[i].permute(1, 2, 0).cpu().numpy()
        img = (img - img.min()) / (img.max() - img.min())
        gt = masks[i].permute(1, 2, 0).cpu().numpy().max(axis=-1)
        pred = preds[i].permute(1, 2, 0).cpu().numpy().max(axis=-1)

        axes[i, 0].imshow(img)
        axes[i, 0].set_title("Image")
        axes[i, 1].imshow(gt, cmap="gray")
        axes[i, 1].set_title("Ground Truth")
        axes[i, 2].imshow(pred, cmap="gray")
        axes[i, 2].set_title("Prediction")
        for ax in axes[i]:
            ax.axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Predictions saved to {save_path}")
