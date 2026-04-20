"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts";
import { FileText, Zap } from "lucide-react";

interface Complaint {
  id: string;
  category: string | null;
  urgency: string | null;
  status: string | null;
  timestamp: string | null;
  assigned_at: string | null;
  resolved_at: string | null;
}

const PIE_COLORS = [
  "#1B3A5C",
  "#3b82f6",
  "#22c55e",
  "#f97316",
  "#eab308",
  "#a855f7",
];

export default function AnalyticsPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const { data } = await supabase
        .from("raw_complaints")
        .select("id,category,urgency,status,timestamp,assigned_at,resolved_at");
      setComplaints((data || []) as Complaint[]);
    } catch {
      console.error("Failed to fetch analytics data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ── Derived metrics ──
  const total = complaints.length;
  const resolved = complaints.filter((c) => c.status === "resolved").length;
  const resolvedPct = total > 0 ? (resolved / total) * 100 : 0;

  // Response velocity: avg minutes from timestamp to assigned_at
  const responseTimes = complaints
    .filter((c) => c.timestamp && c.assigned_at)
    .map((c) => {
      const diff =
        new Date(c.assigned_at!).getTime() -
        new Date(c.timestamp!).getTime();
      return diff / 60000; // minutes
    })
    .filter((m) => m > 0);
  const avgResponse =
    responseTimes.length > 0
      ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
      : 0;



  // ── Incidence Velocity (last 14 days) ──
  const dailyMap: Record<string, number> = {};
  const now = Date.now();
  for (let i = 13; i >= 0; i--) {
    const d = new Date(now - i * 86400000);
    const key = d.toISOString().slice(0, 10);
    dailyMap[key] = 0;
  }
  for (const c of complaints) {
    if (!c.timestamp) continue;
    const key = c.timestamp.slice(0, 10);
    if (key in dailyMap) dailyMap[key]++;
  }
  const dailyData = Object.entries(dailyMap).map(([date, count]) => ({
    date: new Date(date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
    }),
    count,
  }));

  // ── Urgency distribution ──
  const urgCounts: Record<string, number> = {
    Critical: 0,
    High: 0,
    Medium: 0,
    Low: 0,
  };
  for (const c of complaints) {
    const raw = c.urgency || "Low";
    const key = raw.split("(")[0].trim();
    urgCounts[key] = (urgCounts[key] || 0) + 1;
  }
  const urgData = Object.entries(urgCounts).map(([name, value]) => ({
    name,
    value,
    pct: total > 0 ? Math.round((value / total) * 100) : 0,
  }));
  const urgColors: Record<string, string> = {
    Critical: "#ef4444",
    High: "#f97316",
    Medium: "#eab308",
    Low: "#22c55e",
  };

  // ── Category breakdown ──
  const catCounts: Record<string, number> = {};
  for (const c of complaints) {
    const cat = c.category || "Other";
    catCounts[cat] = (catCounts[cat] || 0) + 1;
  }
  const catData = Object.entries(catCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({ name, value }));

  // ── Resolution rate over time (weekly) ──
  const weeklyRes: Record<string, { total: number; resolved: number }> = {};
  for (const c of complaints) {
    if (!c.timestamp) continue;
    const d = new Date(c.timestamp);
    const weekStart = new Date(d);
    weekStart.setDate(d.getDate() - d.getDay());
    const key = weekStart.toISOString().slice(0, 10);
    if (!weeklyRes[key]) weeklyRes[key] = { total: 0, resolved: 0 };
    weeklyRes[key].total++;
    if (c.status === "resolved") weeklyRes[key].resolved++;
  }
  const resolutionData = Object.entries(weeklyRes)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .slice(-8)
    .map(([week, v]) => ({
      week: new Date(week).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
      }),
      rate: v.total > 0 ? Math.round((v.resolved / v.total) * 100) : 0,
    }));

  return (
    <div className="p-4 md:p-6 lg:p-8">
      <div className="mb-1">
        <h1 className="text-xl font-bold text-[#1B3A5C] md:text-2xl">
          Analytics
        </h1>
      </div>
      <p className="mb-4 text-xs text-slate-500 md:mb-6 md:text-sm">
        Comprehensive analytics and performance metrics
      </p>

      {/* Top metrics */}
      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 md:mb-8 md:gap-4">
        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-[#1B3A5C]">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              {loading ? (
                <div className="h-7 w-12 animate-pulse rounded bg-slate-200" />
              ) : (
                <span className="text-2xl font-bold text-[#1B3A5C]">
                  {total}
                </span>
              )}
              <p className="text-xs text-slate-500">Total Reports</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <Zap className="h-5 w-5" />
            </div>
            <div>
              {loading ? (
                <div className="h-7 w-12 animate-pulse rounded bg-slate-200" />
              ) : (
                <span className="text-2xl font-bold text-blue-600">
                  {avgResponse.toFixed(1)}m
                </span>
              )}
              <p className="text-xs text-slate-500">Response Velocity</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Incidence Velocity */}
        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-3">
            <CardTitle className="text-sm font-semibold text-[#1B3A5C]">
              Incidence Velocity (14 days)
            </CardTitle>
          </CardHeader>
          <CardContent className="h-64 pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f1f1" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#1B3A5C"
                  strokeWidth={2}
                  dot={{ r: 3, fill: "#1B3A5C" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Urgency Distribution */}
        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-3">
            <CardTitle className="text-sm font-semibold text-[#1B3A5C]">
              Urgency Distribution
            </CardTitle>
          </CardHeader>
          <CardContent className="h-64 pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={urgData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f1f1" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10 }} width={80} />
                <Tooltip formatter={(val) => [`${val}`, "Count"]} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {urgData.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={urgColors[entry.name] || "#6b7280"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Category Breakdown */}
        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-3">
            <CardTitle className="text-sm font-semibold text-[#1B3A5C]">
              Category Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent className="h-64 pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={catData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                  }
                >
                  {catData.map((_, i) => (
                    <Cell
                      key={i}
                      fill={PIE_COLORS[i % PIE_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Resolution Rate */}
        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-3">
            <CardTitle className="text-sm font-semibold text-[#1B3A5C]">
              Resolution Rate Over Time
            </CardTitle>
          </CardHeader>
          <CardContent className="h-64 pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={resolutionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f1f1" />
                <XAxis dataKey="week" tick={{ fontSize: 10 }} />
                <YAxis
                  tick={{ fontSize: 10 }}
                  domain={[0, 100]}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip formatter={(val) => [`${val}%`, "Resolution Rate"]} />
                <Area
                  type="monotone"
                  dataKey="rate"
                  stroke="#22c55e"
                  fill="#22c55e"
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
