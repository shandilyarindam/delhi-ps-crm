/* ──────────────────────────────────────────────
   Shared constants, mappings, and helper fns
   ────────────────────────────────────────────── */

export const CATEGORY_DEPT: Record<string, string> = {
  "Waste Management": "MCD",
  "Water Supply": "DJB Water",
  Roads: "PWD",
  "Sewage & Drainage": "DJB Drainage",
  Electricity: "BSES/TPDDL",
  Other: "Nodal",
};

export const OFFICERS: Record<string, string[]> = {
  "Waste Management": ["Saksham Gupta", "Priya Mehta", "Rajesh Kumar", "Deepak Sharma"],
  "Water Supply": ["Ritika Singh", "Amit Verma", "Sunita Rao", "Vikram Nair"],
  Roads: ["Ridhima Aggarwal", "Manish Tiwari", "Kavita Joshi", "Suresh Pandey"],
  "Sewage & Drainage": ["Gaurav Yadav", "Neha Gupta", "Ravi Shankar", "Pooja Mishra"],
  Electricity: ["Eon Aether", "Rohit Kapoor", "Ananya Singh", "Karan Malhotra"],
  Other: ["Priya Mehta", "Amit Verma"],
};

export const ALL_OFFICERS = Object.entries(OFFICERS).flatMap(([dept, names]) =>
  names.map((n) => ({ name: n, department: dept }))
);

export const CATEGORIES = [
  "Waste Management",
  "Water Supply",
  "Roads",
  "Sewage & Drainage",
  "Electricity",
  "Other",
] as const;

export type Status = "open" | "assigned" | "resolved" | "escalated";
export type Urgency = "Critical" | "High" | "Medium" | "Low";

export const STATUS_COLOR: Record<Status, string> = {
  open: "bg-amber-100 text-amber-800 border-amber-300",
  assigned: "bg-blue-100 text-blue-800 border-blue-300",
  resolved: "bg-emerald-100 text-emerald-800 border-emerald-300",
  escalated: "bg-red-100 text-red-800 border-red-300",
};

export const URGENCY_COLOR: Record<Urgency, string> = {
  Critical: "bg-red-100 text-red-800 border-red-300",
  High: "bg-orange-100 text-orange-800 border-orange-300",
  Medium: "bg-yellow-100 text-yellow-800 border-yellow-300",
  Low: "bg-green-100 text-green-800 border-green-300",
};

export function ticketId(uuid: string): string {
  return uuid.slice(0, 8).toUpperCase();
}

export function dept(category: string | null): string {
  return CATEGORY_DEPT[category || "Other"] ?? "Nodal";
}

export function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function fmtDate(ts: string): string {
  return new Date(ts).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

/** Truncate urgency like "Critical (health/safety risk...)" to "Critical" */
export function shortUrgency(raw: string | null): string {
  if (!raw) return "Low";
  return raw.split("(")[0].trim() || "Low";
}
