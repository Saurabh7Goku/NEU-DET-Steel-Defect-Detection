#!/usr/bin/env python
"""FastAPI backend for NEU-DET Steel Surface Defect Detection.

Run:
    python app.py
    # or: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
"""

import base64
import io
import os
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image

from src.data.constants import (
    DEFECT_LABELS,
    IMAGE_SIZE,
    MEAN,
    NUM_CLASSES,
    ONNX_DIR,
    STD,
    VALIDATION_IMAGES_DIR,
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="NEU-DET Steel Defect Detection API")

# In production, set ALLOWED_ORIGINS to your Vercel domain, e.g.:
#   https://your-app.vercel.app
# For development, localhost origins are included automatically.
import os

_ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# ONNX session (loaded once at startup)
# ---------------------------------------------------------------------------
import onnxruntime as ort

ONNX_PATH = os.path.join(ONNX_DIR, "steel_defect_fpn_efficientnet-b3.onnx")
_session: ort.InferenceSession | None = None

# Hugging Face model repo to download from if file is missing
HF_MODEL_REPO = os.environ.get(
    "HF_MODEL_REPO", "Saurabhgk2303/steel-defect-detection-model"
)


def _ensure_model():
    """Download the ONNX model from Hugging Face Model Hub if not present."""
    if os.path.exists(ONNX_PATH):
        return
    print(f"[...] Downloading model from hf.co/{HF_MODEL_REPO} ...")
    os.makedirs(ONNX_DIR, exist_ok=True)
    # Use huggingface_hub to download with resume support
    from huggingface_hub import hf_hub_download

    hf_hub_download(
        repo_id=HF_MODEL_REPO,
        filename="model.onnx",
        local_dir=ONNX_DIR,
        local_dir_use_symlinks=False,
        token=os.environ.get("HF_TOKEN"),
        resume_download=True,
    )
    # Rename from model.onnx to the expected filename
    downloaded = os.path.join(ONNX_DIR, "model.onnx")
    if downloaded != ONNX_PATH and os.path.exists(downloaded):
        import shutil

        shutil.move(downloaded, ONNX_PATH)
    print(f"[OK] Model downloaded to {ONNX_PATH}")


def _get_session() -> ort.InferenceSession:
    global _session
    if _session is None:
        _ensure_model()
        if not os.path.exists(ONNX_PATH):
            raise RuntimeError(f"ONNX model not found at {ONNX_PATH}")
        _session = ort.InferenceSession(ONNX_PATH)
    return _session


@app.on_event("startup")
def _load_model():
    _get_session()
    print(f"[OK] ONNX model loaded from {ONNX_PATH}")


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------
def _preprocess(img_rgb: np.ndarray) -> np.ndarray:
    """Resize → float → normalize → HWC→CHW → add batch dim."""
    resized = cv2.resize(img_rgb, (IMAGE_SIZE, IMAGE_SIZE))
    arr = resized.astype(np.float32) / 255.0
    arr = (arr - np.array(MEAN)) / np.array(STD)
    arr = arr.transpose(2, 0, 1)  # CHW
    return np.expand_dims(arr, 0).astype(np.float32)  # NCHW — ensure float32 for ONNX


# ---------------------------------------------------------------------------
# Defect overlay colours (BGR for cv2)
# ---------------------------------------------------------------------------
COLORS = np.array(
    [
        [56, 56, 255],    # crazing — red
        [151, 189, 255],  # patches — light blue
        [8, 232, 222],    # inclusion — teal
        [52, 168, 83],    # pitted_surface — green
        [255, 210, 63],   # rolled-in_scale — yellow
        [190, 50, 240],   # scratches — purple
    ],
    dtype=np.uint8,
)


# ---------------------------------------------------------------------------
# Shared inference (used by both FastAPI and Gradio)
# ---------------------------------------------------------------------------
def run_prediction(img_rgb: np.ndarray) -> dict:
    """Run ONNX inference on an RGB image. Returns predictions + base64 overlay."""
    blob = _preprocess(img_rgb)
    input_name = _get_session().get_inputs()[0].name
    output = _get_session().run(None, {input_name: blob})[0]

    probs = 1.0 / (1.0 + np.exp(-output[0]))
    confidences = {
        DEFECT_LABELS[i]: float(probs[i].mean()) for i in range(NUM_CLASSES)
    }

    resized = cv2.resize(img_rgb, (IMAGE_SIZE, IMAGE_SIZE))
    top_idx = int(probs.mean(axis=(1, 2)).argmax())
    mask = probs[top_idx] > 0.5
    overlay = resized.copy()
    color = COLORS[top_idx][::-1]
    overlay[mask] = (overlay[mask] * 0.5 + color * 0.5).astype(np.uint8)

    overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode(".png", overlay_bgr)
    overlay_b64 = base64.b64encode(buf).decode()

    ranked = sorted(confidences.items(), key=lambda x: x[1], reverse=True)

    return {
        "predictions": [
            {"class": cls, "confidence": round(conf, 4)} for cls, conf in ranked
        ],
        "overlay": f"data:image/png;base64,{overlay_b64}",
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/model-info")
def model_info():
    return {
        "model": Path(ONNX_PATH).stem,
        "input_size": IMAGE_SIZE,
        "num_classes": NUM_CLASSES,
        "classes": DEFECT_LABELS,
    }


@app.get("/api/samples")
def list_samples():
    """Return available validation images grouped by defect class."""
    samples: dict[str, list[str]] = {}
    val_dir = Path(VALIDATION_IMAGES_DIR)
    if not val_dir.exists():
        return {"samples": samples}

    for cls in DEFECT_LABELS:
        files = sorted(val_dir.glob(f"{cls}_*.jpg"))[:2]  # 2 per class
        samples[cls] = [f.name for f in files]
    return {"samples": samples}


@app.get("/api/sample/{name}")
def get_sample(name: str):
    fpath = Path(VALIDATION_IMAGES_DIR) / name
    if not fpath.exists():
        raise HTTPException(404, f"Sample {name} not found")
    return FileResponse(fpath, media_type="image/jpeg")


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    """Accept an image, return per-class confidence + base64 overlay."""
    raw = await file.read()
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img_np = np.array(img)
    return run_prediction(img_np)


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
