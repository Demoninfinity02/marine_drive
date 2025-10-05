"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type RawPhyto = {
  Sample_Volume?: number | string;
  phytoplanktonscientificName: string;
};

export default function SampleVolume() {
  const [data, setData] = useState<RawPhyto[]>([]);
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<number[]>([]);
  const sseRef = useRef<EventSource | null>(null);

  // Initial fetch
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const res = await fetch("/api/phytoplankton", { cache: "no-store" });
        const json = await res.json();
        if (alive) setData(Array.isArray(json) ? json : []);
      } catch { if (alive) setData([]); }
      finally { if (alive) setLoading(false); }
    })();
    return () => { alive = false; };
  }, []);

  // SSE subscription
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

  const { total, avg, contributors } = useMemo(() => {
    if (!data.length) return { total: 0, avg: 0, contributors: 0 };
    const toNum = (v: unknown): number => {
      if (typeof v === 'number') return isFinite(v) ? v : 0;
      if (typeof v === 'string') {
        const n = Number(v.replace(/[^\d.+-]/g, ''));
        return isNaN(n) ? 0 : n;
      }
      return 0;
    };
    let total = 0; let contributors = 0;
    for (const r of data) {
      const vol = toNum(r.Sample_Volume);
      if (vol > 0) { total += vol; contributors += 1; }
    }
    const avg = contributors ? total / contributors : 0;
    return { total, avg, contributors };
  }, [data]);

  // History tracks avg
  useEffect(() => {
    if (avg > 0) setHistory(h => { const next = [...h, avg]; while (next.length > 20) next.shift(); return next; });
  }, [avg]);

  const displayAvg = avg > 0 ? avg.toFixed(2) : '--';
  const spark = history.slice(-12);
  const minH = Math.min(...spark, avg || 0) || 0;
  const maxH = Math.max(...spark, avg || 0) || 1;

  return (
    <div className="h-full bg-white rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
      <div className="p-3 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--foreground)]">Sample Volume</h3>
        <p className="text-[10px] text-[var(--muted)]">mL (avg)</p>
      </div>
      <div className="p-3 flex flex-col h-full">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-2xl font-bold text-[var(--foreground)] leading-none">{displayAvg}</div>
            <div className="text-[10px] text-[var(--muted)] mt-1">{contributors} samples</div>
          </div>
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-full flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-cyan-600">
              <path d="M10 2v7.31a2 2 0 0 0 .584 1.414L16 16.31V21a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1v-4.69l5.416-5.585A2 2 0 0 0 14 9.31V2" />
              <path d="M7 2h10" />
            </svg>
          </div>
        </div>
        <div className="flex-1 flex items-end gap-[2px] bg-gradient-to-r from-slate-50 to-slate-100 rounded-md px-1 overflow-hidden">
          {spark.map((v,i)=>{ const norm = maxH===minH?0.5:(v-minH)/(maxH-minH); const h = Math.max(2, Math.round(norm*24)); return <div key={i} className="flex-1 bg-cyan-400/60 rounded-sm" style={{height:h}}/>; })}
          {!spark.length && <div className="text-[10px] text-[var(--muted)] mx-auto">{loading?"Loading…":"No data"}</div>}
        </div>
        <div className="mt-2 grid grid-cols-2 gap-2 text-[10px]">
          <div className="bg-slate-50 border border-slate-100 rounded p-2">
            <div className="text-[9px] uppercase tracking-wide text-[var(--muted)]">Total</div>
            <div className="font-medium text-[var(--foreground)]">{total>0?total.toFixed(2):'--'} mL</div>
          </div>
          <div className="bg-slate-50 border border-slate-100 rounded p-2">
            <div className="text-[9px] uppercase tracking-wide text-[var(--muted)]">Latest</div>
            <div className="font-medium text-[var(--foreground)]">{spark.length? spark[spark.length-1].toFixed(2): '--'} mL</div>
          </div>
        </div>
      </div>
    </div>
  );
}