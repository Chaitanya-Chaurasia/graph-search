import { ShortestResponseSchema } from "@/models/schemas";
import type { LatLon, ShortestResponse, MapNodesResponse } from "@/models/schemas";
import { MapNodesResponseSchema } from "@/models/schemas";

export async function fetchShortestPath(
  origin: LatLon,
  destination: LatLon
): Promise<ShortestResponse> {
  const res = await fetch("/api/routes/shortest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ origin, destination }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Route request failed (${res.status}): ${detail}`);
  }
  const data = await res.json();
  return ShortestResponseSchema.parse(data);
}

export async function fetchMapNodes(bbox?: {
  min_lat: number;
  max_lat: number;
  min_lon: number;
  max_lon: number;
}): Promise<MapNodesResponse> {
  const params = new URLSearchParams();
  if (bbox) {
    params.set("min_lat", String(bbox.min_lat));
    params.set("max_lat", String(bbox.max_lat));
    params.set("min_lon", String(bbox.min_lon));
    params.set("max_lon", String(bbox.max_lon));
  }
  const url = `/api/map/nodes${bbox ? `?${params}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Map nodes request failed (${res.status})`);
  }
  const data = await res.json();
  return MapNodesResponseSchema.parse(data);
}
