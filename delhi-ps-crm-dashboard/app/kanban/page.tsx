"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin } from "lucide-react";
import { ticketId } from "@/lib/constants";
import {
  DragDropContext,
  Droppable,
  Draggable,
  type DropResult,
} from "@hello-pangea/dnd";
import ManageComplaintModal, {
  type ManageComplaint,
  type ModalFocus,
} from "@/components/manage-complaint-modal";

type ColumnId = "open" | "assigned" | "resolved";

const COLUMN_META: Record<
  ColumnId,
  { title: string; color: string }
> = {
  open: { title: "Open", color: "border-amber-400" },
  assigned: { title: "In Progress", color: "border-blue-400" },
  resolved: { title: "Resolved", color: "border-emerald-400" },
};

const COLUMN_ORDER: ColumnId[] = ["open", "assigned", "resolved"];

function urgencyLabel(u: string | null): string {
  const v = (u || "").split("(")[0].trim();
  if (v === "Critical") return "URGENT";
  if (v === "High") return "HIGH";
  return "ROUTINE";
}

function urgencyBadgeColor(u: string | null): string {
  const v = (u || "").split("(")[0].trim();
  if (v === "Critical") return "bg-red-500 text-white";
  if (v === "High") return "bg-orange-500 text-white";
  return "bg-slate-200 text-slate-600";
}

function colForStatus(s: string | null): ColumnId {
  if (s === "assigned") return "assigned";
  if (s === "resolved") return "resolved";
  return "open"; // open, escalated, null all go here
}

