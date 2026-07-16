# NEU-DET Steel Defect Detection — Frontend

A Next.js web application for the NEU-DET steel surface defect detection system. Upload images of hot-rolled steel strips and get real-time defect segmentation overlays.

## Features

- **Live Demo** — Upload an image and instantly see defect predictions with colour-coded overlay masks
- **Defect Catalog** — Browse sample images for each of the 6 defect classes
- **Model Info** — View the active model's architecture and class labels

## Tech Stack

- **Framework:** Next.js 16 (App Router, Turbopack)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **Runtime:** Node.js

## Getting Started

From the project root, first start the backend API server:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Then start the frontend dev server:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## API Proxy

The Next.js config rewrites `/api/*` requests to the FastAPI backend at `http://localhost:8000/api/*`, so all API calls from the browser go through the Next.js dev server and avoid CORS issues.

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata & fonts
│   ├── page.tsx            # Main page (composes Hero, Demo, DefectCatalog)
│   └── globals.css         # Global styles & Tailwind imports
├── components/
│   ├── Hero.tsx            # Landing section with app description
│   ├── Demo.tsx            # Interactive upload & prediction UI
│   └── DefectCatalog.tsx   # Sample image browser by defect class
├── lib/
│   ├── api.ts              # Fetch wrappers for the backend API
│   └── hooks.ts            # Custom React hooks (useSamples, usePredict)
└── package.json