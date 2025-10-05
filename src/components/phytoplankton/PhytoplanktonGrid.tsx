"use client";
import React, { useEffect, useMemo, useState } from "react";
import CardMini from "./CardMini";
import Image from "next/image";
import { bestMatchIcon } from "@/lib/iconMatch";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": string | number;
};

const ACCENTS = [
  "#22c55e",
  "#06b6d4",
  "#8b5cf6",
  "#f59e0b",
  "#60a5fa",
  "#ec4899",
];

type OnSelect = (item: { name: string; count: number; iconFile?: string }) => void;

export default function PhytoplanktonGrid({ onSelect }: { onSelect?: OnSelect } = {}) {
  const capitalize = (s?: string | null) => {
    if (!s) return "";
    return s.charAt(0).toUpperCase() + s.slice(1);
  };
  const [items, setItems] = useState<RawPhyto[]>([]);
  const [loading, setLoading] = useState(true);
  const [icons, setIcons] = useState<string[]>([]);

  useEffect(() => {
    let ignore = false;
    // Initial load
    fetch("/api/phytoplankton")
      .then((r) => r.json())
      .then((data: RawPhyto[]) => {
        if (!ignore) setItems(data);
      })
      .finally(() => setLoading(false));

    // Live updates via SSE (if backend emits events)
    const sse = new EventSource("/api/phytoplankton/stream");
    sse.onmessage = (ev) => {
      try {
        const payload = JSON.parse(ev.data) as RawPhyto[];
        if (!ignore && Array.isArray(payload)) setItems(payload);
      } catch {}
    };
    sse.onerror = () => {
      // Keep silent if stream is unavailable; grid will show initial fetch.
      sse.close();
    };
    return () => {
      ignore = true;
      sse.close();
    };
  }, []);

  // Fetch list of available svg filenames once
  useEffect(() => {
    fetch("/api/icons/phytoplankton")
      .then((r) => r.json())
      .then((d) => setIcons(Array.isArray(d.files) ? d.files : []))
      .catch(() => setIcons([]));
  }, []);

  const parsed = useMemo(
    () =>
      items.map((d, i) => ({
        name: capitalize(d.phytoplanktonscientificName),
        count: Number(d["no of that pyhtoplankon"]) || 0,
        accent: ACCENTS[i % ACCENTS.length],
      })),
    [items]
  );

  if (!loading && parsed.length === 0) {
    return (
      <div className="min-h-[calc(100vh-6rem)] grid place-items-center">
        <div className="text-base text-[var(--muted)]">
          awaiting data from live feed
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="overflow-x-auto overflow-y-hidden [scrollbar-width:none] [-ms-overflow-style:none]" style={{ WebkitOverflowScrolling: "touch" }}>
        <div className="flex gap-8 pr-8 snap-x snap-mandatory">
          {parsed.map((p) => {
        const file = bestMatchIcon(p.name, icons);
        const icon = file ? (
          <Image
            src={`/pytoplanktonSvg/${file}`}
            alt=""
            width={80}
            height={80}
            className="opacity-90"
          />
        ) : undefined;
            return (
              <button
                key={p.name + p.count}
                className="snap-start first:pl-2 focus:outline-none"
                onClick={() => onSelect?.({ name: p.name, count: p.count, iconFile: file ?? undefined })}
              >
                <CardMini
                    title={p.name}
                  subtitle={String(p.count)}
                  accent={p.accent}
                  icon={icon}
                />
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
