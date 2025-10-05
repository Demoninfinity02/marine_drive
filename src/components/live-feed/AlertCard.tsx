"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Image from "next/image";
import { bestMatchIcon } from "@/lib/iconMatch";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": number | string;
  alertLevel?: string;
};

const LEVEL_ORDER = ["High", "Mid", "Low"]; // priority

function levelRank(level?: string) {
  const idx = LEVEL_ORDER.indexOf(String(level || '').trim());
  return idx === -1 ? Infinity : idx;
}

export default function AlertCard() {
  const [data, setData] = useState<RawPhyto[]>([]);
  const [icons, setIcons] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const sseRef = useRef<EventSource | null>(null);

  // Initial load
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [resData, resIcons] = await Promise.all([
          fetch('/api/phytoplankton', { cache: 'no-store' }),
          fetch('/api/icons/phytoplankton', { cache: 'no-store' })
        ]);
        const json = await resData.json();
        const iconJson = await resIcons.json();
        if (!alive) return;
        setData(Array.isArray(json) ? json : []);
        setIcons(Array.isArray(iconJson?.files) ? iconJson.files : []);
      } catch { if (alive) { setData([]); setIcons([]); } }
      finally { if (alive) setLoading(false); }
    })();
    return () => { alive = false; };
  }, []);

  // Live updates via SSE
  useEffect(() => {
    const sse = new EventSource('/api/phytoplankton/stream');
    sseRef.current = sse;
    sse.onmessage = (ev) => {
      console.log('AlertCard SSE message:', ev.data);
      try {
        const next = JSON.parse(ev.data);
        if (Array.isArray(next)) {
          console.log('AlertCard updating data:', next.length, 'items');
          setData(next);
        }
      } catch (e) {
        console.log('AlertCard parse error:', e);
      }
    };
    sse.onerror = () => {
      console.log('AlertCard SSE error');
      sse.close();
    };
    return () => {
      sse.close();
      sseRef.current = null;
    };
  }, []);

  const mostDangerous = useMemo(() => {
    if (!data.length) return null;
    // Aggregate counts per species with its worst alert level
    const map = new Map<string, { count: number; alert?: string }>();
    for (const row of data) {
      const name = String(row.phytoplanktonscientificName || '').trim();
      if (!name) continue;
      const rawCount = Number(row["no of that pyhtoplankon"]);
      const count = isNaN(rawCount) ? 0 : rawCount;
      const level = row.alertLevel ? String(row.alertLevel).trim() : undefined;
      const prev = map.get(name) || { count: 0, alert: level };
      const worst = levelRank(level) < levelRank(prev.alert) ? level : prev.alert;
      map.set(name, { count: prev.count + count, alert: worst });
    }
    // Pick species with highest alert (lowest rank); tie-breaker by count desc
    let pick: { name: string; count: number; alert?: string } | null = null;
    for (const [name, { count, alert }] of map.entries()) {
      if (!pick) { pick = { name, count, alert }; continue; }
      const currentRank = levelRank(alert);
      const pickRank = levelRank(pick.alert);
      if (currentRank < pickRank || (currentRank === pickRank && count > pick.count)) {
        pick = { name, count, alert };
      }
    }
    return pick;
  }, [data]);

  const icon = mostDangerous ? bestMatchIcon(mostDangerous.name, icons) : null;
  const level = mostDangerous?.alert;
  const levelColors: Record<string, { badge: string; ring: string }> = {
    High: { badge: 'bg-red-100 text-red-700', ring: 'from-red-100 to-rose-100' },
    Mid: { badge: 'bg-amber-100 text-amber-700', ring: 'from-amber-100 to-yellow-100' },
    Low: { badge: 'bg-emerald-100 text-emerald-700', ring: 'from-emerald-100 to-green-100' },
  };
  const color = level ? levelColors[level] : { badge: 'bg-slate-100 text-slate-600', ring: 'from-slate-100 to-gray-100' };

  return (
    <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm overflow-hidden">
      <div className="p-3 border-b border-[var(--border)] flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-[var(--foreground)]">Alert</h3>
          <p className="text-[10px] text-[var(--muted)]">most critical species</p>
        </div>
        {level && <span className={`px-2 py-1 rounded-full text-[10px] font-medium ${color.badge}`}>{level}</span>}
      </div>
      <div className="p-3 flex flex-col items-center justify-center h-[calc(100%-56px)] text-center">
        {loading ? (
          <div className="text-[11px] text-[var(--muted)]">Loading…</div>
        ) : !mostDangerous ? (
          <div className="text-[11px] text-[var(--muted)]">No alerts</div>
        ) : (
          <>
            <div className={`w-16 h-16 bg-gradient-to-br ${color.ring} rounded-xl border border-[var(--border)] grid place-items-center mb-3`}> 
              {icon ? (
                <Image src={`/pytoplanktonSvg/${icon}`} alt={mostDangerous.name} width={40} height={40} className="opacity-90" />
              ) : (
                <div className="w-6 h-6 bg-slate-400/60 rounded-full" />
              )}
            </div>
            <div className="text-sm font-semibold text-[var(--foreground)] truncate max-w-[140px] mx-auto">{mostDangerous.name}</div>
            <div className="text-[11px] text-[var(--muted)] mt-1">{mostDangerous.count.toLocaleString()} cells</div>
          </>
        )}
      </div>
    </div>
  );
}
