---
title: NEU-DET Steel Surface Defect Detection
emoji: 🔩
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 5.35.0
app_file: space.py
pinned: false
license: mit
---

# NEU-DET Steel Surface Defect Detection

Machine learning–based semantic segmentation of surface defects on hot-rolled steel strips using PyTorch, with a FastAPI backend and Next.js frontend.

## Defect Types

| Defect | Code |
|--------|------|
| Crazing | Cr |
| Patches | Pa |
| Inclusion | In |
| Pitted Surface | PS |
| Rolled-in Scale | RS |
| Scratches | Sc |

Dataset: [NEU Surface Defect Database](http://faculty.neu.edu.cn/yunhyan/NEU_surface_defect_database.html) — 1,800 grayscale images (300 per defect class), 200×200 px.

## Project Structure

```
├── app.py                          # FastAPI backend server
├── space.py                        # Gradio wrapper for Hugging Face Spaces
├── main.py                         # CLI entry point (train / evaluate / export)
├── requirements.txt                # Python dependencies (training + inference)
├── Dockerfile                      # (optional — not used on HF free tier)
│
├── frontend/                       # Next.js web application
│   ├── app/                        # App router pages & layout
│   ├── components/                 # React components (Hero, Demo, DefectCatalog)
│   ├── lib/                        # API client & React hooks
│   └── package.json
│
├── src/
│   ├── models/
│   │   ├── fpn_resnet.py           # FPN + ResNet-34
│   │   ├── fpn_inceptionv4.py      # FPN + InceptionV4
│   │   ├── fpn_xception.py         # FPN + Xception
│   │   └── unet_resnet.py          # UNet + ResNet-34
│   ├── data/
│   │   ├── constants.py            # Paths, hyperparams, labels
│   │   ├── dataset.py              # Training / inference / validation datasets
│   │   └── masks.py                # XML annotation parsing & mask creation
│   ├── training/
│   │   ├── trainer.py              # Train/val loop, checkpointing
│   │   └── metrics.py              # Dice & IoU metrics
│   ├── evaluation/
│   │   └── evaluator.py            # Validate against held-out set
│   └── utils/
│       ├── visualization.py        # Training curves & prediction plots
│       └── onnx_export.py          # PyTorch → ONNX conversion
│
├── data/
│   ├── IMAGES/                     # Training images
│   ├── ANNOTATIONS/                # Pascal VOC XML annotations
│   ├── validation_images/          # Held-out validation images
│   └── validation_annotations/     # Held-out validation annotations
│
├── checkpoints/                    # Saved .pth model weights (LFS)
├── onnx/                           # Exported ONNX models (LFS)
└── notebooks/                      # Reference Jupyter notebooks
```

## Quick Start

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Train a model (optional — a pre-trained ONNX model is included)

```bash
# FPN + ResNet-34 (default 20 epochs, lr=5e-4)
python main.py train --model fpn_resnet

# UNet + ResNet-34 for 30 epochs
python main.py train --model unet_resnet --epochs 30 --lr 1e-4

# Save training curves
python main.py train --model fpn_inceptionv4 --plot
```

### 3. Run the backend API server locally

```bash
# The ONNX model at onnx/steel_defect_fpn_efficientnet-b3.onnx is loaded automatically
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/model-info` | GET | Model metadata (architecture, input size, classes) |
| `/api/samples` | GET | List validation images grouped by defect class |
| `/api/sample/{name}` | GET | Serve a validation image |
| `/api/predict` | POST | Upload an image, get per-class confidences + overlay mask |
| `/docs` | GET | Interactive Swagger documentation |

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The web app will be available at `http://localhost:3000`. The Next.js dev server proxies `/api/*` requests to the FastAPI backend automatically.

## Deployment

### Hugging Face Spaces (Backend API)

1. Create a new Space at https://huggingface.co/new-space
2. Choose **Gradio** SDK (free tier)
3. Connect your GitHub repo
4. Set environment variable: `ALLOWED_ORIGINS=https://your-app.vercel.app`
5. The Space auto-deploys from `space.py`

### Vercel (Frontend)

1. Import your GitHub repo at https://vercel.com/new
2. Set root directory to `frontend/`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-space.hf.space`
4. Deploy

### Keep the Space Warm

A GitHub Actions workflow (`.github/workflows/wake-up-hf.yml`) pings the Space daily at 7:00 AM IST to prevent cold starts.

## Evaluate

```bash
python main.py evaluate --model fpn_resnet --checkpoint checkpoints/model_fpn_resnet.pth
```

## Export to ONNX

```bash
python main.py export --model fpn_resnet --checkpoint checkpoints/model_fpn_resnet.pth
```

## Available Models

| Config | Architecture | Encoder | Params |
|--------|-------------|---------|--------|
| `fpn_resnet` | FPN | ResNet-34 | ~26M |
| `fpn_inceptionv4` | FPN | InceptionV4 | ~46M |
| `fpn_xception` | FPN | Xception | ~42M |
| `unet_resnet` | UNet | ResNet-34 | ~24M |

All encoders are pretrained on ImageNet. The segmentation head outputs 6 channels (one per defect type) as raw logits.

## Training Details

- **Loss:** BCEWithLogitsLoss
- **Optimizer:** Adam (lr=5e-4)
- **Scheduler:** ReduceLROnPlateau (patience=3, mode=max on dice)
- **Image size:** 128×128
- **Normalization:** ImageNet stats (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- **Batch size:** 4 with gradient accumulation (effective batch size = 16)
- **Augmentation:** Horizontal flip (training only)