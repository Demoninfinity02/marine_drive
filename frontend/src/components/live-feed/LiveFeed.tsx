/* eslint-disable @next/next/no-img-element */
"use client";

import { useEffect, useState } from "react";

export default function LiveFeed() {
  const [src, setSrc] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const url =
      process.env.NEXT_PUBLIC_MJPEG_URL ||
      "http://10.223.141.65:5001/stream/mjpeg?source=0";
    // Quick HEAD check to avoid broken <img> loop; browsers often block HEAD for mjpeg, so fall back to direct usage
    setSrc(url);
  }, []);

  return (
    <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Compact Header */}
      <div className="p-3 border-b border-[var(--border)]">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-[var(--foreground)]">
              Live Microscopy Feed
            </h3>
            <p className="text-xs text-[var(--muted)]">
              Real-time microscopic view
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-xs text-[var(--muted)]">Live</span>
          </div>
        </div>
      </div>

      {/* Content - fills remaining space */}
      <div className="p-3 h-[calc(100%-60px)]">
        <div className="w-full h-full rounded-lg border border-teal-100 overflow-hidden bg-gradient-to-br from-teal-50 to-emerald-50">
          {src ? (
            // MJPEG plays directly in <img/>
            <img
              src={src}
              alt="Live microscopy feed"
              className="w-full h-full object-contain bg-white"
              onError={() => setError("Stream unavailable")}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center">
                <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="text-teal-600"
                  >
                    <circle cx="12" cy="12" r="3" />
                    <path d="M12 1v6m0 6v6" />
                    <path d="m1 12 6 0m6 0 6 0" />
                  </svg>
                </div>
                <p className="text-[var(--muted)] text-xs">
                  {error || "Microscopy feed will appear here"}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Controls bar */}
      <div className="p-2 bg-white/50 border-t border-[var(--border)]">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-teal-200 rounded-sm" />
            <span className="text-[var(--muted)]">Zoom: 400x</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-1 h-3 bg-teal-300 rounded-full" />
            <div className="w-1 h-2 bg-teal-300 rounded-full" />
            <div className="w-1 h-4 bg-teal-300 rounded-full" />
            <div className="w-1 h-2 bg-teal-300 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}