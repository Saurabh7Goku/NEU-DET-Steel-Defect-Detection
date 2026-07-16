"""PyTorch datasets for training and inference."""

import os

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from albumentations import Compose, HorizontalFlip, Normalize, Resize
from albumentations.pytorch import ToTensorV2

from src.data.constants import MEAN, STD, IMAGE_SIZE, DEFECT_LABELS
from src.data.masks import create_filepaths, make_mask


class SegmentationDataset(Dataset):
    """Training/validation dataset that reads images + Pascal VOC XML masks."""

    def __init__(self, df, image_folder, annot_folder, mean=MEAN, std=STD, phase="train"):
        self.df = df
        self.image_folder = image_folder
        self.annot_folder = annot_folder
        self.phase = phase
        self.fnames = df["Name"].tolist()
        self.labels = {col: 1 for col in DEFECT_LABELS}
        self.transform = self._build_transforms(mean, std)

    def __len__(self):
        return len(self.fnames)

    def __getitem__(self, index):
        name = self.fnames[index]
        image_path = os.path.join(self.image_folder, f"{name}.jpg")
        annot_path = os.path.join(self.annot_folder, f"{name}.xml")
        row = self.df.iloc[index]
        label_dict = {col: int(row[col]) for col in DEFECT_LABELS}

        image = cv2.imread(image_path)
        mask = make_mask(annot_path, label_dict)

        augmented = self.transform(image=image, mask=mask)
        image = augmented["image"]
        mask = augmented["mask"]
        if isinstance(mask, np.ndarray):
            mask = torch.from_numpy(mask.transpose(2, 0, 1)).float()
        else:
            mask = mask.permute(2, 0, 1).float()
        return image, mask

    @staticmethod
    def _build_transforms(mean, std):
        transforms = []
        transforms.append(Normalize(mean=mean, std=std, p=1))
        transforms.append(Resize(IMAGE_SIZE, IMAGE_SIZE))
        transforms.append(ToTensorV2())
        return Compose(transforms)


class SegmentationTrainDataset(SegmentationDataset):
    """Training split with horizontal-flip augmentation."""

    def __init__(self, df, image_folder, annot_folder, mean=MEAN, std=STD):
        super().__init__(df, image_folder, annot_folder, mean, std, phase="train")

    @staticmethod
    def _build_transforms(mean, std):
        return Compose([
            HorizontalFlip(p=0.5),
            Normalize(mean=mean, std=std, p=1),
            Resize(IMAGE_SIZE, IMAGE_SIZE),
            ToTensorV2(),
        ])


class InferenceDataset(Dataset):
    """Single-image dataset for inference."""

    def __init__(self, image_path, mean=MEAN, std=STD):
        self.image_path = image_path
        self.fname = os.path.splitext(os.path.basename(image_path))[0]
        self.transform = Compose([
            Normalize(mean=mean, std=std, p=1),
            Resize(IMAGE_SIZE, IMAGE_SIZE),
            ToTensorV2(),
        ])

    def __len__(self):
        return 1

    def __getitem__(self, idx):
        image = cv2.imread(self.image_path)
        image = self.transform(image=image)["image"]
        return self.fname, image


class ValidationDataset(Dataset):
    """Dataset over the held-out validation images/annotations."""

    def __init__(self, annot_dir, image_dir, mean=MEAN, std=STD):
        self.df = create_filepaths(annot_dir)
        self.image_dir = image_dir
        self.annot_dir = annot_dir
        self.labels = {col: 1 for col in DEFECT_LABELS}
        self.transform = Compose([
            Normalize(mean=mean, std=std, p=1),
            Resize(IMAGE_SIZE, IMAGE_SIZE),
            ToTensorV2(),
        ])

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        name = row["Name"]
        image = cv2.imread(os.path.join(self.image_dir, f"{name}.jpg"))
        label_dict = {col: int(row[col]) for col in DEFECT_LABELS}
        mask = make_mask(os.path.join(self.annot_dir, f"{name}.xml"), label_dict)
        augmented = self.transform(image=image, mask=mask)
        image_tensor = augmented["image"]
        mask_tensor = augmented["mask"]
        if isinstance(mask_tensor, np.ndarray):
            mask_tensor = torch.from_numpy(mask_tensor.transpose(2, 0, 1)).float()
        else:
            mask_tensor = mask_tensor.permute(2, 0, 1).float()
        return image_tensor, mask_tensor