export default function KanbanPage() {
  const [complaints, setComplaints] = useState<ManageComplaint[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal state for drag-triggered actions
  const [modalComplaint, setModalComplaint] = useState<ManageComplaint | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalFocus, setModalFocus] = useState<ModalFocus>(null);

  const fetchData = useCallback(async () => {
    try {
      const { data } = await supabase
        .from("raw_complaints")
        .select(
          "id,summary,category,status,urgency,timestamp,location,ward,assigned_to,resolved_at"
        )
        .order("timestamp", { ascending: false });
      setComplaints((data || []) as ManageComplaint[]);
    } catch {
      console.error("Failed to fetch kanban data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ── Build column data ──
  const columns: Record<ColumnId, ManageComplaint[]> = {
    open: [],
    assigned: [],
    resolved: [],
  };
  for (const c of complaints) {
    columns[colForStatus(c.status)].push(c);
  }

  // ── Drag handler — opens modal instead of direct update ──
  function handleDragEnd(result: DropResult) {
    const { draggableId, destination, source } = result;
    if (!destination) return;
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    )
      return;

    const newStatus = destination.droppableId as ColumnId;
    const oldStatus = source.droppableId as ColumnId;
    if (newStatus === oldStatus) return; // same column reorder — no action

    // Find the dragged complaint
    const complaint = complaints.find((c) => c.id === draggableId);
    if (!complaint) return;

    if (newStatus === "assigned") {
      // Dragging to "In Progress" → open modal with assign focus
      setModalComplaint(complaint);
      setModalFocus("assign");
      setModalOpen(true);
    } else if (newStatus === "resolved") {
      // Dragging to "Resolved" → open modal with resolve focus
      setModalComplaint(complaint);
      setModalFocus("resolve");
      setModalOpen(true);
    } else {
      // Dragging back to "Open" — revert status directly
      revertToOpen(draggableId);
    }
  }

  async function revertToOpen(id: string) {
    setComplaints((prev) =>
      prev.map((c) =>
        c.id === id ? { ...c, status: "open" } : c
      )
    );
    await supabase
      .from("raw_complaints")
      .update({ status: "open" })
      .eq("id", id);
    fetchData();
  }

  function handleModalClose() {
    // User cancelled — card stays in original column (no optimistic update was done)
    setModalOpen(false);
    setModalComplaint(null);
    setModalFocus(null);
  }

  function handleModalUpdated() {
    setModalOpen(false);
    setModalComplaint(null);
    setModalFocus(null);
    fetchData();
  }

  // ── Derived stats ────────────────────────────────────────
  const now = Date.now();
  const oneWeekAgo = now - 7 * 86400000;
  const thisWeekAll = complaints.filter(
    (c) => c.timestamp && new Date(c.timestamp).getTime() > oneWeekAgo
  );
  const thisWeekResolved = thisWeekAll.filter(
    (c) => c.status === "resolved"
  );
  const weeklyPct =
    thisWeekAll.length > 0
      ? Math.round((thisWeekResolved.length / thisWeekAll.length) * 100)
      : 0;

  const resolvedList = columns.resolved;
  const tats = resolvedList
    .filter((c) => c.timestamp && (c as any).resolved_at)
    .map((c) => {
      const diff =
        new Date((c as any).resolved_at!).getTime() -
        new Date(c.timestamp!).getTime();
      return diff / 3600000;
    })
    .filter((h) => h > 0);
  const avgTAT =
    tats.length > 0
      ? (tats.reduce((a, b) => a + b, 0) / tats.length).toFixed(1)
      : "N/A";

  return (
    <div className="p-4 md:p-6 lg:p-8">
      <h1 className="mb-1 text-xl font-bold text-[#1B3A5C] md:text-2xl">
        Workflow Management
      </h1>
      <p className="mb-4 max-w-2xl text-xs text-slate-500 md:mb-6 md:text-sm">
        Drag and drop complaints between columns to update their status.
        A confirmation modal will open before any changes are saved.
      </p>

      {loading ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-3">
              {[1, 2, 3, 4].map((j) => (
                <div
                  key={j}
                  className="h-28 animate-pulse rounded-lg bg-slate-200"
                />
              ))}
            </div>
          ))}
        </div>
      ) : (
        <DragDropContext onDragEnd={handleDragEnd}>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {COLUMN_ORDER.map((colId) => {
              const meta = COLUMN_META[colId];
              const items = columns[colId];

              return (
                <div key={colId} className="flex flex-col">
                  {/* Column header */}
                  <div
                    className={`mb-3 flex items-center justify-between rounded-lg border-l-4 bg-white px-4 py-3 shadow-sm ${meta.color}`}
                  >
                    <span className="text-sm font-semibold text-[#1B3A5C]">
                      {meta.title}
                    </span>
                    <Badge
                      variant="outline"
                      className="text-xs text-slate-500"
                    >
                      {items.length}
                    </Badge>
                  </div>

                  {/* Droppable area */}
                  <Droppable droppableId={colId}>
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.droppableProps}
                        className={`min-h-[120px] flex-1 space-y-3 overflow-y-auto rounded-lg p-1 transition-colors md:max-h-[calc(100vh-280px)] ${
                          snapshot.isDraggingOver
                            ? "bg-slate-100/80"
                            : "bg-transparent"
                        }`}
                      >
                        {items.slice(0, 30).map((c, index) => (
                          <Draggable
                            key={c.id}
                            draggableId={c.id}
                            index={index}
                          >
                            {(prov, snap) => (
                              <div
                                ref={prov.innerRef}
                                {...prov.draggableProps}
                                {...prov.dragHandleProps}
                                style={prov.draggableProps.style}
                                className={`transition-shadow ${
                                  snap.isDragging
                                    ? "rotate-[1.5deg] shadow-lg shadow-slate-300/60"
                                    : ""
                                }`}
                              >
                                <Card className="border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md">
                                  <CardContent className="p-4">
                                    <div className="mb-2 flex items-start justify-between">
                                      <Badge
                                        className={`text-[10px] font-semibold ${urgencyBadgeColor(
                                          c.urgency
                                        )}`}
                                      >
                                        {urgencyLabel(c.urgency)}
                                      </Badge>
                                      <span className="font-mono text-[10px] text-slate-400">
                                        {ticketId(c.id)}
                                      </span>
                                    </div>
                                    <p className="mb-2 line-clamp-2 text-sm font-medium text-slate-700">
                                      {c.summary || "No summary"}
                                    </p>
                                    {(c.location || c.ward) && (
                                      <div className="flex items-center gap-1 text-[10px] text-slate-400">
                                        <MapPin className="h-3 w-3" />
                                        <span className="truncate">
                                          {c.ward ||
                                            c.location ||
                                            "Unknown"}
                                        </span>
                                      </div>
                                    )}
                                  </CardContent>
                                </Card>
                              </div>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                        {items.length > 30 && (
                          <p className="py-2 text-center text-xs text-slate-400">
                            +{items.length - 30} more
                          </p>
                        )}
                      </div>
                    )}
                  </Droppable>

                  {/* Resolved column footer stats */}
                  {colId === "resolved" && (
                    <div className="mt-3 space-y-2 rounded-lg bg-slate-50 p-3">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-500">
                          Weekly Resolution %
                        </span>
                        <span className="font-semibold text-emerald-600">
                          {weeklyPct}%
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-500">Average TAT</span>
                        <span className="font-semibold text-[#1B3A5C]">
                          {avgTAT}h
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </DragDropContext>
      )}

      {/* ── Manage Complaint Modal (triggered by drag) ── */}
      <ManageComplaintModal
        complaint={modalComplaint}
        open={modalOpen}
        focus={modalFocus}
        onClose={handleModalClose}
        onUpdated={handleModalUpdated}
      />
    </div>
  );
}
