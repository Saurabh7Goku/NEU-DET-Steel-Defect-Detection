"""Dice score and IoU metrics for segmentation evaluation."""

import numpy as np
import torch


class Meter:
    """Tracks Dice and IoU scores across an epoch."""

    def __init__(self, phase: str, epoch: int):
        self.base_threshold = 0.5
        self.dice_scores = []
        self.dice_neg_scores = []
        self.dice_pos_scores = []
        self.iou_scores = []
        self.phase = phase
        self.epoch = epoch

    def update(self, targets, outputs):
        probs = torch.sigmoid(outputs)
        dice, dice_neg, dice_pos, _, _ = self._dice_metric(probs, targets, self.base_threshold)
        self.dice_scores.extend(dice.tolist())
        self.dice_pos_scores.extend(dice_pos.tolist())
        self.dice_neg_scores.extend(dice_neg.tolist())
        preds = self._predict(probs, self.base_threshold)
        iou = self._compute_iou_batch(preds, targets, classes=[1])
        self.iou_scores.append(iou)

    def get_metrics(self):
        dice = np.nanmean(self.dice_scores)
        dice_neg = np.nanmean(self.dice_neg_scores)
        dice_pos = np.nanmean(self.dice_pos_scores)
        iou = np.nanmean(self.iou_scores)
        return [dice, dice_neg, dice_pos], iou

    @staticmethod
    def _predict(x, threshold):
        return (x.cpu().numpy() > threshold).astype("uint8")

    @staticmethod
    def _dice_metric(probability, truth, threshold=0.5):
        batch_size = len(truth)
        with torch.no_grad():
            p = (probability > threshold).float()
            t = (truth > 0.5).float()
            t_sum = t.sum(-1)
            p_sum = p.sum(-1)
            neg_index = torch.nonzero(t_sum == 0)
            pos_index = torch.nonzero(t_sum >= 1)
            dice_neg = (p_sum == 0).float()
            dice_pos = 2 * (p * t).sum(-1) / ((p + t).sum(-1))
            dice_neg = dice_neg[neg_index]
            dice_pos = dice_pos[pos_index]
            dice = torch.cat([dice_pos, dice_neg])
        return dice, dice_neg, dice_pos, len(neg_index), len(pos_index)

    def _compute_ious(self, pred, label, classes, ignore_index=255, only_present=True):
        pred = pred.copy()
        pred[label == ignore_index] = 0
        ious = []
        for c in classes:
            label_c = label == c
            if only_present and np.sum(label_c) == 0:
                ious.append(np.nan)
                continue
            pred_c = pred == c
            intersection = np.logical_and(pred_c, label_c).sum()
            union = np.logical_or(pred_c, label_c).sum()
            if union != 0:
                ious.append(intersection / union)
        return ious if ious else [1]

    def _compute_iou_batch(self, outputs, labels, classes=None):
        ious = []
        preds = np.copy(outputs)
        labels = np.array(labels)
        for pred, label in zip(preds, labels):
            ious.append(np.nanmean(self._compute_ious(pred, label, classes)))
        return np.nanmean(ious)
