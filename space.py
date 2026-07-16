#!/usr/bin/env python
"""Entry point for Hugging Face Spaces (Gradio SDK).

Gradio UI that calls the same shared inference function as the FastAPI backend.
HF Spaces manages the server lifecycle — no demo.launch() or uvicorn needed.
"""

import os
os.environ["GRADIO_SSR_MODE"] = "False"

import gradio as gr
import spaces
import numpy as np
from PIL import Image

from app import run_prediction, _ensure_model, _get_session

# Ensure ONNX model is loaded at import time
_ensure_model()
_get_session()


@spaces.GPU
def predict_ui(file):
    """Run inference and return overlay HTML + table rows."""
    if file is None:
        return None, [["—", 0.0]]

    img = Image.open(file).convert("RGB")
    img_np = np.array(img)

    result = run_prediction(img_np)

    overlay_html = (
        f'<img src="{result["overlay"]}" '
        f'style="max-width:100%;border-radius:12px"/>'
    )
    table = [[p["class"], p["confidence"]] for p in result["predictions"]]

    return overlay_html, table


# ---------------------------------------------------------------------------
# Gradio Blocks UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="NEU-DET Steel Defect Detection", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
    # NEU-DET — Steel Surface Defect Detection
    Upload a steel surface image to detect 6 types of defects.
    """
    )

    status = gr.Textbox(visible=False)

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(
                label="Upload Image",
                file_types=[".jpg", ".jpeg", ".png"],
            )
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
        fn=predict_ui,
        inputs=file_input,
        outputs=[overlay_output, predictions_output],
    )

    gr.Markdown(
        """
    ---
    **Model:** FPN + EfficientNet-B3  |  **Framework:** ONNX Runtime  |  **Classes:** Crazing, Patches, Inclusion, Pitted Surface, Rolled-in Scale, Scratches
    """
    )

# HF Spaces mounts the Gradio app via the `demo` object at module level.
# Do NOT call demo.launch() or uvicorn.run() here.
