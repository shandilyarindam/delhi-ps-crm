"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Users, Activity, Zap, X, Clock } from "lucide-react";
import { ALL_OFFICERS, ticketId, timeAgo, fmtDate } from "@/lib/constants";

/* ── Types ─────────────────────────────────────────────── */
interface RawComplaint {
  id: string;
  summary: string | null;
  category: string | null;
  status: string | null;
  urgency: string | null;
  location: string | null;
  ward: string | null;
  assigned_to: string | null;
  assigned_at: string | null;
  resolved_at: string | null;
  timestamp: string | null;
}

interface OfficerData {
  name: string;
  department: string;
  assigned: number;
  resolved: number;
  avgResHours: number | null;
  resolutionRate: number;
  resolvedThisWeek: boolean;
  hasActive: boolean;
  complaints: RawComplaint[];
}

/* ── Helpers ───────────────────────────────────────────── */
function initials(name: string): string {
  const parts = name.split(" ");
  return (parts[0]?.[0] || "") + (parts[parts.length - 1]?.[0] || "");
}

function urgencyBadgeColor(u: string | null): string {
  const v = (u || "").split("(")[0].trim();
  if (v === "Critical") return "bg-red-500 text-white";
  if (v === "High") return "bg-orange-500 text-white";
  if (v === "Medium") return "bg-yellow-500 text-white";
  return "bg-slate-200 text-slate-600";
}

function urgencyLabel(u: string | null): string {
  const v = (u || "").split("(")[0].trim();
  if (v === "Critical") return "URGENT";
  if (v === "High") return "HIGH";
  if (v === "Medium") return "MED";
  return "LOW";
}

function statusRowColor(s: string | null): string {
  if (s === "resolved") return "bg-emerald-50/60";
  if (s === "assigned") return "bg-blue-50/60";
  if (s === "escalated") return "bg-red-50/60";
  return "";
}

function timeTaken(a: string | null, r: string | null): string {
  if (!a || !r) return "--";
  const diff = new Date(r).getTime() - new Date(a).getTime();
  if (diff <= 0) return "--";
  const hrs = diff / 3600000;
  if (hrs < 1) return `${Math.round(hrs * 60)}m`;
  if (hrs < 24) return `${hrs.toFixed(1)}h`;
  return `${(hrs / 24).toFixed(1)}d`;
}

/* ── Avatar colors by department ───────────────────────── */
const DEPT_COLORS: Record<string, string> = {
  "Waste Management": "bg-amber-600",
  "Water Supply": "bg-blue-600",
  Roads: "bg-slate-600",
  "Sewage & Drainage": "bg-teal-600",
  Electricity: "bg-violet-600",
  Other: "bg-gray-500",
};

