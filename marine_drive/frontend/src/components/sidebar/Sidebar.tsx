"use client";
import React from "react";
import {
  Home,
  Activity,
  Bell,
  Search,
  Settings,
  Users2,
  BarChart3,
  Calendar,
  LayoutGrid,
} from "lucide-react";
import NavIcon from "./NavIcon";

export default function Sidebar() {
  return (
    <aside
      className="fixed left-0 top-0 z-20 h-screen w-[84px] border-r border-[var(--border)] bg-white/80 backdrop-blur-xl"
      aria-label="Primary"
    >
      <div className="flex h-full flex-col items-center py-6 gap-6">
        {/* Top spacer in place of logo (intentionally blank) */}
        <div className="h-10 w-10 rounded-2xl bg-transparent" />

        {/* Primary group */}
        <nav className="flex flex-col items-center gap-3">
          <NavIcon icon={Home} label="Dashboard" active />
          <NavIcon icon={Search} label="Search" />
          <NavIcon icon={Activity} label="Analytics" />
          <NavIcon icon={Users2} label="Users" />
        </nav>

        {/* Divider */}
        <div className="my-2 h-px w-10 bg-white/10" />

        {/* Secondary group */}
        <nav className="flex flex-col items-center gap-3">
          <NavIcon icon={BarChart3} label="Reports" />
          <NavIcon icon={Calendar} label="Calendar" />
          <NavIcon icon={LayoutGrid} label="Apps" />
        </nav>

        {/* Grow spacer */}
        <div className="flex-1" />

        {/* Utility group */}
        <nav className="flex flex-col items-center gap-3 pb-2">
          <NavIcon icon={Bell} label="Notifications" />
          <NavIcon icon={Settings} label="Settings" />
        </nav>

        {/* Profile circle */}
        <div
          className="mb-2 grid h-12 w-12 place-items-center rounded-2xl bg-white/10 ring-1 ring-white/10"
          aria-label="Profile"
        >
          <div className="h-7 w-7 rounded-full bg-gradient-to-br from-orange-400 to-pink-500" />
        </div>
      </div>
    </aside>
  );
}
