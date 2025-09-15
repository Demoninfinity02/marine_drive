"use client";
import React, { useEffect, useRef } from "react";
import maplibregl, { type Map as MaplibreMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

type Props = {
  center?: [number, number]; // [lng, lat]
  zoom?: number;
  markers?: Array<{ id: string; coords: [number, number] }>;
  // Optional MapTiler style id; defaults to 'topo'. Examples: 'outdoor', 'streets', 'darkmatter'
  styleId?: string;
};

export default function MapView({ center = [72.8777, 19.0760], zoom = 4, markers = [], styleId = "topo" }: Props) {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const instance = useRef<MaplibreMap | null>(null);
  const markerRef = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!mapRef.current || instance.current) return;
    const key = process.env.NEXT_PUBLIC_MAPTILER_KEY || "YjWrSMoA7ZS7qB4sCmwu";
    const styleUrl = key
      ? `https://api.maptiler.com/maps/${styleId}/style.json?key=${key}`
      : "https://demotiles.maplibre.org/style.json";
    const map = new maplibregl.Map({
      container: mapRef.current,
      style: styleUrl,
      center,
      zoom,
      attributionControl: false,
    });
    console.log("[MapView] init center=", center, "zoom=", zoom);
    instance.current = map;
    return () => {
      map.remove();
      instance.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const map = instance.current;
    if (!map) return;
    // Clear previous markers
    markerRef.current.forEach((m) => m.remove());
    markerRef.current = markers.map((m) =>
      new maplibregl.Marker({ color: "#f43f5e" }).setLngLat(m.coords).addTo(map)
    );
    console.log("[MapView] markers updated:", markers.length);

    if (markers.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      markers.forEach((m) => bounds.extend(m.coords));
      // Fit with some padding, but don't zoom in past a comfortable level
      map.fitBounds(bounds, { padding: 40, maxZoom: Math.max(zoom, 8), duration: 600 });
      console.log("[MapView] fitBounds to markers");
    } else {
      // Reset to default center/zoom when no markers
      map.setCenter(center);
      map.setZoom(zoom);
      console.log("[MapView] reset to center/zoom");
    }
  }, [markers, center, zoom]);

  return <div ref={mapRef} className="h-full w-full" />;
}