/* ── Component ─────────────────────────────────────────── */
export default function OfficersPage() {
  const [officers, setOfficers] = useState<OfficerData[]>([]);
  const [allComplaints, setAllComplaints] = useState<RawComplaint[]>([]);
  const [loading, setLoading] = useState(true);
  const [drawerOfficer, setDrawerOfficer] = useState<OfficerData | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const { data } = await supabase
        .from("raw_complaints")
        .select("id,summary,category,status,urgency,location,ward,assigned_to,assigned_at,resolved_at,timestamp")
        .order("assigned_at", { ascending: false });

      const rows = (data || []) as RawComplaint[];
      setAllComplaints(rows);

      const now = Date.now();
      const weekAgo = now - 7 * 86400000;

      const officerMap = new Map<string, RawComplaint[]>();
      for (const r of rows) {
        if (!r.assigned_to) continue;
        const key = r.assigned_to.trim();
        if (!officerMap.has(key)) officerMap.set(key, []);
        officerMap.get(key)!.push(r);
      }

      const result: OfficerData[] = ALL_OFFICERS.map((o) => {
        const myComplaints = officerMap.get(o.name) || [];
        const assigned = myComplaints.filter((c) => c.status === "assigned").length;
        const resolved = myComplaints.filter((c) => c.status === "resolved").length;

        const resTimes = myComplaints
          .filter((c) => c.status === "resolved" && c.assigned_at && c.resolved_at)
          .map((c) => (new Date(c.resolved_at!).getTime() - new Date(c.assigned_at!).getTime()) / 3600000)
          .filter((h) => h > 0);

        const avgResHours = resTimes.length > 0
          ? resTimes.reduce((a, b) => a + b, 0) / resTimes.length
          : null;

        const total = assigned + resolved;
        const resolutionRate = total > 0 ? (resolved / total) * 100 : 0;

        const resolvedThisWeek = myComplaints.some(
          (c) => c.status === "resolved" && c.resolved_at && new Date(c.resolved_at).getTime() > weekAgo
        );
        const hasActive = assigned > 0;

        return {
          name: o.name,
          department: o.department,
          assigned,
          resolved,
          avgResHours,
          resolutionRate,
          resolvedThisWeek,
          hasActive,
          complaints: myComplaints,
        };
      });

      setOfficers(result);
    } catch {
      console.error("Failed to fetch officer data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  /* ── Derived metrics ─────────────────────────────────── */
  const totalOfficers = ALL_OFFICERS.length;
  const activeOfficers = officers.filter((o) => o.assigned > 0).length;
  const activeFieldPct = totalOfficers > 0 ? Math.round((activeOfficers / totalOfficers) * 100) : 0;

  const allResTimes = allComplaints
    .filter((c) => c.assigned_at && c.resolved_at && c.status === "resolved")
    .map((c) => (new Date(c.resolved_at!).getTime() - new Date(c.assigned_at!).getTime()) / 60000)
    .filter((m) => m > 0);
  const avgResponseMin = allResTimes.length > 0
    ? allResTimes.reduce((a, b) => a + b, 0) / allResTimes.length
    : 0;

  /* ── Timeline entries ────────────────────────────────── */
  const timelineEntries = allComplaints
    .filter((c) => c.assigned_to && (c.assigned_at || c.resolved_at))
    .slice(0, 50)
    .flatMap((c) => {
      const entries: { type: "assigned" | "resolved"; complaint: RawComplaint; time: string }[] = [];
      if (c.assigned_at) entries.push({ type: "assigned", complaint: c, time: c.assigned_at });
      if (c.status === "resolved" && c.resolved_at) entries.push({ type: "resolved", complaint: c, time: c.resolved_at });
      return entries;
    })
    .sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
    .slice(0, 50);

  const metricCards = [
    { label: "Total Officers", value: totalOfficers.toString(), icon: Users, accent: "text-[#1B3A5C]" },
    { label: "Active Field Load", value: `${activeFieldPct}%`, icon: Activity, accent: "text-blue-600" },
    { label: "Avg Response", value: `${avgResponseMin.toFixed(1)}m`, icon: Zap, accent: "text-emerald-600" },
  ];

  return (
    <div className="p-4 md:p-6 lg:p-8">
      <h1 className="mb-1 text-xl font-bold text-[#1B3A5C] md:text-2xl">
        Officer Accountability
      </h1>
      <p className="mb-4 text-xs text-slate-500 md:mb-6 md:text-sm">
        Performance tracking, activity feed, and complaint assignments
      </p>

      {/* ── Metric cards ────────────────────────────────── */}
      <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3 md:mb-6 md:gap-4">
        {metricCards.map((c) => (
          <Card key={c.label} className="border border-slate-200 bg-white shadow-sm">
            <CardContent className="flex items-center gap-4 p-5">
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 ${c.accent}`}>
                <c.icon className="h-5 w-5" />
              </div>
              <div>
                {loading ? (
                  <div className="h-7 w-12 animate-pulse rounded bg-slate-200" />
                ) : (
                  <span className={`text-2xl font-bold ${c.accent}`}>{c.value}</span>
                )}
                <p className="text-xs text-slate-500">{c.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ── Section 1: Officer Performance Overview ──── */}
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-400">
        Officer Performance Overview
      </h2>

      {loading ? (
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-48 animate-pulse rounded-lg bg-slate-200" />
          ))}
        </div>
      ) : (
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {officers.map((o) => {
            const statusDot = o.resolvedThisWeek
              ? "bg-emerald-400"
              : o.hasActive
              ? "bg-yellow-400"
              : "bg-slate-300";

            return (
              <Card
                key={`${o.department}-${o.name}`}
                className="cursor-pointer border border-slate-200 bg-white shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5"
                onClick={() => setDrawerOfficer(o)}
              >
                <CardContent className="p-4">
                  {/* Header row */}
                  <div className="mb-3 flex items-center gap-3">
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white ${DEPT_COLORS[o.department] || "bg-slate-500"}`}>
                      {initials(o.name)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="truncate text-sm font-semibold text-slate-800">{o.name}</span>
                        <span className={`inline-block h-2 w-2 shrink-0 rounded-full ${statusDot}`} />
                      </div>
                      <Badge variant="outline" className="mt-0.5 text-[10px] text-slate-500">{o.department}</Badge>
                    </div>
                  </div>

                  {/* Metrics row */}
                  <div className="mb-3 grid grid-cols-3 gap-2 text-center">
                    <div>
                      <span className="block text-lg font-bold text-blue-600">{o.assigned}</span>
                      <span className="text-[10px] text-slate-400">Assigned</span>
                    </div>
                    <div>
                      <span className="block text-lg font-bold text-emerald-600">{o.resolved}</span>
                      <span className="text-[10px] text-slate-400">Resolved</span>
                    </div>
                    <div>
                      <span className="block text-lg font-bold text-[#1B3A5C]">
                        {o.avgResHours !== null ? `${o.avgResHours.toFixed(1)}h` : "N/A"}
                      </span>
                      <span className="text-[10px] text-slate-400">Avg Time</span>
                    </div>
                  </div>

                  {/* Resolution progress bar */}
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                      style={{ width: `${Math.min(o.resolutionRate, 100)}%` }}
                    />
                  </div>
                  <p className="mt-1 text-right text-[10px] text-slate-400">
                    {o.resolutionRate.toFixed(0)}% resolution rate
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* ── Section 2: Activity Timeline ────────────── */}
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-400">
        Activity Timeline
      </h2>
      <Card className="border border-slate-200 bg-white shadow-sm">
        <CardContent className="p-4 md:p-6">
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-12 animate-pulse rounded bg-slate-200" />
              ))}
            </div>
          ) : timelineEntries.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-400">No recent activity</p>
          ) : (
            <div className="relative">
              {/* Vertical connector line */}
              <div className="absolute left-5 top-0 bottom-0 w-px bg-slate-200" />

              <div className="space-y-0">
                {timelineEntries.map((entry, idx) => {
                  const c = entry.complaint;
                  const officerName = c.assigned_to || "Unknown";
                  const isResolved = entry.type === "resolved";

                  return (
                    <div key={`${c.id}-${entry.type}-${idx}`} className="relative flex gap-4 py-3">
                      {/* Avatar */}
                      <div className={`z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${isResolved ? "bg-emerald-600" : "bg-blue-600"}`}>
                        {initials(officerName)}
                      </div>

                      {/* Content */}
                      <div className="min-w-0 flex-1 pt-0.5">
                        <p className="text-sm text-slate-700">
                          <span className="font-semibold">{officerName}</span>
                          {isResolved ? " resolved " : " was assigned "}
                          complaint{" "}
                          <span className="font-mono font-semibold text-[#1B3A5C]">
                            #{ticketId(c.id)}
                          </span>
                          <Badge className={`ml-2 text-[10px] ${urgencyBadgeColor(c.urgency)}`}>
                            {urgencyLabel(c.urgency)}
                          </Badge>
                          {" -- "}
                          <span className="text-slate-500">{c.category || "Uncategorized"}</span>
                          {c.location && (
                            <span className="text-slate-400"> in {c.location}</span>
                          )}
                        </p>
                        <p className="mt-0.5 flex items-center gap-1 text-xs text-slate-400">
                          <Clock className="h-3 w-3" />
                          {timeAgo(entry.time)}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Section 3: Officer Detail Drawer ─────────── */}
      {drawerOfficer && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-40 bg-black/30 transition-opacity"
            onClick={() => setDrawerOfficer(null)}
          />
          {/* Drawer */}
          <aside className="fixed inset-y-0 right-0 z-50 flex w-full max-w-2xl flex-col border-l border-slate-200 bg-white shadow-2xl animate-in slide-in-from-right duration-200">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className={`flex h-11 w-11 items-center justify-center rounded-full text-sm font-bold text-white ${DEPT_COLORS[drawerOfficer.department] || "bg-slate-500"}`}>
                  {initials(drawerOfficer.name)}
                </div>
                <div>
                  <h3 className="text-base font-bold text-[#1B3A5C]">{drawerOfficer.name}</h3>
                  <p className="text-xs text-slate-500">{drawerOfficer.department}</p>
                </div>
              </div>
              <button
                onClick={() => setDrawerOfficer(null)}
                className="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-4 gap-3 border-b border-slate-100 px-6 py-4">
              {[
                { label: "Assigned", value: drawerOfficer.assigned, color: "text-blue-600" },
                { label: "Resolved", value: drawerOfficer.resolved, color: "text-emerald-600" },
                { label: "Avg Time", value: drawerOfficer.avgResHours !== null ? `${drawerOfficer.avgResHours.toFixed(1)}h` : "N/A", color: "text-[#1B3A5C]" },
                { label: "Rate", value: `${drawerOfficer.resolutionRate.toFixed(0)}%`, color: "text-violet-600" },
              ].map((s) => (
                <div key={s.label} className="text-center">
                  <span className={`block text-xl font-bold ${s.color}`}>{s.value}</span>
                  <span className="text-[10px] text-slate-400">{s.label}</span>
                </div>
              ))}
            </div>

            {/* Complaint table */}
            <div className="flex-1 overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="text-xs">Ticket</TableHead>
                    <TableHead className="text-xs">Summary</TableHead>
                    <TableHead className="text-xs">Category</TableHead>
                    <TableHead className="text-xs">Urgency</TableHead>
                    <TableHead className="text-xs">Status</TableHead>
                    <TableHead className="text-xs">Assigned</TableHead>
                    <TableHead className="text-xs">Resolved</TableHead>
                    <TableHead className="text-xs">Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {drawerOfficer.complaints.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="py-8 text-center text-sm text-slate-400">
                        No complaints assigned
                      </TableCell>
                    </TableRow>
                  ) : (
                    [...drawerOfficer.complaints]
                      .sort((a, b) => {
                        const ta = a.assigned_at ? new Date(a.assigned_at).getTime() : 0;
                        const tb = b.assigned_at ? new Date(b.assigned_at).getTime() : 0;
                        return tb - ta;
                      })
                      .map((c) => (
                        <TableRow key={c.id} className={`${statusRowColor(c.status)} hover:bg-slate-50/80`}>
                          <TableCell className="font-mono text-xs font-medium text-[#1B3A5C]">
                            {ticketId(c.id)}
                          </TableCell>
                          <TableCell className="max-w-[160px] truncate text-xs text-slate-600">
                            {c.summary || "--"}
                          </TableCell>
                          <TableCell className="text-xs text-slate-500">{c.category || "--"}</TableCell>
                          <TableCell>
                            <Badge className={`text-[10px] ${urgencyBadgeColor(c.urgency)}`}>
                              {urgencyLabel(c.urgency)}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline" className={`text-[10px] capitalize ${
                              c.status === "resolved" ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                              c.status === "assigned" ? "bg-blue-50 text-blue-700 border-blue-200" :
                              c.status === "escalated" ? "bg-red-50 text-red-700 border-red-200" :
                              "bg-slate-50 text-slate-600"
                            }`}>
                              {c.status || "open"}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-xs text-slate-500">
                            {c.assigned_at ? fmtDate(c.assigned_at) : "--"}
                          </TableCell>
                          <TableCell className="text-xs text-slate-500">
                            {c.resolved_at ? fmtDate(c.resolved_at) : "--"}
                          </TableCell>
                          <TableCell className="text-xs font-medium text-slate-600">
                            {timeTaken(c.assigned_at, c.resolved_at)}
                          </TableCell>
                        </TableRow>
                      ))
                  )}
                </TableBody>
              </Table>
            </div>
          </aside>
        </>
      )}
    </div>
  );
}
