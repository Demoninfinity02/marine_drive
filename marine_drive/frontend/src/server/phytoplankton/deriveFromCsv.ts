import fs from "node:fs";
import path from "node:path";
import { parse } from "csv-parse";
import { setSpeciesMarkers, type Marker } from "@/server/phytoplankton/locationsStore";

const LAT_KEYS = ["decimalLatitude", "lat", "latitude", "Latitude", "LAT"];
const LON_KEYS = ["decimalLongitude", "lon", "lng", "longitude", "Longitude", "LON", "LNG"];
const SPECIES_KEYS = [
  "phytoplanktonscientificName",
  "scientific_name",
  "scientificName",
  "species",
  "Species",
];

function norm(s: string) {
  return s.trim().toLowerCase();
}

function genusOf(name: string) {
  const t = name.trim().split(/\s+/)[0] ?? "";
  return norm(t);
}

function pickFirst(record: Record<string, unknown>, keys: string[]): unknown {
  for (const k of keys) {
    if (k in record) return (record as Record<string, unknown>)[k];
  }
  return undefined;
}

export async function deriveMarkersFromCSV(
  species: string,
  opts: { bucketDeg?: number; limit?: number } = {}
): Promise<Marker[]> {
  const bucket = opts.bucketDeg ?? 0.5; // ~55km bucket
  const limit = opts.limit ?? 200;
  // India bounding box (approx): [minLon, minLat, maxLon, maxLat]
  const INDIA_BBOX: [number, number, number, number] = [68.0, 6.0, 97.5, 37.5];

  const csvPath = path.join(process.cwd(), "data-analytics", "Phytoplankton_harmonized_database_revised.csv");
  if (!fs.existsSync(csvPath)) {
    console.warn("[deriveFromCSV] CSV not found:", csvPath);
    return [];
  }

  const want = norm(species);
  const wantGenus = genusOf(species);
  const buckets = new Map<string, { lon: number; lat: number; count: number }>();
  const bucketsIndia = new Map<string, { lon: number; lat: number; count: number }>();
  let rows = 0;
  let matched = 0;
  let chosenLatKey: string | undefined;
  let chosenLonKey: string | undefined;

  await new Promise<void>((resolve, reject) => {
    const stream = fs
      .createReadStream(csvPath)
      .pipe(
        parse({ columns: true, bom: true, skip_empty_lines: true })
      );

    stream.on("data", (rec: Record<string, unknown>) => {
      try {
        if (rows === 0) {
          const headers = Object.keys(rec);
          console.log("[deriveFromCSV] headers:", headers.slice(0, 20));
          const headersLower = headers.map((h) => h.toLowerCase());
          // Choose lat/lon keys if available
          const pickBy = (candidates: string[], patterns: RegExp[]): string | undefined => {
            for (const p of patterns) {
              const idx = headersLower.findIndex((h) => p.test(h));
              if (idx !== -1) return headers[idx];
            }
            for (const c of candidates) {
              const idx = headersLower.indexOf(c.toLowerCase());
              if (idx !== -1) return headers[idx];
            }
            return undefined;
          };
          chosenLatKey = pickBy(LAT_KEYS, [/\bdecimalLatitude\b/i, /lat/i]);
          chosenLonKey = pickBy(LON_KEYS, [/\bdecimalLongitude\b/i, /(lon|lng)/i]);
          console.log("[deriveFromCSV] chosen keys lat=", chosenLatKey, "lon=", chosenLonKey);
        }
        rows++;
        const spRaw = String(pickFirst(rec, SPECIES_KEYS) ?? "");
        if (!spRaw) return;
        const spNorm = norm(spRaw);
        const spGenus = genusOf(spRaw);
        // Match exact species or any variant that shares the genus
        if (!(spNorm === want || spGenus === wantGenus)) return;
        matched++;

        const latVal = (chosenLatKey ? rec[chosenLatKey] : pickFirst(rec, LAT_KEYS));
        const lonVal = (chosenLonKey ? rec[chosenLonKey] : pickFirst(rec, LON_KEYS));
        const lat = Number(latVal);
        const lon = Number(lonVal);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
        if (lat < -90 || lat > 90 || lon < -180 || lon > 180) return;

        const bx = Math.round(lon / bucket) * bucket;
        const by = Math.round(lat / bucket) * bucket;
        const key = `${bx.toFixed(3)},${by.toFixed(3)}`;
        const inIndia = lon >= INDIA_BBOX[0] && lon <= INDIA_BBOX[2] && lat >= INDIA_BBOX[1] && lat <= INDIA_BBOX[3];
        if (inIndia) {
          const currIn = bucketsIndia.get(key) ?? { lon: bx, lat: by, count: 0 };
          currIn.count += 1;
          bucketsIndia.set(key, currIn);
        } else {
          const curr = buckets.get(key) ?? { lon: bx, lat: by, count: 0 };
          curr.count += 1;
          buckets.set(key, curr);
        }
      } catch {
        // ignore bad rows
      }
    });

    stream.on("end", () => {
      console.log(
        "[deriveFromCSV] rows=", rows,
        "matched=", matched,
        "bucketsIndia=", bucketsIndia.size,
        "bucketsGlobal=", buckets.size
      );
      resolve();
    });
    stream.on("error", (e: Error) => reject(e));
  });

  // Convert to markers; prioritize India buckets, then backfill with global
  const toMarkers = (entries: [string, { lon: number; lat: number; count: number } ][]) =>
    entries.map(([key, v]) => ({ id: `${key}:${v.count}`, coords: [v.lon, v.lat] as [number, number] }));

  const indiaSorted = Array.from(bucketsIndia.entries()).sort((a, b) => b[1].count - a[1].count);
  const globalSorted = Array.from(buckets.entries()).sort((a, b) => b[1].count - a[1].count);

  const indiaMarkers = toMarkers(indiaSorted).slice(0, limit);
  const remaining = Math.max(0, limit - indiaMarkers.length);
  const globalMarkers = remaining > 0 ? toMarkers(globalSorted).slice(0, remaining) : [];
  const markers: Marker[] = [...indiaMarkers, ...globalMarkers];

  console.log("[deriveFromCSV] output markers:", markers.length);

  // Cache into the in-memory store for future quick access
  setSpeciesMarkers(species, markers);
  return markers;
}
