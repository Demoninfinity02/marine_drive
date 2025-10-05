"use client";
import React, { useEffect, useMemo, useState } from "react";
import { cn } from "@/components/utils/cn";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": string | number;
  Confidence: string | number;
};

type Slice = { name: string; count: number; color: string };

const PALETTE = [
  "#34d399", // soft emerald
  "#60a5fa", // soft blue  
  "#a78bfa", // soft violet
  "#fb7185", // soft pink
  "#fbbf24", // soft amber (for "Other")
];

const capitalize = (s?: string | null) => {
  if (!s) return "";
  return s.charAt(0).toUpperCase() + s.slice(1);
};

type Props = {
  selectedName?: string | null;
  className?: string;
};

export default function SpeciesCompositionCard({ selectedName, className }: Props) {
  const [items, setItems] = useState<RawPhyto[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    fetch("/api/phytoplankton")
      .then((r) => r.json())
      .then((data: RawPhyto[]) => {
        if (!ignore) setItems(Array.isArray(data) ? data : []);
      })
      .finally(() => setLoading(false));
    return () => {
      ignore = true;
    };
  }, []);

  const slices = useMemo(() => {
    if (!items.length) return [] as Slice[];
    const mapped = items
      .map((d) => ({
        name: d.phytoplanktonscientificName || "",
        count: Number(d["no of that pyhtoplankon"]) || 0,
      }))
      .filter((x) => x.name && x.count > 0)
      .sort((a, b) => b.count - a.count);

    if (mapped.length === 0) return [] as Slice[];

    const TOP = 4;
    const top = mapped.slice(0, TOP);
    const rest = mapped.slice(TOP);
    const otherTotal = rest.reduce((sum, r) => sum + r.count, 0);

    const base: Slice[] = top.map((t, i) => ({
      name: capitalize(t.name),
      count: t.count,
      color: PALETTE[i % PALETTE.length],
    }));

    if (otherTotal > 0) {
      base.push({ name: "Other", count: otherTotal, color: PALETTE[4] });
    }
    return base;
  }, [items]);

  const total = useMemo(() => slices.reduce((s, x) => s + x.count, 0), [slices]);

  // Compute selected species percentage based on raw items (not sliced), case-insensitive
  const selectedPct = useMemo(() => {
    if (!selectedName || !items.length) return null;
    const sel = String(selectedName).trim().toLowerCase();
    let selCount = 0;
    let t = 0;
    for (const d of items) {
      const name = String(d.phytoplanktonscientificName || "").trim().toLowerCase();
      const count = Number(d["no of that pyhtoplankon"]) || 0;
      t += count;
      if (name === sel) selCount += count;
    }
    if (t === 0) return 0;
    return (selCount / t) * 100;
  }, [items, selectedName]);

  // Donut sizing
  const size = 180; // px
  const half = size / 2;
  const r = 54;
  const stroke = 18;
  const C = 2 * Math.PI * r;

  let offset = 0;

  return (
    <section className={cn("overflow-hidden rounded-xl bg-white", className)}>
      <div className="p-6 border-b border-[var(--border)]">
        <h3 className="text-lg font-medium text-[var(--foreground)]">Species Composition</h3>
        <p className="text-sm text-[var(--muted)] mt-1">Distribution of detected species</p>
      </div>
      <div className="p-6">
        {loading ? (
          <div className="h-[200px] grid place-items-center text-[var(--muted)] text-sm">Loading…</div>
        ) : slices.length === 0 ? (
          <div className="h-[200px] grid place-items-center text-[var(--muted)] text-sm">Awaiting data</div>
        ) : (
          <div className="flex items-center gap-8">
            {/* Donut */}
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="shrink-0">
            <g transform={`translate(${half}, ${half}) rotate(-90)`}>
            {/* track */}
            <circle r={r} cx={0} cy={0} fill="none" stroke="#f1f5f9" strokeWidth={stroke} />
            {slices.map((s, i) => {
                const pct = total === 0 ? 0 : s.count / total;
                const len = Math.max(0, Math.min(C, C * pct));
                
                // Add small gap between arcs to prevent overlap
                const gapSize = 2; // pixels
                const adjustedLen = Math.max(0, len - gapSize);
                const dash = `${adjustedLen} ${C - adjustedLen}`;
                
                // Check if this slice matches the selected species (case-insensitive)
                const isSelected = selectedName && 
                  s.name.toLowerCase().trim() === selectedName.toLowerCase().trim();
                const opacity = selectedName ? (isSelected ? 1.0 : 0.4) : 1.0;
                
                const circle = (
                <circle
                    key={i}
                    r={r}
                    cx={0}
                    cy={0}
                    fill="none"
                    stroke={s.color}
                    strokeWidth={stroke}
                    strokeDasharray={dash}
                    strokeDashoffset={-offset}
                    strokeLinecap="round"
                    opacity={opacity}
                />
                );
                offset += len;
                return circle;
            })}
              </g>
              {/* inner hole to soften */}
              <circle r={r - stroke / 2} cx={half} cy={half} fill="white" />
              {/* center label */}
              <text x={half} y={half} textAnchor="middle" dominantBaseline="middle" className="fill-[var(--foreground)]" style={{ fontSize: 14, fontWeight: 600 }}>
                {selectedPct == null ? "—" : `${Math.round(selectedPct)}%`}
              </text>
            </svg>
            {/* Legend */}
            <div className="grid gap-3 text-sm flex-1">
              {slices.map((s, i) => {
                const pct = total === 0 ? 0 : (s.count / total) * 100;
                const isSelected = selectedName && 
                  s.name.toLowerCase().trim() === selectedName.toLowerCase().trim();
                const opacity = selectedName ? (isSelected ? 1.0 : 0.4) : 1.0;
                
                return (
                  <div key={i} className="flex items-center gap-3" style={{ opacity }}>
                    <span className="inline-block w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: s.color }} />
                    <span className="text-[var(--foreground)] font-medium">{s.name}</span>
                    <span className="ml-auto text-[var(--muted)] tabular-nums">{pct.toFixed(0)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
