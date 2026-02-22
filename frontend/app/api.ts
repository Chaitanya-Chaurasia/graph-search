import { z } from "zod";

const API_BASE = "http://localhost:8000";

// Zod schemas (mirror backend Pydantic models)
export const LatLonSchema = z.object({
  lat: z.number().min(-90).max(90),
  lon: z.number().min(-180).max(180),
});

export const ShortestResponseSchema = z.object({
  path: z.array(LatLonSchema),
  distance_m: z.number(),
});

export const MapNodesResponseSchema = z.object({
  nodes: z.array(
    z.object({
      id: z.number(),
      lat: z.number(),
      lon: z.number(),
    })
  ),
});

// Types inferred from schemas
export type LatLon = z.infer<typeof LatLonSchema>;
export type ShortestResponse = z.infer<typeof ShortestResponseSchema>;
export type MapNodesResponse = z.infer<typeof MapNodesResponseSchema>;

export async function fetchShortestPath(
  origin: LatLon,
  destination: LatLon
): Promise<ShortestResponse> {
  const res = await fetch(`${API_BASE}/routes/shortest`, {
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
  const url = `${API_BASE}/map/nodes${bbox ? `?${params}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Map nodes request failed (${res.status})`);
  }
  const data = await res.json();
  return MapNodesResponseSchema.parse(data);
}
