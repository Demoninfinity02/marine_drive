"use client";

export default function WaterPH() {
  return (
    <div className="h-full bg-white rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--foreground)]">
          Water pH
        </h3>
        <p className="text-xs text-[var(--muted)] mt-1">
          acidity level
        </p>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col items-center justify-center h-full">
        <div className="text-center">
          <div className="mb-3">
            <div className="text-3xl font-bold text-[var(--foreground)]">
              <div className="h-8 bg-slate-200 rounded w-10 mx-auto" />
            </div>
            <div className="text-xs text-[var(--muted)] mt-1">
              <div className="h-2 bg-slate-100 rounded w-12 mx-auto" />
            </div>
          </div>
          
          {/* Visual indicator - pH meter/droplet */}
          <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-purple-500"
            >
              <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}