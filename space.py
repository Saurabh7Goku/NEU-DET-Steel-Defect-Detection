#!/usr/bin/env python
"""Entry point for Hugging Face Spaces (Gradio SDK).

This wraps the existing FastAPI app with a minimal Gradio UI so the
Space stays warm on the free tier. All `/api/*` routes from `app.py`
continue to work normally — the Vercel frontend talks to them directly.
"""

import gradio as gr
from app import app as fastapi_app

# ---------------------------------------------------------------------------
# A lightweight Gradio interface for uploading / previewing predictions.
# HF Spaces needs a Gradio `demo` object to mount on the free tier.
# ---------------------------------------------------------------------------
def _predict_ui(file):
    """Minimal upload → call the same /api/predict logic."""
    if file is None:
        return None, "Please upload an image.", None

    import io
    from PIL import Image

    img = Image.open(file).convert("RGB")

    # Reuse the FastAPI app's internal logic via TestClient
    from fastapi.testclient import TestClient
    client = TestClient(fastapi_app)

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    resp = client.post("/api/predict", files={"file": ("image.jpg", buf, "image/jpeg")})
    if resp.status_code != 200:
        return None, f"Error: {resp.json().get('detail', 'unknown')}", None

    data = resp.json()
    ranked = "\n".join(
        f"{p['class']}: {p['confidence']:.2%}" for p in data["predictions"]
    )
    overlay_url = data["overlay"]  # data:image/png;base64,...

    # Gradio can display the base64 image directly
    overlay_html = f'<img src="{overlay_url}" style="max-width:100%;border-radius:12px"/>'
    return overlay_html, ranked, data["predictions"]


# Build the Gradio Blocks UI
with gr.Blocks(title="NEU-DET Steel Defect Detection", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
    # 🔩 NEU-DET — Steel Surface Defect Detection
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

# ---------------------------------------------------------------------------
# Mount Gradio on the FastAPI app so /api/* routes stay accessible.
# HF Spaces will call `demo.launch()` automatically.
# ---------------------------------------------------------------------------
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

# For direct `python space.py` debugging
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("space:app", host="0.0.0.0", port=7860, reload=True)