import React from "react";
import { cn } from "@/components/utils/cn";

type Props = {
  title: string;
  subtitle?: string;
  accent?: string; // color string like #22d3ee
  icon?: React.ReactNode; // optional icon, no gradients
};

export default function CardMini({ title, subtitle, accent = "#3b82f6", icon }: Props) {
  const capitalize = (s?: string | null) => {
    if (!s) return "";
    return s.charAt(0).toUpperCase() + s.slice(1);
  };
  return (
    <div
      className={cn(
        "relative h-48 w-[160px] rounded-xl border border-[var(--border)] transition-all duration-200 hover:shadow-soft-lg hover:scale-[1.02]",
        "bg-white shadow-soft"
      )}
    >
      <div className="relative flex h-full flex-col items-center justify-center gap-3 text-center px-4">
        {icon ? (
          <div className="h-16 w-16 flex items-center justify-center bg-gray-50 rounded-full" style={{ color: accent }}>
            {icon}
          </div>
        ) : (
          <div className="h-16 w-16 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-full flex items-center justify-center">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full"></div>
          </div>
        )}
        <div className="text-sm font-medium text-[var(--foreground)]">
          {capitalize(title)}
        </div>
        <div className="text-xs text-[var(--muted)] bg-gray-50 px-2 py-1 rounded-full">
          {subtitle ?? 0} detections
        </div>
      </div>
    </div>
  );
}
