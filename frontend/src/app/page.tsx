"use client";
import { useEffect, useMemo, useState } from "react";
import PhytoplanktonGrid from "@/components/phytoplankton/PhytoplanktonGrid";
import Image from "next/image";
import { bestMatchIcon } from "@/lib/iconMatch";
import MapView from "@/components/map/MapView";
import SpeciesCompositionCard from "@/components/charts/SpeciesCompositionCard";

type Marker = { id: string; coords: [number, number] };

export default function Home() {
  // helper to display species with first letter capitalized
  const capitalize = (s?: string | null) => {
    if (!s) return "";
    return s.charAt(0).toUpperCase() + s.slice(1);
  };
  const [selected, setSelected] = useState<{ name: string; count: number; iconFile?: string } | null>(null);
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [heroFiles, setHeroFiles] = useState<string[]>([]);
  const [svgFiles, setSvgFiles] = useState<string[]>([]);

  // Load markers whenever a species is selected
  useEffect(() => {
    let ignore = false;
    async function load() {
      if (!selected?.name) {
        setMarkers([]);
        return;
      }
      console.log("[page] fetching markers for", selected.name);
      try {
        const res = await fetch(`/api/phytoplankton/locations?species=${encodeURIComponent(selected.name)}`, { cache: "no-store" });
        const data = await res.json();
        if (!ignore && Array.isArray(data?.markers)) {
          console.log("[page] received markers:", data.markers.length);
          setMarkers(data.markers);
        } else {
          console.log("[page] received empty/bad markers payload");
        }
      } catch {
        if (!ignore) setMarkers([]);
        console.warn("[page] fetch markers failed");
      }
    }
    load();
    return () => { ignore = true; };
  }, [selected?.name]);

  // Load available hero and svg files once
  useEffect(() => {
    let alive = true;
    fetch("/api/icons/herophyto")
      .then((r) => r.json())
      .then((d) => { if (alive) setHeroFiles(Array.isArray(d.files) ? d.files : []); })
      .catch(() => { if (alive) setHeroFiles([]); });
    fetch("/api/icons/phytoplankton")
      .then((r) => r.json())
      .then((d) => { if (alive) setSvgFiles(Array.isArray(d.files) ? d.files : []); })
      .catch(() => { if (alive) setSvgFiles([]); });
    return () => { alive = false; };
  }, []);

  const leftImg = useMemo(() => {
    if (!selected?.name) return null;
    // Fuzzy match in hero images first
    const hero = bestMatchIcon(selected.name, heroFiles);
    const svg = bestMatchIcon(selected.name, svgFiles);
    const src = hero ? `/heropytoplanktonimg/${hero}` : (svg ? `/pytoplanktonSvg/${svg}` : null);
    if (!src) return null;
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Image
          src={src}
          alt={capitalize(selected.name)}
          width={360}
          height={360}
          className="opacity-95"
        />
      </div>
    );
  }, [selected?.name, heroFiles, svgFiles]);

  return (
    <main className="min-h-screen bg-[var(--background)] px-6 py-8">
      {/* Clean header space */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[var(--foreground)] mb-2">Phytoplankton Species Distribution</h1>
        <p className="text-[var(--muted)] text-sm">Explore phytoplankton detection and geographic distribution</p>
      </div>

      

      {/* Mini-card carousel */}
      <section className="mb-8">
        <PhytoplanktonGrid onSelect={setSelected} />
      </section>

      {/* Clean details section */}
      {selected && (
        <section className="overflow-hidden">
          <div className="p-6 relative">
            <h2 className="text-xl font-medium text-[var(--foreground)]">{capitalize(selected.name)}</h2>
            <p className="text-[var(--muted)] text-sm mt-1">Geographic distribution and occurrences</p>
            {/* Morphing border that fades to white */}
            <div 
              className="absolute bottom-0 left-0 right-0 h-px"
              style={{
                background: "linear-gradient(to right, var(--border) 0%, rgba(229,231,235,0.7) 25%, rgba(229,231,235,0.2) 50%, rgba(229,231,235,0.0) 75%, rgba(229,231,235,0.0) 100%)"
              }}
            />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-5">
            <div className="lg:col-span-2 p-6 flex items-center justify-center">
              {leftImg ?? (
                <div className="flex flex-col items-center justify-center text-[var(--muted)] space-y-2">
                  <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <span className="text-sm">No image available</span>
                </div>
              )}
            </div>
            <div className="lg:col-span-3 relative h-[480px]">
              <MapView center={[72.8777, 19.076]} zoom={5} markers={markers} styleId="voyager" />
              {/* Seamless gradient overlays with new background color */}
              <div
                className="pointer-events-none absolute inset-y-0 left-0 w-64"
                style={{
                  background:
                    "linear-gradient(to right, white 0%, rgba(255,255,255,0.9) 10%, rgba(255,255,255,0.7) 20%, rgba(255,255,255,0.4) 35%, rgba(255,255,255,0.1) 60%, rgba(255,255,255,0.0) 100%)",
                }}
              />
              <div
                className="pointer-events-none absolute inset-y-0 right-0 w-32"
                style={{
                  background:
                    "linear-gradient(to left, white 0%, rgba(255,255,255,0.6) 25%, rgba(255,255,255,0.2) 60%, rgba(255,255,255,0.0) 100%)",
                }}
              />
              <div
                className="pointer-events-none absolute inset-x-0 top-0 h-20"
                style={{
                  background:
                    "linear-gradient(to bottom, white 0%, rgba(255,255,255,0.7) 30%, rgba(255,255,255,0.3) 60%, rgba(255,255,255,0.0) 100%)",
                }}
              />
              <div
                className="pointer-events-none absolute inset-x-0 bottom-0 h-20"
                style={{
                  background:
                    "linear-gradient(to top, white 0%, rgba(255,255,255,0.7) 30%, rgba(255,255,255,0.3) 60%, rgba(255,255,255,0.0) 100%)",
                }}
              />
              {markers.length === 0 && (
                <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-[var(--muted)] space-y-3">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <span className="text-sm font-medium">No locations detected yet</span>
                  <span className="text-xs">Data will appear as detections are made</span>
                </div>
              )}
            </div>
          </div>
          {/* Composition chart card - below image + map */}
          <div className="mt-6">
            <div className="w-full lg:w-1/3">
              <SpeciesCompositionCard selectedName={selected?.name} />
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
