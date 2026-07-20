import Hero from "@/components/Hero";
import Demo from "@/components/Demo";
import DefectCatalog from "@/components/DefectCatalog";

export default function Home() {
  return (
    <>
      <Hero />
      <Demo />
      <DefectCatalog />

      {/* Footer */}
      <footer className="border-t border-white/[0.04] py-8 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:gap-6 sm:flex-row">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-500">
                <svg
                  className="h-4 w-4 text-black"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"
                  />
                </svg>
              </div>
              <span className="text-sm font-semibold text-slate-300">
                NEU-DET
              </span>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-6 text-[10px] sm:text-xs text-slate-600">
              <span>FPN + EfficientNet-B3</span>
              <span className="hidden sm:inline h-3 w-px bg-white/[0.06]" />
              <span>ONNX Runtime</span>
              <span className="hidden sm:inline h-3 w-px bg-white/[0.06]" />
              <span>Next.js + FastAPI</span>
            </div>

            <p className="text-[10px] sm:text-xs text-slate-600">
              &copy; {new Date().getFullYear()} Steel Defect Detection
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
