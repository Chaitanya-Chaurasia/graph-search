"use client";

import type { LatLon } from "../api";

interface SearchPanelProps {
  origin: LatLon | null;
  destination: LatLon | null;
  distance: number | null;
  loading: boolean;
  error: string | null;
  onFindRoute: () => void;
  onReset: () => void;
}

export default function SearchPanel({
  origin,
  destination,
  distance,
  loading,
  error,
  onFindRoute,
  onReset,
}: SearchPanelProps) {
  return (
    <div className="flex w-80 shrink-0 flex-col gap-4 border-r border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-950">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Maps Clone
      </h1>
      <p className="text-sm text-zinc-500">
        Click on the map to set origin (green) then destination (red).
      </p>

      <div className="flex flex-col gap-2">
        <PointDisplay label="Origin" point={origin} color="text-green-600" />
        <PointDisplay label="Destination" point={destination} color="text-red-600" />
      </div>

      <div className="flex gap-2">
        <button
          onClick={onFindRoute}
          disabled={!origin || !destination || loading}
          className="flex-1 rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? "Finding..." : "Find Route"}
        </button>
        <button
          onClick={onReset}
          className="rounded-md border border-zinc-300 px-3 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
        >
          Reset
        </button>
      </div>

      {error && (
        <p className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </p>
      )}

      {distance !== null && (
        <div className="rounded-md bg-zinc-100 p-3 dark:bg-zinc-900">
          <p className="text-sm text-zinc-500">Distance</p>
          <p className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            {distance >= 1000
              ? `${(distance / 1000).toFixed(2)} km`
              : `${distance.toFixed(0)} m`}
          </p>
        </div>
      )}
    </div>
  );
}

function PointDisplay({
  label,
  point,
  color,
}: {
  label: string;
  point: LatLon | null;
  color: string;
}) {
  return (
    <div className="rounded-md border border-zinc-200 p-2 dark:border-zinc-800">
      <span className={`text-xs font-medium ${color}`}>{label}</span>
      {point ? (
        <p className="text-sm text-zinc-700 dark:text-zinc-300">
          {point.lat.toFixed(5)}, {point.lon.toFixed(5)}
        </p>
      ) : (
        <p className="text-sm text-zinc-400">Click on map...</p>
      )}
    </div>
  );
}
