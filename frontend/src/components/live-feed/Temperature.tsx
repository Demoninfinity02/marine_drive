"use client";

export default function Temperature() {
  return (
    <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Compact Header */}
      <div className="p-2 border-b border-[var(--border)]">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-[var(--foreground)]">
              Temperature
            </h3>
            <p className="text-xs text-[var(--muted)]">°C</p>
          </div>
          <div className="text-xs text-emerald-600 font-medium">+0.3°</div>
        </div>
      </div>

      {/* Content */}
      <div className="p-2 flex items-center justify-between h-[calc(100%-48px)]">
        {/* Temperature value */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-red-100 to-orange-100 rounded-full flex items-center justify-center">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-red-500"
            >
              <path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z" />
            </svg>
          </div>
          <div>
            <div className="text-xl font-bold text-[var(--foreground)]">23.7</div>
            <div className="text-xs text-[var(--muted)]">Optimal range</div>
          </div>
        </div>

        {/* Enhanced trend chart */}
        <div className="flex-1 max-w-24 h-6 bg-gradient-to-r from-red-50 to-orange-50 rounded-md flex items-end justify-center gap-px px-1">
          {[4, 6, 5, 7, 9, 8, 10, 9, 11, 10, 12, 11].map((height, index) => (
            <div
              key={index}
              className="bg-red-300 rounded-sm opacity-60 transition-all duration-300"
              style={{
                width: '2px',
                height: `${height * 2}px`,
              }}
            />
          ))}
        </div>

        {/* Status indicator */}
        <div className="text-center">
          <div className="w-6 h-6 bg-gradient-to-br from-green-100 to-emerald-100 rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
          </div>
          <div className="text-xs text-[var(--muted)] mt-1">Good</div>
        </div>
      </div>
    </div>
  );
}