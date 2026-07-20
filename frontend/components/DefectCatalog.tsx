"use client";

import { useInView } from "@/lib/hooks";

const DEFECTS = [
  {
    id: "crazing",
    name: "Crazing",
    icon: "🕸️",
    accent: "#ef4444",
    gradient: "from-red-500/10 to-orange-500/5",
    border: "border-red-500/10",
    hoverBorder: "hover:border-red-500/30",
    glowColor: "rgba(239, 68, 68, 0.08)",
    textColor: "text-red-400",
    badge: "bg-red-500/10 text-red-400",
    description:
      "Network of fine, interconnected cracks on the steel surface caused by thermal stress or inadequate cooling during manufacturing.",
    severity: "Moderate",
  },
  {
    id: "patches",
    name: "Patches",
    icon: "🩹",
    accent: "#3b82f6",
    gradient: "from-blue-500/10 to-indigo-500/5",
    border: "border-blue-500/10",
    hoverBorder: "hover:border-blue-500/30",
    glowColor: "rgba(59, 130, 246, 0.08)",
    textColor: "text-blue-400",
    badge: "bg-blue-500/10 text-blue-400",
    description:
      "Irregular surface patches where the oxide layer is partially detached or discolored, indicating uneven rolling or scaling.",
    severity: "Moderate",
  },
  {
    id: "inclusion",
    name: "Inclusion",
    icon: "🪨",
    accent: "#14b8a6",
    gradient: "from-teal-500/10 to-emerald-500/5",
    border: "border-teal-500/10",
    hoverBorder: "hover:border-teal-500/30",
    glowColor: "rgba(20, 184, 166, 0.08)",
    textColor: "text-teal-400",
    badge: "bg-teal-500/10 text-teal-400",
    description:
      "Non-metallic particles trapped within the steel during solidification. These foreign materials create structural weak points.",
    severity: "High",
  },
  {
    id: "pitted_surface",
    name: "Pitted Surface",
    icon: "🕳️",
    accent: "#10b981",
    gradient: "from-emerald-500/10 to-green-500/5",
    border: "border-emerald-500/10",
    hoverBorder: "hover:border-emerald-500/30",
    glowColor: "rgba(16, 185, 129, 0.08)",
    textColor: "text-emerald-400",
    badge: "bg-emerald-500/10 text-emerald-400",
    description:
      "Small, localized depressions or craters on the surface caused by chemical corrosion or electrolytic reactions during processing.",
    severity: "Moderate",
  },
  {
    id: "rolled-in_scale",
    name: "Rolled-in Scale",
    icon: "🔗",
    accent: "#f59e0b",
    gradient: "from-amber-500/10 to-yellow-500/5",
    border: "border-amber-500/10",
    hoverBorder: "hover:border-amber-500/30",
    glowColor: "rgba(245, 158, 11, 0.08)",
    textColor: "text-amber-400",
    badge: "bg-amber-500/10 text-amber-400",
    description:
      "Oxide scale that becomes embedded into the surface during the rolling process, creating dark elongated marks.",
    severity: "High",
  },
  {
    id: "scratches",
    name: "Scratches",
    icon: "✏️",
    accent: "#a855f7",
    gradient: "from-purple-500/10 to-violet-500/5",
    border: "border-purple-500/10",
    hoverBorder: "hover:border-purple-500/30",
    glowColor: "rgba(168, 85, 247, 0.08)",
    textColor: "text-purple-400",
    badge: "bg-purple-500/10 text-purple-400",
    description:
      "Linear surface marks caused by mechanical contact with rolls, guides, or other steel surfaces during handling and processing.",
    severity: "Low",
  },
];

const SEVERITY_STYLES: Record<string, string> = {
  Low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  Moderate: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  High: "bg-red-500/10 text-red-400 border-red-500/20",
};

export default function DefectCatalog() {
  const { ref, visible } = useInView(0.05);

  return (
    <section id="catalog" ref={ref} className="relative py-16 sm:py-24 lg:py-32">
      {/* Subtle background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[900px] rounded-full bg-blue-500/[0.015] blur-[120px]" />
      </div>

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div
          className={`reveal mx-auto max-w-2xl text-center ${visible ? "visible" : ""}`}
        >
          <div className="mb-4 text-xs font-bold tracking-[0.2em] uppercase text-blue-500/80">
            NEU-DET Dataset
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-5xl font-bold tracking-tight text-white">
            Defect Catalog
          </h2>
          <p className="mt-3 sm:mt-5 text-sm sm:text-lg leading-relaxed text-slate-400">
            The NEU-DET benchmark covers six categories of surface defects
            commonly found in hot-rolled steel strips.
          </p>
        </div>

        {/* Cards grid */}
        <div className="mx-auto mt-12 sm:mt-16 grid max-w-5xl gap-4 sm:gap-5 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {DEFECTS.map((defect, i) => (
            <div
              key={defect.id}
              className={`reveal reveal-delay-${(i % 5) + 1} ${visible ? "visible" : ""} group relative overflow-hidden rounded-2xl border transition-all duration-500 ${defect.border
                } ${defect.hoverBorder} bg-gradient-to-br ${defect.gradient
                } hover:-translate-y-1`}
              style={
                {
                  "--glow-color": defect.glowColor,
                  "--glow-border": `${defect.accent}33`,
                } as React.CSSProperties
              }
            >
              {/* Hover glow */}
              <div
                className="pointer-events-none absolute -top-20 -right-20 h-40 w-40 rounded-full opacity-0 blur-3xl transition-opacity duration-500 group-hover:opacity-100"
                style={{ background: defect.accent }}
              />

              <div className="relative p-6">
                {/* Icon + severity */}
                <div className="mb-4 flex items-start justify-between">
                  <span className="text-3xl">{defect.icon}</span>
                  <span
                    className={`rounded-full border px-2.5 py-0.5 text-[10px] font-bold tracking-wider uppercase ${SEVERITY_STYLES[defect.severity]
                      }`}
                  >
                    {defect.severity}
                  </span>
                </div>

                {/* Name */}
                <h3
                  className={`mb-2 text-lg font-bold ${defect.textColor} transition-colors`}
                >
                  {defect.name}
                </h3>

                {/* Description */}
                <p className="text-sm leading-relaxed text-slate-400/80">
                  {defect.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
