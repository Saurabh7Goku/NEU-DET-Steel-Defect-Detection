"""Training and validation loop for segmentation models."""

import os
import time

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.data.dataset import SegmentationTrainDataset
from src.data.masks import create_filepaths
from src.training.metrics import Meter
from src.data.constants import (
    BATCH_SIZE, NUM_WORKERS, ACCUMULATION_STEPS,
    MEAN, STD, IMAGES_DIR, ANNOTATIONS_DIR, DEFECT_LABELS,
)


class Trainer:
    """Handles the full training lifecycle: train/val loop, checkpointing, metrics."""

    def __init__(self, model, lr, epochs, checkpoint_path):
        self.batch_size = {"train": BATCH_SIZE, "val": BATCH_SIZE}
        self.num_workers = NUM_WORKERS if torch.cuda.is_available() else 0
        self.accumulation_steps = ACCUMULATION_STEPS
        self.lr = lr
        self.num_epochs = epochs
        self.epochs_passed = 0
        self.best_loss = float("inf")
        self.best_dice = 0.0
        self.phases = ["train", "val"]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = model
        self.criterion = nn.BCEWithLogitsLoss()
        self.optimizer = optim.Adam(self.net.parameters(), lr=self.lr)
        self.scheduler = ReduceLROnPlateau(self.optimizer, mode="max", patience=3)

        self.net = nn.DataParallel(self.net)
        self.net = self.net.to(self.device)

        self.checkpoint_path = checkpoint_path
        if os.path.exists(self.checkpoint_path):
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
            self.net.load_state_dict(checkpoint["state_dict"])
            self.optimizer.load_state_dict(checkpoint["optimizer"])
            self.epochs_passed = checkpoint["epoch"]
            self.best_loss = checkpoint["best_loss"]
            self.best_dice = checkpoint["best_dice"]
            print(f"Resumed from checkpoint: epoch {self.epochs_passed}, best_dice={self.best_dice:.4f}")

        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)

        self.dataloaders = {
            phase: self._make_dataloader(phase) for phase in self.phases
        }
        self.losses = {phase: [] for phase in self.phases}
        self.iou_scores = {phase: [] for phase in self.phases}
        self.dice_scores = {phase: [] for phase in self.phases}

    def _make_dataloader(self, phase):
        df = create_filepaths(ANNOTATIONS_DIR)
        # Simple 80/20 split within training data (validation images are held out separately)
        if phase == "train":
            df_split = df.sample(frac=0.8, random_state=42)
        else:
            df_split = df.sample(frac=0.2, random_state=42)

        if phase == "train":
            dataset = SegmentationTrainDataset(df_split, IMAGES_DIR, ANNOTATIONS_DIR, MEAN, STD)
        else:
            from src.data.dataset import SegmentationDataset
            dataset = SegmentationDataset(df_split, IMAGES_DIR, ANNOTATIONS_DIR, MEAN, STD, phase="val")

        return DataLoader(
            dataset,
            batch_size=self.batch_size[phase],
            num_workers=self.num_workers,
            shuffle=(phase == "train"),
        )

    def forward(self, images, targets):
        images = images.to(self.device)
        masks = targets.to(self.device)
        outputs = self.net(images)
        loss = self.criterion(outputs, masks)
        return loss, outputs

    def iterate(self, epoch, phase):
        meter = Meter(phase, epoch)
        start = time.strftime("%H:%M:%S")
        print(f"Starting epoch: {epoch} | phase: {phase} | time: {start}")

        self.net.train(phase == "train")
        dataloader = self.dataloaders[phase]
        running_loss = 0.0
        total_batches = len(dataloader)

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        tk0 = tqdm(dataloader, total=total_batches)
        for itr, batch in enumerate(tk0):
            images, targets = batch
            loss, outputs = self.forward(images, targets)
            loss = loss / self.accumulation_steps

            if phase == "train":
                loss.backward()
                if (itr + 1) % self.accumulation_steps == 0:
                    self.optimizer.step()
                    self.optimizer.zero_grad()

            running_loss += loss.item()
            meter.update(targets, outputs)
            tk0.set_postfix(loss=loss.item())

        epoch_loss = running_loss / total_batches
        dices, iou = meter.get_metrics()
        self.losses[phase].append(epoch_loss)
        self.dice_scores[phase].append(dices[0])
        self.iou_scores[phase].append(iou)

        print(f"Epoch {epoch} | {phase} loss: {epoch_loss:.4f} | dice: {dices[0]:.4f} | iou: {iou:.4f}")
        return epoch_loss, dices[0]

    def start(self):
        for epoch in range(self.epochs_passed, self.num_epochs):
            self.net.train()
            train_loss, train_dice = self.iterate(epoch, "train")
            with torch.no_grad():
                val_loss, val_dice = self.iterate(epoch, "val")

            self.scheduler.step(val_dice)

            if val_dice > self.best_dice:
                self.best_dice = val_dice
                self._save_checkpoint(epoch, train_loss, val_loss)
                print(f"  >> New best dice: {val_dice:.4f} — model saved")

            self.epochs_passed = epoch + 1

        print(f"Training complete. Best dice: {self.best_dice:.4f}")

    def _save_checkpoint(self, epoch, train_loss, val_loss):
        state = {
            "epoch": epoch,
            "state_dict": self.net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "best_loss": self.best_loss,
            "best_dice": self.best_dice,
            "train_loss": train_loss,
            "val_loss": val_loss,
        }
        torch.save(state, self.checkpoint_path)
