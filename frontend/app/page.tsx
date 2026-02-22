"use client";

import { useState, useCallback } from "react";
import dynamic from "next/dynamic";
import SearchPanel from "./components/search-panel";
import { fetchShortestPath } from "@/lib/api";
import type { LatLon } from "@/models/schemas";

// Leaflet requires browser APIs — load MapView only on client
const MapView = dynamic(() => import("./components/map-view"), { ssr: false });

export default function Home() {
  const [origin, setOrigin] = useState<LatLon | null>(null);
  const [destination, setDestination] = useState<LatLon | null>(null);
  const [route, setRoute] = useState<LatLon[]>([]);
  const [distance, setDistance] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFindRoute = useCallback(async () => {
    if (!origin || !destination) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetchShortestPath(origin, destination);
      setRoute(res.path);
      setDistance(res.distance_m);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to find route");
      setRoute([]);
      setDistance(null);
    } finally {
      setLoading(false);
    }
  }, [origin, destination]);

  const handleReset = useCallback(() => {
    setOrigin(null);
    setDestination(null);
    setRoute([]);
    setDistance(null);
    setError(null);
  }, []);

  const handleSetDestination = useCallback(
    (point: LatLon) => {
      setDestination(point);
      setRoute([]);
      setDistance(null);
      setError(null);
    },
    []
  );

  const handleSetOrigin = useCallback((point: LatLon) => {
    setOrigin(point);
    setDestination(null);
    setRoute([]);
    setDistance(null);
    setError(null);
  }, []);

  return (
    <div className="flex h-screen w-screen">
      <SearchPanel
        origin={origin}
        destination={destination}
        distance={distance}
        loading={loading}
        error={error}
        onFindRoute={handleFindRoute}
        onReset={handleReset}
      />
      <div className="flex-1">
        <MapView
          origin={origin}
          destination={destination}
          route={route}
          onSetOrigin={handleSetOrigin}
          onSetDestination={handleSetDestination}
        />
      </div>
    </div>
  );
}
