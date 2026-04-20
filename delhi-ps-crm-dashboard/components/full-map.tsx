"use client";

import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface Complaint {
  id: string;
  summary: string | null;
  category: string | null;
  status: string | null;
  urgency: string | null;
  timestamp: string | null;
  location: string | null;
  ward: string | null;
  assigned_to: string | null;
  photo_url: string | null;
}

interface Props {
  complaints: Complaint[];
  onSelect: (c: Complaint) => void;
}

const URGENCY_CLR: Record<string, string> = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};

const CAT_CLR: Record<string, string> = {
  "Waste Management": "#84cc16",
  "Water Supply": "#3b82f6",
  Roads: "#a855f7",
  "Sewage & Drainage": "#f97316",
  Electricity: "#eab308",
  Other: "#6b7280",
};

function parseLatLng(loc: string | null): [number, number] | null {
  if (!loc) return null;
  const parts = loc.split(",").map((s) => parseFloat(s.trim()));
  if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
    return [parts[0], parts[1]];
  }
  return null;
}

export default function FullMap({ complaints, onSelect }: Props) {
  const markers = complaints
    .map((c) => ({ ...c, latlng: parseLatLng(c.location) }))
    .filter((c) => c.latlng !== null);

  return (
    <MapContainer
      center={[28.6139, 77.209]}
      zoom={11}
      className="h-full w-full"
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {markers.map((m) => {
        const clr = URGENCY_CLR[m.urgency || "Low"] || "#22c55e";
        return (
          <CircleMarker
            key={m.id}
            center={m.latlng!}
            radius={7}
            pathOptions={{
              color: clr,
              fillColor: clr,
              fillOpacity: 0.8,
              weight: 2,
            }}
            eventHandlers={{
              click: () => onSelect(m),
            }}
          >
            <Popup>
              <p className="text-xs font-semibold">
                {m.summary || "No summary"}
              </p>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}
