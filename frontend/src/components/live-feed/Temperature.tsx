"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": number | string;
  optimalTemp?: number | string;
};

export default function Temperature() {
  const [data, setData] = useState<RawPhyto[]>([]);
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<number[]>([]);
  const [lastValid, setLastValid] = useState<number | null>(null);
  const [stale, setStale] = useState(false);
  const sseRef = useRef<EventSource | null>(null);
  const retryRef = useRef<number>(0);

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
    return () => { alive = false; };
  }, []);

  // SSE live updates with simple reconnect
  useEffect(() => {
    let cancelled = false;
    function connect() {
      if (cancelled) return;
      const sse = new EventSource("/api/phytoplankton/stream");
      sseRef.current = sse;
      sse.onmessage = (ev) => {
        try {
          const next = JSON.parse(ev.data);
          if (Array.isArray(next)) setData(next);
          retryRef.current = 0; // reset backoff
        } catch {}
      };
      sse.onerror = () => {
        sse.close();
        retryRef.current = Math.min(retryRef.current + 1, 6);
        const timeout = 500 * Math.pow(2, retryRef.current); // exponential backoff
        setTimeout(connect, timeout);
      };
    }
    connect();
    return () => {
      cancelled = true;
      if (sseRef.current) sseRef.current.close();
      sseRef.current = null;
    };
  }, []);

  const { temp, totalCount, contributors, fallbackUsed } = useMemo(() => {
    let num = 0;
    let den = 0;
    let contributors = 0;
    let tempOnlySum = 0;
    let tempOnlyCount = 0;
    const toNum = (v: unknown): number => {
      if (typeof v === "number") return isFinite(v) ? v : 0;
      if (typeof v === "string") {
        const n = Number(v.trim());
        if (!isNaN(n)) return n;
        const n2 = Number(v.replace(/[^\d.+-]/g, ""));
        return isNaN(n2) ? 0 : n2;
      }
      return 0;
    };
    for (const row of data) {
      const count = toNum(row?.["no of that pyhtoplankon"]);
      const t = toNum(row?.optimalTemp);
      if (t > 0) {
        tempOnlySum += t;
        tempOnlyCount += 1;
      }
      if (count > 0 && t > 0) {
        num += count * t;
        den += count;
        contributors += 1;
      }
    }
    if (den > 0) return { temp: num / den, totalCount: den, contributors, fallbackUsed: false };
    if (tempOnlyCount > 0) return { temp: tempOnlySum / tempOnlyCount, totalCount: 0, contributors: tempOnlyCount, fallbackUsed: true };
    return { temp: 0, totalCount: 0, contributors: 0, fallbackUsed: false };
  }, [data]);

  // Update history (simple rolling window of last 24 points)
  useEffect(() => {
    if (temp > 0) {
      setHistory((h) => {
        const next = [...h, temp];
        while (next.length > 24) next.shift();
        return next;
      });
    }
  }, [temp]);

  // Retain last valid temperature so component does not blank
  useEffect(() => {
    if (temp > 0) {
      setLastValid(temp);
      setStale(false);
    } else if (temp === 0 && lastValid !== null) {
      // entering stale mode when previously had data
      setStale(true);
    }
  }, [temp, lastValid]);

  const effectiveTemp = temp > 0 ? temp : lastValid ?? 0;
  const tempDisplay = effectiveTemp > 0 ? effectiveTemp.toFixed(1) : "--";
  const status = temp === 0 ? "no data" : temp < 10 ? "cold" : temp > 30 ? "hot" : "moderate";
  const ring = temp === 0
    ? "from-slate-100 to-gray-100 text-slate-500"
    : temp < 10
      ? "from-blue-100 to-sky-100 text-sky-600"
      : temp > 30
        ? "from-red-100 to-orange-100 text-orange-600"
        : "from-amber-100 to-yellow-100 text-amber-600";

  // Sparkline bars derived from normalized history
  const spark = history.length ? history.slice(-12) : [];
  const minH = Math.min(...spark, temp || 0) || 0;
  const maxH = Math.max(...spark, temp || 0) || 1;

  return (
    <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Compact Header */}
      <div className="p-2 border-b border-[var(--border)]">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-[var(--foreground)]">Temperature</h3>
            <p className="text-[10px] text-[var(--muted)]">estimated °C</p>
          </div>
          <div className="text-[10px] text-[var(--muted)]">
            {loading ? "…" : effectiveTemp === 0 ? "--" : stale ? "stale" : fallbackUsed ? "unweighted" : `n=${totalCount}`}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-2 flex items-center justify-between h-[calc(100%-44px)] gap-2">
        {/* Temperature value */}
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 bg-gradient-to-br ${ring} rounded-full flex items-center justify-center`}>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z" />
            </svg>
          </div>
          <div>
            <div className="text-lg font-bold text-[var(--foreground)] leading-none">{tempDisplay}</div>
            <div className="text-[10px] text-[var(--muted)] capitalize flex items-center gap-1">
              {status}
              {stale && <span className="px-1 py-0.5 rounded bg-amber-100 text-amber-700 text-[9px] font-medium">stale</span>}
            </div>
          </div>
        </div>

        {/* Sparkline */}
        <div className="flex-1 max-w-24 h-6 bg-gradient-to-r from-slate-50 to-slate-100 rounded-md flex items-end justify-center gap-[2px] px-1">
          {spark.map((v, i) => {
            const norm = maxH === minH ? 0.5 : (v - minH) / (maxH - minH);
            const h = Math.max(2, Math.round(norm * 20));
            return <div key={i} className="flex-1 bg-amber-400/60 rounded-sm" style={{ height: h }} />;
          })}
        </div>

        {/* Status indicator */}
        <div className="text-center w-10">
          <div className="w-6 h-6 bg-gradient-to-br from-emerald-100 to-green-100 rounded-full flex items-center justify-center mx-auto">
            <div className={`w-2 h-2 rounded-full ${status === 'hot' ? 'bg-orange-500' : status === 'cold' ? 'bg-sky-500' : 'bg-green-500'}`} />
          </div>
          <div className="text-[10px] text-[var(--muted)] mt-1">{contributors}</div>
        </div>
      </div>
    </div>
  );
}