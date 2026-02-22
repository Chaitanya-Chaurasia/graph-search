import { z } from "zod";

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
