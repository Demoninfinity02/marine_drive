"use client";

export default function SampleVolume() {
  return (
    <div className="h-full bg-white rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--foreground)]">
          Sample Volume
        </h3>
        <p className="text-xs text-[var(--muted)] mt-1">
          mL
        </p>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col items-center justify-center h-full">
        <div className="text-center">
          <div className="mb-3">
            <div className="text-3xl font-bold text-[var(--foreground)]">
              <div className="h-8 bg-slate-200 rounded w-12 mx-auto" />
            </div>
            <div className="text-xs text-[var(--muted)] mt-1">
              <div className="h-2 bg-slate-100 rounded w-16 mx-auto" />
            </div>
          </div>
          
          {/* Visual indicator - flask/beaker icon */}
          <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-cyan-100 rounded-full flex items-center justify-center mx-auto">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-blue-500"
            >
              <path d="M10 2v7.31a2 2 0 0 0 .584 1.414L16 16.31V21a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1v-4.69l5.416-5.585A2 2 0 0 0 14 9.31V2" />
              <path d="M7 2h10" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}