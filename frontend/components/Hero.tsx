"use client";

export default function Hero() {
  return (
    <section className="relative flex min-h-screen items-center overflow-hidden">
      {/* Mesh gradient background */}
      <div className="mesh-bg absolute inset-0" />

      {/* Grid pattern overlay */}
      <div className="grid-pattern pointer-events-none absolute inset-0" />

      {/* Noise texture */}
      <div className="noise pointer-events-none absolute inset-0" />

      {/* Floating orbs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div
          className="absolute -top-32 -left-32 h-[500px] w-[500px] rounded-full opacity-[0.04]"
          style={{
            background: "radial-gradient(circle, #f59e0b, transparent 70%)",
            animation: "float 8s ease-in-out infinite",
          }}
        />
        <div
          className="absolute -right-24 top-1/3 h-[400px] w-[400px] rounded-full opacity-[0.04]"
          style={{
            background: "radial-gradient(circle, #3b82f6, transparent 70%)",
            animation: "float 10s ease-in-out infinite 2s",
          }}
        />
        <div
          className="absolute -bottom-20 left-1/3 h-[350px] w-[350px] rounded-full opacity-[0.03]"
          style={{
            background: "radial-gradient(circle, #a855f7, transparent 70%)",
            animation: "float 12s ease-in-out infinite 4s",
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-6xl px-6 py-32 lg:px-8">
        <div className="max-w-4xl">
          {/* Badge */}
          <div className="animate-fade-in-up opacity-0 stagger-1">
            <div className="mb-8 inline-flex items-center gap-2.5 rounded-full border border-amber-500/20 bg-amber-500/5 px-4 py-2 text-sm font-medium text-amber-400/90">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-amber-500" />
              </span>
              Deep Learning &bull; ONNX Runtime &bull; Real-time Inference
            </div>
          </div>

          {/* Heading */}
          <div className="animate-fade-in-up opacity-0 stagger-2">
            <h1 className="text-5xl font-bold tracking-tight sm:text-7xl lg:text-8xl">
              <span className="text-white">Steel Surface</span>
              <br />
              <span className="text-gradient">Defect Detection</span>
            </h1>
          </div>

          {/* Subheading */}
          <div className="animate-fade-in-up opacity-0 stagger-3">
            <p className="mt-8 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
              Machine learning–based detection of 6 common steel surface defects using a{" "}
              <span className="font-medium text-slate-200">
                Feature Pyramid Network
              </span>{" "}
              with{" "}
              <span className="font-medium text-slate-200">
                EfficientNet-B3
              </span>{" "}
              backbone — trained on the NEU-DET benchmark dataset.
            </p>
          </div>

          {/* CTAs */}
          <div className="animate-fade-in-up opacity-0 stagger-4 mt-12 flex flex-wrap items-center gap-5">
            <a
              href="#demo"
              className="glow-amber group relative overflow-hidden rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-8 py-4 text-sm font-bold text-black shadow-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-amber-500/25"
            >
              <span className="relative z-10 flex items-center gap-2">
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
                  />
                </svg>
                Try the Demo
              </span>
              <span className="absolute inset-0 bg-gradient-to-r from-amber-400 to-orange-400 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
            </a>
            <a
              href="#catalog"
              className="group rounded-xl border border-white/10 px-8 py-4 text-sm font-semibold text-slate-300 transition-all duration-300 hover:border-white/20 hover:text-white hover:bg-white/[0.03]"
            >
              View Defect Catalog
              <span className="ml-1.5 inline-block transition-transform duration-300 group-hover:translate-x-0.5">
                &rarr;
              </span>
            </a>
          </div>

          {/* Stats */}
          <div className="animate-fade-in-up opacity-0 stagger-5 mt-20">
            <div className="grid max-w-lg grid-cols-3 gap-8 border-t border-white/[0.06] pt-10">
              {[
                { value: "6", label: "Defect Classes" },
                { value: "256²", label: "Input Resolution" },
                { value: "FPN", label: "Architecture" },
              ].map((stat) => (
                <div key={stat.label}>
                  <div className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                    {stat.value}
                  </div>
                  <div className="mt-1.5 text-xs font-medium tracking-wide text-slate-500 uppercase">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom fade */}
      <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
    </section>
  );
}
