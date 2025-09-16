"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": number | string;
  Area_Concentration?: number | string;
};

export default function AreaConcentration() {
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
      } finally { if (alive) setLoading(false); }
    })();
    return () => { alive = false; };
  }, []);

  // Live SSE subscription
  useEffect(() => {
    const sse = new EventSource("/api/phytoplankton/stream");
    sseRef.current = sse;
    sse.onmessage = (ev) => {
      try {
        const next = JSON.parse(ev.data);
        if (Array.isArray(next)) setData(next);
      } catch {}
    };
    sse.onerror = () => { sse.close(); };
    return () => { sse.close(); sseRef.current = null; };
  }, []);

  const { avg, total, top } = useMemo(() => {
    if (!data.length) return { avg: 0, total: 0, top: [] as { name: string; conc: number }[] };
    const toNum = (v: unknown): number => {
      if (typeof v === "number") return isFinite(v) ? v : 0;
      if (typeof v === "string") {
        const n = Number(v.replace(/[^\d.+-]/g, ""));
        return isNaN(n) ? 0 : n;
      }
      return 0;
    };
    let sum = 0;
    const perSpecies = new Map<string, number>();
    for (const r of data) {
      const name = String(r.phytoplanktonscientificName || "").trim();
      const conc = toNum(r.Area_Concentration);
      if (!name || conc <= 0) continue;
      sum += conc;
      perSpecies.set(name, (perSpecies.get(name) || 0) + conc);
    }
    const species = Array.from(perSpecies.entries()).map(([name, conc]) => ({ name, conc }));
    species.sort((a, b) => b.conc - a.conc);
    const total = sum;
    const avg = species.length ? sum / species.length : 0;
    return { avg, total, top: species.slice(0, 4) };
  }, [data]);

  const displayAvg = avg > 0 ? avg.toFixed(1) : "--";

  return (
    <div className="h-full bg-white rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--foreground)]">Area Concentration</h3>
        <p className="text-[10px] text-[var(--muted)]">cells / mL</p>
      </div>
      <div className="p-3 flex flex-col h-full">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-2xl font-bold text-[var(--foreground)] leading-none">{displayAvg}</div>
            <div className="text-[10px] text-[var(--muted)] mt-1">mean of {top.length ? top.length : 0} species</div>
          </div>
          <div className="w-10 h-10 bg-gradient-to-br from-amber-100 to-orange-100 rounded-full flex items-center justify-center">
            <div className="w-5 h-5 bg-orange-400/70 rounded-full" />
          </div>
        </div>
        <div className="text-[10px] text-[var(--muted)] mb-1">Top contributors</div>
        {loading ? (
          <div className="text-[10px] text-[var(--muted)]">Loading…</div>
        ) : !top.length ? (
          <div className="text-[10px] text-[var(--muted)]">No data</div>
        ) : (
          <div className="space-y-1 flex-1 overflow-y-auto">
            {top.map((t) => {
              const pct = total > 0 ? Math.round((t.conc / total) * 100) : 0;
              return (
                <div key={t.name} className="bg-slate-50 border border-slate-100 rounded-md p-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium truncate max-w-[90px]">{t.name}</span>
                    <span className="text-[10px] text-[var(--muted)]">{t.conc.toFixed(1)}</span>
                  </div>
                  <div className="mt-1 h-1.5 bg-slate-200 rounded overflow-hidden">
                    <div className="h-1.5 bg-orange-400" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}