"use client";

import { useCallback, useRef, useState, useEffect } from "react";
import { fetchSamples, sampleUrl, predictImage } from "@/lib/api";
import type { Prediction } from "@/lib/api";

const CLASS_COLORS: Record<string, string> = {
  crazing:       "#ef4444",
  patches:       "#3b82f6",
  inclusion:     "#10b981",
  pitted_surface:"#f59e0b",
  rolled_in_scale:"#8b5cf6",
  scratches:     "#ec4899",
};

export default function Demo() {
  const [samples, setSamples] = useState<Record<string, string[]>>({});
  const [selected, setSelected] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<{
    overlay: string;
    predictions: Prediction[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [visible, setVisible] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 150);
    fetchSamples()
      .then((s) => {
        setSamples(s);
      })
      .catch(() => {});
    return () => clearTimeout(t);
  }, []);

  const runPrediction = useCallback(
    async (file: File) => {
      setLoading(true);
      setError(null);
      setResult(null);
      try {
        const res = await predictImage(file);
        setResult(res);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Prediction failed");
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (!file?.type.startsWith("image/")) return;
      setSelected(null);
      setPreviewUrl(URL.createObjectURL(file));
      runPrediction(file);
    },
    [runPrediction],
  );

  const handleFile = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setSelected(null);
      setPreviewUrl(URL.createObjectURL(file));
      runPrediction(file);
    },
    [runPrediction],
  );

  const handleSampleClick = useCallback(
    async (name: string) => {
      setSelected(name);
      setPreviewUrl(null);
      setResult(null);
      setError(null);
      setLoading(true);
      try {
        const res = await fetch(sampleUrl(name));
        const blob = await res.blob();
        const file = new File([blob], name, { type: "image/jpeg" });
        const predictRes = await predictImage(file);
        setResult(predictRes);
      } catch {
        setError("Failed to predict sample");
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const topPred = result?.predictions?.[0];
  const allClasses = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled_in_scale",
    "scratches",
  ] as const;

  return (
    <section
      id="demo"
      className={`relative mx-auto max-w-6xl px-4 py-24 transition-all duration-1000 ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      }`}
    >
      {/* ── Section Header ── */}
      <div className="mb-10 text-center">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.3em] text-amber-500/80">
          Live Prediction
        </p>
        <h2 className="text-3xl font-bold text-white sm:text-4xl">
          Try It <span className="text-amber-400">Out</span>
        </h2>
        <p className="mt-3 text-sm text-slate-400">
          Upload a steel surface image or pick a sample to classify
        </p>
      </div>

      {/* ── Two-Panel Layout ── */}
      <div className="grid gap-5 lg:grid-cols-2">
        {/* ── Left: Upload + Samples ── */}
        <div className="flex flex-col gap-5">
          {/* Drop Zone */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            className={`relative flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-8 transition-all duration-300 ${
              dragOver
                ? "border-amber-400 bg-amber-500/10 shadow-[0_0_30px_rgba(245,158,11,0.15)]"
                : "border-white/[0.08] bg-white/[0.02] hover:border-white/[0.15] hover:bg-white/[0.04]"
            }`}
          >
            <div
              className={`flex h-12 w-12 items-center justify-center rounded-xl transition-colors ${
                dragOver ? "bg-amber-500/20 text-amber-400" : "bg-white/[0.05] text-slate-500"
              }`}
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 16V4m0 0L8 8m4-4l4 4" />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-slate-300">
                {dragOver ? "Drop image here" : "Drag & drop an image"}
              </p>
              <p className="mt-1 text-xs text-slate-500">or click to browse • JPG, PNG, BMP</p>
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFile}
            />
          </div>

          {/* Sample Grid */}
          {Object.keys(samples).length > 0 && (
            <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Sample Images
              </p>
              <div className="grid grid-cols-6 gap-2">
                {allClasses.map((cls) =>
                  (samples[cls] || []).slice(0, 2).map((img, i) => {
                    const isSelected = selected === img;
                    return (
                      <button
                        key={`${cls}-${i}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSampleClick(img);
                        }}
                        className={`group relative aspect-square overflow-hidden rounded-lg border transition-all duration-200 ${
                          isSelected
                            ? "border-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.3)]"
                            : "border-white/[0.06] hover:border-white/[0.2]"
                        }`}
                        title={cls.replace(/_/g, " ")}
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={sampleUrl(img)}
                          alt={cls}
                          className="h-full w-full object-cover transition-transform duration-200 group-hover:scale-110"
                          loading="lazy"
                        />
                        {/* Class color dot */}
                        <span
                          className="absolute bottom-1 right-1 h-2 w-2 rounded-full ring-1 ring-black/40"
                          style={{ backgroundColor: CLASS_COLORS[cls] }}
                        />
                        {/* Hover label */}
                        <span className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent px-1 py-0.5 text-[9px] font-medium text-white opacity-0 transition-opacity group-hover:opacity-100">
                          {cls.replace(/_/g, " ")}
                        </span>
                      </button>
                    );
                  }),
                )}
              </div>
            </div>
          )}
        </div>

        {/* ── Right: Results ── */}
        <div className="flex flex-col gap-5">
          {/* Overlay / Empty State */}
          <div className="relative flex min-h-[280px] items-center justify-center overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.02]">
            {loading ? (
              <div className="flex flex-col items-center gap-3">
                <div className="h-10 w-10 rounded-full border-2 border-amber-500/20 border-t-amber-400 animate-spin" />
                <p className="text-sm text-slate-400">Analyzing surface…</p>
              </div>
            ) : result?.overlay ? (
              <>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={result.overlay}
                  alt="Prediction overlay"
                  className="max-h-80 w-full rounded-xl object-contain p-4"
                />
                {topPred && (
                  <span className="absolute top-3 right-3 flex items-center gap-1.5 rounded-full bg-black/60 px-3 py-1 text-xs font-semibold text-white backdrop-blur-sm">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{
                        backgroundColor: CLASS_COLORS[topPred.class],
                        boxShadow: `0 0 8px ${CLASS_COLORS[topPred.class]}`,
                      }}
                    />
                    {topPred.class.replace(/_/g, " ")}
                  </span>
                )}
              </>
            ) : previewUrl ? (
              <>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-h-80 w-full rounded-xl object-contain p-4 opacity-60"
                />
              </>
            ) : (
              <div className="flex flex-col items-center gap-2 text-center px-6">
                <svg className="h-10 w-10 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="text-sm text-slate-600">Upload or select an image to see results</p>
              </div>
            )}
          </div>

          {/* Confidence Bars */}
          {result?.predictions && (
            <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5">
              <div className="mb-4 flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Class Confidence
                </p>
                <span className="rounded-full bg-amber-500/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-amber-400">
                  {(topPred!.confidence * 100).toFixed(1)}% match
                </span>
              </div>
              <div className="space-y-3">
                {result.predictions.map((pred, i) => {
                  const pct = pred.confidence * 100;
                  const color = CLASS_COLORS[pred.class] ?? "#64748b";
                  return (
                    <div key={pred.class}>
                      <div className="mb-1 flex items-center justify-between">
                        <span className="flex items-center gap-2 text-sm text-slate-300">
                          <span
                            className="h-2 w-2 rounded-full"
                            style={{ backgroundColor: color }}
                          />
                          {pred.class.replace(/_/g, " ")}
                          {i === 0 && (
                            <span className="rounded bg-amber-500/15 px-1.5 py-0.5 text-[9px] font-bold uppercase text-amber-400">
                              top
                            </span>
                          )}
                        </span>
                        <span className="text-xs font-mono text-slate-500">
                          {pct.toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06]">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{
                            width: `${pct}%`,
                            backgroundColor: color,
                            boxShadow: `0 0 10px ${color}40`,
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-5 py-3 text-sm text-red-400">
              {error}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
