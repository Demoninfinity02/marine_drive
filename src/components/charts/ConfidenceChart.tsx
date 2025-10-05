"use client";
import React, { useEffect, useMemo, useState } from "react";
import { cn } from "@/components/utils/cn";

type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": string | number;
  Confidence: string | number;
};

type ConfidenceData = {
  name: string;
  confidence: number;
  count: number;
  color: string;
};

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 85) return "#10b981"; // emerald - excellent
  if (confidence >= 75) return "#3b82f6"; // blue - good
  if (confidence >= 65) return "#8b5cf6"; // purple - medium
  if (confidence >= 50) return "#f59e0b"; // amber - fair
  return "#ef4444"; // red - low
};

const getConfidenceLabel = (confidence: number) => {
  if (confidence >= 85) return "Excellent";
  if (confidence >= 75) return "Good";
  if (confidence >= 65) return "Medium";
  if (confidence >= 50) return "Fair";
  return "Low";
};

const capitalize = (s?: string | null) => {
  if (!s) return "";
  return s.charAt(0).toUpperCase() + s.slice(1);
};

type Props = {
  selectedName?: string | null;
  className?: string;
};

export default function ConfidenceChart({ selectedName, className }: Props) {
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

  const confidenceData = useMemo(() => {
    if (!items.length) return [] as ConfidenceData[];
    
    return items
      .map((d) => ({
        name: capitalize(d.phytoplanktonscientificName || ""),
        confidence: Number(d.Confidence) || 0,
        count: Number(d["no of that pyhtoplankon"]) || 0,
        color: getConfidenceColor(Number(d.Confidence) || 0),
      }))
      .filter((x) => x.name && x.confidence > 0)
      .sort((a, b) => b.confidence - a.confidence) // Sort by confidence descending
      .slice(0, 6); // Show top 6 species
  }, [items]);

  return (
    <section className={cn("overflow-hidden rounded-xl", className)}>
      <div className="p-6 border-b border-[var(--border)]">
        <h3 className="text-lg font-medium text-[var(--foreground)]">Detection Confidence</h3>
        <p className="text-sm text-[var(--muted)] mt-1">AI confidence scores for species identification</p>
      </div>
      <div className="p-6">
        {loading ? (
          <div className="h-[280px] grid place-items-center text-[var(--muted)] text-sm">Loading…</div>
        ) : confidenceData.length === 0 ? (
          <div className="h-[280px] grid place-items-center text-[var(--muted)] text-sm">Awaiting data</div>
        ) : (
          <div className="space-y-4">
            {/* Vertical bar chart */}
            <div className="flex items-end justify-center gap-6 h-48 relative">
              {/* Y-axis baseline */}
              <div className="absolute bottom-0 left-0 right-0 h-px bg-gray-300"></div>
              
              {confidenceData.map((item, i) => {
                const isSelected = selectedName && 
                  item.name.toLowerCase().trim() === selectedName.toLowerCase().trim();
                const opacity = selectedName ? (isSelected ? 1.0 : 0.5) : 1.0;
                const barHeight = (item.confidence / 100) * 100; // Convert to percentage of container
                
                return (
                  <div key={i} className="flex flex-col items-center" style={{ opacity }}>
                    {/* Confidence score on top */}
                    <span className="text-xs font-semibold text-[var(--foreground)] tabular-nums mb-2">
                      {item.confidence}%
                    </span>
                    
                    {/* Confidence label badge */}
                    <span 
                      className="text-xs px-2 py-0.5 rounded-full text-white font-medium whitespace-nowrap mb-2"
                      style={{ backgroundColor: item.color }}
                    >
                      {getConfidenceLabel(item.confidence)}
                    </span>
                    
                    {/* Vertical bar */}
                    <div className="relative flex flex-col justify-end h-32 w-12">
                      <div 
                        className="w-full rounded-t-lg transition-all duration-700 ease-out"
                        style={{ 
                          height: `${barHeight}%`,
                          backgroundColor: item.color,
                          background: `linear-gradient(180deg, ${item.color}, ${item.color}dd)`
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* X-axis labels */}
            <div className="flex justify-center gap-6">
              {confidenceData.map((item, i) => {
                const isSelected = selectedName && 
                  item.name.toLowerCase().trim() === selectedName.toLowerCase().trim();
                const opacity = selectedName ? (isSelected ? 1.0 : 0.5) : 1.0;
                
                return (
                  <div key={i} className="w-12 text-center" style={{ opacity }}>
                    <span className="text-xs font-medium text-[var(--foreground)] leading-tight">
                      {item.name}
                    </span>
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