"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": number | string;
  optimalPh?: number | string;
};

export default function WaterPH() {
  const [data, setData] = useState<RawPhyto[]>([]);
  const [loading, setLoading] = useState(true);
  const sseRef = useRef<EventSource | null>(null);

  // Initial fetch
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const res = await fetch("/api/phytoplankton", { cache: "no-store" });
        const json = await res.json();
        if (alive) setData(Array.isArray(json) ? json : []);
      } catch {
        if (alive) setData([]);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  // Live updates via SSE
  useEffect(() => {
    const sse = new EventSource("/api/phytoplankton/stream");
    sseRef.current = sse;
    sse.onmessage = (ev) => {
      try {
        const next = JSON.parse(ev.data);
        if (Array.isArray(next)) setData(next);
      } catch {}
    };
    sse.onerror = () => {
      sse.close();
    };
    return () => {
      sse.close();
      sseRef.current = null;
    };
  }, []);

  const { ph, totalCount, contributors, fallbackUsed } = useMemo(() => {
    let num = 0;
    let den = 0;
    let contributors = 0;
    let phOnlySum = 0;
    let phOnlyCount = 0;
    const toNum = (v: unknown): number => {
      if (typeof v === "number") return isFinite(v) ? v : 0;
      if (typeof v === "string") {
        const n = Number(v.replace(/[^\d.+-]/g, ""));
        return isNaN(n) ? 0 : n;
      }
      return 0;
    };
    for (const row of data) {
      const count = toNum(row?.["no of that pyhtoplankon"]);
      const ph = toNum(row?.optimalPh);
      if (ph > 0) {
        phOnlySum += ph;
        phOnlyCount += 1;
      }
      if (count > 0 && ph > 0) {
        num += count * ph;
        den += count;
        contributors += 1;
      }
    }
    if (den > 0) {
      return { ph: num / den, totalCount: den, contributors, fallbackUsed: false };
    }
    // Fallback: unweighted average if counts are missing but pH present
    if (phOnlyCount > 0) {
      return { ph: phOnlySum / phOnlyCount, totalCount: 0, contributors: phOnlyCount, fallbackUsed: true };
    }
    return { ph: 0, totalCount: 0, contributors: 0, fallbackUsed: false };
  }, [data]);

  // Simple pH descriptor and color
  const phDisplay = ph > 0 ? ph.toFixed(2) : "--";
  const phLabel = ph === 0 ? "insufficient data" : ph < 7 ? "acidic" : ph > 8.5 ? "alkaline" : "neutral";
  const ring = ph === 0
    ? "from-slate-100 to-gray-100 text-slate-500"
    : ph < 7
      ? "from-red-100 to-rose-100 text-rose-600"
      : ph > 8.5
        ? "from-emerald-100 to-green-100 text-emerald-600"
        : "from-yellow-100 to-amber-100 text-amber-600";

  return (
    <div className="h-full bg-white rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--foreground)]">Water pH</h3>
        <p className="text-xs text-[var(--muted)] mt-1">weighted from organism optimal pH</p>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col items-center justify-center h-full">
        <div className="text-center">
          <div className="mb-3">
            <div className="text-3xl font-bold text-[var(--foreground)]">{phDisplay}</div>
            <div className="text-xs text-[var(--muted)] mt-1">{phLabel}</div>
          </div>

          {/* Visual indicator - pH meter/droplet */}
          <div className={`w-12 h-12 bg-gradient-to-br ${ring} rounded-full flex items-center justify-center mx-auto`}>
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
            </svg>
          </div>
          <div className="mt-2 text-[10px] text-[var(--muted)]">
            {loading
              ? "Loading…"
              : ph === 0
                ? "No usable data"
                : fallbackUsed
                  ? `contributors = ${contributors} (unweighted)`
                  : `n = ${totalCount.toLocaleString()} (weighted)`}
          </div>
        </div>
      </div>
    </div>
  );
}