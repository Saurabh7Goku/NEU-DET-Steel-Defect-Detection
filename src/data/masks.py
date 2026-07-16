"""Utilities for parsing Pascal VOC XML annotations and creating binary masks."""

import os
import xml.etree.ElementTree as ET
from itertools import product

import numpy as np
import pandas as pd


def create_filepaths(annot_folder: str) -> pd.DataFrame:
    """Parse all XML annotations in a folder and return a label DataFrame.

    Columns: Name, crazing, patches, inclusion, pitted_surface,
             rolled-in_scale, scratches, Number_of_Defects.
    """
    rows = []
    for fname in sorted(os.listdir(annot_folder)):
        if not fname.endswith(".xml"):
            continue
        tree = ET.parse(os.path.join(annot_folder, fname))
        root = tree.getroot()
        labels = {elem.text for elem in root.iter("name")}
        row = {"Name": fname[:-4]}
        for label in ("crazing", "patches", "inclusion", "pitted_surface", "rolled-in_scale", "scratches"):
            row[label] = 1 if label in labels else 0
        row["Number_of_Defects"] = sum(1 for v in row.values() if v == 1)
        rows.append(row)
    df = pd.DataFrame(rows)
    cols = ["Name", "crazing", "patches", "inclusion", "pitted_surface", "rolled-in_scale", "scratches", "Number_of_Defects"]
    return df[cols]


def make_mask(annot_path: str, labels: dict) -> np.ndarray:
    """Create a multi-channel binary mask from a Pascal VOC XML annotation.

    Args:
        annot_path: Path to the XML annotation file.
        labels: Dict mapping label name -> 1/0 indicating presence.

    Returns:
        np.ndarray of shape (H, W, num_label_channels) with dtype uint8.
    """
    tree = ET.parse(annot_path)
    root = tree.getroot()
    width = int(root.find(".//size/width").text)
    height = int(root.find(".//size/height").text)
    masks = np.zeros((height, width, len(labels)), dtype=np.uint8)

    for idx, label in enumerate(labels):
        if labels[label] != 1:
            continue
        mask = np.zeros((height, width), dtype=np.uint8)
        for obj in root.findall(".//object"):
            if obj.find("name").text != label:
                continue
            for box in obj.findall("bndbox"):
                xmin = int(box.find("xmin").text)
                ymin = int(box.find("ymin").text)
                xmax = int(box.find("xmax").text)
                ymax = int(box.find("ymax").text)
                coords = np.array(list(product(range(ymin, ymax), range(xmin, xmax))))
                mask[coords[:, 0], coords[:, 1]] = 1
        masks[:, :, idx] = mask

    return masks
