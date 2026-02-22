"use client";

import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import type { LatLon } from "@/models/schemas";

// Fix default marker icons (Leaflet + webpack/bundler issue)
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const originIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const destIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Piedmont, CA center
const DEFAULT_CENTER: [number, number] = [37.824, -122.232];
const DEFAULT_ZOOM = 15;

interface MapViewProps {
  origin: LatLon | null;
  destination: LatLon | null;
  route: LatLon[];
  onSetOrigin: (point: LatLon) => void;
  onSetDestination: (point: LatLon) => void;
}

function ClickHandler({
  origin,
  onSetOrigin,
  onSetDestination,
}: {
  origin: LatLon | null;
  onSetOrigin: (p: LatLon) => void;
  onSetDestination: (p: LatLon) => void;
}) {
  useMapEvents({
    click(e) {
      const point: LatLon = { lat: e.latlng.lat, lon: e.latlng.lng };
      if (!origin) {
        onSetOrigin(point);
      } else {
        onSetDestination(point);
      }
    },
  });
  return null;
}

export default function MapView({
  origin,
  destination,
  route,
  onSetOrigin,
  onSetDestination,
}: MapViewProps) {
  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={DEFAULT_ZOOM}
      className="h-full w-full"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickHandler
        origin={origin}
        onSetOrigin={onSetOrigin}
        onSetDestination={onSetDestination}
      />
      {origin && (
        <Marker position={[origin.lat, origin.lon]} icon={originIcon} />
      )}
      {destination && (
        <Marker position={[destination.lat, destination.lon]} icon={destIcon} />
      )}
      {route.length > 0 && (
        <Polyline
          positions={route.map((p) => [p.lat, p.lon])}
          pathOptions={{ color: "#2563eb", weight: 4 }}
        />
      )}
    </MapContainer>
  );
}
