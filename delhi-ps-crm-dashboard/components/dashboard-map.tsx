"use client";

import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface Props {
  complaints: {
    id: string;
    summary: string | null;
    urgency: string | null;
    location: string | null;
    ward: string | null;
  }[];
}

const URGENCY_CLR: Record<string, string> = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};

function parseLatLng(loc: string | null): [number, number] | null {
  if (!loc) return null;
  // Try "lat, lng" format
  const parts = loc.split(",").map((s) => parseFloat(s.trim()));
  if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
    return [parts[0], parts[1]];
  }
  return null;
}

export default function DashboardMap({ complaints }: Props) {
  const markers = complaints
    .map((c) => ({ ...c, latlng: parseLatLng(c.location) }))
    .filter((c) => c.latlng !== null);

  return (
    <MapContainer
      center={[28.6139, 77.209]}
      zoom={11}
      className="h-full w-full rounded-b-lg"
      scrollWheelZoom={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {markers.map((m) => (
        <CircleMarker
          key={m.id}
          center={m.latlng!}
          radius={6}
          pathOptions={{
            color: URGENCY_CLR[m.urgency || "Low"] || "#22c55e",
            fillColor: URGENCY_CLR[m.urgency || "Low"] || "#22c55e",
            fillOpacity: 0.7,
          }}
        >
          <Popup>
            <div className="text-xs">
              <p className="font-semibold">{m.summary || "No summary"}</p>
              <p className="text-slate-500">{m.ward || "Unknown ward"}</p>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
