"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect, useCallback } from "react";
import {
  LayoutDashboard,
  FileText,
  Map,
  BarChart3,
  Kanban,
  Users,
  Settings,
  Menu,
  X,
} from "lucide-react";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/complaints", label: "Complaints", icon: FileText },
  { href: "/map", label: "Map View", icon: Map },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/kanban", label: "Kanban Board", icon: Kanban },
  { href: "/officers", label: "Officers", icon: Users },
  { href: "/settings", label: "Settings", icon: Settings },
] as const;

export default function Sidebar() {
  const path = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close mobile drawer on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [path]);

  // Close on Escape
  const handleKey = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") setMobileOpen(false);
  }, []);
  useEffect(() => {
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [handleKey]);

  // Lock body scroll when mobile drawer open
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  return (
    <>
      {/* ── Mobile top bar (below md) ───────────────────────── */}
      <header className="fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 md:hidden">
        <span className="text-base font-bold tracking-tight text-[#1B3A5C]">
          Delhi PS-CRM
        </span>
        <button
          onClick={() => setMobileOpen(true)}
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
          aria-label="Open navigation"
        >
          <Menu className="h-5 w-5" />
        </button>
      </header>

      {/* ── Mobile overlay ──────────────────────────────────── */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* ── Mobile drawer ───────────────────────────────────── */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-200 md:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div>
            <span className="text-base font-bold tracking-tight text-[#1B3A5C]">
              Delhi PS-CRM
            </span>
            <p className="text-[10px] text-slate-500">Every complaint heard. Every issue resolved.</p>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100"
            aria-label="Close navigation"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-1">
            {NAV.map(({ href, label, icon: Icon }) => {
              const active =
                href === "/" ? path === "/" : path.startsWith(href);
              return (
                <li key={href}>
                  <Link
                    href={href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                      active
                        ? "bg-[#1B3A5C] text-white"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* ── Tablet sidebar — icons only (md to lg) ──────────── */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-16 flex-col border-r border-slate-200 bg-white md:flex lg:hidden">
        <div className="flex h-14 items-center justify-center border-b border-slate-200">
          <span className="text-sm font-bold text-[#1B3A5C]">PS</span>
        </div>
        <nav className="flex-1 overflow-y-auto px-2 py-3">
          <ul className="space-y-1">
            {NAV.map(({ href, label, icon: Icon }) => {
              const active =
                href === "/" ? path === "/" : path.startsWith(href);
              return (
                <li key={href}>
                  <Link
                    href={href}
                    title={label}
                    className={`flex items-center justify-center rounded-lg p-2.5 transition-colors ${
                      active
                        ? "bg-[#1B3A5C] text-white"
                        : "text-slate-500 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* ── Desktop sidebar — full (lg and above) ───────────── */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-slate-200 bg-white lg:flex">
        <div className="flex flex-col gap-0.5 border-b border-slate-200 px-6 py-5">
          <span className="text-lg font-bold tracking-tight text-[#1B3A5C]">
            Delhi PS-CRM
          </span>
          <span className="text-xs text-slate-500">Every complaint heard. Every issue resolved.</span>
        </div>
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-1">
            {NAV.map(({ href, label, icon: Icon }) => {
              const active =
                href === "/" ? path === "/" : path.startsWith(href);
              return (
                <li key={href}>
                  <Link
                    href={href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                      active
                        ? "bg-[#1B3A5C] text-white"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>
    </>
  );
}
