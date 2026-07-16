#!/usr/bin/env python
"""Upload the ONNX model to Hugging Face Model Hub.

Usage:
    HF_TOKEN=hf_your_token python upload_model.py
"""

import os
import sys
from huggingface_hub import HfApi, create_repo

token = os.environ.get("HF_TOKEN")

if not token:
    raise RuntimeError(
        "HF_TOKEN environment variable is not set.\n"
        "Example:\n"
        "PowerShell: $env:HF_TOKEN='hf_xxx'\n"
        "python upload_model.py"
    )

api = HfApi(token=token)

repo_id = "Saurabhgk2303/steel-defect-detection-model"

create_repo(repo_id, repo_type="model", exist_ok=True)

model_path = "onnx/steel_defect_fpn_efficientnet-b3.onnx"

url = api.upload_file(
    path_or_fileobj=model_path,
    path_in_repo="model.onnx",
    repo_id=repo_id,
    repo_type="model",
)

print(url)