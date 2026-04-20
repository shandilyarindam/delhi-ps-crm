"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  FileText,
  AlertCircle,
  CheckCircle,
  Users,
  AlertTriangle,
} from "lucide-react";
import {
  ticketId,
  dept,
  STATUS_COLOR,
  type Status,
  fmtDate,
} from "@/lib/constants";
import dynamic from "next/dynamic";

/* ── Mini-map (Leaflet, SSR-safe) ────────────────────────────── */
const DashboardMap = dynamic(() => import("@/components/dashboard-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center text-sm text-slate-400">
      Loading map...
    </div>
  ),
});

/* ── Types ────────────────────────────────────────────────────── */
interface Complaint {
  id: string;
  summary: string | null;
  category: string | null;
  status: string | null;
  urgency: string | null;
  timestamp: string | null;
  location: string | null;
  ward: string | null;
}

interface Stats {
  total: number;
  open: number;
  assigned: number;
  resolved: number;
  critical: number;
}

/* ── Page ─────────────────────────────────────────────────────── */
export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>({
    total: 0,
    open: 0,
    assigned: 0,
    resolved: 0,
    critical: 0,
  });
  const [recent, setRecent] = useState<Complaint[]>([]);
  const [allComplaints, setAllComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from("raw_complaints")
        .select("id,summary,category,status,urgency,timestamp,location,ward")
        .order("timestamp", { ascending: false });

      if (error) throw error;
      const rows = (data || []) as Complaint[];
      setAllComplaints(rows);
      setRecent(rows.slice(0, 10));

      const s: Stats = { total: 0, open: 0, assigned: 0, resolved: 0, critical: 0 };
      for (const r of rows) {
        s.total++;
        if (r.status === "open") s.open++;
        if (r.status === "assigned") s.assigned++;
        if (r.status === "resolved") s.resolved++;
        if (r.urgency === "Critical" && r.status !== "resolved") s.critical++;
      }
      setStats(s);
    } catch {
      console.error("Failed to fetch dashboard data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const iv = setInterval(fetchData, 30000);
    return () => clearInterval(iv);
  }, [fetchData]);

  const statCards = [
    {
      label: "TOTAL",
      value: stats.total,
      icon: FileText,
      sub: "All complaints",
      accent: "text-slate-700",
    },
    {
      label: "OPEN",
      value: stats.open,
      icon: AlertCircle,
      sub: "Awaiting action",
      accent: "text-amber-600",
    },
    {
      label: "ASSIGNED",
      value: stats.assigned,
      icon: Users,
      sub: "Under investigation",
      accent: "text-blue-600",
    },
    {
      label: "RESOLVED",
      value: stats.resolved,
      icon: CheckCircle,
      sub: "Closed complaints",
      accent: "text-emerald-600",
    },
    {
      label: "CRITICAL",
      value: stats.critical,
      icon: AlertTriangle,
      sub: "Action required",
      accent: "text-red-600",
    },
  ];

  return (
    <div className="p-4 md:p-6 lg:p-8">
      <h1 className="mb-1 text-xl font-bold text-[#1B3A5C] md:text-2xl">
        Real-time Grievance Analytics
      </h1>
      <p className="mb-4 text-xs text-slate-500 md:mb-6 md:text-sm">
        Live overview of civic complaints across Delhi
      </p>

      {/* Stat cards */}
      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 md:mb-8 md:gap-4 lg:grid-cols-5">
        {statCards.map((c) => (
          <Card
            key={c.label}
            className="border border-slate-200 bg-white shadow-sm"
          >
            <CardContent className="flex flex-col gap-1 p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold tracking-wider text-slate-400">
                  {c.label}
                </span>
                <c.icon className={`h-4 w-4 ${c.accent}`} />
              </div>
              {loading ? (
                <div className="h-8 w-16 animate-pulse rounded bg-slate-200" />
              ) : (
                <span className={`text-2xl font-bold ${c.accent}`}>
                  {c.value}
                </span>
              )}
              <span className="text-xs text-slate-400">{c.sub}</span>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Bottom — Table + Map side-by-side */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Recent Activity Table */}
        <Card className="border border-slate-200 bg-white shadow-sm xl:col-span-2">
          <CardHeader className="border-b border-slate-100 pb-3">
            <CardTitle className="text-base font-semibold text-[#1B3A5C]">
              Recent System Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto p-0">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="text-xs">Complaint ID</TableHead>
                  <TableHead className="text-xs">Subject</TableHead>
                  <TableHead className="text-xs">Department</TableHead>
                  <TableHead className="text-xs">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading
                  ? Array.from({ length: 5 }).map((_, i) => (
                      <TableRow key={i}>
                        {Array.from({ length: 4 }).map((_, j) => (
                          <TableCell key={j}>
                            <div className="h-4 w-20 animate-pulse rounded bg-slate-200" />
                          </TableCell>
                        ))}
                      </TableRow>
                    ))
                  : recent.map((c) => (
                      <TableRow
                        key={c.id}
                        className="hover:bg-slate-50/50"
                      >
                        <TableCell className="font-mono text-xs font-medium text-slate-700">
                          {ticketId(c.id)}
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate text-sm text-slate-600">
                          {c.summary || "No summary"}
                        </TableCell>
                        <TableCell className="text-xs text-slate-500">
                          {dept(c.category)}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={`text-xs capitalize ${
                              STATUS_COLOR[
                                (c.status as Status) || "open"
                              ]
                            }`}
                          >
                            {c.status || "open"}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Mini map — hidden on mobile */}
        <Card className="hidden border border-slate-200 bg-white shadow-sm md:block">
          <CardHeader className="border-b border-slate-100 pb-3">
            <CardTitle className="text-base font-semibold text-[#1B3A5C]">
              Geospatial Distribution
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[400px] p-0">
            <DashboardMap complaints={allComplaints} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
