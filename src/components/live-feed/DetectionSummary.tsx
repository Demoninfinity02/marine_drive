"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": number | string;
  Confidence?: number | string;
};

type Row = {
  species: string;
  genus: string;
  count: number;
  confidence: number; // percentage 0-100 (rounded)
};

// Best-effort genus extractor from scientific name
function deriveGenus(name: string): string {
  const cleaned = String(name || "").trim();
  if (!cleaned) return "—";
  // Split on whitespace, hyphen, or underscore and take the first token
  const first = cleaned.split(/[\s_-]+/)[0] || cleaned;
  // Normalize capitalization: Genus should be Capitalized
  const lower = first.toLowerCase();
  return lower.charAt(0).toUpperCase() + lower.slice(1);
}

export default function DetectionSummary() {
  const [data, setData] = useState<RawPhyto[]>([]);
  const [loading, setLoading] = useState(true);
  const sseRef = useRef<EventSource | null>(null);

  // Initial load
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
      } catch {
        // ignore malformed events
      }
    };
    sse.onerror = () => {
      sse.close();
    };
    return () => {
      sse.close();
      sseRef.current = null;
    };
  }, []);

  // Aggregate by species name; compute weighted confidence by counts
  const rows: Row[] = useMemo(() => {
    if (!data?.length) return [];
    const map = new Map<string, { count: number; confWeighted: number }>();

    const toNumber = (v: unknown): number => {
      if (typeof v === "number") return isFinite(v) ? v : 0;
      if (typeof v === "string") {
        const n = Number(v.replace(/[^\d.+-]/g, ""));
        return isNaN(n) ? 0 : n;
      }
      return 0;
    };

    for (const row of data) {
      const species = String(row?.phytoplanktonscientificName || "").trim();
      if (!species) continue;
      const count = toNumber(row?.["no of that pyhtoplankon"]);
      const conf = toNumber(row?.Confidence);
      const prev = map.get(species) || { count: 0, confWeighted: 0 };
      const nextCount = prev.count + count;
      const nextWeighted = prev.confWeighted + conf * count; // weight by count
      map.set(species, { count: nextCount, confWeighted: nextWeighted });
    }

    const out: Row[] = [];
    for (const [species, agg] of map.entries()) {
      const avgConf = agg.count > 0 ? Math.round(agg.confWeighted / agg.count) : 0;
      out.push({
        species,
        genus: deriveGenus(species),
        count: agg.count,
        confidence: Math.max(0, Math.min(100, avgConf)),
      });
    }
    // Sort by count desc
    out.sort((a, b) => b.count - a.count);
    return out;
  }, [data]);

  return (
    <div className="h-full min-h-0 bg-white rounded-xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Compact Header */}
      <div className="p-3 border-b border-[var(--border)]">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-[var(--foreground)]">
              Detection Summary
            </h3>
            <p className="text-xs text-[var(--muted)]">
              Species identification results
            </p>
          </div>
          <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full">
            Active
          </span>
        </div>
      </div>

  {/* Content */}
  <div className="p-3 overflow-y-auto h-[calc(100%-68px)]">
        {/* Table Header */}
        <div className="grid grid-cols-4 gap-3 pb-2 border-b border-[var(--border)] text-xs font-medium text-[var(--muted)] mb-2">
          <div>Species</div>
          <div>Genus</div>
          <div>Count</div>
          <div>Confidence</div>
        </div>

        {/* Table Rows - compact spacing */}
        {loading ? (
          <div className="text-xs text-[var(--muted)] px-2 py-2">Loading…</div>
        ) : !rows.length ? (
          <div className="text-xs text-[var(--muted)] px-2 py-2">No detections yet</div>
        ) : (
          <div className="space-y-1">
            {rows.map((item, index) => (
              <div key={index} className="grid grid-cols-4 gap-3 py-2 px-2 rounded-md hover:bg-slate-50 transition-colors text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-teal-100 to-emerald-100 rounded-sm flex items-center justify-center">
                    <div className="w-2 h-2 bg-teal-500 rounded-full opacity-60" />
                  </div>
                  <span className="font-medium text-[var(--foreground)] truncate">{item.species}</span>
                </div>
                <div className="text-[var(--muted)] truncate">{item.genus}</div>
                <div className="font-medium text-[var(--foreground)]">{item.count.toLocaleString()}</div>
                <div className="flex items-center">
                  <div
                    className={`${
                      item.confidence <= 40
                        ? 'bg-red-100 text-red-700'
                        : item.confidence <= 60
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-emerald-100 text-emerald-700'
                    } px-2 py-1 rounded-md text-xs font-medium`}
                  >
                    {item.confidence}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}