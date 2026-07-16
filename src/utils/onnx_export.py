"""Export a trained PyTorch model to ONNX format."""

import argparse
import os

import torch

from src.data.constants import IMAGE_SIZE, ONNX_DIR
from src.models import build_model


def export_to_onnx(model_name: str, ckpt_path: str, output_path: str = None):
    """Load a checkpoint and export the model to ONNX.

    Args:
        model_name: One of 'fpn_resnet', 'fpn_inceptionv4', 'fpn_xception', 'unet_resnet'.
        ckpt_path: Path to the .pth checkpoint.
        output_path: Where to save the .onnx file. Defaults to onnx/<model_name>.onnx.
    """
    if output_path is None:
        os.makedirs(ONNX_DIR, exist_ok=True)
        output_path = os.path.join(ONNX_DIR, f"{model_name}.onnx")

    # Build and load model
    model = build_model(model_name, pretrained=False)
    checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    state_dict = checkpoint.get("state_dict", checkpoint)
    cleaned = {}
    for k, v in state_dict.items():
        cleaned[k[7:]] = v if k.startswith("module.") else v
        cleaned[k] = v
    model.load_state_dict(cleaned)
    model.eval()

    # Dummy input
    dummy = torch.rand(1, 3, IMAGE_SIZE, IMAGE_SIZE)

    torch.onnx.export(
        model,
        dummy,
        output_path,
        opset_version=11,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    )
    print(f"ONNX model exported to {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export PyTorch model to ONNX")
    parser.add_argument("model_name", help="Model name (fpn_resnet, fpn_inceptionv4, fpn_xception, unet_resnet)")
    parser.add_argument("checkpoint", help="Path to .pth checkpoint")
    parser.add_argument("--output", default=None, help="Output .onnx path")
    args = parser.parse_args()
    export_to_onnx(args.model_name, args.checkpoint, args.output)
