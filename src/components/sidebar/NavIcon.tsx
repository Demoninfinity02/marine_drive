"use client";
import { type LucideIcon } from "lucide-react";
import { cn } from "../utils/cn";
import React from "react";
import { useRouter, usePathname } from "next/navigation";

type Props = {
  icon: LucideIcon;
  label: string;
  active?: boolean;
  href?: string;
};

export const NavIcon: React.FC<Props> = ({ icon: Icon, label, active, href }) => {
  const router = useRouter();
  const pathname = usePathname();
  
  // Auto-detect active state based on current pathname if not explicitly set
  const isActive = active !== undefined ? active : (href === pathname || (href === "/" && pathname === "/"));

  const handleClick = () => {
    if (href) {
      router.push(href);
    }
  };
  
  return (
    <div className="relative">
      {isActive && (
        <span
          aria-hidden
          className="absolute -left-3 top-1/2 -translate-y-1/2 h-10 w-[6px] rounded-full bg-orange-500 shadow-[0_0_12px_2px_rgba(249,115,22,0.6)]"
        />
      )}
      <button
        type="button"
        title={label}
        aria-label={label}
        onClick={handleClick}
        className={cn(
          "group relative grid h-12 w-12 place-items-center rounded-2xl transition",
          isActive
            ? "bg-[rgba(255,255,255,0.06)] ring-1 ring-white/10"
            : "hover:bg-white/5"
        )}
      >
        <Icon className={cn(
          "h-5 w-5 transition-colors duration-200",
          isActive ? "text-orange-500" : "text-[var(--muted)] group-hover:text-[var(--foreground)]"
        )} />
      </button>
    </div>
  );
};

export default NavIcon;
