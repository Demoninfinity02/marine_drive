"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Image from "next/image";
import { bestMatchIcon } from "@/lib/iconMatch";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": number | string;
  Confidence?: number | string;
};

export default function TopSpecies() {
  const [data, setData] = useState<RawPhyto[]>([]);
  const [icons, setIcons] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const sseRef = useRef<EventSource | null>(null);

  // Initial fetch
  useEffect(() => {
    let alive = true;
    async function load() {
      try {
        const [resData, resIcons] = await Promise.all([
          fetch("/api/phytoplankton", { cache: "no-store" }),
          fetch("/api/icons/phytoplankton", { cache: "no-store" }),
        ]);
        const json = await resData.json();
        const iconJson = await resIcons.json();
        if (!alive) return;
        setData(Array.isArray(json) ? json : []);
        setIcons(Array.isArray(iconJson?.files) ? iconJson.files : []);
      } catch {
        if (alive) {
          setData([]);
          setIcons([]);
        }
      } finally {
        if (alive) setLoading(false);
      }
    }
    load();
    return () => {
      alive = false;
    };
  }, []);

  // Live updates via SSE
  useEffect(() => {
    const sse = new EventSource("/api/phytoplankton/stream");
    sseRef.current = sse;
    sse.onmessage = (ev) => {
      console.log('TopSpecies SSE message:', ev.data);
      try {
        const next = JSON.parse(ev.data);
        if (Array.isArray(next)) {
          console.log('TopSpecies updating data:', next.length, 'items');
          setData(next);
        }
      } catch (e) {
        console.log('TopSpecies parse error:', e);
      }
    };
    sse.onerror = () => {
      // On error, close and let initial snapshot remain
      sse.close();
    };
    return () => {
      sse.close();
      sseRef.current = null;
    };
  }, []);

  const top = useMemo(() => {
    if (!data.length) return [] as { name: string; count: number; icon?: string }[];
    // Aggregate counts by name (in case duplicates arrive)
    const map = new Map<string, number>();
    for (const row of data) {
      const name = String(row.phytoplanktonscientificName || "").trim();
      if (!name) continue;
      const c = Number(row["no of that pyhtoplankon"]);
      const count = isNaN(c) ? 0 : c;
      map.set(name, (map.get(name) || 0) + count);
    }
    const entries = Array.from(map.entries()).map(([name, count]) => ({ name, count }));
    entries.sort((a, b) => b.count - a.count);

    // Attach best icon match per species
    return entries.slice(0, 8).map((e) => ({
      ...e,
      icon: bestMatchIcon(e.name, icons) || undefined,
    }));
  }, [data, icons]);

  const total = useMemo(() => top.reduce((s, x) => s + (x.count || 0), 0), [top]);

  return (
    <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Compact Header */}
      <div className="p-3 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--foreground)]">Top Species</h3>
        <p className="text-xs text-[var(--muted)]">Most abundant detected</p>
      </div>

      {/* Content */}
      <div className="p-3 overflow-y-auto h-[calc(100%-68px)]">
        {loading ? (
          <div className="text-xs text-[var(--muted)]">Loading…</div>
        ) : !top.length ? (
          <div className="text-xs text-[var(--muted)]">No detections yet</div>
        ) : (
          <div className="space-y-2">
            {top.map((s) => {
              const pct = total > 0 ? Math.round((s.count / total) * 100) : 0;
              return (
                <div
                  key={s.name}
                  className="flex items-center gap-2 p-2 rounded-lg bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-100 hover:from-slate-100 hover:to-gray-100 transition-colors"
                >
                  <div className="w-7 h-7 rounded-md bg-white grid place-items-center border border-[var(--border)]">
                    {s.icon ? (
                      <Image
                        src={`/pytoplanktonSvg/${s.icon}`}
                        alt={s.name}
                        width={18}
                        height={18}
                        className="opacity-90"
                      />
                    ) : (
                      <div className="w-3.5 h-3.5 bg-teal-400/70 rounded-full" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium text-[var(--foreground)] truncate">{s.name}</div>
                    <div className="text-[10px] text-[var(--muted)]">{s.count.toLocaleString()} cells</div>
                    <div className="mt-1 h-1.5 rounded bg-slate-100 overflow-hidden">
                      <div
                        className="h-1.5 bg-teal-300"
                        style={{ width: `${pct}%` }}
                        aria-hidden
                      />
                    </div>
                  </div>
                  <div className="text-[10px] font-medium text-[var(--foreground)] w-8 text-right">{pct}%</div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}