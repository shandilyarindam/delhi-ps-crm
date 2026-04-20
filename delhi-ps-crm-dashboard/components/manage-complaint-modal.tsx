"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CheckCircle, UserPlus } from "lucide-react";
import {
  ticketId,
  OFFICERS,
  URGENCY_COLOR,
  shortUrgency,
  type Urgency,
} from "@/lib/constants";

export interface ManageComplaint {
  id: string;
  summary: string | null;
  category: string | null;
  status: string | null;
  urgency: string | null;
  timestamp: string | null;
  location: string | null;
  ward: string | null;
  assigned_to: string | null;
}

export type ModalFocus = "assign" | "resolve" | null;

interface Props {
  complaint: ManageComplaint | null;
  open: boolean;
  focus?: ModalFocus;
  onClose: () => void;
  onUpdated: () => void;
}

function getOfficersForCategory(category: string | null): string[] {
  if (!category) return OFFICERS["Other"];
  return OFFICERS[category] || OFFICERS["Other"];
}

export default function ManageComplaintModal({
  complaint,
  open,
  focus,
  onClose,
  onUpdated,
}: Props) {
  const [selectedOfficer, setSelectedOfficer] = useState("");
  const [resolveNotes, setResolveNotes] = useState("");
  const [resolveError, setResolveError] = useState(false);
  const [assigning, setAssigning] = useState(false);
  const [resolving, setResolving] = useState(false);

  function reset() {
    setSelectedOfficer("");
    setResolveNotes("");
    setResolveError(false);
  }

  function handleClose() {
    reset();
    onClose();
  }

  async function handleAssignOfficer() {
    if (!complaint || !selectedOfficer) return;
    setAssigning(true);
    await supabase
      .from("raw_complaints")
      .update({
        assigned_to: selectedOfficer,
        assigned_at: new Date().toISOString(),
        status: "assigned",
      })
      .eq("id", complaint.id);
    setAssigning(false);
    reset();
    onUpdated();
  }

  async function handleMarkResolved() {
    if (!complaint) return;
    if (!resolveNotes.trim()) {
      setResolveError(true);
      return;
    }
    setResolving(true);
    await supabase
      .from("raw_complaints")
      .update({
        status: "resolved",
        resolved_at: new Date().toISOString(),
        officer_notes: resolveNotes.trim(),
      })
      .eq("id", complaint.id);
    setResolving(false);
    reset();
    onUpdated();
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        if (!o) handleClose();
      }}
    >
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-[#1B3A5C]">
            Manage Complaint
            {complaint && (
              <Badge variant="outline" className="ml-1 font-mono text-xs">
                {ticketId(complaint.id)}
              </Badge>
            )}
          </DialogTitle>
        </DialogHeader>

        {complaint && (
          <div className="space-y-5">
            {/* ── Complaint Details (Read Only) ── */}
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Category
                  </p>
                  <p className="mt-0.5 font-medium text-slate-700">
                    {complaint.category || "Uncategorized"}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Urgency
                  </p>
                  <Badge
                    variant="outline"
                    className={`mt-0.5 text-xs ${
                      URGENCY_COLOR[
                        (shortUrgency(complaint.urgency) as Urgency) || "Low"
                      ]
                    }`}
                  >
                    {shortUrgency(complaint.urgency)}
                  </Badge>
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Location
                  </p>
                  <p className="mt-0.5 font-medium text-slate-700">
                    {complaint.location || "—"}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Ward
                  </p>
                  <p className="mt-0.5 font-medium text-slate-700">
                    {complaint.ward || "—"}
                  </p>
                </div>
              </div>
              <div className="mt-3">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                  Summary
                </p>
                <p className="mt-0.5 text-sm leading-relaxed text-slate-700">
                  {complaint.summary || "No summary available"}
                </p>
              </div>
            </div>

            {/* ── Divider ── */}
            <div className="border-t border-slate-200" />

            {/* ── Assign Officer Section (show when focus is null or 'assign') ── */}
            {(focus === null || focus === undefined || focus === "assign") && (
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <UserPlus className="h-4 w-4 text-[#2E7D9E]" />
                  <h3 className="text-sm font-semibold text-slate-800">
                    Assign Officer
                  </h3>
                  {focus === "assign" && (
                    <Badge className="bg-blue-100 text-blue-700 text-[10px]">
                      Action Required
                    </Badge>
                  )}
                </div>
                {complaint.assigned_to && (
                  <p className="mb-2 text-xs text-slate-500">
                    Currently assigned to:{" "}
                    <span className="font-medium text-slate-700">
                      {complaint.assigned_to}
                    </span>
                  </p>
                )}
                <div className="flex items-center gap-2">
                  <Select
                    value={selectedOfficer}
                    onValueChange={(value: string | null) => setSelectedOfficer(value ?? "")}
                  >
                    <SelectTrigger className="flex-1 bg-white">
                      <SelectValue placeholder="Select an officer" />
                    </SelectTrigger>
                    <SelectContent>
                      {getOfficersForCategory(complaint.category).map((o) => (
                        <SelectItem key={o} value={o}>
                          {o}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <button
                    onClick={handleAssignOfficer}
                    disabled={!selectedOfficer || assigning}
                    className="rounded-lg bg-[#1B3A5C] px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-[#152d48] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {assigning ? "Assigning..." : "Assign"}
                  </button>
                </div>
              </div>
            )}

            {/* ── Divider (only when both sections visible) ── */}
            {(focus === null || focus === undefined) && (
              <div className="border-t border-slate-200" />
            )}

            {/* ── Resolve Section (show when focus is null or 'resolve') ── */}
            {(focus === null || focus === undefined || focus === "resolve") && (
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-emerald-600" />
                  <h3 className="text-sm font-semibold text-slate-800">
                    Mark as Resolved
                  </h3>
                  {focus === "resolve" && (
                    <Badge className="bg-emerald-100 text-emerald-700 text-[10px]">
                      Action Required
                    </Badge>
                  )}
                </div>
                <div>
                  <label className="mb-1.5 block text-xs font-medium text-slate-500">
                    Officer Notes
                  </label>
                  <textarea
                    value={resolveNotes}
                    onChange={(e) => {
                      setResolveNotes(e.target.value);
                      if (e.target.value.trim()) setResolveError(false);
                    }}
                    placeholder="Describe the action taken to resolve this complaint..."
                    className={`w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-700 placeholder-slate-400 outline-none transition-colors focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 ${
                      resolveError
                        ? "border-red-400 focus:border-red-400 focus:ring-red-400"
                        : "border-slate-200"
                    }`}
                    rows={3}
                  />
                  {resolveError && (
                    <p className="mt-1.5 text-xs font-medium text-red-500">
                      Please add resolution notes before marking as resolved
                    </p>
                  )}
                </div>
                <button
                  onClick={handleMarkResolved}
                  disabled={resolving}
                  className="mt-3 w-full rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {resolving ? "Resolving..." : "Mark Resolved"}
                </button>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
