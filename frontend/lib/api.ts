const BASE = "/api";

export interface ModelInfo {
  model: string;
  input_size: number;
  num_classes: number;
  classes: string[];
}

export interface Prediction {
  class: string;
  confidence: number;
}

export interface PredictResult {
  predictions: Prediction[];
  overlay: string; // data:image/png;base64,...
}

export interface SampleGroup {
  [defectClass: string]: string[];
}

export async function fetchModelInfo(): Promise<ModelInfo> {
  const res = await fetch(`${BASE}/model-info`);
  if (!res.ok) throw new Error("Failed to fetch model info");
  return res.json();
}

// Client-side sample list fetched from static JSON (no backend needed).
// Falls back to inline data if the file fails to load.
const FALLBACK_SAMPLES: SampleGroup = {
  crazing: ["crazing_151.jpg", "crazing_153.jpg"],
  inclusion: ["inclusion_161.jpg", "inclusion_169.jpg"],
  patches: ["patches_128.jpg", "patches_151.jpg"],
  pitted_surface: ["pitted_surface_110.jpg", "pitted_surface_125.jpg"],
  rolled_in_scale: ["rolled-in_scale_138.jpg", "rolled-in_scale_14.jpg"],
  scratches: ["scratches_195.jpg", "scratches_264.jpg"],
};

export async function fetchSamples(): Promise<SampleGroup> {
  // Fetch from static JSON served by Next.js (no API proxy needed)
  try {
    const res = await fetch("/samples/index.json");
    if (res.ok) {
      const data = await res.json();
      if (data && Object.keys(data).length > 0) return data;
    }
  } catch {
    // Ignore and try API as fallback
  }
  // Fall back to API (requires backend running on port 8000)
  try {
    const res = await fetch(`${BASE}/samples`);
    if (!res.ok) throw new Error("Failed to fetch samples");
    const data = await res.json();
    if (data.samples && Object.keys(data.samples).length > 0) return data.samples;
  } catch {
    // Final fallback to inline data
  }
  return FALLBACK_SAMPLES;
}

export function sampleUrl(name: string): string {
  return `/samples/${encodeURIComponent(name)}`;
}

export async function predictImage(file: File): Promise<PredictResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/predict`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    if (res.status === 500 && err.detail?.includes("ECONNREFUSED")) {
      throw new Error("Backend server is not running. Start it with: python app.py");
    }
    throw new Error(err.detail || "Prediction failed");
  }
  return res.json();
}
