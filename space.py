#!/usr/bin/env python
"""Entry point for Hugging Face Spaces.

Mounts the Gradio UI onto the FastAPI app so both the Gradio demo
and the /api/* routes (used by the Vercel frontend) are accessible.
"""
# 1. This import MUST sit rawly at the absolute top for the ZeroGPU parser to find it
import spaces
import os
os.environ["GRADIO_SSR_MODE"] = "False"

import gradio as gr
import numpy as np
from PIL import Image

from app import app as fastapi_app, run_prediction, _ensure_model, _get_session

_ensure_model()
_get_session()

# 2. Directly decorate the execution entry point 
@spaces.GPU
def predict_ui(image):
    if image is None:
        return "<p>Please upload an image.</p>", []

    result = run_prediction(np.array(image))

    overlay_html = (
        f'<img src="{result["overlay"]}" '
        f'style="max-width:100%;border-radius:12px"/>'
    )
    return overlay_html, result["predictions"]


with gr.Blocks(title="NEU-DET Steel Defect Detection", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
    # NEU-DET — Steel Surface Defect Detection
    Upload a steel surface image to detect 6 types of defects.
    """
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.Image(type="pil", label="Upload Image")
            predict_btn = gr.Button("Detect Defects", variant="primary")

        with gr.Column(scale=1):
            overlay_output = gr.HTML(label="Segmentation Overlay")
            predictions_output = gr.JSON(label="Predictions")

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

app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("space:app", host="0.0.0.0", port=7860)