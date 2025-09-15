import { NextRequest } from "next/server";
import { addSpeciesMarkers, getSpeciesMarkers, setSpeciesMarkers, type Marker } from "@/server/phytoplankton/locationsStore";
import { deriveMarkersFromCSV } from "@/server/phytoplankton/deriveFromCsv";

// GET /api/phytoplankton/locations?species=Leptocylindrus
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const species = searchParams.get("species");
  if (!species) {
    return Response.json({ error: "missing species" }, { status: 400 });
  }
  let markers = getSpeciesMarkers(species);
  console.log("[locations][GET] species=", species, "cacheCount=", markers.length);
  if (markers.length === 0) {
    try {
      console.log("[locations][GET] cache miss → deriving from CSV");
      markers = await deriveMarkersFromCSV(species);
      console.log("[locations][GET] derived markers count=", markers.length);
    } catch {
      // swallow errors; return empty
      console.warn("[locations][GET] CSV derivation failed");
    }
  }
  return Response.json({ species, markers });
}

// POST /api/phytoplankton/locations
// Body: { species: string, markers: Array<{ id: string, coords: [number, number] }>, mode?: 'replace'|'append' }
export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as {
      species: string;
      markers: Marker[];
      mode?: "replace" | "append";
    };
    if (!body?.species || !Array.isArray(body?.markers)) {
      return Response.json({ error: "invalid body" }, { status: 400 });
    }
    console.log("[locations][POST] species=", body.species, "mode=", body.mode, "incoming=", body.markers?.length ?? 0);
    const filtered: Marker[] = body.markers
      .map((m) => ({ id: String(m.id), coords: [Number(m.coords?.[0]), Number(m.coords?.[1])] as [number, number] }))
      .filter((m) => Number.isFinite(m.coords[0]) && Number.isFinite(m.coords[1]));
    if (body.mode === "replace") setSpeciesMarkers(body.species, filtered);
    else addSpeciesMarkers(body.species, filtered);
    console.log("[locations][POST] stored=", filtered.length);
    return Response.json({ ok: true, count: filtered.length });
  } catch {
    return Response.json({ error: "bad json" }, { status: 400 });
  }
}
