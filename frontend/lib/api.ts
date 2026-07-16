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

export async function fetchSamples(): Promise<SampleGroup> {
  const res = await fetch(`${BASE}/samples`);
  if (!res.ok) throw new Error("Failed to fetch samples");
  const data = await res.json();
  return data.samples;
}

export function sampleUrl(name: string): string {
  return `${BASE}/sample/${encodeURIComponent(name)}`;
}

export async function predictImage(file: File): Promise<PredictResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/predict`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Prediction failed");
  }
  return res.json();
}
