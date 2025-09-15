"use client";

export default function AreaConcentration() {
  return (
    <div className="h-full bg-white rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--foreground)]">
          Area Concentration
        </h3>
        <p className="text-xs text-[var(--muted)] mt-1">
          cells/mL
        </p>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col items-center justify-center h-full">
        <div className="text-center">
          <div className="mb-3">
            <div className="text-3xl font-bold text-[var(--foreground)]">
              <div className="h-8 bg-slate-200 rounded w-16 mx-auto" />
            </div>
            <div className="text-xs text-[var(--muted)] mt-1">
              <div className="h-2 bg-slate-100 rounded w-12 mx-auto" />
            </div>
          </div>
          
          {/* Visual indicator */}
          <div className="w-12 h-12 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mx-auto">
            <div className="w-6 h-6 bg-orange-400 rounded-full opacity-60" />
          </div>
        </div>
      </div>
    </div>
  );
}