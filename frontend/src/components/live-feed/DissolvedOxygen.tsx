"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": number | string;
  Dissolved_Oxygen?: number | string; // mg/L (can be per-species measurement or associated reading)
};

export default function DissolvedOxygen() {
  const [data, setData] = useState<RawPhyto[]>([]);
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<number[]>([]);
  const sseRef = useRef<EventSource | null>(null);

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

  const { value, contributors, fallback } = useMemo(() => {
    if (!data.length) return { value: 0, contributors: 0, fallback: false };
    const toNum = (v: unknown): number => {
      if (typeof v === 'number') return isFinite(v) ? v : 0;
      if (typeof v === 'string') {
        const n = Number(v.replace(/[^\d.+-]/g, ''));
        return isNaN(n) ? 0 : n;
      }
      return 0;
    };
    let num = 0; let den = 0; let countOnlySum = 0; let countOnlyN = 0; let contributors = 0;
    for (const r of data) {
      const cells = toNum(r["no of that pyhtoplankon"]);
      const o2 = toNum(r.Dissolved_Oxygen);
      if (o2 > 0) { countOnlySum += o2; countOnlyN += 1; }
      if (cells > 0 && o2 > 0) { num += cells * o2; den += cells; contributors += 1; }
    }
    if (den > 0) return { value: num/den, contributors, fallback: false };
    if (countOnlyN > 0) return { value: countOnlySum/countOnlyN, contributors: countOnlyN, fallback: true };
    return { value: 0, contributors: 0, fallback: false };
  }, [data]);

  useEffect(() => {
    if (value > 0) setHistory(h => { const next = [...h, value]; while (next.length > 24) next.shift(); return next; });
  }, [value]);

  const display = value > 0 ? value.toFixed(2) : '--';
  const spark = history.slice(-12);
  const minH = Math.min(...spark, value || 0) || 0;
  const maxH = Math.max(...spark, value || 0) || 1;

  return (
    <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm overflow-hidden">
      <div className="p-3 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--foreground)]">Dissolved O₂</h3>
        <p className="text-[10px] text-[var(--muted)]">mg/L {fallback && '(avg)'}</p>
      </div>
      <div className="p-3 flex flex-col h-full">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-2xl font-bold leading-none text-[var(--foreground)]">{display}</div>
            <div className="text-[10px] text-[var(--muted)] mt-1">{contributors} sources</div>
          </div>
          <div className="w-10 h-10 bg-gradient-to-br from-sky-100 to-blue-100 rounded-full flex items-center justify-center">
            <div className="w-5 h-5 bg-sky-400/70 rounded-full" />
          </div>
        </div>
        <div className="flex-1 flex items-end gap-[2px] bg-gradient-to-r from-slate-50 to-slate-100 rounded-md px-1 overflow-hidden">
          {spark.map((v,i)=>{ const norm=maxH===minH?0.5:(v-minH)/(maxH-minH); const h=Math.max(2, Math.round(norm*24)); return <div key={i} className="flex-1 bg-sky-400/60 rounded-sm" style={{height:h}}/>; })}
          {!spark.length && <div className="text-[10px] text-[var(--muted)] mx-auto">{loading?"Loading…":"No data"}</div>}
        </div>
      </div>
    </div>
  );
}
