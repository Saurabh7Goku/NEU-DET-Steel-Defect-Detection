#!/usr/bin/env python
"""Entry point for Hugging Face Spaces (Gradio SDK).

This wraps the existing FastAPI app with a minimal Gradio UI so the
Space stays warm on the free tier. All `/api/*` routes from `app.py`
continue to work normally — the Vercel frontend talks to them directly.
"""

import os
os.environ["GRADIO_SSR_MODE"] = "False"

import gradio as gr
import spaces
import numpy as np
import cv2
from PIL import Image

from src.data.constants import (
    DEFECT_LABELS,
    IMAGE_SIZE,
    MEAN,
    NUM_CLASSES,
    ONNX_DIR,
    STD,
)
from app import _ensure_model, _get_session, _preprocess, COLORS

# ---------------------------------------------------------------------------
# GPU-decorated predict function — must be at module level for HF scanner
# ---------------------------------------------------------------------------
@spaces.GPU
def _predict_ui(file):
    """Minimal upload → run ONNX inference directly."""
    if file is None:
        return None, "Please upload an image.", None

    img = Image.open(file).convert("RGB")
    img_np = np.array(img)

    blob = _preprocess(img_np)
    session = _get_session()
    input_name = session.get_inputs()[0].name
    output = session.run(None, {input_name: blob})[0]

    probs = 1.0 / (1.0 + np.exp(-output[0]))
    confidences = {
        DEFECT_LABELS[i]: float(probs[i].mean()) for i in range(NUM_CLASSES)
    }

    resized = cv2.resize(img_np, (IMAGE_SIZE, IMAGE_SIZE))
    top_idx = int(probs.mean(axis=(1, 2)).argmax())
    mask = probs[top_idx] > 0.5
    overlay = resized.copy()
    color = COLORS[top_idx][::-1]
    overlay[mask] = (overlay[mask] * 0.5 + color * 0.5).astype(np.uint8)

    overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
    import base64, io
    _, buf = cv2.imencode(".png", overlay_bgr)
    overlay_b64 = base64.b64encode(buf).decode()

    ranked = sorted(confidences.items(), key=lambda x: x[1], reverse=True)
    ranked_text = "\n".join(f"{cls}: {conf:.2%}" for cls, conf in ranked)
    overlay_html = f'<img src="data:image/png;base64,{overlay_b64}" style="max-width:100%;border-radius:12px"/>'
    predictions = [{"class": cls, "confidence": round(conf, 4)} for cls, conf in ranked]

    return overlay_html, ranked_text, predictions


# Build the Gradio Blocks UI
with gr.Blocks(title="NEU-DET Steel Defect Detection", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
    # NEU-DET — Steel Surface Defect Detection
    Upload a steel surface image to detect 6 types of defects.
    """
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload Image", file_types=[".jpg", ".jpeg", ".png"])
            predict_btn = gr.Button("Detect Defects", variant="primary")

        with gr.Column(scale=1):
            overlay_output = gr.HTML(label="Segmentation Overlay")
            predictions_output = gr.Dataframe(
                label="Predictions",
                headers=["Class", "Confidence"],
                datatype=["str", "number"],
                row_count=6,
            )

    predict_btn.click(
        fn=_predict_ui,
        inputs=file_input,
        outputs=[overlay_output, gr.Textbox(visible=False), predictions_output],
    )

    gr.Markdown(
        """
    ---
    **Model:** FPN + EfficientNet-B3  |  **Framework:** ONNX Runtime  |  **Classes:** Crazing, Patches, Inclusion, Pitted Surface, Rolled-in Scale, Scratches
    """
    )

if __name__ == "__main__":
    demo.launch()
